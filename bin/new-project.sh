#!/usr/bin/env bash
# Create a project repo with the full markdown architecture from spec §6.
#
#   new-project.sh <name> "<one-line description>"
#
# Produces CLAUDE.md (index, ≤80 lines), AGENTS.md symlinked to it for Codex,
# docs/, tasks/ with the template, tests/, and a pre-commit hook that enforces
# the contract. Idempotent — refuses to clobber an existing directory.
set -euo pipefail

NAME="${1:-}"
DESC="${2:-}"
ROOT="$HOME/projects/${NAME}"

[ -n "$NAME" ] || { echo "usage: new-project.sh <name> \"<description>\"" >&2; exit 1; }
[ -e "$ROOT" ] && { echo "$ROOT already exists" >&2; exit 1; }

mkdir -p "$ROOT"/{docs,tasks/done,tests/fixtures,scrapers}
cd "$ROOT"

cat >CLAUDE.md <<EOF
# ${NAME}

${DESC:-[What it does, who/what consumes it.]}

## Commands
- Test: \`uv run pytest -x\`
- Lint: \`uv run ruff check . --fix\`
- Run:  \`uv run python -m app.main\`

## Contract (non-negotiable)
- Run tests + lint BEFORE every commit. NEVER commit on red tests.
- Always work on a branch: \`task/<task-file-name>\`. Never directly on main.
- Commit after each completed task (atomic — rollback must be one revert).
- NEVER add dependencies without explicit approval from Lukas.
- NEVER touch: \`.env\`, \`infrastructure/\`, CI configs, files outside task scope.
- Max 3 attempts on the same failing test → stop, write a note in the task file,
  move to review queue.
- Definition of done: tests green + lint clean + affected docs updated + task
  file moved to \`tasks/done/\`.

## Document routing (read ONLY when needed)
| Working on...            | Read first                        |
|--------------------------|-----------------------------------|
| Goals, scope, priorities | docs/PROJECT.md                   |
| Architecture, dataflow   | docs/ARCHITECTURE.md              |
| Setup, deploy, secrets   | docs/SETUP.md                     |
| Known pitfalls           | docs/LEARNINGS.md                 |
| Cross-project patterns   | workbench repo: context/PATTERNS.md |

## Docs duty
Any change that invalidates a docs statement MUST fix it in the same commit.
New permanent decisions → PROJECT.md. New experiences → LEARNINGS.md (dated).
EOF

ln -sf CLAUDE.md AGENTS.md

cat >docs/PROJECT.md <<EOF
# ${NAME} — goals and decisions

## What this is
${DESC}

## Success criteria
- [ ] [What must be true for this to be worth running?]

## Decision log
Permanent decisions only — "we chose X because Y". Experiences go in LEARNINGS.md.

### $(date +%F) — Project created
Skeleton from spec §6.
EOF

cat >docs/ARCHITECTURE.md <<'EOF'
# Architecture

## Components
[What runs, and where.]

## Dataflow
[fetch → parse → validate → upsert → score → alert]

## Interfaces
[Schemas at each boundary. Local-model output is UNTRUSTED: schema-enforced
JSON, then validated — schema check + sanity check. Invalid → quarantine + log,
never silently pass.]
EOF

cat >docs/SETUP.md <<'EOF'
# Setup

## Environment
`uv sync` — Python 3.12.

## Secrets
Live in `~/.secrets/`, never in the repo, never printed. See
`~/.secrets/README.md` for what exists and how to rotate it.

## Scheduled jobs
Registered as systemd user timers. Every job writes a heartbeat marker on
success; add a matching line to `~/.config/workbench/watchdog.conf` or the
watchdog will not notice when it dies.
EOF

cat >docs/LEARNINGS.md <<'EOF'
# Learnings — dated

Experiences, not decisions. These can expire. Date every entry and delete what
stops being true.
EOF

cat >tasks/TEMPLATE.md <<'EOF'
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
[Which docs files must be updated? Write "none" deliberately, never as default.]

## Size check
[Must fit one focused session, ~30–60 min of agent work. Bigger → split it.]

## Working notes (agent fills in)
[Errors, attempts, decisions made along the way.]
EOF

cat >scrapers/CLAUDE.md <<'EOF'
# Scraper rules (this directory)

- All HTTP via `curl_cffi` with Chrome impersonation — never raw requests.
- Respect delay configuration in `config.py`. Never hardcode delays.
- New site: write a snapshot test with a golden file in `tests/fixtures/`
  BEFORE parser logic.
- Parser output is schema-validated before it reaches Supabase.
- On parse failure: log a raw HTML excerpt to `logs/failures/` — never delete
  existing fixtures.
EOF

cat >.gitignore <<'EOF'
__pycache__/
*.pyc
.venv/
.env
logs/
.pytest_cache/
EOF

git init -q
mkdir -p .git/hooks
cat >.git/hooks/pre-commit <<'EOF'
#!/usr/bin/env bash
# Contract enforcement (spec §7). Tool-agnostic — applies to every agent.
set -uo pipefail
fail() { echo "COMMIT BLOCKED: $*" >&2; exit 1; }

staged=$(git diff --cached --name-only)

for p in .env infrastructure/ .github/workflows/; do
    echo "$staged" | grep -q "^${p}" && fail "protected path touched: $p"
done

if echo "$staged" | grep -qE '^(pyproject\.toml|requirements.*\.txt|uv\.lock)$'; then
    grep -rqs "DEPENDENCY APPROVED" tasks/ \
        || fail "dependency file changed with no 'DEPENDENCY APPROVED' marker in any task file"
fi

# Only gate on tests once tests actually exist — an empty tests/ dir makes
# pytest exit 5 ("no tests collected"), which is not a red suite.
if command -v uv >/dev/null && compgen -G "tests/test_*.py" >/dev/null; then
    uv run pytest -x -q || fail "tests are red"
    uv run ruff check . || fail "lint is red"
fi
exit 0
EOF
chmod +x .git/hooks/pre-commit

git add -A
git -c commit.gpgsign=false commit -q -m "Initialise ${NAME} from the spec §6 skeleton

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"

echo "created $ROOT"
echo "  CLAUDE.md + AGENTS.md symlink, docs/, tasks/, tests/, scrapers/"
echo "  pre-commit hook: protected paths, dependency approval, tests, lint"
