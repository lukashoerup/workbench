# Task: honest health reporting

## Goal
STATUS.md answers "what is going on?" for a reader who cannot check. It was
answering with more confidence than it had measured: a real pytest failure
read as a pass, a dead notification channel aged into silence, and a watchdog
that had never written a log produced "Nothing. All clear." A page whose
promise is "measured, never remembered" must also never say more than it
measured — and must be able to say *unknown*.

Two halves, two agents. **This file tracks the generator half** (Claude, this
branch). The publisher/updater/installer/CI half is Codex's, on its own
branch, and integrates this one.

## Acceptance criteria — generator (this branch)
- [x] `collect_tests` respects the exit code: `1 passed, 1 error`, exit 1, is
      `fail` (was `pass` — the regex only looked for the word "failed")
- [x] Command absence, timeout and ambiguous output are explicit states
      (`no-runner`, `timeout`, `unknown` with a reason), never `pass`
- [x] `unknown`, `--quick` and `external` test results cannot imply all clear
- [x] A `FAILED`/`NOCHANNEL` notification attempt is retained until a later
      `SENT` proves recovery (was dropped after one hour)
- [x] Missing or malformed watchdog evidence, an expected repository that is
      not checked out, expected heartbeats without markers, and failed probes
      surface as `unknown`/`failed`, with no invented explanation
- [x] `failed` and `unknown` are distinct everywhere; the page and the public
      summary claim an all-clear only when every check was measured and ok
- [x] `--public` (`--json` optional): curated summary from allowed health
      facts, ISO-8601 `collected_at`, explicit unknowns; no raw logs,
      notification text, task names, commit subjects, usernames, home paths
      or hostnames. Normal detailed mode kept.
- [x] Regression tests: teardown error (fake and real pytest), missing
      runner and timeout (fake and real), unknown/quick/external, old
      notification failure and later recovery, absent/malformed watchdog
      evidence, private sentinels absent from public output
- [x] Tests that required the old unsafe behaviour replaced
- [x] `docs/health-reporting.md` written — the contract for both outputs
- [x] Complete Linux suite green before commit (87 → 141)
- [x] Review round 1 (Codex, 2026-09-12, anchored at `ea8dd60`), three
      findings fixed with regressions — see working notes

## Acceptance criteria — publisher side (Codex, separate branch)
- [ ] Publisher, updater, installer and CI changes
- [ ] Publication metadata wrapped around `--public` output
- [ ] `CLAUDE.md` command table mentions `--public` (global docs are Codex's)
- [ ] Integrated branch green; this file moved to `tasks/done/`

## Scope
**May change (this branch):** `bin/workbench-status.py`,
`tests/test_status_generator.py`, `docs/health-reporting.md`, this file.
**Must NOT touch:** `bin/publish-status.sh`, `bin/workbench-apply.sh`,
`setup/`, `.github/`, `CLAUDE.md`, `SYSTEM.md`, `context/` — Codex's half.
No new dependencies, no secrets, no real machine access, no merge, no deploy.

## Detail — the reproduced defects, as they stood at `6ab5193`
1. **Exit code discarded.** `collect_tests` (`workbench-status.py:63-72`)
   concatenated stdout+stderr and searched for `(\d+) passed` / `(\d+) failed`.
   pytest reports a fixture that dies on teardown as `1 passed, 1 error` and
   exits 1 — no "failed", so state was `pass`. A missing `uv` or a timeout
   became `(probe failed: …)` text with neither word, so state `unknown`,
   which `collect_blockers` then ignored — the page stayed clear.
2. **Notification failure aged out.** `collect_blockers` (`:257-262`)
   escalated `FAILED`/`NOCHANNEL` only within 3600 s of the attempt. A
   channel dead since last week, with nothing delivered since, read as fine.
3. **Absence read as health.** `_last_log_entry` returned `(None, [])` for
   `(no log yet)` and every caller took that as "nothing to say". A watchdog
   that never ran, a missing `REPOS` entry (`build()` skipped it), and a
   missing heartbeat directory ("no scrapers are running" — invented) all
   left "Nothing. All clear." on the page. `run()` placeholders leaked into
   counts: a failed `git status` was "1 uncommitted file"; a missing
   `tailscale` was "no peers".

## Design
- One pure `assess(facts) -> list[Check]` decides every verdict; both
  renderers (`render_detailed`, `public_summary`/`render_public`) read it,
  so the "Needs you" list can never disagree with the sections below it.
- `Check.name`/`Check.note` are public-safe by construction (fixed labels,
  counts, ages); `Check.details` carry the local-only wording. The public
  summary reads only the former. A sentinel test plants every excluded kind
  of string and asserts none survives.
- `probe()` returns `Probe(rc, out, error)`; `run()` is display-only.
- `collect_facts()` measures once; `render_*` are pure over the dict.
- `NamedTuple`, not `dataclass`: the tests load the module from its path
  without registering it in `sys.modules`, and `dataclass` under
  `from __future__ import annotations` needs that registration.

## Docs affected
`docs/health-reporting.md` (new). `CLAUDE.md`'s command table does not yet
mention `--public` — global docs are outside this branch's scope.

## Working notes (agent fills in)
- Branch `claude/workbench-health-reporting-nv5vzb` (dispatch-assigned; the
  `task/<name>` convention is Codex's to apply on integration).
- Behaviour change visible on the page: while `erhvervsklubben` is checked
  out, the page will never again say "All clear" — its tests are CI's to run
  and this box cannot see CI, so that check is a standing `unknown`. This is
  deliberate; see `context/LEARNINGS.md` 2026-09-05 (red CI for four weeks
  behind a page that said nothing).
- Old tests replaced, each because it asserted the unsafe behaviour:
  `test_all_clear_produces_no_blockers` (all-clear with no watchdog/notify
  evidence), `test_a_clean_watchdog_run_is_not_a_blocker` (`== []` with no
  notify evidence), `test_an_old_notification_failure_is_not_escalated`
  (the one-hour age-out).
- The end-to-end teardown test runs real pytest through a stand-in `uv`
  under a temp dir, so the reproduced defect is exercised, not simulated.
- Validation: `uv run pytest tests/ -o addopts=""` → 141 passed
  (docs invariants, notify, watchdog, publish and install suites untouched
  and green). CLI smoke-tested in all three modes against an empty fake HOME.

### Review round 1 — Codex, 2026-09-12, anchored at `ea8dd60`
Three findings, four isolated probes; none used live Lenovo data. Each is
now a named regression in `tests/test_status_generator.py`.
1. **Watchdog freshness came from any activity.** An old `run complete: 0
   failing` followed by a fresh `no config` or `ALERT` line returned ok,
   because `silent_min` was measured from the last line of any kind. Now
   freshness is measured from the last *completed* run; a later `no config`
   exit makes the verdict unknown, a later `ALERT`/`STILL-FAILING` line is
   failure evidence, and any other later line is reported as activity, "not
   yet a completed run" — never as health. Tests:
   `test_fresh_activity_does_not_refresh_an_old_completed_run` (three
   cases), `test_a_no_config_exit_after_a_fresh_run_is_unknown`,
   `test_an_alert_after_the_last_completed_run_is_failure_evidence`,
   `test_a_run_in_progress_is_activity_not_health_evidence`.
2. **Invalid heartbeat evidence vanished or passed.** `heartbeat apply` was
   dropped by the parser, so the expected monitor left the assessment; a
   marker dated a day ahead had a negative age and was ok; ages were
   compared in whole minutes. Now malformed lines are kept with a `problem`
   and assessed as unknown by name; limits must be positive integers of
   seconds; ages and limits compare in seconds; a marker more than
   `FUTURE_TOLERANCE_S` (300 s) in the future is unknown. The same skew
   rule covers a clean watchdog run and a `SENT` from the future. Tests:
   `test_read_watchdog_conf_keeps_malformed_lines_and_rejects_bad_limits`,
   `test_a_malformed_heartbeat_line_stays_visible_as_unknown`,
   `test_collect_heartbeats_with_a_marker_from_the_future` (real file),
   `test_collect_heartbeats_stale_by_seconds_end_to_end` (real file),
   `test_freshness_is_compared_in_seconds_not_rounded_minutes`,
   `test_a_future_dated_completed_run_is_unknown_not_ok`,
   `test_a_future_dated_delivery_is_unknown_not_ok`.
3. **`tests_measured` meant "not `--quick`".** With `uv` missing the public
   page still printed "Tests measured this run: yes". Now the summary
   carries `tests: {suites, measured, coverage, quick}`, where measured
   means a verdict from actually running (ok or failed) and coverage is
   full / partial / none; `tests_measured` is true only for full. Markdown
   prints "N of M suite(s) (coverage)". Tests:
   `test_tests_measured_reflects_actual_verdicts` (six cases),
   `test_quick_mode_measures_nothing_and_says_so_in_both_formats`.
- Two existing tests changed with the contract: the silent-watchdog wording
  is now "has not completed a run in N min", and the old mid-run test (an
  `ALERT` after a fresh run stayed ok) is split into the recovery-line case
  (ok, activity noted) and the alert case (failed).
- Model for this round, per the session record: configured, running and
  last-served `claude-fable-5-1`; no overage in use.
