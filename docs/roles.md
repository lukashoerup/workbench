# Roles — who builds, which model, when Astra reviews

Decided by Lukas 2026-09-19. This is the only place roles live; a swap is an edit here.

## Builder: Claude
- Default model **Opus**. **Fable 5.1** only when the task file's first line says
  `Model: fable` and gives the reason: architecture, a cross-cutting refactor, an
  ambiguous bug, anything where a wrong answer is expensive to detect.
- **Save mode.** A session whose seven-day rate-limit status reads `allowed_warning`
  runs on Opus whatever the task says, unless Lukas's dispatch message overrides it.
  Sessions cannot read the percentage, only that flag; the flag *is* the 60% rule.
  Lukas sees the exact bar in the app, and the word "spar" from him means the same.
- Scheduled work (routines) is always pinned to Opus.
- Deterministic checks first: tests, shellcheck, docs invariants. CI is the judge.

## Reviewer: Astra (ChatGPT), on included usage only
- Reviews follow the development flow, not a calendar: a milestone, a PR with real
  code ready to merge, a design or direction change, a data-handling change.
- Never on process documents, and never a Claude/Codex round about each other's reviews.
- Engaged the simplest way that works: a session, or Lukas, pastes the PR link into
  ChatGPT with Astra selected. The one-paste event-task experiment in
  `docs/astra-work-setup.md` (kept on the closed PR #2 branch) may be tried once when
  the OpenAI allowance has reset; if its read-only step says the trigger or the model
  is unavailable, that is the answer and nothing substitutes another reviewer.
- A missing review is written on the PR as "unreviewed". It never blocks a merge.

## Hard limits
- No API keys, overage, usage credits or credit purchases for either provider.
- A written rule is not a running job. Nothing here starts a scheduler or a bot.
