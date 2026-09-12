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

## Setup, split by who can do it (corrected 2026-09-12 after Codex's review)
Agents do the read-only checks and the already-authorized reversible steps themselves.
Only permission-sensitive or account-linking actions wait for Lukas.

**Agent, read-only, done 2026-09-12:** subscribing a cloud session to PR #2 events
succeeded, and a Codex-authored review posted under Lukas's account reached the session
through that subscription at 17:01Z with no relay on the receiving side. No routines exist;
one Default cloud environment; the session's rate-limit record shows no overage in use.
A routine run cap is not a prerequisite: the pilot uses no routines.

**Agent, reversible, authorized within this pilot:** subscribe the building session to
its own PR; apply the labels below. No polling check-in and no routine, by Lukas's
instruction of 2026-09-12; the one check-in scheduled earlier that day was deleted.

**Lukas only:**
1. **Claude GitHub App on `lukashoerup/workbench`.** github.com/apps/claude → Configure;
   evidence is the repository listed under the App's access. The subscription success
   above shows the event path works; whether it rides on the App or on the account's
   GitHub connection cannot be told apart from inside a session.
2. **Codex ↔ GitHub.** In Codex settings, connect GitHub and either switch on Automatic
   reviews or rely on `@codex review` from Lukas's linked account. Evidence so far: no
   bot-authored review exists in this repository; the PR #3 review was hand-carried. That
   leaves the integration's status unverified, not absent. Not while the OpenAI allowance
   is exhausted.
3. **Usage credits.** Off, verified by Lukas on 2026-09-12. Never enable.

## Labels: visible pilot state on the PR, not an automatic retry
Each label names an owner and the next action in the PR comment that applies it, so a
missed event never quietly hands coordination back to Lukas.
- `astra-review` (renamed from `needs-review` on 2026-09-12 to match the trigger the Work
  task listens for). Owner: Astra through the Work task once `docs/astra-work-setup.md` is
  done, via Lukas until then. Next action: review the exact head named in the comment.
  Remove only after inspecting that head and the verdict; keep it while findings are
  unresolved or the head has moved since the review.
- `needs-claude`. Owner: the building session. Next action: the scoped repair plus tests.
  Remove only after both are complete and pushed.
- `review-pending`. Owner: Lukas. Next action and retry date in the comment. Stays until a
  review lands or Lukas explicitly overrides.
After a missed event (rejected run, dropped webhook): the label stays, and the next action
is Lukas's next prompt to the building session, which re-reads the PR. No polling check-in
exists by design. Labels are created on first use; nothing automated depends on them.

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

## Event path, configured 2026-09-12: the per-PR subscription
The building session is subscribed to PR #2's GitHub activity through the existing
per-PR watcher. No routine was created; none is needed. Evidence that it wakes an idle
session (all times UTC, from the GitHub API and the session's wake record):

| Step | Time |
|---|---|
| Codex review 5187283580 submitted at head `c433fdc`, under Lukas's account | 17:01:15 |
| Wake queued to the idle session | 17:01:17 |
| `review-event received` acknowledgment posted from the session | 17:03:07 |
| Corrections pushed as `37f4fc6`; consolidated handoff posted | 17:05:19 |

Posting side was hand-carried; receiving side was automatic; no OpenAI run was used.

Rules the session follows on every wake:
- Ignore events that echo its own comments (the ones ending in the Claude Code footer,
  IDs recorded below) and repeated deliveries of the same event.
- Ignore a review whose ID is in the handled list, or that names a head already handled,
  unless it is a new review with a new finding.
- Per new actionable review: acknowledge with `review-event received` and the head, apply
  at most one scoped repair, run the tests, push, update the labels. A review with no
  actionable finding gets the acknowledgment only; nothing is manufactured.
- Missing or unavailable review stays pending under its label; never approval.

Handled: review 5187283580 at `c433fdc` → `37f4fc6`. Own comments: 5647369119, 5647381593.

## Next native-cloud setup step (prepared, not executed)
1. Astra side, by Lukas, once: `docs/astra-work-setup.md`, step 1 (read-only check) then
   step 2 (create the label-triggered task) only if step 1 shows Astra, review posting and
   a label trigger. Record the answers under Working notes. Not while the OpenAI allowance
   is exhausted.
2. Claude side: ready. An external test is a pull request review (not a plain comment) on
   PR #2 at its current head with at least one concrete finding about this PR's files.

## Review evidence
Reviewer: Codex, scoped review at `c433fdc`, delivered through the subscription on
2026-09-12. Verdict: the Claude-heavy allocation accepted; CI green; three corrections
(evidence versus conclusions, roles and scope consistency, honest pending state).
Resolution: applied in the commit that carries this text; re-review pending at the new
head under `needs-review`. Independent review of the corrected head: pending, not approval.

## Handoff for Astra: one consolidated review at the corrected head, at most three items
1. Confirm the corrected F1 wording (unverified, not impossible) and the label rules above
   match the intent of the `c433fdc` review; name the single line to change if not.
2. On the PR #1 branch, route the active assignment sentences to `docs/roles.md` and mark
   the rest historical: the "Current assignment" bullet in `docs/workbench-direction.md`,
   the "Product direction — clarified 2026-09-12" paragraph in `context/STACK.md`, and the
   "Current desired roles" bullet in `docs/claude-project-instructions.md`. Not edited here
   to avoid a parallel change to that branch.
3. Agree or amend the two prompts in `docs/astra-work-setup.md` before the allowance
   resets, so the setup runs once, not repeatedly.

## Working notes (agent fills in)
- 2026-09-12: created by Claude Fable 5.1 on the PR #2 branch. The subscription probe
  above was the only account action taken; it is reversible. No pilot step has run.
- 2026-09-12, later: Codex review at `c433fdc` arrived through the subscription;
  acknowledged on the PR from the session; corrections applied in `37f4fc6`.
- 2026-09-12, evening: Lukas confirmed the allocation (Claude implements and runs routine
  checks; Astra reviews milestones only). Label renamed to `astra-review`; the polling
  check-in deleted; `docs/astra-work-setup.md` written; event path documented above and
  announced on the PR as ready for an external review-event test. PR #3 at `b231f26`
  passed Astra's targeted re-review per Lukas; nothing here touches it.
