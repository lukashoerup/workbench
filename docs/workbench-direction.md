# Workbench: product direction and feasibility

Updated 2026-09-12. User requirements are recorded below; execution choices
remain proposals. This document does not activate a service or grant access.

## What Lukas actually wants

Workbench should help Lukas develop, operate and reconsider several projects
with little coordination work. Success means a useful result or decision from
one phone conversation, not more scripts, agent activity or documentation.

- One phone app is sufficient; Lukas prefers Claude. From there, request work,
  engage Astra, retrieve its review and let Claude continue with any repairs.
  ChatGPT mobile entry is optional. Agents still need to pass work/results
  between providers without Lukas acting as messenger.
- No requirement to keep two desktop windows open or carry messages between
  agents. Work should run elsewhere while Lukas's Mac is closed.
- Current assignment: Claude Fable 5.1 builds using Claude Max; GPT-6 Astra
  reviews ideas, architecture, code and the way the project is being pursued.
- Provider/model assignments must be changeable when subscriptions change.
  Store the role assignment separately from enduring project instructions.
- Keep a current overview, decisions and useful cross-project lessons. Offer
  concrete next steps when helpful. After inactivity, first consider whether
  the project is still worth pursuing. Enjoyment and learning count as value.
- Compare BOTH Lenovo and hosted execution. Lukas confirmed Lenovo is powered
  off. It runs Ubuntu; no decision to reinstall or replace it has been made.

The final mobile clarification supersedes the earlier requirement for BOTH
phone apps. The home server is an execution option, not the product's centre.
Existing operational boundaries
still apply. Deployment and production access need their agreed authorization.

## Candid assessment

The current repository mostly implements server setup, status publishing and
notifications. The proposed shared workflow adds useful review rules, but it
does not yet provide automatic handoff between providers or a phone-accessible
project partner. Improving the old machinery alone will not deliver that.

GitHub remains a useful portable record of code and decisions. Keep a short
current goal, active task, reviewed revision and next decision per project.
Pass that context with each task; do not assume either provider can read the
other's chat memory. Save a lesson only when evidence changes a reusable
practice, with its scope and source. Do not accumulate every agent's opinion
or turn old lessons into permanent rules without checking their relevance.

Use direct deployment/uptime signals for operations. An LLM should interpret
an incident or decision, not repeatedly spend subscription usage to establish
whether an HTTP endpoint responds. Distinguish project value from code health.

## Documented capability versus verified access

Checked against official documentation on 2026-09-12:

| Capability | Evidence and limit |
|---|---|
| Claude can work with all personal machines off | [Cloud sessions](https://code.claude.com/docs/en/claude-code-on-the-web) persist and are accessible from mobile. Our two Fable tasks already produced PRs. |
| Claude can run scheduled/event work on Max | [Routines](https://code.claude.com/docs/en/routines) support schedule/API/GitHub triggers and consume subscription allowance, with daily caps. Not enabled or account-tested here. |
| Claude can react to PR feedback | Cloud sessions support per-PR Auto-fix with the Claude GitHub App. The toggle and a complete review/fix cycle have not been verified on these PRs. |
| Codex can run without an open window, with a chosen model | [Non-interactive mode](https://learn.chatgpt.com/docs/non-interactive-mode), [model selection](https://learn.chatgpt.com/docs/models), and [headless account sign-in](https://learn.chatgpt.com/docs/auth) are documented. Astra access must be verified on the actual executor. |
| Native Codex GitHub review can remove manual dispatch | [GitHub review](https://learn.chatgpt.com/docs/third-party/github) supports automatic reviews. It is not proof of an Astra run; the Codex cloud default model is not freely selectable. |
| Another hosted OpenAI path may be smaller | [ChatGPT Work and scheduled/event tasks](https://learn.chatgpt.com/docs/automations) can use connected tools on eligible accounts. Test Astra, repository/test access and return delivery in that surface separately from Codex cloud. |
| Claude can call a custom connector from mobile | [Remote connectors](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp) connect from Anthropic's cloud; the server must be internet-reachable and authenticated. A private Tailscale address alone does not satisfy this. |
| Optional ChatGPT mobile entry | **Unverified, not a pilot blocker.** [Developer-mode MCP](https://developers.openai.com/api/docs/guides/developer-mode) documents web read/write tools, not native mobile support. Verify that separately if adding this entry point later. |

Subscription allowance is not general API credit. A paid API route must be
identified explicitly with its own budget; never silently switch billing when
a subscription hits a limit. CLI account authentication can expire. This
actually blocked our direct Claude cloud follow-up on 2026-09-12, after the
installed CLI was updated to 2.1.269. The feedback exists on GitHub; no cloud
follow-up was successfully dispatched by that attempt.

## Two execution options to investigate

| | Lenovo | Hosted execution |
|---|---|---|
| What runs there | A small task executor using supported provider clients; heavy model inference remains with the providers | Prefer vendor cloud jobs; add a small hosted executor only for missing handoff/model-control capabilities |
| Existing allowances | Prefer supported Claude/ChatGPT account sign-in; confirm both selected models | Claude cloud can use Max. OpenAI hosted Work eligibility or hosted CLI account sign-in must be verified; APIs bill separately |
| Availability | Requires power, internet, restart recovery and remote access | Removes the home power dependency; vendor limits, hosting failures and authentication still matter |
| Operating cost | Electricity and maintenance; owning it does not make upkeep free | Native jobs may fit existing allowances; an extra executor has hosting costs and still needs maintenance |
| Main uncertainty | Can it recover and deliver results without Lukas tending it? | Can the required models, Claude mobile entry and return delivery work without a custom platform? |

Ubuntu is not itself a reason to start over: a headless executor fits this
design. Native desktop remote-control support is a separate issue: OpenAI's
[Remote guide](https://learn.chatgpt.com/docs/remote-connections) currently
documents macOS/Windows hosts, even though a Linux desktop preview exists.
Choose the execution path first, then decide whether any OS change helps.
No host purchase, installation on Lenovo, exposed endpoint or new paid API
has been authorized or performed by this document.

## Smallest useful pilot

Preferred first route: Claude Code in the phone app → a scoped GitHub task/PR
→ an Astra review executor → a GitHub review → Claude's PR Auto-fix → result
in Claude. Use a hosted OpenAI task if the account exposes the required model
and tools; otherwise compare a small supported CLI executor on Lenovo versus
a hosted worker. This route may avoid a custom public dispatch server entirely.
Use a short proposal artifact for material idea reviews; small fixes do not
need an extra proposal stage. None of this chain is yet verified end to end.

Use one bounded Workbench task. Prefer existing GitHub task/PR records over
building a second task database or new dashboard. Add only the dispatch
connection missing from the providers' supported capabilities.

1. From Claude on the phone, request a small change. Fable receives the
   original goal and constraints, produces a branch/PR and test evidence.
2. Astra reviews that exact revision and, when relevant, the premise. A real
   finding returns to Fable; one targeted repair is reviewed again.
3. The originating interface can retrieve the final result without copied
   messages. Separately prove proactive completion notification; do not count
   a result available on the next prompt as a delivered notification.
4. From the same Claude phone conversation, ask it to engage Astra for an
   idea review and use the returned judgment to revise the proposed next step.
5. Close the Mac apps. Verify work continues; interrupt the executor and
   exhaust/mock quota to check honest pending state and bounded resumption.

Record the actual served model, artifact revision, job ID, result and next
action. Treat the same revision/event idempotently, limit repair rounds, and
queue unavailable work visibly. No recursive model-to-model task explosion.
A worker crash or a missing review is not approval. Lukas may explicitly
override a review requirement; elapsed time alone does not do that for him.

Only after this loop works should we automate portfolio reflection: a single
combined nonurgent prompt at most weekly, respectful of parked projects,
snoozes and answered questions. A central record of delivered prompts is
needed across both providers. Measure useful decisions, avoided rework and
Lukas's coordination effort; simplify if the process consumes more attention.

## Existing repair work

PR #3 fixes real reporting defects but has [three Codex review findings](https://github.com/lukashoerup/workbench/pull/3#pullrequestreview-5185752633).
The publisher/updater/watchdog repair drafts remain local and unmerged. Keep
their regression evidence, but reassess their scope after the pilot chooses
where work runs. [Claude's review and Codex's dispositions](https://github.com/lukashoerup/workbench/pull/2#issuecomment-5644506504)
record the simplification discussion. Do not expand the legacy server plan
merely because implementation has already begun.
