# Independent review — Codex policy PRs and the reliability repair plan

_Addendum 2026-09-12: see `2026-09-12-direction-feasibility-addendum.md` for the phone-first direction review at PR 1 head `644d533`._

Date: 2026-09-09. Reviewer: Claude Fable 5.1 (`claude-fable-5-1`, confirmed via the
session record for both configured and last-served model). Requested by Lukas as a
cross-model review of Codex-authored work. Read-only: nothing was edited, merged or
messaged during the review; this file was written afterwards on request.

| Item | Revision | What was verified |
|---|---|---|
| workbench PR 1 | `6b21c8c` | Full diff (8 files); CI green (pytest, shellcheck, 4 check runs); 87 tests pass locally; generator run in a scratch HOME |
| erhvervsklubben PR 1 | `44981f9` | Full diff via anonymous git (5 files); policy copy byte-identical to workbench; `AGENTS.md` symlink present |
| Publisher and updater on main | `6ab5193` | `bin/publish-status.sh`, `bin/workbench-apply.sh`, `setup/install-user.sh`, units, tests; two defects reproduced |

Method: success criteria were written down before reading the implementation; primary
artifacts (diffs, scripts, tests, CI runs) were read rather than PR bodies; the two
publisher defects were reproduced in a throwaway repo with a bare remote.

## Success criteria (formed first)
- Purpose: the policy must give overview and occasional guidance, not ceremony.
- Honesty: written rules must never read as running integrations or schedules.
- No deadlock: nothing blocks on a party that may not exist or may not answer.
- Blast radius: automation touching git must never delete or rewrite human-written code.
- Smallest thing: a shorter text or simpler mechanism with the same outcome wins.

## Verdicts
| Item | Verdict |
|---|---|
| workbench `6b21c8c` | **Proceed** after the two wording fixes in A1 and A2; **simplify** the policy at the two-week evaluation the PR already schedules |
| erhvervsklubben `44981f9` | **Proceed**; it inherits whatever workbench decides. Its CI status could not be checked from this session |
| Reliability plan | **Simplify**, run the B1 **experiment** first, ship the observer before anything else; one **decision** for Lukas (B1/B2) |

---

## Part A — the policy PRs

**What is good.** Honesty is strong throughout. `docs/workflow-rollout.md` lists every
unbuilt integration; both PRs state the change is Codex-authored and unreviewed; the
Project instructions warn that a written rule is not a scheduler. No place was found
where a policy is represented as a running integration or schedule.

**Generator (`bin/new-project.sh`).** Installs the policy safely. Verified by running it
in a scratch HOME through an installed-style symlink: refuses when the canonical file is
missing (exit 1, before creating anything), refuses an existing directory, copies the
policy before writing `CLAUDE.md`, produces a byte-identical copy and a working
`AGENTS.md` symlink; generated `CLAUDE.md` is 38 lines. Gap: no automated test covers
it, and the PR's "installer tests" (`tests/test_install_user.py`) do not touch it.

### A1 — defect (clarity): "review pending" has no owner and no time bound
- Evidence: the rollout doc says no reviewer access, trigger or gate exists; the PR body
  records a failed 150 s review attempt; this review had to be dispatched by hand; the
  Project instructions tell the phone Claude to "initiate independent Codex review",
  which that surface cannot do.
- Consequence: every "substantial" change waits for a hand-carried review round — the
  approval loop Lukas asked to end — and an agent reading "hold the affected acceptance"
  may refuse to finish. No technical deadlock: `main` has no required-review protection
  and the PR reports mergeable. The deadlock is procedural.
- Fix: two sentences in `docs/WORKBENCH.md`. Pending review never blocks Lukas from
  merging; it is a label. If no independent review lands within 48 h, proceed on CI plus
  builder evidence and record "unreviewed".

### A2 — defect (clarity): the interrupt rule went from concrete to subjective
- Evidence: `CLAUDE.md`, `SYSTEM.md` and `docs/claude-project-instructions.md` replace
  the agreed 2026-07-26 list (money, security, access, taste, or a change in machine
  behaviour) with "meaningful decisions or operational changes" plus "occasional useful
  reflection". The weekly budget and snooze rules need memory across sessions; the
  rollout doc says that memory is not installed and no file is named for it.
- Consequence: the one rule that governs how often Lukas is interrupted becomes a
  per-session judgement with nothing to check against.
- Fix: keep the concrete list, add one bullet for the weekly reflection, and name the
  file where sent prompts, answers and snooze dates are recorded (erhvervsklubben already
  uses `docs/PROJECT.md`'s decision log this way).

### A3 — preference (proportionality): 99 lines, copied per project, plus a card with no home
- Evidence: `docs/WORKBENCH.md` asks for an eight-field project card, recorded reviewer
  identity/revision/scope per review, three checkpoints and success metrics; workbench
  ships no card; copies are plain duplicates with drift checking "not installed yet";
  workbench `CLAUDE.md` is at 78 of its 80-line cap after the PR.
- Consequence: more text per session in a repo whose own tests enforce document size,
  and more places to drift.
- Smaller solution: ~30 lines covering when review applies, that pending never blocks,
  the quiet-project question with a named record, one prompt per week across projects,
  plain-language chat, and "a rule is not a job". Reference the canonical file by
  repository path instead of copying; the generator's copy step then disappears.

Minor, not material: the `context/STACK.md` rewrite silently drops the 2026-07-26
sentence that the free layer is "the only layer allowed to run unattended by default" —
mark decisions superseded rather than rewriting them.

---

## Part B — the reliability repair plan

### Premise confirmed by reproduction
Scratch repo, bare remote, stubbed generator and notifier (same harness shape as
`tests/test_publish_status.py`):
1. Two files staged but not committed (`half_done.py`, `notes.env`) were swept into the
   next status commit and pushed. Cause: `git commit` after `git add STATUS.md` commits
   the whole index. The existing containment test covers unstaged and untracked files only.
2. A real commit pushed to `main` while the publisher was measuring, plus one background
   `git fetch origin main` of the kind `workbench-apply.timer` performs every 10 min, was
   removed from remote `main` by the amend + `--force-with-lease` push. Exit code 0.
   Cause: a bare lease takes its expected value from `origin/main` at push time, which
   the concurrent fetch had just advanced.
3. `bin/workbench-apply.sh:101-105` writes the success heartbeat on a blocked exit (2).

All three are defects in shipped code. The plan's direction is right.

### Context the plan should lead with
`STATUS.md` on `main` was generated 07 Aug 05:05 and nothing has published since, despite
a 5 Sep commit the publisher would have picked up. The box has been offline or broken for
a month and nobody was told. The GitHub observer is the only proposed component that
would have caught this; it needs no box and no credentials and works today against
`main`'s `STATUS.md` timestamp. **Ship it first.**

### B1 — assumption to verify: the primary consumer must be able to read the status branch
- Evidence: `CLAUDE.md`, `SYSTEM.md` and the Project instructions all point the phone
  Claude at `STATUS.md` in workbench; whether the GitHub connector reads a non-default
  branch is unverified; a pointer on `main` adds a hop in the GitHub app too.
- Consequence: if the connector reads only the default branch, the redesign makes the
  phone view worse.
- Fix: five-minute experiment first — push a file to a test branch and ask the Claude app
  to read it. If it cannot, publish to a tiny dedicated repository whose default branch
  is the report: same isolation, no pointer hop, no history in the code repo. Where Lukas
  looks is his call → needs decision.

### B2 — design gap: observer channel and cadence undefined; the obvious build nags
- Evidence: a scheduled workflow that fails while the report is stale emails on every
  run; at 30 min that recreates the 2026-08-06 mail storm in `context/LEARNINGS.md`.
  GitHub also disables scheduled workflows in public repos after 60 days without
  repository activity (verify) — the dead-box case is exactly the quiet one.
- Consequence: dozens of emails a day during an outage, or a watcher that switches
  itself off.
- Fix: run a few times a day; report through one GitHub issue opened when stale and
  closed on recovery, using the default token (no new credential); thresholds in one
  place, e.g. unknown after 90 min, failure after 24 h. One writer per ref: the box
  writes the status branch, the observer writes an issue, nothing automated writes `main`.

### B3 — over-specification: three gates plus rollback on a box nobody edits
- Evidence: `SYSTEM.md` declares lenovo "never a workspace"; CI already runs the suite on
  every SHA; an isolated test run on a CPU-only box that also loads a 6.6 GB model
  duplicates that verdict; automatic rollback is a second untested path that can fail.
- Smaller solution: refuse unless the checkout is clean and on `main`; advance only to a
  SHA whose CI is green; run `install-user.sh --check` against a candidate worktree as
  the only box-specific test; heartbeat only after every step succeeded; on failure alert
  once and keep running the old revision (what a failed fast-forward leaves anyway), with
  the previous SHA recorded for a human.
- Two things the plan misses: the CI gate needs `paths-ignore: STATUS.md` removed from
  `.github/workflows/tests.yml` once `main`'s `STATUS.md` stops changing, otherwise "no
  CI run" is an undefined state; and the publisher's measurement must share the updater's
  lock, or a test run across an activation reports a false red on the phone.

### A smaller publisher than the plan describes
On a status-only ref built from an explicit tree, force-pushing a single orphan commit is
safe by construction: no retry logic, no concurrent-publication case, no growth of ~48
commits/day that every fresh cloud clone downloads. Sketch (isolated bare store, code
checkout never opened for writing):

```
export GIT_DIR=$STATE/status.git            # git init --bare once
b1=$(git hash-object -w STATUS.md); b2=$(git hash-object -w status.json)
tree=$(printf '100644 blob %s\tSTATUS.md\n100644 blob %s\tstatus.json\n' "$b1" "$b2" | git mktree)
c=$(git commit-tree "$tree" -m "Status: $(date '+%d %b %H:%M')")
git push --force-with-lease=refs/heads/status:"$expected" origin "$c":refs/heads/status
```

Assert the target ref is never `main` and the tree holds only the allowed paths. If
history on the branch is wanted for the observer, append-only is fine; then plan a
periodic re-root.

### Agreed without change
Publish every successful measurement so freshness is visible. Heartbeat only after
confirmed delivery, plus a watchdog heartbeat line so Telegram fires when the box is
alive but cannot publish; the observer covers the dead-box case. Allowlisted public
output — this fixes a real exposure: both repositories are public and `STATUS.md`
currently publishes Telegram message text and log lines. No claims about branch
protection or live rollout until the status branch shows a fresh report. Health-reporting
content is left to the separate Claude task already changing it.

Suggested order: observer → publisher → updater → docs pointer.

---

## Limitations
- erhvervsklubben was read through anonymous git only; its CI for `44981f9` and any
  review comments were not checked (push-scoped attach denied).
- Nothing on lenovo could be inspected; all box statements come from the repo and the
  frozen `STATUS.md`.
- The claude.ai GitHub connector's branch behaviour was not tested. The 60-day
  auto-disable rule for scheduled workflows is from memory; confirm against GitHub docs.
- shellcheck was not installed locally; CI's shellcheck result was relied on.
