# Task: the §8 autonomy layer (nightly triage + weekly docs gardener)

Depends on: ~~`2026-07-26-notify-retry-outbox.md`~~ — **satisfied 2026-08-04**
(a 03:15 message lost to a blip is now retried and queued rather than lost) —
and on the box being able to pull, satisfied 2026-07-26.

## Goal
Spec §8 — "the 24/7 part, zero cloud tokens" — is entirely unbuilt. This is the
layer that actually delivers "keeps working without being prompted".

Originally scoped as two local-model jobs. **Lukas ruled the local model out on
2026-08-04** (see below), which does not weaken the layer: the nightly brief
becomes pure code, which is cheaper, faster and strictly more reliable. The
gardener is the only part that genuinely needed judgement, and it moved to Claude
when he chose that over dropping it, later the same day.

So: **nightly triage, deterministic, no model. Gardener, Claude, weekly.**

## Acceptance criteria
- [x] ~~`bin/ollama_json.py`~~ — **deferred, no consumer.** Both jobs that would
      have used it are now model-free or blocked; building a client for nobody is
      speculative work. Un-defer when something actually needs Ollama. The
      `"think": false` trap it was meant to encapsulate stays recorded in
      `context/LEARNINGS.md` and `context/PATTERNS.md`, which is where it is
      useful anyway.
- [x] `bin/nightly-triage.py` — one short brief from the day's logs, failures
      and commits; `reports/nightly/YYYY-MM-DD.md`; heartbeat on success only
- [x] **The brief is entirely computed. No model is involved at all** — see
      "Lukas's ruling" below. Counts, names, statuses and the needs-a-human
      verdict come from code, reusing `collect_blockers()` in
      `bin/workbench-status.py`
- [x] The brief is deterministic: same inputs → same output, byte for byte.
      That makes it diffable, and makes a wrong brief a bug with a repro rather
      than a bad roll
- [x] `bin/weekly-gardener.py` — **runs on Claude, weekly** (Lukas chose this
      2026-08-04). Headless `claude -p`, one call per docs file, the spec's
      verbatim prompt (`workbench-setup-spec.md:305-316`)
- [x] **It only points; it never fixes** (`workbench-setup-spec.md:310`). No
      write tools, no commits, no branch. Output is a report, full stop
- [x] **The hallucination guard survives the model upgrade** — a finding is
      rejected unless the named file exists *and* the quoted statement appears in
      it verbatim. Cheap, and the failure it catches is silent
- [x] Findings land in `reports/gardener/YYYY-MM-DD.md`; one Telegram summary,
      and **silence when nothing was found** — a weekly "nothing to report" buzz
      trains him to ignore it
- [x] Exits cleanly on rate-limit exhaustion rather than burning retries
      (spec §1); never runs concurrently with a work block, since both want
      Claude on the same box
- [x] ~~Both units wrapped in `flock -n` on a shared Ollama lock~~ — no Ollama
      left. The gardener still needs a lock, but against the **work block**, not
      against a model
- [x] `setup/watchdog.conf` gains a heartbeat line per job
- [x] Tests green — 169 passing (was 117), shellcheck clean; `claude` stubbed as a subprocess (no network, CI-safe),
      the same way the bash scripts are already driven in `tests/`

## Scope
**May change:** `bin/nightly-triage.py`, `bin/weekly-gardener.py`,
`setup/systemd/user/`, `setup/watchdog.conf`, `context/STACK.md`, `tests/`
**Must NOT touch:** `bin/notify.py` internals, `pyproject.toml` (no new deps).
No `bin/ollama_json.py` — deferred, see the first criterion.

## Lukas's ruling — 2026-08-04 (supersedes the section below)
Asked what the next step was, Lukas rejected running the nightly brief and the
weekly docs review on the local model: the job "kræver tankekraft", a weak local
model taking decisions and writing summaries is risky, and it "vil reelt ødelægge
mere kontekst end det vil gavne."

He is right, and the 2026-07-26 analysis below already conceded the ground —
it kept a model in the loop for one sentence and left an explicit escape hatch
("drop it and ship the deterministic brief alone — it is complete without it").
Take the escape hatch.

**Nightly brief: no model. Pure code.** Every question that matters is already
deterministic — did tests fail, is a heartbeat stale, is the channel dead, is
there unpushed work. `collect_blockers()` answers all of them. The model was only
ever writing a decorative headline on top of correct facts; deleting it removes a
whole class of failure and loses nothing measurable. This also makes the job
cheaper, faster, and testable without stubbing Ollama.

**Weekly docs gardener: Claude, weekly. Chosen by Lukas 2026-08-04.** This one
cannot be made deterministic — "which statements in this doc are no longer true"
is irreducibly a judgement call, which is precisely why it was the *worst* fit
for the weakest model available. Asked to choose between running it on Claude and
dropping it, he took Claude.

Consequences to build against:
- **It runs on the box, not in CI.** Claude Code is installed and authenticated
  at `/home/lukashoerup/.local/bin/claude` (`STATUS.md` toolchain table), so a
  weekly user timer reuses the existing auth. A GitHub Actions schedule would
  need an API key — a new secret *and* a second billing relationship, when the
  subscription already covers this.
- **It competes with the work block for the same Claude.** Both run headless on
  one box against one rate-limit window. They must not overlap: lock, and
  schedule the gardener well clear of the block.
- **Weekly is what makes this affordable.** The zero-token rule in spec §8 was
  aimed at jobs running *every night* and burning 5-hour windows on machines that
  are idle most nights. One weekly pass over ~10 docs files is a rounding error
  next to a single dispatched session. If the cadence ever creeps toward daily,
  this decision needs re-taking, not extending.
- **The hallucination guard stays.** A better model lowers the rate but does not
  change the shape of the failure, and the check — does this file exist, does
  this quoted line actually appear in it — costs nothing. The 4B earned this
  guard; Claude does not get to inherit an exemption from it.

**One correction to his framing, for the record:** the plan was the 9B, not the
4B. The 4B was rejected on 2026-07-22 for exactly the failure he describes
(`context/STACK.md`: 6/6 schema-valid, 3/6 correct — a coin flip that looks like
an answer). His objection survives the correction, because the 9B was never
shown capable of *this* task either; its one benchmark was bounded
classification against a rubric, on a sample of six, recorded as "indicative not
conclusive".

## Which model writes the brief — decided 2026-07-26 (superseded, kept for the reasoning)
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
Done 2026-08-04. 52 new tests; 169 green overall, shellcheck clean.

**The brief reuses `collect_blockers()` rather than reimplementing it.**
workbench-status.py has a dash in its name, so it loads via importlib — the same
trick `tests/test_status_generator.py` already uses. This matters beyond tidiness:
two implementations of "is this machine healthy" would eventually disagree, and
the phone page and the 03:15 brief disagreeing is the worst possible version of
that.

**`render()` is pure and tested as such**, including a test that fails if it ever
shells out. Determinism is what replaces the model's judgement with something
reviewable: a wrong brief is now a bug with a reproduction.

**Status commits are excluded from the brief's commit list.** The publisher
amends one forward every 30 minutes, so including them buries the real work.

**The publisher had to be widened to `reports/`** — otherwise both jobs write
files that never leave the box, and a brief nobody can read is a brief that was
not written. Guarded on the directory existing, because `git add` fails outright
on a pathspec matching nothing and would have taken STATUS.md down with it. A
test covers the case that actually bites: a report landing on a quiet night when
STATUS.md has not substantively changed, which used to hit the early exit. Note
it arrives by *amending* the standing status commit, so the commit count does not
move — the first version of that test asserted otherwise and was wrong.

**This pathspec is now duplicated knowledge.** `bin/publish-status.sh` and the
future `hooks/pre-commit` fast-path must list the same paths; both carry a
comment saying so. If a third place ever needs it, extract it instead.

**Gardener notes.** One call per docs file, contents passed inline so the model
needs no tools at all — which is what makes denying the mutating tools honest
rather than decorative. The hallucination guard normalises whitespace before
matching, because these docs are hard-wrapped at 90 columns and an exact
substring test would reject nearly every true finding; the smoke test on the real
`CLAUDE.md` confirmed a real quote spanning a line wrap passes while an invented
one is quarantined. Quarantined findings are *listed*, not hidden, so the
invention rate stays visible — if it turns out to be high, that is the evidence
for dropping the job.

**A rate-limited pass writes no heartbeat.** It writes the report, says it was
truncated, and exits 0. The watchdog then surfaces "has not completed in over a
week", which is the honest signal; a heartbeat there would hide a job that
silently stopped working.

**Not built: the §8.3 canary.** Still no scrapers, so its trigger is unchanged —
un-defer when the first scraper writes its first heartbeat.

**Untested on real hardware.** The `claude -p` flag set (`--strict-mcp-config`,
`--disallowedTools`) was read off `claude --help` in a cloud container and is
stubbed in tests, so the *contract* is covered but the invocation itself has
never run against the real CLI on the box. First live Sunday will prove it.
