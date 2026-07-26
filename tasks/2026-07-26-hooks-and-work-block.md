# Task: guardrail hooks, then the bounded work-block runner

Depends on: the box being able to pull, and `reports/` publishing existing
(the hook allowlist and the publisher's staging pathspec must match).

## Goal
Two halves of the same contract. The `CLAUDE.md:22-31` guardrails and the spec
§2.5 circuit breaker exist only as prose — nothing enforces them. And session
type 2 (`SYSTEM.md:33`) was un-deferred on 2026-07-26: Lukas wants one batched
summary instead of prompting per task.

## Start from the hook that already exists
`bin/new-project.sh:160-184` (recovered from the box 2026-07-26) already
contains a working pre-commit hook: protected paths, a dependency-approval
marker, and a tests-and-lint gate — including the subtlety that an empty
`tests/` makes pytest exit 5, which is not a red suite. Adapt that rather than
writing a new one, and keep the two in step.

Note it uses the marker `DEPENDENCY APPROVED`; this repo's task files were
written expecting `Dependency approved by Lukas:`. Pick one and use it in both.

## Acceptance criteria — hooks
- [ ] `hooks/pre-commit` + `setup/install-hooks.sh`, activated with
      `git config core.hooksPath hooks`
- [ ] **Publisher fast-path is the first branch in the file:** staged paths
      entirely within `STATUS.md` / `reports/` exit 0 without running anything
- [ ] Blocks staged `.env`, `.secrets/`, `/etc` paths
- [ ] Blocks `pyproject.toml` dependency changes without the literal marker
      `Dependency approved by Lukas:` in a task file on the branch
- [ ] Rejects a commit with red tests
- [ ] `hooks/circuit-breaker.sh`: same failing node-id set 3× → exit 2; a
      different set or a green run resets; state keyed per branch

## Acceptance criteria — work block
- [ ] Does nothing unless `~/.config/workbench/work-block.enabled` exists
      (default **off**)
- [ ] Works only task files explicitly marked approved
- [ ] Per task: branch `task/<name>`, headless run, tests, push **only** on green
- [ ] **Never merges to `main`, never force-pushes**
- [ ] 3 attempts on the same failing test → note in the task file, move to the
      review queue, move on (`CLAUDE.md:28-29`)
- [ ] Exits the block cleanly on rate-limit exhaustion rather than burning retries
- [ ] Ends with exactly ONE Telegram summary: done / blocked / questions
- [ ] Writes a heartbeat
- [ ] Tests green

## Scope
**May change:** `hooks/`, `setup/install-hooks.sh`, `bin/work-block.sh`,
`setup/systemd/user/`, `.claude/settings.json`, `tests/`
**Must NOT touch:** `main` merge policy, `bin/publish-status.sh` containment

## The trap: the hook will fight the status publisher
`bin/publish-status.sh` commits and `--amend`s on `main` **every 30 minutes**.
A hook that runs pytest or blocks commits on `main` without the allowlist
fast-path first will fire ~48×/day on a CPU-only box that is also loading a
6.6 GB model — and can wedge the phone's only view of the machine. The
allowlist must stay byte-for-byte in sync with the publisher's staging
pathspec; if one is widened, widen the other in the same commit.

## Why the runner is bounded rather than continuous
Spec §1 (`workbench-setup-spec.md:34`): *"Never plan long autonomous overnight
cloud-agent runs — 5-hour rate-limit windows are the real bottleneck, not
compute."* That warning is not overridden by un-deferring the runner; it is why
the runner is capped, night-scheduled, one atomic task at a time, and off by
default. The free layer (CI, watchdog, local-model jobs) is what runs forever.

## Needs Lukas
- Enabling the kill switch the first time is his call, not an agent's.
- `.claude/settings.json` changes agent behaviour in his own sessions too.

## Docs affected
`SYSTEM.md` session types (already updated 2026-07-26), `context/STACK.md`
scheduled jobs.

## Size check
Two commits minimum: hooks, then the runner.

## Working notes (agent fills in)
