# Task: register the new gridmaster repo

## Goal
Lukas started a new project on 2026-10-04: a renewable-energy tycoon game for
Steam, working title "Gridmaster", in the private repo `lukashoerup/gridmaster`.
Sessions that start from the workbench (the "Workbench HQ" Project on the phone,
cloud dispatch) must know it exists and where its conventions live — otherwise
"what's going on with the game?" gets answered from memory.

## Acceptance criteria
- [x] `SYSTEM.md` repo table lists `gridmaster` (line cap 90 still holds)
- [x] `docs/claude-project-instructions.md` names the repo for the GitHub
      connector and as an active project
- [x] The repo-creation gotcha is recorded in `context/LEARNINGS.md`
- [x] Tests green

## Scope
**May change:** `SYSTEM.md`, `docs/claude-project-instructions.md`,
`context/LEARNINGS.md`, this file
**Must NOT touch:** anything in `bin/`, `setup/`, the game repo's own docs
(they live in `lukashoerup/gridmaster`)

## Lukas must do two steps himself
1. Re-paste `docs/claude-project-instructions.md` into the "Workbench HQ"
   Project on claude.ai — a commit cannot update the Project's copy.
2. Add `lukashoerup/gridmaster` to that Project's GitHub connector.

## Docs affected
The task is the docs change.

## Working notes
- `create_repository` from the cloud session returned 403; Lukas created the
  repo himself and the session attached it with `add_repo`. See LEARNINGS.
- Game research, plan and conventions are in the gridmaster repo itself
  (`CLAUDE.md`, `docs/`, `tasks/`), not here.
