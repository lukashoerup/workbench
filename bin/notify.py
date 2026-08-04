#!/usr/bin/env python3
"""Telegram notification helper for all workbench jobs (spec §7).

Stdlib only — no dependencies, works in any venv or none.

CLI:
    notify.py "message"
    echo "message" | notify.py
    notify.py --flush          # drain the outbox, exit 0 regardless

Import (from a project venv):
    import sys; sys.path.insert(0, os.path.expanduser("~/bin"))
    from notify import notify
    notify("DBA: 3 new matches above threshold")

Credentials come from ~/.secrets/telegram.env (TELEGRAM_BOT_TOKEN,
TELEGRAM_CHAT_ID). If that file is absent the call degrades to a log line and
returns False rather than raising — a missing notification must never take down
a scraper run.

The box is Wi-Fi only, so a dropped link is routine. A message lost to one used
to exist solely as a log line nobody reads; now transient failures are retried
and then queued to the outbox, which drains on the next send and on every
watchdog tick.

**Queuing is not delivery.** notify() returns False whenever *this* message did
not go out *now*, even when it was safely queued — see the comment at the end
of notify() for what breaks otherwise.
"""
from __future__ import annotations

import os
import sys
import json
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

SECRETS = Path.home() / ".secrets" / "telegram.env"
LOG = Path.home() / "logs" / "notify.log"
OUTBOX = Path.home() / ".local" / "state" / "workbench" / "outbox.jsonl"
API = "https://api.telegram.org"
TIMEOUT = 20

# Three attempts, sleeping between them. A Wi-Fi blip that clears within seven
# seconds is the common case and worth waiting out inline; anything longer
# belongs in the outbox rather than in a blocked caller.
RETRY_BACKOFF = (2.0, 5.0)

# Drop-oldest bounds. The outbox is a safety net, not a log: an old alert about
# a machine that has since been rebooted is noise, and an unbounded queue on a
# box with a failing link is its own incident.
OUTBOX_MAX_ENTRIES = 200
OUTBOX_MAX_BYTES = 64 * 1024


def _load_env() -> dict[str, str]:
    """Parse the KEY=value secrets file. Never logs or returns the raw text.

    Unreadable file (wrong owner, bad mode) is treated as "no credentials"
    rather than an exception — a caller must never die over this.
    """
    env: dict[str, str] = {}
    try:
        if not SECRETS.is_file():
            return env
        raw = SECRETS.read_text(encoding="utf-8")
    except OSError:
        return env
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip().strip("'\"")
    return env


def _credentials() -> tuple[str | None, str | None]:
    env = _load_env()
    return (
        env.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN"),
        env.get("TELEGRAM_CHAT_ID") or os.environ.get("TELEGRAM_CHAT_ID"),
    )


def _log(status: str, message: str) -> None:
    """Append one tab-separated line. Swallows every filesystem error.

    A full disk is exactly when the watchdog needs to alert, so logging must
    never be the thing that raises. Tabs and newlines in the message are
    escaped so one entry stays one line.
    """
    try:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
        flat = message.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n")
        with LOG.open("a", encoding="utf-8") as fh:
            fh.write(f"{stamp}\t{status}\t{flat}\n")
    except OSError:
        pass


# --------------------------------------------------------------------- sending
def _send_once(token: str, chat_id: str, message: str, silent: bool) -> tuple[bool, str, bool]:
    """One delivery attempt. Returns (delivered, status, retryable).

    `retryable` separates "the link was down" from "Telegram said no". Only the
    former is worth retrying or queueing: a bad token or a deleted chat fails
    identically forever, and queueing those would fill the outbox with messages
    that can never leave it.
    """
    payload = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": "true",
            "disable_notification": "true" if silent else "false",
        }
    ).encode()

    req = urllib.request.Request(f"{API}/bot{token}/sendMessage", data=payload)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            ok = json.loads(resp.read()).get("ok", False)
    except urllib.error.HTTPError as exc:
        # Do not log the response body — it echoes back request parameters.
        # 429 is rate limiting and 5xx is Telegram being down: both clear on
        # their own. Every other 4xx is us being wrong, and will stay wrong.
        return False, f"FAILED(http={exc.code})", exc.code == 429 or 500 <= exc.code < 600
    except Exception as exc:  # network down, DNS, timeout
        return False, f"FAILED({type(exc).__name__})", True

    # HTTP 200 with {"ok": false} is Telegram rejecting the request itself
    # (unknown chat, blocked bot). Permanent, so it is not queued.
    return bool(ok), "SENT" if ok else "FAILED(api)", False


def _send_with_retries(token: str, chat_id: str, message: str, silent: bool) -> tuple[bool, str, bool]:
    """_send_once, retried through RETRY_BACKOFF while the failure is retryable."""
    for attempt in range(len(RETRY_BACKOFF) + 1):
        delivered, status, retryable = _send_once(token, chat_id, message, silent)
        if delivered or not retryable:
            return delivered, status, retryable
        if attempt < len(RETRY_BACKOFF):
            time.sleep(RETRY_BACKOFF[attempt])
    return delivered, status, retryable


# ---------------------------------------------------------------------- outbox
def _outbox_read() -> list[dict]:
    """Parse the outbox, skipping anything unusable.

    A half-written line from a power cut must not wedge the queue forever, so
    unparseable entries are dropped rather than raised on.
    """
    try:
        raw = OUTBOX.read_text(encoding="utf-8")
    except OSError:
        return []
    entries = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if isinstance(entry, dict) and isinstance(entry.get("message"), str):
            entries.append(entry)
    return entries


def _outbox_trim(entries: list[dict]) -> list[dict]:
    """Enforce both caps, dropping oldest first."""
    entries = list(entries)[-OUTBOX_MAX_ENTRIES:]
    lines = [json.dumps(e, ensure_ascii=False) for e in entries]
    total = sum(len(line.encode("utf-8")) + 1 for line in lines)
    while entries and total > OUTBOX_MAX_BYTES:
        total -= len(lines.pop(0).encode("utf-8")) + 1
        entries.pop(0)
    return entries


def _outbox_write(entries: list[dict]) -> None:
    """Replace the outbox atomically at mode 600. Swallows filesystem errors.

    Same rule as the log: a full disk must not turn a failed notification into
    a crashed caller.
    """
    entries = _outbox_trim(entries)
    try:
        if not entries:
            OUTBOX.unlink(missing_ok=True)
            return
        OUTBOX.parent.mkdir(parents=True, exist_ok=True)
        body = "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in entries)
        tmp = OUTBOX.with_name(OUTBOX.name + ".tmp")
        fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(body)
        os.replace(tmp, OUTBOX)
        os.chmod(OUTBOX, 0o600)
    except OSError:
        pass


def _outbox_append(message: str, silent: bool) -> None:
    """Queue one message. Credentials are deliberately not stored — the token
    must never reach disk here, and the chat is resolved fresh at drain time."""
    entries = _outbox_read()
    entries.append(
        {
            "ts": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
            "message": message,
            "silent": bool(silent),
        }
    )
    _outbox_write(entries)


def flush() -> int:
    """Deliver queued messages, oldest first. Returns the number delivered.

    One attempt per message, stopping at the first retryable failure: the queue
    is drained on a working link, never hammered on a dead one. Order is
    preserved so a recovered link replays the night in sequence.
    """
    entries = _outbox_read()
    if not entries:
        return 0

    token, chat_id = _credentials()
    if not token or not chat_id:
        # Keep them queued. A channel that is not configured yet is not the
        # queue's fault, and dropping the backlog would lose the evidence.
        return 0

    remaining = list(entries)
    delivered = 0
    while remaining:
        entry = remaining[0]
        ok, status, retryable = _send_once(
            token, chat_id, entry["message"], bool(entry.get("silent", False))
        )
        if not ok and retryable:
            break
        remaining.pop(0)
        if ok:
            delivered += 1
            _log("SENT(outbox)", entry["message"])
        else:
            _log(f"DROPPED(outbox,{status})", entry["message"])

    if len(remaining) != len(entries):
        _outbox_write(remaining)
    return delivered


# ---------------------------------------------------------------------- public
def notify(message: str, *, silent: bool = False) -> bool:
    """Send `message` to the configured Telegram chat. Returns True on delivery.

    silent=True delivers without a notification sound (for routine reports).
    """
    message = str(message or "").strip()
    if not message:
        return False

    token, chat_id = _credentials()
    if not token or not chat_id:
        # Permanent by definition: there is nowhere to send it, so it is logged
        # and dropped rather than queued.
        _log("NOCHANNEL", message)
        return False

    # Drain first, so anything queued earlier goes out ahead of this message.
    flush()

    delivered, status, retryable = _send_with_retries(token, chat_id, message, silent)
    if delivered:
        _log("SENT", message)
        return True

    if retryable:
        _outbox_append(message, silent)
        status = f"{status}+QUEUED"
    _log(status, message)

    # Queuing is not delivery. watchdog-check.sh reads this return value to
    # decide whether to start its 6h alert cooldown; reporting a queued alert as
    # sent would start that cooldown on a Wi-Fi drop and bury the very incident
    # the alert was about until morning.
    return False


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "--flush":
        flush()
        # Draining is best-effort maintenance called from the end of the
        # watchdog run; it must never colour that run's exit status.
        return 0
    text = " ".join(args) if args else sys.stdin.read()
    return 0 if notify(text) else 1


if __name__ == "__main__":
    raise SystemExit(main())
