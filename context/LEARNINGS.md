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

## 2026-07-22 — Machine is Wi-Fi only, no ethernet
`lenovo` has no wired connection at its home location. Wi-Fi power save is disabled via a
systemd unit because an idle headless box otherwise drops its link. The watchdog retries
once with a 10 s pause before declaring the network down, to avoid false alarms on a
brief Wi-Fi blip.

## 2026-07-22 — sudo on this box needs an interactive password
No passwordless sudo, no askpass helper, no polkit. Coding agents cannot perform
privileged setup; anything needing root has to be handed to Lukas as a single script to
run. Written as `~/workbench/setup/phase1-privileged.sh` — idempotent, so re-running is safe.

## 2026-07-22 — User systemd timers need lingering
`systemctl --user` timers stop when the last login session ends. `loginctl enable-linger`
is required for anything meant to run 24/7, and that needs root. Until it is set, the
watchdog timer only runs while an SSH/tmux session is open.
