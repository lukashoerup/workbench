"""Invariants over the docs themselves.

Fixing a stale statement by hand only resets the clock — the same class of
error comes back the next time something is renamed or moved. These tests fail
when it does.

Every check walks `git ls-files`, so a new file is covered the moment it is
tracked, without anyone remembering to add it here.
"""
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent

# Not authored, so not held to these rules:
#   workbench-setup-spec.md — carries a historical banner (:3-9), deliberately
#     not kept current
#   tasks/done/ — a record of what was true when the task was completed
#   STATUS.md — generated output, rewritten by the box every 30 minutes. Its
#     *generator* (bin/workbench-status.py) is authored and is checked, which
#     is where the footer bug that motivated this test actually lived.
EXCLUDED_PREFIXES = ("tasks/done/",)
EXCLUDED_FILES = ("workbench-setup-spec.md", "STATUS.md")


def tracked(suffix=None):
    out = subprocess.run(
        ["git", "ls-files"], cwd=REPO, capture_output=True, text=True, check=True
    ).stdout.split()
    paths = [
        p for p in out
        if not p.startswith(EXCLUDED_PREFIXES) and p not in EXCLUDED_FILES
    ]
    if suffix:
        paths = [p for p in paths if p.endswith(suffix)]
    return paths


def read(rel):
    return (REPO / rel).read_text(encoding="utf-8", errors="replace")


def test_no_references_to_the_merged_away_context_repo():
    """The old cross-project repo was merged into `context/` on 2026-07-24. The
    reference sweep missed the status generator's footer, which then
    republished the dead path to GitHub every 30 minutes for two days.

    The needle is assembled at runtime so this file can name the thing it
    forbids without matching itself — otherwise the check flags its own source
    the moment it becomes tracked, which is exactly what happened first time.
    """
    needle = "workbench" + "-context"
    offenders = [p for p in tracked() if needle in read(p)]
    assert not offenders, f"{offenders} still reference the merged-away {needle} repo"


def test_every_referenced_bin_script_is_actually_in_the_repo():
    """CLAUDE.md promises "`~/bin` symlinks here, so edits are version-controlled".
    A script referenced in the docs but absent from `bin/` means that promise is
    false and the script would be lost with the box."""
    import re

    missing = set()
    for p in tracked(".md"):
        for name in re.findall(r"~/bin/([A-Za-z0-9_.-]+)", read(p)):
            if not (REPO / "bin" / name).exists():
                missing.add(name)
    assert not missing, f"referenced in docs but not in bin/: {sorted(missing)}"


@pytest.mark.parametrize(
    "rel,cap",
    [("CLAUDE.md", 80), ("SYSTEM.md", 90)],
)
def test_index_files_stay_small(rel, cap):
    """Spec §6: these are read on every session and on a phone. Bloat here is
    measurably expensive — context rot, and buried answers in connector search."""
    n = len(read(rel).splitlines())
    assert n <= cap, f"{rel} is {n} lines, cap is {cap}"


def test_context_and_docs_files_stay_readable():
    too_long = {
        p: len(read(p).splitlines())
        for p in tracked(".md")
        if (p.startswith("context/") or p.startswith("docs/"))
        and len(read(p).splitlines()) > 200
    }
    assert not too_long, f"over the 200-line cap: {too_long}"
