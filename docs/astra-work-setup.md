# Astra as milestone reviewer: one-time ChatGPT Work setup

Claude owns implementation and routine checks; Astra gives short milestone reviews only
(`docs/roles.md`). This is the one setup Lukas does himself, once, in ChatGPT Work with
GPT-6 Astra selected and the GitHub plugin that is already connected. Afterwards Claude is
the daily interface: it applies the `astra-review` label when a review is wanted, and the
task does the rest. Lukas does nothing per review.

Rules built into the prompts: verify before creating; one brief review per requested
revision; no polling; no paid fallback; no merge or deploy; if event triggers or Astra are
unsupported in this surface, say so rather than substituting ordinary Codex cloud review.

## Step 1: read-only check
Paste into a new Work chat with GPT-6 Astra selected.

```
Read-only check, change nothing. Using the GitHub plugin on lukashoerup/workbench:
1. Report the default branch and its head commit SHA.
2. List open pull requests with number, title, head SHA and labels.
3. Show the first 12 lines of docs/roles.md on the default branch.
Then answer, one line each, without trying workarounds:
- Which model served this reply, exactly as your settings name it?
- Can you read a pull request's diff?
- Can you post a pull request review, not just a comment, on this repository?
- Can you run the repository's tests, or only read files?
- Can a cloud task in this workspace be triggered by a GitHub event, specifically a
  label added to a pull request, or only by a schedule or a manual start?
If anything is unavailable, say "unavailable" and why. Do not modify the repository.
```

Record the five answers under Working notes in `tasks/2026-09-12-phone-first-pilot.md`.
If the model is not GPT-6 Astra, or a label trigger is unavailable, stop here: the gap is
the answer, and the Claude-side pilot continues without this task.

## Step 2: create the task
Only if step 1 showed Astra, review posting and a label trigger.

```
Create a cloud task named "Astra milestone review: workbench".
Model: GPT-6 Astra. If this task cannot run on GPT-6 Astra, stop and tell me; do not
pick another model.
Trigger: only when the label "astra-review" is added to a pull request in
lukashoerup/workbench, or when a review is explicitly requested from me on such a pull
request. No schedule. No polling.
On each trigger:
- Read the pull request, its current head SHA, and the comment that applied the label
  or requested the review.
- Review that exact head once, briefly: a verdict (proceed, changes needed, or
  unverified), at most three consequential findings with evidence and a suggested
  response, and one next action. Put the head SHA you reviewed in the first line.
- Post it as a GitHub pull request review on that pull request.
- Do not review the same head twice. Do not comment on CI status. Never merge, deploy,
  change repository settings, enable other automations, or use paid usage.
If the trigger, the model, or posting a review is unsupported here, tell me exactly which
part is unsupported and create nothing.
```

Record the task name, the trigger the UI actually offered and the model shown. Then tell
Claude in plain language that the reviewer task exists.

## What this does not do
- It does not enable Codex cloud automatic reviews; those use an auto-selected model and
  are not a substitute for Astra.
- It grants no new permission: it uses the GitHub plugin already connected to the
  workspace.
- It does not remove the `astra-review` label; Claude does that after reading the review
  at the named head.
