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

## 2026-09-27 — An AI judge optimises whatever its brief says, including the wrong thing
In the re-enactment fix loop (generate → Gemini judge → retry with the judge's own fix),
the bundle reference image was sent with a shot that comes *before* the bundle is shown.
The judge failed a good take for lacking the bundle, its "fix" went into the next
prompt, and the next take put the bundle in — worse than the one rejected. An automatic
loop amplifies a wrong brief. Give every item its own brief and only the references that
apply to it; keep a human-readable log of each verdict and fix so a bad loop is visible.

## 2026-09-27 — Vision-model judges are useful, stochastic, and blind below a threshold
Gemini 3.1 Pro watching a 22 s cut found 6 of 7 story-level defects blind (< 1 kr);
3.5 Flash found 2. The same judge on the fixed cut raised issues it had not mentioned
before and made one false claim. It missed small continuity (boot colour, heights) and
everything measurable (timing drift, exposure jumps, audio holes) — code caught those.
Gemini samples video at 1 fps unless `fps` is set. Pattern: code checks for anything
measurable; the model for meaning; run it several times or pairwise; compare against
the best alternative rather than a fixed score (a 4/10 take was still the best one).

## 2026-09-27 — Gemini API video quota is per model per day, and it bites early
After 10 Veo 3.1 Lite videos the project got `429 exceeded your current quota` for the
rest of the day while Veo Fast and text models still worked. Credit balance was not the
issue. Anything at episode scale needs Vertex AI or a higher tier. Danish credit moves by
list price × 1.25 (VAT).

## 2026-09-27 — The GitHub MCP connector still cannot create repositories
`create_repository` → 403 "Resource not accessible by integration", same as the write
failures in July. `add_repo` with push access works for repos that already exist, so a
new repo needs Lukas to create it (one tap: github.com/new) before an agent can push.

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

## 2026-09-05 — A data migration that names a production row breaks every fresh database
erhvervsklubben's `adhoc_fines` migration (2026-08-08) inserted a fine against meeting
record id 30 and then asserted the result. Production had the row, so it ran clean there.
CI rebuilds the database from scratch on every run, has no record 30, and died on the
foreign key at `supabase start` — before a single test ran — on every push for four weeks.
Nobody noticed because the next two commits were documents and the site itself, deployed
by Vercel from `main`, never blinked. Found only when someone asked whether everything
was running.

Two lessons. A migration that writes rows must say what to do when the rows it depends
on are absent (the repo already had the pattern: check the club's own totals, `raise
notice`, `return`) — and a green production run proves nothing about a fresh stack. And
"is CI green on main" belongs in any "is everything OK" check, because a red CI with a
live site is exactly the failure that stays quiet.

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
