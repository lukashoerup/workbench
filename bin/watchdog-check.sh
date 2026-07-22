#!/usr/bin/env bash
# Workbench watchdog (spec §5.7). Reads ~/.config/workbench/watchdog.conf,
# runs each check, and pings Telegram via notify.py on state change.
#
# Alerting is edge-triggered: one message when a check starts failing, one when
# it recovers. A still-failing check re-alerts at most once per COOLDOWN.
# Exit status: 0 = all good, 1 = at least one check failing.
#
#   --test   send a test alert and exit (Phase 1 acceptance check)
set -uo pipefail

CONF="$HOME/.config/workbench/watchdog.conf"
STATE_DIR="$HOME/.local/state/workbench/watchdog"
LOG="$HOME/logs/watchdog.log"
NOTIFY="$HOME/bin/notify.py"
COOLDOWN=21600   # 6h between repeat alerts for a still-failing check

mkdir -p "$STATE_DIR" "$(dirname "$LOG")"

log() { printf '%s\t%s\n' "$(date -Is)" "$*" >>"$LOG"; }

if [ "${1:-}" = "--test" ]; then
    "$NOTIFY" "🧪 Workbench watchdog test alert from $(hostname) at $(date -Is)"
    rc=$?
    log "test alert attempted (notify rc=$rc)"
    if [ $rc -eq 0 ]; then
        echo "Test alert delivered — check your phone."
    else
        echo "Not delivered (rc=$rc). See the last line of ~/logs/notify.log:"
        tail -1 "$HOME/logs/notify.log" 2>/dev/null
        echo "NOCHANNEL means ~/.secrets/telegram.env is missing — run telegram-setup.py."
    fi
    exit $rc
fi

now=$(date +%s)
failures=0

# key -> safe filename
statefile() { printf '%s/%s' "$STATE_DIR" "$(printf '%s' "$1" | tr -c 'A-Za-z0-9._-' '_')"; }

report() {  # report <key> <ok|fail|missing> <human message>
    local key="$1" status="$2" msg="$3"
    local sf; sf="$(statefile "$key")"
    local prev="ok" last=0
    if [ -r "$sf" ]; then read -r prev last <"$sf" 2>/dev/null || true; fi
    : "${prev:=ok}" "${last:=0}"
    # A mangled state file must never wedge a check. Anything non-numeric, or a
    # timestamp from the future (RTC ahead of NTP after a reboot), resets to 0 so
    # the cooldown expires immediately rather than muting this check forever.
    case "$last" in (*[!0-9]*|'') last=0 ;; esac
    [ "$last" -gt "$now" ] && last=0
    [ "$prev" != "ok" ] && [ "$prev" != "fail" ] && prev="ok"

    case "$status" in
        ok)
            if [ "$prev" != "ok" ]; then
                "$NOTIFY" "✅ Recovered on $(hostname): ${msg}"
                log "RECOVERED $key - $msg"
            fi
            printf 'ok %s\n' "$now" >"$sf"
            ;;
        missing)
            log "MISSING $key - $msg"
            printf 'ok %s\n' "$now" >"$sf"
            ;;
        fail)
            failures=$((failures + 1))
            if [ "$prev" = "ok" ] || [ $((now - last)) -ge $COOLDOWN ]; then
                if "$NOTIFY" "⚠️ Watchdog on $(hostname): ${msg}"; then
                    log "ALERT $key - $msg"
                    printf 'fail %s\n' "$now" >"$sf"
                else
                    # Undelivered alert must not start the 6h cooldown, or a
                    # Wi-Fi blip during the alert buries the incident until
                    # morning. Retry on the next tick instead.
                    log "ALERT-UNDELIVERED $key - $msg"
                    printf 'fail %s\n' "$last" >"$sf"
                fi
            else
                log "STILL-FAILING $key - $msg (within cooldown)"
                printf 'fail %s\n' "$last" >"$sf"
            fi
            ;;
    esac
}

check_unit() {  # check_unit <unit> <system|user>
    local unit="$1" scope="${2:-system}" flag=""
    [ "$scope" = "user" ] && flag="--user"
    # shellcheck disable=SC2086
    if ! systemctl $flag list-unit-files "$unit" >/dev/null 2>&1 || \
       [ -z "$(systemctl $flag list-unit-files --no-legend "$unit" 2>/dev/null)" ]; then
        report "unit:$unit" missing "unit $unit not installed yet"
        return
    fi
    # shellcheck disable=SC2086
    if systemctl $flag is-active --quiet "$unit"; then
        report "unit:$unit" ok "$unit is active again"
    else
        local st; st="$(systemctl $flag is-active "$unit" 2>&1)"
        report "unit:$unit" fail "$unit is $st"
    fi
}

check_heartbeat() {  # check_heartbeat <label> <file> <max-age>
    local label="$1" file="$2" max="$3"
    if [ ! -e "$file" ]; then
        report "hb:$label" fail "$label has never run (no marker at $file)"
        return
    fi
    local mtime age
    mtime=$(stat -c %Y "$file" 2>/dev/null || echo 0)
    age=$((now - mtime))
    if [ "$age" -gt "$max" ]; then
        report "hb:$label" fail "$label is stale — last run $((age / 60)) min ago (limit $((max / 60)) min)"
    else
        report "hb:$label" ok "$label is running again"
    fi
}

check_net() {  # check_net <host>
    local host="$1"
    if ping -c 2 -W 5 "$host" >/dev/null 2>&1; then
        report "net:$host" ok "network reachable again ($host)"
    else
        # Wi-Fi only box: nudge the link before declaring it down.
        local iface; iface="$(ip -o -4 route show default 2>/dev/null | awk '{print $5; exit}')"
        sleep 10
        if ping -c 2 -W 5 "$host" >/dev/null 2>&1; then
            report "net:$host" ok "network reachable again ($host)"
        else
            report "net:$host" fail "cannot reach $host (iface=${iface:-none})"
        fi
    fi
}

check_disk() {  # check_disk <mount> <min-free-pct>
    local mount="$1" minfree="$2" usedpct freepct
    usedpct=$(df --output=pcent "$mount" 2>/dev/null | tail -1 | tr -dc '0-9')
    [ -z "$usedpct" ] && { report "disk:$mount" missing "cannot stat $mount"; return; }
    freepct=$((100 - usedpct))
    if [ "$freepct" -lt "$minfree" ]; then
        report "disk:$mount" fail "disk $mount only ${freepct}% free (floor ${minfree}%)"
    else
        report "disk:$mount" ok "disk $mount back above ${minfree}% free"
    fi
}

[ -r "$CONF" ] || { log "no config at $CONF"; exit 0; }

while read -r kind a b c; do
    case "${kind:-}" in
        ''|\#*)     continue ;;
        unit)       check_unit "$a" system ;;
        user)       check_unit "$a" user ;;
        heartbeat)  check_heartbeat "$a" "$b" "$c" ;;
        net)        check_net "$a" ;;
        disk)       check_disk "$a" "$b" ;;
        *)          log "unknown check kind: $kind" ;;
    esac
done < <(grep -v '^[[:space:]]*#' "$CONF")

log "run complete: $failures failing"
[ "$failures" -eq 0 ]
