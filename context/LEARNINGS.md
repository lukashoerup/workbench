# Learnings — cross-project, dated

Experiences, not decisions. Decisions go in a project's PROJECT.md and are permanent;
entries here describe how the world behaved on a given date and **can expire**.
Date every entry. Delete entries that stop being true.

## 2026-07-22 — qwen3 needs `think: False` or it looks completely broken
With thinking left on, Ollama puts the model's answer in a separate `thinking` field and
returns `"response": ""`. Every `json.loads(response)` call fails, so the model appears
incapable of producing JSON — 0/6 on the first benchmark run. It was producing perfect JSON
the whole time, in the field nobody was reading. Also 9× slower: 15.0 s versus 1.7 s on the
same prompt. Recipe in [[PATTERNS]].

## 2026-07-22 — A model can be 100% schema-valid and 50% wrong
The 4B passed schema validation on every listing while getting half the judgements wrong,
marking almost everything relevant with a score of 0. Structural validation cannot detect
this; only human-labelled samples can. Confirms the spec's insistence on a weekly
spot-check, and the reason the benchmark measures agreement rather than just tok/s.

## 2026-08-06 — A heartbeat commit that runs CI turns any GitHub outage into mail
`publish-status.sh` pushes a STATUS.md-only commit every 30 minutes, and `tests.yml`
triggered on every push, so the repo ran ~46 CI runs a day that could only ever repeat the
previous commit's verdict. On 2026-08-06 GitHub could not assign hosted runners: queue
times crept up (22 s → 105 s → 321 s), then two consecutive runs sat unassigned
(`runner_id: 0`) for exactly 951 s and were cancelled. Nothing was broken — 87 tests green
locally, last real code commit green in CI — but each cancellation mailed a "Run failed"
notice, so the first symptom of a GitHub-side problem was an inbox, not a red test.

Fixed by `paths-ignore: STATUS.md` on both triggers. The general lesson: a scheduled
heartbeat commit must not trigger CI. It multiplies every provider hiccup by the heartbeat
frequency, and alerts that fire when nothing is wrong are the ones that get ignored when
something is.

## 2026-07-22 — Machine is Wi-Fi only, no ethernet
`lenovo` has no wired connection at its home location. Wi-Fi power save is disabled via a
systemd unit because an idle headless box otherwise drops its link. The watchdog retries
once with a 10 s pause before declaring the network down, to avoid false alarms on a
brief Wi-Fi blip.

## 2026-07-26 — agents on this box have unrestricted root (measured)
`sudo -n true` succeeds. Both grants exist:

```
-r--r----- 50-workbench-agent    scoped: apt, systemctl, journalctl, ollama, tailscale
-r--r----- 90-agent-nopasswd     lukashoerup ALL=(ALL) NOPASSWD: ALL
```

The blanket grant wins, so **the scoped one is currently decorative** — an agent here can
do anything root can. Lukas's decision 2026-07-26: leave it. It is a personal box with no
production data, and the blanket grant is what lets an agent install things unattended,
which is the point. Revisit if the box ever holds something worth stealing.

This replaces an entry claiming the opposite ("no passwordless sudo, coding agents cannot
perform privileged setup"), written 2026-07-22 before `phase1-privileged.sh` ran. It was
false from 2026-07-23 onward, and an agent reading it would wrongly conclude it had to
hand every privileged step to a human. Privileged setup still *belongs* in
`setup/phase1-privileged.sh` — idempotent, reviewable, re-runnable — but that is a
convention now, not a constraint.

## 2026-07-22 — User systemd timers need lingering
`systemctl --user` timers stop when the last login session ends, so `loginctl
enable-linger` is required for anything meant to run 24/7, and that needs root. Enabled on
this box by `setup/phase1-privileged.sh:103`. The failure mode it prevents: without it the
watchdog timer only runs while an SSH/tmux session is open, so an unattended box quietly
stops checking itself.
