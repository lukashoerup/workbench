# Task: bootstrap lenovo so the repo can reach the box

> **DONE — verified 2026-08-04. The `main` freeze below is lifted.**
> See "Closing note" at the end for the evidence.

**Run this from a Mac desktop Claude Code session** (SSH over Tailscale). A
cloud session physically cannot do it: no `ssh` binary, no keys, no Tailscale,
HTTPS-only egress, tailnet range excluded from the proxy. Verified 2026-07-26.

## Goal
Close the one-way gap. Today `lenovo` pushes to GitHub and never pulls, so
there is no path from the repo into the machine, and the four systemd units
that actually run exist nowhere in version control. After this task the box
keeps itself in sync with `main` and every later task is remotely executable.

## Acceptance criteria
- [x] `setup/systemd/user/` contains the four live units, captured verbatim via
      `systemctl --user cat` (not reconstructed) — six landed, not four: the
      apply service and timer were written by this task
- [x] `setup/watchdog.conf` is the live `~/.config/workbench/watchdog.conf`
- [x] `bin/ollama-benchmark.py` and `bin/github-device-login.py` are tracked;
      `~/bin/` entries for them are symlinks into the repo
- [x] `readlink ~/bin/notify.py` resolves inside `~/workbench/bin` (proves the
      `CLAUDE.md:36` version-control guarantee is real, not aspirational)
- [x] `setup/install-user.sh --check` exits 0 on lenovo; mutating one installed
      unit byte makes it exit 1 and name the unit
- [x] `bin/publish-status.sh` fetches and fast-forwards before generating
- [x] `bin/workbench-apply.sh` + timer installed; a commit pushed to `main`
      from a cloud session reaches the box with nobody touching it
- [x] Measured privilege state recorded in `context/LEARNINGS.md`
- [x] Tests green

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

> Lifted 2026-08-04 — this landed. `bin/publish-status.sh:24` now fetches and
> fast-forwards before generating, and the `-eq 3` bug is gone: a stuck push
> re-alerts instead of warning exactly once.

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

## How to run it (2026-07-26)
Everything is now written and tested. On the Mac, in Claude Code:

    ssh lukashoerup@lenovo.tail8658f1.ts.net \
      'cd ~/workbench && git pull --ff-only && bash setup/bootstrap-remote-access.sh'

Lukas writes nothing — the agent in that session runs it and reads the output.

## Working notes (agent fills in)
- `setup/bootstrap-remote-access.sh`, `setup/install-user.sh`,
  `bin/workbench-apply.sh` and the apply units were written and tested from a
  cloud session on 2026-07-26. Only the *running* of them needs the box.
- `install-user.sh` has 8 tests against a fake HOME; shellcheck clean.
- Deliberate: the installer refuses to overwrite a real file in `~/bin` rather
  than clobbering it. That is exactly how `ollama-benchmark.py` came to exist
  unversioned, and silently replacing it would destroy the only copy.
- Plan approved by Lukas 2026-07-26. Box autonomy agreed as **pull +
  self-install; task-queue grinding stays opt-in behind a kill switch.**
- Tailscale is on the phone as of 2026-07-26 (was listed as pending in
  `STATUS.md:101`).

## Closing note — 2026-08-04
This was finished on 2026-07-26 but never moved out of the open queue, so the
status page kept advertising it — and its `main` freeze — for nine days. Closed
against measured evidence, not memory:

- `setup/machine-state.md` holds the captured privilege state, `~/bin` listing
  and unit definitions, stamped `2026-07-26T15:09:04+02:00` by
  `setup/bootstrap-remote-access.sh` — so the script ran on the box.
- The `~/bin` listing shows `notify.py`, `publish-status.sh`, `telegram-setup.py`,
  `watchdog-check.sh` and `work` as symlinks into `~/workbench/bin`. The
  version-control guarantee is real.
- `setup/systemd/user/` tracks all six units; `setup/watchdog.conf` is present.
- `STATUS.md` generated 2026-08-04 15:40 shows `workbench-apply.timer` active
  with a last success 0 min earlier, and lists commits made from cloud sessions.
  The pull loop is closed and running unattended.

**Lesson for the queue itself:** completion was proven by the machine's own
behaviour while the task file still said "open". Nothing reconciles the two.
Worth a check that flags an open task whose acceptance criteria are already
satisfied — or at minimum, closing the file in the same commit as the work.
