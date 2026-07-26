# Task: make the box's own facts trustworthy and self-publishing

## Goal
The bootstrap's machine report says `uv: NOT INSTALLED`. It is installed —
`context/STACK.md:17` records it at `~/.local/bin/uv`,
`bin/workbench-status.py:64` runs it by that absolute path, and the published
STATUS.md reports 83 tests actually running. The probe used `command -v`, and
an `ssh` non-login shell has no `~/.local/bin` on its `PATH`.

That is not a cosmetic bug. The same probe reports `claude: NOT INSTALLED`, and
that reading is what decides whether the overnight worker is possible at all.
It is unreliable in the one place it is load-bearing.

Second half of the goal: this information should not live in a file that only a
manual bootstrap can refresh. Folded into STATUS.md it rides the publishing
path that already works, so "what is installed on the box" is never more than
30 minutes stale and never needs a shell again.

## Acceptance criteria
- [x] Toolchain probe resolves known install locations, not just `PATH`:
      `~/.local/bin`, `~/.npm-global/bin`, `~/bin`, `/usr/local/bin`, `/usr/bin`,
      and `npm prefix -g` when npm exists
- [x] It reports the resolved path, or a genuine absence
- [x] The result appears in STATUS.md's `Machine` section, so it is republished
      every 30 minutes
- [x] `setup/bootstrap-remote-access.sh` uses the same logic (no second
      implementation that can drift from the first)
- [x] Commit times render in one timezone and therefore read in order
- [x] `context/LEARNINGS.md` states the measured privilege state
- [x] Tests green, shellcheck clean

## Scope
**May change:** `bin/workbench-status.py`, `setup/bootstrap-remote-access.sh`,
`context/LEARNINGS.md`, `tests/`
**Must NOT touch:** `/etc` or any sudoers file — the grant stays as measured;
this task only records the truth (Lukas's decision 2026-07-26)

## Detail
1. **The probe.** A shared helper that checks `PATH` first, then the known
   locations above. Absence must mean absence, not "not on this shell's PATH".
2. **Mixed timezones.** `bin/workbench-status.py:83-86` uses `--date=format:`,
   which renders each commit in *its own* zone. Commits authored in a cloud
   container are UTC while the box is CEST, so the published list currently
   reads `13:15, 13:12, 15:09, 13:05` — out of order on a phone.
   `--date=format-local:` renders everything in the box's zone. Same family as
   the `%ad`/`%cd` bug fixed earlier today.
3. **Sudo.** Measured 2026-07-26: `sudo -n true` succeeds; both
   `/etc/sudoers.d/50-workbench-agent` (scoped) and `90-agent-nopasswd`
   (blanket) exist, so the blanket grant is in force and the scoped one is
   redundant while it is. `context/LEARNINGS.md` asserts the opposite today, and
   per its own rule at `:5` the false entry must be deleted rather than
   softened — an agent reading it would wrongly conclude it cannot install
   anything.

## Docs affected
`context/LEARNINGS.md` (privilege), `context/STACK.md` if the toolchain section
belongs there too.

## Size check
Three small changes plus tests.

## Working notes (agent fills in)
- Proven rather than assumed: with `PATH=/usr/bin:/bin`, `command -v uv` fails
  while the new probe resolves `~/.local/bin/uv`. That is exactly the false
  negative the box reported.
- One implementation, not two: the bootstrap now calls
  `workbench-status.py --toolchain` instead of keeping its own copy that could
  drift.
- Folded into STATUS.md's Machine section, so the answer to "what is installed"
  is republished every 30 minutes and never needs a shell again.
- The privilege question is settled by measurement, not inference: both sudoers
  files exist and the blanket one wins.
- Tests 83 -> 87.
