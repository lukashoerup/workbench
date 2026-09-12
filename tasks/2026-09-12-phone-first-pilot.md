# Task: phone-first pilot — Claude builds, one Astra review at acceptance

## Goal
Prove, from the Claude phone app with both Macs closed, that Claude can take a small
task to a PR, react to review feedback on that PR without Lukas relaying anything, and
that Lukas can retrieve the result from the phone. Astra reviews once, at the end, when
allowance permits. Nothing here needs Lenovo, a routine, an endpoint or a purchase.

## Allocation (decided 2026-09-12)
Claude does substantially more, Astra less, because OpenAI usage limits are hit
repeatedly. Recorded in `docs/roles.md`; that file is the only place roles live.

## Acceptance criteria
- [ ] Account-side prerequisites below recorded as done or blocked, with evidence
- [ ] From the Claude phone app: one small documented change → branch → PR, which the
      session labels `needs-review`
- [ ] A review comment on that PR (Lukas's own, or Codex once allowance allows) is picked
      up by the watching Claude session and answered with a push or a reply, no relay
- [ ] Lukas retrieves the outcome on the phone, from the session or the PR, without a
      copied message
- [ ] Served models, head revisions and timestamps recorded under Working notes
- [ ] One Astra review of the finished PR at its exact head, recorded under Review
      evidence; if Astra is unavailable, "pending" with an owner and a retry date
- [ ] Tests green; docs affected updated

## Account-side setup (Lukas, about a minute each; no agent does these)
1. **Claude GitHub App on `lukashoerup/workbench`.** Check at github.com/apps/claude →
   Configure. Evidence from 2026-09-12: subscribing a cloud session to PR #2 activity
   succeeded ("comments, CI status changes, reviews and other PR events will now be
   delivered"), so the event path is live for this repository from a cloud session.
   Whether that rides on the App or on the account's GitHub connection cannot be told
   apart from inside a session.
2. **Codex ↔ GitHub.** In Codex settings, connect GitHub and either switch on Automatic
   reviews or rely on `@codex review` from Lukas's linked account. Evidence of the gap:
   the "Codex review" on PR #3 was submitted under Lukas's own account, not by a Codex
   bot; no bot review exists in this repository. Do not touch this while the OpenAI
   allowance is exhausted.
3. **Daily routine run cap.** Read it at claude.ai/code/routines and write the number
   here. Evidence: no routines exist on the account as of 2026-09-12.
4. **Usage credits.** Off, verified by Lukas on 2026-09-12. Never enable.

## Labels: the pending state lives on the PR, not in a service
- `needs-review`: set by the building session when the PR is ready; removed by whoever
  reviews.
- `needs-claude`: set by a reviewer, human or bot, when a repair is expected; removed by
  the session that pushes the repair.
- `review-pending`: set when the required reviewer was unavailable; the retry date goes
  in a PR comment.
Labels are created on first use. No automation depends on their existence, so a rejected
run or a dropped event simply leaves the label where it was, visible from the phone.

## Scope
**May change:** this task, `docs/roles.md`, `tests/test_roles.py`, the pilot PR's one
documented change.
**Must NOT touch:** `bin/`, `setup/`, `.github/`, credentials, billing settings, Lenovo,
and the generator work owned by `tasks/2026-09-09-honest-health-reporting.md` on PR #3.

## What not to do during the pilot
No routines, API-trigger endpoints, webhook receivers, Lenovo repairs or repeated OpenAI
experiments. A dropped event or a rejected run is a label left on the PR, not a reason to
build a queue.

## Docs affected
`docs/roles.md` (new), the `CLAUDE.md` routing row. On the direction branch (PR #1):
one pointer from `docs/workbench-direction.md` and `docs/workflow-rollout.md` to
`docs/roles.md`; requested in the handoff, not edited here to avoid a parallel edit.

## Size check
One PR, one review round, one repair. Under a day of wall time; zero purchases.

## Review evidence
Reviewer: Astra. Revision: the PR #2 head named in the review-request comment.
Scope: the 2026-09-09 review, the 2026-09-12 addendum, `docs/roles.md`, this task.
Findings and resolution: (fill). If unavailable: pending; owner Lukas, retry after the
OpenAI allowance resets.

## Handoff for Astra: one review, at acceptance, at most three questions
1. Does `docs/roles.md` record the allocation you and Lukas intend, including "one
   review per acceptance point"? If not, which single line changes?
2. Is pending-state-as-label acceptable as the entire retry mechanism for the pilot,
   given that Claude rejects runs at quota and drops over-cap GitHub events?
3. Should the pilot's review comment come from Lukas, at zero OpenAI cost, or wait for
   Codex Automatic reviews after the allowance resets?

## Working notes (agent fills in)
- 2026-09-12: created by Claude Fable 5.1 on the PR #2 branch. The subscription probe
  above was the only account action taken; it is reversible. No pilot step has run.
