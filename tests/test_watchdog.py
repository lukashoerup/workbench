"""Tests for bin/watchdog-check.sh.

The watchdog is the only thing that will notice a scraper dying silently at
04:00, so the properties that matter are:

  1. A stale or missing heartbeat is caught.
  2. Alerts are edge-triggered — a service down for a week must not send 672
     messages. One on the way down, one on the way back up.
  3. A not-yet-installed service is MISSING, not FAILED. The config lists
     Phase 2+ units before they exist.
  4. Exit status is honest: 0 all clear, 1 something is wrong.

Everything is driven through HOME, which is the script's only path root.
"""
import os
import subprocess
import textwrap
import time
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "bin" / "watchdog-check.sh"


@pytest.fixture
def wd(tmp_path):
    """Isolated watchdog: fake HOME, stub notifier that records its messages."""
    (tmp_path / "logs").mkdir()
    (tmp_path / "bin").mkdir()
    (tmp_path / ".config" / "workbench").mkdir(parents=True)

    sent = tmp_path / "sent.txt"
    stub = tmp_path / "bin" / "notify.py"
    stub.write_text(
        textwrap.dedent(
            f"""\
            #!/usr/bin/env python3
            import sys
            with open({str(sent)!r}, "a") as fh:
                fh.write(" ".join(sys.argv[1:]) + "\\n")
            """
        )
    )
    stub.chmod(0o755)

    class Harness:
        home = tmp_path
        conf = tmp_path / ".config" / "workbench" / "watchdog.conf"

        def write_conf(self, text):
            self.conf.write_text(textwrap.dedent(text))

        def run(self, *args):
            env = {**os.environ, "HOME": str(tmp_path)}
            return subprocess.run(
                ["bash", str(SCRIPT), *args],
                env=env, capture_output=True, text=True, timeout=60,
            )

        @property
        def sent(self):
            return sent.read_text().splitlines() if sent.exists() else []

        def heartbeat(self, name, age_seconds=0):
            hb = tmp_path / "hb" / name
            hb.parent.mkdir(exist_ok=True)
            hb.touch()
            if age_seconds:
                old = time.time() - age_seconds
                os.utime(hb, (old, old))
            return hb

    return Harness()


# ------------------------------------------------------------------ heartbeats
def test_fresh_heartbeat_passes_silently(wd):
    hb = wd.heartbeat("scraper", age_seconds=60)
    wd.write_conf(f"heartbeat scraper {hb} 3600\n")
    result = wd.run()
    assert result.returncode == 0
    assert wd.sent == []


def test_stale_heartbeat_alerts_and_fails(wd):
    hb = wd.heartbeat("scraper", age_seconds=7200)
    wd.write_conf(f"heartbeat scraper {hb} 3600\n")
    result = wd.run()
    assert result.returncode == 1
    assert len(wd.sent) == 1
    assert "stale" in wd.sent[0]
    assert "scraper" in wd.sent[0]


def test_never_run_heartbeat_alerts(wd):
    missing = wd.home / "hb" / "never"
    wd.write_conf(f"heartbeat never {missing} 3600\n")
    result = wd.run()
    assert result.returncode == 1
    assert "never run" in wd.sent[0]


# -------------------------------------------------------------- edge triggering
def test_repeat_failure_within_cooldown_does_not_realert(wd):
    hb = wd.heartbeat("scraper", age_seconds=7200)
    wd.write_conf(f"heartbeat scraper {hb} 3600\n")

    assert wd.run().returncode == 1
    assert wd.run().returncode == 1
    assert wd.run().returncode == 1

    assert len(wd.sent) == 1, f"expected one alert, got: {wd.sent}"


def test_recovery_sends_exactly_one_message(wd):
    hb = wd.heartbeat("scraper", age_seconds=7200)
    wd.write_conf(f"heartbeat scraper {hb} 3600\n")
    wd.run()

    hb.touch()  # job runs again
    assert wd.run().returncode == 0

    assert len(wd.sent) == 2
    assert "Recovered" in wd.sent[1]

    wd.run()  # still healthy — must stay quiet
    assert len(wd.sent) == 2


def test_healthy_from_the_start_never_mentions_recovery(wd):
    hb = wd.heartbeat("scraper", age_seconds=10)
    wd.write_conf(f"heartbeat scraper {hb} 3600\n")
    wd.run()
    wd.run()
    assert wd.sent == []


# -------------------------------------------------------------------- units
def test_uninstalled_unit_is_missing_not_a_failure(wd):
    wd.write_conf("unit definitely-not-a-real-unit-xyz.service\n")
    result = wd.run()
    assert result.returncode == 0
    assert wd.sent == []
    assert "MISSING" in (wd.home / "logs" / "watchdog.log").read_text()


# --------------------------------------------------------------------- disk
def test_disk_check_passes_with_a_reachable_floor(wd):
    wd.write_conf("disk / 0\n")
    assert wd.run().returncode == 0


def test_disk_check_fails_against_an_impossible_floor(wd):
    wd.write_conf("disk / 100\n")
    result = wd.run()
    assert result.returncode == 1
    assert "free" in wd.sent[0]


def test_unstattable_mount_is_missing_not_a_failure(wd):
    wd.write_conf("disk /no/such/mount 10\n")
    assert wd.run().returncode == 0


# ------------------------------------------------------------------- parsing
def test_comments_and_blank_lines_are_ignored(wd):
    hb = wd.heartbeat("scraper", age_seconds=10)
    wd.write_conf(
        f"""\
        # a comment

           # indented comment
        heartbeat scraper {hb} 3600
        """
    )
    assert wd.run().returncode == 0


def test_unknown_check_kind_is_logged_not_fatal(wd):
    wd.write_conf("banana / 10\n")
    result = wd.run()
    assert result.returncode == 0
    assert "unknown check kind" in (wd.home / "logs" / "watchdog.log").read_text()


def test_absent_config_exits_clean(wd):
    assert wd.run().returncode == 0


def test_multiple_checks_report_independently(wd):
    good = wd.heartbeat("good", age_seconds=10)
    bad = wd.heartbeat("bad", age_seconds=99999)
    wd.write_conf(
        f"""\
        heartbeat good {good} 3600
        heartbeat bad {bad} 3600
        disk / 0
        """
    )
    result = wd.run()
    assert result.returncode == 1
    assert len(wd.sent) == 1
    assert "bad" in wd.sent[0]


# ---------------------------------------------------------------------- --test
def test_test_flag_reports_delivery_failure_honestly(wd, tmp_path):
    """A test alert that cannot be delivered must not exit 0."""
    (tmp_path / "bin" / "notify.py").write_text("#!/usr/bin/env python3\nimport sys; sys.exit(1)\n")
    (tmp_path / "bin" / "notify.py").chmod(0o755)
    result = wd.run("--test")
    assert result.returncode == 1
    assert "Not delivered" in result.stdout


def test_test_flag_succeeds_when_delivery_works(wd):
    result = wd.run("--test")
    assert result.returncode == 0
    assert len(wd.sent) == 1
    assert "test alert" in wd.sent[0].lower()


# ------------------------------------------- regressions (fable review 2026-07-22)
def statefile(wd, key):
    safe = "".join(c if c.isalnum() or c in "._-" else "_" for c in key)
    return wd.home / ".local" / "state" / "workbench" / "watchdog" / safe


def test_corrupt_state_file_does_not_wedge_the_check(wd):
    """A mangled timestamp must not abort the branch and mute the check forever."""
    hb = wd.heartbeat("scraper", age_seconds=7200)
    wd.write_conf(f"heartbeat scraper {hb} 3600\n")
    wd.run()

    sf = statefile(wd, "hb:scraper")
    sf.write_text("fail 12:34\n")

    result = wd.run()
    assert result.returncode == 1
    assert len(wd.sent) == 2, "corrupt state should reset, not silence the check"


def test_future_timestamp_does_not_mute_alerts(wd):
    """RTC ahead of NTP after reboot must not suppress alerts for hours."""
    hb = wd.heartbeat("scraper", age_seconds=7200)
    wd.write_conf(f"heartbeat scraper {hb} 3600\n")
    wd.run()

    sf = statefile(wd, "hb:scraper")
    sf.write_text(f"fail {int(time.time()) + 86400}\n")

    assert wd.run().returncode == 1
    assert len(wd.sent) == 2


def test_cooldown_expiry_sends_exactly_one_repeat(wd):
    """Suppression must expire. Without this, a week-long outage sends either
    one message or hundreds, and the suite cannot tell which."""
    hb = wd.heartbeat("scraper", age_seconds=7200)
    wd.write_conf(f"heartbeat scraper {hb} 3600\n")
    wd.run()
    assert len(wd.sent) == 1

    sf = statefile(wd, "hb:scraper")
    sf.write_text(f"fail {int(time.time()) - 8 * 3600}\n")   # older than the 6h cooldown

    assert wd.run().returncode == 1
    assert len(wd.sent) == 2, "cooldown should have expired"

    assert wd.run().returncode == 1
    assert len(wd.sent) == 2, "and then go quiet again"


def test_undelivered_alert_does_not_start_the_cooldown(wd, tmp_path):
    """Wi-Fi drops are a common cause of failing checks. If the alert about it
    is lost, the incident must not be buried for 6 hours."""
    stub = tmp_path / "bin" / "notify.py"
    stub.write_text("#!/usr/bin/env python3\nimport sys; sys.exit(1)\n")
    stub.chmod(0o755)

    hb = wd.heartbeat("scraper", age_seconds=7200)
    wd.write_conf(f"heartbeat scraper {hb} 3600\n")

    assert wd.run().returncode == 1
    log = (wd.home / "logs" / "watchdog.log").read_text()
    assert "ALERT-UNDELIVERED" in log

    sf = statefile(wd, "hb:scraper")
    assert sf.read_text().split()[1] == "0", "must not enter cooldown on a lost alert"


# --------------------------------------------------- outbox drain (2026-08-04)
def outbox(wd):
    path = wd.home / ".local" / "state" / "workbench" / "outbox.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def test_a_queued_message_is_drained_at_the_end_of_a_run(wd):
    """The watchdog tick is what empties the outbox on a silent box — without
    it a queued message waits for the next thing that happens to notify."""
    outbox(wd).write_text('{"message": "queued while offline", "silent": false}\n')
    hb = wd.heartbeat("scraper", age_seconds=10)
    wd.write_conf(f"heartbeat scraper {hb} 3600\n")

    assert wd.run().returncode == 0
    assert wd.sent == ["--flush"]


def test_an_empty_outbox_does_not_spawn_the_notifier(wd):
    """96 interpreter starts a day on a CPU-only box, for nothing."""
    outbox(wd).write_text("")
    hb = wd.heartbeat("scraper", age_seconds=10)
    wd.write_conf(f"heartbeat scraper {hb} 3600\n")

    assert wd.run().returncode == 0
    assert wd.sent == []


def test_draining_does_not_change_the_exit_status(wd, tmp_path):
    """A failing flush must not turn a clean run red, nor a red run clean."""
    stub = tmp_path / "bin" / "notify.py"
    stub.write_text("#!/usr/bin/env python3\nimport sys; sys.exit(1)\n")
    stub.chmod(0o755)
    outbox(wd).write_text('{"message": "stuck", "silent": false}\n')

    good = wd.heartbeat("good", age_seconds=10)
    wd.write_conf(f"heartbeat good {good} 3600\n")
    assert wd.run().returncode == 0

    bad = wd.heartbeat("bad", age_seconds=99999)
    wd.write_conf(f"heartbeat bad {bad} 3600\n")
    assert wd.run().returncode == 1


def test_user_scope_keyword_is_recognised(wd):
    """Everything interesting on this box is a --user unit. A typo here means a
    config full of silently-ignored checks reporting all-clear."""
    wd.write_conf("user definitely-not-a-real-unit-xyz.service\n")
    result = wd.run()
    log = (wd.home / "logs" / "watchdog.log").read_text()
    assert "unknown check kind" not in log
    assert "MISSING" in log
