#!/usr/bin/env python3
"""Telegram notification helper for all workbench jobs (spec §7).

Stdlib only — no dependencies, works in any venv or none.

CLI:
    notify.py "message"
    echo "message" | notify.py

Import (from a project venv):
    import sys; sys.path.insert(0, os.path.expanduser("~/bin"))
    from notify import notify
    notify("DBA: 3 new matches above threshold")

Credentials come from ~/.secrets/telegram.env (TELEGRAM_BOT_TOKEN,
TELEGRAM_CHAT_ID). If that file is absent the call degrades to a log line and
returns False rather than raising — a missing notification must never take down
a scraper run.
"""
from __future__ import annotations

import os
import sys
import json
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

SECRETS = Path.home() / ".secrets" / "telegram.env"
LOG = Path.home() / "logs" / "notify.log"
API = "https://api.telegram.org"
TIMEOUT = 20


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


def notify(message: str, *, silent: bool = False) -> bool:
    """Send `message` to the configured Telegram chat. Returns True on delivery.

    silent=True delivers without a notification sound (for routine reports).
    """
    message = str(message or "").strip()
    if not message:
        return False

    env = _load_env()
    token = env.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = env.get("TELEGRAM_CHAT_ID") or os.environ.get("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        _log("NOCHANNEL", message)
        return False

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
        _log(f"FAILED(http={exc.code})", message)
        return False
    except Exception as exc:  # network down, DNS, timeout
        _log(f"FAILED({type(exc).__name__})", message)
        return False

    _log("SENT" if ok else "FAILED(api)", message)
    return bool(ok)


def main() -> int:
    text = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else sys.stdin.read()
    return 0 if notify(text) else 1


if __name__ == "__main__":
    raise SystemExit(main())
