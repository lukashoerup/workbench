# Workbench status

_Generated Friday 07 August 2026, 05:05 CEST on `lenovo`._
_Regenerated automatically every 30 minutes. Everything below is measured, not remembered._

## Needs you

Nothing. All clear.

## Repositories

### `workbench`
Branch `main` — clean.

**Tests: 87 passing.** ✅

Recent commits:
```
07 Aug 04:33  Status: 07 Aug 04:33
06 Aug 19:15  Stop the 30-minute status commit from triggering CI
06 Aug 19:07  Status: 06 Aug 19:07
26 Jul 16:17  Make the plain-language rule permanent
26 Jul 16:01  Status: 26 Jul 16:01
26 Jul 15:37  Make the box's own facts trustworthy, and publish them continuously
26 Jul 15:30  Status: 26 Jul 15:30
26 Jul 15:15  Stop the apply agent notifying every 10 minutes, and let it self-heal
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
NEXT                             LEFT LAST                           PASSED UNIT                           ACTIVATES
Fri 2026-08-07 05:10:14 CEST 4min 50s Fri 2026-08-07 05:00:14 CEST 5min ago workbench-apply.timer          workbench-apply.service
Fri 2026-08-07 05:21:01 CEST    15min Fri 2026-08-07 05:05:14 CEST   9s ago workbench-watchdog.timer       workbench-watchdog.service
Fri 2026-08-07 19:56:14 CEST      14h Thu 2026-08-06 19:56:14 CEST   9h ago launchpadlib-cache-clean.timer launchpadlib-cache-clean.service
-                                   - Fri 2026-08-07 05:05:14 CEST   9s ago workbench-status.timer         workbench-status.service

4 timers listed.
```

| Job | Last success |
|---|---|
| `apply` | 5 min ago |

## Machine

- Disk: 60G free of 98G (36% used)
- RAM: 11Gi available of 15Gi
- Uptime: up 2 weeks, 1 day, 9 hours, 27 minutes

Toolchain:

| Tool | Path |
|---|---|
| `claude` | /home/lukashoerup/.local/bin/claude |
| `uv` | /home/lukashoerup/.local/bin/uv |
| `python3` | /usr/bin/python3 |
| `ollama` | /usr/local/bin/ollama |
| `git` | /usr/bin/git |
| `node` | /usr/bin/node |
| `npm` | /usr/bin/npm |

Local models:
```
NAME          ID              SIZE      MODIFIED    
qwen3.5:9b    6488c96fa5fa    6.6 GB    2 weeks ago    
qwen3:4b      359d7dd4bcda    2.5 GB    2 weeks ago

Currently loaded:
NAME    ID    SIZE    PROCESSOR    CONTEXT    UNTIL
```

## Tasks

Open:
- workbench/2026-07-26-bootstrap-lenovo.md
- workbench/2026-07-26-hooks-and-work-block.md
- workbench/2026-07-26-local-model-jobs.md
- workbench/2026-07-26-notify-retry-outbox.md
- erhvervsklubben/T020-rls-tests.md
- erhvervsklubben/T022-ci-and-hooks.md

Completed: 15

## Recent activity

Watchdog:
```
2026-08-07T03:29:16+02:00	run complete: 0 failing
2026-08-07T03:45:16+02:00	run complete: 0 failing
2026-08-07T04:01:16+02:00	run complete: 0 failing
2026-08-07T04:17:16+02:00	run complete: 0 failing
2026-08-07T04:33:16+02:00	run complete: 0 failing
2026-08-07T04:49:16+02:00	run complete: 0 failing
```

Notifications sent:
```
2026-07-22T19:09:36+00:00	SENT	Silent-mode check — this one should not buzz.
2026-07-22T21:56:50+02:00	SENT	🌙 Overnight summary — nothing needs you tonight.\n\nWrote the first test suite: 43 tests, all green. Adversarial review (fable) found 5 real defects, all fixed and proven by mutation testing. Worst one: notify.py crashed on a full disk — so a disk-full incident would have killed every scraper AND the alert path.\n\nErhvervsklub work is blocked: GitHub not authenticated, Supabase project paused. Nothing faked.\n\nMorning, in order:\n1. python3 ~/bin/github-device-login.py  → unlocks Claude app on your phone\n2. Install Tailscale on the phone → unlocks SSH to the box\n3. sudo bash ~/workbench/setup/allow-agent-installs.sh\n\nThen I can work from your phone.
2026-07-26T15:09:05+02:00	SENT	⚠️ lenovo's repo has diverged from GitHub and holds local work I will not discard. It has stopped applying updates until this is resolved.
2026-07-26T15:09:06+02:00	SENT	✅ lenovo bootstrapped: it now pulls from GitHub every 10 min and applies updates itself. No terminal needed from here on.
2026-07-26T15:19:16+02:00	SENT	⚠️ lenovo failed to apply an update from GitHub. It is running older code than the repo.
2026-07-26T15:30:15+02:00	SENT	⚠️ lenovo cannot finish applying an update — something on the box needs a decision. See the apply log or STATUS.md.
```

---

_Ask Claude about any file in this repo — the markdown in `docs/`, `context/`, and `workbench-setup-spec.md` is the full picture._
