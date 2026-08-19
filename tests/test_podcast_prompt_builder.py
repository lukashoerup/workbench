"""Tests for projects/podcast-visuals.

Two different jobs in here.

The first is the ordinary one: the prompt builder does what it says.

The second matters more. The editorial rails in `docs/RAILS.md` — no faces, no
body, no fabricated evidence — are the whole reason this approach is usable for
broadcast at all, and they are exactly the kind of rule that erodes quietly one
shot at a time when a deadline is close. So the shot list itself is under test:
a shot that asks for a face fails the suite, before anyone spends a credit on
it and long before it reaches a screen.
"""
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parent.parent / "projects" / "podcast-visuals"
sys.path.insert(0, str(PROJECT))

from episode import ENTITIES, HEROES, LOOK, LOOKS, SHOTS  # noqa: E402
from prompt_builder import (  # noqa: E402
    FORBIDDEN,
    Entity,
    Look,
    Shot,
    UnsafeShot,
    build_image_prompt,
    build_motion_prompt,
    check_shot,
)


# --------------------------------------------------------------------------
# The rails
# --------------------------------------------------------------------------

@pytest.mark.parametrize("shot", SHOTS, ids=lambda s: s.id)
def test_every_shot_in_the_episode_clears_the_rails(shot):
    check_shot(shot)


@pytest.mark.parametrize(
    "subject",
    [
        "A close-up of the suspect, his face lit from one side",
        "A portrait of the investigating officer at his desk",
        "A woman looking into the camera from the doorway",
    ],
)
def test_a_shot_naming_a_face_is_rejected(subject):
    with pytest.raises(UnsafeShot, match="face or a portrait"):
        check_shot(Shot(id="X", segment="t", subject=subject, camera="50mm"))


@pytest.mark.parametrize(
    "subject",
    [
        "The body on the table under a sheet",
        "A wound visible on the forearm",
        "Blood soaking into the grass",
    ],
)
def test_a_shot_depicting_a_body_is_rejected(subject):
    with pytest.raises(UnsafeShot, match="body or an injury"):
        check_shot(Shot(id="X", segment="t", subject=subject, camera="50mm"))


def test_the_rails_are_checked_on_motion_text_too():
    """A still can be clean and the clip prompt can still ask for the thing —
    'the camera tilts up to his face' is a rail breach that only exists in the
    motion field."""
    shot = Shot(
        id="X",
        segment="t",
        subject="Two hands on a table",
        camera="50mm",
        motion="The camera tilts up to his face",
    )
    with pytest.raises(UnsafeShot):
        build_motion_prompt(shot, LOOK)


@pytest.mark.parametrize("shot", SHOTS, ids=lambda s: s.id)
def test_no_shot_can_opt_out_of_the_forbidden_block(shot):
    prompt = build_image_prompt(shot, LOOK, ENTITIES)
    for rule in FORBIDDEN:
        assert rule in prompt


# --------------------------------------------------------------------------
# Consistency — the reason 300 shots read as one programme
# --------------------------------------------------------------------------

def test_the_look_block_is_byte_identical_across_shots():
    """If the look were rebuilt per shot it would drift, and drift across a few
    hundred shots is exactly what makes AI footage look like AI footage."""
    blocks = {LOOK.block() for _ in SHOTS}
    assert len(blocks) == 1


def test_a_shot_with_its_own_light_drops_the_look_s_lighting_rule():
    """Sending the general rule and the specific instance together makes the
    model average them."""
    lit = Shot(id="X", segment="t", subject="A table", camera="50mm", light="A single candle")
    unlit = Shot(id="Y", segment="t", subject="A table", camera="50mm")
    assert LOOK.light not in build_image_prompt(lit, LOOK)
    assert LOOK.light in build_image_prompt(unlit, LOOK)


def test_entity_descriptions_are_inserted_verbatim():
    """Paraphrasing a recurring place per shot is how the same clearing becomes
    three different clearings."""
    shot = next(s for s in SHOTS if "baalplads" in s.entities)
    prompt = build_image_prompt(shot, LOOK, ENTITIES)
    assert ENTITIES["baalplads"].description in prompt


def test_an_unknown_entity_is_an_error_not_a_silent_omission():
    shot = Shot(id="X", segment="t", subject="A table", camera="50mm", entities=("nowhere",))
    with pytest.raises(KeyError, match="nowhere"):
        build_image_prompt(shot, LOOK, ENTITIES)


# --------------------------------------------------------------------------
# The shot list holds together
# --------------------------------------------------------------------------

def test_shot_ids_are_unique():
    ids = [s.id for s in SHOTS]
    assert len(ids) == len(set(ids))


def test_every_hero_is_a_real_shot():
    ids = {s.id for s in SHOTS}
    assert set(HEROES) <= ids


def test_every_shot_carries_a_motion_description():
    """A still with no motion plan is a still that gets animated by whoever is
    on the timeline at 23:00, which is where the format falls apart."""
    missing = [s.id for s in SHOTS if not s.motion]
    assert not missing, f"no motion planned for {missing}"


def test_motion_tiers_are_known():
    assert {s.motion_tier for s in SHOTS} <= {"A", "B", "C"}


def test_clips_stay_short_enough_to_survive_generation():
    """Generative video degrades with length; past about eight seconds the
    failure rate stops being worth the credits."""
    too_long = [s.id for s in SHOTS if s.seconds > 8]
    assert not too_long, f"over the 8s cap: {too_long}"


def test_a_motion_prompt_needs_something_to_animate():
    shot = Shot(id="X", segment="t", subject="A table", camera="50mm")
    with pytest.raises(ValueError, match="needs a motion description"):
        build_motion_prompt(shot, LOOK)


# --------------------------------------------------------------------------
# The CLI
# --------------------------------------------------------------------------

def test_render_produces_a_prompt_for_every_shot():
    out = subprocess.run(
        [sys.executable, str(PROJECT / "render.py"), "--all", "--json"],
        capture_output=True, text=True, check=True,
    ).stdout
    import json

    rows = json.loads(out)
    assert len(rows) == len(SHOTS)
    assert all(r["image_prompt"] and r["motion_prompt"] for r in rows)


def test_render_defaults_to_the_heroes():
    out = subprocess.run(
        [sys.executable, str(PROJECT / "render.py"), "--json"],
        capture_output=True, text=True, check=True,
    ).stdout
    import json

    assert {r["id"] for r in json.loads(out)} == set(HEROES)


def test_a_look_change_reaches_every_prompt():
    """The style bible is meant to be the one steering wheel: change a line
    there and the whole episode changes with it."""
    other = Look(
        name="test", stock="STOCK-X", palette="p", light="l",
        lens_family="lf", texture="t",
    )
    for shot in SHOTS:
        assert "STOCK-X" in build_image_prompt(shot, other, ENTITIES)


# --------------------------------------------------------------------------
# Reference anchoring — the largest single quality lever
# --------------------------------------------------------------------------

def test_an_anchor_shot_does_not_reference_itself():
    """An anchor is generated cold and judged. If it referenced itself there
    would be nothing to generate it from."""
    from prompt_builder import reference_frames

    anchors = {e.anchor for e in ENTITIES.values() if e.anchor}
    for shot in SHOTS:
        if shot.id in anchors:
            assert shot.id not in reference_frames(shot, ENTITIES)


def test_every_anchor_names_a_real_shot():
    ids = {s.id for s in SHOTS}
    for entity in ENTITIES.values():
        if entity.anchor:
            assert entity.anchor in ids, f"{entity.id} anchors to missing {entity.anchor}"


def test_every_recurring_location_has_an_anchor():
    """Words alone will not hold a location across a dozen frames. A location
    used more than once without an anchor frame will drift."""
    from collections import Counter

    used = Counter(e for s in SHOTS for e in s.entities)
    unanchored = [e for e, n in used.items() if n > 1 and not ENTITIES[e].anchor]
    assert not unanchored, f"recurring but unanchored: {unanchored}"


def test_dependent_shots_carry_their_anchor_as_a_reference():
    from prompt_builder import reference_frames

    shot = next(s for s in SHOTS if s.id == "S1-03")
    assert "S1-01" in reference_frames(shot, ENTITIES)


def test_anchors_are_rendered_before_the_shots_that_depend_on_them():
    import json

    out = subprocess.run(
        [sys.executable, str(PROJECT / "render.py"), "--all", "--json"],
        capture_output=True, text=True, check=True,
    ).stdout
    rows = json.loads(out)
    position = {r["id"]: i for i, r in enumerate(rows)}
    for row in rows:
        for ref in row["reference_frames"]:
            assert position[ref] < position[row["id"]], (
                f"{row['id']} is generated before its reference {ref}"
            )


# --------------------------------------------------------------------------
# Continuity — one weather, one hour, one season, across every scene
# --------------------------------------------------------------------------

@pytest.mark.parametrize("shot", SHOTS, ids=lambda s: s.id)
def test_every_shot_holds_the_established_continuity(shot):
    """The look can be perfectly consistent and the programme still fall apart
    because it rains in one scene and not the next. This catches the second
    kind of drift, which is the one nobody writes down."""
    from prompt_builder import check_continuity

    check_continuity(shot, LOOK)


@pytest.mark.parametrize(
    "field,value",
    [
        ("light", "Low raking sun under a heavy sky"),
        ("atmosphere", "A clear sky after the rain has passed"),
        ("subject", "The clearing in bright sunshine"),
        ("motion", "Sunlight moves across the ash"),
    ],
)
def test_a_shot_that_fights_the_weather_is_rejected(field, value):
    from prompt_builder import ContinuityBreak

    kwargs = {"id": "X", "segment": "t", "subject": "A table", "camera": "50mm"}
    kwargs[field] = value
    kwargs.setdefault("motion", "nothing moves")
    with pytest.raises(ContinuityBreak):
        build_image_prompt(Shot(**kwargs), LOOK, ENTITIES)


@pytest.mark.parametrize("shot", SHOTS, ids=lambda s: s.id)
def test_the_continuity_block_reaches_every_prompt(shot):
    assert LOOK.continuity in build_image_prompt(shot, LOOK, ENTITIES)


def test_all_directed_light_is_motivated_by_something_in_the_scene():
    """The episode has no sun and no break in the weather, so any hard
    directional light has to come from an object that is physically there — a
    work lamp, a torch, a bulb, a forecourt canopy. Light with no source in the
    scene is the tell that gives a generated frame away.

    This started life asserting exactly one such shot. The transcript added the
    night of the disposal, which is lit by torches and forecourt lights, so the
    count was never the invariant — the motivation was.
    """
    sources = ("lamp", "torch", "bulb", "forecourt", "surgical", "fluorescent",
               "flame", "sodium", "firelight")
    unmotivated = [
        s.id for s in SHOTS
        if any(w in s.light.lower() for w in ("raking", "directed", "beam"))
        and not any(src in s.light.lower() for src in sources)
    ]
    assert not unmotivated, f"directed light with no source in the scene: {unmotivated}"


def test_the_look_carries_the_bridge_between_interiors_and_exteriors():
    """A cut from a wet wood to a tiled room is where an episode most obviously
    stops being one piece. The continuity block has to say what carries across."""
    assert "cyan" in LOOK.continuity and "jar" in LOOK.continuity


# --------------------------------------------------------------------------
# Sources — the narration outranks everything, including better facts
# --------------------------------------------------------------------------

# True since 19 Aug 2026: Lukas transcribed the episode with TurboScribe and put
# it in Drive. It covers the first 30 minutes only, which is why segment 5 is
# still on Lasse's notes rather than on the audio.
TRANSCRIPT_EXISTS = True


@pytest.mark.parametrize("shot", SHOTS, ids=lambda s: s.id)
def test_every_shot_declares_a_real_source(shot):
    from prompt_builder import check_source

    check_source(shot, transcript_exists=TRANSCRIPT_EXISTS)


def test_the_untranscribed_segment_does_not_claim_the_audio():
    """The transcript stops at 30 minutes, so nothing after it can rest on the
    audio. Segment 5 is the part that is not covered, and it must say so."""
    unsupported = [
        s.id for s in SHOTS
        if s.id.startswith("S5-") and s.source == "audio"
    ]
    assert not unsupported, (
        f"{unsupported} claim the audio, but the transcript stops before 36:40"
    )


def test_most_of_the_shot_list_now_rests_on_the_audio():
    """The measure of whether the transcript did its job. Before it arrived this
    was zero."""
    from_audio = [s.id for s in SHOTS if s.source == "audio"]
    assert len(from_audio) > len(SHOTS) * 0.6, (
        f"only {len(from_audio)}/{len(SHOTS)} shots rest on the audio"
    )


def test_a_shot_cannot_claim_the_audio_while_none_exists():
    from prompt_builder import UnknownSource, check_source

    shot = Shot(id="X", segment="t", subject="A table", camera="50mm", source="audio")
    with pytest.raises(UnknownSource, match="no transcript"):
        check_source(shot, transcript_exists=False)


def test_an_invented_source_tier_is_rejected():
    from prompt_builder import UnknownSource, check_source

    shot = Shot(id="X", segment="t", subject="A table", camera="50mm", source="vibes")
    with pytest.raises(UnknownSource, match="not one of"):
        check_source(shot)


def test_no_hero_frame_rests_on_art_direction_alone():
    """The heroes are the frames that carry the case. An atmosphere shot may be
    invented; the frame that says what happened may not."""
    invented = [s.id for s in SHOTS if s.id in HEROES and s.source == "direction"]
    assert not invented, f"hero frames sourced to nothing: {invented}"


# --------------------------------------------------------------------------
# Motion grammar — one speed across the whole programme
# --------------------------------------------------------------------------

@pytest.mark.parametrize("shot", [s for s in SHOTS if s.motion], ids=lambda s: s.id)
def test_the_motion_grammar_reaches_every_clip(shot):
    """Motion that varies shot to shot reads as a collection of clips rather
    than as an edit, so the grammar is frozen exactly like the look is."""
    assert LOOK.motion_grammar in build_motion_prompt(shot, LOOK)


def test_the_grammar_holds_one_speed_and_forbids_ramping():
    """A clip that starts slow and returns to normal is the single most
    recognisable AI-video move there is."""
    assert "half real speed" in LOOK.motion_grammar
    assert "never ramps" in LOOK.motion_grammar
    assert "no speed ramp" in build_motion_prompt(SHOTS[0], LOOK)


def test_the_camera_is_exempt_from_the_slow_motion():
    """Slowing the camera as well turns every push into a drift and every drift
    into nothing. The event slows; the move does not."""
    assert "camera itself moves at ordinary speed" in LOOK.motion_grammar


def test_generated_clips_animate_something_that_reads_when_slowed():
    """Slow motion needs a fast physical event to slow down. A shot whose only
    movement is the camera belongs in tier A, where it is done in post for free
    and cannot fail."""
    camera_only = ("drift", "push", "pan", "tilt", "track")
    misfiled = [
        s.id for s in SHOTS
        if s.motion_tier == "B"
        and any(s.motion.lower().startswith(w) or f"a slow {w}" in s.motion.lower()
                for w in camera_only)
    ]
    assert not misfiled, f"camera-only motion filed as generative: {misfiled}"


# --------------------------------------------------------------------------
# Two looks, one shot list
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name,look", sorted(LOOKS.items()))
@pytest.mark.parametrize("shot", SHOTS, ids=lambda s: s.id)
def test_every_shot_survives_both_looks(shot, name, look):
    """The whole value of a second look is that it is the *only* variable. If a
    shot works in one and not the other, something other than the medium
    changed."""
    prompt = build_image_prompt(shot, look, ENTITIES)
    assert look.block(include_light=not shot.light) in prompt
    for rule in FORBIDDEN:
        assert rule in prompt


def test_the_drawn_look_carries_drawn_tells_not_photographic_ones():
    """"No HDR glow" says nothing about a charcoal drawing, and a prompt full of
    irrelevant negatives spends the model's attention on nothing."""
    from prompt_builder import PHOTO_TELLS

    drawn = build_image_prompt(SHOTS[0], LOOKS["drawn"], ENTITIES)
    assert "vector-clean" in drawn and "no comic-book inking" in drawn
    assert not any(tell in drawn for tell in PHOTO_TELLS)


def test_the_photographic_look_still_carries_the_photographic_tells():
    from prompt_builder import PHOTO_TELLS

    photo = build_image_prompt(SHOTS[0], LOOKS["photo"], ENTITIES)
    assert all(tell in photo for tell in PHOTO_TELLS)


def test_the_drawn_look_does_not_describe_itself_as_photographed():
    """A model reading "Shot on charcoal" hedges towards a photograph of a
    drawing, which is the one thing neither look wants."""
    drawn = build_image_prompt(SHOTS[0], LOOKS["drawn"], ENTITIES)
    assert "Shot on" not in drawn
    assert "Drawn in" in drawn


def test_both_looks_frame_the_shots_identically():
    """A fair comparison needs the framing held constant. The camera line is the
    shot's, not the look's, so it appears verbatim in both."""
    for shot in SHOTS:
        line = shot.camera.strip().rstrip(".")
        for look in LOOKS.values():
            assert line in build_image_prompt(shot, look, ENTITIES)


@pytest.mark.parametrize("name,look", sorted(LOOKS.items()))
def test_both_looks_hold_the_same_world(name, look):
    """Same case, same weather, same year. Only the medium changes."""
    assert "1999" in look.continuity
    assert "slow motion" in look.motion_grammar


def test_both_prompt_packs_on_disk_are_current():
    import subprocess

    for flag, rel in (([], "PROMPT-PACK.md"), (["--look", "drawn"], "PROMPT-PACK-DRAWN.md")):
        generated = subprocess.run(
            [sys.executable, str(PROJECT / "render.py"), "--all", *flag],
            capture_output=True, text=True, check=True,
        ).stdout
        on_disk = (PROJECT / "docs" / rel).read_text()
        assert on_disk == generated, f"stale: docs/{rel}"


def test_nothing_undescribed_may_appear_in_frame():
    """Found by looking at output, not by reasoning about it. Asked for an empty
    forest track, the model twice put a period estate car on it. In a factual
    programme nobody reads a vehicle at the scene as set dressing — it is the
    killer's car or a police car, and this case's was neither. An invented
    object that carries a claim is a rails breach."""
    prompt = build_image_prompt(SHOTS[0], LOOK, ENTITIES)
    assert "no vehicles, no people" in prompt
    assert "nothing in frame that is not described above" in prompt
