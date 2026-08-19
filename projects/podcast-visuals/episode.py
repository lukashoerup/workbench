"""The test episode: look, world registry and shot list.

The episode
-----------
*Danske Drabssager* s6e5, "Det Brændende Lig", 29 March 2022, 44:37.

**Identification confirmed 19 Aug 2026 against the audio.** Four of Lasse's
five timecodes are matched by content in the transcript, in his order: the
children and the burning bonfire, the forensic pathologist, the lighter fluid
and the tyre track, and the sweating men disposing of her. The fifth — the
prosecutor at 36:40 — falls past the transcript's cut, but Anne Birgitte
Stürup is in the episode's contributor list. The question is closed.

The transcript itself is **not in this repo**: it is a verbatim transcript of a
commercial podcast and this repository is public. It lives in Lukas's Drive.
Only short quotations appear here, to justify a shot.

What the audio actually says
----------------------------
Late September 1999, a forest near Køge. Children playing in pouring rain see a
large bonfire burning with high flames and something lying in it. Køge police
call in Rejseholdet; the fire brigade is called both to put the fire out and to
tent the site against the rain. In the fire, a bundle about 70 cm across,
wrapped in plastic, fabric and carpet.

At Retsmedicinsk Institut in the Teilum building on Frederik den 5.s Vej, in
the section room they call *Drabstuen*, Hans Petter Hougen finds a woman: the
front of her burnt away where she lay against the fire, the back largely
intact, several skull fractures and severe brain injury — and **no soot in the
airways**, so she was already dead when she was put on the fire. Blunt force,
several impressions in the skull. Forensic anthropologists under Niels
Lynnerup add age, that she had borne children, and — by strontium analysis —
that she grew up in Iran, Iraq or Turkey. Forensic odontologists map her teeth;
the press is told she was midway through extensive dental work; a Copenhagen
dentist recognises an Iranian patient who stopped coming. That is the match.

She was 29, married to an Iranian man, three small daughters, a kiosk in inner
Copenhagen. He never reported her missing. The weapon was a seven-kilo club
kept for Iranian martial arts or for defending the kiosk. Blood had run between
the floorboards of the back room, under a moved piece of furniture, and the
floor had been washed. Lighter fluid was bought in quantity between Copenhagen
and Køge; the melted bottle was left in the fire and went to Teknologisk
Institut for analysis. A tyre impression in the wet forest floor was cast in
plaster, traced through the tyre importers' association to a VW Golf or Polo,
and matched 100% to the Golf belonging to a friend — parked across the street
from the kiosk — who was charged with complicity.

On 30 September 1999 Ekstra Bladet published a photograph of her burnt, unknown
face to get her identified. That decision is the episode's hardest thread, and
the one image this production will never generate (docs/RAILS.md).

What is fact and what is direction
----------------------------------
Almost everything below is now `audio`. The weather was a guess and the audio
confirmed it outright — "regnen står ned i stænger", "rejnværstunge september",
"rigtig dårlig vejr". So was the forensic odontology, which the audio makes
central rather than incidental. The date moves the look from "recent past" to
**late September 1999**, which is a real change: period cars, period clothing,
a 1999 kiosk, a 1999 front page.

Still unverified: everything in segment 5. The transcript stops at 30 minutes —
the free tier's limit — so the prosecutor is not in it.
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
        "daylight through a soaked canopy outdoors, hard 4000K fluorescent in "
        "institutional rooms, sodium and forecourt light at night, firelight where "
        "something is burning. Shadows stay open and blacks lift to charcoal."
    ),
    palette=(
        "soaked forest greens desaturated towards grey, wet black bark, the "
        "grey-white of sodden ash, one cold cyan sitting in the shadows, and amber "
        "only where a real flame or a sodium lamp is putting it there"
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
        "Everything happens inside one wet stretch of late September 1999 — the "
        "night the body is driven south, and the grey day the children find the "
        "fire. Rain falls or has just fallen in every frame, indoors and out; "
        "there is no break in the weather and nothing in the sky. Period is 1999 "
        "Denmark and it is visible: cars, clothing, signage and fittings of the "
        "late nineties, no flat screens, no mobile phones with screens. Interiors "
        "carry the same cold cyan in the shadows and the same open blacks as the "
        "forest, so a cut from the wood to a tiled room does not jar."
    ),
    motion_grammar=(
        "Everything that moves, moves in slight slow motion — roughly half real "
        "speed, as if filmed at 48 frames and played at 24. Rain, flame, water, "
        "dust, fabric and smoke all fall and drift more slowly than they should, "
        "with the weight kept: nothing floats, nothing hangs. The camera itself "
        "moves at ordinary speed. The clip holds a single continuous speed "
        "throughout — it never ramps, never speeds up at the end and never comes "
        "back to normal."
    ),
    breaks_continuity=(
        "sun", "sunlight", "sunlit", "sunny", "sunshine", "sunset", "sunrise",
        "golden hour", "blue sky", "clear sky", "summer", "snow",
        "smartphone", "mobile phone", "flat screen", "LED",
    ),
    format="16:9 for broadcast, composed with clear space on one side for lower-thirds",
)

ENTITIES = {
    e.id: e
    for e in (
        Entity(
            "baalplads",
            "The bonfire site",
            "The fire is a big heap of cut branches and firewood built down in a "
            "natural hollow off a forestry track, burning hard with high flames in "
            "spite of the rain, with the ground around it churned to mud.",
            anchor="S1-01",
        ),
        Entity(
            "skoven",
            "The forest",
            "The wood is Danish mixed plantation south of Copenhagen — wet spruce on "
            "one side, beech on the other, deep soft leaf litter underfoot strewn with "
            "the rubbish a roadside wood collects, and a rutted forestry track running "
            "through it, everything soaked through.",
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
            "kiosken",
            "The kiosk",
            "The kiosk is a small 1999 Copenhagen corner shop: wire racks, a chest "
            "freezer, cigarette shelves behind the counter, worn lino at the front and "
            "bare painted floorboards in the back room.",
            anchor="X-02",
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
    # ---- Segment 1 — 03:30–06:00 ------------------------------------------
    # "legede børn og bål og beredskab på gerningsstedet"
    # "de bliver opmærksomme på et kæmpebål med meget høje flammer … selvom
    #  regnen står ned i stænger"
    Shot(
        id="S1-01",
        source="audio",
        segment="03:30-06:00 what the children walked up to",
        subject=(
            "A big bonfire burning hard with high flames down in a hollow off a forestry "
            "track, driving rain falling straight through the fire and turning to steam "
            "above it"
        ),
        camera=(
            "35mm at f/2.8, camera on the track at chest height some twenty metres back, "
            "fire low and left of centre with the wet track running out to the right"
        ),
        atmosphere=(
            "Rain coming down hard through bare branches, the whole wood soaked and the "
            "light flat and shadowless under the canopy"
        ),
        entities=("baalplads", "skoven"),
        motion="Rain drives through the flames and lifts off them as steam; the fire holds",
        motion_tier="B",
        seconds=6,
    ),
    Shot(
        id="S1-02",
        source="audio",
        segment="03:30-06:00 the children",
        subject=(
            "Two children seen from behind at forty metres, small dark shapes stopped "
            "still on the wet forestry track, a bicycle lying on its side beside them"
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
    # "sådan en skov, der er fyldt med kondomer, kapsler, plastik … flasker,
    #  skrald, cigaretpakker og alt muligt"
    Shot(
        id="S1-03",
        source="audio",
        segment="03:30-06:00 a scene with no edges",
        subject=(
            "The forest floor close up: sodden leaf litter with bottle caps, a crushed "
            "plastic bottle, a cigarette packet gone soft and a scrap of wrapper trodden "
            "into the mould, a numbered evidence marker standing among them"
        ),
        camera=(
            "50mm at f/2, camera down on the litter looking along the ground, marker "
            "sharp and the rubbish falling away either side"
        ),
        entities=("skoven",),
        motion="Rain strikes the leaf litter and darkens it in patches",
        motion_tier="B",
    ),
    # "man får tilkaldt beredskab … prøver at overdække … og få slukket, men
    #  også for at sikre sporene" / "dækket over med presenning, fordi det er
    #  styrtregn"
    Shot(
        id="S1-04",
        source="audio",
        segment="03:30-06:00 the site is tented against the rain",
        subject=(
            "A tarpaulin rigged on poles over the hollow to keep the rain off the scene, "
            "sagging and pooling with water, lit from beneath by work lamps so the "
            "underside glows against the dark wood"
        ),
        camera=(
            "35mm at f/2.8, camera outside the tarpaulin at chest height and slightly "
            "below, the sheet filling the upper half of frame"
        ),
        light=(
            "Work lamps under the tarpaulin, throwing everything upward; grey daylight "
            "failing behind the trees"
        ),
        entities=("skoven",),
        motion="Water gathers in a sag of the tarpaulin and lets go in a single fall",
        motion_tier="B",
    ),
    Shot(
        id="S1-05",
        source="direction",
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

    # ---- Segment 2 — 09:34–13:00 ------------------------------------------
    # "forsigtigt at løfte det op, og nogle flige" — burnt fabric and carpet
    # lifted off, piece by piece
    Shot(
        id="S2-01",
        source="audio",
        segment="09:34-13:00 the forensic examination",
        subject=(
            "A gloved hand lifting the charred edge of a piece of carpet with forceps, "
            "the fabric coming away in a stiff burnt flake, everything beneath it held "
            "out of focus and out of frame"
        ),
        camera=(
            "85mm at f/1.8, camera at table height, very shallow focus held on the "
            "forceps and the flake, hand entering from the right"
        ),
        light=(
            "Hard even 4000K fluorescent from directly overhead, so nothing in frame "
            "casts a shadow with anywhere to go"
        ),
        entities=("retspatologi",),
        motion="The flake comes free and lifts out of frame; nothing else moves",
        motion_tier="B",
    ),
    # "På Frederik den 5.s Vej på Østerbro … i Teilumbygningen lige ved siden af
    #  Rigshospitalet"
    Shot(
        id="S2-02",
        source="audio",
        segment="09:34-13:00 arriving at the institute",
        subject=(
            "A 1960s hospital block of pale concrete and repeating windows seen from the "
            "wet pavement across the road, rain streaking the frame, one lit window on an "
            "otherwise dark elevation"
        ),
        camera=(
            "50mm at f/2.8, camera at head height from across the street, the building "
            "filling the right of frame and running out of the top"
        ),
        light="Flat grey afternoon under heavy cloud, one warm interior window",
        motion="Rain runs down; a car passes through the near foreground out of focus",
        motion_tier="B",
    ),
    # "den sektionsstue de kalder Drabstuen"
    Shot(
        id="S2-03",
        source="audio",
        segment="09:34-13:00 Drabstuen",
        subject=(
            "An empty stainless steel examination table with a drain slot down its centre "
            "and a film of water still lying on the surface, a bank of surgical lights "
            "switched on above it"
        ),
        camera=(
            "50mm at f/2, camera at table height at the foot end, looking down the length "
            "of the table into the lights"
        ),
        light="Hard even 4000K fluorescent, plus the surgical lights burning into the lens",
        entities=("retspatologi",),
        motion="A single drop of water travels down the drain slot",
        motion_tier="B",
    ),
    # "retsodontologerne … tandkort … og så var der et bingo, så var der et match"
    Shot(
        id="S2-04",
        source="audio",
        segment="09:34-13:00 the teeth are what identify her",
        subject=(
            "A row of small dental radiographs clipped side by side to a backlit viewing "
            "panel in an otherwise dark room, and beside them a paper dental chart held "
            "just out of focus, a gloved fingertip resting under one of the little grey "
            "shapes"
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

    # ---- Segment 3 — 15:30–17:09 ------------------------------------------
    # "der fandt man resterne af en flaske, der havde indeholdt tændvæske"
    Shot(
        id="S3-01",
        source="audio",
        segment="15:30-17:09 what was used",
        subject=(
            "The scorched remains of a plastic bottle half sunk in wet grey ash, one side "
            "melted and slumped inward and the label burnt away to nothing, a gloved hand "
            "lowering an opened evidence bag towards it"
        ),
        camera=(
            "85mm at f/1.8, camera down at ash level, bottle left of centre with focus "
            "held on the melted shoulder"
        ),
        entities=("baalplads",),
        motion="Rain strikes the ash around the bottle and darkens it",
        motion_tier="B",
        seconds=5,
    ),
    # "rigtig mange indkøb af lige præcis tændvæske fra København til Køge"
    Shot(
        id="S3-02",
        source="audio",
        segment="15:30-17:09 bought along the way",
        subject=(
            "A shelf of identical lighter-fluid bottles in a late-nineties petrol station "
            "shop, seen at an angle so the labels turn away, one gap in the row where "
            "several have been taken"
        ),
        camera=(
            "50mm at f/2, camera at shelf height and slightly below, the gap sitting just "
            "right of centre"
        ),
        light="Hard fluorescent strip lighting the whole aisle evenly",
        motion="A slow drift along the shelf towards the gap in the row",
        motion_tier="A",
        seconds=5,
    ),
    # "så sender man den på Teknologisk Institut, hvor man laver en analyse for
    #  brændbare væsker"
    Shot(
        id="S3-03",
        source="audio",
        segment="15:30-17:09 the analysis",
        subject=(
            "A sealed nylon evidence bag lying on a laboratory bench with the scorched "
            "bottle inside it, condensation on the inside of the plastic, laboratory glass "
            "out of focus behind"
        ),
        camera=(
            "85mm at f/2, camera at bench height, bag filling the lower left with the "
            "bench running away to the right"
        ),
        light="Hard even 4000K fluorescent from directly overhead",
        motion="A slow drift right along the bench",
        motion_tier="A",
        seconds=4,
    ),
    # "der var dækaftryk af nogle biler … affotografering med målestok på siden af"
    Shot(
        id="S3-04",
        source="audio",
        segment="15:30-17:09 the tyre print",
        subject=(
            "One tyre track pressed deep into soft forest floor where a vehicle turned off "
            "the track, leaf litter and needles compressed down into wet loam, the tread "
            "edge sharp and holding standing water, a plastic evidence scale laid beside it"
        ),
        camera=(
            "35mm at f/4, camera low and raking along the track so the tread stands up in "
            "relief, the impression running diagonally out of frame"
        ),
        light=(
            "A technician's work lamp set low and to one side, raking hard across the "
            "impression so the tread stands up in relief — the one piece of directed light "
            "in the episode, and it is a police lamp, not weather"
        ),
        entities=("skoven",),
        motion="The water standing in the tread trembles as a drip comes off the branches above",
        motion_tier="B",
    ),
    # "og så laver man gipsafstøbninger derude"
    Shot(
        id="S3-05",
        source="audio",
        segment="15:30-17:09 the cast",
        subject=(
            "A set plaster cast being lifted clear of the ground, wet loam and needles "
            "still clinging to its underside where the tread has come away in reverse, two "
            "gloved hands under it"
        ),
        camera=(
            "50mm at f/2, camera low at ground level, the cast lifting towards the lens "
            "and filling the frame as it comes"
        ),
        entities=("skoven",),
        motion="The cast lifts free and turns slightly; loam falls from its underside",
        motion_tier="B",
    ),

    # ---- Segment 4 — 20:17–21:05 ------------------------------------------
    # "Sveden løber fra panden, mens de arbejder. Løfter den døde, pakker hende
    #  ind, gemmer hende væk." — the disposal, not an interrogation.
    Shot(
        id="S4-01",
        source="audio",
        segment="20:17-21:05 the men working",
        subject=(
            "A bare forearm and the back of a neck under a bare bulb, sweat standing on "
            "the skin and running into the collar, the head cropped away above and the "
            "room behind gone to black"
        ),
        camera=(
            "85mm at f/1.8, camera close and behind at shoulder height, the neck filling "
            "the right of frame, everything else unlit"
        ),
        light="One bare bulb overhead, hard and close, nothing else lit at all",
        motion="A bead of sweat runs down into the collar; the shoulder shifts once",
        motion_tier="B",
    ),
    # "bliver lagt i en dyne, en sovepose og en stor sæk"
    Shot(
        id="S4-02",
        source="audio",
        segment="20:17-21:05 what she was wrapped in",
        subject=(
            "A duvet, a sleeping bag and a large woven sack laid out flat and empty on "
            "bare painted floorboards, in the order they will be used, a roll of plastic "
            "sheeting standing at the edge of frame"
        ),
        camera=(
            "35mm at f/2.8, camera high and looking almost straight down, the three "
            "objects filling the frame end to end"
        ),
        light="One bare bulb overhead",
        entities=("kiosken",),
        motion="A slow push straight down towards the floorboards",
        motion_tier="A",
        seconds=6,
    ),
    # "Sammen bærer de hende ud i bilen og kører syd for København"
    Shot(
        id="S4-03",
        source="audio",
        segment="20:17-21:05 the car",
        subject=(
            "The open boot of a late-nineties hatchback at night in rain, the interior "
            "bulb the only light in it, the boot floor bare and the back seats already "
            "folded down"
        ),
        camera=(
            "50mm at f/2, camera at bumper height directly behind the car, the boot "
            "opening filling the centre of frame"
        ),
        light="The boot bulb alone, with wet sodium street light falling in from behind camera",
        motion="Rain crosses the light in the boot opening; nothing else moves",
        motion_tier="B",
    ),
    # "Undervejs standser de ved flere tankstationer. Ikke for at købe hotdogs
    #  eller tanke op. De har en helt anden plan."
    Shot(
        id="S4-04",
        source="audio",
        segment="20:17-21:05 the stops along the way",
        subject=(
            "A petrol station forecourt at night in heavy rain, seen from across the road, "
            "one hatchback standing at a pump with nobody at it, the whole forecourt "
            "burning white against the wet black road"
        ),
        camera=(
            "50mm at f/2 from across the road at head height, forecourt small and central "
            "with the wet road filling the lower third and throwing it all back"
        ),
        light="The forecourt canopy lights are the only source; everything outside them is unlit",
        motion="Rain crosses the forecourt light; a car passes through the near foreground",
        motion_tier="B",
        seconds=6,
    ),
    # "I skoven finder de en egen fordybning, og gør bålet klar. Oven på brænde
    #  og kviste …"
    Shot(
        id="S4-05",
        source="audio",
        segment="20:17-21:05 the fire is built",
        subject=(
            "Cut branches and firewood stacked ready and unlit in a natural hollow in the "
            "forest at night, rain falling on it, torchlight coming in low from one side"
        ),
        camera=(
            "35mm at f/2, camera down in the hollow at the level of the stacked wood, the "
            "stack left of centre and the black wood beyond"
        ),
        light="A single torch beam from outside the frame, raking low across the wood",
        entities=("baalplads", "skoven"),
        motion="Rain falls through the torch beam; the beam moves a little across the stack",
        motion_tier="B",
    ),

    # ---- Segment 5 — 36:40–39:36 ------------------------------------------
    # NOT in the transcript: it stops at 30 minutes. These stand on Lasse's
    # note "anklager" and on the contributor list, and should be rewritten when
    # the rest of the audio is transcribed.
    Shot(
        id="S5-01",
        source="notes",
        segment="36:40-39:36 the prosecution (segment not yet transcribed)",
        subject=(
            "An empty courtroom in the morning before anyone has come in, the long bench "
            "and the rows of plain chairs standing in high flat window light, rain running "
            "down the tall windows"
        ),
        camera=(
            "35mm at f/2.8, camera at seated height in the public gallery, bench left of "
            "centre and the windows at the right edge"
        ),
        entities=("retssal",),
        motion="Rain runs down the window glass; the light on the bench shifts very slightly",
        motion_tier="B",
        seconds=6,
    ),
    Shot(
        id="S5-02",
        source="notes",
        segment="36:40-39:36 the case as paper (segment not yet transcribed)",
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
        source="notes",
        segment="36:40-39:36 the prosecutor speaks (segment not yet transcribed)",
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

    # ---- Extra — outside Lasse's five timecodes ---------------------------
    # "Hvem kender denne kvinde? Sådan stod der i Ekstra Bladet den 30.
    #  september 1999." The photograph is the one image we will never generate.
    Shot(
        id="X-01",
        source="audio",
        segment="extra — the decision that felt brutal",
        subject=(
            "A bundle of the next morning's newspapers dropped on a wet pavement outside "
            "a shuttered kiosk, still bound with plastic strapping, the top copy lying "
            "printed side down so the whole front page is pressed against the ground"
        ),
        camera=(
            "50mm at f/2, camera down at kerb height on the pavement, the bundle right of "
            "centre with the shop front out of focus behind"
        ),
        atmosphere="Early, before anyone is about; standing water on the paving stones",
        motion="Rain lands on the plastic strapping and beads along it",
        motion_tier="B",
        seconds=5,
    ),
    # "vi flyttede et møbel, og nede bag ved møblet kunne man se blodstænk …
    #  det så nemt ud, som om det var rengjort"
    Shot(
        id="X-02",
        source="audio",
        segment="extra — the back room of the kiosk",
        subject=(
            "Bare painted floorboards in a small back room, scrubbed noticeably cleaner "
            "than the skirting and the corners around them, and one clean rectangle in the "
            "dust where a cabinet has been pulled away from the wall"
        ),
        camera=(
            "35mm at f/2.8, camera low in the corner looking along the boards towards the "
            "gap where the cabinet stood"
        ),
        light="One overhead bulb and a strip of grey daylight from a doorway out of frame",
        entities=("kiosken",),
        motion="A slow push towards the gap at the wall",
        motion_tier="A",
        seconds=6,
    ),
)



# A second look, to be tested against the first on the same eight frames.
#
# The argument for it is not only taste. A drawing cannot be mistaken for
# archive, which removes most of the ethical and regulatory weight in one move;
# it has no uncanny valley to fall into; and it does not look like everybody
# else's AI. The argument against is that it can slide into "true crime comic",
# and that it is harder to intercut with real talking heads. Which is why it is
# a test and not a decision.
#
# Courtroom sketch is the reference that matters: it is the one drawn form this
# genre already treats as legitimate reporting.
LOOK_DRAWN = Look(
    name="Kul og blæk",
    stock=(
        "Charcoal, graphite and diluted India ink on heavy grey-toned paper, worked "
        "fast and left unresolved — construction lines still visible, edges "
        "unfinished, smudges and the print of a hand in the tone, the tooth of the "
        "paper reading through everything. In the tradition of courtroom sketch "
        "rather than illustration"
    ),
    light=(
        "Light is what has been left blank, not what has been drawn. One direction "
        "of light per image and no other. Darks are deep, smudged and completely "
        "illegible — nothing is described inside them."
    ),
    palette=(
        "the black of charcoal, the warm grey of the paper it is drawn on, and white "
        "chalk used sparingly on the few things that catch light; one bled "
        "rust-orange, and only where something is actually burning"
    ),
    lens_family=(
        "composed as a photograph would be — 35mm, 50mm and 85mm equivalents, the "
        "subject small in the frame with a lot of empty paper around it, never a "
        "comic panel and never a page of them"
    ),
    texture=(
        "The tooth of the paper visible throughout, dry-brush breaks where the ink "
        "ran out, drips allowed to run and dry, line weight varying constantly and "
        "some passages barely drawn at all."
    ),
    continuity=(
        "Everything happens inside one wet stretch of late September 1999 — the "
        "night the body is driven south, and the grey day the children find the "
        "fire. Rain falls or has just fallen in every image. Period is 1999 Denmark "
        "and it shows in the shapes of the cars, the clothing and the fittings. "
        "Every drawing is on the same grey paper in the same hand, so a cut from "
        "the wood to a tiled room does not jar."
    ),
    breaks_continuity=(
        "sun", "sunlight", "sunlit", "sunny", "sunshine", "sunset", "sunrise",
        "golden hour", "blue sky", "clear sky", "summer", "snow",
        "smartphone", "mobile phone", "flat screen", "LED",
    ),
    motion_grammar=(
        "Movement is limited and deliberate, the way hand-drawn animation is: the "
        "line itself boils very slightly, as though every frame were redrawn, at "
        "around eight to twelve drawings a second, while any camera move runs "
        "smooth. Whatever actually moves — rain, flame, smoke, water — moves in "
        "slight slow motion, roughly half real speed, and keeps its weight. The clip "
        "holds one speed throughout; it never ramps and never resolves into smooth "
        "three-dimensional motion."
    ),
    anti_tells=(
        "not vector-clean, no even-weight outlines, no digital smoothness",
        "no comic-book inking, no cross-hatching used as a shading fill, no halftone",
        "no concept-art or fantasy-illustration polish, nothing rendered",
        "not symmetrical, not centred, no glowing edges, no colour outside the palette",
        "no cartoon faces, no caricature, no stylised eyes",
    ),
    medium_lead="Drawn in",
    frame_lead="Framing",
    format="16:9 for broadcast, composed with clear space on one side for lower-thirds",
)

# The two looks under test. Same 24 shots, same rails, same continuity — the
# only variable is the medium, which is the point.
LOOKS = {"photo": LOOK, "drawn": LOOK_DRAWN}

# The frame Lasse asked to see for each timecode, plus the two extras. Segment 3
# gets two because his note named two distinct things.
HEROES = ("S1-01", "S2-01", "S3-01", "S3-04", "S4-01", "S5-01", "X-01", "X-02")
