#!/usr/bin/env bash
# Regenerate STATUS.md and push it to GitHub, so the Claude app on a phone can
# read a current picture of this machine without any inbound connection.
#
# Run by workbench-status.timer every 30 min. Safe to run by hand.
#
# Deliberately narrow: it commits STATUS.md and nothing else. Work in progress
# is never auto-pushed — that stays a human decision.
set -uo pipefail

REPO="$HOME/workbench"
STATUS="$REPO/STATUS.md"
NOTIFY="$HOME/bin/notify.py"
STATE="$HOME/.local/state/workbench/publish-failures"

mkdir -p "$(dirname "$STATE")"
cd "$REPO" || exit 1

# --quick on the timer path: the test suite runs in the dedicated job below so a
# slow suite never delays the status page. Here we want the real numbers, so no.
python3 "$HOME/bin/workbench-status.py" --write "$STATUS" >/dev/null 2>&1 || {
    echo "status generation failed" >&2
    exit 1
}

# An untracked STATUS.md produces no diff at all, so the very first run would
# exit here and never publish. Intent-to-add makes it visible to git diff.
git add -N STATUS.md 2>/dev/null

# Nothing changed but the "Generated <time>" line? Don't commit every 30 min
# forever. -I ignores lines matching the pattern, so this is exact rather than
# a guess at how many lines a timestamp-only change touches.
if git diff --quiet -I '^_Generated ' -- STATUS.md; then
    git reset -q -- STATUS.md 2>/dev/null || true
    exit 0
fi

git add STATUS.md

# Uptime, free RAM and log tails move on every run, so a plain commit-per-run
# would bury real history under ~48 status commits a day. The *history* of a
# status page is worthless — only its current contents matter — so consecutive
# status commits collapse into one that keeps moving forward.
if git log -1 --pretty=%s | grep -q '^Status: '; then
    git commit -q --amend -m "Status: $(date '+%d %b %H:%M')" || exit 0
    push_args="--force-with-lease"
else
    git commit -q -m "Status: $(date '+%d %b %H:%M')" || exit 0
    push_args=""
fi

# shellcheck disable=SC2086
if git push -q $push_args origin HEAD 2>/dev/null; then
    rm -f "$STATE"
    exit 0
fi

# Push failed. Wi-Fi drops here, so one failure is not worth a message; three
# consecutive ones means the phone view is going stale and Lukas should know.
fails=$(( $(cat "$STATE" 2>/dev/null || echo 0) + 1 ))
echo "$fails" >"$STATE"
if [ "$fails" -eq 3 ]; then
    "$NOTIFY" "⚠️ Status page has failed to reach GitHub 3 times — the view on your phone is going stale."
fi
exit 1
