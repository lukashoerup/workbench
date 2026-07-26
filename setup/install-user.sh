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

# Drift is fixable by re-running. Blocked needs a human, so the caller must not
# retry it every 10 minutes — workbench-apply.sh keys its alerting on this.
drift=0
blocked=0
note() { echo "$1"; drift=1; }
halt() { echo "$1"; blocked=1; }

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
    if [ -e "$dest" ] && [ ! -L "$dest" ]; then
        if cmp -s "$dest" "$want"; then
            # Byte-identical to the repo copy, so converting it to a symlink
            # loses nothing — and it is what makes edits version-controlled
            # from here on. This is the state the box lands in right after a
            # bootstrap recovers a previously unversioned script.
            # shellcheck disable=SC2088  # display text for a human, not a path to expand
            note "~/bin/$name is a copy of the repo file — converting to a symlink"
            [ "$CHECK" -eq 1 ] || ln -sfn "$want" "$dest"
            continue
        fi
        if [ "$FORCE" -eq 0 ]; then
            # Content differs, so this file holds edits that exist nowhere else.
            # Never overwrite it, and never retry: a human has to reconcile it.
            # shellcheck disable=SC2088  # display text for a human, not a path to expand
            halt "~/bin/$name differs from the repo copy — it holds unversioned edits. Reconcile it, or re-run with --force to discard them."
            continue
        fi
    fi
    # shellcheck disable=SC2088  # display text for a human, not a path to expand
    note "~/bin/$name needs linking"
    [ "$CHECK" -eq 1 ] || ln -sfn "$want" "$dest"
done

# ------------------------------------------------------------- watchdog.conf
# Add-only. The live file is operational config and may hold checks someone
# added on the box, so it is never overwritten or pruned — but a check the repo
# declares must reach the machine, otherwise a new job ships with nothing
# watching it and its silent death is invisible.
mkdir -p "$CONF"
LIVE="$CONF/watchdog.conf"
if [ ! -f "$LIVE" ]; then
    note "watchdog.conf missing"
    [ "$CHECK" -eq 1 ] || cp "$REPO/setup/watchdog.conf" "$LIVE"
else
    while IFS= read -r line; do
        case "$line" in ''|\#*) continue ;; esac
        if ! grep -qxF "$line" "$LIVE"; then
            note "watchdog check missing: $line"
            [ "$CHECK" -eq 1 ] || printf '%s\n' "$line" >>"$LIVE"
        fi
    done <"$REPO/setup/watchdog.conf"
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
    # 2 outranks 1: a blocked box needs a human, and the caller must not retry.
    [ "$blocked" -eq 1 ] && exit 2
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

[ "$blocked" -eq 1 ] && { echo "installed, with unresolved items above" >&2; exit 2; }
echo "installed"
