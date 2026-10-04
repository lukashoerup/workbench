# Task: Opus builds everything; Fable only when stuck or as a second opinion

## Goal
Lukas, 2026-10-04: "I think we should just run opus as a default, even for
foundational stuff. If Opus gets stuck we can use fable. And perhaps use fable
once in while to review some stuff/get an opinion from another type model."
This replaces the 2026-09-19 rule that routed tasks marked `Model: fable` to
Fable. (Earlier the same day he had kept that rule; this message revises it.)

## Acceptance criteria
- [x] `docs/roles.md` states the new rule (≤ 30 lines; names Opus, Fable,
      Astra and `allowed_warning`, as `tests/test_roles.py` requires)
- [x] `context/STACK.md` and `docs/claude-project-instructions.md` agree
- [x] Tests green

## Lukas must do one step himself
Re-paste `docs/claude-project-instructions.md` into the "Workbench HQ" Project
on claude.ai (it also carries the 2026-10-04 gridmaster registration).

## Working notes
- "Stuck" is made concrete as the existing 3-attempt limit on one problem.
- Save mode now means Opus only: no Fable escalation, no Fable review.
- gridmaster's Phase 1 task line `Model: fable` is changed in that repo.
