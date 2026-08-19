"""The test episode: look, world registry and shot list.

The five segments are the ones Lasse picked out of the reference episode by
timecode. Each gets a hero shot — the frame he asked to see — plus the shots
around it that show how the whole segment would be built, because a single
frame proves the look and a sequence proves the format.

Descriptions are written from Lasse's own one-line notes on each timecode. The
exact wording of the narration is not in here yet: the audio has not reached
this machine (see README.md). When it does, `subject` lines get rewritten
against the transcript and everything else in this file stands.
"""
from prompt_builder import Entity, Look, Shot

LOOK = Look(
    name="Kold Sankt Hans",
    stock=(
        "Kodak Vision3 500T rated at 320 and processed normal, scanned flat and "
        "graded down"
    ),
    light=(
        "One dominant, motivated source per frame and nothing else: flat overcast "
        "sky outdoors, hard 4000K fluorescent in institutional rooms, sodium or "
        "firelight at night. Shadows stay open and blacks lift to charcoal."
    ),
    palette=(
        "wet greens desaturated towards grey, ash white, weathered timber, "
        "one cold cyan sitting in the shadows, and amber only where a real flame "
        "or a sodium lamp is putting it there"
    ),
    lens_family=(
        "35mm, 50mm and 85mm spherical primes worked near wide open, nothing "
        "wider than 28mm and nothing longer than 135mm"
    ),
    texture=(
        "Fine 35mm grain, faint halation on the highlights, a trace of lens "
        "breathing, focus falling off fast."
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
            "The site is a head-high stack of broken pallets, storm branches and a "
            "discarded panel door, built on the cut edge of a field with the grass "
            "trodden flat in a wide ring around it.",
            anchor="S1-01",
        ),
        Entity(
            "mark",
            "The field",
            "The field is flat, recently cut, hemmed by a dark hawthorn hedge on one "
            "side and a thin line of birch on the other, with a rutted farm track "
            "running out of it.",
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
        segment="03:30-06:00 the site before anything happened",
        subject=(
            "The unlit bonfire stack on the edge of a field, with a child's bicycle "
            "lying on its side in the long grass at the near edge, front wheel still "
            "turned"
        ),
        camera=(
            "35mm at f/2.8, camera at hip height down in the grass looking slightly up "
            "at the stack, stack left of centre and the empty field open to the right"
        ),
        atmosphere=(
            "Late June, half an hour before rain. The air is completely still and the "
            "light is flat and shadowless"
        ),
        entities=("baalplads", "mark"),
        motion="The long grass across the foreground moves once in a slow gust and settles",
        motion_tier="B",
        seconds=6,
    ),
    Shot(
        id="S1-02",
        segment="03:30-06:00 children at the site",
        subject=(
            "Three children at fifty metres, small dark silhouettes against a pale sky, "
            "running past the stack towards the treeline"
        ),
        camera=(
            "85mm at f/4 from across the field, heavy compression, the silhouettes small "
            "and low in the frame"
        ),
        entities=("baalplads",),
        motion="The silhouettes cross the frame right to left and are gone; the grass keeps moving",
        motion_tier="B",
    ),
    Shot(
        id="S1-03",
        segment="03:30-06:00 the morning after",
        subject=(
            "The burnt-out ring the next morning, a low bed of white ash and blackened "
            "timber ends collapsed inward and still giving off thin smoke"
        ),
        camera=(
            "50mm at f/2, camera low and close in to the ash, focus on the near embers "
            "with the field falling out of focus behind"
        ),
        entities=("baalplads",),
        motion="A thread of smoke rises and bends; one ember brightens and dulls",
        motion_tier="B",
    ),
    Shot(
        id="S1-04",
        segment="03:30-06:00 the response arrives",
        subject=(
            "Blue emergency light sweeping across a wet hawthorn hedge and the flattened "
            "grass in front of it, with the vehicle itself out of frame so only the light "
            "and what it touches are visible"
        ),
        camera=(
            "50mm at f/2, locked off, hedge filling the right two-thirds and empty grey "
            "sky at the top left"
        ),
        entities=("mark",),
        motion="The blue light sweeps across the hedge twice at the rhythm of a rotating beacon",
        motion_tier="B",
    ),
    Shot(
        id="S1-05",
        segment="03:30-06:00 the scene is closed",
        subject=(
            "Police tape strung between a fence post and a young birch, running diagonally "
            "across the foreground and thrown out of focus at the near edge, with the "
            "trodden ring in the grass beyond it"
        ),
        camera=(
            "35mm at f/2, camera behind the tape at chest height, tape crossing low-left "
            "to upper-right"
        ),
        entities=("mark",),
        motion="The tape flutters and snaps taut in the wind",
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
        segment="09:34-13:00 what the examination found",
        subject=(
            "A radiograph clipped to a backlit viewing panel in an otherwise dark room, "
            "the image abstracted to soft grey shapes and held out of focus"
        ),
        camera=(
            "85mm at f/1.4, camera close and off-axis with the panel filling the left of "
            "frame and darkness to the right"
        ),
        entities=("retspatologi",),
        motion="The panel's fluorescent tube flickers once as it warms",
        motion_tier="B",
        seconds=4,
    ),

    # ---- Segment 3 — 15:30–17:09 -----------------------------------------
    # "tændvæske i bål, dæk aftryk"
    Shot(
        id="S3-01",
        segment="15:30-17:09 the fire was helped",
        subject=(
            "Fire taking hold at the base of the stack, a low sheet of flame running fast "
            "along one fuel-wet timber while the wood beneath it is still black and unlit"
        ),
        camera=(
            "85mm at f/2.8, camera low and close to the base of the stack, flame filling "
            "the lower half of frame and darkness above"
        ),
        light="The flame is the only source; everything is lit from below and from inside the frame",
        entities=("baalplads",),
        motion="The sheet of flame spreads along the timber from left to right and lifts",
        motion_tier="B",
    ),
    Shot(
        id="S3-02",
        segment="15:30-17:09 what was used",
        subject=(
            "A plastic lighter-fluid bottle lying on its side in wet grass, cap gone and "
            "the label turned away from the lens, grass blades pressed flat under it"
        ),
        camera=(
            "85mm at f/1.8, camera down in the grass at bottle height, bottle left of "
            "centre with focus on the neck"
        ),
        entities=("mark",),
        motion="A last bead of liquid runs from the neck into the grass",
        motion_tier="B",
        seconds=4,
    ),
    Shot(
        id="S3-03",
        segment="15:30-17:09 the accelerant in the timber",
        subject=(
            "Charred timber filling the frame edge to edge with liquid soaking into the "
            "grain, the wet edge advancing across the char and throwing a faint iridescence"
        ),
        camera="Macro-equivalent at f/4, camera directly above the timber, frame filled",
        entities=("baalplads",),
        motion="The wet edge creeps a centimetre further across the char",
        motion_tier="B",
        seconds=4,
    ),
    Shot(
        id="S3-04",
        segment="15:30-17:09 the tyre print",
        subject=(
            "One tyre track pressed deep into wet clay at the edge of a farm track, the "
            "tread pattern sharp and holding standing water, a plastic evidence scale "
            "lying beside it"
        ),
        camera=(
            "35mm at f/4, camera low and raking along the track so the tread stands up in "
            "relief, the track running diagonally out of frame"
        ),
        light=(
            "Low raking sun beneath a heavy sky — the one moment of direct light in the "
            "sequence"
        ),
        entities=("mark",),
        motion="The water standing in the tread trembles as a gust crosses it",
        motion_tier="B",
    ),
    Shot(
        id="S3-05",
        segment="15:30-17:09 where it led",
        subject=(
            "The farm track running away from camera between two hedges into flat white "
            "fog, the double line of ruts filled with water and holding the sky"
        ),
        camera=(
            "50mm at f/2.8, camera centred down in the ruts at knee height with the "
            "vanishing point high in frame"
        ),
        entities=("mark",),
        motion="A slow push forward along the ruts; the fog does not resolve",
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
            "A dented metal jerrycan standing in the corner of a concrete garage with a "
            "dark stain on the floor beneath its spout, dust hanging in a shaft of daylight "
            "from a door out of frame"
        ),
        camera=(
            "50mm at f/2, camera down on the concrete floor looking slightly up, can right "
            "of centre"
        ),
        motion="Dust drifts slowly through the shaft of light",
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
