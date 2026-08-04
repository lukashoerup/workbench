# Patterns — reusable recipes

Copy-paste solutions proven on this workbench. A pattern earns a place here only after it
has worked in a real project. Keep each entry short; link to the project file for detail.

## Telegram notification
```python
import sys, os
sys.path.insert(0, os.path.expanduser("~/bin"))
from notify import notify

notify("DBA: 3 new matches above threshold")   # returns bool, never raises
notify("Nightly triage: all green", silent=True)  # no sound for routine reports
```
Missing credentials degrade to a log line in `~/logs/notify.log` and return `False` — a
dead notification channel must never take down a job.

**A dropped Wi-Fi link no longer loses the message.** Transient failures (network, timeout,
429, 5xx) are retried three times over 7 s and then queued to
`~/.local/state/workbench/outbox.jsonl`. The queue drains oldest-first at the start of the
next `notify()` call, and from the end of every watchdog run — so it empties within 15 min
even on a box with nothing to say. Permanent failures (no credentials, other 4xx, an API
`ok: false`) are never queued, because they would never leave.

**`False` means "not delivered now", not "lost".** A queued message still returns `False`,
and callers must keep treating that as failure: `bin/watchdog-check.sh` starts a 6 h alert
cooldown on `True`, so a queued alert reporting success would mute the incident it was
about until morning.

## Job heartbeat (so the watchdog notices silent death)
```python
from pathlib import Path
HB = Path.home() / ".local/state/workbench/heartbeats" / "dba"
HB.parent.mkdir(parents=True, exist_ok=True)
HB.touch()          # last line of a SUCCESSFUL run only — never in a finally block
```
Then add to `~/.config/workbench/watchdog.conf`:
```
heartbeat dba /home/lukashoerup/.local/state/workbench/heartbeats/dba 7200
```

## Ollama structured output
```python
payload = {
    "model": "qwen3.5:9b",    # the workhorse — the 4B was rejected, see STACK
    "prompt": prompt,
    "stream": False,
    "think": False,            # <-- REQUIRED on qwen3. See below.
    "format": SCHEMA,          # JSON Schema, enforced by Ollama
    "options": {"temperature": 0},
}
body = json.loads(urlopen(Request(f"{OLLAMA}/api/generate",
                  data=json.dumps(payload).encode(),
                  headers={"Content-Type": "application/json"}), timeout=600).read())
result = json.loads(body["response"])
```

**`think: False` is not optional on qwen3.** Left on, Ollama routes the model's answer
into a separate `thinking` field and returns `"response": ""` — so `json.loads(response)`
fails on every single call and it looks like the model cannot produce JSON at all. It can;
you are reading the wrong field. Measured 2026-07-22: same prompt took 15.0 s with thinking
on versus 1.7 s off, because the reasoning tokens were nearly the entire cost. Bounded
structured tasks want no reasoning preamble.

Then validate at the boundary: schema check + sanity check (e.g. price is a plausible
number). Invalid → quarantine + log, never silently pass.

## curl_cffi Chrome impersonation
_pending Phase 4._

## Snapshot test for a parser
_pending Phase 4 — golden file in `tests/fixtures/`, written BEFORE parser logic._
