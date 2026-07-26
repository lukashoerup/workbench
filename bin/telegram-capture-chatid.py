#!/usr/bin/env python3
"""Wait for the first message sent to the bot and record its chat_id.

Uses the token already stored in ~/.secrets/telegram.env, fills in the empty
TELEGRAM_CHAT_ID line, and sends a confirmation. Safe to re-run; exits 0 as
soon as a chat_id is known, 1 on timeout.

    python3 ~/bin/telegram-capture-chatid.py [timeout_seconds]
"""
from __future__ import annotations

import sys
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path.home() / "bin"))
from notify import _load_env, SECRETS, notify  # noqa: E402

API = "https://api.telegram.org"


def call(token: str, method: str, **params):
    url = f"{API}/bot{token}/{method}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=40) as resp:
        return json.loads(resp.read())


def main() -> int:
    timeout = int(sys.argv[1]) if len(sys.argv) > 1 else 600
    env = _load_env()
    token = env.get("TELEGRAM_BOT_TOKEN")
    if not token:
        print("no TELEGRAM_BOT_TOKEN in ~/.secrets/telegram.env")
        return 1
    if env.get("TELEGRAM_CHAT_ID"):
        print(f"chat_id already set: {env['TELEGRAM_CHAT_ID']}")
        return 0

    deadline = time.time() + timeout
    offset = 0
    chat_id = None
    chat_name = ""

    while time.time() < deadline and chat_id is None:
        try:
            upd = call(token, "getUpdates", timeout=25, offset=offset)
        except Exception as exc:
            print(f"poll error ({type(exc).__name__}), retrying")
            time.sleep(5)
            continue
        for item in upd.get("result", []):
            offset = item["update_id"] + 1
            msg = item.get("message") or item.get("channel_post")
            if msg and "chat" in msg:
                chat_id = msg["chat"]["id"]
                chat_name = msg["chat"].get("first_name") or msg["chat"].get("title", "")
                break

    if chat_id is None:
        print(f"timed out after {timeout}s — no message received")
        return 1

    # Rewrite only the chat-id line; leave the token untouched.
    lines = SECRETS.read_text(encoding="utf-8").splitlines()
    out = [l for l in lines if not l.startswith("TELEGRAM_CHAT_ID")]
    out.append(f"TELEGRAM_CHAT_ID={chat_id}")
    SECRETS.write_text("\n".join(out) + "\n", encoding="utf-8")
    SECRETS.chmod(0o600)

    print(f"captured chat_id {chat_id} ({chat_name}) and wrote it to {SECRETS}")
    ok = notify("🔧 Workbench notifications are live. This is where alerts will land.")
    print("confirmation sent" if ok else "confirmation FAILED — check ~/logs/notify.log")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
