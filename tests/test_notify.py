"""Tests for bin/notify.py — the single notification path for every job.

The contract these lock down:
  1. A missing or broken channel NEVER raises. A scraper must not die because
     Telegram is down.
  2. The bot token never reaches the log file.
  3. Delivery is reported honestly: True only when Telegram confirmed ok.
"""
import io
import json
import urllib.error

import pytest

TOKEN = "123456:FAKE-TOKEN-DO-NOT-LOG"
CHAT = "987654"


def write_secrets(home, token=TOKEN, chat=CHAT):
    (home / ".secrets" / "telegram.env").write_text(
        f"# comment line\n\nTELEGRAM_BOT_TOKEN={token}\nTELEGRAM_CHAT_ID={chat}\n"
    )


def read_log(home):
    log = home / "logs" / "notify.log"
    return log.read_text() if log.exists() else ""


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


@pytest.fixture
def captured(monkeypatch, notify_mod):
    """Intercept urlopen; record the request instead of hitting the network."""
    calls = []

    def fake_urlopen(req, timeout=None):
        calls.append(req)
        return FakeResponse(json.dumps({"ok": True}).encode())

    monkeypatch.setattr(notify_mod.urllib.request, "urlopen", fake_urlopen)
    return calls


# --------------------------------------------------------------- env parsing
def test_load_env_parses_and_ignores_noise(notify_mod, fake_home):
    (fake_home / ".secrets" / "telegram.env").write_text(
        "# a comment\n\nTELEGRAM_BOT_TOKEN='quoted'\nTELEGRAM_CHAT_ID=  42  \nJUNK\n"
    )
    env = notify_mod._load_env()
    assert env["TELEGRAM_BOT_TOKEN"] == "quoted"
    assert env["TELEGRAM_CHAT_ID"] == "42"
    assert "JUNK" not in env


def test_load_env_absent_file_is_empty_not_error(notify_mod):
    assert notify_mod._load_env() == {}


# ------------------------------------------------------- degradation, no channel
def test_no_credentials_returns_false_and_logs_nochannel(notify_mod, fake_home):
    assert notify_mod.notify("hello") is False
    assert "NOCHANNEL\thello" in read_log(fake_home)


def test_no_credentials_does_not_raise(notify_mod):
    notify_mod.notify("must not raise")  # absence of exception is the assertion


def test_empty_message_is_a_noop(notify_mod, fake_home):
    assert notify_mod.notify("") is False
    assert notify_mod.notify("   ") is False
    assert read_log(fake_home) == ""


# ------------------------------------------------------------------ delivery
def test_successful_send_returns_true_and_logs_sent(notify_mod, fake_home, captured):
    write_secrets(fake_home)
    assert notify_mod.notify("it works") is True
    assert "SENT\tit works" in read_log(fake_home)
    assert len(captured) == 1


def test_send_targets_the_configured_chat(notify_mod, fake_home, captured):
    write_secrets(fake_home)
    notify_mod.notify("routed")
    body = captured[0].data.decode()
    assert f"chat_id={CHAT}" in body
    assert TOKEN in captured[0].full_url  # token belongs in the URL...


def test_silent_flag_suppresses_notification_sound(notify_mod, fake_home, captured):
    write_secrets(fake_home)
    notify_mod.notify("routine report", silent=True)
    assert "disable_notification=true" in captured[0].data.decode()

    notify_mod.notify("urgent")
    assert "disable_notification=false" in captured[1].data.decode()


def test_env_vars_used_when_secrets_file_absent(notify_mod, monkeypatch, captured):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", TOKEN)
    monkeypatch.setenv("TELEGRAM_CHAT_ID", CHAT)
    assert notify_mod.notify("from env") is True


# ------------------------------------------------------------------- failures
def test_http_error_returns_false_and_logs_status(notify_mod, fake_home, monkeypatch):
    write_secrets(fake_home)

    def boom(req, timeout=None):
        raise urllib.error.HTTPError(req.full_url, 401, "Unauthorized", {}, None)

    monkeypatch.setattr(notify_mod.urllib.request, "urlopen", boom)
    assert notify_mod.notify("bad token") is False
    assert "FAILED(http=401)" in read_log(fake_home)


def test_network_error_returns_false_and_names_the_exception(notify_mod, fake_home, monkeypatch):
    write_secrets(fake_home)

    def boom(req, timeout=None):
        raise TimeoutError("no route to host")

    monkeypatch.setattr(notify_mod.urllib.request, "urlopen", boom)
    assert notify_mod.notify("offline") is False
    assert "FAILED(TimeoutError)" in read_log(fake_home)


def test_api_level_rejection_is_reported_as_failure(notify_mod, fake_home, monkeypatch):
    """HTTP 200 with {"ok": false} is still a failure — Telegram does this."""
    write_secrets(fake_home)
    monkeypatch.setattr(
        notify_mod.urllib.request,
        "urlopen",
        lambda req, timeout=None: FakeResponse(json.dumps({"ok": False}).encode()),
    )
    assert notify_mod.notify("rejected") is False
    assert "FAILED(api)" in read_log(fake_home)


# -------------------------------------------------------------------- secrets
@pytest.mark.parametrize("scenario", ["success", "http_error", "network_error"])
def test_token_never_appears_in_the_log(notify_mod, fake_home, monkeypatch, scenario):
    write_secrets(fake_home)
    if scenario == "http_error":
        def send(req, timeout=None):
            raise urllib.error.HTTPError(req.full_url, 401, "Unauthorized", {}, None)
    elif scenario == "network_error":
        def send(req, timeout=None):
            raise TimeoutError("boom")
    else:
        def send(req, timeout=None):
            return FakeResponse(json.dumps({"ok": True}).encode())

    monkeypatch.setattr(notify_mod.urllib.request, "urlopen", send)
    notify_mod.notify("carrying a secret")
    assert TOKEN not in read_log(fake_home)


# ------------------------------------------------------------------ log format
def test_log_lines_are_three_tab_separated_fields(notify_mod, fake_home):
    notify_mod.notify("first")
    notify_mod.notify("second")
    lines = read_log(fake_home).strip().splitlines()
    assert len(lines) == 2
    for line in lines:
        stamp, status, message = line.split("\t")
        assert stamp.startswith("20")
        assert status and message


def test_log_is_created_when_logs_dir_missing(notify_mod, fake_home):
    """A fresh machine has no ~/logs — notify must create it, not crash."""
    import shutil

    shutil.rmtree(fake_home / "logs")
    assert notify_mod.notify("cold start") is False
    assert (fake_home / "logs" / "notify.log").exists()


# ------------------------------------------- regressions (fable review 2026-07-22)
def test_unwritable_log_does_not_raise(notify_mod, fake_home):
    """Disk full / read-only logs is exactly when the watchdog needs to alert.
    Logging must never be the thing that raises."""
    logs = fake_home / "logs"
    logs.chmod(0o500)
    try:
        assert notify_mod.notify("disk is full") is False
    finally:
        logs.chmod(0o700)


def test_unreadable_secrets_is_treated_as_no_credentials(notify_mod, fake_home):
    secrets = fake_home / ".secrets" / "telegram.env"
    write_secrets(fake_home)
    secrets.chmod(0o000)
    try:
        assert notify_mod.notify("bad perms") is False
    finally:
        secrets.chmod(0o600)


def test_non_string_message_does_not_raise(notify_mod, fake_home):
    assert notify_mod.notify(42) is False or True  # must not raise
    assert "42" in read_log(fake_home)


def test_multiline_message_stays_one_log_line(notify_mod, fake_home):
    notify_mod.notify("line one\nline two\twith tab")
    lines = read_log(fake_home).strip().splitlines()
    assert len(lines) == 1
    assert len(lines[0].split("\t")) == 3


def test_urlopen_receives_a_finite_timeout(notify_mod, fake_home, monkeypatch):
    """Without a timeout a stalled connection hangs a scraper forever."""
    write_secrets(fake_home)
    seen = {}

    def capture(req, timeout=None):
        seen["timeout"] = timeout
        return FakeResponse(json.dumps({"ok": True}).encode())

    monkeypatch.setattr(notify_mod.urllib.request, "urlopen", capture)
    notify_mod.notify("timed")
    assert isinstance(seen["timeout"], (int, float)) and 0 < seen["timeout"] < 120
