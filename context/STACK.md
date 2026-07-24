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

## Scheduled jobs
| Job | Cadence | Heartbeat marker |
|---|---|---|
| _none yet_ | | |

Watchdog (`~/bin/watchdog-check.sh`, user timer, every 15 min) reads its check list from
`~/.config/workbench/watchdog.conf`. Add a `heartbeat` line there for every new job.
