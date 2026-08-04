#!/usr/bin/env python3
"""Weekly docs gardener — find statements in the docs that stopped being true.

Spec §8.4. This is the one job in the layer that cannot be computed: "which of
these sentences has quietly become false" is irreducibly a judgement call, so
Lukas chose (2026-08-04) to run it on Claude rather than on the local model or
not at all. See `context/STACK.md`.

    weekly-gardener.py [--since YYYY-MM-DD] [--stdout] [--claude PATH]

Three properties hold regardless of which model is behind it:

**It only points; it never fixes** (`workbench-setup-spec.md:310`). Every file's
contents are handed to the model inside the prompt, so it needs no tools at all,
and the mutating tools are denied on top of that. There is no branch, no commit,
no edit — the output is a report a human reads.

**Every finding is verified against the file before it is shown.** A finding is
discarded unless the named file exists *and* the quoted statement actually
appears in it. A stronger model lowers the hallucination rate but does not change
the shape of the failure, and the check costs nothing — so Claude does not
inherit an exemption from the guard the 4B earned.

**One file per call.** A single call carrying every doc invites the model to
answer about the wrong file, and makes one rate-limit failure lose the whole run.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HOME = Path.home()
BIN = Path(__file__).resolve().parent
REPO = HOME / "workbench"
HEARTBEAT = HOME / ".local" / "state" / "workbench" / "heartbeats" / "gardener"
CLAUDE = HOME / ".local" / "bin" / "claude"
TIMEOUT = 300

# Generated output and historical records are not docs, and reviewing them
# produces findings that are either meaningless or actively wrong:
#   STATUS.md    rewritten every 30 min; every statement in it is *meant* to
#                change, so "this is no longer true" is its normal state
#   reports/     this job's own output, and the nightly brief's
#   tasks/done/  a record of what was true when the task closed
#   spec         carries a historical banner and is deliberately not kept current
SKIP_PREFIXES = ("reports/", "tasks/done/")
SKIP_FILES = ("STATUS.md", "workbench-setup-spec.md")

# The spec's prompt, verbatim (workbench-setup-spec.md:305-316). Kept intact
# rather than improved: it was written to be model-agnostic, and rewriting it
# for Claude would quietly make the two versions incomparable.
PROMPT = """You are a documentation gardener. You receive (1) this week's git commits with
file names and (2) the contents of the docs files in this repo.

Task: Find statements in docs that have likely become false due to this week's
changes. Report ONLY likely mismatches — never fix anything yourself.

Respond exclusively with JSON matching this schema:
{"findings": [{"file": "...", "statement": "...", "reason": "...", "confidence": "high|medium|low"}]}

No findings → {"findings": []}. No text outside the JSON."""


def docs_files(repo: Path) -> list[str]:
    """Tracked markdown, minus what is generated or historical."""
    try:
        out = subprocess.run(
            ["git", "ls-files", "*.md"], cwd=repo,
            capture_output=True, text=True, timeout=60, check=True,
        ).stdout
    except Exception:
        return []
    return sorted(
        p for p in out.split()
        if not p.startswith(SKIP_PREFIXES) and p not in SKIP_FILES
    )


def week_commits(repo: Path, since: str) -> str:
    """The week's commits with file names — input (1) of the prompt."""
    try:
        out = subprocess.run(
            ["git", "log", "--since", since, "--stat", "--no-merges",
             "--invert-grep", "--grep=^Status: ",
             "--date=short", "--pretty=%h %ad %s"],
            cwd=repo, capture_output=True, text=True, timeout=60,
        ).stdout.strip()
    except Exception:
        return ""
    return out


def build_prompt(commits: str, path: str, content: str) -> str:
    return (
        f"{PROMPT}\n\n"
        f"=== (1) This week's commits ===\n{commits or '(no commits this week)'}\n\n"
        f"=== (2) The file under review: {path} ===\n{content}\n"
    )


# --------------------------------------------------------------------- the call
def run_claude(prompt: str, claude: Path = CLAUDE) -> tuple[bool, str]:
    """One headless call. Returns (ok, output).

    Denying the mutating tools is belt and braces — the file's contents are
    already in the prompt, so a correct run needs no tools whatsoever. It is
    here so that "never fixes anything" is enforced by the harness rather than
    by the prompt asking nicely.
    """
    cmd = [
        str(claude), "-p",
        "--output-format", "text",
        "--strict-mcp-config",
        "--disallowedTools", "Edit", "Write", "NotebookEdit", "Bash",
        prompt,
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT)
    except Exception as exc:
        return False, f"({type(exc).__name__})"
    return proc.returncode == 0, (proc.stdout + proc.stderr).strip()


def is_rate_limited(output: str) -> bool:
    """Spec §1: 5-hour rate-limit windows are the real bottleneck. Hitting one is
    an expected outcome, not a defect — the run stops cleanly rather than
    burning the rest of the window on retries that cannot succeed."""
    low = output.lower()
    return any(s in low for s in ("rate limit", "usage limit", "rate_limit_error"))


def parse_findings(output: str) -> list[dict] | None:
    """Pull the findings array out of a reply. None means unparseable.

    Tolerates a fenced block or prose around the JSON — the prompt forbids both,
    but a run thrown away over a stray "```json" would be a silly way to lose a
    real finding.
    """
    text = output.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fence:
        text = fence.group(1).strip()
    if not text.startswith("{"):
        start, end = text.find("{"), text.rfind("}")
        if start == -1 or end <= start:
            return None
        text = text[start:end + 1]
    try:
        data = json.loads(text)
    except ValueError:
        return None
    if not isinstance(data, dict) or not isinstance(data.get("findings"), list):
        return None
    return [f for f in data["findings"] if isinstance(f, dict)]


# --------------------------------------------------------------- the guard
def _normalise(text: str) -> str:
    """Collapse whitespace so a quote that crossed a line wrap still matches.

    Without this the guard would reject almost every true finding — these docs
    are hard-wrapped at 90 columns — and a guard that rejects everything is
    indistinguishable from no job at all.
    """
    return " ".join(text.split())


def verify(finding: dict, repo: Path) -> tuple[bool, str]:
    """Confirm a finding against the file it names. Returns (ok, reason-if-not).

    This is the boundary validation from spec §2.6, kept after the model upgrade
    on purpose: structural validity says nothing about truth, and an invented
    quotation is exactly the failure that reads as authoritative.
    """
    name = finding.get("file")
    statement = finding.get("statement")
    if not isinstance(name, str) or not isinstance(statement, str) or not statement.strip():
        return False, "missing file or statement"

    target = repo / name
    try:
        target.relative_to(repo)
    except ValueError:
        return False, f"path escapes the repo: {name}"
    if not target.is_file():
        return False, f"no such file: {name}"

    try:
        content = target.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False, f"unreadable: {name}"

    if _normalise(statement) not in _normalise(content):
        return False, f"quoted statement does not appear in {name}"
    return True, ""


# ---------------------------------------------------------------------- render
def render(day: str, confirmed: list[dict], quarantined: list[dict],
           reviewed: int, stopped_early: str = "") -> str:
    out = [f"# Docs gardener — {day}", ""]

    if stopped_early:
        out.append(f"**Run stopped early: {stopped_early}.** "
                   f"Only {reviewed} file(s) were reviewed, so this pass is incomplete.")
        out.append("")

    if confirmed:
        out.append(f"**{len(confirmed)} statement(s) may have stopped being true.** "
                   "Nothing has been changed — this only points.")
    else:
        out.append(f"**Nothing found.** {reviewed} file(s) reviewed.")
    out.append("")

    for f in confirmed:
        out.append(f"### `{f.get('file')}` — {f.get('confidence', 'unknown')} confidence")
        out.append("")
        out.append(f"> {f.get('statement', '').strip()}")
        out.append("")
        out.append(f.get("reason", "").strip() or "_No reason given._")
        out.append("")

    if quarantined:
        out.append("## Quarantined")
        out.append("")
        out.append(f"{len(quarantined)} finding(s) were discarded because they could not be "
                   "confirmed against the file. Listed so the failure rate stays visible — "
                   "a job whose findings are mostly invented is not worth keeping.")
        out.append("")
        for f, why in quarantined:
            out.append(f"- `{f.get('file')}` — {why}")
        out.append("")

    out.append("---")
    out.append("")
    out.append("_Every finding above was checked against the file it names: the file exists, "
               "and the quoted line is really in it._")
    return "\n".join(out) + "\n"


# ------------------------------------------------------------------------ main
def _notify(message: str) -> None:
    try:
        sys.path.insert(0, str(BIN))
        from notify import notify as send
        send(message)
    except Exception:
        pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", help="YYYY-MM-DD (default: 7 days ago)")
    ap.add_argument("--stdout", action="store_true", help="print instead of writing the report")
    ap.add_argument("--claude", type=Path, default=CLAUDE, help="path to the claude CLI")
    ap.add_argument("--repo", type=Path, default=REPO)
    args = ap.parse_args()

    now = datetime.now(timezone.utc).astimezone()
    since = args.since or (now - timedelta(days=7)).strftime("%Y-%m-%d")
    day = now.strftime("%Y-%m-%d")

    commits = week_commits(args.repo, since)
    files = docs_files(args.repo)

    confirmed: list[dict] = []
    quarantined: list[tuple[dict, str]] = []
    reviewed = 0
    stopped_early = ""

    for path in files:
        try:
            content = (args.repo / path).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        ok, output = run_claude(build_prompt(commits, path, content), args.claude)
        if is_rate_limited(output):
            stopped_early = "the rate-limit window was exhausted"
            break
        reviewed += 1
        if not ok:
            quarantined.append(({"file": path}, "the call failed"))
            continue

        findings = parse_findings(output)
        if findings is None:
            quarantined.append(({"file": path}, "reply was not the requested JSON"))
            continue

        for f in findings:
            good, why = verify(f, args.repo)
            (confirmed if good else quarantined).append(f if good else (f, why))

    text = render(day, confirmed, quarantined, reviewed, stopped_early)

    if args.stdout:
        sys.stdout.write(text)
        return 0

    out_path = args.repo / "reports" / "gardener" / f"{day}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")

    # Silence when there is nothing to say. A weekly "no findings" buzz is how a
    # channel teaches its reader to ignore it.
    if confirmed:
        _notify(
            f"📝 Docs gardener: {len(confirmed)} statement(s) may have stopped being true.\n\n"
            + "\n".join(f"• {f.get('file')}" for f in confirmed[:5])
            + "\n\nNothing was changed. See reports/gardener/ in the repo."
        )

    # No heartbeat on a truncated run. "This job has not completed in over a
    # week" is exactly what the watchdog should surface, and a heartbeat written
    # here would hide it.
    if not stopped_early:
        HEARTBEAT.parent.mkdir(parents=True, exist_ok=True)
        HEARTBEAT.touch()

    print(f"wrote {out_path} ({len(confirmed)} confirmed, {len(quarantined)} quarantined)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
