#!/usr/bin/env python3
"""Authenticate the GitHub CLI on a headless box via OAuth device flow.

Prints a short code and a URL. You open the URL on any device, enter the code,
approve — this polls until GitHub confirms, then hands the token to `gh` and
stores a copy in ~/.secrets/github.env.

Uses the GitHub CLI's own public OAuth client id, i.e. exactly the handshake
`gh auth login --web` performs; it is reimplemented here only because gh needs a
terminal for that flow and this box has none.

    python3 ~/bin/github-device-login.py
"""
from __future__ import annotations

import json
import time
import subprocess
import urllib.parse
import urllib.request
from pathlib import Path

CLIENT_ID = "178c6fc778ccc68e1d6a"  # GitHub CLI, public
SCOPES = "repo,read:org,workflow,gist"
SECRETS = Path.home() / ".secrets" / "github.env"
GH = str(Path.home() / ".local/bin/gh")


def post(url: str, **params) -> dict:
    data = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request(url, data=data, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def main() -> int:
    start = post("https://github.com/login/device/code",
                 client_id=CLIENT_ID, scope=SCOPES)
    if "device_code" not in start:
        print(f"could not start device flow: {start}")
        return 1

    print("\n" + "=" * 52)
    print(f"  Open:  {start['verification_uri']}")
    print(f"  Code:  {start['user_code']}")
    print("=" * 52 + "\n")
    print("Waiting for you to approve (15 min timeout)…", flush=True)

    interval = int(start.get("interval", 5))
    deadline = time.time() + 900
    token = None

    while time.time() < deadline:
        time.sleep(interval)
        r = post("https://github.com/login/oauth/access_token",
                 client_id=CLIENT_ID,
                 device_code=start["device_code"],
                 grant_type="urn:ietf:params:oauth:grant-type:device_code")
        err = r.get("error")
        if err == "authorization_pending":
            continue
        if err == "slow_down":
            interval += 5
            continue
        if err:
            print(f"device flow failed: {err}")
            return 1
        token = r.get("access_token")
        break

    if not token:
        print("timed out — nobody approved the code")
        return 1

    SECRETS.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    SECRETS.write_text(f"GH_TOKEN={token}\n", encoding="utf-8")
    SECRETS.chmod(0o600)

    proc = subprocess.run([GH, "auth", "login", "--with-token"],
                          input=token, text=True, capture_output=True)
    if proc.returncode != 0:
        print(f"gh rejected the token: {proc.stderr.strip()}")
        return 1

    who = subprocess.run([GH, "api", "user", "--jq", ".login"],
                         text=True, capture_output=True)
    print(f"\n✅ Authenticated as {who.stdout.strip()}")
    print(f"✅ Token stored in {SECRETS} (mode 600)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
