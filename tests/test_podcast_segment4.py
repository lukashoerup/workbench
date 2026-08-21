"""Segment 4, pass two: the rebuild under motion doctrine v2."""

import pathlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "projects" / "podcast-visuals"))

import post  # noqa: E402
import prompt_builder as pb  # noqa: E402
import segment4  # noqa: E402


def test_the_cut_is_exactly_the_narration_window():
    """20:17 to 21:05 is 48 seconds. A cut that does not fill it is not the
    segment, and one that overruns walks into the next."""
    assert segment4.RUNTIME == 48


def test_every_shot_rests_on_the_audio():
    """This passage is narrated almost verbatim, so nothing here needs a note
    or the case file. If a shot ever claims a weaker source, it has drifted
    away from what is actually said."""
    for shot in segment4.SHOTS:
        assert shot.source == "audio", shot.id


def test_the_rails_hold():
    for shot in segment4.SHOTS:
        pb.check_shot(shot)
        pb.check_continuity(shot, segment4.LOOK_V2)
        pb.check_source(shot, transcript_exists=True)


def test_no_bare_skin_anywhere():
    """The rail, exercised on the real shot list rather than on a fixture.

    Pass one's S4-01 put a neck and a forearm under a bare bulb and both looks
    came back with an arm attached to nobody. That shot is retired and this is
    the guard that stops the next one.
    """
    for shot in segment4.SHOTS:
        pb.check_skin(shot, segment4.LOOK_V2)


def test_the_skin_rail_actually_catches_the_shot_that_failed():
    """The exact wording that got through pass one must not get through now."""
    bad = pb.Shot(
        id="X-BAD",
        segment="test",
        subject=(
            "A bare forearm and the back of a neck under a bare bulb, sweat "
            "standing on the skin"
        ),
        camera="85mm at f/2",
        motion="A bead of sweat runs down",
        motion_tier="B",
        source="audio",
    )
    with pytest.raises(pb.UnsafeShot):
        pb.check_skin(bad, segment4.LOOK_V2)


def test_the_skin_rail_does_not_fire_on_a_camera_position():
    """'Camera at chest height' is a place to stand, not a body in frame. If
    the rail cannot tell those apart it will be switched off, and then it
    protects nothing."""
    fine = pb.Shot(
        id="X-OK",
        segment="test",
        subject="A steel shelf unit and a clean rectangle in the dust",
        camera="35mm at f/2.8, camera at chest height, knee height for the insert",
        motion_tier="A",
        source="audio",
    )
    pb.check_skin(fine, segment4.LOOK_V2)


def test_pass_one_keeps_reproducing_under_the_older_rule():
    """The rail is opt-in. Pass one's approved shots were made under the looser
    rule and their prompts must still build, or the two passes cannot be
    compared."""
    import episode
    for shot in episode.SHOTS:
        pb.check_skin(shot, episode.LOOK)


def test_the_shot_lasse_stopped_on_is_gone_for_good():
    import episode
    assert not any(s.id == "S4-01" for s in episode.SHOTS)
    assert "S4-01" not in episode.HEROES
    stills = pathlib.Path(__file__).resolve().parents[1] / "projects" / "podcast-visuals" / "stills"
    clips = stills.parent / "clips"
    assert not list(stills.glob("S4-01*"))
    assert not list(clips.glob("S4-01*"))


def test_the_opening_shot_carries_sweat_without_a_body():
    """'Sveden løber fra panden' with nobody in frame: the floor under the bulb,
    where it has been landing for a while."""
    first = segment4.SHOTS[0]
    assert "concrete floor" in first.subject
    assert "no feet, no legs" in first.subject
    assert first.motion.startswith("One more drop falls")


def test_no_hands_anywhere():
    """Hands are the most reliable generative tell there is. Pass one put a
    gloved fingertip in frame; this pass has none, including in the motion."""
    for shot in segment4.SHOTS:
        text = f"{shot.subject} {shot.camera} {shot.motion}".lower()
        for word in ("hand", "hands", "finger", "fingers", "fingertip", "wrist", "palm"):
            assert word not in text.split(), f"{shot.id}: {word}"


def test_the_look_is_the_first_pass_look_with_only_the_camera_changed():
    """Consistency across segments is the whole product. If pass two quietly
    regrades, the two passes cannot be intercut and the comparison is void."""
    for field in ("stock", "palette", "light", "lens_family", "texture",
                  "continuity", "anti_tells", "format"):
        assert getattr(segment4.LOOK_V2, field) == getattr(segment4.LOOK, field), field
    assert segment4.LOOK_V2.motion_grammar != segment4.LOOK.motion_grammar
    assert segment4.LOOK_V2.camera_locked is True
    assert segment4.LOOK.camera_locked is False


def test_the_model_is_told_the_camera_is_bolted_down():
    """The move is added in post. If the model is left free to move the camera
    we get both moves at once, and one of them will be a move no camera makes."""
    for shot in segment4.SHOTS:
        if shot.motion_tier == "A":
            continue
        prompt = pb.build_motion_prompt(shot, segment4.LOOK_V2)
        assert "locked off on a tripod" in prompt
        assert "no camera movement of any kind" in prompt
        assert "handheld drift" not in prompt


def test_the_first_pass_still_asks_for_its_own_camera_move():
    """The flag must be opt-in: pass one's clips were made with a moving
    camera and its prompts have to keep reproducing."""
    import episode
    shot = next(s for s in episode.SHOTS if s.motion_tier != "A")
    prompt = pb.build_motion_prompt(shot, episode.LOOK)
    assert "locked off on a tripod" not in prompt
    assert "handheld drift" in prompt


def test_every_shot_has_a_move_and_none_of_them_is_visible():
    """A move you notice is a move that dates the picture. Five per cent of
    frame width across a whole shot is the ceiling."""
    assert set(segment4.MOVES) == {s.id for s in segment4.SHOTS}
    for shot_id, (kind, travel) in segment4.MOVES.items():
        assert kind in ("push", "pull", "left", "right"), shot_id
        assert 0 < travel <= 0.05, shot_id


def test_moving_shots_describe_one_event_and_still_ones_describe_none():
    for shot in segment4.SHOTS:
        if shot.motion_tier == "A":
            continue
        assert shot.motion, shot.id
        assert "." not in shot.motion.rstrip("."), f"{shot.id}: one event, one clause"


def test_the_ending_withholds_the_fire():
    """The narration's last words are 'og så tænder de ilden'. The last shot
    must not show it — that withholding is the whole thesis."""
    last = segment4.SHOTS[-1]
    assert "no flame anywhere in the picture" in last.subject


@pytest.mark.parametrize("kind", ["push", "pull", "left", "right"])
def test_the_move_eases_rather_than_ramping(kind):
    """A linear ramp is the giveaway of a machine-made move."""
    expr = post.move_filter(kind, 0.04, 4)
    assert "3-2*" in expr, "smoothstep missing"
    assert "sin(on/" in expr, "gate weave missing"


def test_an_unknown_move_is_refused():
    with pytest.raises(ValueError):
        post.move_filter("spin", 0.04, 4)
