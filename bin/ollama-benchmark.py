#!/usr/bin/env python3
"""Benchmark local models for the workbench (spec §3).

Measures the two things that decide the 4B-vs-9B question:

  1. Speed — tokens/sec on a realistic scoring prompt.
  2. Structured-output reliability — does the model return schema-valid JSON
     every time? A model that is fast but needs retries is not fast.

Listings are deliberately awkward: Danish text, mixed casing, a junk price, a
wrong-category item, and one where the seller says "byd" (make an offer) instead
of giving a price. That is what DBA actually looks like.

    python3 ~/bin/ollama-benchmark.py [model ...]

Writes JSON results to ~/logs/benchmarks/<timestamp>.json for STACK.md.
"""
from __future__ import annotations

import sys
import json
import time
import urllib.request
from pathlib import Path
from datetime import datetime, timezone

OLLAMA = "http://127.0.0.1:11434"
OUT_DIR = Path.home() / "logs" / "benchmarks"

# A watchlist criterion of the kind Project 1 will use.
CRITERION = (
    "Lukas is looking for a roof box (tagboks) for a family car. "
    "He wants one in good condition, 400 litres or more, under 2500 DKK, "
    "and is not interested in roof racks, bike carriers, or damaged items."
)

LISTINGS = [
    "Thule Motion XT L tagboks 450L. Brugt 2 sæsoner, ingen skader. Nøgler medfølger. Pris 2200 kr.",
    "TAGBOKS SÆLGES!!! ca 300 liter, lidt ridser i lakken men helt tæt. 800,-",
    "Thule tagbøjler til VW Passat, sælges billigt. 350 kr.",
    "Stor tagboks Hapro Traxer 6.6, 410 liter, som ny. Byd!",
    "Tagboks 480L, revne i siden så den er utæt, kan bruges til opbevaring. 200 kr",
    "Cykelholder til anhængertræk, 3 cykler, Thule. 1800 kr",
]

SCHEMA = {
    "type": "object",
    "properties": {
        "relevant": {"type": "boolean"},
        "score": {"type": "integer", "minimum": 0, "maximum": 100},
        "price_dkk": {"type": ["integer", "null"]},
        "reason": {"type": "string"},
    },
    "required": ["relevant", "score", "price_dkk", "reason"],
}

# What a careful human would say. Used to flag semantically-wrong-but-valid JSON.
EXPECTED_RELEVANT = [True, False, False, True, False, False]


def score_listing(model: str, listing: str) -> tuple[dict | None, float, int]:
    """Return (parsed_json_or_None, seconds, eval_token_count)."""
    prompt = (
        f"Criterion:\n{CRITERION}\n\n"
        f"Listing:\n{listing}\n\n"
        "Score how well this listing matches the criterion. "
        "price_dkk is the asking price as an integer, or null if none is stated."
    )
    payload = json.dumps({
        "model": model,
        "prompt": prompt,
        "stream": False,
        # Qwen3 is a reasoning model. Left on, Ollama routes the answer into a
        # separate "thinking" field, leaves "response" empty, and spends most of
        # the tokens getting there. Bounded structured tasks do not want it.
        "think": False,
        "format": SCHEMA,
        "options": {"temperature": 0},
    }).encode()

    req = urllib.request.Request(f"{OLLAMA}/api/generate", data=payload,
                                 headers={"Content-Type": "application/json"})
    start = time.time()
    with urllib.request.urlopen(req, timeout=600) as resp:
        body = json.loads(resp.read())
    elapsed = time.time() - start

    try:
        parsed = json.loads(body.get("response", ""))
    except json.JSONDecodeError:
        parsed = None
    return parsed, elapsed, body.get("eval_count", 0)


def valid(obj) -> bool:
    if not isinstance(obj, dict):
        return False
    if not all(k in obj for k in SCHEMA["required"]):
        return False
    if not isinstance(obj.get("relevant"), bool):
        return False
    s = obj.get("score")
    if not isinstance(s, int) or not 0 <= s <= 100:
        return False
    p = obj.get("price_dkk")
    return p is None or isinstance(p, int)


def bench(model: str) -> dict:
    print(f"\n=== {model} ===", flush=True)
    rows, total_tok, total_s, schema_ok, agree = [], 0, 0.0, 0, 0

    for i, listing in enumerate(LISTINGS):
        try:
            parsed, secs, toks = score_listing(model, listing)
        except Exception as exc:
            print(f"  [{i}] ERROR {type(exc).__name__}: {exc}", flush=True)
            rows.append({"listing": listing[:50], "error": str(exc)})
            continue

        ok = valid(parsed)
        schema_ok += ok
        total_tok += toks
        total_s += secs
        match = ok and parsed["relevant"] == EXPECTED_RELEVANT[i]
        agree += match

        tps = toks / secs if secs else 0
        flag = "ok " if ok else "BAD"
        mark = "✓" if match else "✗"
        got = f"{parsed['relevant']}/{parsed['score']}" if ok else "unparseable"
        print(f"  [{i}] {flag} {mark} {secs:5.1f}s {tps:5.1f} tok/s  "
              f"got={got:<12} want={EXPECTED_RELEVANT[i]}", flush=True)
        rows.append({"listing": listing[:50], "seconds": round(secs, 2),
                     "tokens": toks, "schema_valid": ok,
                     "agrees_with_human": match, "output": parsed})

    n = len(LISTINGS)
    result = {
        "model": model,
        "tokens_per_sec": round(total_tok / total_s, 1) if total_s else 0,
        "avg_seconds_per_listing": round(total_s / n, 1),
        "schema_valid": f"{schema_ok}/{n}",
        "agrees_with_human": f"{agree}/{n}",
        "rows": rows,
    }
    print(f"  -> {result['tokens_per_sec']} tok/s | "
          f"schema {result['schema_valid']} | human-agreement {result['agrees_with_human']}",
          flush=True)
    return result


def main() -> int:
    models = sys.argv[1:] or ["qwen3:4b", "qwen3.5:9b"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    results = []
    for m in models:
        try:
            results.append(bench(m))
        except Exception as exc:
            print(f"{m}: FAILED — {type(exc).__name__}: {exc}")

    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y%m%d-%H%M%S")
    out = OUT_DIR / f"{stamp}.json"
    out.write_text(json.dumps({"listings": LISTINGS, "results": results},
                              indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {out}")

    print("\n| Model | tok/s | s/listing | schema | agrees |")
    print("|---|---|---|---|---|")
    for r in results:
        print(f"| `{r['model']}` | {r['tokens_per_sec']} | "
              f"{r['avg_seconds_per_listing']} | {r['schema_valid']} | "
              f"{r['agrees_with_human']} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
