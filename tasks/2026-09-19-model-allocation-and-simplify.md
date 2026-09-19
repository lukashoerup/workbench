# Task: put the work back in Claude, cut the review carousel, route models by cost

## Decision — Lukas, 2026-09-19 (chat, recorded here verbatim in substance)
- Most work runs in Claude. Astra (ChatGPT) is used **only** to review the more
  important things, occasionally, in review sessions that are spun up automatically.
- Inside Claude: **Opus for simpler code, Fable 5.1 for more complex code.**
- **When weekly Claude usage is above 60%, economise on Fable.** When the Fable
  limit is close, economise on Fable too — Opus takes everything it can.
- All of this should run automatically, not by Lukas choosing per session.
- Lukas's own read of the situation, which this investigation confirms: the setup
  had drifted onto a side track.

## What the investigation found (measured 2026-09-19, main at `6ab5193`)
| Fact | Evidence |
|---|---|
| The box has been dark for six weeks | `STATUS.md` on `main` was generated 07 Aug 05:05; Lukas confirmed lenovo powered off on 2026-09-12 (PR #2 comments). The page still says "Nothing. All clear." |
| `main` has not moved since 5 Sep | 87 tests green locally today. Nothing merged since. |
| Three PRs open, all stalled since 12 Sep | #1 (workflow + direction docs, 689 lines), #2 (reviews of reviews + Astra setup, 720 lines, docs only), #3 (honest health reporting, real code, reviewed and accepted 12 Sep, CI green, **mergeable, never merged**) |
| An August branch with finished work was never merged | `claude/naeste-trin-yjpv8y` (04 Aug): notify outbox, deterministic nightly triage, gardener, bootstrap close-out — 2,396 lines with tests. It moves three task files to `done/` that `main` still lists as open. |
| 12 Sep was a review carousel, not development | Four review rounds on PR #2 in one afternoon (Codex → Claude fix → Codex → Claude fix), every one reading ~1,400 lines of process docs. Zero product code changed. |
| Every "Codex review" ran through Lukas's own account and Mac | All reviews and comments on #1–#3 are authored by `lukashoerup`; the task file records the posting side as hand-carried. The thing Lukas did not want — being the messenger — was the mechanism. |
| The automatic Astra review has never run | `docs/astra-work-setup.md` (PR #2) is an untested ChatGPT Work event task. No Astra review has ever reached a PR by automation. OpenAI allowance was "near exhaustion" on 12 Sep — spent on reviewing policy documents. |
| Claude's weekly window is already in warning | This session's rate-limit record: type `seven_day_overage_included`, status `allowed_warning`, resets 2026-09-22 14:00 UTC. The percentage is not exposed to a session; the warning flag is. |
| The one earlier independent review said so | `docs/reviews/2026-09-09-…` (Claude, on PR #2): "the policy must give overview and occasional guidance, not ceremony"; recommended ~30 lines instead of 99 and warned that every substantial change would wait on a hand-carried review round. The disposition kept the 99 lines. |

Verdict: the *direction* (phone-first, Claude builds, occasional independent review)
is sound. The *execution* built a review bureaucracy before there was anything to
review, and then spent both subscriptions reviewing the bureaucracy.

## Proposed plan — smallest change that lands the value
1. **Merge PR #3.** Real defects fixed, reviewed, CI green. Nothing else needs to
   land first; `main` has no branch protection.
2. **Collapse PR #1 and PR #2 into one file of ≤30 lines**, `docs/roles.md`, holding:
   who builds, which model when, when Astra reviews, what "pending" means, and "a
   written rule is not a running job". Keep `docs/reviews/` as history under
   `docs/reviews/` (excluded from every session's required reading). Drop the
   99-line `docs/WORKBENCH.md`, its per-project copies and the generator copy step.
   Do not merge the direction doc's rewrites of `CLAUDE.md` / `SYSTEM.md` /
   `STACK.md` as they stand; they widen the interrupt rule the 2026-07-26 decision
   made concrete (finding A2 of the 09-09 review, never fixed).
3. **Model routing, written as a rule and measurable by a session:**
   - Task files carry `Model: opus | fable`. Default `opus`. `fable` only where the
     task file says why (architecture, cross-cutting refactor, an ambiguous bug,
     anything where a wrong answer is expensive to detect).
   - A session reads its own rate-limit status at start. `allowed_warning` on the
     seven-day window = **save mode**: run on Opus regardless of the task's model
     line unless Lukas overrides in the dispatch message. Until a session can read
     the actual percentage, the warning flag *is* the 60% rule; Lukas sees the exact
     bar in the app and one word ("spar") from him flips the default.
   - Scheduled work (routines) is pinned to Opus, always.
   - Reviews of documents never use Fable, and never use Astra.
4. **Astra cadence and mechanism.** At most one Astra review per week, only at a
   milestone: a PR with real code ready to merge, or a direction decision with
   money/data consequences. Never on docs-about-process. Mechanism, simplest first:
   (a) Codex Automatic reviews on GitHub if Lukas wants routine PR review at all
   (auto-selected model, included in Plus, zero relay);
   (b) for the milestone review, the ChatGPT Work event task from
   `docs/astra-work-setup.md` — one paste by Lukas, once, after the allowance
   resets; if step 1 of that file says the trigger or Astra is unavailable, stop
   there and fall back to (c);
   (c) Lukas opens ChatGPT, picks Astra, pastes the PR link. One minute, a few
   times a month. Not automatic, but honest and free of machinery.
5. **Lenovo: decide, then act.** It is off. Either someone turns it on and the
   August branch is rebased and merged (it is the box's own reliability work), or
   the box is parked in writing, the three Lenovo task files are moved to a parked
   state, and `STATUS.md` stops being the answer to "what is going on" until it is
   back. The current state — a six-week-old "all clear" — is the worst of both.
6. **Docs diet.** Every session currently loads CLAUDE.md (79/80 lines) + SYSTEM.md +
   STACK.md, and the branches add direction (150) + WORKBENCH (99) + rollout (71) +
   roles (44). Cut what a session must read to CLAUDE.md, roles.md and the task
   file; everything else on demand. This is where the Fable spend actually goes.

## Needs Lukas (decisions genuinely his)
- Merge PR #3 now? (Recommended: yes.)
- Close PR #1 and PR #2 in favour of the 30-line roles file? (Recommended: yes.)
- Lenovo: back on, or parked?
- Routine PR review by Codex's auto-selected model: wanted, or Astra-only by hand?

## Scope
**May change:** `docs/roles.md`, `CLAUDE.md` routing row, `tasks/`, `context/STACK.md`
(mark the 2026-09-08 workflow paragraph superseded, do not delete it).
**Must NOT touch:** `bin/`, `setup/`, `.github/`, billing, credentials, Lenovo, PR #3's
generator work.

## Docs affected
`context/STACK.md` (model routing decision, dated), `CLAUDE.md` (routing row to
`docs/roles.md`), `docs/claude-project-instructions.md` (roles sentence).

## Size check
One session for steps 2, 3 and 6 once Lukas has answered the four questions. Steps 1
and 5 are clicks and a power button.

## Working notes (agent fills in)
- 2026-09-19: created by the investigating Claude session on `claude/zen-knuth-z2xyd4`.
  Nothing merged, closed, enabled or purchased. 87 tests green on `main` and on this
  branch. The erhvervsklubben repository could not be attached from this session, so
  its CI and PR state were not checked.
