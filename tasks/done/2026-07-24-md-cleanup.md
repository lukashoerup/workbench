# Task: markdown cleanup after the interface-model decision

## Goal
Workbench docs stop describing the pre-cloud-dispatch world: SSH/tmux demoted
to fallback, the setup spec marked historical with its known deviations.

## Acceptance criteria
- [x] CLAUDE.md "How Lukas reaches this system" reflects Claude app / GitHub / Telegram / SSH-fallback
- [x] workbench-setup-spec.md carries a historical banner naming the deviations
- [x] Tests green

## Scope
**May change:** `CLAUDE.md`, `workbench-setup-spec.md`
**Must NOT touch:** `bin/`, `setup/`

## Docs affected
These ARE the docs.

## Size check
Two edits.

## Working notes (agent fills in)
- `bin/` reviewed for legacy code: nothing to remove — `work`/tmux stays as the
  fallback path, setup and telegram scripts remain the machine's ops tooling.
