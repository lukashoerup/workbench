"""Tests for setup/install-user.sh — the script that keeps the box in sync.

workbench-apply.sh runs `--check` every 10 minutes and only calls the installer
when it reports drift, so the properties that matter are that it is honest
about drift, that repeated runs change nothing, and that it never destroys a
file it did not create.

Driven as a subprocess against a fake HOME, the same way the watchdog and
publisher are tested.
"""
import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "setup" / "install-user.sh"


@pytest.fixture
def home(tmp_path):
    class H:
        def __init__(self):
            self.path = tmp_path

        def run(self, *args):
            env = {**os.environ, "HOME": str(tmp_path)}
            # PATH without systemctl so the tests exercise the same code path in
            # CI containers as on a box where systemd --user is unavailable.
            return subprocess.run(
                ["bash", str(SCRIPT), *args],
                env=env, capture_output=True, text=True, timeout=60,
            )

        def snapshot(self):
            out = []
            for p in sorted(tmp_path.rglob("*")):
                rel = p.relative_to(tmp_path)
                out.append(f"{rel}|{'L' if p.is_symlink() else 'F' if p.is_file() else 'D'}")
            return out

    return H()


def test_check_reports_drift_on_a_bare_home(home):
    """Nothing installed yet, so --check must say so rather than claim sync."""
    result = home.run("--check")
    assert result.returncode == 1, result.stdout
    assert "needs linking" in result.stdout


def test_install_then_check_is_clean(home):
    home.run()
    result = home.run("--check")
    assert result.returncode == 0, f"still drifting after install:\n{result.stdout}"
    assert "in sync" in result.stdout


def test_bin_entries_are_symlinks_into_the_repo(home):
    """Copies would silently decouple the box from the repo: an edit made on the
    machine would never be version-controlled and would die with the disk."""
    home.run()
    link = home.path / "bin" / "notify.py"
    assert link.is_symlink(), "~/bin entries must be symlinks, not copies"
    assert link.resolve() == (REPO / "bin" / "notify.py").resolve()


def test_running_twice_changes_nothing(home):
    """It runs unattended every 10 minutes; a non-idempotent installer would
    churn the machine forever."""
    home.run()
    before = home.snapshot()
    home.run()
    assert home.snapshot() == before


def test_a_modified_file_in_bin_is_never_overwritten_and_blocks(home):
    """A real file whose content differs holds edits that exist nowhere else.
    Refuse — and report it as blocked (exit 2) rather than drift, so the caller
    stops retrying. Retrying forever is what spammed Telegram on 2026-07-26."""
    (home.path / "bin").mkdir(parents=True, exist_ok=True)
    stray = home.path / "bin" / "notify.py"
    stray.write_text("# hand-edited on the box\n")

    result = home.run()
    assert stray.read_text() == "# hand-edited on the box\n", "clobbered a real file"
    assert "unversioned edits" in result.stdout
    assert home.run("--check").returncode == 2, "must be blocked, not retryable drift"


def test_an_identical_copy_in_bin_is_converted_to_a_symlink(home):
    """Right after a bootstrap recovers a previously unversioned script, ~/bin
    holds a byte-identical copy of the repo file. Converting it loses nothing
    and is what makes later edits version-controlled — refusing instead leaves
    --check permanently dirty, which makes the caller loop."""
    (home.path / "bin").mkdir(parents=True, exist_ok=True)
    copy = home.path / "bin" / "notify.py"
    copy.write_bytes((REPO / "bin" / "notify.py").read_bytes())

    home.run()
    assert copy.is_symlink(), "an identical copy should become a symlink"
    assert home.run("--check").returncode == 0


def test_live_watchdog_checks_are_added_never_removed(home):
    """The live checklist may hold checks someone added on the box, so it is
    never pruned. But a check the repo declares must still reach the machine —
    otherwise a new job ships with nothing watching it, and its silent death is
    invisible. That is exactly what happened when the box's config overwrote
    the repo's and dropped the apply-timer checks."""
    conf = home.path / ".config" / "workbench" / "watchdog.conf"
    conf.parent.mkdir(parents=True, exist_ok=True)
    conf.write_text("net 8.8.8.8\n")

    home.run()
    after = conf.read_text()
    assert "net 8.8.8.8" in after, "dropped a check that only existed on the box"
    assert "user       workbench-apply.timer" in after, "repo check never reached the box"
    assert home.run("--check").returncode == 0

    # And it must not append the same lines again on the next run.
    home.run()
    assert conf.read_text() == after


def test_units_are_installed_from_the_repo(home):
    home.run()
    unit = home.path / ".config" / "systemd" / "user" / "workbench-apply.timer"
    assert unit.is_file()
    assert unit.read_text() == (REPO / "setup/systemd/user/workbench-apply.timer").read_text()


def test_check_detects_a_mutated_unit(home):
    """The whole point of --check is catching a box that has drifted from the
    repo, which is what workbench-apply.sh polls for."""
    home.run()
    unit = home.path / ".config" / "systemd" / "user" / "workbench-apply.timer"
    unit.write_text(unit.read_text() + "\n# edited on the box\n")

    result = home.run("--check")
    assert result.returncode == 1
    assert "workbench-apply.timer differs" in result.stdout
