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
REPOS = [HOME / "workbench", HOME / "workbench-context"]
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
        "log": run(["git", "log", "-8", "--date=format:%d %b %H:%M",
                    "--pretty=%ad  %s"], repo),
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


def collect_blockers() -> list[str]:
    """Things that need Lukas. This is the part worth reading on a phone."""
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

    # ---- needs you
    blockers = collect_blockers()
    out.append(section("Needs you"))
    out.append("\n".join(f"- {b}" for b in blockers) if blockers else "Nothing. All clear.")

    # ---- repos
    out.append(section("Repositories"))
    for repo in REPOS:
        if not repo.is_dir():
            continue
        g = collect_git(repo)
        out.append(f"### `{repo.name}`")
        dirty = g.get("dirty", "")
        state = f"{len(dirty.splitlines())} uncommitted file(s)" if dirty else "clean"
        unpushed = g.get("unpushed", "")
        if unpushed:
            state += f", {len(unpushed.splitlines())} unpushed commit(s)"
        out.append(f"Branch `{g.get('branch','?')}` — {state}.")
        if not args.quick:
            t = collect_tests(repo)
            if t["state"] == "pass":
                out.append(f"\n**Tests: {t['passed']} passing.** ✅")
            elif t["state"] == "fail":
                out.append(f"\n**Tests: {t['failed']} FAILING**, {t['passed']} passing. ❌\n")
                out.append(f"```\n{t['tail']}\n```")
            elif t["state"] == "none":
                out.append("\n_No test suite in this repo._")
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
    out.append(f"\nLocal models:\n```\n{collect_models()}\n```")

    # ---- tasks
    open_t, done_t = collect_tasks()
    out.append(section("Tasks"))
    out.append("Open:\n" + ("\n".join(f"- {t}" for t in open_t) if open_t else "_none_"))
    if done_t:
        out.append(f"\nCompleted: {len(done_t)}")

    # ---- logs
    out.append(section("Recent activity"))
    out.append(f"Watchdog:\n```\n{tail_log('watchdog.log', 6)}\n```")
    out.append(f"\nNotifications sent:\n```\n{tail_log('notify.log', 6)}\n```")

    out.append("\n---\n")
    out.append("_Ask Claude about any file in this repo — the markdown in `docs/`, "
               "`workbench-setup-spec.md`, and `../workbench-context/` is the full picture._")
    return "\n".join(out) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", type=Path, help="write to this path instead of stdout")
    ap.add_argument("--quick", action="store_true", help="skip running the test suites")
    build.args = ap.parse_args()

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
