# Workbench status

_Generated Sunday 26 July 2026, 16:01 CEST on `lenovo`._
_Regenerated automatically every 30 minutes. Everything below is measured, not remembered._

## Needs you

Nothing. All clear.

## Repositories

### `workbench`
Branch `main` — clean.

**Tests: 87 passing.** ✅

Recent commits:
```
26 Jul 15:37  Make the box's own facts trustworthy, and publish them continuously
26 Jul 15:30  Status: 26 Jul 15:30
26 Jul 15:15  Stop the apply agent notifying every 10 minutes, and let it self-heal
26 Jul 15:12  Decide what the local model is actually allowed to do in the nightly brief
26 Jul 15:09  Capture lenovo's live machine state
26 Jul 15:05  Close the loop: let the box pull from GitHub instead of only pushing
26 Jul 15:05  Record the 2026-07-26 autonomy decisions and queue the remaining work
26 Jul 15:05  Fix docs that contradict the repo, and test that they stay fixed
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
Sun 2026-07-26 16:02:14 CEST      50s Sun 2026-07-26 15:52:14 CEST 9min ago workbench-apply.timer          workbench-apply.service
Sun 2026-07-26 16:16:18 CEST    14min Sun 2026-07-26 16:01:18 CEST   5s ago workbench-watchdog.timer       workbench-watchdog.service
Sun 2026-07-26 19:46:14 CEST 3h 44min Sat 2026-07-25 19:46:14 CEST  20h ago launchpadlib-cache-clean.timer launchpadlib-cache-clean.service
-                                   - Sun 2026-07-26 16:01:14 CEST   9s ago workbench-status.timer         workbench-status.service

4 timers listed.
```

| Job | Last success |
|---|---|
| `apply` | 9 min ago |

## Machine

- Disk: 60G free of 98G (36% used)
- RAM: 12Gi available of 15Gi
- Uptime: up 3 days, 20 hours, 23 minutes

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
qwen3.5:9b    6488c96fa5fa    6.6 GB    3 days ago    
qwen3:4b      359d7dd4bcda    2.5 GB    3 days ago

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

Completed: 14

## Recent activity

Watchdog:
```
2026-07-26T14:26:16+02:00	run complete: 0 failing
2026-07-26T14:42:16+02:00	run complete: 0 failing
2026-07-26T14:58:16+02:00	run complete: 0 failing
2026-07-26T15:14:16+02:00	run complete: 0 failing
2026-07-26T15:30:16+02:00	run complete: 0 failing
2026-07-26T15:46:16+02:00	run complete: 0 failing
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
