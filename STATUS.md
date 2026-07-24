# Workbench status

_Generated Sunday 26 July 2026, 14:59 CEST on `lenovo`._
_Regenerated automatically every 30 minutes. Everything below is measured, not remembered._

## Needs you

Nothing. All clear.

## Repositories

### `workbench`
Branch `main` — clean.

**Tests: 56 passing.** ✅

Recent commits:
```
24 Jul 13:32  Status: 26 Jul 14:27
24 Jul 13:31  Merge task/2026-07-24-merge-context
24 Jul 13:31  Merge workbench-context into context/ — repo-qualified references everywhere
24 Jul 13:12  Merge task/2026-07-24-md-cleanup
24 Jul 13:12  Docs cleanup: interface table + historical banner on the spec
24 Jul 13:09  Merge task/2026-07-24-defer-runner
24 Jul 13:09  Record work-block-runner deferral: cloud dispatch covers it
24 Jul 13:01  Status: 24 Jul 13:01
```
### `erhvervsklubben`
Branch `main` — clean.

_Tests not run by this box (Node project — CI is the judge)._

Recent commits:
```
24 Jul 13:32  T023: point cross-project references at workbench/context (repo merge)
24 Jul 13:14  Queue T022: CI pipeline + repo hooks (approved track D)
24 Jul 13:13  Merge task/T021-docs-realignment
24 Jul 13:13  T021: docs realignment for the cloud-dispatch model + discovery artifacts
24 Jul 08:16  Docs: complete the intended §6 structure + mark project status
23 Jul 22:45  Fix migration fidelity from Fable review (verified against prod)
23 Jul 22:37  Phase 1: schema migration, seed, and RLS test harness (green)
23 Jul 22:13  T001: scaffold React+Vite+TS+Tailwind app with green pipeline
```

## Scheduled jobs

```
NEXT                             LEFT LAST                              PASSED UNIT                           ACTIVATES
Sun 2026-07-26 15:13:31 CEST    14min Sun 2026-07-26 14:58:14 CEST 1min 2s ago workbench-watchdog.timer       workbench-watchdog.service
Sun 2026-07-26 19:46:14 CEST 4h 46min Sat 2026-07-25 19:46:14 CEST     19h ago launchpadlib-cache-clean.timer launchpadlib-cache-clean.service
-                                   - Sun 2026-07-26 14:59:14 CEST      2s ago workbench-status.timer         workbench-status.service

3 timers listed.
```

_No job heartbeats yet — no scrapers are running._

## Machine

- Disk: 60G free of 98G (36% used)
- RAM: 12Gi available of 15Gi
- Uptime: up 3 days, 19 hours, 21 minutes

Local models:
```
NAME          ID              SIZE      MODIFIED   
qwen3.5:9b    6488c96fa5fa    6.6 GB    3 days ago    
qwen3:4b      359d7dd4bcda    2.5 GB    3 days ago

Currently loaded:
NAME    ID    SIZE    PROCESSOR    CONTEXT    UNTIL
```

## Tasks

Open:
- erhvervsklubben/T020-rls-tests.md
- erhvervsklubben/T022-ci-and-hooks.md

Completed: 9

## Recent activity

Watchdog:
```
2026-07-26T13:38:16+02:00	run complete: 0 failing
2026-07-26T13:54:16+02:00	run complete: 0 failing
2026-07-26T14:10:16+02:00	run complete: 0 failing
2026-07-26T14:26:16+02:00	run complete: 0 failing
2026-07-26T14:42:16+02:00	run complete: 0 failing
2026-07-26T14:58:16+02:00	run complete: 0 failing
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
