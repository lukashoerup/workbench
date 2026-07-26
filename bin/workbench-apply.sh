#!/usr/bin/env bash
# Pull `main` from GitHub and apply it to this machine.
#
# This is the script that makes remote work possible at all. Before it existed
# the box only ever pushed: nothing in the repo could reach the machine, so
# every change needed a human at a terminal. Now the box reconciles itself to
# the repo on a timer, and a cloud session can change what this machine does by
# pushing a commit.
#
# Deliberately NOT an agent: it pulls and runs the idempotent installer, and
# nothing else. Working the task queue is a separate, opt-in thing behind its
# own kill switch — see SYSTEM.md session type 2.
#
# Run by workbench-apply.timer every 10 min. Safe to run by hand.
set -uo pipefail

REPO="$HOME/workbench"
NOTIFY="$HOME/bin/notify.py"
STATE="$HOME/.local/state/workbench"
HEARTBEAT="$STATE/heartbeats/apply"
FAILS="$STATE/apply-failures"
LOG="$HOME/logs/apply.log"

mkdir -p "$STATE/heartbeats" "$(dirname "$LOG")"
log() { printf '%s\t%s\n' "$(date -Is)" "$*" >>"$LOG"; }

cd "$REPO" || { log "no repo at $REPO"; exit 1; }

if ! git fetch -q origin main 2>/dev/null; then
    # Offline is normal on a Wi-Fi-only box. Count it, but only shout if it
    # persists — the watchdog's heartbeat check covers prolonged silence.
    fails=$(( $(cat "$FAILS" 2>/dev/null || echo 0) + 1 ))
    echo "$fails" >"$FAILS"
    log "fetch failed ($fails consecutive)"
    [ "$fails" -eq 6 ] && "$NOTIFY" "⚠️ lenovo has not reached GitHub in an hour — it is no longer picking up changes."
    exit 1
fi
rm -f "$FAILS"

local_head=$(git rev-parse HEAD)
remote_head=$(git rev-parse origin/main)

if [ "$local_head" != "$remote_head" ]; then
    if git merge-base --is-ancestor HEAD origin/main; then
        # Clean fast-forward: the normal case.
        git merge -q --ff-only origin/main && log "fast-forwarded to ${remote_head:0:8}"
    else
        # Diverged. The only commits this machine creates on its own are status
        # commits, and the status page's *history* is worthless by design — only
        # its current contents matter (publish-status.sh:41-43). So if every
        # local-only commit is a status commit, they are safe to discard and
        # the page regenerates on the next timer.
        #
        # Anything else is real work that only exists here. Never discard that;
        # stop and say so, because a silent reset would destroy it.
        extra=$(git log --pretty=%s origin/main..HEAD)
        if [ -n "$extra" ] && ! grep -qv '^Status: ' <<<"$extra"; then
            git reset -q --hard origin/main
            log "discarded local status commits, reset to ${remote_head:0:8}"
        else
            log "DIVERGED with non-status commits — not touching it"
            "$NOTIFY" "⚠️ lenovo's repo has diverged from GitHub and holds local work I will not discard. It has stopped applying updates until this is resolved."
            exit 1
        fi
    fi
fi

# Idempotent: a no-op when nothing changed, which is almost every run.
#
# A successful update is deliberately NOT announced. This runs every 10 minutes
# forever, and SYSTEM.md's rule is that the machine interrupts Lukas only when
# something needs him — an update that worked does not. It is in the log and on
# the status page. Only failures and human-blocking problems send a message.
bash "$REPO/setup/install-user.sh" --check >/dev/null 2>&1
check_status=$?
case "$check_status" in
    0) : ;;                       # in sync, nothing to do
    1)                            # fixable drift
        log "drift detected, installing"
        if bash "$REPO/setup/install-user.sh" >>"$LOG" 2>&1; then
            log "install complete at ${remote_head:0:8}"
        else
            log "install FAILED"
            "$NOTIFY" "⚠️ lenovo failed to apply an update from GitHub. It is running older code than the repo."
            exit 1
        fi
        ;;
    2)                            # blocked: needs a human, re-running cannot help
        # Alert once per distinct blockage, not every 10 minutes forever. The
        # loop this prevents is not hypothetical: four unversioned scripts in
        # ~/bin did exactly this on 2026-07-26.
        fingerprint=$(bash "$REPO/setup/install-user.sh" --check 2>&1 | sort | cksum)
        if [ "$fingerprint" != "$(cat "$STATE/apply-blocked" 2>/dev/null)" ]; then
            echo "$fingerprint" >"$STATE/apply-blocked"
            log "BLOCKED: $(bash "$REPO/setup/install-user.sh" --check 2>&1 | tr '\n' '; ')"
            "$NOTIFY" "⚠️ lenovo cannot finish applying an update — something on the box needs a decision. See the apply log or STATUS.md."
        fi
        ;;
esac
# Clear the blocked marker once the box is healthy, so a future blockage alerts.
[ "$check_status" -eq 2 ] || rm -f "$STATE/apply-blocked"

# Last line of a successful run only — never in a trap. A heartbeat written on
# failure would tell the watchdog everything is fine while nothing works.
touch "$HEARTBEAT"
exit 0
