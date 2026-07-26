#!/usr/bin/env python3
"""Generate STATUS.md — the single page that answers "what is going on?".

Written for reading on a phone through the Claude app: the machine pushes this
to GitHub on a timer, so no inbound connection, VPN or shell is needed. Ask
Claude about the repo and it is reading a picture at most 30 minutes old.

Ordering is deliberate: what needs a human first, then what changed, then the
boring green stuff. Everything here is measured, never asserted — test counts
come from actually running pytest, timers from systemd, disk from df.

    workbench-status.py [--write PATH] [--quick]

--quick skips the test run (a few seconds) for cheap interactive use.
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

HOME = Path.home()
REPOS = [
    HOME / "workbench",
    HOME / "projects" / "erhvervsklubben",
]
LOGS = HOME / "logs"
TIMEOUT = 120


def run(cmd: list[str] | str, cwd: Path | None = None, timeout: int = TIMEOUT) -> str:
    """Run a command, return stdout. Never raises — a broken probe must not
    take down the whole report."""
    try:
        proc = subprocess.run(
            cmd, cwd=cwd, shell=isinstance(cmd, str),
            capture_output=True, text=True, timeout=timeout,
        )
        return (proc.stdout + proc.stderr).strip()
    except Exception as exc:
        return f"(probe failed: {type(exc).__name__})"


def section(title: str) -> str:
    return f"\n## {title}\n"


# ------------------------------------------------------------------ collectors
def collect_tests(repo: Path) -> dict:
    """Actually run the suite. A status page that reports remembered results is
    the exact failure mode the spec warns about."""
    if not (repo / "tests").is_dir():
        return {"state": "none"}
    if (repo / "package.json").is_file():
        # Node project: its suite needs npm and Docker services this 30-minute
        # timer must not own. CI is the judge there — say so, never guess.
        return {"state": "external"}
    uv = HOME / ".local" / "bin" / "uv"
    out = run([str(uv), "run", "pytest", "tests/", "-q", "-o", "addopts=",
               "-p", "no:cacheprovider"], cwd=repo, timeout=300)
    m = re.search(r"(\d+) passed", out)
    f = re.search(r"(\d+) failed", out)
    return {
        "state": "fail" if f else ("pass" if m else "unknown"),
        "passed": int(m.group(1)) if m else 0,
        "failed": int(f.group(1)) if f else 0,
        "tail": "\n".join(out.splitlines()[-12:]),
    }


def collect_git(repo: Path) -> dict:
    if not (repo / ".git").is_dir():
        return {}
    return {
        "branch": run(["git", "branch", "--show-current"], repo),
        "dirty": run(["git", "status", "--porcelain"], repo),
        # %cd, not %ad: publish-status.sh collapses consecutive status commits
        # with --amend, which preserves the author date and moves only the
        # committer date. With %ad the page showed commits days older than they
        # were — the status line claiming "26 Jul" dated "24 Jul".
        #
        # format-local, not format: plain `format:` renders each commit in its
        # own timezone, so commits made in a cloud container (UTC) sat above
        # commits made on this box (CEST) reading as earlier. The list looked
        # shuffled. Local time puts everything in the box's zone.
        "log": run(["git", "log", "-8", "--date=format-local:%d %b %H:%M",
                    "--pretty=%cd  %s"], repo),
        "unpushed": run(["git", "log", "--oneline", "@{u}..HEAD"], repo)
        if "no upstream" not in run(["git", "rev-parse", "--abbrev-ref", "@{u}"], repo)
        else "",
    }


def collect_timers() -> str:
    out = run(["systemctl", "--user", "list-timers", "--all", "--no-pager"])
    return "\n".join(out.splitlines()[:8])


def collect_heartbeats() -> list[str]:
    hb_dir = HOME / ".local" / "state" / "workbench" / "heartbeats"
    if not hb_dir.is_dir():
        return []
    now = datetime.now().timestamp()
    rows = []
    for f in sorted(hb_dir.iterdir()):
        age_min = int((now - f.stat().st_mtime) / 60)
        rows.append(f"| `{f.name}` | {age_min} min ago |")
    return rows


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


def tail_log(name: str, n: int = 8) -> str:
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
    peers = run(["tailscale", "status"])
    if peers and len(peers.splitlines()) <= 1:
        b.append("**Tailnet has no peers** — install Tailscale on phone/Mac to reach the box "
                 "by SSH. (Not needed for the Claude app, which reads GitHub.)")
    if not (HOME / ".secrets" / "telegram.env").exists():
        b.append("**Telegram not configured** — run `python3 ~/bin/telegram-setup.py`.")
    return b


def _last_log_entry(tail: str) -> tuple[datetime | None, list[str]]:
    """Timestamp and tab-separated fields of a log's last real line.

    Both logs are `<iso>\\t<field>...` — watchdog-check.sh:20 and notify.py:68.
    tail_log() returns a parenthesised placeholder when there is no log, which
    must read as "nothing to say", never as a failure.
    """
    for line in reversed([ln for ln in tail.splitlines() if ln.strip()]):
        if line.startswith("("):
            return None, []
        parts = line.split("\t")
        try:
            return datetime.fromisoformat(parts[0]), parts[1:]
        except ValueError:
            continue
    return None, []


def collect_blockers(facts: dict) -> list[str]:
    """Things that need Lukas, derived from what the collectors already measured.

    Pure by design: no subprocess, no filesystem. Everything arrives in `facts`,
    which is what makes the escalation logic testable without a machine — and
    this is the part of the page worth reading on a phone, so it is the part
    that most needs tests.

    Operational failures sort above setup gaps: a red test outranks a missing
    tailnet peer.
    """
    b: list[str] = []
    now = facts["now"]

    for r in facts["repos"]:
        name, g, t = r["name"], r["git"], r["tests"]
        if t and t.get("state") == "fail":
            b.append(f"**Tests red in `{name}`** — {t['failed']} failing, "
                     f"{t['passed']} passing. Nothing should be committed on top of this.")
        if g.get("dirty"):
            n = len(g["dirty"].splitlines())
            b.append(f"**{n} uncommitted file(s) in `{name}`** — work that exists only on "
                     "the box. A rebuild would lose it.")
        if g.get("unpushed"):
            n = len(g["unpushed"].splitlines())
            b.append(f"**{n} unpushed commit(s) in `{name}`** — GitHub cannot see this work, "
                     "so no other Claude can either.")

    # The watchdog is the box's own alarm. Two ways it fails Lukas: it reports
    # failures nobody reads, or it stops running and everything looks quiet.
    wd_time, wd_fields = _last_log_entry(facts["watchdog_tail"])
    if wd_fields:
        m = re.search(r"run complete: (\d+) failing", wd_fields[0])
        if m and int(m.group(1)) > 0:
            b.append(f"**Watchdog reports {m.group(1)} failing check(s)** — see the watchdog "
                     "log at the bottom of this page.")
    if wd_time is not None:
        silent_min = int((now - wd_time).total_seconds() / 60)
        if silent_min > 45:
            b.append(f"**Watchdog has not run in {silent_min} min** — its timer fires every "
                     "15, so the box's own alarm is off.")

    # A dead notification channel hides every other failure on this machine,
    # and notify.py degrades silently by design (:90) so nothing else surfaces
    # it. STATUS.md can, because Lukas pulls this page rather than being pushed.
    nt_time, nt_fields = _last_log_entry(facts["notify_tail"])
    if nt_fields and nt_time is not None:
        status = nt_fields[0]
        if (status.startswith("FAILED") or status == "NOCHANNEL") \
                and (now - nt_time).total_seconds() < 3600:
            b.append(f"**The machine's voice is broken** — last notification attempt was "
                     f"`{status}`. Alerts are not reaching you; this page is the only channel "
                     "still working.")

    if facts["quick"]:
        b.append("_Tests were not measured in this run (`--quick`)._")

    return b + facts["setup"]


# ---------------------------------------------------------------------- render
def build() -> str:
    args = build.args
    now = datetime.now(timezone.utc).astimezone()
    out = [
        "# Workbench status",
        "",
        f"_Generated {now.strftime('%A %d %B %Y, %H:%M %Z')} on `{os.uname().nodename}`._",
        "_Regenerated automatically every 30 minutes. Everything below is measured, not remembered._",
    ]

    # ---- measure first, render second: the blocker list is derived from the
    # same facts the sections below display, so it cannot disagree with them.
    watchdog_tail = tail_log("watchdog.log", 6)
    notify_tail = tail_log("notify.log", 6)
    repo_facts = []
    for repo in REPOS:
        if not repo.is_dir():
            continue
        repo_facts.append({
            "name": repo.name,
            "path": repo,
            "git": collect_git(repo),
            "tests": None if args.quick else collect_tests(repo),
        })

    # ---- needs you
    blockers = collect_blockers({
        "now": now,
        "quick": args.quick,
        "repos": repo_facts,
        "watchdog_tail": watchdog_tail,
        "notify_tail": notify_tail,
        "setup": collect_setup_blockers(),
    })
    out.append(section("Needs you"))
    out.append("\n".join(f"- {b}" for b in blockers) if blockers else "Nothing. All clear.")

    # ---- repos
    out.append(section("Repositories"))
    for r in repo_facts:
        g, t = r["git"], r["tests"]
        out.append(f"### `{r['name']}`")
        dirty = g.get("dirty", "")
        state = f"{len(dirty.splitlines())} uncommitted file(s)" if dirty else "clean"
        unpushed = g.get("unpushed", "")
        if unpushed:
            state += f", {len(unpushed.splitlines())} unpushed commit(s)"
        out.append(f"Branch `{g.get('branch','?')}` — {state}.")
        if t is not None:
            if t["state"] == "pass":
                out.append(f"\n**Tests: {t['passed']} passing.** ✅")
            elif t["state"] == "fail":
                out.append(f"\n**Tests: {t['failed']} FAILING**, {t['passed']} passing. ❌\n")
                out.append(f"```\n{t['tail']}\n```")
            elif t["state"] == "none":
                out.append("\n_No test suite in this repo._")
            elif t["state"] == "external":
                out.append("\n_Tests not run by this box (Node project — CI is the judge)._")
        out.append(f"\nRecent commits:\n```\n{g.get('log','(none)')}\n```")

    # ---- jobs
    out.append(section("Scheduled jobs"))
    out.append(f"```\n{collect_timers()}\n```")
    hb = collect_heartbeats()
    if hb:
        out.append("\n| Job | Last success |\n|---|---|\n" + "\n".join(hb))
    else:
        out.append("\n_No job heartbeats yet — no scrapers are running._")

    # ---- machine
    out.append(section("Machine"))
    disk = run("df -h / | tail -1 | awk '{print $4\" free of \"$2\" (\"$5\" used)\"}'")
    mem = run("free -h | awk 'NR==2{print $7\" available of \"$2}'")
    up = run(["uptime", "-p"])
    out.append(f"- Disk: {disk}\n- RAM: {mem}\n- Uptime: {up}")
    out.append("\nToolchain:\n\n| Tool | Path |\n|---|---|\n"
               + "\n".join(collect_toolchain()))
    out.append(f"\nLocal models:\n```\n{collect_models()}\n```")

    # ---- tasks
    open_t, done_t = collect_tasks()
    out.append(section("Tasks"))
    out.append("Open:\n" + ("\n".join(f"- {t}" for t in open_t) if open_t else "_none_"))
    if done_t:
        out.append(f"\nCompleted: {len(done_t)}")

    # ---- logs
    out.append(section("Recent activity"))
    out.append(f"Watchdog:\n```\n{watchdog_tail}\n```")
    out.append(f"\nNotifications sent:\n```\n{notify_tail}\n```")

    out.append("\n---\n")
    out.append("_Ask Claude about any file in this repo — the markdown in `docs/`, "
               "`context/`, and `workbench-setup-spec.md` is the full picture._")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", type=Path, help="write to this path instead of stdout")
    ap.add_argument("--quick", action="store_true", help="skip running the test suites")
    ap.add_argument("--toolchain", action="store_true",
                    help="print just the resolved toolchain and exit")
    build.args = ap.parse_args()

    if build.args.toolchain:
        for t in TOOLS:
            print(f"{t}: {find_tool(t) or 'NOT INSTALLED'}")
        return 0

    text = build()
    if build.args.write:
        build.args.write.parent.mkdir(parents=True, exist_ok=True)
        build.args.write.write_text(text, encoding="utf-8")
        print(f"wrote {build.args.write} ({len(text.splitlines())} lines)")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
