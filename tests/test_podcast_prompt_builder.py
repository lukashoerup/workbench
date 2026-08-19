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

from episode import ENTITIES, HEROES, LOOK, SHOTS  # noqa: E402
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


def test_the_prompt_pack_on_disk_is_current():
    """PROMPT-PACK.md is generated. A stale one is worse than none, because it
    is the file a human pastes from."""
    generated = subprocess.run(
        [sys.executable, str(PROJECT / "render.py"), "--all"],
        capture_output=True, text=True, check=True,
    ).stdout
    on_disk = (PROJECT / "docs" / "PROMPT-PACK.md").read_text()
    assert on_disk == generated, "run: python3 render.py --all > docs/PROMPT-PACK.md"
