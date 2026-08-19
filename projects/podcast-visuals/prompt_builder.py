"""Build image and motion prompts for AI-visualised true crime.

The quality problem this solves
------------------------------
An episode needs a few hundred shots. Written one at a time by hand they drift:
different light, different grade, different lens language — three hundred AI
pictures instead of one programme. Written by a template that re-describes the
look each time, they go generic, which is the other failure mode.

So the look is written **once**, as a frozen block, and pasted byte-identical
into every prompt. Recurring places and objects live in a registry and are
inserted verbatim rather than re-invented per shot. What varies per shot is
only what should vary: what is in frame, and where the camera is.

This is the `promptBuilder` idea from the ImageBooks repo, with one change that
matters here: the registry holds **places and objects**, not characters. True
crime does not need a consistent face — it needs a consistent world, and
consistent faces are the part that is legally and editorially radioactive
(docs/RAILS.md).

Stdlib only, per the workbench contract.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# Content this production never generates, in any shot, for the reasons in
# docs/RAILS.md. Appended to every prompt; a shot cannot opt out.
FORBIDDEN = (
    "no recognisable human face, no portrait, no eye contact with camera",
    "no depiction of a body, no wounds, no blood, no gore",
    "no legible text, no signage, no logos, no brand marks, no watermarks",
    "no news-graphic or true-crime-poster styling",
)

# The tells that make an image read as "AI" rather than as footage. Naming them
# as exclusions is more reliable than hoping the positive prompt outruns them.
ANTI_SLOP = (
    "not symmetrical, not centred, not a hero composition",
    "no HDR glow, no bloom, no lens flare, no rim-light halo",
    "no glossy plastic surfaces, no over-clean textures",
    "no drone or god's-eye viewpoint",
    "no crushed blacks, no orange-and-teal grade",
)


@dataclass(frozen=True)
class Look:
    """The frozen style block. One per production. This is the steering wheel:
    change a line here and every shot in the episode changes with it."""

    name: str
    stock: str          # film stock and grade
    palette: str        # colours that are allowed to appear
    light: str          # the default lighting logic
    lens_family: str    # the lens set, so focal lengths stay in one language
    texture: str        # grain, softness, imperfection
    format: str = "16:9, broadcast delivery"

    # The world state — season, weather, hour, era. Frozen like the rest of the
    # block, because a look can be perfectly consistent and the programme still
    # fall apart if it rains in one shot and not the next.
    continuity: str = ""

    # Words that contradict the continuity above. Checked against every shot
    # before a prompt is built, so a stray "low sun" cannot survive to the
    # render. Cheaper than noticing it on a television three weeks later.
    breaks_continuity: tuple[str, ...] = ()

    def block(self, include_light: bool = True) -> str:
        """The frozen block, pasted byte-identical into every prompt.

        `include_light` goes False when the shot states its own source. Sending
        both the general rule and the specific instance makes the model average
        the two, which is how an institutional interior ends up with a hint of
        overcast sky in it.
        """
        light = f"{self.light} " if include_light else ""
        continuity = f"{self.continuity} " if self.continuity else ""
        return (
            f"Shot on {self.stock}. {continuity}{light}"
            f"Palette: {self.palette}. Lenses: {self.lens_family}. "
            f"{self.texture} Framed {self.format}."
        )


@dataclass(frozen=True)
class Entity:
    """A place or object that recurs across the episode. Its description is
    written once and pasted verbatim wherever it appears, which is what stops
    the crime scene being a different clearing every time we cut back to it.

    `anchor` names the shot whose approved frame becomes the visual reference
    for every later shot in the same place. Words alone will not hold a location
    across a dozen frames; an approved image passed back in as a reference will.
    The flagship image models take up to ten reference images, and using them is
    the single largest quality lever available — so the anchor shot is generated
    and approved first, and everything else in that location is conditioned on
    it.
    """

    id: str
    display: str
    description: str
    anchor: str = ""      # shot id whose approved frame conditions the rest


@dataclass(frozen=True)
class Shot:
    """One frame. `subject` is written as a camera report, not as a caption:
    what the lens sees, not what the scene means."""

    id: str
    segment: str                       # which narration beat it serves
    subject: str
    camera: str                        # focal length, stop, height, angle
    light: str = ""                    # overrides Look.light when the scene needs it
    atmosphere: str = ""               # weather, air, particulates
    entities: tuple[str, ...] = ()     # ids into the registry
    motion: str = ""                   # the ONE physical event, for the video pass
    motion_tier: str = "A"             # A parallax | B micro-motion | C generative
    seconds: float = 5.0


class UnsafeShot(ValueError):
    """Raised when a shot asks for something the rails forbid."""


# Phrases that mean "a person's face is in this frame". Checked before a prompt
# is ever built, because the cheapest place to catch a rail breach is here —
# not in a select session after the credits have already been spent.
_FACE_PATTERNS = (
    r"\bface\b", r"\bfaces\b", r"\bportrait\b", r"\bfacial\b",
    r"\bhis eyes\b", r"\bher eyes\b", r"\btheir eyes\b",
    r"\blooking (?:at|into) (?:the )?camera\b",
    r"\bclose-?up of (?:a |the )?(?:man|woman|boy|girl|child|suspect|victim)\b",
)

_BODY_PATTERNS = (
    r"\bthe body\b", r"\bcorpse\b", r"\bdead body\b", r"\bwound\b",
    r"\bblood\b", r"\bbruis", r"\bautopsy incision\b",
)


def check_shot(shot: Shot) -> None:
    """Reject a shot that breaches the editorial rails.

    Deliberately blunt: false positives are cheap (reword the shot), a false
    negative is a frame of a real person's face in a programme about a real
    killing.
    """
    text = f"{shot.subject} {shot.atmosphere} {shot.motion}".lower()
    for pattern in _FACE_PATTERNS:
        if re.search(pattern, text):
            raise UnsafeShot(
                f"{shot.id}: names a face or a portrait "
                f"(matched /{pattern}/). Reframe to hands, back, silhouette or "
                f"the object. See docs/RAILS.md."
            )
    for pattern in _BODY_PATTERNS:
        if re.search(pattern, text):
            raise UnsafeShot(
                f"{shot.id}: depicts a body or an injury "
                f"(matched /{pattern}/). Show the aftermath, the room or the "
                f"instrument instead. See docs/RAILS.md."
            )


class ContinuityBreak(ValueError):
    """Raised when a shot contradicts the production's frozen world state."""


def check_continuity(shot: Shot, look: Look) -> None:
    """Reject a shot that fights the established weather, hour or season.

    Consistency across scenes is the whole difference between one programme and
    three hundred pictures, and it does not erode in the look — it erodes here,
    one plausible-sounding shot at a time. A single "low raking sun" in an
    episode established as overcast and wet reads as a continuity error to every
    viewer, whether or not they could name what was wrong.
    """
    text = f"{shot.subject} {shot.light} {shot.atmosphere} {shot.motion}".lower()
    for word in look.breaks_continuity:
        if re.search(rf"\b{re.escape(word)}\b", text):
            raise ContinuityBreak(
                f"{shot.id}: '{word}' contradicts the established continuity "
                f"({look.continuity.strip()!r}). Motivate the light from "
                f"something in the scene instead."
            )


def _entity_block(shot: Shot, registry: dict[str, Entity]) -> str:
    missing = [e for e in shot.entities if e not in registry]
    if missing:
        raise KeyError(f"{shot.id}: unknown entities {missing}")
    return " ".join(registry[e].description for e in shot.entities)


def reference_frames(shot: Shot, registry: dict[str, Entity]) -> tuple[str, ...]:
    """Which approved frames to attach as visual references for this shot.

    A shot never references itself: an anchor shot is generated cold, judged,
    and only then becomes the reference for its neighbours.
    """
    missing = [e for e in shot.entities if e not in registry]
    if missing:
        raise KeyError(f"{shot.id}: unknown entities {missing}")
    return tuple(
        registry[e].anchor
        for e in shot.entities
        if registry[e].anchor and registry[e].anchor != shot.id
    )


def build_image_prompt(shot: Shot, look: Look, registry: dict[str, Entity] | None = None) -> str:
    """The still. Layered rather than prose: subject, then camera, then the
    frozen look, then what must not appear."""
    check_shot(shot)
    check_continuity(shot, look)
    registry = registry or {}

    parts = [shot.subject.strip().rstrip(".") + "."]

    entities = _entity_block(shot, registry)
    if entities:
        parts.append(entities)

    parts.append(shot.camera.strip().rstrip(".") + ".")

    if shot.light:
        parts.append(shot.light.strip().rstrip(".") + ".")
    if shot.atmosphere:
        parts.append(shot.atmosphere.strip().rstrip(".") + ".")

    parts.append(look.block(include_light=not shot.light))
    parts.append("Negative: " + "; ".join(FORBIDDEN + ANTI_SLOP) + ".")

    return " ".join(parts)


def build_motion_prompt(shot: Shot, look: Look) -> str:
    """The clip. One physical event and one camera move — no more.

    Generative video fails in proportion to how much it has to invent. A shot
    that asks for smoke to drift and nothing else comes back usable most of the
    time; a shot that asks for a person to walk, turn and speak does not.
    """
    check_shot(shot)
    check_continuity(shot, look)
    if not shot.motion:
        raise ValueError(f"{shot.id}: motion tier {shot.motion_tier} needs a motion description")

    return (
        f"Animate the supplied frame. {shot.motion.strip().rstrip('.')}. "
        f"Everything else in frame is still. "
        f"Camera: {shot.camera.strip().rstrip('.')}, moving only as described. "
        f"Duration {shot.seconds:g}s, single continuous take, no cut. "
        f"Preserve the grade and grain of the supplied frame exactly. "
        f"Negative: no new objects entering frame; no morphing; no added people; "
        f"no camera shake beyond a slow handheld drift; "
        + "; ".join(FORBIDDEN) + "."
    )
