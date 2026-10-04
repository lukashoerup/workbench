# Roles — who builds, which model, when Astra reviews

Decided by Lukas 2026-09-19, models revised 2026-10-04. Roles live only here.

## Builder: Claude
- **Opus builds everything**, foundation work included (Lukas, 2026-10-04).
- **Fable 5.1** only (a) on a problem Opus has failed 3 times, telling Lukas in chat,
  and (b) now and then as a read-only second-opinion review at a milestone or design
  change, findings to the PR or `docs/reviews/`.
- **Save mode.** A session whose seven-day rate-limit status reads `allowed_warning`
  runs Opus only, unless Lukas's dispatch message overrides it. Sessions see only
  that flag, which *is* the 60% rule; Lukas sees the bar, and "spar" means the same.
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
