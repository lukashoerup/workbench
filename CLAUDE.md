# Workbench

Project coordination for Lukas. Current code provides Lenovo notifications,
watchdog, status publishing and setup. The phone-first, interchangeable-agent
target and its unverified integrations are in `docs/workbench-direction.md`.

## Read this first if you are answering "what is going on?"

**[STATUS.md](STATUS.md)** — regenerated every 30 minutes by the machine itself
and pushed here. It leads with anything that needs a human, then repo and test
state, scheduled jobs, and machine health. It is measured at generation time,
never remembered.

If STATUS.md's timestamp is more than an hour old, the box is offline or the
publisher is broken — say so rather than reporting its contents as current.

## Commands
- Test: `uv run pytest tests/ -o addopts=""`
- Status now: `python3 bin/workbench-status.py --quick`
- Publish now: `bin/publish-status.sh`

## Contract (non-negotiable)
- Run tests BEFORE every commit. NEVER commit on red tests.
- Always work on a branch: `task/<task-file-name>`. Never directly on main.
- Commit after each completed task (atomic — rollback must be one revert).
- NEVER add dependencies without explicit approval from Lukas.
- NEVER touch: `~/.secrets/`, `.env`, anything under `/etc`.
- Max 3 attempts on the same failing test → stop, write a note in the task file,
  move to the review queue.
- Definition of done: tests green + affected docs updated + task file moved to
  `tasks/done/`.

## Layout
| Path | What |
|---|---|
| `bin/` | The tooling. `~/bin` symlinks here, so edits are version-controlled. |
| `tests/` | pytest. Bash scripts are driven as subprocesses with a fake `HOME`. |
| `setup/` | Privileged setup scripts. Idempotent; safe to re-run. |
| `workbench-setup-spec.md` | The original build spec. Sections are cited as §N. |

## Document routing (read ONLY when needed)
| Working on... | Read first |
|---|---|
| Shared workflow and product direction | `docs/WORKBENCH.md`, `docs/workbench-direction.md` |
| The whole system, what runs where | `SYSTEM.md` |
| What the machine is doing right now | `STATUS.md` |
| The Claude Project setup (claude.ai) | `docs/claude-project-instructions.md` |
| Standard choices, model benchmarks | `context/STACK.md` |
| Reusable recipes | `context/PATTERNS.md` |
| Dated gotchas | `context/LEARNINGS.md` |
| Why the setup is shaped this way | `workbench-setup-spec.md` |

## How Lukas reaches this system
| From | Path | Role |
|---|---|---|
| Claude app (phone/desktop), "Workbench HQ" Project | Chat + dispatch cloud sessions on the GitHub repos | **Primary interface.** Decisions get committed to task files. |
| GitHub app | STATUS.md, docs, diffs, PRs — rendered | Review surface. |
| Telegram, via `bin/notify.py` | Push: alerts, summaries, blocked questions | The machine's voice. |
| SSH over Tailscale → `work` (tmux) | Full shell on `lenovo` | Emergency fallback only — day-to-day work never needs it. |

## Talking to Lukas (agreed 2026-07-26)
He does not program, so an update he cannot read is not an update.
**In chat: plain language** — no file paths, no jargon, no code.
**In the repo: technical as usual** — docs, commits and task files need the
precision; the split is by channel, not a lowering of standards.
**Interrupt him** for money, security, access, taste or operational changes;
also for useful reflection under `docs/WORKBENCH.md`, respecting its limits.

## Code Review Rules
- Read `docs/WORKBENCH.md` before substantial work; initiate independent review.
- Check goal fit and needless complexity as well as correctness; cite evidence.
- Flag data loss, unintended publication, or healthy claims without measurements.
- Missing or stale independent review is pending, never approval.

## Docs duty
Any change that invalidates a docs statement MUST fix it in the same commit.
New permanent decisions → `context/STACK.md`.
New dated experiences → `context/LEARNINGS.md`.
