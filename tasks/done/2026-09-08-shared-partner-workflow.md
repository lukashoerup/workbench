# Task: shared independent review and project partner workflow

## Goal
Adopt Lukas's requested cross-model scrutiny and critical project guidance as
shared project rules, including Erhvervsklubben and future project scaffolds.

## Authorization
2026-09-08: Lukas requested the workflow and explicitly answered
"Also update the GitHub project rules now" during the Workbench review.

## Acceptance criteria
- [x] Canonical, versioned workflow covers idea, implementation and project review.
- [x] Claude/Codex root instructions route to it without breaking line budgets.
- [x] Future projects receive a local copy and review instructions automatically.
- [x] Existing project copy and exceptions are recorded; background jobs are not
      represented as configured merely because instructions were written.
- [x] Relevant checks pass; task and affected docs reflect actual delivery.

## Scope
May change: CLAUDE.md, SYSTEM.md, docs/, context/STACK.md, bin/new-project.sh,
tests/test_new_project.py, this task. No credentials, CI configuration,
operational scripts, deployment settings, or dependencies.

## Docs affected
Shared workflow, rollout status, system map, repository instructions, Claude
Project paste-ready instructions and the cross-project decisions.

## Working notes
This installs standing rules. Review triggers, independent reviewer access,
scheduled check-ins and gates require separate verified implementation.
Codex authored this change; it has not received independent Claude review.

## Validation
- 14 relevant documentation and installer tests passed on macOS.
- Bash syntax and diff whitespace checks passed.
- Generated a temporary project through the ~/bin symlink: identical policy,
  Claude/Codex routing, review evidence field and existing-project refusal verified.
- Policy copies are identical in both projects. Full Linux CI will run on the PR.
- The full macOS suite was previously 81 passing / 6 Linux-command failures;
  this change does not claim those platform-specific watchdog tests passed locally.

## Follow-up decision — 2026-09-09
Lukas chose questioning whether a quiet project is still worth pursuing as the
default. Policy version 2026-09-09.1 reflects that preference in both projects.
