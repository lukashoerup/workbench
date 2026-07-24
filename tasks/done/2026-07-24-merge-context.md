# Task: merge workbench-context into workbench/context/

## Goal
One repo fewer: the 176-line cross-project knowledge base moves into
`workbench/context/`, so references are repo-qualified and resolve from any
machine (relative `../workbench-context` paths only worked on the lenovo's
folder layout). The old repo is archived on GitHub, not deleted — history kept.

## Acceptance criteria
- [x] `context/STACK.md`, `context/PATTERNS.md`, `context/LEARNINGS.md` in this repo
- [x] All references updated: CLAUDE.md, SYSTEM.md, claude-project-instructions.md, workbench-status.py REPOS
- [x] `lukashoerup/workbench-context` archived on GitHub with a pointer commit
- [x] Tests green

## Scope
**May change:** `context/`, `CLAUDE.md`, `SYSTEM.md`, `docs/`, `bin/workbench-status.py`
**Must NOT touch:** `setup/`

## Docs affected
CLAUDE.md, SYSTEM.md, claude-project-instructions.md — updated here.

## Size check
File moves + reference sweep.

## Working notes (agent fills in)
- Decision by Lukas 2026-07-24. Git history of the old repo lives in the
  archived GitHub repo; files were copied, not history-grafted.
- Local `~/workbench-context/` dir left in place pending Lukas's deletion OK.
