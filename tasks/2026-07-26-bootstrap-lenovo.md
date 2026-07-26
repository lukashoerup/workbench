# Task: bootstrap lenovo so the repo can reach the box

**Run this from a Mac desktop Claude Code session** (SSH over Tailscale). A
cloud session physically cannot do it: no `ssh` binary, no keys, no Tailscale,
HTTPS-only egress, tailnet range excluded from the proxy. Verified 2026-07-26.

## Goal
Close the one-way gap. Today `lenovo` pushes to GitHub and never pulls, so
there is no path from the repo into the machine, and the four systemd units
that actually run exist nowhere in version control. After this task the box
keeps itself in sync with `main` and every later task is remotely executable.

## Acceptance criteria
- [ ] `setup/systemd/user/` contains the four live units, captured verbatim via
      `systemctl --user cat` (not reconstructed)
- [ ] `setup/watchdog.conf` is the live `~/.config/workbench/watchdog.conf`
- [ ] `bin/ollama-benchmark.py` and `bin/github-device-login.py` are tracked;
      `~/bin/` entries for them are symlinks into the repo
- [ ] `readlink ~/bin/notify.py` resolves inside `~/workbench/bin` (proves the
      `CLAUDE.md:36` version-control guarantee is real, not aspirational)
- [ ] `setup/install-user.sh --check` exits 0 on lenovo; mutating one installed
      unit byte makes it exit 1 and name the unit
- [ ] `bin/publish-status.sh` fetches and fast-forwards before generating
- [ ] `bin/workbench-apply.sh` + timer installed; a commit pushed to `main`
      from a cloud session reaches the box with nobody touching it
- [ ] Measured privilege state recorded in `context/LEARNINGS.md`
- [ ] Tests green

## Scope
**May change:** `setup/`, `bin/publish-status.sh`, `bin/workbench-apply.sh`,
`context/LEARNINGS.md`, `context/STACK.md`, `tests/`
**Must NOT touch:** `/etc` or any sudoers file — privilege state is *measured
and documented only* (`CLAUDE.md:27`). Changing `AGENT_SUDO` is a separate
task needing Lukas's approval.

## Why the pull step is urgent, not cosmetic
`bin/publish-status.sh:44-50` amends the status commit and pushes with
`--force-with-lease`. The moment `main` on GitHub moves ahead of lenovo's stale
clone, the lease check fails and the push is rejected. Because of the `:62`
`-eq 3` bug, Lukas gets **exactly one** Telegram warning ever, after which
STATUS.md silently freezes while still looking fine on the phone.

**Consequence: do not merge any other branch to `main` until this lands.**
Feature branches are safe; `main` is not.

## What only the box knows
There is no other copy of these anywhere — not in the repo, not in git history
(verified across all 30 paths ever tracked):
- the four unit definitions
- `~/.config/workbench/watchdog.conf`
- `~/bin/ollama-benchmark.py`, `~/bin/github-device-login.py`
- whether `~/bin/*` are symlinks or copies
- actual sudoers state (`sudo -n true`; `ls -l /etc/sudoers.d/`) — the repo
  contains two mutually contradictory claims, see `context/LEARNINGS.md:26-29`
  versus `setup/phase1-privileged.sh:120-122`
- whether Claude Code is installed and authenticated (gates the dispatcher)

Capture, do not reconstruct: where the repo and the box disagree, **the box
wins** — it is the thing that demonstrably works.

## Docs affected
`context/LEARNINGS.md` (privilege state, symlink finding), `context/STACK.md`
(scheduled-jobs table), `CLAUDE.md` layout table if `setup/` gains directories.

## Size check
One session with shell on the box. Capture is quick; `install-user.sh` and
`workbench-apply.sh` are the real work.

## Working notes (agent fills in)
- Plan approved by Lukas 2026-07-26. Box autonomy agreed as **pull +
  self-install; task-queue grinding stays opt-in behind a kill switch.**
- Tailscale is on the phone as of 2026-07-26 (was listed as pending in
  `STATUS.md:101`).
