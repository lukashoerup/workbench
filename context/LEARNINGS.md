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

## 2026-07-22 — privileged setup is handed to Lukas as one script
Anything needing root goes into `setup/phase1-privileged.sh` — idempotent, so re-running
is safe. Written when the box had no passwordless sudo at all.

**Superseded, state unverified (noted 2026-07-26).** That original entry claimed "coding
agents cannot perform privileged setup", and the repo now contradicts it two ways:
`setup/phase1-privileged.sh:120-122` defaults `AGENT_SUDO=1` and writes a blanket
`NOPASSWD: ALL`, while `setup/allow-agent-installs.sh` writes a deliberately scoped grant
in a *different* file. Which is actually in force cannot be determined from the repo —
nothing records whether either ran. Measure on the box (`sudo -n true`;
`ls -l /etc/sudoers.d/`) and rewrite this entry with the answer; see
`tasks/2026-07-26-bootstrap-lenovo.md`. Until then, assume nothing about privilege.

## 2026-07-22 — User systemd timers need lingering
`systemctl --user` timers stop when the last login session ends, so `loginctl
enable-linger` is required for anything meant to run 24/7, and that needs root. Enabled on
this box by `setup/phase1-privileged.sh:103`. The failure mode it prevents: without it the
watchdog timer only runs while an SSH/tmux session is open, so an unattended box quietly
stops checking itself.
