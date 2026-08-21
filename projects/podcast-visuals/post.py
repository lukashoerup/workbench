"""The post pass: camera moves, grain and the assembly. No model involved.

Doctrine v2 puts every camera move here rather than in the video model. That
buys three things at once:

* **The move cannot look wrong.** A ninety-year-old rostrum move on a still
  frame is the most-used shot in factual television. Nothing is invented, so
  nothing can be invented badly.
* **The move is identical everywhere.** The same easing and the same travel on
  a generated clip and on a still means a cut between them does not announce
  which was which.
* **Grain on top of everything.** This is the load-bearing trick. Generated
  video's most consistent signature is that it is too clean — no grain, no
  gate weave, no sensor noise. Laying one grain structure over all eleven
  shots removes that signature and welds the set into one piece of film.

Run:
    python3 post.py --shots segment4 --stills stills/ --clips clips/ --out cut/
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

W, H, FPS = 1920, 1080, 25
CRF = "20"

#: How much grain. Luma only, temporal, at a level that reads as 35mm on a
#: television and disappears on a phone. Higher is not better: grain that is
#: visible as noise looks like a bad encode, not like film.
GRAIN = "noise=c0s=6:c0f=t+u"

#: Sub-pixel gate weave, two incommensurate periods so it never repeats.
WEAVE_X = "+1.1*sin(on/23.0)+0.7*sin(on/41.0)"
WEAVE_Y = "+0.9*sin(on/29.0)+0.6*sin(on/37.0)"


def _ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg
    except ImportError:  # pragma: no cover - environment dependent
        raise SystemExit("ffmpeg not found and imageio-ffmpeg is not installed")
    return imageio_ffmpeg.get_ffmpeg_exe()


def _ease(n: int) -> str:
    """Smoothstep over n frames, as an ffmpeg expression in `on`.

    A linear ramp is the giveaway of a machine-made move: real dolly and
    rostrum moves start and stop softly. Smoothstep is the cheapest honest
    ease there is.
    """
    p = f"min(1,on/{max(n - 1, 1)})"
    return f"({p}*{p}*(3-2*{p}))"


def move_filter(kind: str, travel: float, seconds: float) -> str:
    """The zoompan expression for one move.

    `travel` is how far the frame goes as a fraction of its width, over the
    whole shot. Everything here stays under 5%: a move you can see is a move
    that dates the picture.
    """
    n = int(round(seconds * FPS))
    e = _ease(n)
    if kind == "push":
        z = f"1+{travel:g}*{e}"
        x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif kind == "pull":
        z = f"1+{travel:g}*(1-{e})"
        x, y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif kind in ("left", "right"):
        z = f"{1 + travel:g}"
        span = f"(iw-iw/zoom)"
        prog = e if kind == "right" else f"(1-{e})"
        x, y = f"{span}*{prog}", "ih/2-(ih/zoom/2)"
    else:
        raise ValueError(f"unknown move {kind!r}")
    return (
        f"zoompan=z='{z}':x='{x}{WEAVE_X}':y='{y}{WEAVE_Y}'"
        f":d=1:s={W}x{H}:fps={FPS}"
    )


def _encode(inputs: list[str], vf: str, dest: Path) -> None:
    cmd = [
        _ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
        *inputs,
        "-vf", vf,
        "-an", "-c:v", "libx264", "-preset", "slow", "-tune", "grain", "-crf", CRF,
        "-pix_fmt", "yuv420p", "-r", str(FPS), str(dest),
    ]
    subprocess.run(cmd, check=True)


def from_still(src: Path, dest: Path, seconds: float, kind: str, travel: float) -> None:
    """A still becomes a moving shot. Nothing is generated."""
    vf = ",".join([
        "scale=3840:-2:flags=lanczos",
        move_filter(kind, travel, seconds),
        "format=yuv420p",
        GRAIN,
    ])
    _encode(["-loop", "1", "-framerate", str(FPS), "-t", f"{seconds:g}", "-i", str(src)], vf, dest)


def from_clip(src: Path, dest: Path, seconds: float, kind: str, travel: float,
              slow: float = 2.2) -> None:
    """A generated clip is slowed, trimmed to its calm middle, then given the
    same move and the same grain as the stills.

    Trimming to the middle matters: the first and last frames of a generated
    clip are where drift shows up, because that is where the model has had the
    most room to invent. The middle is the part that is still the picture we
    approved.
    """
    src_len = probe_duration(src)
    stretched = src_len * slow
    if stretched < seconds:
        slow = seconds / src_len
        stretched = seconds
    start = (stretched - seconds) / 2
    vf = ",".join([
        f"setpts={slow:g}*PTS",
        f"trim=start={start:g}:duration={seconds:g}",
        "setpts=PTS-STARTPTS",
        "scale=3840:-2:flags=lanczos",
        move_filter(kind, travel, seconds),
        "format=yuv420p",
        GRAIN,
    ])
    _encode(["-i", str(src)], vf, dest)


def probe_duration(src: Path) -> float:
    out = subprocess.run(
        [_ffmpeg(), "-hide_banner", "-i", str(src)],
        capture_output=True, text=True,
    ).stderr
    for line in out.splitlines():
        if "Duration:" in line:
            clock = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = clock.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise ValueError(f"no duration in {src}")


def assemble(parts: list[Path], dest: Path) -> None:
    """Hard cuts, no dissolves. Factual television cuts; it does not fade."""
    listing = dest.with_suffix(".txt")
    listing.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    subprocess.run(
        [_ffmpeg(), "-y", "-hide_banner", "-loglevel", "error",
         "-f", "concat", "-safe", "0", "-i", str(listing),
         "-c", "copy", str(dest)],
        check=True,
    )
    listing.unlink()


def build(shots, moves, stills: Path, clips: Path, out: Path,
          look_suffix: str = "photo") -> dict:
    out.mkdir(parents=True, exist_ok=True)
    parts, report = [], []
    for shot in shots:
        kind, travel = moves[shot.id]
        dest = out / f"{shot.id}.mp4"
        clip = clips / f"{shot.id}_{look_suffix}_1.mp4"
        still = stills / f"{shot.id}-{look_suffix}.jpg"
        if shot.motion_tier != "A" and clip.exists():
            from_clip(clip, dest, shot.seconds, kind, travel)
            origin = "clip"
        elif still.exists():
            from_still(still, dest, shot.seconds, kind, travel)
            origin = "still"
        else:
            report.append({"id": shot.id, "status": "missing"})
            continue
        parts.append(dest)
        report.append({
            "id": shot.id, "status": "ok", "from": origin,
            "seconds": shot.seconds, "move": kind, "travel": travel,
        })
    cut = out / "SEGMENT.mp4"
    if parts:
        assemble(parts, cut)
    return {"shots": report, "cut": str(cut), "seconds": sum(
        r.get("seconds", 0) for r in report if r["status"] == "ok")}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--shots", default="segment4")
    ap.add_argument("--stills", type=Path, default=Path("stills"))
    ap.add_argument("--clips", type=Path, default=Path("clips"))
    ap.add_argument("--out", type=Path, default=Path("cut"))
    ap.add_argument("--look", default="photo")
    args = ap.parse_args()

    module = __import__(args.shots)
    result = build(module.SHOTS, module.MOVES, args.stills, args.clips,
                   args.out, args.look)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
