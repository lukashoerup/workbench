# Task: notify.py must survive a Wi-Fi blip

## Goal
`bin/notify.py` has no retry and no outbox: a message lost to a dropped Wi-Fi
link is gone, recorded only as a log line. The box is Wi-Fi only
(`context/LEARNINGS.md:20-24`), so this is routine, not exotic. It matters more
once the nightly jobs land — a 03:15 brief lost to a blip is a brief nobody
ever sees.

## Acceptance criteria
- [ ] Transient failures (network, timeout, 5xx, 429) retry 3× with 2s/5s backoff
- [ ] Undelivered transient messages queue to
      `~/.local/state/workbench/outbox.jsonl`, mode 600, capped at 200 entries
      / 64 KB, drop-oldest
- [ ] The outbox drains at the top of every `notify()` call, oldest first, and
      via `notify.py --flush` called from the end of `bin/watchdog-check.sh`
      (so it drains every 15 min even with no traffic)
- [ ] `NOCHANNEL` and non-429 4xx never queue — they are permanent
- [ ] The bot token never appears in the outbox file
- [ ] All 20 existing notify tests and all 21 watchdog tests pass **unmodified**
- [ ] Tests green

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
