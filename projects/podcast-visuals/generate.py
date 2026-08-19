#!/usr/bin/env python3
"""Generate stills from the shot list with Gemini's image models.

    GEMINI_API_KEY=... python3 generate.py S1-01 --look photo -n 3

The key is read from the environment and never written anywhere. This file is
in a public repository; nothing here may contain a credential.

Every image is written alongside a manifest entry recording model, prompt,
look, aspect ratio and time. That is not bookkeeping for its own sake — EU AI
Act disclosure (docs/RAILS.md) expects a production to be able to say what
generated what, and the record costs nothing if it is kept from the first
image rather than reconstructed later.

Stdlib only, per the workbench contract.
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

from episode import ENTITIES, HEROES, LOOKS, SHOTS  # noqa: E402
from prompt_builder import build_image_prompt, reference_frames  # noqa: E402

API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
DEFAULT_MODEL = "gemini-3-pro-image"   # Nano Banana Pro — reference images, 2K/4K


def _post(url: str, payload: dict, timeout: int = 300) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:600]
        raise SystemExit(f"HTTP {e.code}: {body}") from None


def generate(shot, look, out_dir: Path, n: int, model: str, size: str,
             references: list[Path] | None = None) -> list[Path]:
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        raise SystemExit("GEMINI_API_KEY is not set")

    prompt = build_image_prompt(shot, look, ENTITIES)
    parts: list[dict] = [{"text": prompt}]
    for ref in references or []:
        parts.append({
            "inline_data": {
                "mime_type": "image/png",
                "data": base64.b64encode(ref.read_bytes()).decode(),
            }
        })

    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for i in range(n):
        body = _post(
            API.format(model=model) + f"?key={key}",
            {
                "contents": [{"parts": parts}],
                "generationConfig": {
                    "responseModalities": ["IMAGE"],
                    "imageConfig": {"aspectRatio": "16:9", "imageSize": size},
                },
            },
        )
        got = False
        for cand in body.get("candidates", []):
            for part in cand.get("content", {}).get("parts", []):
                data = part.get("inlineData") or part.get("inline_data")
                if not data:
                    continue
                path = out_dir / f"{shot.id}_{look.name.replace(' ', '-')}_{i + 1}.png"
                path.write_bytes(base64.b64decode(data["data"]))
                written.append(path)
                got = True
        if not got:
            fb = body.get("candidates", [{}])[0].get("finishReason", "?")
            print(f"  ! no image returned (finishReason={fb})", file=sys.stderr)
            continue

        (out_dir / "manifest.jsonl").open("a").write(json.dumps({
            "shot": shot.id, "look": look.name, "model": model,
            "size": size, "aspect": "16:9", "variant": i + 1,
            "references": [r.name for r in references or []],
            "file": written[-1].name, "prompt": prompt,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }, ensure_ascii=False) + "\n")
        print(f"  {written[-1].name}")
    return written


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("shots", nargs="*", help="shot ids; default is the hero set")
    ap.add_argument("--look", default="photo", choices=sorted(LOOKS))
    ap.add_argument("-n", type=int, default=1, help="variants per shot")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--size", default="2K", choices=["1K", "2K", "4K"])
    ap.add_argument("--out", default="out")
    ap.add_argument("--refs", nargs="*", default=[], help="reference image paths")
    args = ap.parse_args(argv)

    wanted = args.shots or list(HEROES)
    by_id = {s.id: s for s in SHOTS}
    look = LOOKS[args.look]
    refs = [Path(r) for r in args.refs]

    for sid in wanted:
        if sid not in by_id:
            raise SystemExit(f"unknown shot {sid}")
        print(f"{sid} · {look.name} · {args.model} · {args.size}")
        generate(by_id[sid], look, Path(args.out), args.n, args.model, args.size, refs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
