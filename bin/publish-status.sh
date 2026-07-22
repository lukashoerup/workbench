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

# Nothing changed beyond the timestamp line? Don't create an empty-noise commit.
if git diff --quiet -- STATUS.md; then
    exit 0
fi
changed=$(git diff --numstat -- STATUS.md | awk '{print $1+$2}')
if [ "${changed:-0}" -le 2 ]; then
    git checkout -- STATUS.md    # timestamp-only churn
    exit 0
fi

git add STATUS.md
git commit -q -m "Status: $(date '+%d %b %H:%M')" || exit 0

if git push -q origin HEAD 2>/dev/null; then
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
