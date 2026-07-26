# Task: CI so tests judge every push, not just the 30-minute timer

## Goal
Spec §7.4 requires "GitHub Actions runs the test suite on push as a safety
net". The repo has no `.github/` directory at all. Today the only thing running
the suite is `workbench-status.timer` on the box — so a push from a cloud
session is unjudged until lenovo happens to notice, and a push made while the
box is off is never judged at all.

This is also the free half of "keep iterating testing for a long time": CI
costs no cloud tokens and runs forever.

## Acceptance criteria
- [x] `.github/workflows/tests.yml` runs the suite on push and pull_request
- [x] `shellcheck` runs over `bin/*.sh` and `setup/*.sh`
- [x] No third-party actions — first-party `actions/checkout` and
      `actions/setup-python` only (`CLAUDE.md:26`)
- [x] Green on this branch
- [x] Tests green locally

## Scope
**May change:** `.github/`, `CLAUDE.md` (commands table)
**Must NOT touch:** `pyproject.toml` — adding dependencies needs approval

## Why plain pip rather than uv
`astral-sh/setup-uv` is a third-party action, and a third-party action is a
dependency under `CLAUDE.md:26`. `pyproject.toml:6` declares
`dependencies = []` and the only dev dependency is pytest, so
`pip install pytest` needs nothing new. The box keeps using `uv` locally; CI
does not need to match the local runner to be a useful judge.

## Do not enable branch protection
Requiring this check before merge would block `bin/publish-status.sh`, which
amends and force-pushes `STATUS.md` to `main` every 30 minutes. Flagged here
so nobody enables it later while "hardening CI".

## Docs affected
`CLAUDE.md` — nothing to change; the test command is already documented.

## Size check
One workflow file.

## Working notes (agent fills in)
- Verified before pushing rather than after: shellcheck clean over all five
  scripts, and the suite re-run in a CI-like environment (plain venv, no uv on
  PATH, minimal PATH) to confirm nothing depends on the box's toolchain.
- Two jobs rather than one so a shell-lint failure and a test failure are
  distinguishable at a glance on the phone.
