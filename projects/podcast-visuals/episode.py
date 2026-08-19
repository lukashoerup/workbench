"""The test episode: look, world registry and shot list.

The case
--------
Identified 19 Aug 2026 from Lasse's timecode notes plus public sources. Two
children find a bonfire burning in a forest in the rain; there is a body in it.
An investigator from Rejseholdet lives a few hundred metres away and is on the
scene fast. The forensic pathologist works on a partly burnt body and calls in a
forensic odontologist, and the teeth turn out to be decisive. An emptied
lighter-fluid bottle is left in the fire and a tyre track is pressed into the
forest floor. The victim is a woman.

The same case is episode one of *Dødens detektiver*, "Liget i bålet" (True Crime
Agency, 2020), which is where most of the corroboration comes from.

**This is the case, not the transcript.** Every visual fact below is sourced;
the wording of the narration is not, because the audio has not reached this
machine (see README.md). The match is strong — bonfire, lighter fluid, tyre
track, children, forensic pathologist and prosecutor all line up with Lasse's
five notes — but it should be confirmed against the episode before anything is
built on it.

The five segments are the timecodes Lasse picked. Each gets a hero shot — the
frame he asked to see — plus the shots around it, because one frame proves the
look and a sequence proves the format.
"""
from prompt_builder import Entity, Look, Shot

LOOK = Look(
    name="Våd aske",
    stock=(
        "Kodak Vision3 500T rated at 320 and processed normal, scanned flat and "
        "graded down"
    ),
    light=(
        "One dominant, motivated source per frame and nothing else: flat grey "
        "daylight filtered down through a soaked canopy outdoors, hard 4000K "
        "fluorescent in institutional rooms, firelight where something is actually "
        "burning. Shadows stay open and blacks lift to charcoal."
    ),
    palette=(
        "soaked forest greens desaturated towards grey, wet black bark, the "
        "grey-white of sodden ash, one cold cyan sitting in the shadows, and amber "
        "only where a real flame is putting it there"
    ),
    lens_family=(
        "35mm, 50mm and 85mm spherical primes worked near wide open, nothing "
        "wider than 28mm and nothing longer than 135mm"
    ),
    texture=(
        "Fine 35mm grain, faint halation on the highlights, a trace of lens "
        "breathing, focus falling off fast."
    ),
    continuity=(
        "The whole episode is one continuous wet grey day in late autumn, some time "
        "in the recent past: rain falling or just fallen, no sun anywhere, no blue in "
        "the sky, standing water on every horizontal surface, and the same soaked "
        "flat light indoors and out. Interiors carry the same cold cyan in the "
        "shadows and the same open blacks as the forest, so a cut from the wood to a "
        "tiled room does not jar."
    ),
    breaks_continuity=(
        "sun", "sunlight", "sunlit", "sunny", "sunshine", "sunset", "sunrise",
        "golden hour", "blue sky", "clear sky", "warm light", "dry", "dusty light",
        "summer", "snow", "moonlight",
    ),
    format="16:9 for broadcast, composed with clear space on one side for lower-thirds",
)

# Places and objects that recur. Written once, pasted verbatim wherever they
# appear — this is what stops the clearing being a different clearing each time
# the programme cuts back to it.
ENTITIES = {
    e.id: e
    for e in (
        Entity(
            "baalplads",
            "The bonfire site",
            "The fire is a low, wide heap of branches and broken pallet wood in a small "
            "clearing off a forestry track, burning badly in the rain so that it gives "
            "far more smoke than flame, with the ground around it churned to mud.",
            anchor="S1-01",
        ),
        Entity(
            "skoven",
            "The forest",
            "The wood is Danish mixed plantation — dark wet spruce on one side, bare "
            "beech on the other, deep soft leaf litter and needles underfoot, a rutted "
            "forestry track running through it, and everything soaked through.",
            anchor="S1-01",
        ),
        Entity(
            "retspatologi",
            "The forensic institute",
            "The rooms are green-grey tile to waist height and cream above, stainless "
            "steel fittings, no daylight anywhere, and a hard even fluorescent that "
            "leaves shadows nowhere to go.",
            anchor="S2-01",
        ),
        Entity(
            "afhoering",
            "The interview room",
            "The room is small and grey: scratched laminate table, two stacking chairs, "
            "a wall-mounted recorder, and one window of closed venetian blinds.",
            anchor="S4-02",
        ),
        Entity(
            "retssal",
            "The courtroom",
            "The courtroom is pale birch panelling and plain chairs under tall windows, "
            "Danish and institutional rather than grand, with the light coming in high "
            "and flat.",
            anchor="S5-01",
        ),
    )
}

SHOTS = (
    # ---- Segment 1 — 03:30–06:00 -----------------------------------------
    # "legede børn og bål og beredskab på gerningsstedet"
    Shot(
        id="S1-01",
        segment="03:30-06:00 what the children walked up to",
        subject=(
            "A low wide bonfire burning badly in steady rain in a small forest clearing, "
            "giving off far more smoke than flame, the smoke hanging low and refusing to "
            "rise through the wet air"
        ),
        camera=(
            "35mm at f/2.8, camera on the forestry track at chest height some twenty "
            "metres back, fire low and left of centre with the wet track running out to "
            "the right"
        ),
        atmosphere=(
            "Steady rain falling through bare branches, the whole wood soaked and the "
            "light flat and shadowless under the canopy"
        ),
        entities=("baalplads", "skoven"),
        motion="Smoke rolls sideways off the heap and settles again; rain keeps falling through it",
        motion_tier="B",
        seconds=6,
    ),
    Shot(
        id="S1-02",
        segment="03:30-06:00 the children",
        subject=(
            "Two children seen from behind at forty metres, small dark shapes stopped "
            "still on the wet forestry track, one bicycle lying on its side beside them"
        ),
        camera=(
            "85mm at f/4 from further down the track, heavy compression, the figures "
            "small and low in frame with the track closing in around them"
        ),
        entities=("skoven",),
        motion="Rain falls through the frame; neither figure moves",
        motion_tier="B",
        seconds=5,
    ),
    Shot(
        id="S1-03",
        segment="03:30-06:00 close on the fire",
        subject=(
            "Wet branches and pallet wood at the edge of the heap, steaming as much as "
            "burning, water running off the bark into the ash below"
        ),
        camera=(
            "85mm at f/2, camera low and close to the edge of the heap, focus held on "
            "the steaming wood with the heart of the fire soft and dark behind"
        ),
        light="Firelight from within the heap, weak and intermittent against the grey daylight",
        entities=("baalplads",),
        motion="Steam lifts off the wet wood in a slow curl; one branch settles",
        motion_tier="B",
    ),
    Shot(
        id="S1-04",
        segment="03:30-06:00 the response arrives",
        subject=(
            "Blue emergency light pulsing through wet spruce trunks from somewhere off "
            "the track, the vehicle itself never in frame, only the light and the water "
            "on the bark it catches"
        ),
        camera=(
            "50mm at f/2, locked off, trunks filling the frame in receding layers with "
            "the light coming from deep behind them"
        ),
        entities=("skoven",),
        motion="The blue light pulses through the trunks at the rhythm of a rotating beacon",
        motion_tier="B",
    ),
    Shot(
        id="S1-05",
        segment="03:30-06:00 the scene is closed",
        subject=(
            "Police tape strung between two spruce trunks across the forestry track, "
            "beaded with rain and sagging under the weight of it, thrown out of focus at "
            "the near edge"
        ),
        camera=(
            "35mm at f/2, camera behind the tape at chest height, tape crossing low-left "
            "to upper-right with the track receding beyond it"
        ),
        entities=("skoven",),
        motion="The tape lifts once in the wind and drops, shedding water",
        motion_tier="B",
    ),

    # ---- Segment 2 — 09:34–13:00 -----------------------------------------
    # "retsmediciner og kig på lig"
    Shot(
        id="S2-01",
        segment="09:34-13:00 the forensic examination",
        subject=(
            "A wet gloved hand lifting a stainless steel instrument from a folded green "
            "cloth on a trolley, with only the hand and the gown cuff in frame and the "
            "rest of the room falling away into soft green-grey"
        ),
        camera=(
            "85mm at f/1.8, camera at trolley height, very shallow focus held on the "
            "instrument, hand entering from the right"
        ),
        light=(
            "Hard even 4000K fluorescent from directly overhead, so nothing in frame "
            "casts a shadow with anywhere to go"
        ),
        entities=("retspatologi",),
        motion="The hand lifts the instrument clear of the cloth and out of frame; nothing else moves",
        motion_tier="B",
    ),
    Shot(
        id="S2-02",
        segment="09:34-13:00 arriving at the institute",
        subject=(
            "An empty institutional corridor with one heavy door standing ajar at the far "
            "end and brighter light behind it"
        ),
        camera=(
            "35mm at f/2.8, camera low and centred in the corridor so the door sits small "
            "at the end of the perspective"
        ),
        entities=("retspatologi",),
        motion="A slow push down the corridor towards the door; the light on the tile shifts very slightly",
        motion_tier="A",
        seconds=6,
    ),
    Shot(
        id="S2-03",
        segment="09:34-13:00 the examination room",
        subject=(
            "An empty stainless steel examination table with a drain slot down its centre "
            "and a film of water still lying on the surface, a folded sheet at the far end"
        ),
        camera=(
            "50mm at f/2, camera at table height at the foot end, looking down the length "
            "of the table"
        ),
        light="Hard even 4000K fluorescent from directly overhead",
        entities=("retspatologi",),
        motion="A single drop of water travels down the drain slot",
        motion_tier="B",
    ),
    Shot(
        id="S2-04",
        segment="09:34-13:00 the teeth are what identify her",
        subject=(
            "A row of small dental radiographs clipped side by side to a backlit viewing "
            "panel in an otherwise dark room, the little grey shapes abstracted and held "
            "slightly out of focus, a gloved fingertip resting under one of them"
        ),
        camera=(
            "85mm at f/1.4, camera close and off-axis with the lit panel filling the left "
            "of frame and darkness to the right"
        ),
        light="The viewing panel is the only source, lighting the hand from the front",
        entities=("retspatologi",),
        motion="The fingertip moves one frame to the left along the row and stops",
        motion_tier="B",
    ),

    # ---- Segment 3 — 15:30–17:09 -----------------------------------------
    # "tændvæske i bål, dæk aftryk"
    Shot(
        id="S3-01",
        segment="15:30-17:09 the fire was helped",
        subject=(
            "One patch of the heap burning hard and clean in the rain while everything "
            "around it only smoulders and steams — a bright wrong heat in a single place"
        ),
        camera=(
            "85mm at f/2.8, camera low and close, the burning patch filling the lower "
            "third with wet smoking wood above and behind it"
        ),
        light="The flame is the only source; everything is lit from below and from inside the frame",
        entities=("baalplads",),
        motion="The clean flame gutters in the rain, holds, and lifts again",
        motion_tier="B",
    ),
    Shot(
        id="S3-02",
        segment="15:30-17:09 what was used",
        subject=(
            "A scorched plastic bottle at the edge of the ash, one side melted and "
            "slumped inward, the label burnt away to nothing, half sunk in wet grey ash"
        ),
        camera=(
            "85mm at f/1.8, camera down at ash level, bottle left of centre with focus "
            "on the melted shoulder"
        ),
        entities=("baalplads",),
        motion="Rain strikes the ash around the bottle and darkens it",
        motion_tier="B",
        seconds=4,
    ),
    Shot(
        id="S3-03",
        segment="15:30-17:09 the accelerant in the timber",
        subject=(
            "Charred timber filling the frame edge to edge, the char broken open to show "
            "the burn running deeper along one line than anywhere around it"
        ),
        camera="Macro-equivalent at f/4, camera directly above the timber, frame filled",
        entities=("baalplads",),
        motion="A drop of rain lands on the char and steams off",
        motion_tier="B",
        seconds=4,
    ),
    Shot(
        id="S3-04",
        segment="15:30-17:09 the tyre print",
        subject=(
            "One tyre track pressed deep into soft forest floor where a vehicle turned "
            "off the track, leaf litter and needles compressed down into wet loam, the "
            "tread edge sharp and holding standing water, a plastic evidence scale laid "
            "beside it"
        ),
        camera=(
            "35mm at f/4, camera low and raking along the track so the tread stands up in "
            "relief, the impression running diagonally out of frame"
        ),
        light=(
            "A technician's work lamp set low and to one side, raking hard across the "
            "impression so the tread stands up in relief — the one piece of directed "
            "light in the episode, and it is a police lamp, not weather"
        ),
        entities=("skoven",),
        motion="The water standing in the tread trembles as a drip comes off the branches above",
        motion_tier="B",
    ),
    Shot(
        id="S3-05",
        segment="15:30-17:09 where it led",
        subject=(
            "The forestry track running away from camera between wet spruce walls into "
            "flat white mist, the double line of ruts filled with water and holding what "
            "little sky there is"
        ),
        camera=(
            "50mm at f/2.8, camera centred down in the ruts at knee height with the "
            "vanishing point high in frame"
        ),
        entities=("skoven",),
        motion="A slow push forward along the ruts; the mist does not resolve",
        motion_tier="A",
        seconds=6,
    ),

    # ---- Segment 4 — 20:17–21:05 -----------------------------------------
    # "sveder, drabsmænd, brandbart væske"
    Shot(
        id="S4-01",
        segment="20:17-21:05 the interview",
        subject=(
            "Two hands on a scratched laminate table, fingers interlaced too tightly and "
            "the knuckles pale, an untouched paper cup of water beside them; above the "
            "wrists the figure is only a dark unlit mass"
        ),
        camera=(
            "50mm at f/1.8, camera at table height directly opposite, hands centred low, "
            "the room behind going to a soft dark mass"
        ),
        light=(
            "One hard fluorescent panel directly overhead so the hands are lit and "
            "everything above them is not"
        ),
        entities=("afhoering",),
        motion="One thumb moves against the other twice and stops",
        motion_tier="B",
    ),
    Shot(
        id="S4-02",
        segment="20:17-21:05 before the interview",
        subject=(
            "The interview room before anyone is in it: two stacking chairs at the table, "
            "the wall recorder, and daylight edging through closed venetian blinds"
        ),
        camera=(
            "35mm at f/2.8, camera in the corner at seated eye level, table to the left "
            "and empty wall to the right"
        ),
        entities=("afhoering",),
        motion="A blade of light from the blinds creeps a few centimetres across the table",
        motion_tier="A",
        seconds=6,
    ),
    Shot(
        id="S4-03",
        segment="20:17-21:05 on the record",
        subject=(
            "A wall-mounted interview recorder with one red indicator lit and dust settled "
            "on the housing"
        ),
        camera=(
            "85mm at f/1.4, camera close and slightly below, recorder to the right of "
            "frame with the wall falling away left"
        ),
        entities=("afhoering",),
        motion="The red indicator pulses slowly",
        motion_tier="B",
        seconds=4,
    ),
    Shot(
        id="S4-04",
        segment="20:17-21:05 the flammable liquid",
        subject=(
            "A shelf in a cold garage lined with household tins and bottles gone furry "
            "with dust, and one clean gap in the dust where something round has been "
            "lifted out"
        ),
        camera=(
            "50mm at f/2, camera at shelf height and slightly below, the gap sitting just "
            "right of centre with the labels all turned away from the lens"
        ),
        motion="Motes drift slowly through the grey light falling from a door out of frame",
        motion_tier="B",
    ),

    # ---- Segment 5 — 36:40–39:36 -----------------------------------------
    # "anklager"
    Shot(
        id="S5-01",
        segment="36:40-39:36 the prosecution",
        subject=(
            "An empty courtroom in the morning before anyone has come in, the long bench "
            "and the rows of plain chairs standing in high flat window light with dust in "
            "the air"
        ),
        camera=(
            "35mm at f/2.8, camera at seated height in the public gallery, bench left of "
            "centre and the windows gently blowing out at the right edge"
        ),
        entities=("retssal",),
        motion="Dust turns slowly in the window light",
        motion_tier="B",
        seconds=6,
    ),
    Shot(
        id="S5-02",
        segment="36:40-39:36 the case as paper",
        subject=(
            "A stack of case binders bound with red cotton tape on a bench, the edges "
            "furred from handling, a pair of reading glasses folded on top"
        ),
        camera=(
            "85mm at f/2, camera at bench height with the stack to the left of frame and "
            "the room out of focus behind"
        ),
        entities=("retssal",),
        motion="A slow drift to the right across the stack",
        motion_tier="A",
    ),
    Shot(
        id="S5-03",
        segment="36:40-39:36 the prosecutor speaks",
        subject=(
            "A dark-suited shoulder and the back of a head at a lectern in the near "
            "foreground, thrown completely out of focus into a soft dark mass, with the "
            "sharp empty bench beyond"
        ),
        camera=(
            "85mm at f/1.8, camera behind and to one side so the figure fills the left "
            "third unreadably"
        ),
        entities=("retssal",),
        motion="The out-of-focus figure shifts weight once",
        motion_tier="B",
    ),
    Shot(
        id="S5-04",
        segment="36:40-39:36 outside the court",
        subject=(
            "The steps of a courthouse in rain seen from across the street through passing "
            "traffic, three or four umbrellas at the top of the steps far too distant to "
            "read as individuals"
        ),
        camera=(
            "135mm at f/4 from across the street, heavy compression, steps small and "
            "central, foreground traffic passing out of focus"
        ),
        atmosphere="Steady rain, standing water on the road throwing the sky back up",
        motion="A car passes through the near foreground and briefly wipes the frame",
        motion_tier="B",
    ),
)

# The frame Lasse asked to see for each timecode. Segment 3 gets two, because
# his note named two distinct things (the accelerant and the tyre print).
HEROES = ("S1-01", "S2-01", "S3-01", "S3-04", "S4-01", "S5-01")
