"""Unit tests for workbench-status.py collectors (the dash in the filename
means we load it via importlib rather than a plain import)."""
import importlib.util
import subprocess
from pathlib import Path

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
