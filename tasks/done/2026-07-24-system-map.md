# Task: SYSTEM.md map + Claude Project instructions

## Goal
A half-page SYSTEM.md at the workbench root that tells a context-free Claude
(phone app, cloud session, new machine) what this system is, what runs where,
and the agreed autonomy rules — plus a paste-ready Claude Project instructions
file pointing at it.

## Acceptance criteria
- [ ] SYSTEM.md exists, ≤ ~90 lines, covers: what runs where, channels, session types, autonomy boundary, decision flow, repos
- [ ] docs/claude-project-instructions.md holds the paste-ready Project text
- [ ] CLAUDE.md routing table points to SYSTEM.md
- [ ] Tests green

## Scope
**May change:** `SYSTEM.md`, `docs/`, `CLAUDE.md`
**Must NOT touch:** `bin/`, `setup/`

## Docs affected
`CLAUDE.md` (routing table row). SYSTEM.md is itself the doc.

## Size check
Docs only, one session.

## Working notes (agent fills in)
- Autonomy boundary and work-block model as agreed with Lukas 2026-07-24.
