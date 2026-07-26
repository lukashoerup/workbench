#!/usr/bin/env bash
# Run ONCE on `lenovo`. After this, the box keeps itself in sync with GitHub and
# nobody needs a terminal on it again.
#
# Why this exists: the machine only ever pushed to GitHub, never pulled. So
# there was no way for anything in the repo to reach it — every change needed a
# human at a shell. This script closes that loop, and captures the pieces of the
# machine that exist nowhere else before a disk failure takes them.
#
# Safe to re-run. It changes nothing it does not have to.
#
#   bash ~/workbench/setup/bootstrap-remote-access.sh
set -uo pipefail

REPO="$HOME/workbench"
NOTIFY="$HOME/bin/notify.py"
REPORT="$REPO/setup/machine-state.md"

say() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }
warn() { printf '  !! %s\n' "$*"; }
ok() { printf '  ok %s\n' "$*"; }

cd "$REPO" || { echo "No repo at $REPO — is this lenovo?"; exit 1; }

say "0. Sync with GitHub"
git fetch -q origin main || { echo "Cannot reach GitHub. Check the network and re-run."; exit 1; }
if git merge-base --is-ancestor HEAD origin/main; then
    git merge -q --ff-only origin/main && ok "fast-forwarded to $(git rev-parse --short HEAD)"
else
    extra=$(git log --pretty=%s origin/main..HEAD)
    if [ -n "$extra" ] && ! grep -qv '^Status: ' <<<"$extra"; then
        git reset -q --hard origin/main
        ok "discarded disposable status commits, now at $(git rev-parse --short HEAD)"
    elif [ -n "$extra" ]; then
        warn "this clone holds local commits that are not on GitHub:"
        git log --oneline origin/main..HEAD | sed 's/^/     /'
        warn "not discarding them. Push or drop them, then re-run."
        exit 1
    fi
fi

# ---------------------------------------------------------------------------
say "1. Capture the systemd units that exist only on this machine"
mkdir -p setup/systemd/user
captured=0
for unit in workbench-status.service workbench-status.timer \
            workbench-watchdog.service workbench-watchdog.timer; do
    if systemctl --user cat "$unit" >/dev/null 2>&1; then
        # `systemctl cat` prefixes each file with a "# /path" comment line.
        systemctl --user cat "$unit" | sed '/^# \//d' >"setup/systemd/user/$unit"
        ok "captured $unit"
        captured=$((captured + 1))
    else
        warn "$unit is not installed on this machine"
    fi
done
[ "$captured" -eq 0 ] && warn "captured nothing — are the timers installed under a different name?"

# ---------------------------------------------------------------------------
say "2. Capture the live watchdog checklist"
LIVE_CONF="$HOME/.config/workbench/watchdog.conf"
if [ -f "$LIVE_CONF" ]; then
    if cmp -s "$LIVE_CONF" setup/watchdog.conf; then
        ok "watchdog.conf already matches the repo"
    else
        # The live file decides what gets noticed at 04:00. It wins.
        cp "$LIVE_CONF" setup/watchdog.conf
        ok "captured the live watchdog.conf (it differed from the repo)"
    fi
else
    warn "no live watchdog.conf — the repo copy will be installed"
fi

# ---------------------------------------------------------------------------
say "3. Recover scripts that live only in ~/bin"
# CLAUDE.md promises "~/bin symlinks here, so edits are version-controlled".
# Any real file in ~/bin is a script that would die with this disk.
recovered=0
for f in "$HOME"/bin/*; do
    # -f follows symlinks, so check -L second to let real files through only.
    [ -f "$f" ] || continue
    [ -L "$f" ] && continue
    name="$(basename "$f")"
    if [ ! -e "$REPO/bin/$name" ]; then
        cp "$f" "$REPO/bin/$name"
        chmod +x "$REPO/bin/$name"
        ok "recovered $name into the repo"
        recovered=$((recovered + 1))
    fi
done
[ "$recovered" -eq 0 ] && ok "nothing to recover — ~/bin is already all symlinks"

# ---------------------------------------------------------------------------
say "4. Record what this machine actually looks like"
{
    echo "# Machine state — measured on \`$(hostname)\`"
    echo
    echo "_Captured $(date -Is) by \`setup/bootstrap-remote-access.sh\`._"
    echo "_Measured, not remembered. Re-run the script to refresh._"
    echo
    echo "## Privilege"
    echo
    echo '```'
    echo "sudo -n true => $(sudo -n true 2>/dev/null && echo 'passwordless sudo IS available' || echo 'requires a password')"
    echo "/etc/sudoers.d:"
    # shellcheck disable=SC2012  # a human-readable listing is the point here
    ls -l /etc/sudoers.d/ 2>/dev/null | sed 's/^/  /' || echo "  (not readable)"
    echo '```'
    echo
    echo "## ~/bin"
    echo
    echo '```'
    # shellcheck disable=SC2012  # permissions and link targets are what we want to show
    ls -l "$HOME/bin" | sed 's/^/  /'
    echo '```'
    echo
    echo "## Toolchain"
    echo
    echo "_Resolved by \`bin/workbench-status.py\`, which also republishes this"
    echo "every 30 minutes — so STATUS.md is the current answer, not this file._"
    echo
    echo '```'
    # One implementation, not two. `command -v` alone was the original bug here:
    # this runs over ssh without ~/.local/bin on PATH, so uv reported missing
    # while it was demonstrably running the test suite.
    python3 "$REPO/bin/workbench-status.py" --toolchain 2>/dev/null \
        || echo "(probe failed)"
    echo '```'
    echo
    echo "## Timers"
    echo
    echo '```'
    systemctl --user list-timers --all --no-pager 2>/dev/null | sed 's/^/  /' || echo "  (unavailable)"
    echo '```'
} >"$REPORT"
ok "wrote setup/machine-state.md"

# ---------------------------------------------------------------------------
say "5. Install everything, including the pull agent"
bash "$REPO/setup/install-user.sh" || warn "installer reported a problem — see above"

# ---------------------------------------------------------------------------
say "6. Publish the captured state back to GitHub"
git add -A setup/ bin/
if git diff --cached --quiet; then
    ok "nothing new to publish — already captured"
else
    git commit -q -m "Capture lenovo's live machine state

Captured by setup/bootstrap-remote-access.sh on the box. The systemd units,
the live watchdog checklist and any ~/bin-only scripts existed nowhere but
this disk; they are now version-controlled and a rebuild can restore them."
    if git push -q origin HEAD; then
        ok "pushed $(git rev-parse --short HEAD)"
    else
        warn "push failed — run 'git push origin HEAD' once the network is back"
    fi
fi

# ---------------------------------------------------------------------------
say "Done"
echo
echo "  This machine now pulls from GitHub every 10 minutes and applies what it"
echo "  finds. Changes pushed to main from anywhere reach it without a terminal."
echo
systemctl --user list-timers --all --no-pager 2>/dev/null | head -6

[ -x "$NOTIFY" ] && "$NOTIFY" "✅ lenovo bootstrapped: it now pulls from GitHub every 10 min and applies updates itself. No terminal needed from here on."
exit 0
