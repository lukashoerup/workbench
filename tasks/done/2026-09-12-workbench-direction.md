# Record the actual Workbench product goal

## Decision
Lukas's final 2026-09-12 clarification: one phone app is enough, preferably
Claude. It should dispatch Astra and retrieve results without
two open desktop windows or copied messages. Fable 5.1 builds; Astra reviews;
the assignment must remain changeable with subscriptions. Cloud without extra
cost is preferred; investigate native subscription-backed jobs first and use
Lenovo (currently powered off) as fallback. No OS change was chosen. Quota
exhaustion leaves work pending; no added server/API/overage spending is authorized.

## Changes
Added `docs/workbench-direction.md`: goals, candid assessment, official-source
capability comparison, unverified mobile/model/return paths, and a bounded
pilot. Updated the entry-point description and review rollout record. Real
reporting defects remain tracked; unmerged server work is preserved for scope
review. No new service, permission, scheduler, merge or deployment was enabled.

## Validation and independent review
Documentation invariants: 5 passed. Staged whitespace check: passed. These
checks run before commit. No runtime code changed in this follow-up.
Claude's previous review covered earlier revisions only. Independent review
of this direction is pending, owned by the dispatching Codex task. The direct
cloud follow-up failed because Claude CLI sign-in expired; bounded follow-up
text is prepared. Retry after normal login is restored. Do not call it reviewed.
