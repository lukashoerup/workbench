"""Tests for bin/weekly-gardener.py — the one job that runs on Claude.

Lukas approved spending tokens here because the judgement cannot be computed
(context/STACK.md, 2026-08-04). That approval buys the *reasoning*, not trust in
the output, so the properties under test are the ones that keep a confident wrong
answer from reaching him:

  1. It only points. No write tools, no commits, no edits — ever.
  2. Every finding is checked against the file it names before it is shown.
     An invented quotation is quarantined, not surfaced.
  3. A rate-limited run stops cleanly and says it was truncated, rather than
     quietly reporting a partial pass as a complete one.

Claude is stubbed as a subprocess throughout: no network, no tokens, CI-safe.
"""
import importlib.util
import json
import os
import subprocess
import textwrap
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


@pytest.fixture
def gardener():
    spec = importlib.util.spec_from_file_location(
        "weekly_gardener", REPO / "bin" / "weekly-gardener.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def repo(tmp_path):
    """A small git repo with docs, generated output and a historical record.

    Deliberately a subdirectory of tmp_path, so the stub `claude` and the fake
    heartbeat live *outside* it — otherwise the test scaffolding shows up as
    untracked files and the "nothing outside reports/ was written" assertion
    catches itself rather than the code.
    """
    tmp_path = tmp_path / "repo"
    tmp_path.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    (tmp_path / "CLAUDE.md").write_text(
        "# Rules\n\nRun tests BEFORE every commit. Never commit\non red tests.\n"
    )
    (tmp_path / "SYSTEM.md").write_text("# System\n\nThe box pulls every 10 minutes.\n")
    (tmp_path / "STATUS.md").write_text("# Status\n\nGenerated output.\n")
    for rel in ("reports/nightly/2026-08-04.md", "tasks/done/old.md"):
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("# Not a doc\n")
    (tmp_path / "workbench-setup-spec.md").write_text("# Spec\n\nHistorical.\n")

    env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t"}
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True, env=env)
    subprocess.run(["git", "commit", "-q", "-m", "seed"], cwd=tmp_path, check=True, env=env)
    return tmp_path


class Stub:
    """A stand-in `claude` executable, plus the log of how it was invoked.

    Behaves as a path anywhere one is expected, so the code under test cannot
    tell it apart from the real CLI.
    """

    def __init__(self, path, argv_log):
        self.path = path
        self.argv_log = argv_log

    def __str__(self):
        return str(self.path)

    def __fspath__(self):
        return str(self.path)


def stub_claude(tmp_path, body, name="fake-claude"):
    """A stand-in `claude` that prints `body` and records how it was invoked."""
    argv_log = tmp_path / f"{name}-argv.jsonl"
    script = tmp_path / name
    # One JSON array per line: the prompt is multi-line, so any plain-text
    # separator would smear a single invocation across many log lines and make
    # "how many calls were made" unanswerable.
    script.write_text(textwrap.dedent(f"""\
        #!/usr/bin/env python3
        import json, sys
        with open({str(argv_log)!r}, "a") as fh:
            fh.write(json.dumps(sys.argv[1:]) + "\\n")
        sys.stdout.write({body!r})
        """))
    script.chmod(0o755)
    return Stub(script, argv_log)


def invocations(script):
    if not script.argv_log.exists():
        return []
    return [json.loads(line) for line in script.argv_log.read_text().splitlines() if line.strip()]


# ------------------------------------------------------------------- the guard
def test_a_real_quotation_is_confirmed(gardener, repo):
    ok, why = gardener.verify(
        {"file": "SYSTEM.md", "statement": "The box pulls every 10 minutes."}, repo
    )
    assert ok, why


def test_a_quotation_across_a_line_wrap_still_matches(gardener, repo):
    """These docs are hard-wrapped, so a quote will routinely span a newline. A
    guard that rejects those rejects nearly every true finding, which is the
    same as having no job at all."""
    ok, why = gardener.verify(
        {"file": "CLAUDE.md", "statement": "Run tests BEFORE every commit. Never commit on red tests."},
        repo,
    )
    assert ok, why


def test_an_invented_quotation_is_rejected(gardener, repo):
    ok, why = gardener.verify(
        {"file": "SYSTEM.md", "statement": "The box pulls every 3 seconds."}, repo
    )
    assert not ok
    assert "does not appear" in why


def test_a_finding_about_a_nonexistent_file_is_rejected(gardener, repo):
    ok, why = gardener.verify({"file": "NOPE.md", "statement": "anything"}, repo)
    assert not ok
    assert "no such file" in why


def test_a_path_escaping_the_repo_is_rejected(gardener, repo):
    """Nothing should be reading /etc through a findings field."""
    ok, why = gardener.verify({"file": "../../etc/passwd", "statement": "root"}, repo)
    assert not ok


def test_a_finding_missing_its_fields_is_rejected(gardener, repo):
    assert not gardener.verify({"file": "SYSTEM.md"}, repo)[0]
    assert not gardener.verify({"statement": "orphan"}, repo)[0]
    assert not gardener.verify({"file": "SYSTEM.md", "statement": "   "}, repo)[0]


# ------------------------------------------------------------------- parsing
def test_bare_json_parses(gardener):
    assert gardener.parse_findings('{"findings": []}') == []


def test_fenced_json_parses(gardener):
    """The prompt forbids the fence, but losing a real finding to a stray
    ```json would be a silly way to waste the call."""
    out = gardener.parse_findings('```json\n{"findings": [{"file": "a"}]}\n```')
    assert out == [{"file": "a"}]


def test_json_with_prose_around_it_parses(gardener):
    out = gardener.parse_findings('Sure!\n{"findings": [{"file": "b"}]}\nHope that helps.')
    assert out == [{"file": "b"}]


@pytest.mark.parametrize("bad", ["", "no json here", "{not json}", '{"wrong": 1}', "[]"])
def test_unparseable_replies_are_none_not_empty(gardener, bad):
    """None means "the call failed"; [] means "reviewed, nothing found".
    Collapsing the two would report a broken model as a clean bill of health."""
    assert gardener.parse_findings(bad) is None


# -------------------------------------------------------------- rate limiting
@pytest.mark.parametrize("text", [
    "Error: rate limit exceeded",
    "You have hit your usage limit for this 5-hour window",
    '{"type": "rate_limit_error"}',
])
def test_rate_limit_messages_are_recognised(gardener, text):
    assert gardener.is_rate_limited(text)


def test_ordinary_output_is_not_mistaken_for_a_rate_limit(gardener):
    assert not gardener.is_rate_limited('{"findings": []}')


# ------------------------------------------------------------- which files
def test_generated_and_historical_files_are_not_reviewed(gardener, repo):
    """STATUS.md is rewritten every 30 minutes, so 'this is no longer true' is
    its normal condition. reports/ is this job's own output. tasks/done/ is a
    record of what was true at the time."""
    files = gardener.docs_files(repo)
    assert "CLAUDE.md" in files
    assert "SYSTEM.md" in files
    assert "STATUS.md" not in files
    assert "workbench-setup-spec.md" not in files
    assert not any(f.startswith("reports/") for f in files)
    assert not any(f.startswith("tasks/done/") for f in files)


# ------------------------------------------------------------- only points
def test_the_mutating_tools_are_denied_on_every_call(gardener, repo, tmp_path):
    """'It only points' is enforced by the harness, not by the prompt asking
    nicely. The file's contents are already in the prompt, so a correct run needs
    no tools at all."""
    claude = stub_claude(tmp_path, '{"findings": []}')
    gardener.run_claude("anything", claude)

    argv = invocations(claude)[0]
    assert "--disallowedTools" in argv
    denied = argv[argv.index("--disallowedTools") + 1:]
    for tool in ("Edit", "Write", "NotebookEdit", "Bash"):
        assert tool in denied
    assert "-p" in argv, "must be headless"


def test_a_run_never_modifies_the_docs(gardener, repo, tmp_path, monkeypatch):
    """The strongest form of 'never fixes anything': nothing tracked changes,
    except the report it is supposed to write."""
    claude = stub_claude(tmp_path, json.dumps({"findings": [
        {"file": "SYSTEM.md", "statement": "The box pulls every 10 minutes.",
         "reason": "changed", "confidence": "high"}
    ]}))
    monkeypatch.setattr(gardener, "HEARTBEAT", tmp_path / "hb" / "gardener")
    monkeypatch.setattr(gardener, "_notify", lambda m: None)
    monkeypatch.setattr(gardener.sys, "argv", [
        "weekly-gardener.py", "--repo", str(repo), "--claude", str(claude)])

    assert gardener.main() == 0

    status = subprocess.run(["git", "status", "--porcelain"], cwd=repo,
                            capture_output=True, text=True).stdout
    for line in status.splitlines():
        code, path = line[:2].strip(), line[3:]
        assert code == "??", f"a tracked file was modified: {line}"
        assert path.startswith("reports/"), f"wrote outside reports/: {line}"


# ------------------------------------------------------------------ end to end
def test_confirmed_and_invented_findings_are_separated(gardener, repo, tmp_path, monkeypatch):
    claude = stub_claude(tmp_path, json.dumps({"findings": [
        {"file": "SYSTEM.md", "statement": "The box pulls every 10 minutes.",
         "reason": "the cadence changed", "confidence": "high"},
        {"file": "SYSTEM.md", "statement": "This sentence was never written.",
         "reason": "invented", "confidence": "high"},
    ]}))
    sent = []
    monkeypatch.setattr(gardener, "HEARTBEAT", tmp_path / "hb" / "gardener")
    monkeypatch.setattr(gardener, "_notify", lambda m: sent.append(m))
    monkeypatch.setattr(gardener.sys, "argv", [
        "weekly-gardener.py", "--repo", str(repo), "--claude", str(claude)])

    assert gardener.main() == 0

    report = next((repo / "reports" / "gardener").glob("*.md")).read_text()
    assert "the cadence changed" in report
    assert "This sentence was never written." not in report
    assert "Quarantined" in report
    assert len(sent) == 1


def test_nothing_found_writes_a_report_but_stays_silent(gardener, repo, tmp_path, monkeypatch):
    """A weekly 'no findings' buzz is how a channel teaches its reader to
    ignore it."""
    claude = stub_claude(tmp_path, '{"findings": []}')
    sent = []
    monkeypatch.setattr(gardener, "HEARTBEAT", tmp_path / "hb" / "gardener")
    monkeypatch.setattr(gardener, "_notify", lambda m: sent.append(m))
    monkeypatch.setattr(gardener.sys, "argv", [
        "weekly-gardener.py", "--repo", str(repo), "--claude", str(claude)])

    assert gardener.main() == 0
    assert sent == []
    assert "Nothing found" in next((repo / "reports" / "gardener").glob("*.md")).read_text()


def test_one_call_per_docs_file(gardener, repo, tmp_path, monkeypatch):
    """A single call carrying every doc invites the model to answer about the
    wrong file, and makes one rate-limit failure lose the entire run."""
    claude = stub_claude(tmp_path, '{"findings": []}')
    monkeypatch.setattr(gardener, "HEARTBEAT", tmp_path / "hb" / "gardener")
    monkeypatch.setattr(gardener, "_notify", lambda m: None)
    monkeypatch.setattr(gardener.sys, "argv", [
        "weekly-gardener.py", "--repo", str(repo), "--claude", str(claude)])

    gardener.main()
    assert len(invocations(claude)) == len(gardener.docs_files(repo))


def test_a_rate_limited_run_stops_and_says_so(gardener, repo, tmp_path, monkeypatch):
    claude = stub_claude(tmp_path, "Error: usage limit reached for this window")
    hb = tmp_path / "hb" / "gardener"
    monkeypatch.setattr(gardener, "HEARTBEAT", hb)
    monkeypatch.setattr(gardener, "_notify", lambda m: None)
    monkeypatch.setattr(gardener.sys, "argv", [
        "weekly-gardener.py", "--repo", str(repo), "--claude", str(claude)])

    assert gardener.main() == 0, "hitting a limit is expected, not a crash"
    assert len(invocations(claude)) == 1, "must stop, not burn the window on the rest"

    report = next((repo / "reports" / "gardener").glob("*.md")).read_text()
    assert "stopped early" in report.lower()
    assert not hb.exists(), "a truncated pass must not look like a completed one"


def test_a_complete_run_writes_the_heartbeat(gardener, repo, tmp_path, monkeypatch):
    claude = stub_claude(tmp_path, '{"findings": []}')
    hb = tmp_path / "hb" / "gardener"
    monkeypatch.setattr(gardener, "HEARTBEAT", hb)
    monkeypatch.setattr(gardener, "_notify", lambda m: None)
    monkeypatch.setattr(gardener.sys, "argv", [
        "weekly-gardener.py", "--repo", str(repo), "--claude", str(claude)])

    gardener.main()
    assert hb.is_file()


def test_a_broken_reply_is_quarantined_not_treated_as_clean(gardener, repo, tmp_path, monkeypatch):
    claude = stub_claude(tmp_path, "I'm afraid I can't help with that.")
    monkeypatch.setattr(gardener, "HEARTBEAT", tmp_path / "hb" / "gardener")
    monkeypatch.setattr(gardener, "_notify", lambda m: None)
    monkeypatch.setattr(gardener.sys, "argv", [
        "weekly-gardener.py", "--repo", str(repo), "--claude", str(claude)])

    gardener.main()
    report = next((repo / "reports" / "gardener").glob("*.md")).read_text()
    assert "not the requested JSON" in report


def test_the_prompt_carries_the_file_and_the_commits(gardener, repo, tmp_path, monkeypatch):
    """The model is never asked to go and read anything — that is what lets the
    tools be denied."""
    claude = stub_claude(tmp_path, '{"findings": []}')
    monkeypatch.setattr(gardener, "HEARTBEAT", tmp_path / "hb" / "gardener")
    monkeypatch.setattr(gardener, "_notify", lambda m: None)
    monkeypatch.setattr(gardener.sys, "argv", [
        "weekly-gardener.py", "--repo", str(repo), "--claude", str(claude)])

    gardener.main()
    prompts = [argv[-1] for argv in invocations(claude)]
    # Match the review marker, not a bare filename — the commit stat block names
    # every changed file, so "SYSTEM.md in prompt" is true of every call.
    system_prompt = next(p for p in prompts if "The file under review: SYSTEM.md" in p)
    assert "The box pulls every 10 minutes." in system_prompt
    assert "documentation gardener" in system_prompt
    assert "never fix anything yourself" in system_prompt
