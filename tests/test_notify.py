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
import urllib.parse

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


# ===================================================== retry + outbox (2026-08-04)
# The box is Wi-Fi only, so a dropped link is routine rather than exotic. A
# message lost to one used to exist solely as a log line nobody reads.
#
# The property that matters most is the one that looks like a bug: a queued
# message must still report failure. See test_queued_message_still_reports_failure.

def outbox_path(home):
    return home / ".local" / "state" / "workbench" / "outbox.jsonl"


def read_outbox(home):
    path = outbox_path(home)
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def flaky(fail_times, exc=None):
    """urlopen stub that fails `fail_times` times and then succeeds."""
    state = {"n": 0}

    def send(req, timeout=None):
        state["n"] += 1
        if state["n"] <= fail_times:
            raise exc or TimeoutError("link down")
        return FakeResponse(json.dumps({"ok": True}).encode())

    send.state = state
    return send


@pytest.fixture
def no_backoff(monkeypatch, notify_mod):
    """Keep the retry count, drop the waiting, so the suite stays quick."""
    monkeypatch.setattr(notify_mod, "RETRY_BACKOFF", (0, 0))
    return notify_mod


# ------------------------------------------------------------------- retrying
def test_transient_failure_is_retried_three_times(notify_mod, fake_home, monkeypatch, no_backoff):
    write_secrets(fake_home)
    send = flaky(99)
    monkeypatch.setattr(notify_mod.urllib.request, "urlopen", send)
    assert notify_mod.notify("keeps failing") is False
    assert send.state["n"] == 3, "one attempt plus two retries"


def test_a_blip_that_clears_needs_no_outbox(notify_mod, fake_home, monkeypatch, no_backoff):
    write_secrets(fake_home)
    monkeypatch.setattr(notify_mod.urllib.request, "urlopen", flaky(2))
    assert notify_mod.notify("third time lucky") is True
    assert read_outbox(fake_home) == []


def test_backoff_waits_two_then_five_seconds(notify_mod, fake_home, monkeypatch):
    write_secrets(fake_home)
    slept = []
    monkeypatch.setattr(notify_mod.time, "sleep", slept.append)
    monkeypatch.setattr(notify_mod.urllib.request, "urlopen", flaky(99))
    notify_mod.notify("offline")
    assert slept == [2.0, 5.0], "no sleep after the final attempt"


def test_permanent_failure_is_not_retried(notify_mod, fake_home, monkeypatch):
    """A bad token fails identically forever — retrying it just wastes 7s."""
    write_secrets(fake_home)
    calls = []

    def boom(req, timeout=None):
        calls.append(1)
        raise urllib.error.HTTPError(req.full_url, 401, "Unauthorized", {}, None)

    monkeypatch.setattr(notify_mod.urllib.request, "urlopen", boom)
    notify_mod.notify("bad token")
    assert len(calls) == 1


# -------------------------------------------------------- what queues, what doesn't
def test_queued_message_still_reports_failure(notify_mod, fake_home, monkeypatch, no_backoff):
    """Queuing is not delivery.

    watchdog-check.sh starts its 6h alert cooldown when notify() returns True.
    If a queued alert reported success, a Wi-Fi drop during an incident would
    mute that incident until morning — the exact bug the cooldown branch in
    watchdog-check.sh was written to prevent.
    """
    write_secrets(fake_home)
    monkeypatch.setattr(notify_mod.urllib.request, "urlopen", flaky(99))
    assert notify_mod.notify("⚠️ disk full") is False
    assert len(read_outbox(fake_home)) == 1, "queued, but still reported as undelivered"


def test_transient_failure_preserves_the_silent_flag(notify_mod, fake_home, monkeypatch, no_backoff):
    write_secrets(fake_home)
    monkeypatch.setattr(notify_mod.urllib.request, "urlopen", flaky(99))
    notify_mod.notify("routine report", silent=True)
    entry = read_outbox(fake_home)[0]
    assert entry["message"] == "routine report"
    assert entry["silent"] is True


@pytest.mark.parametrize("code", [400, 401, 403, 404])
def test_permanent_http_errors_never_queue(notify_mod, fake_home, monkeypatch, code, no_backoff):
    write_secrets(fake_home)

    def boom(req, timeout=None):
        raise urllib.error.HTTPError(req.full_url, code, "nope", {}, None)

    monkeypatch.setattr(notify_mod.urllib.request, "urlopen", boom)
    assert notify_mod.notify("hopeless") is False
    assert read_outbox(fake_home) == []


@pytest.mark.parametrize("code", [429, 500, 503])
def test_rate_limits_and_server_errors_queue(notify_mod, fake_home, monkeypatch, code, no_backoff):
    write_secrets(fake_home)

    def boom(req, timeout=None):
        raise urllib.error.HTTPError(req.full_url, code, "later", {}, None)

    monkeypatch.setattr(notify_mod.urllib.request, "urlopen", boom)
    assert notify_mod.notify("come back later") is False
    assert len(read_outbox(fake_home)) == 1


def test_api_level_rejection_never_queues(notify_mod, fake_home, monkeypatch):
    """HTTP 200 + {"ok": false} is Telegram refusing the request itself."""
    write_secrets(fake_home)
    monkeypatch.setattr(
        notify_mod.urllib.request,
        "urlopen",
        lambda req, timeout=None: FakeResponse(json.dumps({"ok": False}).encode()),
    )
    assert notify_mod.notify("rejected") is False
    assert read_outbox(fake_home) == []


def test_nochannel_never_queues(notify_mod, fake_home):
    """No credentials means nowhere to send it, now or later."""
    assert notify_mod.notify("nowhere to go") is False
    assert read_outbox(fake_home) == []


# ---------------------------------------------------------------------- draining
def test_outbox_drains_oldest_first_on_the_next_send(notify_mod, fake_home, monkeypatch, no_backoff):
    write_secrets(fake_home)
    monkeypatch.setattr(notify_mod.urllib.request, "urlopen", flaky(99))
    notify_mod.notify("first")
    notify_mod.notify("second")
    assert len(read_outbox(fake_home)) == 2

    sent = []

    def ok(req, timeout=None):
        sent.append(urllib.parse.parse_qs(req.data.decode())["text"][0])
        return FakeResponse(json.dumps({"ok": True}).encode())

    monkeypatch.setattr(notify_mod.urllib.request, "urlopen", ok)
    assert notify_mod.notify("third") is True
    assert sent == ["first", "second", "third"], "a recovered link replays in order"
    assert read_outbox(fake_home) == []


def test_drain_stops_at_the_first_transient_failure(notify_mod, fake_home, monkeypatch):
    """A dead link must not burn the whole queue in one pass."""
    write_secrets(fake_home)
    for msg in ("a", "b", "c"):
        notify_mod._outbox_append(msg, False)

    calls = []

    def send(req, timeout=None):
        calls.append(1)
        raise TimeoutError("still down")

    monkeypatch.setattr(notify_mod.urllib.request, "urlopen", send)
    assert notify_mod.flush() == 0
    assert len(calls) == 1, "one attempt, then stop — not one per queued message"
    assert len(read_outbox(fake_home)) == 3


def test_drain_drops_a_permanently_undeliverable_entry(notify_mod, fake_home, monkeypatch):
    """Otherwise one poisoned entry blocks the queue behind it forever."""
    write_secrets(fake_home)
    notify_mod._outbox_append("doomed", False)
    notify_mod._outbox_append("fine", False)

    seen = []

    def send(req, timeout=None):
        text = urllib.parse.parse_qs(req.data.decode())["text"][0]
        seen.append(text)
        if text == "doomed":
            raise urllib.error.HTTPError(req.full_url, 400, "Bad Request", {}, None)
        return FakeResponse(json.dumps({"ok": True}).encode())

    monkeypatch.setattr(notify_mod.urllib.request, "urlopen", send)
    assert notify_mod.flush() == 1
    assert seen == ["doomed", "fine"]
    assert read_outbox(fake_home) == []


def test_flush_without_a_channel_keeps_the_queue(notify_mod, fake_home):
    notify_mod._outbox_append("hold me", False)
    assert notify_mod.flush() == 0
    assert len(notify_mod._outbox_read()) == 1, "a missing channel is not the queue's fault"


def test_flush_on_an_empty_outbox_says_nothing(notify_mod, fake_home):
    assert notify_mod.flush() == 0
    assert read_log(fake_home) == ""


def test_cli_flush_exits_zero_even_with_a_dead_link(notify_mod, fake_home, monkeypatch):
    """watchdog-check.sh calls this at the end of a run; it must never colour
    that run's exit status."""
    write_secrets(fake_home)
    notify_mod._outbox_append("queued", False)
    monkeypatch.setattr(notify_mod.urllib.request, "urlopen", flaky(99))
    monkeypatch.setattr(notify_mod.sys, "argv", ["notify.py", "--flush"])
    assert notify_mod.main() == 0
    assert len(notify_mod._outbox_read()) == 1


# ------------------------------------------------------------------ outbox limits
def test_outbox_is_capped_at_200_entries_dropping_oldest(notify_mod, fake_home):
    for i in range(250):
        notify_mod._outbox_append(f"msg-{i}", False)
    entries = read_outbox(fake_home)
    assert len(entries) == 200
    assert entries[0]["message"] == "msg-50"
    assert entries[-1]["message"] == "msg-249", "the newest alert is the one worth keeping"


def test_outbox_is_capped_at_64kb(notify_mod, fake_home):
    for i in range(60):
        notify_mod._outbox_append(f"{i:03d}-" + "x" * 2000, False)
    assert outbox_path(fake_home).stat().st_size <= 64 * 1024
    assert read_outbox(fake_home)[-1]["message"].startswith("059-")


def test_outbox_is_private(notify_mod, fake_home):
    notify_mod._outbox_append("not for other users", False)
    assert oct(outbox_path(fake_home).stat().st_mode & 0o777) == "0o600"


def test_token_never_appears_in_the_outbox(notify_mod, fake_home, monkeypatch, no_backoff):
    write_secrets(fake_home)
    monkeypatch.setattr(notify_mod.urllib.request, "urlopen", flaky(99))
    notify_mod.notify("carrying a secret")
    assert TOKEN not in outbox_path(fake_home).read_text()


def test_corrupt_outbox_line_does_not_wedge_the_queue(notify_mod, fake_home):
    """A half-written line from a power cut must not block every later drain."""
    path = outbox_path(fake_home)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('{"message": "good", "silent": false}\n{"message": "trunc\n')
    assert [e["message"] for e in notify_mod._outbox_read()] == ["good"]


def test_missing_state_dir_is_created_not_fatal(notify_mod, fake_home):
    """A fresh machine has no ~/.local/state — queueing must create it."""
    assert not outbox_path(fake_home).parent.exists()
    notify_mod._outbox_append("cold start", False)
    assert len(read_outbox(fake_home)) == 1
