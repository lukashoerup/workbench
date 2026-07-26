# Task: make the plain-language rule permanent

## Goal
Lukas said he does not fully understand what agents write to him. That is a
defect in the system's primary interface, and the fix currently exists only in
a chat window — which `SYSTEM.md:24-27` says is exactly where it will be lost:
decisions made in chat must be committed, because agents on other machines read
the repo, not the chat.

Every future session, on every device, has to inherit this.

## Acceptance criteria
- [x] The rule is in `CLAUDE.md`, `SYSTEM.md` and
      `docs/claude-project-instructions.md`, worded the same way
- [x] It states the reason, not just the instruction
- [x] Line caps still pass (`CLAUDE.md` ≤ 80, `SYSTEM.md` ≤ 90) — enforced by
      `tests/test_docs_invariants.py`
- [x] Tests green

## Scope
**May change:** `CLAUDE.md`, `SYSTEM.md`, `docs/claude-project-instructions.md`
**Must NOT touch:** anything about how repo artefacts are written — the split
is by channel, not a lowering of precision anywhere

## The rule (agreed with Lukas 2026-07-26)
- **Chat: plain language.** No file paths, no jargon, no code. He does not
  program; an update he cannot read is not an update.
- **Repo: technical as usual.** Docs, commit messages, task files and code
  comments keep their precision — that is what they are for.
- **Interrupt him only** for a decision genuinely his (money, security, access,
  taste), or when the machine's behaviour changes — new jobs, new automatic
  behaviour — even where permission is not needed.

State the reason inline wherever it appears. A rule whose purpose is visible
survives; a bare instruction gets tidied away by the next agent saving lines.

## Lukas must do one step himself
`docs/claude-project-instructions.md` is the versioned original of the
claude.ai Project instructions. A commit cannot update the Project — that copy
lives on Anthropic's servers. **He has to re-paste it.** This is the second
time this file has needed re-pasting today (the first was the stale
"headless agent work blocks" claim), so both changes go over in one paste.

## Docs affected
The task is the docs change.

## Size check
A few lines in three files.

## Working notes (agent fills in)
- Placed in all three so it is inherited whichever door a Claude comes in
  through: CLAUDE.md at the start of every repo session, SYSTEM.md when meeting
  the system for the first time, and the Project instructions on the phone.
- Line caps after the change: CLAUDE.md 71/80, SYSTEM.md 87/90. Tight in
  SYSTEM.md — anything added there next needs to earn its place.
- The reason is stated inline in each copy, deliberately. A bare instruction
  gets tidied away by the next agent trying to save lines.
- **Outstanding for Lukas: re-paste `docs/claude-project-instructions.md` into
  the "Workbench HQ" Project on claude.ai.** Two changes are waiting in it now.
