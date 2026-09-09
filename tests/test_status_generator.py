"""Unit tests for workbench-status.py collectors (the dash in the filename
means we load it via importlib rather than a plain import).

The property under test throughout: the page may only say "all clear" when
every check was measured and none failed. Absent evidence, a runner that is
not there, a suite that never finished, a repo that is not checked out — each
must surface as *unknown*, never fold into green, and never be dressed up with
an invented explanation.
"""
import importlib.util
import json
import os
import subprocess
import sys
import textwrap
from datetime import datetime, timedelta
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "bin" / "workbench-status.py"


def git(repo, *args):
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.strip()


def load_status_mod():
    spec = importlib.util.spec_from_file_location("workbench_status", SCRIPT)
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


# ------------------------------------------------------------ test verdicts
#
# collect_tests used to grep the output for "passed" and "failed" and throw
# the exit code away. pytest's "1 passed, 1 error" exits 1 — a fixture that
# blows up on teardown — and the page called it a pass. Every verdict below is
# a probe result the box has actually produced, fed through the real parser.

def pytest_repo(tmp_path):
    (tmp_path / "tests").mkdir(exist_ok=True)
    return tmp_path


def fake_probe(mod, monkeypatch, *, rc=None, out="", error=None):
    """Stand in for the subprocess: what pytest printed and how it exited."""
    calls = []

    def _probe(cmd, cwd=None, timeout=None):
        calls.append(cmd)
        return mod.Probe(rc, out, error)

    monkeypatch.setattr(mod, "probe", _probe)
    monkeypatch.setattr(mod, "find_tool", lambda name: "/fake/uv")
    return calls


def test_a_teardown_error_with_exit_1_is_a_failure(tmp_path, monkeypatch):
    """The reproduced defect: no "failed" in the output, but pytest counted an
    error and exited 1. Previously reported as pass."""
    mod = load_status_mod()
    fake_probe(mod, monkeypatch, rc=1, out="tests/test_x.py .E\n1 passed, 1 error in 0.05s")
    r = mod.collect_tests(pytest_repo(tmp_path))
    assert r["state"] == "fail", r
    assert (r["passed"], r["failed"], r["errors"], r["rc"]) == (1, 0, 1, 1)


def test_a_clean_run_is_a_pass_with_its_count(tmp_path, monkeypatch):
    mod = load_status_mod()
    fake_probe(mod, monkeypatch, rc=0, out="....\n87 passed in 8.82s")
    r = mod.collect_tests(pytest_repo(tmp_path))
    assert r["state"] == "pass" and r["passed"] == 87, r


def test_a_nonzero_exit_is_never_a_pass_even_with_a_green_summary(tmp_path, monkeypatch):
    """Interrupted after some tests passed (exit 2): the summary looks green,
    the exit code says the run did not finish. The exit code wins — but this
    is not a *test* failure either, so it is unknown, with the reason."""
    mod = load_status_mod()
    fake_probe(mod, monkeypatch, rc=2, out="3 passed in 0.10s")
    r = mod.collect_tests(pytest_repo(tmp_path))
    assert r["state"] == "unknown", r
    assert "exit code 2" in r["reason"]


def test_a_missing_runner_is_reported_not_passed(tmp_path, monkeypatch):
    mod = load_status_mod()
    monkeypatch.setattr(mod, "find_tool", lambda name: None)
    monkeypatch.setattr(mod, "probe", lambda *a, **k: pytest.fail("ran without a runner"))
    r = mod.collect_tests(pytest_repo(tmp_path))
    assert r["state"] == "no-runner", r


def test_a_runner_that_cannot_execute_is_reported_not_passed(tmp_path, monkeypatch):
    """find_tool says uv is there; exec says otherwise (broken symlink, wrong
    arch). The probe reports "missing" and the verdict must follow it."""
    mod = load_status_mod()
    fake_probe(mod, monkeypatch, error="missing")
    r = mod.collect_tests(pytest_repo(tmp_path))
    assert r["state"] == "no-runner", r


def test_a_timeout_is_reported_not_passed(tmp_path, monkeypatch):
    mod = load_status_mod()
    fake_probe(mod, monkeypatch, out="tests/test_slow.py ...", error="timeout")
    r = mod.collect_tests(pytest_repo(tmp_path))
    assert r["state"] == "timeout", r
    assert str(mod.TEST_TIMEOUT) in r["reason"]


def test_output_without_a_pytest_summary_is_unknown(tmp_path, monkeypatch):
    """`uv run` can fail before pytest starts (venv build, network). Exit 0
    with no summary is just as ambiguous as exit 1 with none."""
    mod = load_status_mod()
    fake_probe(mod, monkeypatch, rc=0, out="Resolved 5 packages\nSomething unrelated")
    assert mod.collect_tests(pytest_repo(tmp_path))["state"] == "unknown"
    fake_probe(mod, monkeypatch, rc=1, out="error: Failed to build the environment")
    r = mod.collect_tests(pytest_repo(tmp_path))
    assert r["state"] == "unknown" and "no pytest summary" in r["reason"], r


def test_nothing_passing_is_not_a_pass(tmp_path, monkeypatch):
    """Everything skipped exits 0; nothing collected exits 5. Neither proves
    anything about the code."""
    mod = load_status_mod()
    fake_probe(mod, monkeypatch, rc=0, out="3 skipped in 0.01s")
    assert mod.collect_tests(pytest_repo(tmp_path))["state"] == "unknown"
    fake_probe(mod, monkeypatch, rc=5, out="no tests ran in 0.01s")
    r = mod.collect_tests(pytest_repo(tmp_path))
    assert r["state"] == "unknown" and "no tests collected" in r["reason"], r


@pytest.mark.parametrize("line,expect", [
    ("87 passed in 8.82s", {"passed": 87, "failed": 0, "errors": 0}),
    ("===== 3 failed, 53 passed in 1.20s =====", {"passed": 53, "failed": 3, "errors": 0}),
    ("1 passed, 2 errors in 0.05s", {"passed": 1, "failed": 0, "errors": 2}),
    ("2 passed, 1 skipped, 1 xfailed, 3 warnings in 90.00s (0:01:30)",
     {"passed": 2, "failed": 0, "errors": 0, "skipped": 1, "xfailed": 1, "warnings": 3}),
    ("\x1b[32m5 passed\x1b[0m in 0.3s", {"passed": 5, "failed": 0, "errors": 0}),
])
def test_pytest_summary_parsing(line, expect):
    mod = load_status_mod()
    assert mod.parse_pytest_summary(f"preamble\n{line}") == expect


def test_a_line_that_merely_mentions_passed_is_not_a_summary():
    mod = load_status_mod()
    out = "tests/test_x.py::test_passed_flag PASSED\nFinished in 3s"
    assert mod.parse_pytest_summary(out) is None


def fake_uv(tmp_path, body):
    """A stand-in `uv` binary: collect_tests calls `uv run pytest ...`."""
    uv = tmp_path / "uv"
    uv.write_text("#!/bin/sh\n" + body)
    uv.chmod(0o755)
    return uv


def test_a_real_teardown_error_is_a_failure_end_to_end(tmp_path, monkeypatch):
    """Not a fake: real pytest, real fixture that dies on teardown, real exit
    code, through the real probe. This is the case that was misreported."""
    mod = load_status_mod()
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    (repo / "tests" / "test_teardown.py").write_text(textwrap.dedent("""
        import pytest

        @pytest.fixture
        def resource():
            yield 1
            raise RuntimeError("teardown broke")

        def test_body_passes(resource):
            assert resource == 1
    """))
    # `shift` drops "run"; the rest is `pytest tests/ -q ...` for the real interpreter.
    uv = fake_uv(tmp_path, f'shift\nexec "{sys.executable}" -m "$@"\n')
    monkeypatch.setattr(mod, "find_tool", lambda name: str(uv))
    r = mod.collect_tests(repo)
    assert r["state"] == "fail", r
    assert (r["passed"], r["errors"], r["rc"]) == (1, 1, 1), r


def test_a_real_timeout_is_reported_end_to_end(tmp_path, monkeypatch):
    mod = load_status_mod()
    uv = fake_uv(tmp_path, "sleep 5\n")
    monkeypatch.setattr(mod, "find_tool", lambda name: str(uv))
    monkeypatch.setattr(mod, "TEST_TIMEOUT", 1)
    r = mod.collect_tests(_mk_repo(tmp_path))
    assert r["state"] == "timeout", r


def _mk_repo(tmp_path):
    repo = tmp_path / "repo"
    (repo / "tests").mkdir(parents=True)
    return repo


def test_a_real_missing_runner_is_reported_end_to_end(tmp_path, monkeypatch):
    mod = load_status_mod()
    monkeypatch.setattr(mod, "find_tool", lambda name: str(tmp_path / "no-such-uv"))
    r = mod.collect_tests(_mk_repo(tmp_path))
    assert r["state"] == "no-runner", r


# --------------------------------------------------------------- needs you
#
# assess()/collect_blockers are pure, so every escalation is testable with a
# hand-built facts dict and no machine at all. That is the point of the split:
# the section Lukas actually reads used to be the least testable part of the
# page.

NOW = datetime.fromisoformat("2026-07-26T14:00:00+02:00")


def ago(**kw):
    return (NOW - timedelta(**kw)).isoformat(timespec="seconds")


def facts(**over):
    """Facts with NO evidence for the watchdog or the notification channel.
    Whatever the repos say, this can never justify an all-clear."""
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


def healthy(**over):
    """Fresh, good evidence for every check — the only facts that do."""
    base = facts(
        repos=[repo(tests={"state": "pass", "passed": 87})],
        watchdog_tail=f"{ago(minutes=5)}\trun complete: 0 failing",
        notify_tail=f"{ago(hours=3)}\tSENT\troutine check",
        heartbeats={"configured": [{"name": "apply", "path": Path("/x/apply"),
                                    "age_min": 5, "limit_min": 40}],
                    "unwatched": [], "error": None},
    )
    base.update(over)
    return base


def repo(name="workbench", *, dirty="", unpushed="", tests=None, **git_over):
    return {"name": name, "path": None, "present": True,
            "git": {"dirty": dirty, "unpushed": unpushed, **git_over},
            "tests": tests}


def statuses(mod, f):
    return {c.name: c.status for c in mod.assess(f)}


def test_all_clear_needs_evidence_for_every_check():
    mod = load_status_mod()
    assert mod.collect_blockers(healthy()) == []
    assert set(statuses(mod, healthy()).values()) == {"ok"}


def test_absent_evidence_is_never_an_all_clear():
    """The old page printed "Nothing. All clear." over a watchdog that had
    never written a log and a notification channel never exercised."""
    mod = load_status_mod()
    out = mod.collect_blockers(facts(repos=[repo(tests={"state": "pass", "passed": 1})]))
    assert out, "no evidence for the watchdog or notifications, yet nothing was flagged"
    st = statuses(mod, facts(repos=[repo(tests={"state": "pass", "passed": 1})]))
    assert st["watchdog"] == "unknown" and st["notifications"] == "unknown", st


def test_blockers_is_pure_and_touches_nothing(monkeypatch):
    """It must be safe to call with no machine underneath — that is what makes
    the section Lukas reads testable from a cloud session."""
    mod = load_status_mod()
    for name in ("run", "probe"):
        monkeypatch.setattr(mod, name, lambda *a, **k: pytest.fail("collect_blockers ran a probe"))
    monkeypatch.setattr(mod.subprocess, "run",
                        lambda *a, **k: pytest.fail("collect_blockers ran a subprocess"))
    mod.collect_blockers(healthy())
    mod.public_summary(healthy())


def test_failing_tests_are_escalated():
    mod = load_status_mod()
    out = mod.collect_blockers(facts(repos=[
        repo(tests={"state": "fail", "failed": 3, "passed": 53})]))
    assert any("Tests red" in b and "3 failing" in b for b in out), out


def test_teardown_errors_are_escalated_as_red():
    mod = load_status_mod()
    f = healthy(repos=[repo(tests={"state": "fail", "failed": 0, "errors": 1, "passed": 1})])
    out = mod.collect_blockers(f)
    assert any("Tests red" in b and "1 error(s)" in b for b in out), out
    assert statuses(mod, f)["tests: workbench"] == "failed"


@pytest.mark.parametrize("tests", [
    {"state": "unknown",
     "reason": "exit code 2 (interrupted) although no test was counted as failing"},
    {"state": "no-runner", "reason": "uv is not installed on this box"},
    {"state": "timeout", "reason": "no verdict within 300 s"},
    {"state": "external"},
    None,
])
def test_a_test_verdict_that_is_not_a_pass_is_unknown_not_failed_and_not_clear(tests):
    """Failed and unknown are different words for different situations. An
    unknown must block the all-clear without claiming the tests are red."""
    mod = load_status_mod()
    f = healthy(repos=[repo(tests=tests)], quick=tests is None)
    st = statuses(mod, f)
    assert st["tests: workbench"] == "unknown", st
    out = mod.collect_blockers(f)
    assert out, "an unmeasured suite left the page all-clear"
    assert not any("Tests red" in b for b in out), out
    assert mod.public_summary(f)["overall"] == "unknown"


def test_external_tests_cannot_imply_all_clear():
    """erhvervsklubben's suite is CI's to run. Its CI was red for four weeks
    while this page said nothing (context/LEARNINGS.md, 2026-09-05)."""
    mod = load_status_mod()
    f = healthy(repos=[repo(tests={"state": "pass", "passed": 87}),
                       repo("erhvervsklubben", tests={"state": "external"})])
    out = mod.collect_blockers(f)
    assert any("CI is the judge" in b for b in out), out
    assert mod.public_summary(f)["overall"] == "unknown"


def test_quick_mode_says_tests_were_not_measured():
    """Silence would read as green on a phone."""
    mod = load_status_mod()
    out = mod.collect_blockers(facts(quick=True, repos=[repo(tests=None)]))
    assert any("not measured" in b for b in out), out
    s = mod.public_summary(facts(quick=True, repos=[repo(tests=None)]))
    assert s["tests_measured"] is False


def test_uncommitted_and_unpushed_work_is_escalated():
    mod = load_status_mod()
    out = mod.collect_blockers(facts(repos=[
        repo(dirty="?? a.py\n M b.py", unpushed="abc123 wip", tests={"state": "pass"})]))
    assert any("2 uncommitted file(s)" in b for b in out), out
    assert any("1 unpushed commit(s)" in b for b in out), out


def test_a_failed_git_probe_is_unknown_not_dirty():
    """run() used to return "(probe failed: ...)" in the dirty field, which then
    counted as one uncommitted file. A failed probe is an unknown, not a fact."""
    mod = load_status_mod()
    f = healthy(repos=[repo(tests={"state": "pass", "passed": 1}, error="missing")])
    out = mod.collect_blockers(f)
    assert not any("uncommitted" in b for b in out), out
    assert any("could not be read" in b for b in out), out
    assert statuses(mod, f)["repository: workbench"] == "unknown"


def test_an_expected_repository_that_is_absent_is_reported():
    """REPOS is the list of what this box is supposed to hold. A missing
    checkout used to be skipped silently, so a wiped clone looked like a
    clean one."""
    mod = load_status_mod()
    missing = {"name": "erhvervsklubben", "path": Path("/nowhere/erhvervsklubben"),
               "present": False, "git": {}, "tests": None}
    f = healthy(repos=[repo(tests={"state": "pass", "passed": 1}), missing])
    out = mod.collect_blockers(f)
    assert any("not checked out" in b for b in out), out
    st = statuses(mod, f)
    assert st["repository: erhvervsklubben"] == "unknown"
    assert "tests: erhvervsklubben" not in st, "nothing to test in an absent checkout"


# ---- watchdog
def test_watchdog_reporting_failures_is_escalated():
    mod = load_status_mod()
    out = mod.collect_blockers(facts(
        watchdog_tail="2026-07-26T13:54:16+02:00\trun complete: 2 failing"))
    assert any("2 failing check(s)" in b for b in out), out


def test_a_clean_watchdog_run_is_not_a_blocker():
    mod = load_status_mod()
    f = healthy(watchdog_tail="2026-07-26T13:54:16+02:00\trun complete: 0 failing")
    assert mod.collect_blockers(f) == []
    assert statuses(mod, f)["watchdog"] == "ok"


def test_a_silent_watchdog_is_escalated():
    """The alarm going quiet looks identical to everything being fine."""
    mod = load_status_mod()
    out = mod.collect_blockers(facts(watchdog_tail=f"{ago(hours=3)}\trun complete: 0 failing"))
    assert any("has not run in 180 min" in b for b in out), out


def test_an_absent_watchdog_log_is_unknown_and_blocks_the_all_clear():
    """No log is the watchdog never having run — at least as bad as silence,
    and it used to produce no blocker at all."""
    mod = load_status_mod()
    f = healthy(watchdog_tail="(no log yet)")
    st = statuses(mod, f)
    assert st["watchdog"] == "unknown", st
    out = mod.collect_blockers(f)
    assert any("Watchdog" in b and "no log exists yet" in b for b in out), out


@pytest.mark.parametrize("tail,why", [
    ("", "the log is empty"),
    ("garbage\nmore garbage", "no parseable entries"),
    ("(unreadable)", "could not be read"),
])
def test_malformed_watchdog_evidence_is_unknown_not_healthy(tail, why):
    mod = load_status_mod()
    f = healthy(watchdog_tail=tail)
    assert statuses(mod, f)["watchdog"] == "unknown"
    assert any(why in b for b in mod.collect_blockers(f))


def test_a_watchdog_without_a_check_list_is_unknown_and_does_not_leak_the_path():
    """watchdog-check.sh logs "no config at <path>" and exits 0 forever. It is
    running, and checking nothing."""
    mod = load_status_mod()
    line = f"{ago(minutes=2)}\tno config at /home/someone/.config/workbench/watchdog.conf"
    f = healthy(watchdog_tail=line)
    checks = {c.name: c for c in mod.assess(f)}
    assert checks["watchdog"].status == "unknown"
    assert "/home/" not in checks["watchdog"].note


def test_the_last_completed_run_decides_even_mid_run():
    """The status timer and the watchdog fire in the same second, so the tail
    can end in ALERT lines from a run still in progress."""
    mod = load_status_mod()
    f = healthy(watchdog_tail="\n".join([
        f"{ago(minutes=16)}\trun complete: 0 failing",
        f"{ago(seconds=3)}\tALERT unit:ollama.service - ollama.service is failed",
    ]))
    assert statuses(mod, f)["watchdog"] == "ok"


# ---- notifications
def test_a_broken_notification_channel_is_escalated():
    """notify.py degrades to a log line and returns False by design, so a dead
    Telegram channel is silent — and it hides every other alert on the box."""
    mod = load_status_mod()
    out = mod.collect_blockers(facts(
        notify_tail=f"{ago(minutes=5)}\tFAILED(URLError)\tsomething broke"))
    assert any("machine's voice is broken" in b for b in out), out


def test_an_old_notification_failure_stays_escalated_until_something_is_delivered():
    """The old rule aged a failure out after an hour. A channel that failed
    four days ago and has delivered nothing since is a channel that is still
    broken — the age is how long Lukas has heard nothing."""
    mod = load_status_mod()
    f = healthy(notify_tail=f"{ago(days=4)}\tNOCHANNEL\troutine check")
    out = mod.collect_blockers(f)
    assert any("machine's voice is broken" in b and "4 days ago" in b for b in out), out
    assert statuses(mod, f)["notifications"] == "failed"


def test_a_later_delivery_establishes_recovery():
    mod = load_status_mod()
    f = healthy(notify_tail="\n".join([
        f"{ago(days=4)}\tFAILED(URLError)\talert that never arrived",
        f"{ago(days=1)}\tSENT\tback online",
    ]))
    assert statuses(mod, f)["notifications"] == "ok"
    assert mod.collect_blockers(f) == []


def test_a_failure_after_a_delivery_is_broken_again():
    mod = load_status_mod()
    f = healthy(notify_tail="\n".join([
        f"{ago(days=1)}\tSENT\tfine then",
        f"{ago(hours=2)}\tFAILED(http=401)\tnot fine now",
    ]))
    assert statuses(mod, f)["notifications"] == "failed"


def test_no_notification_evidence_is_unknown_not_ok():
    mod = load_status_mod()
    f = healthy(notify_tail="(no log yet)")
    assert statuses(mod, f)["notifications"] == "unknown"
    assert mod.collect_blockers(f), "an unexercised channel was reported as fine"


def test_a_garbled_notification_status_is_not_echoed():
    """Whatever ends up in the status column is not ours to republish."""
    mod = load_status_mod()
    f = healthy(notify_tail=f"{ago(minutes=1)}\tWEIRD /home/x/secret\tmsg")
    c = {c.name: c for c in mod.assess(f)}["notifications"]
    assert c.status == "unknown" and "/home/" not in c.note


# ---- heartbeats
def hb(configured, unwatched=(), error=None):
    return {"configured": configured, "unwatched": list(unwatched), "error": error}


def test_an_expected_heartbeat_that_never_ran_is_a_failure():
    mod = load_status_mod()
    f = healthy(heartbeats=hb([{"name": "dba", "path": Path("/x/dba"), "age_min": None,
                                "limit_min": 120}]))
    out = mod.collect_blockers(f)
    assert any("has never run" in b for b in out), out
    assert statuses(mod, f)["heartbeats"] == "failed"


def test_a_stale_heartbeat_is_a_failure_and_a_fresh_one_is_not():
    mod = load_status_mod()
    stale = healthy(heartbeats=hb([{"name": "apply", "path": Path("/x"), "age_min": 90,
                                    "limit_min": 40}]))
    assert statuses(mod, stale)["heartbeats"] == "failed"
    assert statuses(mod, healthy())["heartbeats"] == "ok"


def test_an_unreadable_watchdog_config_makes_expectations_unknown():
    """The old page said "no scrapers are running" when the marker dir was
    missing — an explanation it had no evidence for."""
    mod = load_status_mod()
    f = healthy(heartbeats=hb(None))
    assert statuses(mod, f)["heartbeats"] == "unknown"
    page = mod.render_detailed(full(f))
    assert "no scrapers" not in page
    assert "could not be read" in page


def test_collect_heartbeats_reads_expectations_from_the_config(fake_home, monkeypatch):
    """Real files under a fake HOME: the config names two jobs, one has a
    fresh marker, one has none; a third marker nobody watches sits alongside."""
    monkeypatch.setenv("HOME", str(fake_home))
    mod = load_status_mod()
    markers = fake_home / ".local" / "state" / "workbench" / "heartbeats"
    markers.mkdir(parents=True)
    (markers / "apply").touch()
    (markers / "stray").touch()
    conf = fake_home / ".config" / "workbench" / "watchdog.conf"
    conf.parent.mkdir(parents=True)
    conf.write_text(textwrap.dedent(f"""
        # comment
        user       workbench-apply.timer
        heartbeat  apply  {markers / 'apply'}  2400
        heartbeat  dba    {markers / 'dba'}    7200
    """))
    got = mod.collect_heartbeats(datetime.now().astimezone())
    by_name = {h["name"]: h for h in got["configured"]}
    assert by_name["apply"]["age_min"] == 0 and by_name["apply"]["limit_min"] == 40
    assert by_name["dba"]["age_min"] is None
    assert [u["name"] for u in got["unwatched"]] == ["stray"]
    assert got["error"] is None


def test_collect_heartbeats_without_a_config_says_so(fake_home, monkeypatch):
    monkeypatch.setenv("HOME", str(fake_home))
    mod = load_status_mod()
    got = mod.collect_heartbeats(datetime.now().astimezone())
    assert got["configured"] is None
    assert got["unwatched"] == []


def test_operational_failures_sort_above_setup_gaps():
    mod = load_status_mod()
    out = mod.collect_blockers(facts(
        repos=[repo(tests={"state": "fail", "failed": 1, "passed": 0})],
        setup=["**Telegram not configured** — run setup."]))
    assert "Tests red" in out[0]
    assert "Telegram" in out[-1]


# ------------------------------------------------------------- the page
def full(f, **over):
    """A facts dict with every field the renderers read."""
    base = {
        "hostname": "box",
        "heartbeats": hb([]),
        "timers": "",
        "machine": {"disk": {"total": 100 * 2**30, "free": 60 * 2**30, "used_pct": 40},
                    "memory": {"total": 16 * 2**30, "available": 11 * 2**30},
                    "uptime_s": 90000},
        "toolchain": ["| `uv` | /usr/bin/uv |"],
        "models": "not installed",
        "tasks": ([], []),
    }
    base.update(f)
    base.update(over)
    return base


def test_the_page_claims_all_clear_only_when_everything_was_measured():
    mod = load_status_mod()
    page = mod.render_detailed(full(healthy()))
    assert "none failed" in page and "not an all-clear" not in page
    page = mod.render_detailed(full(healthy(watchdog_tail="(no log yet)")))
    assert "not an all-clear" in page and "none failed" not in page
    assert "Not measured this run (1)" in page


def test_the_page_lists_failures_and_unknowns_separately():
    mod = load_status_mod()
    f = healthy(repos=[repo(tests={"state": "fail", "failed": 2, "passed": 5}),
                       repo("erhvervsklubben", tests={"state": "external"})])
    page = mod.render_detailed(full(f))
    needs = page.split("## Needs you")[1].split("## Repositories")[0]
    assert "Tests red in `workbench`" in needs
    assert "Not measured this run (1)" in needs and "CI is the judge" in needs


# ------------------------------------------------------------- --public
def test_public_summary_has_an_iso_timestamp_and_explicit_unknowns():
    mod = load_status_mod()
    f = full(healthy(repos=[repo(tests={"state": "pass", "passed": 87}),
                            repo("erhvervsklubben", tests={"state": "external"})]))
    s = mod.public_summary(f)
    assert datetime.fromisoformat(s["collected_at"]) == NOW
    assert s["collected_at"] == "2026-07-26T14:00:00+02:00"
    assert s["overall"] == "unknown"
    assert s["failed"] == []
    assert s["unknown"] == ["tests: erhvervsklubben — not run by this machine; CI is the judge"]
    md = mod.render_public(s)
    assert "not an all-clear" in md and "CI is the judge" in md
    assert "2026-07-26T14:00:00+02:00" in md


def test_public_summary_is_all_clear_only_when_supported():
    mod = load_status_mod()
    s = mod.public_summary(full(healthy()))
    assert s["overall"] == "ok" and s["unknown"] == [] and s["failed"] == []
    assert "none failed" in mod.render_public(s)
    unmeasured = {"disk": None, "memory": None, "uptime_s": None}
    s = mod.public_summary(full(healthy(), machine=unmeasured))
    assert s["overall"] == "unknown"
    assert "disk — not measured" in s["unknown"]


def test_public_summary_reports_failures_as_failures():
    mod = load_status_mod()
    s = mod.public_summary(full(healthy(
        notify_tail=f"{ago(days=4)}\tNOCHANNEL\troutine check")))
    assert s["overall"] == "failed"
    assert s["failed"] == ["notifications — last attempt 4 days ago: no channel configured; "
                           "nothing delivered since"]


def test_public_output_excludes_private_sentinels():
    """Everything the local page may show and the public one must not: raw
    logs, notification text, task names, commit subjects, usernames, home
    paths, hostnames, branch and file names. Each carries a sentinel; the
    local page must contain them (proving they are in play) and neither public
    rendering may."""
    mod = load_status_mod()
    S = "SENTINEL"
    f = full(healthy(
        hostname=f"{S}-HOST",
        repos=[
            {"name": "workbench", "path": Path(f"/home/{S}-USER/workbench"), "present": True,
             "git": {"branch": f"task/{S}-BRANCH", "dirty": f"?? {S}-FILE.py",
                     "unpushed": f"abc123 {S}-COMMIT-SUBJECT",
                     "log": f"09 Sep 10:00  {S}-COMMIT-SUBJECT", "upstream": True,
                     "error": None},
             "tests": {"state": "fail", "passed": 3, "failed": 1, "errors": 1, "rc": 1,
                       "tail": f"FAILED tests/test_{S}.py::test_x - {S}-TRACEBACK"}},
            {"name": "erhvervsklubben", "path": Path(f"/home/{S}-USER/projects/e"),
             "present": False, "git": {}, "tests": None},
        ],
        watchdog_tail="\n".join([
            f"{ago(minutes=3)}\tALERT hb:{S}-JOB - {S}-JOB is stale "
            f"(no marker at /home/{S}-USER/x)",
            f"{ago(minutes=2)}\trun complete: 1 failing",
        ]),
        notify_tail=f"{ago(minutes=1)}\tFAILED(URLError)\t{S}-MESSAGE about {S}-HOST",
        heartbeats=hb([{"name": f"{S}-JOB", "path": Path(f"/home/{S}-USER/.local/x"),
                        "age_min": None, "limit_min": 40}],
                      unwatched=[{"name": f"{S}-UNWATCHED", "age_min": 3}]),
        timers=f"NEXT LEFT {S}-TIMER.timer",
        toolchain=[f"| `uv` | /home/{S}-USER/.local/bin/uv |"],
        models=f"{S}-MODEL 6.6 GB",
        tasks=([f"workbench/{S}-TASK.md"], [f"workbench/{S}-DONE.md"]),
        setup=[f"**SSH keys** — run `ssh-copy-id {S}-USER@{S}-HOST.tail.ts.net`."],
    ))
    page = mod.render_detailed(f)
    for needle in (f"{S}-HOST", f"{S}-COMMIT-SUBJECT", f"{S}-TASK.md", f"{S}-MESSAGE",
                   f"/home/{S}-USER", f"{S}-BRANCH", f"{S}-JOB", f"{S}-TRACEBACK"):
        assert needle in page, f"{needle} not on the local page — the sentinel is not in play"
    summary = mod.public_summary(f)
    md, js = mod.render_public(summary), json.dumps(summary)
    assert S not in md, md
    assert S not in js, js
    # ...while the health facts themselves survive the curation.
    assert summary["overall"] == "failed"
    assert any(c["name"] == "tests: workbench" and "1 error(s)" in c["note"]
               for c in summary["checks"])
    assert summary["setup_pending"] == 1


# ------------------------------------------------------------------- CLI
def cli(fake_home, *args):
    env = {**os.environ, "HOME": str(fake_home)}
    return subprocess.run([sys.executable, str(SCRIPT), *args],
                          capture_output=True, text=True, env=env, timeout=240)


def test_cli_public_json_against_an_empty_home(fake_home):
    """End to end, no repos, no logs, no config: every check is an explicit
    unknown, the stamp parses, and nothing from the fake HOME leaks."""
    r = cli(fake_home, "--public", "--quick", "--json")
    assert r.returncode == 0, r.stderr
    s = json.loads(r.stdout)
    datetime.fromisoformat(s["collected_at"])
    assert s["overall"] == "unknown" and s["tests_measured"] is False
    assert {c["status"] for c in s["checks"]} == {"unknown"}
    assert any(u.startswith("repository: workbench") for u in s["unknown"])
    assert str(fake_home) not in r.stdout


def test_cli_public_markdown_and_write(fake_home):
    out = fake_home / "out" / "health.md"
    r = cli(fake_home, "--public", "--quick", "--write", str(out))
    assert r.returncode == 0, r.stderr
    text = out.read_text()
    assert text.startswith("# Workbench health")
    assert "not an all-clear" in text
    assert str(fake_home) not in text


def test_cli_detailed_page_is_not_all_clear_on_an_empty_home(fake_home):
    r = cli(fake_home, "--quick")
    assert r.returncode == 0, r.stderr
    assert "## Needs you" in r.stdout
    assert "Not measured this run" in r.stdout
    assert "none failed" not in r.stdout


def test_cli_json_requires_public(fake_home):
    r = cli(fake_home, "--json")
    assert r.returncode != 0 and "--public" in r.stderr


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


# ------------------------------------------------------------------- git
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

    g = load_status_mod().collect_git(tmp_path)
    assert "26 Jul 13:55" in g["log"], f"expected the committer date, got: {g}"
    assert "02 Jan" not in g["log"], f"author date leaked into the page: {g}"
    assert g["error"] is None


def test_a_checkout_with_no_remote_counts_its_commits_as_unpushed(tmp_path):
    """No upstream used to mean "nothing unpushed". A repo no remote has ever
    seen is the opposite of that."""
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "config", "user.name", "Test")
    (tmp_path / "f.txt").write_text("x\n")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "only here")
    g = load_status_mod().collect_git(tmp_path)
    assert g["upstream"] is False
    assert len(g["unpushed"].splitlines()) == 1, g


def test_a_git_probe_that_fails_sets_error_instead_of_a_placeholder(tmp_path, monkeypatch):
    (tmp_path / ".git").mkdir()
    mod = load_status_mod()
    monkeypatch.setattr(mod, "probe", lambda *a, **k: mod.Probe(None, "", "missing"))
    g = mod.collect_git(tmp_path)
    assert g["error"] == "missing"
    assert g["dirty"] == "" and g["unpushed"] == ""


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
