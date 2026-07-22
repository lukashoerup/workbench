#!/usr/bin/env bash
# Phase 1 privileged steps (spec §5). Run once:  sudo bash ~/workbench/setup/phase1-privileged.sh
# Idempotent — safe to re-run. Every change is written as a drop-in file so it
# can be undone by deleting that file.
set -euo pipefail

USER_NAME="lukashoerup"
WIFI_IFACE="wlp0s20f3"

[ "$(id -u)" -eq 0 ] || { echo "run with sudo" >&2; exit 1; }

say() { printf '\n\033[1m==> %s\033[0m\n' "$*"; }

# ----------------------------------------------------------------- 0. timezone
say "Timezone -> Europe/Copenhagen (nightly job windows are local time)"
timedatectl set-timezone Europe/Copenhagen

# ---------------------------------------------------------------- 1. lid/sleep
say "Always-on: ignore lid close, block suspend/hibernate (§5.5)"
install -d /etc/systemd/logind.conf.d
cat >/etc/systemd/logind.conf.d/10-workbench-always-on.conf <<'EOF'
# Headless 24/7 server: the lid is closed permanently, and nothing may suspend it.
[Login]
HandleLidSwitch=ignore
HandleLidSwitchExternalPower=ignore
HandleLidSwitchDocked=ignore
IdleAction=ignore
EOF

systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
systemctl restart systemd-logind    # note: does not drop existing SSH sessions

# ------------------------------------------------------------------ 2. packages
say "Installing mosh, iw, curl (§5.3)"
export DEBIAN_FRONTEND=noninteractive
apt-get update -qq
apt-get install -y -qq mosh iw curl ca-certificates

# ------------------------------------------------------------- 3. wifi powersave
say "Disabling Wi-Fi power save on ${WIFI_IFACE} (home Wi-Fi-only box)"
cat >/etc/systemd/system/wifi-powersave-off.service <<EOF
[Unit]
Description=Disable Wi-Fi power saving on ${WIFI_IFACE}
After=network.target sys-subsystem-net-devices-${WIFI_IFACE}.device
Wants=sys-subsystem-net-devices-${WIFI_IFACE}.device

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/sbin/iw dev ${WIFI_IFACE} set power_save off

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable --now wifi-powersave-off.service || \
    echo "  (non-fatal: power_save may be unsupported by this driver)"

# ------------------------------------------------------------------ 4. tailscale
say "Installing Tailscale (§5.2)"
if ! command -v tailscale >/dev/null; then
    curl -fsSL https://tailscale.com/install.sh | sh
fi
systemctl enable --now tailscaled

# ------------------------------------------------------------------- 5. ssh keys
say "SSH hardening (§5.1)"
KEYS="/home/${USER_NAME}/.ssh/authorized_keys"
if [ -s "$KEYS" ]; then
    cat >/etc/ssh/sshd_config.d/10-workbench.conf <<'EOF'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin no
EOF
    sshd -t && systemctl reload ssh
    echo "  password auth disabled (authorized_keys present)"
else
    echo "  !! NO authorized_keys for ${USER_NAME} — password auth LEFT ON."
    echo "  !! Run from your Mac first:  ssh-copy-id ${USER_NAME}@$(hostname -I | awk '{print $1}')"
    echo "  !! Then re-run this script to lock it down."
fi

# --------------------------------------------------------- 6. user services live
say "Enabling lingering so user timers run without a login session"
loginctl enable-linger "${USER_NAME}"

# ----------------------------------------------------------- 7. no reboot at 03
say "Unattended upgrades: security patches yes, automatic reboots no (§5.6)"
cat >/etc/apt/apt.conf.d/52workbench-no-reboot <<'EOF'
// Nightly job window must never be interrupted by an automatic reboot.
Unattended-Upgrade::Automatic-Reboot "false";
EOF

say "Done. Now, as ${USER_NAME}, run:  sudo tailscale up"
