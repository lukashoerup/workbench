# Task: put the work back in Claude, pause Lenovo, cut the review carousel

Model: opus. Everything here is docs, task hygiene and GitHub clicks; nothing needs Fable.
Do not re-investigate: the findings are below and were measured on 2026-09-19.

## Decisions — Lukas, 2026-09-19 (chat; recorded here so other sessions read them)
1. **Lenovo is unnecessary for now. That track is paused.** Nothing is built for or
   repaired on the box until Lukas un-pauses it.
2. Most work runs in Claude. **Opus for simpler code, Fable 5.1 for complex code.**
3. **Save on Fable when the weekly window is above 60% or near its limit.** Opus then
   takes everything it can.
4. Astra (ChatGPT) reviews **only the important things**: milestones, design changes,
   whatever the development flow calls for. No weekly cap. No review rounds on
   documents about process.
5. All of it should be automatic, not chosen per session by Lukas.

## What was found (so nobody has to look again)
- `STATUS.md` on `main` is from 07 Aug; the box was confirmed off on 12 Sep. The page
  still says "Nothing. All clear."
- `main` (`6ab5193`) untouched since 5 Sep, 87 tests green. PR #1, #2, #3 open and
  stalled since 12 Sep. #3 is real code, reviewed and accepted, CI green, never merged.
  #1 and #2 are 1,400 lines of process docs, produced by four review rounds in one
  afternoon between Codex and Claude. That afternoon exhausted both subscriptions.
- Every "Codex review" on those PRs was posted from Lukas's own account via his Mac. The
  automated Astra review (`docs/astra-work-setup.md` on PR #2) has never run once.
- Branch `claude/naeste-trin-yjpv8y` (04 Aug) holds finished, tested Lenovo work
  (notify outbox, deterministic triage, gardener, bootstrap close-out) never merged.
- A session can see its own weekly rate-limit state (`rateLimitType`
  `seven_day_overage_included`, `status` `allowed` / `allowed_warning`) but not the
  percentage. On 2026-09-19 the status was already `allowed_warning`.

## Plan — one branch from `main`, one PR, merge when CI is green
Work on `task/2026-09-19-model-allocation-and-simplify`. Steps 1 and 7 are GitHub
actions, the rest are edits. Do them in this order.

### 1. Merge PR #3 into `main`
Real defects fixed, reviewed, CI green at `b231f26`. Merge it first so this branch
starts from it. Then move `tasks/2026-09-09-honest-health-reporting.md` to
`tasks/done/` with one line: generator half done; the publisher half is parked with
Lenovo (decision 1).

### 2. Write `docs/roles.md` — at most 30 lines, the only place roles live
Content, nothing more:
- Builder: Claude. Default model **Opus**. **Fable** only when the task file says
  `Model: fable` and gives the reason (architecture, cross-cutting refactor, an
  ambiguous bug, anything where a wrong answer is expensive to detect).
- **Save mode:** a session that sees `allowed_warning` on its seven-day window runs on
  Opus regardless of the task's model line, unless Lukas's dispatch message says
  otherwise. Until a session can read the percentage, the warning flag *is* the 60%
  rule. Lukas sees the exact bar in the app; the word "spar" from him means the same.
- Scheduled work (routines) is always pinned to Opus.
- Reviewer: Astra, when the flow calls for it: a milestone, a PR with real code ready
  to merge, a design or direction change, a decision with money or data consequences. Never on process docs,
  never on Fable's or Opus's reviews of each other.
- How Astra is engaged, simplest first: Lukas opens ChatGPT, picks Astra, pastes the PR
  link. The one-paste automation test in `docs/astra-work-setup.md` (kept on the closed
  PR #2 branch) may be tried once when the OpenAI allowance has reset; if its step 1
  says the trigger or Astra is unavailable, stop there for good.
- Missing review is "unreviewed", written on the PR. It never blocks a merge Lukas wants.
- A written rule is not a running job. Nothing here starts a scheduler.

### 3. Task template and dispatch
- `bin/new-project.sh`'s task template and this repo's task files gain a first line
  `Model: opus | fable` with the reason when `fable`. Default `opus`.
- `docs/claude-project-instructions.md`: replace the SYSTEM.md-first paragraph with:
  read `docs/roles.md`; dispatch cloud sessions with the model the task file names;
  save mode as above; Astra only as roles.md says. Keep the plain-language rules.
- `CLAUDE.md`: add the routing row "Who builds, which model, when Astra reviews →
  `docs/roles.md`". Required reading for any session is CLAUDE.md, roles.md and the
  task file; everything else on demand. Stay under 80 lines.

### 4. Pause Lenovo in writing
- `STATUS.md`: hand-edit a banner as the first lines: "PAUSED 2026-09-19 — the box is
  off by decision; this page is frozen at 07 Aug and is not current." The publisher is
  off, so nothing will overwrite it.
- `CLAUDE.md` "Read this first" section: the box is paused; STATUS.md is frozen; "what
  is going on" is answered from open PRs and task files until it is un-paused.
- `SYSTEM.md` lenovo row: paused 2026-09-19, everything on it is dormant.
- `context/STACK.md` scheduled-jobs table: mark paused. Add one dated line under the
  autonomy model: Lenovo paused 2026-09-19; the finished August work lives on branch
  `claude/naeste-trin-yjpv8y`, to be rebased when the box returns. Mark the
  2026-09-08 "independent review and project partner" paragraph superseded by
  `docs/roles.md`; do not delete it.
- Move to `tasks/parked/` (new directory; add it to `EXCLUDED_PREFIXES` in
  `tests/test_docs_invariants.py` next to `tasks/done/`): `2026-07-26-bootstrap-lenovo.md`,
  `2026-07-26-hooks-and-work-block.md`, `2026-07-26-local-model-jobs.md`,
  `2026-07-26-notify-retry-outbox.md`. One line at the top of each: parked 2026-09-19,
  finished work on the August branch where that applies.

### 5. Keep the history, drop the ceremony
Copy verbatim from branch `claude/codex-review-reliability-9wc44k` into `docs/reviews/`:
`2026-09-09-codex-policy-and-reliability-plan.md` and
`2026-09-12-direction-feasibility-addendum.md`. Nothing else from PR #1 or #2 is
merged: not `docs/WORKBENCH.md`, not the per-project copy step in `new-project.sh`, not
the rewrites of CLAUDE.md, SYSTEM.md and STACK.md, not the direction and rollout docs.

### 6. Tests
Run the full suite: `uv run pytest tests/ -o addopts=""`. The docs invariants cover
line caps and dead references. Add one small test: `docs/roles.md` exists, is ≤30
lines, and names both `opus` and `fable`.

### 7. Close PR #1 and PR #2
After this branch's PR is merged: close both with one comment each: superseded by
`docs/roles.md` per Lukas's 2026-09-19 decision; branches kept for history. Do not
delete the branches. Move this file to `tasks/done/`.

## Scope
**May change:** `docs/roles.md`, `docs/reviews/`, `docs/claude-project-instructions.md`,
`CLAUDE.md`, `SYSTEM.md`, `STATUS.md` (banner only), `context/STACK.md`, `tasks/`,
`bin/new-project.sh` (template line only), `tests/test_docs_invariants.py`
(exclusion list), one new test file.
**Must NOT touch:** anything else in `bin/`, `setup/`, `.github/`, billing, credentials,
the August branch, Lenovo. No new dependencies. No routine, no scheduler, no Astra
machinery.

## Docs affected
Listed per step above. Everything a session must read afterwards: CLAUDE.md,
docs/roles.md, the task file.

## Size check
One Opus session. If it runs long, split after step 4 and open the PR then.

## Working notes (agent fills in)
- 2026-09-19: written by the investigating session on `claude/zen-knuth-z2xyd4` after
  Lukas paused Lenovo.
- 2026-09-19, later: Lukas: "you do it, I do nothing; Astra needs no weekly cap, it
  follows milestones and design changes." Executed by the same session on its own
  branch (the designated one), not a `task/` branch. PR #3 merged at `cbde9c1`.
  Steps 2–6 done in this commit; step 7 (close #1 and #2) after this PR merges.
