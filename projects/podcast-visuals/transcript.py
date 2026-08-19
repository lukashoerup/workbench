"""Read a transcript in whatever shape it arrives in, and slice it by timecode.

Lukas is producing the transcript with whatever tool suits him, so the format is
not ours to dictate — it could be SRT out of MacWhisper, WebVTT, bracketed
timestamps pasted into a document, or a plain two-column dump. All of those are
the same thing wearing different clothes: a time, and some words said at it.

So this parses the shapes that actually turn up rather than demanding one, and
fails loudly if it finds no timestamps at all — because a transcript without
them cannot be tied to Lasse's timecodes, which is the entire point of having
it.

Stdlib only, per the workbench contract.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# 00:03:30,500 / 00:03:30.500 / 00:03:30 / 03:30
_CLOCK = r"(?:(\d{1,2}):)?(\d{1,2}):(\d{2})(?:[.,](\d{1,3}))?"

_PATTERNS = (
    # SRT / WebVTT cue line: "00:03:30,500 --> 00:03:36,000"
    re.compile(rf"^\s*{_CLOCK}\s*-->\s*{_CLOCK}\s*$"),
    # "[00:03:30] text"  or  "[3:30] text"
    re.compile(rf"^\s*[\[(]\s*{_CLOCK}\s*[\])]\s*(?P<text>.*)$"),
    # "00:03:30  text"  or  "3:30 text"  or  "00:03:30 - text"
    re.compile(rf"^\s*{_CLOCK}\s*[-–—:\t ]\s*(?P<text>\S.*)$"),
)

# "Stine Bolther:" at the head of a line — kept, but not mistaken for content.
_SPEAKER = re.compile(r"^\s*(?P<who>[A-ZÆØÅ][\wÆØÅæøå .-]{1,40}):\s*(?P<rest>.*)$")


@dataclass(frozen=True)
class Cue:
    at: float          # seconds from the start of the episode
    text: str
    speaker: str = ""

    @property
    def clock(self) -> str:
        m, s = divmod(int(self.at), 60)
        return f"{m:02d}:{s:02d}"


class NoTimestamps(ValueError):
    """A transcript with no timestamps cannot be tied to Lasse's timecodes."""


def _seconds(h, m, s, ms) -> float:
    return int(h or 0) * 3600 + int(m) * 60 + int(s) + int((ms or "0").ljust(3, "0")) / 1000


def parse(text: str) -> list[Cue]:
    """Turn a transcript into cues, whatever shape it arrived in."""
    cues: list[Cue] = []
    pending_at: float | None = None

    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.isdigit():        # SRT sequence numbers
            continue
        if line.upper().startswith("WEBVTT"):
            continue

        matched = False
        for i, pattern in enumerate(_PATTERNS):
            m = pattern.match(line)
            if not m:
                continue
            at = _seconds(*m.groups()[:4])
            body = (m.groupdict().get("text") or "").strip()
            if i == 0:                        # a cue line; text is on the next line
                pending_at = at
            elif body:
                cues.append(_make(at, body))
            matched = True
            break

        if matched:
            continue
        if pending_at is not None:            # the line after an SRT/VTT cue
            cues.append(_make(pending_at, line))
            pending_at = None
        elif cues:                            # a continuation of the last cue
            cues[-1] = Cue(cues[-1].at, f"{cues[-1].text} {line}".strip(), cues[-1].speaker)

    if not cues:
        raise NoTimestamps(
            "no timestamps found. A transcript without them cannot be tied to "
            "the timecodes — ask the tool for SRT, VTT, or timestamped text."
        )
    return cues


def _make(at: float, body: str) -> Cue:
    m = _SPEAKER.match(body)
    if m and m.group("rest"):
        return Cue(at, m.group("rest").strip(), m.group("who").strip())
    return Cue(at, body)


def window(cues: list[Cue], start: str | float, end: str | float) -> list[Cue]:
    """The cues falling inside a window, given as seconds or as "3:30"."""
    a, b = _to_seconds(start), _to_seconds(end)
    if b <= a:
        raise ValueError(f"window ends before it starts: {start} -> {end}")
    return [c for c in cues if a <= c.at < b]


def _to_seconds(v: str | float) -> float:
    if isinstance(v, (int, float)):
        return float(v)
    parts = [float(p) for p in str(v).replace(".", ":").split(":")]
    while len(parts) < 3:
        parts.insert(0, 0.0)
    return parts[0] * 3600 + parts[1] * 60 + parts[2]


def coverage(cues: list[Cue], expected_seconds: float, tolerance: float = 120) -> str:
    """Report whether the transcript plausibly covers the whole episode.

    A truncated transcript is the quiet failure here: it parses, it reads fine,
    and the segment nobody checked is simply missing.
    """
    last = max(c.at for c in cues)
    if last < expected_seconds - tolerance:
        return (
            f"WARNING: transcript ends at {Cue(last, '').clock} but the episode "
            f"runs to {Cue(expected_seconds, '').clock} — it looks truncated."
        )
    return f"OK: {len(cues)} cues, ending {Cue(last, '').clock}."
