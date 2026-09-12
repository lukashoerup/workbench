# Shared workflow adoption and integration

Agreed 2026-09-08: Lukas requested independent Codex review of Claude's ideas
and implementation, automatic standard workflow across his projects, and a
critical project partner that occasionally asks worthwhile questions. He
explicitly requested updating the GitHub project rules now.

## Policy adoption
Canonical policy: `docs/WORKBENCH.md`, version `2026-09-09.1`.
On 2026-09-09 Lukas chose questioning whether a quiet project is still worth
pursuing as the default, before suggesting another step.

| Project | Local instructions | Policy path |
|---|---|---|
| `lukashoerup/workbench` | `CLAUDE.md`; `AGENTS.md` symlink | `docs/WORKBENCH.md` (canonical) |
| `lukashoerup/erhvervsklubben` | `CLAUDE.md`; `AGENTS.md` symlink | `docs/WORKBENCH.md` (identical versioned copy; T092) |
| Future projects from `bin/new-project.sh` | Generated Claude/Codex instructions | Copy of the template's current canonical policy |

This is the initial project registry. Update it when onboarding a project.
For a policy revision, update registered copies and their versions together;
never silently replace a project's explicit goals or permission exceptions.
Automated update PRs and policy-drift checking are not installed yet.

Role record, added 2026-09-12 evening: `docs/roles.md` holds the builder/reviewer
assignment; `docs/astra-work-setup.md` holds Lukas's one-time reviewer setup, not yet run.
The GitHub review → Claude return leg was demonstrated twice on PR #2 through the per-PR
watcher, with no relay on the receiving side. The Astra side remains unconfigured.

## What has not been established
- Codex automatic GitHub review settings have not been inspected or enabled
  by this change. Existing reviews, if any, are not evidence of these settings.
- Automatic pre-build idea review and reciprocal Claude review of Codex work
  are not configured or verified by these instructions.
- Scheduled partner check-ins, delivery memory/snoozes, and a global weekly
  notification budget are not installed by this change.
- Required review-completion gates for the current revision are not installed.
- The paste-ready Claude Project instructions are updated in this repository;
  that does not update the separately stored claude.ai Project settings.

Claude Fable 5.1 reviewed Workbench `6b21c8c` and Erhvervsklubben `44981f9`;
see [PR #2](https://github.com/lukashoerup/workbench/pull/2) and Codex's response.
That review was conditional and does not cover later revisions. The dispatching
agent owns pending review: record the exact revision, access/quota blocker and
next retry in the task. Continue unrelated work; no automatic 48-hour approval.

Lukas clarified the phone-first, interchangeable-model goal on
2026-09-12. Read `docs/workbench-direction.md` before more infrastructure work.
Cloud within existing subscription allowances, without extra cost, is Lukas's
preferred route; Lenovo is the fallback and is currently powered off. Neither
has passed the proposed end-to-end mobile pilot. No added hosting, API or
overage spending is authorized; quota exhaustion must leave work pending.
Final clarification: one phone app is enough, preferably Claude. ChatGPT mobile
entry is optional; automatic handoff of work/results between agents remains key.

## Next implementation acceptance checks
1. Confirm native cloud access, exact Astra selection, return delivery and
   included-usage billing settings. Test quota exhaustion without paid fallback.
   Evaluate Lenovo only if cloud cannot meet the requirements without extra cost.
2. Enable and verify one Codex review of a Claude-authored PR without Lukas
   manually requesting it; verify relevant fixes receive a fresh review.
3. Connect dedicated idea/project review and a trusted current-revision
   completion gate. Missing results, rate limits and stale reviews stay pending.
4. Pilot check-ins on these two projects: one useful combined nonurgent
   message at most per week, silence while parked/snoozed, remembered answers.
5. Evaluate after two weeks: useful decisions, defects caught, scope avoided,
   false alarms and interruption cost. Simplify the workflow where appropriate.

Codex documents automatic GitHub reviews and local review guidance; these are
separate from installing written rules. Its built-in review focuses on serious
change defects, so the broader partner role requires dedicated review work.
[Official code review documentation](https://learn.chatgpt.com/docs/third-party/github).
