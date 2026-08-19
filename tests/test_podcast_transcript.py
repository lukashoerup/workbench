"""Tests for the transcript reader.

Lukas is producing the transcript with whatever tool suits him, so these lock
down the shapes that actually turn up rather than one we invented. The
expensive failure is not a crash — it is a transcript that parses, reads fine,
and is quietly missing the half nobody checked.
"""
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent / "projects" / "podcast-visuals"
sys.path.insert(0, str(PROJECT))

from transcript import Cue, NoTimestamps, coverage, parse, window  # noqa: E402

SRT = """1
00:00:03,500 --> 00:00:06,000
To børn legede i skoven.

2
00:03:30,000 --> 00:03:36,000
Der lå et bål og brændte.
"""

VTT = """WEBVTT

00:00:03.500 --> 00:00:06.000
To børn legede i skoven.

00:03:30.000 --> 00:03:36.000
Der lå et bål og brændte.
"""

BRACKETED = """[00:00:03] To børn legede i skoven.
[00:03:30] Der lå et bål og brændte.
"""

PLAIN = """00:00:03  To børn legede i skoven.
00:03:30  Der lå et bål og brændte.
"""

SHORT_CLOCK = """[0:03] To børn legede i skoven.
[3:30] Der lå et bål og brændte.
"""


@pytest.mark.parametrize(
    "text,label",
    [(SRT, "srt"), (VTT, "vtt"), (BRACKETED, "bracketed"),
     (PLAIN, "plain"), (SHORT_CLOCK, "mm:ss")],
    ids=lambda v: v if isinstance(v, str) and len(v) < 12 else "",
)
def test_every_shape_parses_to_the_same_cues(text, label):
    cues = parse(text)
    assert [c.at for c in cues] == [3.5 if label in ("srt", "vtt") else 3.0, 210.0]
    assert cues[1].text == "Der lå et bål og brændte."


def test_a_speaker_prefix_is_captured_not_swallowed():
    cues = parse("[00:01:00] Stine Bolther: Det var en tirsdag.")
    assert cues[0].speaker == "Stine Bolther"
    assert cues[0].text == "Det var en tirsdag."


def test_a_colon_inside_ordinary_speech_is_not_a_speaker():
    cues = parse("[00:01:00] Han sagde noget mærkeligt, og så gik han.")
    assert cues[0].speaker == ""
    assert cues[0].text.startswith("Han sagde")


def test_wrapped_lines_join_onto_the_previous_cue():
    cues = parse("[00:01:00] Det var en tirsdag\ni slutningen af november.")
    assert len(cues) == 1
    assert cues[0].text == "Det var en tirsdag i slutningen af november."


def test_a_transcript_without_timestamps_is_refused():
    """It would parse as prose and then silently fail to line up with any
    timecode, which is the whole reason for having it."""
    with pytest.raises(NoTimestamps, match="no timestamps"):
        parse("To børn legede i skoven. Der lå et bål og brændte.")


def test_windows_are_half_open_so_adjacent_ones_do_not_double_count():
    cues = [Cue(10, "a"), Cue(20, "b"), Cue(30, "c")]
    assert [c.text for c in window(cues, 10, 20)] == ["a"]
    assert [c.text for c in window(cues, 20, 30)] == ["b"]


def test_a_window_accepts_clock_strings():
    cues = [Cue(200, "før"), Cue(215, "i vinduet"), Cue(400, "efter")]
    assert [c.text for c in window(cues, "3:30", "6:00")] == ["i vinduet"]


def test_a_backwards_window_is_an_error_not_an_empty_list():
    with pytest.raises(ValueError, match="ends before it starts"):
        window([Cue(1, "a")], "6:00", "3:30")


def test_a_truncated_transcript_is_reported():
    """The quiet failure: it parses, it reads fine, and the last twenty minutes
    are simply not there."""
    assert "truncated" in coverage([Cue(600, "a")], expected_seconds=2677)


def test_a_complete_transcript_passes_coverage():
    assert coverage([Cue(2650, "a")], expected_seconds=2677).startswith("OK")


def test_lasses_five_windows_can_all_be_addressed():
    """The five timecodes, with padding, against a synthetic full-length
    transcript — so the slicing is proven before the real one arrives."""
    cues = [Cue(float(t), f"t{t}") for t in range(0, 2677, 5)]
    windows = [("3:00", "6:30"), ("9:00", "13:30"), ("15:00", "17:40"),
               ("19:45", "21:35"), ("36:10", "40:10")]
    for a, b in windows:
        assert window(cues, a, b), f"{a}-{b} came back empty"


# --------------------------------------------------------------------------
# What actually arrived: TurboScribe free tier, no timestamps, cut at 30 min
# --------------------------------------------------------------------------

BANNER = "(Transskriberet af TurboScribe. Opgrader til Ubegrænset for at fjerne denne meddelelse.)"
TRUNCATED = (
    "(Denne fil er længere end 30 minutter. Opgrader til Ubegrænset på "
    "https://turboscribe.ai/da/ for at transskribere filer på op til 10 timer.)"
)


def test_the_services_own_truncation_notice_is_read_not_stripped():
    """The single most useful line in the file. A free tier that quietly stops
    at thirty minutes produces a transcript that parses, reads well, and is
    missing a third of the episode."""
    from transcript import truncation_notice

    assert "30 minutter" in truncation_notice(f"{BANNER}\n\nnoget tekst\n\n{TRUNCATED}")


def test_an_ordinary_upgrade_banner_is_not_mistaken_for_truncation():
    """The banner at the top of every free-tier transcript also says 'opgrader'.
    Treating that as a warning would cry wolf on every file."""
    from transcript import truncation_notice

    assert truncation_notice(f"{BANNER}\n\nnoget tekst") == ""


def test_an_untimed_transcript_is_usable_for_content_and_refused_for_placement():
    """Two functions on purpose: the words are still the primary source for what
    is described, and still cannot be tied to a timecode. Saying which is which
    out loud is the point."""
    from transcript import NoTimestamps, parse, parse_untimed

    text = f"{BANNER}\n\nTo børn fik deres livs chok.\n\nDer lå et bål.\n\n{TRUNCATED}"
    assert parse_untimed(text) == ["To børn fik deres livs chok.", "Der lå et bål."]
    with pytest.raises(NoTimestamps):
        parse(text)


def test_service_notices_never_reach_the_content():
    """Boilerplate in the shot-building material would end up quoted as if the
    episode had said it."""
    from transcript import parse_untimed

    for para in parse_untimed(f"{BANNER}\n\nrigtig tekst\n\n{TRUNCATED}"):
        assert "TurboScribe" not in para and "Opgrader" not in para
