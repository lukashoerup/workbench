"""Segment 4 rebuilt — "Bortskaffelsen", 20:17–21:05, under motion doctrine v2.

Why a second pass
-----------------
Lasse watched the first pass and said some of it read as AI, the movement
above all. The research agrees with him: in the CHI 2026 perceptual study it
was *appearance* that actually reduced realism, but *motion* was what viewers
reported. Motion is the thing an audience puts into words, so motion is the
thing that gets us caught.

The three failures the literature names — unnaturally smooth glide, things
that grow or drift, and a camera that moves in ways no camera moves — are all
avoidable, and none of them requires giving up movement. Doctrine v2:

1. **The camera is locked off in the model.** The generated clip is a tripod
   shot. Every camera move is added afterwards in post, on the finished frame.
   That kills the impossible-camera tell outright, and it makes the move
   identical across generated and non-generated shots.
2. **In-frame movement only where the scene physically has some** — rain,
   sweat, a flame, a shadow shifting — and small enough that a viewer notices
   it on the second look, not the first.
3. **Grain and gate weave over everything, generated or not.** This is the
   load-bearing one: once the same grain sits on all eleven shots, a still
   with a camera move and a generated clip are indistinguishable from each
   other. AI video's most consistent signature is that it is too clean.

The passage
-----------
This segment is one continuous piece of narration, and the shot list follows
it beat for beat:

    "Sveden løber fra panden, mens de arbejder. Løfter den døde, pakker hende
    ind, gemmer hende væk. Den døde 29-årige krop bliver lagt i dyner, en
    sovepose og en stor sæk. Sammen bærer de hende ud i bilen og kører syd for
    København. Undervejs standser de ved flere tankstationer. Ikke for at købe
    hotdogs eller tanke op. De har en helt anden plan. I skoven finder de en
    egen fordybning, og gør bålet klar. Oven på brænde og kviste lægger de den
    døde, indpakkede kvinde, og overhælder bylten med brændbar væske. Og så
    tænder de ilden."

Every shot below is `audio`. Nothing here rests on a note or on the case file.

The ending
----------
The narration's last words are "og så tænder de ilden". The last shot does not
show the fire. It shows the stream of fluid still falling, and lets the line
land on it. Withholding the image the sentence promises is the whole thesis of
this production in four seconds.

No skin
-------
Pass one bent the withheld-frame rule for one shot: a neck and a forearm under
a bare bulb, on the argument that a cropped body part is not a person. Both
looks came back with an arm attached to nobody, and it is the shot Lasse
stopped on. So the rule is no longer "less body" but *no bare skin at all* —
enforced in code, not in judgement. Presence is carried by a shadow on a wall,
a soaked collar, a drop landing on a floor. The opening shot of this segment is
now that floor: sweat has been falling on it for a while, and one more drop
lands. It says the same thing and there is nothing in it to get wrong.

No hands
--------
Pass one put a gloved fingertip and a hand lowering an evidence bag in frame
and got away with it. Hands are the single most reliable generative tell, so
this pass has none: where something is being poured, the frame starts below
the bottle.
"""

from prompt_builder import Look, Shot
from episode import LOOK, ENTITIES  # noqa: F401  (registry re-exported for render.py)


MOTION_GRAMMAR_V2 = (
    "The camera does not move at all. This is a locked-off tripod shot: the "
    "framing of the supplied image must hold, edge to edge, unchanged, for "
    "every frame of the clip. No push, no pull, no pan, no tilt, no drift, no "
    "handheld sway, no parallax, no lens breathing. "
    "Only the one described thing moves, and it moves in slight slow motion — "
    "roughly half real speed, with the weight kept: nothing floats, nothing "
    "hangs, nothing drifts free. The movement must be small enough that a "
    "viewer notices it on the second look rather than the first. "
    "Across the whole clip almost nothing changes: the last frame must be "
    "recognisably the same picture as the first. Nothing grows, spreads, "
    "billows, enters the frame or leaves it; no smoke, steam, fog or fire "
    "expands beyond where it already sits in the supplied frame; no light "
    "source brightens, dims or changes colour; no object completes a gesture "
    "or arrives anywhere. "
    "One continuous speed throughout — it never ramps, never speeds up at the "
    "end and never returns to normal."
)

#: The look is the frozen first-pass look with the camera taken out of the
#: model's hands. Everything else — stock, palette, light, period — is
#: byte-identical, because consistency across segments is the point.
LOOK_V2 = Look(
    name=LOOK.name,
    stock=LOOK.stock,
    palette=LOOK.palette,
    light=LOOK.light,
    lens_family=LOOK.lens_family,
    texture=LOOK.texture,
    continuity=LOOK.continuity,
    motion_grammar=MOTION_GRAMMAR_V2,
    anti_tells=LOOK.anti_tells,
    breaks_continuity=LOOK.breaks_continuity,
    format=LOOK.format,
    medium_lead=LOOK.medium_lead,
    frame_lead=LOOK.frame_lead,
    camera_locked=True,
    no_bare_skin=True,
)

_SEG = "20:17-21:05 bortskaffelsen"


SHOTS = (
    Shot(
        id="S4B-01",
        segment=_SEG,
        subject=(
            "A bare grey concrete floor directly under a single hanging bulb, dry "
            "everywhere except for five or six small dark round spots that have "
            "fallen at different times and dried to different depths, and one "
            "fresh wet spot still bright at its edge; nothing else at all is in "
            "the picture — no feet, no legs, no shadow of anyone standing"
        ),
        camera=(
            "50mm at f/2.8, camera looking straight down at the floor from "
            "standing height, the pool of light from the bulb filling the middle "
            "of the frame and falling off to black in the corners"
        ),
        light=(
            "One bare tungsten bulb directly above and out of frame, and nothing "
            "else"
        ),
        motion=(
            "One more drop falls into the lit pool and lands, and nothing else in "
            "the picture changes"
        ),
        motion_tier="B",
        seconds=5,
        source="audio",
    ),
    Shot(
        id="S4B-02",
        segment=_SEG,
        subject=(
            "Two soft human shadows thrown across a bare painted back-room wall by "
            "one bulb behind them, overlapping at the edges; the wall itself is "
            "plain, bare and completely unmarked, and nobody is in the picture"
        ),
        camera=(
            "50mm at f/2.8, camera square to the wall at chest height, the wall "
            "filling the frame and the shadows falling across the middle of it"
        ),
        light="One bare tungsten bulb behind and above the shadows, out of frame",
        motion=(
            "The two shadows shift slightly where they overlap, one soft edge "
            "sliding a few centimetres across the other, and settle"
        ),
        motion_tier="B",
        seconds=4,
        source="audio",
    ),
    Shot(
        id="S4B-03",
        segment=_SEG,
        subject=(
            "A roll of clear plastic sheeting standing on end against a back-room "
            "wall, its loose end unrolled a metre across a concrete floor; the "
            "floor is plain, bare and completely unmarked"
        ),
        camera=(
            "35mm at f/2.8, camera low at floor height a couple of metres back, "
            "the roll left of centre and the unrolled end running towards camera"
        ),
        light="One bare tungsten bulb overhead and out of frame",
        motion="The loose end of the sheeting lifts a centimetre in a draught and settles back",
        motion_tier="A",
        seconds=4,
        source="audio",
    ),
    Shot(
        id="S4B-04",
        segment=_SEG,
        subject=(
            "A steel shelf unit in a kiosk back room, stacked with boxed stock, and "
            "one clean rectangle on the dusty floor beside it where something heavy "
            "has been moved away; every surface is plain, bare and completely "
            "unmarked apart from that dust line"
        ),
        camera=(
            "35mm at f/2.8, camera at chest height three metres back, shelf right "
            "of frame and the clean rectangle low and left"
        ),
        light="One bare tungsten bulb overhead and out of frame",
        entities=("kiosken",),
        motion="",
        motion_tier="A",
        seconds=4,
        source="audio",
    ),
    Shot(
        id="S4B-05",
        segment=_SEG,
        subject=(
            "A heavy patterned duvet, a sleeping bag and a large woven sack laid out "
            "flat side by side on a concrete floor, all three empty and flat, in the "
            "order they are going to be used"
        ),
        camera=(
            "35mm at f/4, camera high and looking almost straight down from standing "
            "height, the three items running across the frame with floor showing "
            "between them"
        ),
        light="One bare tungsten bulb overhead and out of frame",
        motion="",
        motion_tier="A",
        seconds=5,
        source="audio",
    ),
    Shot(
        id="S4B-06",
        segment=_SEG,
        subject=(
            "The open tailgate of a 1999 five-door hatchback at night in rain, the "
            "rear seats folded flat and the load bay empty and lined with a blanket, "
            "the dome light the only light in the picture"
        ),
        camera=(
            "35mm at f/2, camera outside the car at waist height two metres back, "
            "the raised tailgate glass across the top of frame"
        ),
        light=(
            "The car's own dome light and nothing else, falling off to black a metre "
            "outside the load bay"
        ),
        atmosphere="Rain falling steadily, visible as streaks where the dome light catches it",
        motion=(
            "Rain falls through the dome light and one drop runs down the inside of "
            "the raised tailgate glass"
        ),
        motion_tier="B",
        seconds=4,
        source="audio",
    ),
    Shot(
        id="S4B-07",
        segment=_SEG,
        subject=(
            "A car's rear side window at night from inside, completely covered in "
            "running rain, with one distant sodium street light bloomed and "
            "unreadable behind the water; nothing else is legible through the glass"
        ),
        camera=(
            "50mm at f/2, camera inside the car half a metre from the glass, focus "
            "on the water on the glass and not on what is behind it"
        ),
        light="Sodium light from outside, dim and diffused through the water",
        motion="The rain runs down the outside of the glass and the bloomed light behind it stays exactly where it is",
        motion_tier="B",
        seconds=4,
        source="audio",
    ),
    Shot(
        id="S4B-08",
        segment=_SEG,
        subject=(
            "A 1999 petrol station forecourt at night in rain seen from across the "
            "road, one car standing at a pump with nobody at it and nobody anywhere "
            "in the picture, the shop window lit and empty behind"
        ),
        camera=(
            "50mm at f/2.8, camera at chest height across the road, the forecourt "
            "canopy across the top third and wet tarmac in the foreground"
        ),
        light="Forecourt fluorescents under the canopy and the lit shop window, nothing else",
        atmosphere="Rain falling hard enough to be visible in the forecourt light and standing in the tarmac",
        motion=(
            "Rain falls through the forecourt light and one fluorescent tube under "
            "the canopy flickers once"
        ),
        motion_tier="B",
        seconds=5,
        source="audio",
    ),
    Shot(
        id="S4B-09",
        segment=_SEG,
        subject=(
            "A forestry track at night, wet ruts holding standing water, the wet "
            "trunks either side raked by headlights coming from behind the camera; "
            "no vehicle is anywhere in the picture, only its light"
        ),
        camera=(
            "35mm at f/2.8, camera at chest height in the middle of the track "
            "looking straight down it, the light throwing the camera's own long "
            "shadow away up the track"
        ),
        light="Headlights from behind camera and nothing else, falling off to black between the trunks",
        atmosphere="Rain falling steadily and visible in the headlight beam",
        entities=("skoven",),
        motion="",
        motion_tier="A",
        seconds=4,
        source="audio",
    ),
    Shot(
        id="S4B-10",
        segment=_SEG,
        subject=(
            "Cut logs and branches stacked ready in a shallow hollow in the forest "
            "floor, nothing burning and no flame anywhere in the picture, the bark "
            "dark and soaked with rain"
        ),
        camera=(
            "35mm at f/2.8, camera at knee height at the lip of the hollow looking "
            "down into it, the stacked wood filling the lower two thirds"
        ),
        light="Headlights from behind camera raking across the wood, nothing else",
        atmosphere="Rain falling steadily onto the stacked wood",
        entities=("baalplads", "skoven"),
        motion="",
        motion_tier="A",
        seconds=5,
        source="audio",
    ),
    Shot(
        id="S4B-11",
        segment=_SEG,
        subject=(
            "The last third of a thin stream of clear liquid falling through the "
            "frame onto stacked wood in a hollow, the source above the top edge of "
            "frame and not visible; the bark where it lands is already dark and wet, "
            "and there is no flame anywhere in the picture"
        ),
        camera=(
            "85mm at f/2, very close, camera at the lip of the hollow, the falling "
            "stream sharp and the stacked wood behind it falling off soft"
        ),
        light="Headlights from behind camera catching the falling stream, nothing else",
        atmosphere="Rain falling steadily",
        entities=("baalplads",),
        motion="The thin stream of liquid keeps falling at the same rate and the wood it lands on does not change",
        motion_tier="B",
        seconds=4,
        source="audio",
    ),
)


#: The camera move, added in post on the finished frame. Kind, and how far it
#: travels over the whole shot as a fraction of frame width. Nothing here goes
#: past 5%: a move you can see is a move that dates.
MOVES = {
    "S4B-01": ("push", 0.040),
    "S4B-02": ("left", 0.030),
    "S4B-03": ("pull", 0.035),
    "S4B-04": ("right", 0.030),
    "S4B-05": ("push", 0.045),
    "S4B-06": ("push", 0.035),
    "S4B-07": ("pull", 0.030),
    "S4B-08": ("left", 0.035),
    "S4B-09": ("push", 0.050),
    "S4B-10": ("push", 0.040),
    "S4B-11": ("pull", 0.035),
}

#: Total running time, which must match the narration window it serves.
RUNTIME = sum(s.seconds for s in SHOTS)
