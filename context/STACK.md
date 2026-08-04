# Stack — standard choices

Cross-project defaults. Deviating from these needs a reason recorded in the project's PROJECT.md.

## Machine
| | |
|---|---|
| Host | `lenovo` — ThinkPad X1 Carbon Gen 10 (21CBCTO1WW) |
| CPU / RAM | i7-1260P, 12C/16T, 16 GB soldered |
| GPU | none — Iris Xe only, **all inference is CPU-only** |
| OS | Ubuntu 24.04.4 LTS, headless |
| Network | Wi-Fi only (`wlp0s20f3`), home. No ethernet. LAN 192.168.1.145. |
| Tailscale | `lenovo.tail8658f1.ts.net` — 100.92.78.13. Always use this, not the LAN IP. |
| Timezone | Europe/Copenhagen (job schedules are local time) |

## Languages & tools
- Python 3.12.3 (system), environments via `uv` (installed 2026-07-22, `~/.local/bin/uv`).
- `ripgrep` for search. `git` for everything versioned.
- HTTP scraping: `curl_cffi` with Chrome impersonation — never raw `requests`.

## Services
- **Supabase** — all persistent data. The laptop is a replaceable worker, never the source of truth.
- **GitHub** — all code **and all markdown**. Single source of truth for docs; the Claude
  apps read repos from there. Decided 2026-07-22: no Google Drive mirror. A mirror is a
  second copy that drifts plus a sync job that can break silently, for a benefit the repo
  path already covers.

### How Lukas reaches the system
| Situation | Path | Can do |
|---|---|---|
| Working on code | GitHub → Claude Code (web/desktop) | Full repo, §6 doc routing intact, can edit |
| Question on the phone | Claude app → Supabase connector | Query data, charts, artifacts — read-only |
| Something broke at 03:00 | Telegram push | One line + link. Free, no session needed |
| Server control | Desktop Claude Code → SSH over Tailscale | Anything. Mobile has no shell |

Consequence: docs discipline matters *more*, not less. Bloated files are merely expensive
in a Claude Code session; in connector-side search they bury the useful answer.
- **Telegram** — all notifications, via `~/bin/notify.py`. Credentials in `~/.secrets/telegram.env`.
  Verified end-to-end 2026-07-22: CLI, Python import, and `silent=True` all deliver.
  Connectors (claude.ai MCP: Supabase, Gmail, Drive, Calendar, M365, Vercel, Kiwi) are for
  interactive sessions only — never for cron jobs, which must stay zero-cloud-token per §8.

## Local models (Ollama)
CPU-only, 16 GB. Never run two simultaneously.

| Role | Model | tok/s | s/listing | Schema valid | Agreed with human |
|---|---|---|---|---|---|
| **Everything** | `qwen3.5:9b` | 2.8 | 35.9 | 6/6 | **6/6** |
| Rejected | `qwen3:4b` | 6.1 | 26.2 | 6/6 | **3/6** |

**Decision 2026-07-22 — the 9B is the workhorse, reversing spec §3.** The spec assumed the
4B would handle the 90% case with the 9B reserved for nightly work. The benchmark says
otherwise: the 4B scored 3/6, marked five of six listings `relevant: true`, and returned
score 0 or 1 for everything — it is not discriminating, it is agreeing. At 3/6 on a
binary judgement that is a coin flip, which is worse than useless because it looks like an
answer. The 9B got 6/6 with sensible spread (100, 85, 15, 15, 12, 0).

The speed cost is smaller than tok/s suggests: 36 s versus 26 s per listing, so a 200-listing
nightly batch is ~2 h instead of ~1.5 h. Both finish overnight, which is the only deadline
that matters. Paying 10 s a listing for a usable answer is obviously right.

Note the 4B's failure mode is exactly the one spec §2.6 warns about: **6/6 schema-valid and
3/6 correct.** Structural validation would have passed all of it. Only a human-labelled
sample catches this — which is why the weekly spot-check is not optional.

Caveat: 6 listings is a small sample, indicative not conclusive. Re-run
`~/bin/ollama-benchmark.py` against real DBA data once Project 1 is scraping, and revisit
if the 9B's wall-clock becomes a problem at real volume.

<!-- Raw results: ~/logs/benchmarks/20260722-215909.json
     The 20260722-215214.json run is the broken one — think:true, 0/6 parseable. -->

**Hard rule:** local models do bounded structured tasks only. They never do open-ended
development work, regardless of harness.

### Decision 2026-08-04 — no local model writes anything a human reads as fact
Lukas ruled out the local model for the nightly brief and the weekly docs review: the work
"kræver tankekraft", and a weak model summarising and deciding "vil reelt ødelægge mere
kontekst end det vil gavne."

The resolution is to **change the job, not the model**:

- **Nightly triage is now entirely deterministic — no model at all.** Every question that
  matters (tests failing, stale heartbeat, dead channel, unpushed work) is already answered
  by `collect_blockers()` in `bin/workbench-status.py`. The model was only ever writing a
  headline over correct facts. Removing it costs nothing measurable and deletes a whole
  failure class: a confabulated "all quiet" on the night something broke is worse than no
  brief, because it actively reassures.
- **The weekly docs gardener runs on Claude, weekly** — Lukas chose this over dropping it,
  same day. "Which statements are no longer true" cannot be computed, so it is the one job
  here that genuinely needs judgement, and it gets the model to match. It runs headless on
  the box against the installed Claude Code auth, not in CI against an API key, and it must
  not overlap the work block — one box, one rate-limit window.

  Weekly is load-bearing, not incidental: §8's zero-token rule was aimed at nightly jobs
  burning 5-hour windows on a box that is idle most nights. A weekly pass over ~10 docs
  files is a rounding error next to one dispatched session. **If the cadence ever creeps
  toward daily, re-take this decision rather than extending it.**

  The hallucination guard stays regardless of model: a finding is rejected unless the named
  file exists and the quoted statement appears in it verbatim. A better model lowers the
  rate but does not change the shape of the failure, and the check is free.

**The generalisation, which outlives both jobs:** prefer computing a fact to generating it.
Reach for a model only where the output is genuinely not computable, and then match the
model to how much judgement the task really needs. This tightens rather than contradicts
the hard rule above — "bounded and structured" was never sufficient on its own, as the 4B
proved by being 6/6 schema-valid and 3/6 correct.

## Autonomy model — decided 2026-07-26
Two layers, because they have different costs and different risks.

**Free layer, runs forever, zero cloud tokens.** CI on every push, the watchdog,
the status publisher, and the §8 nightly triage. This is what actually delivers
"keeps working without being prompted", and it is the only layer allowed to run
unattended by default.

Amended 2026-08-04: this layer is now zero-token because it is *code*, not
because it runs a local model — see the decision above. The weekly gardener left
this layer entirely: it moved to the agent layer below, on Claude, weekly.

**Agent layer, bounded.** Headless Claude work blocks on the box, off by
default. Spec §1 warns against long autonomous cloud-agent runs because
5-hour rate-limit windows, not compute, are the bottleneck on Claude Pro — so
blocks are bounded: one atomic task at a time, wall-clock capped, 3-strike
circuit breaker, night-scheduled, never merging to `main`.

The weekly docs gardener joined this layer 2026-08-04. It is the cheap, safe end
of it — read-only, one weekly pass, never fixes anything — but it draws on the
same rate-limit window as a work block on the same box, so the two must be locked
against each other rather than merely scheduled apart.

Corollary that decides everything else: **the box pulls from GitHub; nothing
pushes into the box.** Cloud sessions cannot reach `lenovo` (no ssh, no keys,
no Tailscale, HTTPS-only egress) and inbound access is not wanted. GitHub is
the meeting point, exactly as the 2026-07-24 deferral note put it: "cloud =
Claude working, lenovo = scripts working, GitHub = meeting point."

## Scheduled jobs
| Job | Cadence | Heartbeat marker |
|---|---|---|
| `workbench-status.timer` | 30 min | _watched as a unit, not a heartbeat_ |
| `workbench-watchdog.timer` | 15 min | _watched as a unit, not a heartbeat_ |

Planned, not yet installed: `workbench-apply` (pull + self-install),
`workbench-triage` (nightly 03:15), `workbench-gardener` (Sunday 04:30).

Watchdog (`~/bin/watchdog-check.sh`, user timer, every 15 min) reads its check list from
`~/.config/workbench/watchdog.conf`. Add a `heartbeat` line there for every new job.
