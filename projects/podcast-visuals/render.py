#!/usr/bin/env python3
"""Print the prompt pack for the test episode.

    python3 render.py                  # the hero frames, photographic look
    python3 render.py --look drawn     # the same frames, charcoal-and-ink look
    python3 render.py --all            # every shot in the shot list
    python3 render.py --json           # machine-readable, for feeding a generator

No network, no keys, no cost. This turns the shot list into text you can paste
into any image model today, and it is the same function the automated pass will
call later — so what gets approved by eye is exactly what gets generated at
scale.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from episode import ENTITIES, HEROES, LOOKS, SHOTS  # noqa: E402
from prompt_builder import (  # noqa: E402
    SOURCE_MEANING,
    build_image_prompt,
    build_motion_prompt,
    reference_frames,
)


ANCHORS = {e.anchor for e in ENTITIES.values() if e.anchor}


def in_generation_order(shots):
    """Anchor shots first. Everything else is conditioned on an approved anchor
    frame, so generating a dependent shot before its anchor throws away the
    largest quality lever available."""
    return sorted(shots, key=lambda s: (s.id not in ANCHORS, s.id))


def pack(shots, look):
    for shot in in_generation_order(shots):
        yield {
            "id": shot.id,
            "segment": shot.segment,
            "is_anchor": shot.id in ANCHORS,
            "source": shot.source,
            "reference_frames": list(reference_frames(shot, ENTITIES)),
            "motion_tier": shot.motion_tier,
            "seconds": shot.seconds,
            "look": look.name,
            "image_prompt": build_image_prompt(shot, look, ENTITIES),
            "motion_prompt": build_motion_prompt(shot, look) if shot.motion else None,
        }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--all", action="store_true", help="every shot, not just the heroes")
    ap.add_argument("--json", action="store_true", help="JSON instead of markdown")
    ap.add_argument("--look", default="photo", choices=sorted(LOOKS),
                    help="which look to render in (default: photo)")
    args = ap.parse_args(argv)

    look = LOOKS[args.look]
    shots = SHOTS if args.all else [s for s in SHOTS if s.id in HEROES]
    rows = list(pack(shots, look))

    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return 0

    print(f"# Prompt pack — look: {look.name}\n")
    print(f"{len(rows)} shot(s), in generation order — anchors first.")
    print("Motion tiers: A parallax, B micro-motion, C generative.\n")
    for row in rows:
        tag = " · **anchor — generate and approve this first**" if row["is_anchor"] else ""
        print(f"## {row['id']} — {row['segment']}{tag}")
        print(f"_Tier {row['motion_tier']}, {row['seconds']:g}s — "
              f"source: {row['source']} ({SOURCE_MEANING[row['source']]})_\n")
        if row["reference_frames"]:
            refs = ", ".join(row["reference_frames"])
            print(f"**Attach as reference image(s):** {refs}\n")
        print("**Still**\n")
        print("```")
        print(row["image_prompt"])
        print("```\n")
        if row["motion_prompt"]:
            print("**Motion**\n")
            print("```")
            print(row["motion_prompt"])
            print("```\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
