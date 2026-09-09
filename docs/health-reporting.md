# Health reporting — what the status page may claim

`bin/workbench-status.py` generates `STATUS.md` (the detailed page) and, with
`--public`, a curated summary meant to leave the box. This page is the
contract for both: which claims exist, how each is earned, and what the public
summary may contain. `tests/test_status_generator.py` holds every rule here.

## Three verdicts, never two

Every check ends as exactly one of:

| Verdict | Meaning |
|---|---|
| `ok` | Measured, and the measurement supports it. |
| `failed` | Measured, and the measurement shows a problem. |
| `unknown` | Could not be measured, or the evidence is missing, malformed or ambiguous. |

`unknown` is printed, never folded into `ok`, and never dressed up as `failed`.
The page says an all-clear only when **every** check is `ok`; with any
`unknown` it says "not an all-clear" and lists what was not measured. A check
that fails to measure never invents an explanation ("no scrapers are running")
— it says what is absent.

## The checks

**tests: `<repo>`** — the suite is actually run (`uv run pytest tests/ -q`).
- `ok`: pytest exited 0 **and** its summary line counts at least one passed
  and zero failed or errored. Both must agree.
- `failed`: the summary counts any `failed` or `error` — teardown and
  collection errors included — whatever the exit code. (`1 passed, 1 error`,
  exit 1, used to read as a pass because only the word "failed" was grepped.)
- `unknown`, with the reason: `uv` not found (`no-runner`); no verdict within
  300 s (`timeout`); no pytest summary in the output; a non-zero exit with
  nothing counted as failing (interrupted, usage error, nothing collected);
  exit 0 with nothing passed (everything skipped); a Node project
  (`external` — CI is the judge, this box cannot see CI); `--quick`
  (`skipped`). None of these can make the page green.

**repository: `<repo>`** — every entry of `REPOS` is expected on the box.
- `ok`: clean, nothing unpushed.
- `failed`: uncommitted files or unpushed commits. A branch with no upstream
  counts the commits no remote has, rather than reporting nothing.
- `unknown`: the checkout is absent (it used to be skipped silently), the
  directory is not a git checkout, or a `git` probe failed.

**watchdog** — the box's own alarm, read from the last 40 lines of
`~/logs/watchdog.log`.
- `ok`: activity within 45 min and the last `run complete` line says
  `0 failing`.
- `failed`: silent for more than 45 min (three missed runs), or the last
  completed run has failing checks. Both can hold at once.
- `unknown`: no log, empty, unreadable or unparseable log; the watchdog runs
  but has no config (it checks nothing); recent activity with no completed
  run in the window.

**notifications** — read from `~/logs/notify.log`. **The last entry decides,
whatever its age.**
- `ok`: the last entry is `SENT`.
- `failed`: the last entry is `FAILED(...)` or `NOCHANNEL`. It stays failed
  until a later `SENT` proves the channel back — a failure used to age out
  after an hour, so a channel dead since last week read as fine.
- `unknown`: no log, empty, unreadable or unparseable; an unrecognised status
  (which is never echoed).

**heartbeats** — expectations come from the `heartbeat` lines of
`~/.config/workbench/watchdog.conf`; the marker directory alone proves nothing.
- `ok`: every expected marker exists and is within its limit.
- `failed`: an expected marker is missing (the job never ran) or older than
  its limit.
- `unknown`: the config cannot be read; a heartbeat line has no usable limit.
- Markers no line names are listed as *unwatched*. A config with no heartbeat
  lines yields no check — there is nothing to measure, and the page says so.

Setup gaps (SSH keys, tailnet, Telegram) are listed under "Needs you" as
before. A `tailscale status` that cannot be read is reported as unverified,
not as "no peers".

## Probes

Every command runs through `probe()`, which returns the exit code, the output,
and — separately — whether the executable was missing or the command timed
out. Health decisions read those fields. `run()` returns display text only and
its `(probe failed: …)` placeholder must never be counted as content; that is
how a failed `git status` once became "1 uncommitted file".

## The public summary (`--public`)

Same measurements, curated for publication. Markdown by default, the same
facts as JSON with `--json`, either to stdout or `--write PATH`.

Contains:
- `collected_at` — ISO-8601 with UTC offset, the moment of measurement.
- `overall` — `failed` if any check failed; else `unknown` if any check or
  machine fact could not be measured; else `ok`. The strongest claim the
  evidence supports, nothing stronger.
- `checks` — name (`tests: workbench`, `watchdog`, …), status, note. Notes
  are counts, ages and fixed phrases only.
- `failed` and `unknown` — the same, as explicit lists. Unknowns are always
  spelled out.
- `machine` — disk free/total/used %, memory available/total, uptime; each
  `null` and listed under unknown when not readable.
- `tests_measured` (false under `--quick`) and `setup_pending` (a count).

Never contains: log lines, notification text, task names, commit subjects,
branch or file names, usernames, home paths, hostnames, setup instructions,
toolchain paths, model names, timer names. The line is held structurally —
only `Check.name` and `Check.note` reach the summary, everything else lives in
`Check.details` for the local page — and by a sentinel test that plants each
excluded kind of string in the facts and asserts none survives.

Publication metadata (where and from which commit it was published) is the
publisher's to add around this output, not the generator's.

## Commands

```
python3 ~/bin/workbench-status.py                   # detailed page, runs the tests
python3 ~/bin/workbench-status.py --quick           # same, tests skipped and said so
python3 ~/bin/workbench-status.py --public          # publishable markdown
python3 ~/bin/workbench-status.py --public --json   # the same facts as JSON
python3 ~/bin/workbench-status.py --write PATH      # any of the above, to a file
```

## Reading it as a Claude

`unknown` means "we do not know" — say that, never "fine". `overall: ok` means
every listed check was measured and none failed, nothing more. A stale
`collected_at` (more than an hour) means the box is offline or the publisher
is broken; report that, not the contents.
