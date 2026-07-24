# Task: include erhvervsklubben in STATUS.md

## Goal
STATUS.md reports the erhvervsklubben repo (git state, commits, open tasks) so
Lukas can see the project from his phone. Its Node/vitest suite is NOT run by
the 30-minute timer — it needs the local Supabase Docker stack; CI is the judge
there. The page must say so explicitly rather than guessing.

## Acceptance criteria
- [ ] `~/projects/erhvervsklubben` appears in STATUS.md with branch/commit/task state
- [ ] Node repos show "tests not run by this box" instead of a bogus pytest run
- [ ] Tests green
- [ ] Affected docs updated

## Scope
**May change:** `bin/workbench-status.py`, `tests/`, `CLAUDE.md` (repo table)
**Must NOT touch:** `setup/`, `~/.secrets/`, erhvervsklubben itself

## Docs affected
`CLAUDE.md` — no statement invalidated (it doesn't enumerate watched repos); verified, so: none.

## Size check
Small: one collector branch + one render branch + tests. Well under one session.

## Working notes (agent fills in)
- erhvervsklubben pushed to private GitHub repo lukashoerup/erhvervsklubben earlier today (secrets/PII scan came back clean; seed is synthetic).
