"""Segment 4, pass two: the rebuild under motion doctrine v2."""

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
