"""Tests for bin/nightly-triage.py — the deterministic nightly brief.

The brief exists to be trusted at 07:00 by someone who was asleep at 03:15, so
the properties that matter are:

  1. It is computed, never generated. There is no model in this job, and the
     rendering step is pure — same facts in, same bytes out.
  2. It reuses collect_blockers() rather than reimplementing it, so the brief
     and STATUS.md cannot disagree about whether the machine is healthy.
  3. Silence is earned: it only interrupts Lukas when something needs him.

(The dash in the filename means we load it via importlib, as with the status
generator.)
"""
import importlib.util
import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


def load(name):
    spec = importlib.util.spec_from_file_location(
        name.replace("-", "_"), REPO / "bin" / f"{name}.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def triage():
    return load("nightly-triage")


def facts(**over):
    base = {
        "day": "2026-08-04",
        "blockers": [],
        "repos": [{"name": "workbench", "tests": {"state": "pass", "passed": 117},
                   "commits": ["09:00  did a thing"]}],
        "watchdog": {"runs": 96, "runs_with_failures": 0, "alerts": 0,
                     "undelivered": 0, "recovered": 0},
        "notify": {"sent": 2, "failed": 0, "queued": 0, "nochannel": 0},
    }
    base.update(over)
    return base


# ------------------------------------------------------------------ determinism
def test_the_same_facts_render_the_same_bytes(triage):
    """A wrong brief should be a bug with a reproduction, not an unlucky roll.
    This is the property the cut model could never have offered."""
    f = facts()
    assert triage.render(f) == triage.render(f)


def test_render_touches_nothing(triage, monkeypatch):
    """render() must be pure — no subprocess, no filesystem, no network. If it
    reaches for any of those, the brief stops being reproducible."""
    def explode(*a, **k):
        raise AssertionError("render() must not shell out")

    monkeypatch.setattr(triage.subprocess, "run", explode)
    triage.render(facts())


# ------------------------------------------------------------------- the verdict
def test_a_quiet_day_says_nothing_needs_a_human(triage):
    out = triage.render(facts())
    assert "**Nothing needs a human.**" in out


def test_blockers_are_listed_verbatim(triage):
    out = triage.render(facts(blockers=["**Tests red in `workbench`**", "disk full"]))
    assert "**2 thing(s) need a human.**" in out
    assert "- **Tests red in `workbench`**" in out
    assert "- disk full" in out


def test_a_silent_watchdog_is_itself_the_finding(triage):
    """Zero runs is not "nothing happened" — the box's own alarm was off."""
    out = triage.render(facts(watchdog={"runs": 0, "runs_with_failures": 0, "alerts": 0,
                                        "undelivered": 0, "recovered": 0}))
    assert "did not run at all" in out


def test_a_dead_channel_is_called_out(triage):
    out = triage.render(facts(notify={"sent": 0, "failed": 0, "queued": 0, "nochannel": 3}))
    assert "nowhere to go" in out


def test_undelivered_alerts_are_surfaced(triage):
    out = triage.render(facts(watchdog={"runs": 96, "runs_with_failures": 2, "alerts": 1,
                                        "undelivered": 1, "recovered": 0}))
    assert "could not be delivered" in out


def test_the_brief_says_it_is_computed(triage):
    """The provenance line is the point of the job, not decoration."""
    assert "Computed, not generated" in triage.render(facts())


# ---------------------------------------------------------------- log summaries
def test_log_rows_keeps_only_the_named_day(triage, tmp_path):
    log = tmp_path / "watchdog.log"
    log.write_text(
        "2026-08-03T23:59:00+02:00\trun complete: 0 failing\n"
        "2026-08-04T00:01:00+02:00\trun complete: 0 failing\n"
        "2026-08-04T23:58:00+02:00\trun complete: 1 failing\n"
        "2026-08-05T00:02:00+02:00\trun complete: 0 failing\n"
    )
    assert len(triage.log_rows(log, "2026-08-04")) == 2


def test_log_rows_skips_torn_lines(triage, tmp_path):
    """A line cut in half by a power cut must not cost the whole brief."""
    log = tmp_path / "notify.log"
    log.write_text(
        "2026-08-04T10:00:00+02:00\tSENT\thello\n"
        "not a log line at all\n"
        "2026-08-04T10:0\n"
        "2026-08-04T11:00:00+02:00\tSENT\tworld\n"
    )
    assert len(triage.log_rows(log, "2026-08-04")) == 2


def test_log_rows_on_a_missing_file_is_empty_not_an_error(triage, tmp_path):
    assert triage.log_rows(tmp_path / "nope.log", "2026-08-04") == []


def test_watchdog_summary_counts_each_kind(triage):
    rows = [
        ["run complete: 0 failing"],
        ["run complete: 2 failing"],
        ["ALERT hb:scraper - stale"],
        ["ALERT-UNDELIVERED hb:scraper - stale"],
        ["RECOVERED hb:scraper - running again"],
    ]
    s = triage.summarise_watchdog(rows)
    assert s == {"runs": 2, "runs_with_failures": 1, "alerts": 1,
                 "undelivered": 1, "recovered": 1}


def test_notify_summary_understands_the_outbox_statuses(triage):
    """SENT(outbox) is a delivery; FAILED(...)+QUEUED is one failure that was
    also queued, not two separate events."""
    rows = [
        ["SENT", "a"],
        ["SENT(outbox)", "b"],
        ["FAILED(TimeoutError)+QUEUED", "c"],
        ["FAILED(http=401)", "d"],
        ["NOCHANNEL", "e"],
    ]
    s = triage.summarise_notify(rows)
    assert s == {"sent": 2, "failed": 2, "queued": 1, "nochannel": 1}


# --------------------------------------------------------------------- commits
def git_repo(path, commits, day="2026-08-04"):
    subprocess.run(["git", "init", "-q", "-b", "main", str(path)], check=True)
    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    for i, msg in enumerate(commits):
        (path / f"f{i}.txt").write_text(str(i))
        subprocess.run(["git", "add", "-A"], cwd=path, check=True, env=env)
        stamp = f"{day}T10:{i:02d}:00"
        subprocess.run(
            ["git", "commit", "-q", "-m", msg], cwd=path, check=True,
            env={**env, "GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp},
        )


def test_commits_for_day_excludes_status_commits(triage, tmp_path):
    """The publisher amends one status commit forward every 30 minutes. A brief
    that leads with those buries the commits that mean something."""
    git_repo(tmp_path, ["real work", "Status: 04 Aug 15:40", "more real work"])
    got = triage.commits_for_day(tmp_path, "2026-08-04")
    assert len(got) == 2
    assert not any("Status:" in c for c in got)


def test_commits_for_day_reads_oldest_first(triage, tmp_path):
    git_repo(tmp_path, ["first", "second", "third"])
    got = triage.commits_for_day(tmp_path, "2026-08-04")
    assert [c.split("  ", 1)[1] for c in got] == ["first", "second", "third"]


def test_commits_for_a_day_with_none_is_empty(triage, tmp_path):
    git_repo(tmp_path, ["only commit"], day="2026-08-04")
    assert triage.commits_for_day(tmp_path, "2026-07-01") == []


def test_a_directory_that_is_not_a_repo_does_not_raise(triage, tmp_path):
    assert triage.commits_for_day(tmp_path, "2026-08-04") == []


# ------------------------------------------------------------------ interrupting
def test_a_quiet_night_writes_the_report_but_stays_silent(triage, tmp_path, monkeypatch):
    """A nightly "nothing happened" buzz teaches its own reader to ignore it."""
    sent = []
    monkeypatch.setattr(triage, "REPO", tmp_path)
    monkeypatch.setattr(triage, "HEARTBEAT", tmp_path / "hb" / "triage")
    monkeypatch.setattr(triage, "_notify", lambda m: sent.append(m))
    monkeypatch.setattr(triage, "gather", lambda day, quick=False: facts(day=day))
    monkeypatch.setattr(triage.sys, "argv", ["nightly-triage.py", "--day", "2026-08-04"])

    assert triage.main() == 0
    assert (tmp_path / "reports" / "nightly" / "2026-08-04.md").is_file()
    assert sent == []


def test_a_night_with_blockers_interrupts_once(triage, tmp_path, monkeypatch):
    sent = []
    monkeypatch.setattr(triage, "REPO", tmp_path)
    monkeypatch.setattr(triage, "HEARTBEAT", tmp_path / "hb" / "triage")
    monkeypatch.setattr(triage, "_notify", lambda m: sent.append(m))
    monkeypatch.setattr(triage, "gather",
                        lambda day, quick=False: facts(day=day, blockers=["tests are red"]))
    monkeypatch.setattr(triage.sys, "argv", ["nightly-triage.py", "--day", "2026-08-04"])

    assert triage.main() == 0
    assert len(sent) == 1
    assert "tests are red" in sent[0]


def test_the_heartbeat_is_written_on_success(triage, tmp_path, monkeypatch):
    hb = tmp_path / "hb" / "triage"
    monkeypatch.setattr(triage, "REPO", tmp_path)
    monkeypatch.setattr(triage, "HEARTBEAT", hb)
    monkeypatch.setattr(triage, "_notify", lambda m: None)
    monkeypatch.setattr(triage, "gather", lambda day, quick=False: facts(day=day))
    monkeypatch.setattr(triage.sys, "argv", ["nightly-triage.py", "--day", "2026-08-04"])

    triage.main()
    assert hb.is_file()


def test_a_broken_telegram_does_not_fail_the_run(triage, tmp_path, monkeypatch):
    """The brief was written and will be published either way. Losing the buzz
    must not report the whole night as failed — notify.py has already queued it
    for the next retry."""
    import notify as notify_mod

    def boom(*a, **k):
        raise RuntimeError("telegram is down")

    monkeypatch.setattr(notify_mod, "notify", boom)
    monkeypatch.setattr(triage, "REPO", tmp_path)
    monkeypatch.setattr(triage, "HEARTBEAT", tmp_path / "hb" / "triage")
    monkeypatch.setattr(triage, "gather",
                        lambda day, quick=False: facts(day=day, blockers=["something"]))
    monkeypatch.setattr(triage.sys, "argv", ["nightly-triage.py", "--day", "2026-08-04"])

    assert triage.main() == 0
    assert (tmp_path / "reports" / "nightly" / "2026-08-04.md").is_file()
    assert (tmp_path / "hb" / "triage").is_file(), "the run genuinely succeeded"
