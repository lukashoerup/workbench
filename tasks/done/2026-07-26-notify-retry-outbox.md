# Task: notify.py must survive a Wi-Fi blip

## Goal
`bin/notify.py` has no retry and no outbox: a message lost to a dropped Wi-Fi
link is gone, recorded only as a log line. The box is Wi-Fi only
(`context/LEARNINGS.md:20-24`), so this is routine, not exotic. It matters more
once the nightly jobs land — a 03:15 brief lost to a blip is a brief nobody
ever sees.

## Acceptance criteria
- [x] Transient failures (network, timeout, 5xx, 429) retry 3× with 2s/5s backoff
- [x] Undelivered transient messages queue to
      `~/.local/state/workbench/outbox.jsonl`, mode 600, capped at 200 entries
      / 64 KB, drop-oldest
- [x] The outbox drains at the top of every `notify()` call, oldest first, and
      via `notify.py --flush` called from the end of `bin/watchdog-check.sh`
      (so it drains every 15 min even with no traffic)
- [x] `NOCHANNEL` and non-429 4xx never queue — they are permanent
- [x] The bot token never appears in the outbox file
- [x] All 20 existing notify tests and all 21 watchdog tests pass **unmodified**
- [x] Tests green — 117 passing (was 87), shellcheck clean

## Scope
**May change:** `bin/notify.py`, `bin/watchdog-check.sh` (flush call only),
`tests/test_notify.py`, `context/PATTERNS.md`
**Must NOT touch:** the return-code contract below, the stdlib-only rule

## The trap this task exists inside
**Queuing is not delivery.** `notify()` must still return `False` when *this*
message was not delivered *now*, even if it was safely queued.
`bin/watchdog-check.sh:70-79` reads the return code to decide whether to start
the 6-hour alert cooldown, and `tests/test_watchdog.py:275-290`
(`test_undelivered_alert_does_not_start_the_cooldown`) locks that in.

If a queued message reports success, a Wi-Fi drop during an incident starts the
cooldown and buries that incident until morning — reintroducing precisely the
bug the comment at `watchdog-check.sh:74-76` was written to prevent. The fix
for lost messages must not become a new way to lose them.

## Docs affected
`context/PATTERNS.md` — the Telegram recipe should mention the outbox.

## Size check
One module change plus tests for each failure class.

## Working notes (agent fills in)
Done 2026-08-04. 30 new tests; the 41 pre-existing notify/watchdog tests were
not touched.

**The trap held.** `test_queued_message_still_reports_failure` locks in that a
queued message returns `False`, alongside the existing
`test_undelivered_alert_does_not_start_the_cooldown` on the watchdog side. Both
ends of that contract are now covered.

**The watchdog flush had to be guarded, and that turned out to be the better
design.** `tests/test_watchdog.py`'s notify stub records *every* invocation
including argv, so an unconditional `"$NOTIFY" --flush` appends `--flush` to the
recorded messages and breaks eight tests asserting exact alert counts — the
"unmodified" criterion catches it immediately. Guarding on `[ -s "$OUTBOX" ]`
keeps those tests honest *and* avoids ~96 pointless interpreter starts a day on
a CPU-only box. Placed after the checks rather than before, because `check_net`
has just woken the Wi-Fi at that point.

**Drain uses single attempts, not the retry ladder.** Retrying each queued
message would mean up to 7 s of sleeping per entry before the caller's own
message is even attempted. The drain instead stops at the first transient
failure, which also preserves ordering.

**A permanently-undeliverable entry is dropped during the drain**, otherwise one
poisoned message blocks everything queued behind it forever.

Suite time went 10 s → 33 s. Almost all of it is real backoff sleeping in the
two pre-existing network-failure tests, which cannot patch `RETRY_BACKOFF`
because they must stay unmodified. New tests use the `no_backoff` fixture.
