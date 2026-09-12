# Addendum — feasibility of the phone-first direction (2026-09-12)

Reviewer: Claude Fable 5.1 (`claude-fable-5-1`, configured and last-served per the session
record). Continues the 2026-09-09 review in this directory; that file is unchanged.
Reviewed: workbench PR 1 head `644d5335cced454c6aa6dc6ddd235e2aa975abb6`, in particular
`docs/workbench-direction.md`, and the instruction diffs since `6b21c8c`. One bounded pass;
nothing implemented, enabled, purchased or merged. Usage credits stay off.

## Assessment formed before reading Codex's rationale
GitHub is the only surface both vendors integrate with natively, so the queue should be a
PR plus labels, not a service. The two hardest claims to prove would be (a) that the OpenAI
review path runs the model Lukas calls Astra on included usage rather than a fixed default,
and (b) that anything returns into the chat where he asked, as opposed to being there the
next time he looks. At quota, work must fail visibly rather than fall through to another
biller. Reading the direction document afterwards: it agrees on all four points and is
honest about what is unverified. The findings below are where its preferred route hides a
decision or where documented behaviour contradicts a stated requirement.

## Evidence classes
Documented = read on the vendor's official page. Account-verified = observed on Lukas's
account from this session. Assumption = neither.

| Capability | Class | Evidence |
|---|---|---|
| Claude cloud sessions on Max, phone can start and monitor them, no separate compute charge | Documented + account-verified | Web doc: "no separate compute charge for the cloud VM"; rate limits shared with all Claude usage. This session and PR 3 are proof of the path. |
| Claude routines: schedule / API / GitHub triggers, model pinned per routine, Pro and Max | Documented; account has the surface, none exist | Routines doc. `list_triggers` returned an empty list; one Default environment. |
| Behaviour at Claude quota with usage credits off | Documented | "Without usage credits, additional runs are rejected until the window resets." GitHub webhook events over the hourly cap "are dropped". No replay is documented. |
| Claude auto-fix reacts to review comments and CI on a PR; can be switched on from the mobile app | Documented; app install on this repo unverified | Web doc, Auto-fix section. Requires the Claude GitHub App on the repository. |
| Proactive completion push to the phone | Documented in this account's tool surface, not exercised | Fresh-session routines accept `notifications: {push, email}`. Nothing is documented for ordinary sessions. |
| Codex reviews a PR on `@codex review` or via Automatic reviews | Documented; connection here unverified | The PR 3 "Codex review" was submitted by `lukashoerup`, not a Codex bot, so it was hand-carried. That shows no bot review exists yet, not that the integration is absent. Mention trigger needs the commenter's GitHub linked to a Codex account. |
| Codex cloud review model is Astra | **Contradicted by docs** | Models page: the default model for Codex cloud cannot be changed; what's-new: Codex cloud "selects its model automatically", review powered by GPT-5.6 Sol for eligible customers. |
| Astra on included usage | Documented, allowance-limited | Pricing: Plus includes Astra "in ChatGPT Work and Codex as it rolls out"; a model at its allowance "may be temporarily unavailable until the allowance resets". |
| Astra selectable non-interactively | Documented for a machine with saved ChatGPT login | `codex exec` reuses saved CLI auth; `--model` selects. The GitHub Action path needs an API key, which is not authorized. |
| ChatGPT Work event-triggered task picks Astra and posts a GitHub review on Plus | Assumption; UI availability observed | Scheduled-task doc says the selected model applies and GitHub events can trigger on "eligible plans". Codex's read-only observation on 2026-09-12: the signed-in Work UI shows GPT-6 Astra selectable and GitHub in the plugin picker. That is UI availability only; repository and test permissions, event-triggered model selection, automatic return and served model remain unverified. |
| Claude custom connectors from mobile | Documented, not needed for the pilot | Support article via search: connects from Anthropic's cloud; mobile can use already-configured connectors (beta). |
| ChatGPT developer-mode MCP on mobile | Documented as web-only | Optional entry point; not a pilot blocker. |

Billing seen from here: `rate_limit_info` shows a five-hour window, status allowed and
`isUsingOverage: false`. The credits toggle itself is not visible to a session; Lukas's
verification on 2026-09-12 is the record.

## Findings (three, consequential)

### F1 — unverified, then a decision: no documented surface yet gives a hosted, included, event-triggered, Astra-pinned reviewer
- Evidence: the table rows on Codex cloud. The direction document's preferred route names
  "an Astra review executor" without saying which surface can be both hosted, included in
  the subscription, mention- or event-triggered, and model-pinned. No documented surface is;
  the ChatGPT Work event-triggered route is untested, not ruled out.
- Consequence: "Fable builds, Astra reviews, cloud, no extra cost, no relay" is not
  established today, and not shown impossible either. Corrected 2026-09-12 after Codex's
  review of `c433fdc`: the earlier wording "cannot all hold" overstated the evidence.
- Options, all within existing subscriptions: (a) accept Codex cloud's auto-selected model
  for routine PR review and reserve Astra for idea and architecture reviews on a machine;
  (b) pin Astra with `codex exec --model` on Lenovo or a Mac, which makes that machine the
  reviewer, not a fallback, and depends on a saved login that expires; (c) test whether a
  ChatGPT Work GitHub-event task on Plus can select Astra and post a GitHub review.
- Suggested response: when the OpenAI allowance allows, one bounded test of (c) first,
  recording served model and whether a GitHub review is posted; until then run the Claude
  leg of the pilot with a human review comment. Do not ask Lukas to give up Astra on
  today's evidence.

### F2 — correction: at quota Claude rejects or drops; nothing queues
- Evidence: routines doc quoted above. The direction document asks for "visibly pending"
  work "within a bounded retry policy"; no retry exists to bound.
- Consequence: a PR can wait for a fix or a review with no signal to anyone. A dropped
  webhook is silent by construction.
- Fix: the pending state must be written on GitHub before dispatch by whatever asks for
  work (a label such as `needs-claude` or `needs-review`), so the PR itself shows it from
  the phone. Retry is then either Lukas's next prompt at zero cost, or a scheduled sweep
  routine that re-reads labels and costs one run per sweep against the daily cap. Pilot
  with labels only; add a sweep only if rejection is actually observed.

### F3 — correction of my B3, and a scope consequence for Lenovo
- I accept Codex's disposition: because `~/bin` symlinks into the checkout, a fast-forward
  activates new scripts before the installer runs, so a failed install leaves a mixed
  state, not the old revision. Any Lenovo activation must switch a `current` symlink only
  after install succeeds, or report partial activation.
- Consequence: if Lenovo returns only as an Astra executor (F1 option b), its job is one
  timer, one script that runs `codex exec` on labelled PRs and posts the review, and the
  existing notifier. That does not need the publisher, updater or watchdog repairs at all.
  Do not fix the old machinery on the assumption the box comes back as an ops server.

## Lenovo versus hosted execution
Hosting cost is separated from token billing. Both columns assume no API key and no credits.

| | Lenovo | Hosted (native vendor cloud) |
|---|---|---|
| Hosting cost | Electricity and upkeep; a human must power it on; Wi-Fi only; was dark a month unnoticed | None extra: Claude cloud VM has no separate charge; Codex cloud is included in the ChatGPT plan |
| Claude tokens | Max via the CLI with subscription login | Max via cloud sessions and routines; daily routine run cap |
| OpenAI tokens | ChatGPT allowance via `codex exec` with saved login | ChatGPT allowance via Codex cloud review |
| Model pinning | Both roles pinnable with CLI flags | Claude: per routine. OpenAI review: auto-selected |
| Trigger without relay | Needs a poller or a webhook receiver on the box | Claude GitHub App and Codex GitHub connection, once installed |
| Login expiry | Both CLIs expire; the 2026-09-12 dispatch failed on exactly this | Vendor-managed web auth |
| Return to phone | Telegram via the existing notifier | Session list in the app; routine push notifications |
| Blast radius | Root box with passwordless sudo and the Telegram secret | Isolated VMs; connectors routed through Anthropic |
| Verdict | Only documented home for a pinned Astra reviewer | Documented and partly account-verified for everything except a pinned Astra |

## Smallest falsifiable pilot
Both Macs closed, phone only, one PR, one review round, one repair, one push test. No
purchase, no new credential, no server.
0. Prerequisites, each a one-minute check: the Claude GitHub App is installed on
   `lukashoerup/workbench`; Lukas's GitHub is linked to his Codex account, or Automatic
   reviews is switched on in Codex settings; the daily routine run cap is read from the
   routines page and noted in the task file.
1. From the Claude phone app start a cloud session: make one trivial documented change
   (the `docs/reviews/` routing row is a candidate), open a PR, label it `needs-review`,
   post `@codex review`, then watch the PR with auto-fix. Falsifiers: Codex does not react
   to a mention posted through Claude under Lukas's identity (then rely on Automatic
   reviews); auto-fix does not wake on a bot review (then the return leg is unproven).
2. Record on the task file: served model of the review as far as the review states it,
   otherwise "auto-selected", plus revision, timestamps and whether any human touched it.
3. Claude's session addresses one finding and pushes; Codex reviews again or is asked to.
4. Proactive return: create one one-off routine (one-off runs do not count against the
   daily cap) with push notification on, doing a trivial check; note whether the phone
   receives a push. This proves the channel, separately from "visible on next prompt".
5. Quota: do not exhaust Max. Record the documented rejection behaviour and check that the
   `needs-review` or `needs-claude` label is still visible on the PR afterwards; that is
   the pending state. Anything more is a later experiment.
Pass means steps 1 to 4 completed with no message carried by Lukas. Step 2 is expected to
show a non-Astra model; that is the F1 decision, not a failure of the pilot.

## Does a custom dispatch service exist in this design?
No. The queue is PR state plus labels. Dispatch is the Claude GitHub App (auto-fix and
routine GitHub triggers) and the Codex GitHub connection (mention or Automatic reviews).
A custom piece appears only under F1 option (b): a label poller on the machine that runs
`codex exec`, which is a script, not a platform. Nothing here needs an API-trigger routine,
a webhook receiver or a public endpoint.

## Dispositions of the 2026-09-09 findings
- A1: agreed, no approval after 48 hours. Pending stays pending with an owner and a next
  retry recorded; Lukas may override explicitly; unrelated work continues.
- A3: copies stay until a cross-repository read is proven; generator regression test added
  to the plan. Fine.
- B1/B2: prerequisites, agreed; the GitHub observer is an interim signal.
- B3: corrected above in F3.

## Verdict
Direction document at `644d533`: proceed, with F1 recorded in the document as unverified
rather than impossible, a decision only after the one Work-task test, and F2 reworded so
"pending" means a label on GitHub with an owner and next action, not a retry the vendor
does not offer. Execution: hosted first, as Lukas prefers, with the reviewer model recorded
rather than assumed. Lenovo is not needed for the pilot.

Open product decisions, deliberately left visible: which F1 route to test first when the
allowance allows; whether an auto-selected review model would be acceptable for routine
PRs if Astra cannot be event-triggered; whether a review pending for a long time should
ever reach him by push rather than wait for his next prompt.

## Limitations
- The sandbox egress policy blocks `learn.chatgpt.com`, `developers.openai.com` and
  `support.claude.com`. Those claims rest on search snippets of the official pages, not
  full page reads. The two Claude Code documentation pages were read in full.
- Not verified: Claude GitHub App installation on the repository, Codex account linking,
  Plus eligibility for GitHub-event Work tasks, and the credits toggle itself. Codex reports
  the full scheduled-tasks page documents Work connected tools and GitHub-event tasks on
  eligible plans; from this sandbox it was reachable only as a search snippet.
- No pilot step was executed; every "falsifier" above is untested.
