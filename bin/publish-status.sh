#!/usr/bin/env bash
# Regenerate STATUS.md and push it to GitHub, so the Claude app on a phone can
# read a current picture of this machine without any inbound connection.
#
# Run by workbench-status.timer every 30 min. Safe to run by hand.
#
# Deliberately narrow: it commits STATUS.md and reports/ and nothing else. Both
# are generated output written by this box's own timers. Work in progress is
# never auto-pushed — that stays a human decision.
set -uo pipefail

REPO="$HOME/workbench"
STATUS="$REPO/STATUS.md"
NOTIFY="$HOME/bin/notify.py"
STATE="$HOME/.local/state/workbench/publish-failures"

mkdir -p "$(dirname "$STATE")"
cd "$REPO" || exit 1

# Keep this clone tracking the remote. The amend + --force-with-lease below
# fails permanently once main moves ahead of us, and the failure looks like a
# network problem rather than a divergence — so a push from anywhere else would
# silently freeze the phone's view. workbench-apply.sh does the real
# reconciliation every 10 min; this is the cheap guard for the gap between.
git fetch -q origin main 2>/dev/null && git merge -q --ff-only origin/main 2>/dev/null

# No --quick here: the whole point of the page is measured test counts, and a
# suite slow enough to delay a 30-minute timer is itself worth noticing.
python3 "$HOME/bin/workbench-status.py" --write "$STATUS" >/dev/null 2>&1 || {
    echo "status generation failed" >&2
    exit 1
}

# The staging pathspec. reports/ carries the nightly brief and the weekly docs
# gardener, which are written by timers on this box and are useless if they never
# reach GitHub — a brief nobody can read is a brief that was not written.
#
# The pre-commit hook's publisher fast-path must match this list byte for byte
# (tasks/2026-07-26-hooks-and-work-block.md), so widening one means widening the
# other in the same commit. Guarded on the directory existing: `git add` fails
# outright on a pathspec that matches nothing, which would take STATUS.md with it.
PATHS=(STATUS.md)
[ -d reports ] && PATHS+=(reports)

# An untracked STATUS.md produces no diff at all, so the very first run would
# exit here and never publish. Intent-to-add makes it visible to git diff.
git add -N "${PATHS[@]}" 2>/dev/null

# Nothing changed but the "Generated <time>" line, and no new report? Don't
# commit every 30 min forever. -I ignores lines matching the pattern, so this is
# exact rather than a guess at how many lines a timestamp-only change touches.
if git diff --quiet -I '^_Generated ' -- "${PATHS[@]}"; then
    git reset -q -- "${PATHS[@]}" 2>/dev/null || true
    exit 0
fi

git add "${PATHS[@]}"

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
#
# Re-alert instead of firing once. A push that stays broken is exactly the case
# that matters, and a single message means Lukas hears about it once and then
# watches a frozen page that still looks healthy. Every 12th failure after the
# third mirrors the watchdog's 6h COOLDOWN at this 30-minute cadence: first
# alert at 1.5h, then every 6h.
fails=$(( $(cat "$STATE" 2>/dev/null || echo 0) + 1 ))
echo "$fails" >"$STATE"
if [ "$fails" -ge 3 ] && [ $(( (fails - 3) % 12 )) -eq 0 ]; then
    "$NOTIFY" "⚠️ Status page has failed to reach GitHub $fails times — the view on your phone is stale."
fi
exit 1
