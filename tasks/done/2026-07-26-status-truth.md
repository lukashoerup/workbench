# Task: stop STATUS.md publishing things that are not true

## Goal
Three defects make the status page misreport, and all three are republished to
GitHub every 30 minutes — so the phone view has been quietly wrong for days.
A page whose job is "measured, never remembered" must not ship falsehoods.

## Acceptance criteria
- [x] A permanently broken push re-alerts on a schedule instead of exactly once
      ever (`bin/publish-status.sh:62`, `-eq 3`)
- [x] Commit timestamps show when the commit actually landed, not the author
      date preserved across `--amend` (`bin/workbench-status.py:83-84`, `%ad`)
- [x] The footer stops pointing at `../workbench-context/`, merged away
      2026-07-24 (`bin/workbench-status.py:228`)
- [x] The `:19-20` comment stops describing a "dedicated job below" that has
      never existed
- [x] Tests green

## Scope
**May change:** `bin/publish-status.sh`, `bin/workbench-status.py`, `tests/`
**Must NOT touch:** `setup/`, the amend/collapse logic, the containment rule
that only `STATUS.md` is ever auto-committed

## Detail
1. **Alert once, ever.** `[ "$fails" -eq 3 ]` fires on exactly the third
   failure. If the push stays broken — which is precisely when it matters —
   Lukas gets one message and then silence, while STATUS.md freezes and still
   looks fine. Re-alert at `fails >= 3` when `(fails - 3) % 12 == 0`, mirroring
   the watchdog's `COOLDOWN=21600` (`bin/watchdog-check.sh:16`): first at 1.5 h,
   then every 6 h at the 30-minute cadence.
2. **Two-day-old dates.** `git log --pretty=%ad` is the *author* date;
   `bin/publish-status.sh:45` collapses status commits with `--amend`, which
   preserves it and moves only the committer date. `STATUS.md:19` therefore
   reads `24 Jul 13:32  Status: 26 Jul 13:23`. Use `%cd`.
3. **Dead repo reference.** `../workbench-context/` was merged into `context/`
   on 2026-07-24 (commit `6dc94be`). `tasks/done/2026-07-24-merge-context.md:11`
   claims all references were updated; this one was missed because it is a
   string inside the generator rather than a doc.

## Docs affected
None — these are code defects. The `context/` path in the footer is the fix.

## Size check
Three small edits plus regression tests.

## Working notes (agent fills in)
- Found during the 2026-07-26 audit. All three were invisible because the page
  reports on everything except itself.
- Re-alert cadence chosen to mirror the watchdog's 6h COOLDOWN rather than
  inventing a second schedule: alerts land at failure 3, 15, 27.
- `test_third_consecutive_push_failure_alerts` still passes unmodified — the
  first alert is still on the third failure.
- Tests 56 -> 58 green.
