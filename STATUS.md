# Workbench status

_Generated Friday 24 July 2026, 11:26 CEST on `lenovo`._
_Regenerated automatically every 30 minutes. Everything below is measured, not remembered._

## Needs you

Nothing. All clear.

## Repositories

### `workbench`
Branch `main` — clean.

**Tests: 53 passing.** ✅

Recent commits:
```
23 Jul 21:18  Status: 24 Jul 10:55
23 Jul 21:03  Mark Phase 1 SSH hardening done — key-only auth verified
22 Jul 22:17  Status: 23 Jul 20:47
22 Jul 22:17  Add repo index and watch the status timer itself
22 Jul 22:16  Status: 22 Jul 22:16
22 Jul 22:16  Collapse consecutive status commits instead of one per run
22 Jul 22:15  Status: 22 Jul 22:15
22 Jul 22:15  Status: 22 Jul 22:15
```
### `workbench-context`
Branch `main` — clean.

_No test suite in this repo._

Recent commits:
```
22 Jul 22:00  Benchmark local models: 9B wins, reversing spec §3
22 Jul 19:24  Record interface decision: GitHub is the single source of truth
22 Jul 19:10  Record Telegram notifications verified and connector boundary
22 Jul 18:39  Add cross-project context: STACK, PATTERNS, LEARNINGS
```

## Scheduled jobs

```
NEXT                             LEFT LAST                            PASSED UNIT                           ACTIVATES
Fri 2026-07-24 11:30:08 CEST 3min 51s Fri 2026-07-24 11:14:14 CEST 12min ago workbench-watchdog.timer       workbench-watchdog.service
Fri 2026-07-24 19:44:14 CEST       8h Thu 2026-07-23 19:44:14 CEST   15h ago launchpadlib-cache-clean.timer launchpadlib-cache-clean.service
-                                   - Fri 2026-07-24 11:26:14 CEST    2s ago workbench-status.timer         workbench-status.service

3 timers listed.
```

_No job heartbeats yet — no scrapers are running._

## Machine

- Disk: 61G free of 98G (36% used)
- RAM: 12Gi available of 15Gi
- Uptime: up 1 day, 15 hours, 48 minutes

Local models:
```
NAME          ID              SIZE      MODIFIED     
qwen3.5:9b    6488c96fa5fa    6.6 GB    38 hours ago    
qwen3:4b      359d7dd4bcda    2.5 GB    38 hours ago

Currently loaded:
NAME    ID    SIZE    PROCESSOR    CONTEXT    UNTIL
```

## Tasks

Open:
_none_

## Recent activity

Watchdog:
```
2026-07-24T09:54:16+02:00	run complete: 0 failing
2026-07-24T10:10:16+02:00	run complete: 0 failing
2026-07-24T10:26:16+02:00	run complete: 0 failing
2026-07-24T10:42:16+02:00	run complete: 0 failing
2026-07-24T10:58:16+02:00	run complete: 0 failing
2026-07-24T11:14:16+02:00	run complete: 0 failing
```

Notifications sent:
```
2026-07-22T18:31:07+00:00	NOCHANNEL	routine report check
2026-07-22T18:31:10+00:00	NOCHANNEL	⚠️ Watchdog on lenovo: selftest is stale — last run 180 min ago (limit 120 min)
2026-07-22T19:09:20+00:00	SENT	🔧 Workbench notifications are live. This is where alerts will land.
2026-07-22T19:09:36+00:00	SENT	🧪 Workbench watchdog test alert from lenovo at 2026-07-22T19:09:36+00:00
2026-07-22T19:09:36+00:00	SENT	Silent-mode check — this one should not buzz.
2026-07-22T21:56:50+02:00	SENT	🌙 Overnight summary — nothing needs you tonight.\n\nWrote the first test suite: 43 tests, all green. Adversarial review (fable) found 5 real defects, all fixed and proven by mutation testing. Worst one: notify.py crashed on a full disk — so a disk-full incident would have killed every scraper AND the alert path.\n\nErhvervsklub work is blocked: GitHub not authenticated, Supabase project paused. Nothing faked.\n\nMorning, in order:\n1. python3 ~/bin/github-device-login.py  → unlocks Claude app on your phone\n2. Install Tailscale on the phone → unlocks SSH to the box\n3. sudo bash ~/workbench/setup/allow-agent-installs.sh\n\nThen I can work from your phone.
```

---

_Ask Claude about any file in this repo — the markdown in `docs/`, `workbench-setup-spec.md`, and `../workbench-context/` is the full picture._
