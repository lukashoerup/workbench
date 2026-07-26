#!/usr/bin/env bash
# Install everything this repo owns into the current user's home. No sudo.
#
# Idempotent by design: workbench-apply.sh runs `--check` every 10 minutes and
# only calls this when something has drifted, so it must be a safe no-op the
# rest of the time.
#
#   install-user.sh           install / repair
#   install-user.sh --check   report drift, exit 1 if anything differs
#
# What it owns:
#   ~/bin/*                        symlinks into this repo, so edits are
#                                  version-controlled (the CLAUDE.md promise)
#   ~/.config/systemd/user/*       timers and services
#   ~/.config/workbench/watchdog.conf   installed only if absent — the live
#                                  file is operational config, never clobbered
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN="$HOME/bin"
UNITS="$HOME/.config/systemd/user"
CONF="$HOME/.config/workbench"

CHECK=0
FORCE=0
for arg in "$@"; do
    case "$arg" in
        --check) CHECK=1 ;;
        --force) FORCE=1 ;;
        *) echo "unknown argument: $arg" >&2; exit 2 ;;
    esac
done

drift=0
note() { echo "$1"; drift=1; }

# ------------------------------------------------------------------ ~/bin
# Symlinks, not copies: a copy silently decouples the box from the repo, so an
# edit made here would never be version-controlled and would die with the disk.
mkdir -p "$BIN"
for src in "$REPO"/bin/*; do
    [ -f "$src" ] || continue
    name="$(basename "$src")"
    dest="$BIN/$name"
    want="$src"

    if [ -L "$dest" ] && [ "$(readlink -f "$dest")" = "$(readlink -f "$want")" ]; then
        continue
    fi
    if [ -e "$dest" ] && [ ! -L "$dest" ] && [ "$FORCE" -eq 0 ]; then
        # A real file here means someone edited the box directly. Refuse rather
        # than overwrite: that file may be the only copy of something.
        # shellcheck disable=SC2088  # display text for a human, not a path to expand
        note "~/bin/$name is a real file, not a symlink — refusing to replace it (use --force)"
        continue
    fi
    # shellcheck disable=SC2088  # display text for a human, not a path to expand
    note "~/bin/$name needs linking"
    [ "$CHECK" -eq 1 ] || ln -sfn "$want" "$dest"
done

# ------------------------------------------------------------- watchdog.conf
mkdir -p "$CONF"
if [ ! -f "$CONF/watchdog.conf" ]; then
    note "watchdog.conf missing"
    [ "$CHECK" -eq 1 ] || cp "$REPO/setup/watchdog.conf" "$CONF/watchdog.conf"
fi

# ------------------------------------------------------------------- units
mkdir -p "$UNITS"
units_changed=0
for src in "$REPO"/setup/systemd/user/*; do
    [ -f "$src" ] || continue
    name="$(basename "$src")"
    dest="$UNITS/$name"
    if ! cmp -s "$src" "$dest"; then
        note "unit $name differs from the repo"
        if [ "$CHECK" -eq 0 ]; then
            cp "$src" "$dest"
            units_changed=1
        fi
    fi
done

if [ "$CHECK" -eq 1 ]; then
    [ "$drift" -eq 0 ] && echo "in sync"
    exit "$drift"
fi

# systemctl is absent in CI containers and in tests. Installing the files is
# still useful there, so warn rather than fail.
if ! command -v systemctl >/dev/null 2>&1 || ! systemctl --user show-environment >/dev/null 2>&1; then
    echo "systemd --user unavailable — files installed, timers not started" >&2
    exit 0
fi

[ "$units_changed" -eq 1 ] && systemctl --user daemon-reload
for src in "$REPO"/setup/systemd/user/*.timer; do
    [ -f "$src" ] || continue
    systemctl --user enable --now "$(basename "$src")" >/dev/null 2>&1 \
        || echo "could not enable $(basename "$src")" >&2
done

echo "installed"
