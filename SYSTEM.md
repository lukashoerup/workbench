# System map

Read this if you are a Claude (phone app, cloud session, any machine) meeting
this system for the first time. It is the half-page version of everything.
Owner: Lukas (Copenhagen). Hobby projects, optimized for minimal human time.

## What runs where

| Piece | Role |
|---|---|
| `lenovo` (always-on Ubuntu box) | The ops box, **never a workspace**: scheduled jobs, watchdog, STATUS.md publisher, local LLM (Ollama). Nobody logs in day-to-day. |
| GitHub (`lukashoerup/*`) | **Single source of truth** for all code, docs, tasks, decisions. The shared memory between every Claude and every device. |
| Anthropic cloud (dispatched sessions) | Repo work while Lukas's Macs are off: dispatch from phone/desktop, results return as commits/PRs. |
| Macs (desktop app / VS Code) | Optional interactive dev. Nothing depends on them being on. |
| Phone (Claude app, GitHub app, Telegram) | Where Lukas monitors and decides. |
| Supabase | Project data (erhvervsklubben). Prod is sacred; staging is disposable. |

## The three channels

- **PUSH — Telegram** (`bin/notify.py`): the machine interrupts Lukas only when
  something needs him: work-block summaries, blocked questions, watchdog alerts.
- **PULL — GitHub**: Lukas reads everything rendered on his phone. Live state:
  `workbench/STATUS.md`, regenerated every 30 min. Timestamp >1h old ⇒ the box
  is offline — say so, don't report stale contents as current.
- **STEER — Claude app / cloud sessions**: two-way. Decisions made in chat
  **must be committed to the relevant task file** — agents on other machines
  read the repo, not the chat.

## How agent work happens (three session types)

1. **Cloud dispatch** — Lukas sends one message from anywhere; the session runs
   in Anthropic's cloud on the GitHub repo; CI judges; Lukas skims the PR.
2. **Lenovo work blocks** *(deferred 2026-07-24)* — headless queue-grinding on
   this box. Deferred because cloud dispatch covers the need on the same token
   budget; revisit only if a real gap shows (local-stack-only work, or wanting
   one batched summary instead of per-task dispatches).
3. **Interactive** — Mac desktop app or VS Code Remote-SSH, when Lukas sits down.

## Autonomy boundary (agreed 2026-07-24)

Agents **proceed without asking** on: anything inside an approved plan/task
file, expanding agreed test suites, building pages per reviewed spec, fixing
red tests, updating docs.
Agents **always stop and ask** before: schema or RLS changes, new dependencies,
deploys, cutover, anything touching prod data or secrets.
Blocked on a decision? Park it — write the question into the task file, push,
Telegram-ping with the GitHub link, and continue with unblocked work. Lukas
answers via the Claude app; the answer is committed back to the task file.

## Repos

| Repo | What |
|---|---|
| `workbench` | This repo: machine tooling, STATUS.md, setup scripts, and cross-project knowledge in `context/` (STACK / PATTERNS / LEARNINGS). |
| `erhvervsklubben` | Active project: members-site rebuild (React + Supabase). |

## Rules for any Claude reading this

- Fetch, don't guess: status questions → read `STATUS.md`; project questions →
  read that repo's `CLAUDE.md`, then only the docs its routing table points to.
- Tests and `git diff` are the judge — never an agent's self-report.
- Every repo follows: `CLAUDE.md` (index) + `docs/` + `tasks/`. No work without
  a task file; work on a branch; never commit on red tests.
- Long-form output for Lukas goes into markdown files in the repo, not chat —
  chat scrollback gets lost; rendered files on GitHub don't.
