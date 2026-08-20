#!/usr/bin/env python3
"""Animate an approved still with Veo, using the shot's motion prompt.

    GEMINI_API_KEY=... python3 animate.py S1-01 --frame path/to/still.png

Tier B only. Tier A shots are a still with a slow camera move added in the
edit — free, deterministic, and not this script's business, so asking for one
here is refused rather than quietly billed.

Same manifest discipline as generate.py: model, prompt and time are recorded
next to the file, because AI Act disclosure expects a production to be able to
say what generated what.
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from episode import LOOKS, SHOTS  # noqa: E402
from prompt_builder import build_motion_prompt  # noqa: E402

BASE = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_MODEL = "veo-3.1-fast-generate-preview"


def _req(url: str, payload: dict | None = None, timeout: int = 300) -> dict:
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"HTTP {e.code}: {e.read().decode(errors='replace')[:700]}") from None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("shot")
    ap.add_argument("--frame", required=True, help="approved still to animate")
    ap.add_argument("--look", default="photo", choices=sorted(LOOKS))
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--out", default="out")
    args = ap.parse_args(argv)

    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY is not set")

    shot = next((s for s in SHOTS if s.id == args.shot), None)
    if shot is None:
        raise SystemExit(f"unknown shot {args.shot}")
    if shot.motion_tier == "A":
        raise SystemExit(
            f"{shot.id} is tier A — a camera move over a still, done in the edit. "
            f"Generating it would spend credits on something that cannot fail."
        )

    look = LOOKS[args.look]
    prompt = build_motion_prompt(shot, look)
    frame = Path(args.frame)

    # Veo accepts only a few discrete lengths, whatever its error message says:
    # it rejects 5 while claiming to allow "between 4 and 8". So the shot's
    # intended length is snapped to the nearest one it will take, and the clip
    # is trimmed back to the intended length in the edit.
    ALLOWED = (4, 6, 8)
    want = int(shot.seconds)
    dur = min(ALLOWED, key=lambda a: (abs(a - want), a))
    if dur != want:
        print(f"  ({want}s not offered by {args.model}; rendering {dur}s, trim in the edit)")
    params = {"aspectRatio": "16:9", "durationSeconds": dur}
    if "lite" not in args.model and "fast" not in args.model:
        params["generateAudio"] = False

    op = _req(
        f"{BASE}/models/{args.model}:predictLongRunning?key={key}",
        {
            "instances": [{
                "prompt": prompt,
                "image": {
                    "bytesBase64Encoded": base64.b64encode(frame.read_bytes()).decode(),
                    "mimeType": "image/jpeg" if frame.suffix.lower() in (".jpg", ".jpeg")
                                else "image/png",
                },
            }],
            # generateAudio is rejected outright by some Veo tiers rather than
            # ignored, so it is only sent where it is accepted. Where it cannot
            # be switched off, the audio track is simply discarded in the edit —
            # the podcast is the audio.
            "parameters": params,
        },
    )
    name = op.get("name")
    print(f"{shot.id}: submitted, polling…")

    for _ in range(90):
        time.sleep(10)
        st = _req(f"{BASE}/{name}?key={key}")
        if st.get("done"):
            if "error" in st:
                raise SystemExit(f"failed: {json.dumps(st['error'])[:500]}")
            resp = st.get("response", {})
            vids = (resp.get("generateVideoResponse", {}).get("generatedSamples")
                    or resp.get("generatedSamples") or resp.get("videos") or [])
            out = Path(args.out)
            out.mkdir(parents=True, exist_ok=True)
            for i, v in enumerate(vids):
                uri = (v.get("video") or {}).get("uri") or v.get("uri")
                if not uri:
                    print(json.dumps(v)[:400]); continue
                sep = "&" if "?" in uri else "?"
                with urllib.request.urlopen(uri + f"{sep}key={key}", timeout=600) as r:
                    path = out / f"{shot.id}_{args.look}_{i + 1}.mp4"
                    path.write_bytes(r.read())
                print(f"  {path.name}  ({path.stat().st_size // 1024} kB)")
                (out / "manifest.jsonl").open("a").write(json.dumps({
                    "shot": shot.id, "look": look.name, "model": args.model,
                    "seconds": shot.seconds, "file": path.name, "prompt": prompt,
                    "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }, ensure_ascii=False) + "\n")
            return 0
        print("  …still rendering")
    raise SystemExit("timed out waiting for the render")


if __name__ == "__main__":
    raise SystemExit(main())
