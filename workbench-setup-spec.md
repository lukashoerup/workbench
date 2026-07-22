# Home AI Workbench — Setup Specification

**Audience:** A coding agent (Claude Code or Codex CLI) executing this setup, step by step, with Lukas approving key decisions.
**Owner:** Lukas (Copenhagen). Hobby projects — the design optimizes for *minimal human time spent on testing and small bugs*, not for maximum autonomy.

---

## 1. Purpose and background

Lukas has a spare work laptop (Lenovo, gaming-capable — exact GPU/RAM unknown, see §3) with a damaged-but-readable screen. It becomes a **24/7 headless server** hosting:

1. Deterministic data pipelines (scrapers on cron) for hobby projects:
   - Used-goods tracking on DBA.dk, Vinted, and similar marketplaces (watchlist + relevance scoring + price-drop alerts).
   - Used-car data collection from Bilbasen and/or DBA.
   - (Erhvervsklubben club automation exists separately on Supabase + Claude; it is **out of scope** for the local LLM — low volume, high correctness requirements.)
2. A **local LLM via Ollama** for cheap, high-volume, low-complexity inference (scoring, extraction, triage, summaries).
3. **Claude Code and Codex CLI** as the development agents, used in short focused sessions.

Lukas interacts from his iMac, MacBook Pro, and phone. **Only the Lenovo stays powered on.**

### Core token-economy principle
Subscriptions in play: Claude Pro + ChatGPT Plus (two separate token pools, ~$40/month total; no MAX, no pay-as-you-go API for now). Therefore:

- **Night = deterministic operations + local model.** Zero cloud tokens in production.
- **Day = short, supervised cloud-agent sessions.** Expensive understanding is paid once (plan/spec), cheap implementation follows.
- Never plan long autonomous overnight cloud-agent runs — 5-hour rate-limit windows are the real bottleneck, not compute.

### Division of labor
| Role | Actor |
|---|---|
| Architecture, hard problems, specs (task files), final reviews | Claude Code (Claude Pro) |
| Volume implementation, iteration, PR code review | Codex CLI (ChatGPT Plus) |
| Production inference: listing relevance scoring, extraction, dedup, log triage, nightly reports, docs-drift detection | Local model (Ollama) |
| Big decisions and acceptance testing only — never small-bug hunting | Lukas |

---

## 2. Non-negotiable principles (from practical-experience research)

These were validated against published field reports and must be encoded into the setup:

1. **Never trust agent self-reports.** Agents can hallucinate *work* (detailed reports about code never written). Verification is deterministic only: `git diff`, test results, CI status. Tests are the judge, not agents.
2. **Small, bounded tasks.** All work is structured as atomic task files (~30–60 min of agent work), scoped to explicit files, with acceptance criteria. Long runs cause scope drift and tunnel vision; periodic fresh starts are required.
3. **Persistent memory is deliberate.** Sessions are ephemeral. Updating the relevant docs is part of every task's definition of done — project memory must grow explicitly.
4. **Guardrails over supervision.** Never commit on red tests; branch per task; commit per completed task (rollback = one revert); no new dependencies without approval; do-not-touch zones (.env, CI configs, infra); retry cap (3 attempts on the same failing test → stop, leave a note, move to review queue).
5. **Circuit breakers.** Hooks stop an agent looping on the same failure rather than letting it burn a rate-limit window.
6. **Local model output is untrusted at the boundary.** Enforce JSON via Ollama structured outputs (schema), then validate: schema check + sanity checks (e.g., price is a plausible number). Watch for semantically-wrong-but-structurally-valid output; a weekly human spot-check of samples is the quality gauge.
7. **Context is the scarce resource.** Small index files, progressive disclosure, subagents for codebase exploration (separate context window, summary back). Bloated context measurably degrades model accuracy ("context rot").

---

## 3. Phase 0 — Hardware discovery (RESOLVED — facts recorded)

Detected via dxdiag on 2026-07-19 and confirmed by Lukas. The agent must NOT re-litigate model tier decisions; use these facts:

- **Machine:** Lenovo ThinkPad X1 Carbon Gen 10 (21CBCTO1WW), i7-1260P (12 cores / 16 threads), 16 GB RAM (**soldered — not upgradeable**), Windows 11 currently installed, machine already wiped of work data. Lukas has confirmed it may be repurposed.
- **No dedicated GPU.** Integrated Iris Xe only → **all local inference is CPU-only.** No VRAM tiers apply. The 30B MoE option is dead (requires 32 GB RAM).
- Idle power draw ~5–10 W — cheap and silent as an always-on server.

### Model plan (CPU-only, 16 GB)
| Role | Model (Ollama) | Expected speed | Used for |
|---|---|---|---|
| Workhorse (fast-ish) | Qwen3 4B-class instruct, Q4 (fallback: `phi-4-mini` if structured output/tool calling proves weak) | ~12–20 tok/s | Listing relevance scoring, extraction, dedup — the 90% case |
| Nightly thorough | `qwen3.5:9b` Q4 | ~5–8 tok/s | Nightly triage report, gardener job, deeper batch scoring |

Rules:
- Never run both models simultaneously (RAM headroom for scrapers + system).
- Benchmark both in Phase 2 (tok/s + a 20-listing scoring quality sample) and record results in `workbench-context/STACK.md`. If the 9B model's quality gain doesn't justify its speed on the sample, standardize on the 4B.
- **Hard rule:** slow ≠ acceptable for *development* work. Weak models iterating for hours wander rather than converge. Local models do bounded structured tasks; they never do open-ended development — regardless of harness (this includes OpenCode pointed at Ollama).

---

## 4. Target architecture

```
  [iMac]        [MacBook Pro]        [Phone]
     \                |         (Telegram + Claude app +
      \               |          Termius/SSH as fallback)
       \              |                /
        ────────  Tailscale VPN  ─────────      ← no router port-forwarding,
                       |                           no public exposure
        ┌──────────────┴───────────────────┐
        │  LENOVO — always on, headless     │
        │                                   │
        │  • tmux (persistent sessions)     │
        │  • Claude Code + Codex CLI        │
        │  • Ollama (local models)          │
        │  • Scrapers + cron/systemd timers │
        │  • Small status dashboard (opt.)  │
        └───────┬─────────┬─────────┬───────┘
                │         │         │
           [GitHub]  [Supabase]  [Telegram bot]
           code sync  data/results  pings to Lukas
```

Cloud services (GitHub, Supabase) hold code and data → the laptop is a replaceable worker, **not** a single point of failure for data.

---

## 5. Phase 1 — Base system

On Ubuntu Server:

1. **Users & SSH:** create user `lukas`, key-based SSH only, disable password auth.
2. **Tailscale:** install, `tailscale up`, note the hostname. Lukas installs the Tailscale app on iMac, MacBook, and phone (same tailnet). Optional: enable Tailscale SSH.
3. **mosh:** install (survives network drops — important from the phone).
4. **tmux:** install; create a default session layout (window 1: `claude`, window 2: `codex`, window 3: shell/logs). Add a `~/bin/work` script: `tmux attach -t main || tmux new -s main`.
5. **Always-on power settings:** ignore lid close (`HandleLidSwitch=ignore` in logind.conf), disable suspend targets. If the battery can be charge-limited or removed, prefer that (always-plugged-in batteries swell). Prefer ethernet.
6. **Unattended upgrades** for security patches; **no** automatic reboots during nightly job windows.
7. **Watchdog:** a systemd timer that checks core services (ollama, cron jobs' last-run markers) and sends a Telegram alert on failure.

## Phase 2 — Toolchain

1. Python 3.12 + `uv` (or venv), git, ripgrep.
2. **Ollama:** install, pull models per §3 matrix, verify tokens/sec with a quick benchmark, record results in `workbench-context/STACK.md`.
3. **Claude Code:** install; Lukas logs in with Claude Pro. (The server needs no GPU power for this — Claude Code only makes API calls.)
4. **Codex CLI:** install; Lukas logs in with ChatGPT Plus.
5. **Codex plugin for Claude Code:** install (provides standard review, adversarial review, and handoff-to-Codex slash commands from inside Claude Code).
5b. **Superpowers (methodology layer):** install in BOTH harnesses — Claude Code (`/plugin marketplace add obra/superpowers-marketplace` then `/plugin install superpowers@superpowers-marketplace`) and Codex (via its plugin marketplace). Provides `/brainstorm`, `/write-plan`, `/execute-plan`, enforced TDD (tests must fail first), a four-phase debugging methodology with architectural-review escalation after 3 failed fix attempts (aligns with our retry-cap guardrail), and a built-in code-reviewer agent. Note: it injects context at session start — one more reason to keep our own docs lean.
5c. **Portability note (no action):** OpenCode (open-source, 75+ providers incl. Ollama, AGENTS.md + MCP support, runs Superpowers) is the designated fallback harness if a subscription is dropped or a new provider is trialed. The file contract (task files + AGENTS.md + tests) makes migration cheap by design. Do not install now.
6. **GitHub:** SSH key for the machine; repos are created per project.
7. **Telegram bot:** create via BotFather; store token in `/home/lukas/.secrets/telegram.env`; a tiny `notify.py` helper used by all jobs.
8. **VS Code Remote-SSH** noted for Lukas's Macs as optional editor window onto the laptop.

Secrets policy: all secrets in `~/.secrets/` and per-repo `.env` (git-ignored). Agents never read or print secret contents.

---

## 6. Repository & markdown architecture (critical — this is the memory system)

Every project repo follows this structure. **One big CLAUDE.md is explicitly rejected** (token cost every session + too generic to help — "context rot"). Instead: progressive disclosure — a small index that routes to topic docs loaded only when needed.

```
project/
├── CLAUDE.md              ← index + contract, max ~80 lines
├── AGENTS.md              ← symlink or mirror of CLAUDE.md for Codex
├── docs/
│   ├── PROJECT.md         ← goals, success criteria, decision log (permanent)
│   ├── ARCHITECTURE.md    ← components, dataflows, interfaces
│   ├── SETUP.md           ← environment, gotchas, where secrets live
│   └── LEARNINGS.md       ← dated experiences (can expire; date every entry)
├── tasks/                 ← one file per task + done/
├── scrapers/CLAUDE.md     ← child file, auto-loaded when working in that dir
└── tests/                 ← incl. golden-file snapshots for parsers
```

Cross-project layer (shared git repo):

```
workbench-context/
├── PATTERNS.md   ← reusable recipes (curl_cffi chrome-impersonation, Ollama JSON enforcement, Telegram boilerplate)
├── LEARNINGS.md  ← cross-project dated experiences (anti-bot behavior, token-economy tricks)
└── STACK.md      ← standard choices: Supabase, Tailscale hostnames, Python version, preferred libs, model benchmarks
```

Global agent rules live in `~/.claude/CLAUDE.md` (applies to all projects).

### Rules for the docs system
- CLAUDE.md ≤ ~80 lines; any docs file hitting ~200 lines gets split or pruned. Every line must earn its context cost.
- No rules that a linter already enforces (hooks catch those deterministically).
- Distinguish **decisions** ("we chose X because Y" → PROJECT.md, permanent) from **experiences** ("Vinted blocks datacenter IPs" → LEARNINGS.md, dated, can expire).
- **Docs duty:** any change that makes a docs statement false must fix that statement in the same commit. Task template has a mandatory "Docs affected" field; cross-review explicitly checks docs still match code.
- HTML comments in these files are stripped before reaching context — free human-only notes.
- Directory-specific knowledge goes in child CLAUDE.md files (auto-loaded) rather than relying on the routing table.

### Templates

**CLAUDE.md (project index):**

```markdown
# [Project name]

[2–3 lines: what it does, who/what consumes it.]

## Commands
- Test: `pytest -x`
- Lint: `ruff check . --fix`
- Run: `python -m app.main`

## Contract (non-negotiable)
- Run tests + lint BEFORE every commit. NEVER commit on red tests.
- Always work on a branch: `task/<task-file-name>`. Never directly on main.
- Commit after each completed task (atomic — rollback must be one revert).
- NEVER add dependencies without explicit approval from Lukas.
- NEVER touch: `.env`, `infrastructure/`, CI configs, files outside task scope.
- Max 3 attempts on the same failing test → stop, write a note in the task file, move to review queue.
- Definition of done: tests green + lint clean + affected docs updated + task file moved to `tasks/done/`.

## Document routing (read ONLY when needed)
| Working on...                  | Read first                        |
|--------------------------------|-----------------------------------|
| Goals, scope, priorities       | docs/PROJECT.md                   |
| Architecture, dataflow         | docs/ARCHITECTURE.md              |
| Setup, deploy, secrets         | docs/SETUP.md                     |
| Known pitfalls                 | docs/LEARNINGS.md                 |
| Cross-project patterns         | ../workbench-context/PATTERNS.md  |

## Docs duty
Any change that invalidates a docs statement MUST fix it in the same commit.
New permanent decisions → PROJECT.md. New experiences → LEARNINGS.md (dated).
```

**~/.claude/CLAUDE.md (global):**

```markdown
# Global rules (Lukas)

## Working style
- Chat and docs in Danish or English as Lukas writes; code, commits, comments in English.
- Never propose a plan and implement it in the same turn for larger changes — wait for approval.
- Use subagents for codebase exploration; keep the main context for implementation.
- When scope is unclear, ask rather than assume.

## Quality
- Tests are the judge. NEVER report a task complete without a green test run shown in output.
- Trust `git diff` and test results — never your own or another agent's status summaries.
- No rules here that the linter already enforces.

## Safety
- Never read or print `.env` or secret contents.
- No destructive commands (rm -rf, DROP TABLE, force push) without explicit confirmation.

## Structure
- Every repo follows: CLAUDE.md (index) + docs/ + tasks/. Create the structure if missing.
- No work without a task file. Task files follow the template in tasks/.
```

**Task file template** (`tasks/YYYY-MM-DD-short-name.md`):

```markdown
# Task: [short title]

## Goal
[1–3 lines. What is true when this is done?]

## Acceptance criteria
- [ ] [Concrete, testable criterion]
- [ ] Tests green, lint clean
- [ ] Affected docs updated

## Scope
**May change:** [files/dirs]
**Must NOT touch:** [files/dirs]

## Docs affected
[Which docs files must be updated? Write "none" deliberately, never as a default.]

## Size check
[Must fit one focused session, ~30–60 min of agent work. Bigger → split it.]

## Working notes (agent fills in)
[Errors, attempts, decisions made along the way.]
```

**scrapers/CLAUDE.md (child-file example):**

```markdown
# Scraper rules (this directory)

- All HTTP via `curl_cffi` with Chrome impersonation — never raw requests.
- Respect delay configuration in `config.py`. Never hardcode delays.
- New site: write a snapshot test with a golden file in `tests/fixtures/` BEFORE parser logic.
- Parser output is schema-validated before it reaches Supabase.
- On parse failure: log a raw HTML excerpt to `logs/failures/` — never delete existing fixtures.
```

---

## 7. Development workflow (dual-agent)

The interface is one terminal: SSH/mosh into the laptop, `tmux attach`. Sessions live on the server, so any device resumes exactly where the last one left off. From the phone: Telegram for pings, the Claude app for remote Claude Code sessions, Termius+Tailscale as full fallback.

Per feature/change:

1. **Plan (Claude Code, window 1):** Lukas describes the goal. Use Superpowers' `/brainstorm` for fuzzy requirements and `/write-plan` to produce the plan; the output is saved/condensed into `tasks/YYYY-MM-DD-name.md` following our task template (acceptance criteria, scope, docs-affected). Claude explores via subagents, asks clarifying questions, *does not implement.* This is where the expensive deep understanding is paid once.
2. **Build (Codex, window 2):** `/execute-plan` against the task file (or: "Read tasks/…md and implement it fully. Iterate until tests are green."). Codex needs no codebase exploration — the task file is the contract. Superpowers enforces TDD (failing test first); hooks auto-run lint + tests after edits; the agent iterates to green without involving Lukas. Debugging follows Superpowers' root-cause-first methodology; 3 failed fix attempts → escalate to review queue, never grind on.
3. **Cross-review (Claude Code):** review the diff against the task file and docs (or via the Codex plugin's review commands). Cross-model review exists because same-model review is biased toward agreeing with its own decisions. Review explicitly checks: does the diff match the spec, and do docs still match the code?
4. **Gates:** GitHub Actions runs the test suite on push as a safety net; Codex automatic PR review (included in Plus) as a second net.
5. **Human acceptance (Lukas):** only when everything is green and reviewed does Lukas get a Telegram ping. His job: does the solution actually work satisfactorily in practice (e.g., are the flagged listings genuinely relevant)? ~10 minutes, never debugging.

### Hooks to configure in Claude Code / Codex
- Post-edit: run `ruff` + `pytest -x` automatically.
- Stop-conditions: same test failing 3× → halt, write note, notify review queue (circuit breaker).
- Pre-commit (git hook, tool-agnostic): block commits with failing tests, block edits to protected paths, block new entries in dependency files unless task file contains an approval marker.

---

## 8. Runtime operations (the 24/7 part — zero cloud tokens)

All scheduled via cron/systemd timers:

1. **Scraper runs** (per project cadence): fetch → parse → schema-validate → upsert to Supabase (dedup) → local model scores relevance against Lukas's watchlist criteria → matches above threshold → Telegram ping with link + price + score reasoning (1 line).
2. **Nightly triage (local model):** summarize the day's logs and failures into ONE short status report. If anything broke, the report is the prepared brief for the next Claude Code session — Claude reads a summary, not raw logs (this is where Claude Code tokens usually go: context reading and iteration).
3. **Nightly canary (local model):** sanity-check that scrapers still return plausible data (sites change; hobby scrapers die silently). Freshness + volume + schema drift checks; alert on anomaly.
4. **Weekly gardener (local model, Sunday night):** input = week's `git log --stat` + docs contents. Output = JSON findings of docs statements likely invalidated by the week's changes. It only points; Claude Code or Lukas curates the fixes. Prompt:

```
You are a documentation gardener. You receive (1) this week's git commits with
file names and (2) the contents of the docs files in this repo.

Task: Find statements in docs that have likely become false due to this week's
changes. Report ONLY likely mismatches — never fix anything yourself.

Respond exclusively with JSON matching this schema:
{"findings": [{"file": "...", "statement": "...", "reason": "...", "confidence": "high|medium|low"}]}

No findings → {"findings": []}. No text outside the JSON.
```

5. **(Optional, if MoE tier available):** deeper nightly batch — richer per-listing summaries, weekly market digests (e.g., used-car price trends) as slow background jobs.

### Local model output contract (applies to ALL local-model jobs)
- Request JSON with Ollama's structured-output/schema enforcement.
- Validate at the boundary: schema check + sanity checks; invalid → quarantine + log, never silently pass.
- Weekly human spot-check of ~10 random scored items to calibrate thresholds.

---

## 9. Project roadmap (order of implementation)

1. **Project 1 — used-goods tracker (DBA + Vinted):** first real pipeline; template for everything else. Reuses Lukas's earlier zero-API-cost workbench concept, now with local-model scoring instead of cloud calls. Deliverables: watchlist config, scrapers, scoring, Telegram alerts, snapshot tests, canary.
2. **Project 2 — used-car data (Bilbasen/DBA):** clone of project 1's skeleton with car-specific extraction schema; later analysis/digests as nightly MoE jobs if hardware allows.
3. **Erhvervsklubben:** remains on its existing Supabase + Claude architecture. Only integration point: the same Telegram bot may deliver its notifications.

## 10. Setup phases & acceptance checks

| Phase | Deliverable | Acceptance check (deterministic) |
|---|---|---|
| 0 | ~~Hardware report + model choice~~ **RESOLVED** — facts in §3 | Done 2026-07-19 (X1 Carbon Gen 10, CPU-only, 4B/9B tier) |
| 1 | Ubuntu headless, Tailscale, mosh, tmux, power config, watchdog | SSH from Mac via tailnet works; lid closed → still reachable; watchdog test alert received |
| 2 | Ollama + models (incl. 4B vs 9B benchmark), Claude Code, Codex, Codex plugin, Superpowers in both harnesses, GitHub, Telegram bot | Benchmarks logged in STACK.md; both CLIs authenticated; `/write-plan` available in both; test ping received on phone |
| 3 | workbench-context repo + first project repo with full markdown architecture, hooks, CI | Repo passes a dry-run task through the full workflow (plan → build → cross-review → green) |
| 4 | Project 1 live: scrapers + scoring + alerts + nightly triage/canary | 48h unattended run; ≥1 real relevant alert; canary and triage reports arrive |
| 5 | Gardener job + weekly spot-check routine | First Sunday report received; findings format validates |

## 11. Open questions for Lukas (agent must ask before relevant phase)

1. ~~Wipe approval~~ and ~~hardware figures~~ — RESOLVED, see §3.
2. Watchlist criteria for project 1 (categories, brands, price ranges, locations). [Phase 4]
3. ~~Telegram vs. another notification channel preference~~ **RESOLVED 2026-07-22** — Telegram. Single helper `~/bin/notify.py` (stdlib only) for both Python jobs and shell/cron callers, reading `~/.secrets/telegram.env`.
4. ~~Where the laptop physically lives~~ **RESOLVED 2026-07-22** — home, Wi-Fi only (`wlp0s20f3`, no ethernet). Consequences: Wi-Fi power save disabled via systemd unit; watchdog retries before declaring the network down.
