#!/usr/bin/env python3
"""Nightly brief — what happened on this box in the last day.

Deliberately model-free. Every question worth asking overnight is deterministic:
did tests fail, did the watchdog report failing checks, is there work that exists
only on this box, is the notification channel dead. `collect_blockers()` in
workbench-status.py already answers exactly these, so this job reuses it rather
than handing raw logs to a model and asking what mattered.

Decided 2026-08-04 (`context/STACK.md`): spec §8.2 specified a local model to
write the headline, and it was cut. A confabulated "all quiet" on the night
something broke is worse than no brief at all, because it actively reassures —
and the sentence it would have written sat on top of facts that were already
correct without it.

    nightly-triage.py [--day YYYY-MM-DD] [--stdout] [--quick]

Writes `reports/nightly/YYYY-MM-DD.md` and touches its heartbeat, on success
only. Telegram is used **only when something needs a human**: a nightly
"nothing happened" buzz teaches its own reader to ignore it, and the watchdog
already alerts the moment something actually breaks.
"""
from __future__ import annotations

import argparse
import importlib.util
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HOME = Path.home()
BIN = Path(__file__).resolve().parent
REPO = HOME / "workbench"
LOGS = HOME / "logs"
HEARTBEAT = HOME / ".local" / "state" / "workbench" / "heartbeats" / "triage"


def load_status_mod():
    """workbench-status.py has a dash in its name, so it cannot be imported
    normally. Loading it is the whole point: the blocker logic must not be
    reimplemented here, or the brief and STATUS.md could disagree about whether
    the machine is healthy."""
    spec = importlib.util.spec_from_file_location(
        "workbench_status", BIN / "workbench-status.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------------ log reading
def log_rows(path: Path, day: str) -> list[list[str]]:
    """Tab-separated fields of every line in `path` stamped with `day`.

    Both logs are `<iso-timestamp>\\t<field>...` — see watchdog-check.sh and
    notify.py. Unparseable lines are skipped rather than raised on: a line torn
    by a power cut must not cost a whole night's brief.
    """
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    rows = []
    for line in raw.splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        try:
            stamp = datetime.fromisoformat(parts[0])
        except ValueError:
            continue
        if stamp.strftime("%Y-%m-%d") == day:
            rows.append(parts[1:])
    return rows


def summarise_watchdog(rows: list[list[str]]) -> dict:
    runs = failing = alerts = undelivered = recovered = 0
    for fields in rows:
        text = fields[0] if fields else ""
        m = re.match(r"run complete: (\d+) failing", text)
        if m:
            runs += 1
            if int(m.group(1)) > 0:
                failing += 1
        elif text.startswith("ALERT-UNDELIVERED"):
            undelivered += 1
        elif text.startswith("ALERT "):
            alerts += 1
        elif text.startswith("RECOVERED"):
            recovered += 1
    return {
        "runs": runs,
        "runs_with_failures": failing,
        "alerts": alerts,
        "undelivered": undelivered,
        "recovered": recovered,
    }


def summarise_notify(rows: list[list[str]]) -> dict:
    sent = failed = queued = nochannel = 0
    for fields in rows:
        status = fields[0] if fields else ""
        if status.startswith("SENT"):            # SENT and SENT(outbox)
            sent += 1
        elif status == "NOCHANNEL":
            nochannel += 1
        elif status.startswith(("FAILED", "DROPPED")):
            failed += 1
            if "QUEUED" in status:
                queued += 1
    return {"sent": sent, "failed": failed, "queued": queued, "nochannel": nochannel}


def commits_for_day(repo: Path, day: str) -> list[str]:
    """Real commits made on `day`, newest last.

    Status commits are excluded. The publisher amends them into one moving
    commit every 30 minutes, so they say nothing about what was worked on — and
    a brief that leads with them buries the commits that matter.
    """
    if not (repo / ".git").is_dir():
        return []
    try:
        proc = subprocess.run(
            ["git", "log", "--all", "--no-merges",
             f"--since={day} 00:00:00", f"--until={day} 23:59:59",
             "--invert-grep", "--grep=^Status: ",
             "--date=format-local:%H:%M", "--pretty=%cd  %s"],
            cwd=repo, capture_output=True, text=True, timeout=60,
        )
    except Exception:
        return []
    return [ln for ln in proc.stdout.strip().splitlines() if ln.strip()][::-1]


# ---------------------------------------------------------------------- gather
def gather(day: str, *, quick: bool = False) -> dict:
    """Measure everything. Impure by definition — every number here comes from a
    log or a command."""
    mod = load_status_mod()
    now = datetime.now(timezone.utc).astimezone()

    watchdog_tail = mod.tail_log("watchdog.log", 6)
    notify_tail = mod.tail_log("notify.log", 6)

    repos = []
    for repo in mod.REPOS:
        if not repo.is_dir():
            continue
        repos.append({
            "name": repo.name,
            "path": repo,
            "git": mod.collect_git(repo),
            "tests": None if quick else mod.collect_tests(repo),
        })

    blockers = mod.collect_blockers({
        "now": now,
        "quick": quick,
        "repos": repos,
        "watchdog_tail": watchdog_tail,
        "notify_tail": notify_tail,
        "setup": mod.collect_setup_blockers(),
    })

    return {
        "day": day,
        "blockers": blockers,
        "repos": [
            {
                "name": r["name"],
                "tests": r["tests"],
                "commits": commits_for_day(r["path"], day),
            }
            for r in repos
        ],
        "watchdog": summarise_watchdog(log_rows(LOGS / "watchdog.log", day)),
        "notify": summarise_notify(log_rows(LOGS / "notify.log", day)),
    }


# ---------------------------------------------------------------------- render
def _test_line(tests: dict | None) -> str:
    if tests is None:
        return "_Tests not measured in this run._"
    state = tests.get("state")
    if state == "pass":
        return f"**Tests: {tests['passed']} passing.** ✅"
    if state == "fail":
        return f"**Tests: {tests['failed']} FAILING**, {tests['passed']} passing. ❌"
    if state == "external":
        return "_Tests not run by this box (Node project — CI is the judge)._"
    if state == "none":
        return "_No test suite in this repo._"
    return "_Test state unknown._"


def render(facts: dict) -> str:
    """Pure: the same facts render the same bytes, every time.

    That is worth more than it looks. It makes the brief diffable night to
    night, and it makes a wrong brief a bug with a reproduction rather than an
    unlucky roll — which is precisely what the cut model could never offer.
    """
    out = [f"# Nightly brief — {facts['day']}", ""]

    blockers = facts["blockers"]
    if blockers:
        out.append(f"**{len(blockers)} thing(s) need a human.**")
        out.append("")
        out.extend(f"- {b}" for b in blockers)
    else:
        out.append("**Nothing needs a human.**")
    out.append("")

    out.append("## Repositories")
    for r in facts["repos"]:
        out.append("")
        out.append(f"### `{r['name']}`")
        out.append("")
        out.append(_test_line(r["tests"]))
        out.append("")
        commits = r["commits"]
        if commits:
            out.append(f"{len(commits)} commit(s):")
            out.append("")
            out.append("```")
            out.extend(commits)
            out.append("```")
        else:
            out.append("_No commits._")
    out.append("")

    wd = facts["watchdog"]
    out.append("## Watchdog")
    out.append("")
    if wd["runs"] == 0:
        out.append("**It did not run at all.** The timer fires every 15 minutes, so this is "
                   "itself the finding: the box's own alarm was off for the day.")
    else:
        out.append(f"- {wd['runs']} run(s), {wd['runs_with_failures']} of them reporting "
                   "a failing check")
        out.append(f"- {wd['alerts']} alert(s) sent, {wd['recovered']} recovery message(s)")
        if wd["undelivered"]:
            out.append(f"- **{wd['undelivered']} alert(s) could not be delivered** — the "
                       "cooldown was deliberately not started for these, so they retry.")
    out.append("")

    nt = facts["notify"]
    out.append("## Notifications")
    out.append("")
    out.append(f"- {nt['sent']} delivered, {nt['failed']} failed, {nt['queued']} queued "
               "for a later retry")
    if nt["nochannel"]:
        out.append(f"- **{nt['nochannel']} had nowhere to go** — the Telegram channel is "
                   "not configured, so nothing is reaching the phone.")
    out.append("")

    out.append("---")
    out.append("")
    out.append("_Computed, not generated. Every number above came from a log or a command; "
               "no model read anything._")
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------------ main
def _notify(message: str) -> None:
    """Best effort. A brief that was written and published must not be reported
    as a failed run just because Telegram was unreachable — notify.py queues it."""
    try:
        sys.path.insert(0, str(BIN))
        from notify import notify as send
        send(message)
    except Exception:
        pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", help="YYYY-MM-DD (default: yesterday, since this runs after midnight)")
    ap.add_argument("--stdout", action="store_true", help="print instead of writing the report")
    ap.add_argument("--quick", action="store_true", help="skip running the test suites")
    args = ap.parse_args()

    # Default to yesterday: the timer fires at 03:15, so "the day that just
    # ended" is the one worth reporting on, not the three hours since midnight.
    day = args.day or (
        datetime.now(timezone.utc).astimezone() - timedelta(days=1)
    ).strftime("%Y-%m-%d")

    facts = gather(day, quick=args.quick)
    text = render(facts)

    if args.stdout:
        sys.stdout.write(text)
        return 0

    path = REPO / "reports" / "nightly" / f"{day}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

    if facts["blockers"]:
        _notify(
            f"🌙 Nightly brief {day} — {len(facts['blockers'])} thing(s) need you.\n\n"
            + "\n".join(f"• {b}" for b in facts["blockers"][:5])
        )

    # Last line of a successful run only, never in a finally block. A heartbeat
    # written on a failed run tells the watchdog everything is fine.
    HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
    HEARTBEAT.touch()
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
