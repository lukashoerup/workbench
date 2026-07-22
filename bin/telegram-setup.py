#!/usr/bin/env python3
"""One-time Telegram bot wiring (spec §7). Run interactively:

    python3 ~/bin/telegram-setup.py

Prerequisite: talk to @BotFather on Telegram, /newbot, copy the token.

The token is read from a hidden prompt (never from argv, so it stays out of
shell history), validated against getMe, then this waits for you to message the
bot so it can capture your chat_id. Result is written to ~/.secrets/telegram.env
with mode 600.
"""
from __future__ import annotations

import json
import time
import getpass
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

SECRETS = Path.home() / ".secrets" / "telegram.env"
API = "https://api.telegram.org"


def call(token: str, method: str, **params):
    url = f"{API}/bot{token}/{method}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=35) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return {"ok": False, "error_code": exc.code}
    except Exception as exc:
        return {"ok": False, "error": type(exc).__name__}


def main() -> int:
    if SECRETS.exists():
        print(f"{SECRETS} already exists.")
        if input("Overwrite? [y/N] ").strip().lower() != "y":
            return 1

    token = getpass.getpass("Paste the BotFather token (input hidden): ").strip()
    if not token:
        print("No token given.")
        return 1

    me = call(token, "getMe")
    if not me.get("ok"):
        print(f"Token rejected by Telegram: {me}")
        return 1
    username = me["result"]["username"]
    print(f"✅ Token valid — bot is @{username}")

    print(f"\nNow open Telegram, find @{username}, and send it any message.")
    print("Waiting (2 min timeout)…")

    chat_id = None
    chat_name = ""
    deadline = time.time() + 120
    offset = 0
    while time.time() < deadline:
        upd = call(token, "getUpdates", timeout=20, offset=offset)
        for item in upd.get("result", []):
            offset = item["update_id"] + 1
            msg = item.get("message") or item.get("channel_post")
            if msg and "chat" in msg:
                chat_id = msg["chat"]["id"]
                chat_name = msg["chat"].get("first_name") or msg["chat"].get("title", "")
                break
        if chat_id:
            break
        time.sleep(2)

    if not chat_id:
        print("\nNo message arrived. Re-run once you've messaged the bot.")
        print("(If the bot has an existing chat history, /start it again first.)")
        return 1

    print(f"✅ Captured chat_id {chat_id} ({chat_name})")

    SECRETS.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    SECRETS.write_text(
        "# Telegram bot credentials — never commit, never print.\n"
        f"TELEGRAM_BOT_TOKEN={token}\n"
        f"TELEGRAM_CHAT_ID={chat_id}\n",
        encoding="utf-8",
    )
    SECRETS.chmod(0o600)
    print(f"✅ Wrote {SECRETS} (mode 600)")

    if call(token, "sendMessage", chat_id=chat_id,
            text="🔧 Workbench notifications are wired up.").get("ok"):
        print("✅ Confirmation message sent — check your phone.")
        return 0
    print("⚠️  Credentials saved but the test message failed.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
