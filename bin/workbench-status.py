#!/usr/bin/env python3
"""Generate STATUS.md — the single page that answers "what is going on?".

Written for reading on a phone through the Claude app: the machine pushes this
to GitHub on a timer, so no inbound connection, VPN or shell is needed. Ask
Claude about the repo and it is reading a picture at most 30 minutes old.

Ordering is deliberate: what needs a human first, then what changed, then the
boring green stuff. Everything here is measured, never asserted — test counts
come from actually running pytest, timers from systemd, disk from the kernel.

Three verdicts, never two. Every check ends as ok, failed or unknown, and
"unknown" is printed, never folded into ok: a missing log, an absent runner, a
timed-out suite or a repo that is not checked out cannot make the page greener.
The page claims an all-clear only when every check was measured and none failed.

    workbench-status.py [--write PATH] [--quick]            the detailed page
    workbench-status.py --public [--json] [--write PATH]    a publishable summary

--quick skips the test run (a few seconds) for cheap interactive use; the page
then says so instead of staying silent.
--public emits health facts only: states, counts, ages, an ISO-8601
collected-at stamp and the explicit unknowns. No log lines, notification text,
task names, commit subjects, usernames, home paths or hostnames.
The contract is written down in docs/health-reporting.md.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

HOME = Path.home()
REPOS = [
    HOME / "workbench",
    HOME / "projects" / "erhvervsklubben",
]
LOGS = HOME / "logs"
WATCHDOG_CONF = HOME / ".config" / "workbench" / "watchdog.conf"
HEARTBEAT_DIR = HOME / ".local" / "state" / "workbench" / "heartbeats"
TIMEOUT = 120
TEST_TIMEOUT = 300
WATCHDOG_EVERY_MIN = 15
WATCHDOG_SILENT_MIN = 45   # three missed runs
LOG_LINES = 40             # read for assessment
SHOW_LINES = 8             # shown on the page
FUTURE_TOLERANCE_S = 300   # evidence dated further ahead than this is clock skew, not health

OK, FAILED, UNKNOWN = "ok", "failed", "unknown"


# --------------------------------------------------------------------- probes
class Probe(NamedTuple):
    """What actually happened when a command ran.

    `error` is None when the command ran to completion (whatever its exit
    code), "missing" when the executable was not there, "timeout" when it did
    not finish, otherwise the exception class name. Anything that decides
    health must look at both `error` and `rc`: folding them into one string is
    how a real failure used to read as a pass.
    """
    rc: int | None
    out: str
    error: str | None = None


def _text(x) -> str:
    if x is None:
        return ""
    return x.decode(errors="replace") if isinstance(x, bytes) else str(x)


def probe(cmd: list[str] | str, cwd: Path | None = None, timeout: int = TIMEOUT) -> Probe:
    """Run a command and report exactly what happened. Never raises — a broken
    probe must not take down the whole report — but it must not vanish either."""
    try:
        proc = subprocess.run(
            cmd, cwd=cwd, shell=isinstance(cmd, str),
            capture_output=True, text=True, timeout=timeout,
        )
    except FileNotFoundError:
        return Probe(None, "", "missing")
    except subprocess.TimeoutExpired as exc:
        return Probe(None, (_text(exc.stdout) + _text(exc.stderr)).strip(), "timeout")
    except Exception as exc:  # see docstring: the report survives, the probe reports
        return Probe(None, "", type(exc).__name__)
    return Probe(proc.returncode, (proc.stdout + proc.stderr).strip())


def run(cmd: list[str] | str, cwd: Path | None = None, timeout: int = TIMEOUT) -> str:
    """Stdout+stderr of a command, or a parenthesised placeholder. For display
    only — nothing that decides health may consume this string."""
    p = probe(cmd, cwd, timeout)
    return f"(probe failed: {p.error})" if p.error is not None else p.out


def section(title: str) -> str:
    return f"\n## {title}\n"


# ------------------------------------------------------------------ collectors
_ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
_SUMMARY = re.compile(
    r"^(?P<body>no tests ran|\d+ [a-z]+(?:, \d+ [a-z]+)*) in [\d.]+s(?: \(\d+:\d\d:\d\d\))?$")
_COUNT = re.compile(r"(\d+) ([a-z]+)")
PYTEST_EXIT = {0: "all passed", 1: "tests failed", 2: "interrupted", 3: "internal error",
               4: "usage error", 5: "no tests collected"}


def parse_pytest_summary(out: str) -> dict[str, int] | None:
    """Counts from pytest's closing summary line ("1 failed, 86 passed in 9.0s"),
    or None when the output has no such line — which is a fact in itself."""
    for line in reversed(_ANSI.sub("", out).splitlines()):
        m = _SUMMARY.match(line.strip().strip("=").strip())
        if not m:
            continue
        counts = {"passed": 0, "failed": 0, "errors": 0}
        for n, word in _COUNT.findall(m.group("body")):
            key = "errors" if word in ("error", "errors") else word
            counts[key] = counts.get(key, 0) + int(n)
        return counts
    return None


def collect_tests(repo: Path) -> dict:
    """Actually run the suite. A status page that reports remembered results is
    the exact failure mode the spec warns about.

    The verdict needs the exit code AND the summary line to agree before this
    says "pass". pytest counting a failure or an error is "fail"; everything
    else — no runner, no verdict in time, no summary, an exit code the summary
    does not explain — is "unknown" with the reason. Never a pass by default:
    "1 passed, 1 error" exiting 1 used to read as green here.
    """
    if not (repo / "tests").is_dir():
        return {"state": "none"}
    if (repo / "package.json").is_file():
        # Node project: its suite needs npm and Docker services this 30-minute
        # timer must not own. CI is the judge there — say so, never guess.
        return {"state": "external"}
    uv = find_tool("uv")
    if uv is None:
        return {"state": "no-runner", "reason": "uv is not installed on this box"}
    p = probe([uv, "run", "pytest", "tests/", "-q", "-o", "addopts=",
               "-p", "no:cacheprovider"], cwd=repo, timeout=TEST_TIMEOUT)
    r = {"rc": p.rc, "passed": 0, "failed": 0, "errors": 0,
         "tail": "\n".join(p.out.splitlines()[-12:])}
    if p.error == "missing":
        return {**r, "state": "no-runner", "reason": "the test runner could not be executed"}
    if p.error == "timeout":
        return {**r, "state": "timeout", "reason": f"no verdict within {TEST_TIMEOUT} s"}
    if p.error is not None:
        return {**r, "state": "unknown", "reason": f"the probe failed ({p.error})"}
    counts = parse_pytest_summary(p.out)
    if counts is None:
        return {**r, "state": "unknown",
                "reason": f"exit code {p.rc} and no pytest summary in the output"}
    r.update(passed=counts["passed"], failed=counts["failed"], errors=counts["errors"])
    if counts["failed"] or counts["errors"]:
        return {**r, "state": "fail"}
    if p.rc != 0:
        return {**r, "state": "unknown",
                "reason": f"exit code {p.rc} ({PYTEST_EXIT.get(p.rc, 'unrecognised')}) "
                          "although no test was counted as failing"}
    if counts["passed"] == 0:
        return {**r, "state": "unknown", "reason": "exit code 0 but nothing passed"}
    return {**r, "state": "pass"}


def collect_git(repo: Path) -> dict:
    """Branch, dirt, unpushed work and recent log. A probe that fails sets
    `error` instead of leaving a placeholder string where a count is expected —
    "(probe failed)" in the dirty field used to count as one uncommitted file."""
    if not (repo / ".git").exists():
        return {}
    g: dict = {"error": None}

    def git(*args: str) -> str:
        p = probe(["git", *args], repo)
        if p.error is not None or p.rc != 0:
            g["error"] = g["error"] or (p.error or f"git {args[0]} exited {p.rc}")
            return ""
        return p.out

    g["branch"] = git("branch", "--show-current")
    g["dirty"] = git("status", "--porcelain")
    # %cd, not %ad: publish-status.sh collapses consecutive status commits
    # with --amend, which preserves the author date and moves only the
    # committer date. With %ad the page showed commits days older than they
    # were — the status line claiming "26 Jul" dated "24 Jul".
    #
    # format-local, not format: plain `format:` renders each commit in its
    # own timezone, so commits made in a cloud container (UTC) sat above
    # commits made on this box (CEST) reading as earlier. The list looked
    # shuffled. Local time puts everything in the box's zone.
    g["log"] = git("log", "-8", "--date=format-local:%d %b %H:%M", "--pretty=%cd  %s")
    up = probe(["git", "rev-parse", "--abbrev-ref", "@{u}"], repo)
    if up.error is None and up.rc == 0:
        g["upstream"] = True
        g["unpushed"] = git("log", "--oneline", "@{u}..HEAD")
    else:
        # No upstream: count what no remote has, rather than reporting nothing.
        g["upstream"] = False
        g["unpushed"] = git("log", "--oneline", "HEAD", "--not", "--remotes")
    return g


def collect_timers() -> str:
    out = run(["systemctl", "--user", "list-timers", "--all", "--no-pager"])
    return "\n".join(out.splitlines()[:8])


def read_watchdog_conf(path: Path | None = None) -> list[dict] | None:
    """The `heartbeat` lines of the watchdog config: which jobs are *expected*
    to prove they ran, and how fresh the proof must be. None when the file
    cannot be read — different from a config that lists no heartbeats.

    A malformed line is kept, with `problem` set, so the job it names stays
    visible as an expectation that cannot be checked. Dropping it made the
    monitor disappear from the assessment altogether.
    """
    try:
        text = (path or WATCHDOG_CONF).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    expected = []
    for line in text.splitlines():
        parts = line.split()
        if not parts or parts[0] != "heartbeat":
            continue
        entry = {"name": parts[1] if len(parts) > 1 else "(unnamed)",
                 "path": Path(parts[2]).expanduser() if len(parts) > 2 else None,
                 "max_s": None, "problem": None}
        if len(parts) < 4:
            entry["problem"] = ("malformed line, expected "
                                "`heartbeat <label> <file> <max-age-secs>`")
        else:
            try:
                max_s = int(parts[3])
            except ValueError:
                max_s = 0
            if max_s > 0:
                entry["max_s"] = max_s
            else:
                entry["problem"] = "the freshness limit is not a positive number of seconds"
        expected.append(entry)
    return expected


def collect_heartbeats(now: datetime) -> dict:
    """Expected heartbeats measured against their markers, plus any marker
    nobody watches. A missing config or marker directory is reported as such;
    it is not evidence that no job exists. Ages stay in seconds: a limit can
    be shorter than a minute, and rounding to minutes hid a marker that was
    54 s past its limit."""
    epoch = now.timestamp()

    def age_s(p: Path | None) -> int | None:
        if p is None:
            return None
        try:
            return int(epoch - p.stat().st_mtime)
        except OSError:
            return None

    expected = read_watchdog_conf()
    configured = None
    if expected is not None:
        configured = [{**h, "age_s": age_s(h["path"])} for h in expected]
    watched = {h["path"].resolve() for h in expected or [] if h["path"] is not None}
    unwatched, error = [], None
    try:
        markers = sorted(HEARTBEAT_DIR.iterdir()) if HEARTBEAT_DIR.is_dir() else []
    except OSError as exc:
        markers, error = [], type(exc).__name__
    for f in markers:
        if f.resolve() not in watched:
            unwatched.append({"name": f.name, "age_s": age_s(f)})
    return {"configured": configured, "unwatched": unwatched, "error": error}


def collect_machine() -> dict:
    """Disk, memory and uptime straight from the kernel: no shell one-liners
    to mis-parse, and each fact is None when it could not be read."""
    m: dict = {"disk": None, "memory": None, "uptime_s": None}
    try:
        du = shutil.disk_usage("/")
        m["disk"] = {"total": du.total, "free": du.free,
                     "used_pct": round(du.used * 100 / (du.used + du.free))}
    except (OSError, ZeroDivisionError):
        pass
    try:
        info = {}
        for line in Path("/proc/meminfo").read_text().splitlines():
            key, _, value = line.partition(":")
            info[key.strip()] = int(value.split()[0]) * 1024
        m["memory"] = {"total": info["MemTotal"], "available": info["MemAvailable"]}
    except (OSError, KeyError, ValueError, IndexError):
        pass
    try:
        m["uptime_s"] = int(float(Path("/proc/uptime").read_text().split()[0]))
    except (OSError, ValueError, IndexError):
        pass
    return m


# Tools we care about, and where they actually land on this box.
TOOLS = ["claude", "uv", "python3", "ollama", "git", "node", "npm"]
TOOL_DIRS = [
    HOME / ".local" / "bin",
    HOME / ".npm-global" / "bin",
    HOME / "bin",
    Path("/usr/local/bin"),
    Path("/usr/bin"),
]


def find_tool(name: str) -> str | None:
    """Resolve a tool by path, not just by PATH.

    `shutil.which` alone lies here: a systemd unit and an ssh non-login shell
    both run without `~/.local/bin` on PATH, so uv — installed and demonstrably
    running the test suite — reported as missing. That false negative mattered,
    because the same probe decides whether Claude Code is on the box.
    """
    found = shutil.which(name)
    if found:
        return found
    for d in TOOL_DIRS:
        candidate = d / name
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    # npm installs global binaries outside PATH more often than not.
    npm = shutil.which("npm")
    if npm:
        prefix = run([npm, "prefix", "-g"], timeout=20)
        if prefix and not prefix.startswith("("):
            candidate = Path(prefix.splitlines()[0].strip()) / "bin" / name
            if candidate.is_file() and os.access(candidate, os.X_OK):
                return str(candidate)
    return None


def collect_toolchain() -> list[str]:
    rows = []
    for t in TOOLS:
        where = find_tool(t)
        rows.append(f"| `{t}` | {where or '**not installed**'} |")
    return rows


def collect_models() -> str:
    if not shutil.which("ollama"):
        return "not installed"
    listed = run(["ollama", "list"])
    loaded = run(["ollama", "ps"])
    return f"{listed}\n\nCurrently loaded:\n{loaded}"


def tail_log(name: str, n: int = SHOW_LINES) -> str:
    p = LOGS / name
    if not p.is_file():
        return "(no log yet)"
    try:
        return "\n".join(p.read_text(errors="replace").splitlines()[-n:])
    except OSError:
        return "(unreadable)"


def collect_tasks() -> tuple[list[str], list[str]]:
    open_t, done_t = [], []
    for repo in REPOS:
        tasks = repo / "tasks"
        if not tasks.is_dir():
            continue
        for f in sorted(tasks.glob("*.md")):
            open_t.append(f"{repo.name}/{f.name}")
        for f in sorted((tasks / "done").glob("*.md")) if (tasks / "done").is_dir() else []:
            done_t.append(f"{repo.name}/{f.name}")
    return open_t, done_t


def collect_setup_blockers() -> list[str]:
    """One-time setup gaps. These probe the machine, so they are not pure."""
    b = []
    keys = HOME / ".ssh" / "authorized_keys"
    if not keys.exists() or keys.stat().st_size == 0:
        b.append("**SSH keys** — no `authorized_keys`, so password auth is still enabled. "
                 "Run `ssh-copy-id lukashoerup@lenovo.tail8658f1.ts.net` from a Mac.")
    ts = probe(["tailscale", "status"])
    if ts.error is not None or ts.rc != 0:
        # A missing or unhappy CLI is not "no peers": say what was not measured.
        b.append("**Tailnet state unverified** — `tailscale status` could not be read, so "
                 "whether phone/Mac can reach the box by SSH is unknown. (Not needed for "
                 "the Claude app, which reads GitHub.)")
    elif len(ts.out.splitlines()) <= 1:
        b.append("**Tailnet has no peers** — install Tailscale on phone/Mac to reach the box "
                 "by SSH. (Not needed for the Claude app, which reads GitHub.)")
    if not (HOME / ".secrets" / "telegram.env").exists():
        b.append("**Telegram not configured** — run `python3 ~/bin/telegram-setup.py`.")
    return b


# ----------------------------------------------------------------- assessment
def _entries(tail: str) -> list[tuple[datetime, list[str]]]:
    """Every parseable `<iso>\\t<field>...` line of a log tail, oldest first.

    Both logs are that shape — watchdog-check.sh:20 and notify.py:68. The
    parenthesised placeholders tail_log() returns when there is no log parse to
    nothing, and so does garbage: absence of evidence is reported by the
    caller, never mistaken for a healthy entry.
    """
    rows = []
    for line in tail.splitlines():
        if not line.strip() or line.startswith("("):
            continue
        parts = line.split("\t")
        try:
            t = datetime.fromisoformat(parts[0])
        except ValueError:
            continue
        if t.tzinfo is None:
            t = t.astimezone()
        rows.append((t, parts[1:]))
    return rows


def _last_log_entry(tail: str) -> tuple[datetime | None, list[str]]:
    rows = _entries(tail)
    return rows[-1] if rows else (None, [])


def _log_problem(tail: str) -> str | None:
    """Why a log tail carries no evidence, or None when it does."""
    if tail.startswith("(no log"):
        return "no log exists yet"
    if tail.startswith("(unreadable"):
        return "the log could not be read"
    if not tail.strip():
        return "the log is empty"
    if not _entries(tail):
        return "the log has no parseable entries"
    return None


def _span(seconds: float) -> str:
    """A duration for a human: "45 s", "5 min", "3 h", "4 days"."""
    seconds = max(0, int(seconds))
    if seconds < 120:
        return f"{seconds} s"
    minutes = seconds // 60
    if minutes < 120:
        return f"{minutes} min"
    if minutes < 48 * 60:
        return f"{minutes // 60} h"
    return f"{minutes // 1440} days"


def _age(now: datetime, then: datetime) -> str:
    return _span((now - then).total_seconds())


def _future_s(now: datetime, then: datetime) -> int:
    """How far ahead of this box's clock a timestamp is, if beyond tolerance;
    0 otherwise. Evidence from the future is clock skew, not health."""
    ahead = int((then - now).total_seconds())
    return ahead if ahead > FUTURE_TOLERANCE_S else 0


class Check(NamedTuple):
    """One measured thing. `name` and `note` are safe to publish: states,
    counts, ages and fixed phrases only. `details` are the local page's
    bullets and may name repos, files, paths and raw log statuses."""
    name: str
    status: str
    note: str
    details: tuple[str, ...] = ()


def _tests_check(name: str, t: dict | None) -> Check | None:
    label = f"tests: {name}"
    state = t.get("state") if t else "skipped"
    reason = (t or {}).get("reason", "no reason recorded")
    if state == "skipped":
        return Check(label, UNKNOWN, "not measured in this run (quick mode)",
                     [f"_Tests in `{name}` were not measured in this run (`--quick`)._"])
    if state == "none":
        return None
    if state == "external":
        return Check(label, UNKNOWN, "not run by this machine; CI is the judge",
                     [f"_Tests in `{name}` are not run by this box (Node project — CI is "
                      "the judge), so their state is unknown here._"])
    if state == "pass":
        return Check(label, OK, f"{t.get('passed', 0)} passed")
    if state == "fail":
        bits = []
        if t.get("failed"):
            bits.append(f"{t['failed']} failing")
        if t.get("errors"):
            bits.append(f"{t['errors']} error(s)")
        note = ", ".join(bits or ["failure counted"]) + f", {t.get('passed', 0)} passing"
        return Check(label, FAILED, note,
                     [f"**Tests red in `{name}`** — {note}. Nothing should be committed on "
                      "top of this."])
    if state == "no-runner":
        return Check(label, UNKNOWN, f"not run: {reason}",
                     [f"**Tests in `{name}` could not run** — {reason}. The suite was not "
                      "measured."])
    if state == "timeout":
        return Check(label, UNKNOWN, f"timed out: {reason}",
                     [f"**Tests in `{name}` did not finish** — {reason}. No verdict."])
    return Check(label, UNKNOWN, f"no verdict: {reason}",
                 [f"**Tests in `{name}` gave no verdict** — {reason}."])


def _repo_check(r: dict) -> Check:
    name = r["name"]
    label = f"repository: {name}"
    if not r.get("present", True):
        return Check(label, UNKNOWN, "expected checkout is absent; nothing about it was measured",
                     [f"**`{name}` is not checked out on the box** — expected at "
                      f"`{r.get('path')}`. Nothing about it was measured."])
    g = r.get("git") or {}
    if not g:
        return Check(label, UNKNOWN, "directory exists but is not a git checkout",
                     [f"**`{name}` is not a git checkout** — its state cannot be measured."])
    if g.get("error"):
        return Check(label, UNKNOWN, "git state could not be read",
                     [f"**Git state of `{name}` could not be read** — {g['error']}. "
                      "Uncommitted or unpushed work there is unknown."])
    bits, details = [], []
    if g.get("dirty"):
        n = len(g["dirty"].splitlines())
        bits.append(f"{n} uncommitted file(s)")
        details.append(f"**{n} uncommitted file(s) in `{name}`** — work that exists only on "
                       "the box. A rebuild would lose it.")
    if g.get("unpushed"):
        n = len(g["unpushed"].splitlines())
        bits.append(f"{n} unpushed commit(s)")
        details.append(f"**{n} unpushed commit(s) in `{name}`** — GitHub cannot see this "
                       "work, so no other Claude can either.")
    if details:
        return Check(label, FAILED, ", ".join(bits), details)
    return Check(label, OK, "clean, nothing unpushed")


_RUN_COMPLETE = re.compile(r"^run complete: (\d+) failing")
_FAILURE_LINE = ("ALERT", "STILL-FAILING")   # what watchdog-check.sh logs for a failing check


def _watchdog_check(tail: str, now: datetime) -> Check:
    """The watchdog is the box's own alarm. It fails Lukas three ways: it
    reports failures nobody reads, it stops running and everything looks
    quiet, or it has never left a log at all — which used to look identical
    to "nothing wrong".

    Freshness is measured from the last *completed* run. Other log activity
    is not health evidence and must not refresh an old success: a later
    "no config" exit means the watchdog now checks nothing, a later ALERT
    means a check is failing right now, and an ordinary line from a run
    underway is just activity. Each is reported for what it is.
    """
    problem = _log_problem(tail)
    if problem:
        return Check("watchdog", UNKNOWN, f"no evidence ({problem})",
                     [f"**Watchdog has left no evidence** — {problem}. The box's own alarm is "
                      "not shown to be running, so nothing else here is being watched."])
    rows = _entries(tail)
    done = None
    for i in range(len(rows) - 1, -1, -1):
        m = _RUN_COMPLETE.match(rows[i][1][0]) if rows[i][1] else None
        if m:
            done = (i, rows[i][0], int(m.group(1)))
            break
    later = [f[0] for _, f in (rows[done[0] + 1:] if done else rows) if f]
    no_config = any(msg.startswith("no config") for msg in later)
    alerts = [msg for msg in later if msg.startswith(_FAILURE_LINE)]
    activity = _age(now, rows[-1][0])
    if done is None:
        if no_config:
            return Check("watchdog", UNKNOWN, "runs, but has no check list, so it checks nothing",
                         ["**Watchdog has no config** — it runs on time but checks nothing, "
                          "so its silence proves nothing."])
        return Check("watchdog", UNKNOWN,
                     f"active {activity} ago but no completed run in the recent log",
                     [f"**Watchdog has not completed a run recently** — last activity "
                      f"{activity} ago, but no `run complete` line in the recent log, "
                      "so its verdict is unknown."])
    _, done_t, failing = done
    ahead = _future_s(now, done_t)
    if ahead and not failing and not alerts:
        return Check("watchdog", UNKNOWN,
                     f"last completed run is dated {_span(ahead)} in the future (clock skew?)",
                     [f"**Watchdog evidence is from the future** — its last completed run is "
                      f"dated {_span(ahead)} ahead of this box's clock, so it is not evidence "
                      "of health."])
    stale_min = int((now - done_t).total_seconds() / 60)
    notes, details = [], []
    if failing:
        notes.append(f"{failing} failing check(s) at the last completed run, "
                     f"{_age(now, done_t)} ago")
        details.append(f"**Watchdog reports {failing} failing check(s)** — see the watchdog "
                       "log at the bottom of this page.")
    if alerts:
        notes.append(f"{len(alerts)} alert(s) since the last completed run")
        details.append(f"**Watchdog has raised {len(alerts)} alert(s) since its last completed "
                       "run** — a check is failing right now and the run underway has not "
                       "finished. See the log at the bottom of this page.")
    if stale_min > WATCHDOG_SILENT_MIN:
        notes.append(f"no completed run in {stale_min} min (fires every {WATCHDOG_EVERY_MIN}; "
                     f"last activity {activity} ago)")
        details.append(f"**Watchdog has not completed a run in {stale_min} min** — its timer "
                       f"fires every {WATCHDOG_EVERY_MIN}, so the box's own alarm is off. "
                       f"Last log activity {activity} ago is not a completed run.")
    if no_config:
        notes.append("has since run without a check list")
        details.append("**Watchdog has lost its config** — since its last completed run it "
                       "has exited without a check list, so it currently checks nothing.")
    if failing or alerts or stale_min > WATCHDOG_SILENT_MIN:
        return Check("watchdog", FAILED, "; ".join(notes), details)
    if no_config:
        return Check("watchdog", UNKNOWN,
                     f"last completed run {_age(now, done_t)} ago, 0 failing, but it has "
                     "since run without a check list", details)
    note = f"last completed run {_age(now, done_t)} ago, 0 failing"
    if later:
        note += f"; activity since ({activity} ago), not yet a completed run"
    return Check("watchdog", OK, note)


_FAILED_STATUS = re.compile(r"^FAILED\(([A-Za-z0-9_=.-]+)\)$")


def _notify_check(tail: str, now: datetime) -> Check:
    """A dead notification channel hides every other failure on this machine,
    and notify.py degrades silently by design (:90) so nothing else surfaces
    it. STATUS.md can, because Lukas pulls this page rather than being pushed.

    The last attempt decides, however old: a failure stays a failure until a
    later delivery proves the channel back. Ageing it out after an hour meant
    a channel dead since last week read as fine.
    """
    problem = _log_problem(tail)
    if problem:
        return Check("notifications", UNKNOWN, f"no delivery evidence ({problem})",
                     [f"_Whether the machine's voice works is unknown — {problem}, so no "
                      "delivery has been observed._"])
    t, fields = _entries(tail)[-1]
    status = fields[0] if fields else ""
    age = _age(now, t)
    if status == "SENT":
        ahead = _future_s(now, t)
        if ahead:
            return Check("notifications", UNKNOWN,
                         f"last delivery is dated {_span(ahead)} in the future (clock skew?)",
                         [f"_The last notification delivery is dated {_span(ahead)} ahead of "
                          "this box's clock — clock skew, not evidence that the channel works._"])
        return Check("notifications", OK, f"last delivery {age} ago")
    if status == "NOCHANNEL" or status.startswith("FAILED"):
        m = _FAILED_STATUS.match(status)
        kind = ("no channel configured" if status == "NOCHANNEL"
                else f"delivery failed ({m.group(1)})" if m else "delivery failed")
        return Check("notifications", FAILED,
                     f"last attempt {age} ago: {kind}; nothing delivered since",
                     [f"**The machine's voice is broken** — the last notification attempt, "
                      f"{age} ago, was `{status}` and nothing has been delivered since. Alerts "
                      "are not reaching you; this page is the only channel still working."])
    return Check("notifications", UNKNOWN, f"last entry {age} ago has an unrecognised status",
                 [f"_The last notification log entry ({age} ago) has an unrecognised status, "
                  "so delivery state is unknown._"])


def _heartbeat_check(hb: dict) -> Check | None:
    """Every job the watchdog config expects, against its marker. A line that
    cannot be evaluated (malformed, bad limit) and a marker from the future
    are unknowns, listed by name — never dropped, never counted as fresh."""
    if hb.get("error"):
        return Check("heartbeats", UNKNOWN, "markers could not be read",
                     [f"**Heartbeat markers could not be read** — {hb['error']}."])
    conf = hb.get("configured")
    if conf is None:
        return Check("heartbeats", UNKNOWN,
                     "watchdog config unreadable, so the expected jobs are unknown",
                     ["**Watchdog config could not be read** — which jobs are expected to "
                      "heartbeat is unknown, so none of them is being checked here."])
    if not conf:
        return None
    malformed = [h for h in conf if h.get("problem")]
    valid = [h for h in conf if not h.get("problem")]
    never = [h for h in valid if h["age_s"] is None]
    future = [h for h in valid if h["age_s"] is not None and -h["age_s"] > FUTURE_TOLERANCE_S]
    stale = [h for h in valid if h["age_s"] is not None and h not in future
             and h["age_s"] > h["max_s"]]
    fresh = [h for h in valid if h["age_s"] is not None and h not in future and h not in stale]
    details = [f"**Job `{h['name']}` has never run** — no heartbeat marker at `{h['path']}`."
               for h in never]
    details += [f"**Job `{h['name']}` is stale** — last success {_span(h['age_s'])} ago, "
                f"limit {_span(h['max_s'])}." for h in stale]
    details += [f"**Job `{h['name']}` cannot be checked** — {h['problem']}." for h in malformed]
    details += [f"**Job `{h['name']}` has a marker from the future** — dated "
                f"{_span(-h['age_s'])} ahead of this box's clock; clock skew, not evidence "
                "that it ran." for h in future]
    bits = [f"{len(group)} {word}" for group, word in
            ((never, "never ran"), (stale, "stale"), (malformed, "malformed"),
             (future, "future-dated")) if group]
    note = f"of {len(conf)} expected job(s): " + ", ".join(bits)
    if never or stale:
        return Check("heartbeats", FAILED, note, details)
    if malformed or future:
        return Check("heartbeats", UNKNOWN, note, details)
    oldest = max(h["age_s"] for h in fresh)
    return Check("heartbeats", OK,
                 f"{len(conf)} expected job(s) reporting, oldest {_span(oldest)} ago")


def assess(facts: dict) -> list[Check]:
    """Every health verdict on the page, derived from what the collectors
    measured. Pure by design: no subprocess, no filesystem, no clock — `now`
    arrives in `facts` — which is what makes the escalation logic testable
    without a machine. Both renderers read this list, so they cannot disagree.
    """
    now = facts["now"]
    checks: list[Check] = []
    for r in facts["repos"]:
        # An absent checkout has nothing to test; one unknown says it all.
        t = _tests_check(r["name"], r.get("tests")) if r.get("present", True) else None
        if t is not None:
            checks.append(t)
        checks.append(_repo_check(r))
    checks.append(_watchdog_check(facts["watchdog_tail"], now))
    checks.append(_notify_check(facts["notify_tail"], now))
    hb = facts.get("heartbeats")
    if hb is not None:
        c = _heartbeat_check(hb)
        if c is not None:
            checks.append(c)
    return checks


def collect_blockers(facts: dict) -> list[str]:
    """Everything that stops the page from saying "all clear": failures first,
    then what could not be measured, then setup gaps. A red test outranks a
    missing tailnet peer."""
    checks = assess(facts)
    failed = [d for c in checks if c.status == FAILED for d in c.details]
    unknown = [d for c in checks if c.status == UNKNOWN for d in c.details]
    return failed + unknown + list(facts.get("setup", []))


# ---------------------------------------------------------------------- facts
def collect_facts(quick: bool) -> dict:
    """Measure everything once. Both renderers work from this dict, so the
    blocker list can never disagree with the sections below it."""
    now = datetime.now(timezone.utc).astimezone()
    repos = []
    for repo in REPOS:
        if not repo.is_dir():
            repos.append({"name": repo.name, "path": repo, "present": False,
                          "git": {}, "tests": None})
            continue
        repos.append({"name": repo.name, "path": repo, "present": True,
                      "git": collect_git(repo),
                      "tests": {"state": "skipped"} if quick else collect_tests(repo)})
    return {
        "now": now,
        "quick": quick,
        "hostname": os.uname().nodename,
        "repos": repos,
        "watchdog_tail": tail_log("watchdog.log", LOG_LINES),
        "notify_tail": tail_log("notify.log", LOG_LINES),
        "heartbeats": collect_heartbeats(now),
        "timers": collect_timers(),
        "machine": collect_machine(),
        "toolchain": collect_toolchain(),
        "models": collect_models(),
        "tasks": collect_tasks(),
        "setup": collect_setup_blockers(),
    }


# ---------------------------------------------------------------------- render
def _gb(n: int) -> str:
    return f"{n / 2**30:.0f}G"


def _disk_line(d: dict | None) -> str:
    if not d:
        return "not measured"
    return f"{_gb(d['free'])} free of {_gb(d['total'])} ({d['used_pct']}% used)"


def _mem_line(m: dict | None) -> str:
    if not m:
        return "not measured"
    return f"{_gb(m['available'])} available of {_gb(m['total'])}"


def _uptime_line(s: int | None) -> str:
    if s is None:
        return "not measured"
    days, rem = divmod(int(s), 86400)
    hours, rem = divmod(rem, 3600)
    minutes = rem // 60
    return f"up {days} day(s), {hours} h {minutes} min" if days else f"up {hours} h {minutes} min"


def _last_lines(tail: str, n: int = SHOW_LINES) -> str:
    return "\n".join(tail.splitlines()[-n:])


def _heartbeat_table(hb: dict | None) -> str:
    if hb is None:
        return "\n_Heartbeats were not collected._"
    conf = hb.get("configured")
    rows = []
    for h in conf or []:
        limit = "—" if h.get("max_s") is None else _span(h["max_s"])
        if h.get("problem"):
            rows.append(f"| `{h['name']}` | — | {limit} | **cannot be checked**: "
                        f"{h['problem']} |")
            continue
        age = h["age_s"]
        if age is None:
            last, state = "never", "**never run**"
        elif -age > FUTURE_TOLERANCE_S:
            last, state = f"{_span(-age)} in the future", "unknown (clock skew?)"
        else:
            last = f"{_span(age)} ago"
            state = "**stale**" if age > h["max_s"] else "ok"
        rows.append(f"| `{h['name']}` | {last} | {limit} | {state} |")
    for h in hb.get("unwatched", []):
        last = "?" if h["age_s"] is None else f"{_span(h['age_s'])} ago"
        rows.append(f"| `{h['name']}` | {last} | — | unwatched |")
    lines = []
    if conf is None:
        lines.append("\n_Watchdog config could not be read — which jobs are expected to "
                     "heartbeat is unknown._")
    elif not conf:
        lines.append("\n_No heartbeat jobs are configured in the watchdog config._")
    if hb.get("error"):
        lines.append(f"\n_Heartbeat markers could not be read: {hb['error']}._")
    if rows:
        lines.append("\n| Job | Last success | Limit | State |\n|---|---|---|---|\n"
                     + "\n".join(rows))
    return "\n".join(lines) if lines else "\n_No heartbeat markers found._"


def render_detailed(facts: dict) -> str:
    now = facts["now"]
    checks = assess(facts)
    failed = [d for c in checks if c.status == FAILED for d in c.details]
    unknown = [d for c in checks if c.status == UNKNOWN for d in c.details]
    setup = list(facts.get("setup", []))
    out = [
        "# Workbench status",
        "",
        f"_Generated {now.strftime('%A %d %B %Y, %H:%M %Z')} on `{facts['hostname']}`._",
        "_Regenerated automatically every 30 minutes. Everything below is measured, "
        "not remembered._",
    ]

    # ---- needs you: derived from the same checks the sections below display.
    out.append(section("Needs you"))
    if failed or setup:
        out.append("\n".join(f"- {b}" for b in failed + setup))
    elif unknown:
        out.append("Nothing failed, but not everything could be measured — this is not "
                   "an all-clear.")
    else:
        out.append(f"Nothing. All {len(checks)} checks were measured and none failed.")
    if unknown:
        out.append(f"\nNot measured this run ({len(unknown)}):\n"
                   + "\n".join(f"- {u}" for u in unknown))

    # ---- repos
    out.append(section("Repositories"))
    for r in facts["repos"]:
        g, t = r.get("git") or {}, r.get("tests")
        out.append(f"### `{r['name']}`")
        if not r.get("present", True):
            out.append(f"_Not checked out on this box (expected at `{r.get('path')}`)._")
            continue
        if not g:
            out.append("_Not a git checkout._")
        elif g.get("error"):
            out.append(f"_Git state could not be read: {g['error']}._")
        else:
            dirty = g.get("dirty", "")
            state = f"{len(dirty.splitlines())} uncommitted file(s)" if dirty else "clean"
            unpushed = g.get("unpushed", "")
            if unpushed:
                state += f", {len(unpushed.splitlines())} unpushed commit(s)"
            if g.get("upstream") is False:
                state += " (no upstream branch)"
            out.append(f"Branch `{g.get('branch') or '?'}` — {state}.")
        state = (t or {}).get("state", "skipped")
        if state == "pass":
            out.append(f"\n**Tests: {t.get('passed', 0)} passing.** ✅")
        elif state == "fail":
            bits = []
            if t.get("failed"):
                bits.append(f"{t['failed']} FAILING")
            if t.get("errors"):
                bits.append(f"{t['errors']} ERROR(S)")
            out.append(f"\n**Tests: {', '.join(bits or ['FAILING'])}**, "
                       f"{t.get('passed', 0)} passing. ❌\n")
            out.append(f"```\n{t.get('tail', '')}\n```")
        elif state == "none":
            out.append("\n_No test suite in this repo._")
        elif state == "external":
            out.append("\n_Tests not run by this box (Node project — CI is the judge)._")
        elif state == "skipped":
            out.append("\n_Tests not measured (`--quick`)._")
        else:
            out.append(f"\n**Tests: no verdict** — {t.get('reason', state)}. ⚠️")
            if t.get("tail"):
                out.append(f"```\n{t['tail']}\n```")
        out.append(f"\nRecent commits:\n```\n{g.get('log') or '(none)'}\n```")

    # ---- jobs
    out.append(section("Scheduled jobs"))
    out.append(f"```\n{facts.get('timers', '')}\n```")
    out.append(_heartbeat_table(facts.get("heartbeats")))

    # ---- machine
    m = facts.get("machine") or {}
    out.append(section("Machine"))
    out.append(f"- Disk: {_disk_line(m.get('disk'))}\n- RAM: {_mem_line(m.get('memory'))}\n"
               f"- Uptime: {_uptime_line(m.get('uptime_s'))}")
    out.append("\nToolchain:\n\n| Tool | Path |\n|---|---|\n"
               + "\n".join(facts.get("toolchain", [])))
    out.append(f"\nLocal models:\n```\n{facts.get('models', '')}\n```")

    # ---- tasks
    open_t, done_t = facts.get("tasks", ([], []))
    out.append(section("Tasks"))
    out.append("Open:\n" + ("\n".join(f"- {t}" for t in open_t) if open_t else "_none_"))
    if done_t:
        out.append(f"\nCompleted: {len(done_t)}")

    # ---- logs
    out.append(section("Recent activity"))
    out.append(f"Watchdog:\n```\n{_last_lines(facts['watchdog_tail'])}\n```")
    out.append(f"\nNotifications sent:\n```\n{_last_lines(facts['notify_tail'])}\n```")

    out.append("\n---\n")
    out.append("_Ask Claude about any file in this repo — the markdown in `docs/`, "
               "`context/`, and `workbench-setup-spec.md` is the full picture._")
    return "\n".join(out) + "\n"


def public_summary(facts: dict) -> dict:
    """The publishable view: what was measured, what it said, what could not
    be measured. Built only from Check.name/note, counts and machine numbers —
    never from log tails, git output, task lists, setup text or the hostname —
    so nothing private can reach it by accident. A test holds this line."""
    checks = assess(facts)
    failed = [f"{c.name} — {c.note}" for c in checks if c.status == FAILED]
    unknown = [f"{c.name} — {c.note}" for c in checks if c.status == UNKNOWN]
    m = facts.get("machine") or {}
    disk, mem = m.get("disk"), m.get("memory")
    machine = {
        "disk": None if not disk else {"free_gb": round(disk["free"] / 2**30, 1),
                                        "total_gb": round(disk["total"] / 2**30, 1),
                                        "used_pct": disk["used_pct"]},
        "memory": None if not mem else {"available_gb": round(mem["available"] / 2**30, 1),
                                         "total_gb": round(mem["total"] / 2**30, 1)},
        "uptime_s": m.get("uptime_s"),
    }
    for key, label in (("disk", "disk"), ("memory", "memory"), ("uptime_s", "uptime")):
        if machine[key] is None:
            unknown.append(f"{label} — not measured")
    overall = FAILED if failed else UNKNOWN if unknown else OK
    # "Measured" means a verdict from actually running the suite (ok or
    # failed). External, quick, no-runner, timeout and no-verdict are not.
    suites = [c for c in checks if c.name.startswith("tests: ")]
    measured = [c for c in suites if c.status in (OK, FAILED)]
    coverage = ("none" if not measured
                else "full" if len(measured) == len(suites) else "partial")
    tests = {"suites": len(suites), "measured": len(measured), "coverage": coverage,
             "quick": bool(facts.get("quick", False))}
    return {
        "collected_at": facts["now"].isoformat(timespec="seconds"),
        "tests_measured": coverage == "full",
        "tests": tests,
        "overall": overall,
        "checks": [{"name": c.name, "status": c.status, "note": c.note} for c in checks],
        "failed": failed,
        "unknown": unknown,
        "setup_pending": len(facts.get("setup", [])),
        "machine": machine,
    }


def render_public(s: dict) -> str:
    n = len(s["checks"])
    if s["overall"] == FAILED:
        verdict = f"**{len(s['failed'])} check(s) failed.**"
        if s["unknown"]:
            verdict += f" {len(s['unknown'])} could not be measured."
    elif s["overall"] == UNKNOWN:
        verdict = (f"**No failures found, but {len(s['unknown'])} check(s) could not be "
                   "measured — this is not an all-clear.**")
    else:
        verdict = f"**All {n} checks were measured and none failed.**"
    out = ["# Workbench health", "",
           f"Collected: `{s['collected_at']}`", "", verdict, "",
           "| Check | Status | Note |", "|---|---|---|"]
    out += [f"| {c['name']} | {c['status']} | {c['note']} |" for c in s["checks"]]
    if s["failed"]:
        out += ["", "Failed:"] + [f"- {x}" for x in s["failed"]]
    out += ["", "Not measured (unknown):"] + ([f"- {x}" for x in s["unknown"]] or ["- none"])
    m = s["machine"]
    bits = [
        "disk not measured" if not m["disk"] else
        f"disk {m['disk']['free_gb']} GB free of {m['disk']['total_gb']} GB "
        f"({m['disk']['used_pct']}% used)",
        "memory not measured" if not m["memory"] else
        f"{m['memory']['available_gb']} GB RAM available of {m['memory']['total_gb']} GB",
        "uptime not measured" if m["uptime_s"] is None else _uptime_line(m["uptime_s"]),
    ]
    out += ["", "Machine: " + "; ".join(bits) + "."]
    t = s["tests"]
    out.append(f"Tests measured this run: {t['measured']} of {t['suites']} suite(s) "
               f"({t['coverage']}{'; quick mode' if t['quick'] else ''}).")
    if s["setup_pending"]:
        out.append(f"One-time setup items still pending: {s['setup_pending']} "
                   "(details on the local page).")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", type=Path, help="write to this path instead of stdout")
    ap.add_argument("--quick", action="store_true", help="skip running the test suites")
    ap.add_argument("--public", action="store_true",
                    help="curated summary safe to publish: health facts only — no logs, "
                         "names, paths or hosts")
    ap.add_argument("--json", action="store_true",
                    help="with --public: emit the summary as JSON instead of markdown")
    ap.add_argument("--toolchain", action="store_true",
                    help="print just the resolved toolchain and exit")
    args = ap.parse_args()
    if args.json and not args.public:
        ap.error("--json only applies to --public")

    if args.toolchain:
        for t in TOOLS:
            print(f"{t}: {find_tool(t) or 'NOT INSTALLED'}")
        return 0

    facts = collect_facts(quick=args.quick)
    if args.public:
        summary = public_summary(facts)
        text = json.dumps(summary, indent=2) + "\n" if args.json else render_public(summary)
    else:
        text = render_detailed(facts)
    if args.write:
        args.write.parent.mkdir(parents=True, exist_ok=True)
        args.write.write_text(text, encoding="utf-8")
        print(f"wrote {args.write} ({len(text.splitlines())} lines)")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
