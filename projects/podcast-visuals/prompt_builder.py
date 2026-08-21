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
    # Also found by looking at output: given a continuity block that says "late
    # September 1999", the model burned "LATE SEPTEMBER 1999 / 02:14 AM" into
    # the corner of the frame. It reads as surveillance or archive footage —
    # the exact thing the rails forbid — and it asserts a time nothing in the
    # case supports. The world state is context, never a caption.
    "no burned-in timecode, no date stamp, no caption, no subtitle, no lower "
    "third, no surveillance or CCTV overlay, no camera-status graphics",
    # And: 16:9 means 16:9. A film-scan border silently crops the deliverable.
    "no letterboxing, no black bars, no film-scan border, no sprocket holes — "
    "the image fills the 16:9 frame edge to edge",
    "no news-graphic or true-crime-poster styling",
    # Found by looking at output: asked for an empty forest track, the model put
    # a period estate car on it, twice. Nobody reads that as set dressing — in a
    # factual programme a vehicle at the scene is the killer's car or a police
    # car, and this case's car was neither. An invented object that carries a
    # claim is a rails breach, not a composition note.
    "nothing in frame that is not described above: no vehicles, no people, "
    "no animals, no buildings, no equipment",
    # The same class again, found in the drawn look: handprints on walls and
    # floors, drag marks, scratches. All invented, all evidential claims, and
    # all borrowed from horror rather than from this case.
    "no handprints, no fingerprints on surfaces, no smears, no drag marks, no "
    "scratches or gouges, no marks of a struggle anywhere",
)

# The tells that make a photographic image read as "AI" rather than as footage.
# Naming them as exclusions is more reliable than hoping the positive prompt
# outruns them. A drawn look needs a completely different list — see
# `Look.anti_tells` — because nothing here describes what gives a drawing away.
PHOTO_TELLS = (
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

    # How the medium and the framing are introduced. "Shot on" and "Lenses" are
    # right for a photograph and faintly ridiculous for a charcoal drawing, and
    # a model reading "Shot on charcoal" will hedge towards a photograph of a
    # drawing, which is the one thing neither look wants.
    medium_lead: str = "Shot on"
    frame_lead: str = "Lenses"

    # The world state — season, weather, hour, era. Frozen like the rest of the
    # block, because a look can be perfectly consistent and the programme still
    # fall apart if it rains in one shot and not the next.
    continuity: str = ""

    # How everything moves. Frozen for the same reason the look is: motion that
    # varies shot to shot reads as a collection of clips, not as an edit. Goes
    # into every motion prompt and nowhere else.
    motion_grammar: str = ""

    # What would give this medium away. Defaults to the photographic tells; a
    # drawn look must supply its own, because "no HDR glow" says nothing about
    # a charcoal drawing and "no vector-clean line" says nothing about a
    # photograph.
    anti_tells: tuple[str, ...] = PHOTO_TELLS

    #: When true the video pass is told the camera is bolted to a tripod, and
    #: the negative list stops making an exception for handheld drift. The
    #: move is then added in post on the finished frame. A camera that moves
    #: in ways no camera moves is one of the three motion tells viewers name,
    #: and it is the one we can simply decline to generate.
    camera_locked: bool = False

    #: When true, no bare human skin may appear in a shot built against this
    #: look. See _SKIN_PATTERNS for why.
    no_bare_skin: bool = False

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
            f"{self.medium_lead} {self.stock}. {continuity}{light}"
            f"Palette: {self.palette}. {self.frame_lead}: {self.lens_family}. "
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


# Where a shot's content came from, best first. The programme is a retelling of
# what a detective says happened, so the narration outranks everything else —
# including research that is more detailed and more interesting. A shot built on
# a good fact from the wrong source is still a shot the episode does not support.
SOURCES = ("audio", "notes", "description", "case", "direction")

SOURCE_MEANING = {
    "audio": "what is actually said in the episode — the only primary source",
    "notes": "Lasse's timecode notes; a human who listened, paraphrasing",
    "description": "the episode's own published description",
    "case": "public reporting about the case, not about this episode",
    "direction": "an art-direction decision, sourced to nothing",
}


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

    # Which tier of SOURCES this shot's content rests on. Recorded per shot so
    # that "we lean on the audio" is an auditable claim rather than a good
    # intention — and so that upgrading a shot after transcription is a visible
    # change rather than a silent one.
    source: str = "direction"


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

# Phrases that put bare human skin in frame. Pass one allowed a neck and a
# forearm on the argument that a cropped body part is not a person, and the
# model produced an arm attached to nobody — in both looks, from the same
# prompt. Skin is where generative image models break, and it breaks in a way
# a viewer reads instantly as fake even when they cannot say why. So under
# doctrine v2 the answer is not "less skin", it is none: presence is carried by
# a shadow, a soaked collar, a drop on the floor. Scoped to what is in the
# picture, not to the camera position — "camera at chest height" is a place to
# stand, not a body in frame.
_SKIN_PATTERNS = (
    r"\bskin\b", r"\bflesh\b",
    r"\bneck\b", r"\bnape\b", r"\bthroat\b", r"\bjaw", r"\bchin\b", r"\bcheek",
    r"\bears?\b", r"\bearlobe\b", r"\bhairline\b", r"\bscalp\b", r"\bforehead\b",
    r"\btemple\b", r"\bbrow\b", r"\bstubble\b", r"\bbeard\b",
    r"\bforearm\b", r"\belbow\b", r"\bwrist\b", r"\bknuckle", r"\bthumb\b",
    r"\bshoulders?\b", r"\btorso\b", r"\bthigh\b", r"\bcalf\b", r"\bankle\b",
    r"\bhands?\b", r"\bfinger", r"\bpalm\b", r"\barms?\b",
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


class UnknownSource(ValueError):
    """Raised when a shot claims a source tier that does not exist."""


def check_source(shot: Shot, transcript_exists: bool = False) -> None:
    """A shot may only claim the audio once there is an audio to claim.

    The temptation this guards against is specific and real: research turns up a
    vivid detail, it goes into a shot, and three weeks later nobody remembers
    that the episode never mentioned it. The programme would then be showing
    something its own narration does not support.
    """
    if shot.source not in SOURCES:
        raise UnknownSource(
            f"{shot.id}: source {shot.source!r} is not one of {SOURCES}"
        )
    if shot.source == "audio" and not transcript_exists:
        raise UnknownSource(
            f"{shot.id}: claims the audio as its source, but no transcript "
            f"exists yet. Downgrade to 'description' or 'case' until it does."
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


def check_skin(shot: Shot, look: Look) -> None:
    """Refuse a shot that puts bare human skin in the picture.

    Only enforced for looks that ask for it: pass one's shot list was approved
    under the older, looser rule and has to keep reproducing.
    """
    if not look.no_bare_skin:
        return
    text = f"{shot.subject} {shot.motion}".lower()
    for pattern in _SKIN_PATTERNS:
        if re.search(pattern, text):
            raise UnsafeShot(
                f"{shot.id}: puts bare skin in frame (matched /{pattern}/). "
                f"Carry the person with a shadow, a soaked collar, a drop on "
                f"the floor — not with a body part. See docs/RAILS.md."
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
    check_skin(shot, look)
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
    parts.append("Negative: " + "; ".join(FORBIDDEN + look.anti_tells) + ".")

    return " ".join(parts)


def build_motion_prompt(shot: Shot, look: Look) -> str:
    """The clip. One physical event and one camera move — no more.

    Generative video fails in proportion to how much it has to invent. A shot
    that asks for smoke to drift and nothing else comes back usable most of the
    time; a shot that asks for a person to walk, turn and speak does not.
    """
    check_shot(shot)
    check_continuity(shot, look)
    check_skin(shot, look)
    if not shot.motion:
        raise ValueError(f"{shot.id}: motion tier {shot.motion_tier} needs a motion description")

    grammar = f"{look.motion_grammar.strip()} " if look.motion_grammar else ""

    if look.camera_locked:
        camera = "Camera: locked off on a tripod, motionless for the whole clip. "
        camera_negative = (
            "no camera movement of any kind — no push, pull, pan, tilt, drift, "
            "sway, parallax or lens breathing; "
        )
    else:
        camera = f"Camera: {shot.camera.strip().rstrip('.')}, moving only as described. "
        camera_negative = "no camera shake beyond a slow handheld drift; "

    return (
        f"Animate the supplied frame. {shot.motion.strip().rstrip('.')}. "
        f"Everything else in frame is still. "
        f"{grammar}"
        f"{camera}"
        f"Duration {shot.seconds:g}s, single continuous take, no cut. "
        f"Preserve the grade and grain of the supplied frame exactly. "
        f"Negative: no new objects entering frame; no morphing; no added people; "
        f"{camera_negative}"
        f"no speed ramp; no time-lapse; no fast motion; "
        + "; ".join(FORBIDDEN) + "."
    )
