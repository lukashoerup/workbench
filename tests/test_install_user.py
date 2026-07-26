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


def test_a_real_file_in_bin_is_never_silently_overwritten(home):
    """A real file there is someone's script, possibly the only copy. Refuse and
    report — this is exactly how ollama-benchmark.py survived unversioned."""
    (home.path / "bin").mkdir(parents=True, exist_ok=True)
    stray = home.path / "bin" / "notify.py"
    stray.write_text("# hand-edited on the box\n")

    result = home.run()
    assert stray.read_text() == "# hand-edited on the box\n", "clobbered a real file"
    assert "refusing to replace" in result.stdout


def test_live_watchdog_config_is_never_clobbered(home):
    """The live checklist decides what gets noticed at 04:00. Overwriting it
    from the repo would silently drop checks someone added on the box."""
    conf = home.path / ".config" / "workbench" / "watchdog.conf"
    conf.parent.mkdir(parents=True, exist_ok=True)
    conf.write_text("net 8.8.8.8\n")

    home.run()
    assert conf.read_text() == "net 8.8.8.8\n"


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
