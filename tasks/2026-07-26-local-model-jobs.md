# Task: the §8 zero-token autonomy layer (triage + gardener)

Depends on: `2026-07-26-notify-retry-outbox.md` (a 03:15 message lost to a blip
is the whole output of a night's work), and on the box being able to pull.

## Goal
Spec §8 — "the 24/7 part, zero cloud tokens" — is entirely unbuilt. This is the
layer that actually delivers "keeps working without being prompted", because it
runs on the local model and therefore costs nothing and is not rate-limited.

Build the two jobs that are useful **today**, before any scraper exists:
nightly triage and the weekly docs gardener.

## Acceptance criteria
- [ ] `bin/ollama_json.py` — one tested client for the
      `context/PATTERNS.md:30-54` recipe, stdlib only, always sending
      `"think": false`, schema-enforced, quarantining invalid output
- [ ] A response with `"response": ""` and a populated `thinking` field
      produces a diagnostic naming the `think` flag, not a generic JSON error
- [ ] `bin/nightly-triage.py` — one short brief from the day's logs, failures
      and commits; `reports/nightly/YYYY-MM-DD.md`; heartbeat on success only
- [ ] **The facts section is computed, never generated** — counts, names,
      statuses and the needs-a-human verdict come from code, reusing
      `collect_blockers()` in `bin/workbench-status.py`
- [ ] The model writes **only** the headline and a "where I would look first"
      line, from facts handed to it — it is never given raw logs to interpret
- [ ] **Triage still produces a brief when the model is down or returns
      garbage** — deterministic fallback from the counts alone, heartbeat still
      touched, exit 0
- [ ] `bin/weekly-gardener.py` — the spec's verbatim prompt
      (`workbench-setup-spec.md:305-316`), one call per docs file
- [ ] Gardener findings are rejected unless the named file exists **and** the
      quoted statement actually appears in it — hallucinated findings are
      quarantined, never surfaced
- [ ] Both units wrapped in `flock -n` on a shared Ollama lock
- [ ] `setup/watchdog.conf` gains a heartbeat line per job
- [ ] Tests green, with Ollama stubbed (no network, CI-safe)

## Scope
**May change:** `bin/ollama_json.py`, `bin/nightly-triage.py`,
`bin/weekly-gardener.py`, `setup/systemd/user/`, `setup/watchdog.conf`,
`context/STACK.md`, `tests/`
**Must NOT touch:** `bin/notify.py` internals, `pyproject.toml` (no new deps —
schema validation is hand-rolled; `jsonschema` would need approval)

## Which model writes the brief — decided 2026-07-26
Lukas asked whether the 9B is actually good enough, and was explicit that
quality wins over the appeal of running it locally. The answer is to change the
job, not the model.

**The 9B has not been shown capable of this task as originally specified.** Its
one benchmark (`context/STACK.md:46-49`) was bounded classification against a
rubric — read a listing, score it — on a sample of six, recorded as "indicative
not conclusive". Reading heterogeneous logs and deciding what matters is a
different and much looser job, and `context/LEARNINGS.md:14-18` records the
failure mode that would bite: a model can be schema-valid and confidently
wrong. A confabulated "all quiet" on the night something broke is worse than no
brief at all, because it actively reassures.

**But that work should not be a model's job at all.** Every question that
matters is deterministic: did tests fail, did the watchdog report failures, is
a heartbeat stale, is the notification channel dead, is there unpushed work.
`collect_blockers()` in `bin/workbench-status.py` already answers exactly these
— that is what it was rewritten for this same day.

So: **facts are computed; the model only writes the sentence on top.** It is
handed a small structured summary and asked for a headline and a "where I would
look first" line. It never sees raw logs, so it cannot invent an incident, and
the worst failure available to it is an awkward sentence sitting next to
correct facts.

**Not using Claude for this.** Spec §8's whole premise is zero cloud tokens
overnight, and on a machine that is idle most nights a nightly Claude call
spends rate-limit window to summarise "nothing happened" — which code writes
perfectly. The night something *does* break is already covered by the watchdog
alerting immediately; the brief's job is the boring nights.

**Settle it with evidence, the way the model tier was settled.** Once the box
is bootstrapped, run the real thing on a real day of logs and compare against
what a Claude session writes from the same facts. If the 9B's sentence is not
usable, drop it and ship the deterministic brief alone — it is complete without
it. Record the outcome in `context/STACK.md`. Do not decide this by opinion;
that is exactly how the 4B nearly got shipped.

## Non-negotiables
- **`"think": False`.** `context/LEARNINGS.md:7-12`: left on, Ollama routes the
  answer into a separate `thinking` field and returns `"response": ""`, so
  every `json.loads` fails and the model looks incapable of JSON. It is not —
  you are reading the wrong field. Also 15.0 s versus 1.7 s on the same prompt.
- **Never two models at once** (`context/STACK.md:44`) — 6.6 GB model, 16 GB
  soldered RAM. `flock -n` in the unit, not in Python, so a blocked job exits
  rather than queueing behind a two-hour run.
- **The gardener only points; it never fixes** (`workbench-setup-spec.md:310`).
- **Validate at the boundary.** The 4B was rejected for being 6/6 schema-valid
  and 3/6 correct (`context/STACK.md:62-64`). Structural validation cannot
  catch that, which is why the gardener checks quoted statements against the
  actual file.
- Local models do bounded structured tasks only, never open-ended work
  (`context/STACK.md:73-74`).

## Not building the canary
Spec §8.3 validates *scraper* data and there are no scrapers
(`STATUS.md:56`). Padding it with invented checks would be exactly the faking
this system is built to avoid. Defer it with the trigger: **un-defer when the
first scraper writes its first heartbeat.**

## Docs affected
`context/STACK.md` scheduled-jobs table; `context/PATTERNS.md` if the client
supersedes the inline recipe.

## Size check
Two jobs plus a shared client. Split into three commits if it runs long.

## Working notes (agent fills in)
