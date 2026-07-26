# Task: fix docs that lie to the next agent, and test that they stay fixed

## Goal
Several docs assert things the repo contradicts. Two of them are load-bearing:
`SYSTEM.md:11` describes a capability declared deferred 22 lines below it, and
`docs/claude-project-instructions.md:11-13` repeats that claim — and that file
is the versioned source of the claude.ai Project instructions, so the error is
live in Lukas's phone interface.

Fixing prose without a test just resets the clock, so the durable half is an
invariant test that fails when the class of error returns.

## Acceptance criteria
- [x] `SYSTEM.md:11` no longer lists "headless agent work blocks" as a live
      lenovo role
- [x] `docs/claude-project-instructions.md` matches reality; Lukas re-pastes
      into the Project (noted in working notes as an action for him)
- [x] `context/LEARNINGS.md` sudo entry states the situation honestly instead
      of asserting a claim the repo contradicts
- [x] `context/LEARNINGS.md` lingering caveat no longer says "until it is set"
      for something already set
- [x] `context/PATTERNS.md` Ollama recipe names the model that was chosen, not
      the one that was rejected
- [x] `tests/test_docs_invariants.py` catches: stale `workbench-context`
      references, `~/bin` scripts missing from `bin/`, and doc size caps
- [x] Tests green

## Scope
**May change:** `SYSTEM.md`, `docs/`, `context/`, `tests/`
**Must NOT touch:** `workbench-setup-spec.md` — it carries a historical banner
(`:3-9`) and is deliberately not kept current

## Detail
1. **`SYSTEM.md:11` vs `:33-36`.** The "What runs where" table lists lenovo as
   running "headless agent work blocks"; the session-types section below
   declares them deferred 2026-07-24. The table also says "never a workspace",
   which sits oddly beside the same claim.
2. **`docs/claude-project-instructions.md:11-13`** propagated it off-repo. Its
   own preamble says "Update this file first if the setup changes".
3. **`context/LEARNINGS.md:26-29`** asserts "No passwordless sudo… Coding
   agents cannot perform privileged setup", but
   `setup/phase1-privileged.sh:120-122` defaults `AGENT_SUDO=1` and writes
   `NOPASSWD: ALL`, while `setup/allow-agent-installs.sh` writes a scoped
   variant. **Which is actually in force is unknowable from the repo** — that
   needs a shell on the box, so this task states the ambiguity honestly and
   points at the bootstrap task rather than guessing.
4. **`context/LEARNINGS.md:31-34`** — lingering was enabled by
   `setup/phase1-privileged.sh:103`; "until it is set" is stale.
5. **`context/PATTERNS.md:33`** — the copy-paste recipe still says
   `qwen3:4b`, the model `context/STACK.md:49-56` rejected for scoring 3/6
   ("not discriminating, it is agreeing"). Anyone following the pattern wires
   up the wrong model.

The `~/bin` invariant fails today on `ollama-benchmark.py` and
`github-device-login.py`, which exist only on the box. It ships as
`xfail(strict=True)` so it turns red the moment the bootstrap task recovers
them and the marker must be removed — a forcing function rather than a TODO.

## Docs affected
The task is the docs fix. `context/LEARNINGS.md` gains a dated entry.

## Size check
Prose edits plus one new test file.

## Working notes (agent fills in)
- The invariant test earned its place immediately: it caught a straggler the
  manual sweep had missed, and each check was proven to fail when the violation
  is reintroduced (verified by temporary mutation, reverted).
- `STATUS.md` is excluded as generated output — its *generator* is authored and
  is checked, which is where the footer bug actually lived. Note that the
  published STATUS.md stays stale until the box pulls the fixed generator,
  which is the bootstrap task.
- The sudo entry is left deliberately unresolved rather than guessed. Nothing
  in the repo records whether either sudoers file was ever applied, and
  inventing an answer here is worse than admitting the gap.
- **Action for Lukas:** re-paste `docs/claude-project-instructions.md` into the
  "Workbench HQ" Project custom instructions — the stale claim is live there.
- Tests 69 -> 73 (+1 xfail).
