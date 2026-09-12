# Astra as milestone reviewer: one-time ChatGPT Work setup

Claude owns implementation and routine checks; Astra gives short milestone reviews only
(`docs/roles.md`). This is the one setup Lukas does himself, once, in ChatGPT Work with
GPT-6 Astra selected and the GitHub plugin that is already connected. Afterwards Claude is
the daily interface: when a review is wanted it applies the `astra-review` label and posts
one request comment naming the head; the task does the rest. Lukas does nothing per review.

Until PR #2 merges, `docs/roles.md` and this file live only on that PR's branch. The
prompts therefore name the ref explicitly, so repository access is not misjudged as broken.

Rules built into the prompts: verify before creating; one brief review per requested head;
dispatch by request comment, not by label alone; no polling; no paid fallback; no merge or
deploy; if the trigger, the model or review posting is unsupported, stop and say so rather
than substituting ordinary Codex cloud review.

## Step 1: read-only check
Paste into a new Work chat with GPT-6 Astra selected.

```
Read-only check, change nothing. Using the GitHub plugin on lukashoerup/workbench:
1. Report the default branch and its head commit SHA.
2. List open pull requests with number, title, head SHA and labels.
3. Read docs/roles.md at ref claude/codex-review-reliability-9wc44k, the head branch of
   pull request #2. That file is not on the default branch until the PR merges. Show its
   first 12 lines. If you can only read the default branch, say so; that is a plugin
   limitation, not broken access.
Then answer, one line each, without trying workarounds:
- Which model does this chat's visible model setting show? Report only what a setting
  actually displays; if none is exposed, answer "unknown". My asking for GPT-6 Astra is
  not evidence of the served model.
- Can you read a pull request's diff?
- Can you post a pull request review, not just a comment, on this repository?
- Can you run the repository's tests, or only read files?
- Can a cloud task here be triggered by a new comment on a pull request in this
  repository, filtered by the pull request's label? If only by a schedule or a manual
  start, say so.
If anything is unavailable, say "unavailable" and why. Do not modify the repository.
```

Record the answers under Working notes in `tasks/2026-09-12-phone-first-pilot.md`. Stop
here if the model is unknown or not GPT-6 Astra, if a review cannot be posted, or if a
comment trigger with a label filter is unavailable: the gap is the answer, and the
Claude-side pilot continues without this task.

## Step 2: create the task
Only if step 1 showed Astra, review posting and a comment trigger with a label filter.

```
Create a cloud task named "Astra milestone review: workbench".
Model: GPT-6 Astra. If this task cannot run on GPT-6 Astra, stop and tell me; do not
pick another model.
Trigger: a new comment on a pull request in lukashoerup/workbench, only when the pull
request carries the label "astra-review", the comment author is lukashoerup, and the
comment's first line is "astra-review-request" followed by a 40-character commit SHA.
No schedule. No polling. Ignore every other comment, including any line beginning with
"review-event received", and ignore your own earlier reviews.
On each matching request:
- Capture the pull request's current head SHA first. If it differs from the requested
  SHA, post one short comment saying the requested SHA is no longer the head, and stop.
- If you have already posted a review for this repository, pull request and head SHA,
  post one line pointing to that review, and stop.
- Review that head once, briefly: a verdict (proceed, changes needed, or unverified), at
  most three consequential findings with evidence and a suggested response, and one next
  action. Put "reviewed <sha>" in the first line.
- Before posting, re-read the head. If it has moved, still post the review, with "head
  has since moved to <new sha>; pending state unchanged" in the first line.
- Post it as a GitHub pull request review on that pull request. Do not add or remove
  labels. Do not comment on CI status.
- Never merge, deploy, change repository settings, enable other automations, or use paid
  usage. If a run fails before posting, retry once for the same request, then stop and
  leave the request unanswered.
If the trigger, the label filter, the model, or posting a review is unsupported here,
tell me exactly which part is unsupported and create nothing.
```

Record the task name, the trigger the UI actually offered and the model shown. Then tell
Claude in plain language that the reviewer task exists.

## Requests
Posted on the pull request by the building Claude session under Lukas's GitHub identity,
or by Lukas. The label `astra-review` must already be on the PR. Cost bound for this pilot:
one initial review and one repair follow-up; no further request without a new head and a
reason.

Initial request, once, after activation, with the PR's head at that moment:

```
astra-review-request <40-character head sha>
Scope: the files changed in this pull request. One review of this head. Pending stays
until it is reviewed.
```

Repair follow-up, once, after the scoped repair and tests are pushed:

```
astra-review-request <40-character repaired head sha>
Repair of: <the finding addressed>. Review this head only.
```

## What this does not do
- It does not enable Codex cloud automatic reviews; those use an auto-selected model and
  are not a substitute for Astra.
- It grants no new permission: it uses the GitHub plugin already connected to the
  workspace.
- It does not react to the label alone. The label is the visible pending state; the
  request comment is the dispatch, so a repaired head gets its own request.
- It does not remove the `astra-review` label; Claude does that after reading the review
  at the named head.
