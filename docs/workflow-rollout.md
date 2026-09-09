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

The September policy changes were authored by Codex and have not received an
independent Claude review. Do not present them as independently approved.

## Next implementation acceptance checks
1. Confirm actual review access/settings and select a bounded execution
   environment and budget. Do not rely on Lenovo while its report is stale.
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
