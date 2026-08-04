"""Tests for bin/publish-status.sh — the phone's view of this machine.

A stale status page is worse than no status page: it answers "what is going
on?" with yesterday's truth and nothing signals the difference. So the
properties that matter are that it publishes at all (the untracked-first-run
bug), that it stays quiet when nothing changed, and that it never
auto-publishes work in progress.

Each test builds a throwaway git repo with a local bare remote, so nothing
touches GitHub.
"""
import os
import subprocess
import textwrap
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "bin" / "publish-status.sh"


def git(repo, *args, check=True):
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True, check=check
    ).stdout.strip()


@pytest.fixture
def pub(tmp_path):
    """Fake HOME containing ~/workbench wired to a local bare remote."""
    home = tmp_path
    repo = home / "workbench"
    remote = home / "remote.git"
    (home / "bin").mkdir()
    (home / "logs").mkdir()
    repo.mkdir()

    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True)
    git(repo, "config", "user.email", "test@example.com")
    git(repo, "config", "user.name", "Test")
    (repo / "seed.txt").write_text("seed\n")
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", "seed")
    git(repo, "remote", "add", "origin", str(remote))
    git(repo, "push", "-q", "origin", "main")

    # Stub the status generator: writes whatever content the test asked for.
    content = home / "content.txt"
    content.write_text("initial status\n")
    gen = home / "bin" / "workbench-status.py"
    gen.write_text(
        textwrap.dedent(
            f"""\
            #!/usr/bin/env python3
            import sys, pathlib
            out = pathlib.Path(sys.argv[sys.argv.index("--write") + 1])
            body = pathlib.Path({str(content)!r}).read_text()
            out.write_text("_Generated " + str(__import__("time").time()) + "_\\n" + body)
            """
        )
    )
    gen.chmod(0o755)

    sent = home / "sent.txt"
    notify = home / "bin" / "notify.py"
    notify.write_text(
        textwrap.dedent(
            f"""\
            #!/usr/bin/env python3
            import sys
            open({str(sent)!r}, "a").write(" ".join(sys.argv[1:]) + "\\n")
            """
        )
    )
    notify.chmod(0o755)

    class Harness:
        def __init__(self):
            self.home, self.repo, self.remote = home, repo, remote

        def set_status(self, text):
            content.write_text(text)

        def run(self):
            env = {**os.environ, "HOME": str(home)}
            return subprocess.run(
                ["bash", str(SCRIPT)], env=env, capture_output=True, text=True, timeout=60
            )

        @property
        def sent(self):
            return sent.read_text().splitlines() if sent.exists() else []

        def remote_has_status(self):
            out = subprocess.run(
                ["git", "ls-tree", "--name-only", "main"],
                cwd=remote, capture_output=True, text=True,
            ).stdout
            return "STATUS.md" in out

        def commit_count(self):
            return int(git(self.repo, "rev-list", "--count", "HEAD"))

    return Harness()


# ------------------------------------------------------------ the shipped bug
def test_first_run_publishes_an_untracked_status_file(pub):
    """git diff reports nothing for an untracked file. The first run — the one
    that matters on a fresh clone — must still publish."""
    pub.set_status("line one\nline two\nline three\n")
    result = pub.run()
    assert result.returncode == 0
    assert pub.remote_has_status(), "STATUS.md never reached the remote"


# ------------------------------------------------------------------ freshness
def test_substantive_change_is_published(pub):
    """What matters is that new content reaches the remote — not that it
    arrives as a separate commit, since status commits collapse by design."""
    pub.set_status("a\nb\nc\n")
    pub.run()

    pub.set_status("completely\ndifferent\ncontent\nhere\nnow\n")
    assert pub.run().returncode == 0

    remote_body = subprocess.run(
        ["git", "show", "main:STATUS.md"], cwd=pub.remote,
        capture_output=True, text=True,
    ).stdout
    assert "different" in remote_body


def test_identical_content_creates_no_commit(pub):
    """Every 30 minutes forever — unchanged state must not spam the history."""
    pub.set_status("a\nb\nc\n")
    pub.run()
    before = pub.commit_count()

    pub.run()
    pub.run()
    assert pub.commit_count() == before


# ---------------------------------------------------------------- containment
def test_work_in_progress_is_never_auto_committed(pub):
    """Publishing must not sweep up unrelated edits. Pushing half-finished work
    is a human decision."""
    pub.set_status("a\nb\nc\n")
    pub.run()

    (pub.repo / "half_done.py").write_text("def broken(:\n")
    (pub.repo / "seed.txt").write_text("locally edited\n")

    pub.set_status("x\ny\nz\nq\nr\n")
    pub.run()

    tracked = git(pub.repo, "ls-tree", "--name-only", "HEAD")
    assert "half_done.py" not in tracked
    assert git(pub.repo, "show", "HEAD:seed.txt") == "seed"


# --------------------------------------------------- reports (added 2026-08-04)
def remote_tree(pub):
    return subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", "main"],
        cwd=pub.remote, capture_output=True, text=True,
    ).stdout


def test_a_nightly_brief_reaches_the_remote(pub):
    """A brief written at 03:15 that never leaves the box is a brief nobody can
    read — and Lukas reads this repo through the GitHub app, not over SSH."""
    pub.set_status("a\nb\nc\n")
    pub.run()

    brief = pub.repo / "reports" / "nightly" / "2026-08-04.md"
    brief.parent.mkdir(parents=True)
    brief.write_text("# Nightly brief\n\nNothing needs a human.\n")
    pub.run()

    assert "reports/nightly/2026-08-04.md" in remote_tree(pub)


def test_a_new_report_publishes_even_when_the_status_page_is_unchanged(pub):
    """The timestamp-only early exit must not swallow a report. The brief lands
    at 03:15 on a quiet night, which is exactly when STATUS.md has not moved —
    so the one case the report most needs to survive is the one that used to
    exit 0 without committing anything.

    It arrives by amending the standing status commit rather than adding a new
    one; collapsing consecutive status commits is deliberate, and the report
    rides along in the amended tree.
    """
    pub.set_status("steady\n")
    pub.run()

    report = pub.repo / "reports" / "gardener" / "2026-08-04.md"
    report.parent.mkdir(parents=True)
    report.write_text("# Docs gardener\n\nNothing found.\n")
    pub.run()

    assert "reports/gardener/2026-08-04.md" in remote_tree(pub)
    published = subprocess.run(
        ["git", "show", "main:reports/gardener/2026-08-04.md"],
        cwd=pub.remote, capture_output=True, text=True,
    ).stdout
    assert "Nothing found." in published, "the file reached the remote, but empty"


def test_reports_do_not_widen_the_net_to_everything_else(pub):
    """Widening the pathspec must not turn the publisher into an auto-committer.
    Work in progress stays a human decision."""
    pub.set_status("a\n")
    pub.run()

    (pub.repo / "reports").mkdir()
    (pub.repo / "reports" / "brief.md").write_text("# report\n")
    (pub.repo / "half_done.py").write_text("def broken(:\n")
    pub.run()

    tree = remote_tree(pub)
    assert "reports/brief.md" in tree
    assert "half_done.py" not in tree


# ------------------------------------------------------------- push failures
def test_unreachable_remote_is_reported_not_silent(pub):
    pub.set_status("a\nb\nc\n")
    pub.run()
    git(pub.repo, "remote", "set-url", "origin", "/nonexistent/remote.git")

    pub.set_status("changed\ncontent\nentirely\nhere\n")
    result = pub.run()
    assert result.returncode == 1, "a failed push must not report success"


def test_third_consecutive_push_failure_alerts(pub):
    """One failure is a Wi-Fi blip. Three means the phone view is going stale."""
    pub.set_status("a\nb\nc\n")
    pub.run()
    git(pub.repo, "remote", "set-url", "origin", "/nonexistent/remote.git")

    for i in range(3):
        pub.set_status(f"change number {i}\n" + f"body-{i}\n" * 5)
        pub.run()

    assert len(pub.sent) == 1, f"expected exactly one alert, got {pub.sent}"
    assert "stale" in pub.sent[0]


def test_a_permanently_broken_push_keeps_re_alerting(pub):
    """The failure that matters most is the one that does not go away. Alerting
    exactly once and then going quiet leaves Lukas watching a frozen page that
    still looks healthy — so the alert has to repeat on a schedule."""
    pub.set_status("a\nb\nc\n")
    pub.run()
    git(pub.repo, "remote", "set-url", "origin", "/nonexistent/remote.git")

    for i in range(30):
        pub.set_status(f"change number {i}\n" + f"body-{i}\n" * 5)
        pub.run()

    # Alerts at failure 3, 15 and 27 — first at ~1.5h, then every ~6h.
    assert len(pub.sent) == 3, f"expected 3 alerts across 30 failures, got {pub.sent}"
    assert "3 times" in pub.sent[0]
    assert "15 times" in pub.sent[1]
    assert "27 times" in pub.sent[2]


def test_recovered_push_clears_the_failure_count(pub):
    pub.set_status("a\nb\nc\n")
    pub.run()
    good_url = str(pub.remote)

    git(pub.repo, "remote", "set-url", "origin", "/nonexistent/remote.git")
    pub.set_status("first failure\n" + "alpha\n" * 5)
    pub.run()

    git(pub.repo, "remote", "set-url", "origin", good_url)
    pub.set_status("now working\n" + "omega\n" * 5)
    assert pub.run().returncode == 0

    state = pub.home / ".local" / "state" / "workbench" / "publish-failures"
    assert not state.exists(), "failure count should reset after a good push"


# ------------------------------------------------------------------- history
def test_consecutive_status_runs_collapse_into_one_commit(pub):
    """Uptime and log tails change every run. Without amending, main would take
    ~48 status commits a day and real history would be unreadable."""
    pub.set_status("a\nb\nc\n")
    pub.run()
    after_first = pub.commit_count()

    for i in range(4):
        pub.set_status(f"run {i}\n" + f"content-{i}\n" * 4)
        assert pub.run().returncode == 0

    assert pub.commit_count() == after_first, "status commits should collapse"


def test_amending_never_swallows_a_real_commit(pub):
    """A status commit must never absorb Lukas's or an agent's actual work."""
    pub.set_status("a\nb\nc\n")
    pub.run()

    (pub.repo / "feature.py").write_text("def real_work(): pass\n")
    git(pub.repo, "add", "feature.py")
    git(pub.repo, "commit", "-q", "-m", "Add a real feature")
    real_sha = git(pub.repo, "rev-parse", "HEAD")

    pub.set_status("later\nstatus\nupdate\nhere\n")
    assert pub.run().returncode == 0

    assert git(pub.repo, "cat-file", "-t", real_sha) == "commit"
    assert "Add a real feature" in git(pub.repo, "log", "--pretty=%s")
    assert "feature.py" in git(pub.repo, "ls-tree", "--name-only", "HEAD")


def test_status_content_reaches_the_remote_after_amending(pub):
    """Amend + force-push must still leave the remote holding current content."""
    pub.set_status("a\nb\nc\n")
    pub.run()
    pub.set_status("the\nnewest\ncontent\nvisible\n")
    pub.run()

    remote_body = subprocess.run(
        ["git", "show", "main:STATUS.md"], cwd=pub.remote,
        capture_output=True, text=True,
    ).stdout
    assert "newest" in remote_body
