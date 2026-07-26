# Task: make "Needs you" able to see an actual failure

## Goal
`collect_blockers()` checks three static setup conditions — SSH keys, tailnet
peers, telegram config — and nothing else. It cannot report a red test, an
unpushed commit, a dead watchdog or a broken notification channel, even though
the generator already measures all four and then throws the answer away.

So STATUS.md can print **"Nothing. All clear."** while the box is broken. It
says exactly that today. This is the single highest-value change for "tell me
only when I am needed", because every other alert path on this machine is
push-only: if the Telegram message is missed, nothing re-surfaces it.

## Acceptance criteria
- [x] `collect_blockers(facts)` is **pure** — no subprocess, no filesystem —
      so it is fully testable from a cloud session with no machine access
- [x] `collect_setup_blockers()` keeps the three existing probes unchanged
- [x] Operational blockers sort above setup ones (a red test outranks a
      missing tailnet peer)
- [x] Six new escalations, each proven by a test: failing tests, unpushed
      commits, dirty tree, watchdog reporting failures, watchdog gone silent,
      notification channel broken
- [x] `--quick` says tests were not measured rather than staying silent —
      silence reads as green
- [x] All clear still renders "Nothing. All clear."
- [x] Tests green

## Scope
**May change:** `bin/workbench-status.py`, `tests/test_status_generator.py`
**Must NOT touch:** `bin/publish-status.sh`, the collectors' own probe logic

## Why "notify broken" matters most
A dead notification channel hides every other failure on this box — the
watchdog's only escape hatch is Telegram. `bin/notify.py:90` logs `NOCHANNEL`
and returns `False` rather than raising, deliberately, so a dead channel is
silent by design. Nothing surfaces it today. STATUS.md is the one place that
can, because Lukas reads it by pulling rather than being pushed to.

## Detail
`bin/workbench-status.py:139-152` takes no arguments, so it cannot see
anything. Split it:
- `collect_setup_blockers()` — the existing three probes, untouched.
- `collect_blockers(facts: dict)` — pure, fed by the collectors.

`build()` (`:156`) gathers facts first, then renders. Log formats to parse:
`bin/watchdog-check.sh:20` writes `<iso>\t<message>` and ends each run with
`run complete: N failing`; `bin/notify.py:59-70` writes
`<iso>\t<SENT|NOCHANNEL|FAILED(...)>\t<message>`.

This file is also the thinnest-tested in the repo — 3 tests, all on
`collect_tests`/`REPOS`, with `collect_blockers`, `collect_git`,
`collect_timers`, `collect_heartbeats`, `collect_tasks` and `build()` entirely
uncovered.

## Docs affected
None — behaviour of an existing page, no doc asserts the blocker list contents.

## Size check
One refactor plus a test per escalation.

## Working notes (agent fills in)
- Split confirmed pure by a test that fails the run if `collect_blockers`
  touches `run()`. That is what lets the section Lukas actually reads be
  developed and verified from a cloud session with no access to the box.
- `build()` now measures once into a facts dict and renders from it, so the
  blocker list cannot disagree with the sections below it.
- Verified end to end: a repo with red tests, dirty tree, unpushed commits, a
  silent watchdog reporting failures and a dead notify channel produces six
  operational blockers above the setup ones.
- Tests 58 -> 69 green.
