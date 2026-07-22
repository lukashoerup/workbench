#!/usr/bin/env bash
# Grant the agent scoped passwordless sudo, so package installs and service
# management stop needing Lukas in the chair.  Run once:
#
#   sudo bash ~/workbench/setup/allow-agent-installs.sh
#
# This is deliberately NOT blanket root. It covers package management, systemd,
# and the timedate/logind knobs an agent legitimately needs during setup.
# Notably absent: passwd/usermod/visudo/su, arbitrary shells, and dd/mkfs —
# so a misfiring agent cannot lock you out of your own machine or silently
# widen its own privileges.
#
# To revoke everything:  sudo rm /etc/sudoers.d/50-workbench-agent
set -euo pipefail

USER_NAME="lukashoerup"
DEST="/etc/sudoers.d/50-workbench-agent"

[ "$(id -u)" -eq 0 ] || { echo "run with sudo" >&2; exit 1; }

TMP="$(mktemp)"
trap 'rm -f "$TMP"' EXIT

cat >"$TMP" <<EOF
# Scoped passwordless sudo for coding agents on the workbench.
# Written by ~/workbench/setup/allow-agent-installs.sh — see that file for rationale.

Cmnd_Alias WB_PKG    = /usr/bin/apt-get, /usr/bin/apt, /usr/bin/dpkg, /usr/bin/snap
Cmnd_Alias WB_SVC    = /usr/bin/systemctl, /usr/bin/journalctl, /usr/bin/loginctl
Cmnd_Alias WB_SYS    = /usr/bin/timedatectl, /usr/sbin/iw, /usr/bin/tee /etc/systemd/*, \\
                       /usr/sbin/sshd -t, /usr/bin/netplan
Cmnd_Alias WB_OLLAMA = /usr/local/bin/ollama, /usr/bin/tailscale

${USER_NAME} ALL=(root) NOPASSWD: WB_PKG, WB_SVC, WB_SYS, WB_OLLAMA
EOF

# Never install a sudoers file that does not parse — a broken one locks out sudo
# entirely, and fixing that needs a rescue boot.
if ! visudo -cqf "$TMP"; then
    echo "REFUSING: generated sudoers file failed validation. Nothing changed." >&2
    exit 1
fi

install -m 0440 -o root -g root "$TMP" "$DEST"
visudo -cqf /etc/sudoers >/dev/null && echo "✅ Installed $DEST"

echo
echo "Verifying as ${USER_NAME}:"
sudo -u "${USER_NAME}" sudo -n systemctl is-system-running >/dev/null 2>&1 \
    && echo "   passwordless systemctl works" \
    || echo "   !! verification failed — check $DEST"

echo
echo "Revoke any time with:  sudo rm $DEST"
