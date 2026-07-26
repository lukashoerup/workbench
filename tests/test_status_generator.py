"""Unit tests for workbench-status.py collectors (the dash in the filename
means we load it via importlib rather than a plain import)."""
import importlib.util
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


def git(repo, *args):
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.strip()


def load_status_mod():
    spec = importlib.util.spec_from_file_location(
        "workbench_status", REPO / "bin" / "workbench-status.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_repo_without_tests_dir_reports_none(tmp_path):
    mod = load_status_mod()
    assert mod.collect_tests(tmp_path) == {"state": "none"}


def test_node_repo_is_external_not_a_bogus_pytest_run(tmp_path):
    """A package.json repo (erhvervsklubben) must never have pytest run against
    it by the status timer — its suite needs npm + the Docker Supabase stack."""
    (tmp_path / "tests").mkdir()
    (tmp_path / "package.json").write_text("{}")
    mod = load_status_mod()
    assert mod.collect_tests(tmp_path) == {"state": "external"}


def test_erhvervsklubben_is_watched():
    mod = load_status_mod()
    assert any(r.name == "erhvervsklubben" for r in mod.REPOS)


# --------------------------------------------------------------- needs you
#
# collect_blockers is pure, so every escalation is testable with a hand-built
# facts dict and no machine at all. That is the point of the split: the section
# Lukas actually reads used to be the least testable part of the page.

NOW = datetime.fromisoformat("2026-07-26T14:00:00+02:00")


def facts(**over):
    base = {
        "now": NOW,
        "quick": False,
        "repos": [],
        "watchdog_tail": "(no log yet)",
        "notify_tail": "(no log yet)",
        "setup": [],
    }
    base.update(over)
    return base


def repo(name="workbench", *, dirty="", unpushed="", tests=None):
    return {"name": name, "path": None,
            "git": {"dirty": dirty, "unpushed": unpushed},
            "tests": tests}


def test_all_clear_produces_no_blockers():
    mod = load_status_mod()
    assert mod.collect_blockers(facts(repos=[repo(tests={"state": "pass"})])) == []


def test_blockers_is_pure_and_touches_nothing(monkeypatch):
    """It must be safe to call with no machine underneath — that is what makes
    the section Lukas reads testable from a cloud session."""
    mod = load_status_mod()
    monkeypatch.setattr(mod, "run", lambda *a, **k: pytest.fail("collect_blockers ran a probe"))
    mod.collect_blockers(facts(repos=[repo(tests={"state": "pass"})]))


def test_failing_tests_are_escalated():
    mod = load_status_mod()
    out = mod.collect_blockers(facts(repos=[
        repo(tests={"state": "fail", "failed": 3, "passed": 53})]))
    assert any("Tests red" in b and "3 failing" in b for b in out), out


def test_uncommitted_and_unpushed_work_is_escalated():
    mod = load_status_mod()
    out = mod.collect_blockers(facts(repos=[
        repo(dirty="?? a.py\n M b.py", unpushed="abc123 wip", tests={"state": "pass"})]))
    assert any("2 uncommitted file(s)" in b for b in out), out
    assert any("1 unpushed commit(s)" in b for b in out), out


def test_watchdog_reporting_failures_is_escalated():
    mod = load_status_mod()
    out = mod.collect_blockers(facts(
        watchdog_tail="2026-07-26T13:54:16+02:00\trun complete: 2 failing"))
    assert any("2 failing check(s)" in b for b in out), out


def test_a_clean_watchdog_run_is_not_a_blocker():
    mod = load_status_mod()
    out = mod.collect_blockers(facts(
        watchdog_tail="2026-07-26T13:54:16+02:00\trun complete: 0 failing"))
    assert out == [], out


def test_a_silent_watchdog_is_escalated():
    """The alarm going quiet looks identical to everything being fine."""
    mod = load_status_mod()
    stale = (NOW - timedelta(hours=3)).isoformat(timespec="seconds")
    out = mod.collect_blockers(facts(watchdog_tail=f"{stale}\trun complete: 0 failing"))
    assert any("has not run in 180 min" in b for b in out), out


def test_a_broken_notification_channel_is_escalated():
    """notify.py degrades to a log line and returns False by design, so a dead
    Telegram channel is silent — and it hides every other alert on the box."""
    mod = load_status_mod()
    recent = (NOW - timedelta(minutes=5)).isoformat(timespec="seconds")
    out = mod.collect_blockers(facts(
        notify_tail=f"{recent}\tFAILED(URLError)\tsomething broke"))
    assert any("machine's voice is broken" in b for b in out), out


def test_an_old_notification_failure_is_not_escalated():
    """A blip last week is history, not a blocker."""
    mod = load_status_mod()
    old = (NOW - timedelta(days=4)).isoformat(timespec="seconds")
    out = mod.collect_blockers(facts(notify_tail=f"{old}\tNOCHANNEL\troutine check"))
    assert out == [], out


def test_quick_mode_says_tests_were_not_measured():
    """Silence would read as green on a phone."""
    mod = load_status_mod()
    out = mod.collect_blockers(facts(quick=True, repos=[repo(tests=None)]))
    assert any("not measured" in b for b in out), out


def test_operational_failures_sort_above_setup_gaps():
    mod = load_status_mod()
    out = mod.collect_blockers(facts(
        repos=[repo(tests={"state": "fail", "failed": 1, "passed": 0})],
        setup=["**Telegram not configured** — run setup."]))
    assert "Tests red" in out[0]
    assert "Telegram" in out[-1]


# ------------------------------------------------------------- toolchain
def test_a_tool_outside_path_is_still_found(tmp_path, monkeypatch):
    """The original bug: an ssh non-login shell and a systemd unit both run
    without ~/.local/bin on PATH, so `command -v uv` reported uv missing while
    it was demonstrably running the test suite. The same probe decides whether
    Claude Code is on the box, so a false negative there is load-bearing."""
    mod = load_status_mod()
    hidden = tmp_path / "hidden-bin"
    hidden.mkdir()
    tool = hidden / "uv"
    tool.write_text("#!/bin/sh\n")
    tool.chmod(0o755)

    monkeypatch.setattr(mod.shutil, "which", lambda n: None)
    monkeypatch.setattr(mod, "TOOL_DIRS", [hidden])
    assert mod.find_tool("uv") == str(tool)


def test_a_genuinely_absent_tool_reports_absent(tmp_path, monkeypatch):
    """Absence must mean absence — otherwise the fix trades one wrong answer
    for another."""
    mod = load_status_mod()
    monkeypatch.setattr(mod.shutil, "which", lambda n: None)
    monkeypatch.setattr(mod, "TOOL_DIRS", [tmp_path])
    assert mod.find_tool("definitely-not-installed") is None


def test_a_non_executable_file_is_not_a_tool(tmp_path, monkeypatch):
    mod = load_status_mod()
    (tmp_path / "uv").write_text("not executable\n")
    monkeypatch.setattr(mod.shutil, "which", lambda n: None)
    monkeypatch.setattr(mod, "TOOL_DIRS", [tmp_path])
    assert mod.find_tool("uv") is None


def test_commit_dates_show_when_the_commit_landed_not_when_it_was_authored(tmp_path):
    """publish-status.sh collapses status commits with --amend, which keeps the
    author date and moves only the committer date. Reporting the author date
    made the page show commits days older than they actually were."""
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "config", "user.name", "Test")
    (tmp_path / "f.txt").write_text("x\n")
    git(tmp_path, "add", "-A")
    subprocess.run(
        ["git", "commit", "-q", "-m", "Status: old author date"],
        cwd=tmp_path, check=True,
        env={
            "PATH": "/usr/bin:/bin",
            "HOME": str(tmp_path),
            "GIT_AUTHOR_DATE": "2020-01-02T03:04:05",
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_DATE": "2026-07-26T13:55:00",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        },
    )

    log = load_status_mod().collect_git(tmp_path)["log"]
    assert "26 Jul 13:55" in log, f"expected the committer date, got: {log}"
    assert "02 Jan" not in log, f"author date leaked into the page: {log}"


def test_commits_from_other_timezones_render_in_local_time(tmp_path, monkeypatch):
    """Plain `--date=format:` renders each commit in its own zone, so commits
    made in a cloud container (UTC) sat above commits made on the box (CEST)
    while reading as earlier — the published list looked shuffled."""
    monkeypatch.setenv("TZ", "UTC")
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "config", "user.name", "Test")
    (tmp_path / "f.txt").write_text("x\n")
    git(tmp_path, "add", "-A")
    subprocess.run(
        ["git", "commit", "-q", "-m", "Committed far from here"],
        cwd=tmp_path, check=True,
        env={
            "PATH": "/usr/bin:/bin", "HOME": str(tmp_path), "TZ": "UTC",
            "GIT_AUTHOR_NAME": "Test", "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test", "GIT_COMMITTER_EMAIL": "test@example.com",
            # 18:00 in UTC+09:00 is 09:00 UTC. Rendered in its own zone it
            # would read 18:00; rendered locally it must read 09:00.
            "GIT_COMMITTER_DATE": "2026-07-26T18:00:00+09:00",
            "GIT_AUTHOR_DATE": "2026-07-26T18:00:00+09:00",
        },
    )

    log = load_status_mod().collect_git(tmp_path)["log"]
    assert "09:00" in log, f"expected local time, got: {log}"
    assert "18:00" not in log, f"rendered in the commit's own timezone: {log}"
