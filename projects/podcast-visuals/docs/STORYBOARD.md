# Storyboard — the five segments

Lasse named five timecodes and asked to see a frame for each. Each one gets a
**hero frame** — that frame — plus the shots around it, because one frame
proves the look and a sequence proves the format.

22 shots, 111 seconds of picture. The exact prompts are in
[PROMPT-PACK.md](PROMPT-PACK.md), generated from the same data and ordered
anchors-first.

## The episode

**"Det Brændende Lig"** — *Danske Drabssager* season 6 episode 5, 29 March
2022, 44:37. Confirmed against the show's own feed: the only episode of 219
whose length and description fit Lasse's five timecodes.

Its own description, verbatim:

> To børn fik deres livs chok, og leg blev vendt til gru, da de i et bål fandt
> en bylt, som indeholdt de jordiske rester af et menneske. Ugenkendelig,
> dræbt, forbrændt og efterladt. Du hører om en tom flaske tændvæske efterladt
> i et bål, et dækspor i skovbunden og et billede i avisen af en afdød kvindes
> maltrakterede ansigt. Og om beslutninger, der skal træffes, selv om de kan
> virke brutale.

The contributors *are* Lasse's five timecodes: former murder chief **Bent
Isager-Nielsen**, forensic technician **Bent Hytholm Jensen**, professor of
forensic medicine **Hans Petter Hougen**, former prosecutor **Anne Birgitte
Stürup**, host **Stine Bolther**. They are also who would be on camera if the
programme keeps its talking heads.

### Identification: confirmed

Settled 19 Aug 2026 against the audio. Four of Lasse's five timecodes are
matched by content in the transcript, in his order — the children and the
burning bonfire, the forensic pathologist, the lighter fluid and the tyre
track, and the sweating men. The fifth falls past the transcript's cut, but the
prosecutor Anne Birgitte Stürup is in the episode's contributor list. Nothing
further is needed.

One of the matches also corrected a mistake, which is the best evidence the
transcript is doing real work. Lasse's note at 20:17 reads *"sveder,
drabsmænd, brandbart væske"*, and that had been storyboarded as an
interrogation — a suspect sweating under questioning. It is not. The narration
there is the disposal: *"Sveden løber fra panden, mens de arbejder. Løfter den
døde, pakker hende ind, gemmer hende væk."* Two men working at night. That
whole segment was rebuilt.

### The case, as the audio tells it

Late September 1999, a forest near Køge. Children playing in pouring rain see a
large bonfire burning with high flames and something lying in it. Køge police
call in Rejseholdet; the fire brigade comes both to put the fire out and to tent
the site against the rain. In the fire, a bundle about 70 cm across, wrapped in
plastic, fabric and carpet.

At Retsmedicinsk Institut — the Teilum building on Frederik den 5.s Vej, in the
section room they call *Drabstuen* — Hans Petter Hougen finds a woman. The front
of her burnt away where she lay against the fire, the back largely intact.
Several skull fractures, severe brain injury, and **no soot in the airways**: she
was already dead when she was put on the fire. Forensic anthropologists under
Niels Lynnerup add her age, that she had borne children, and by strontium
analysis that she grew up in Iran, Iraq or Turkey. Forensic odontologists map
her teeth; the press is told she was midway through extensive dental work; a
Copenhagen dentist recognises an Iranian patient who stopped coming. That is the
match.

She was 29, married, three small daughters, a kiosk in inner Copenhagen. Her
husband never reported her missing. The weapon was a seven-kilo club kept for
Iranian martial arts or for defending the kiosk. Blood had run between the
floorboards of the back room, under a moved cabinet, and the floor had been
washed. Lighter fluid was bought in quantity along the road from Copenhagen to
Køge; the melted bottle was left in the fire and went to Teknologisk Institut.
A tyre impression in the wet forest floor was cast in plaster, traced through
the tyre importers' association to a VW Golf or Polo, and matched to the Golf of
a friend — parked across the street from the kiosk — who was charged with
complicity.

On 30 September 1999 Ekstra Bladet published a photograph of her burnt,
unidentified face to get her named.

**The transcript is not in this repo.** It is a verbatim transcript of a
commercial podcast and this repository is public. It lives in Lukas's Drive;
only short quotations appear here, to justify a shot.

### What the audio changed

- **The weather was a guess and the audio confirmed it outright.** "Regnen står
  ned i stænger", "rejnværstunge september", "rigtig dårligt vejr". The wet grey
  day was the right call for the wrong reason, and it is now a fact.
- **The date is late September 1999**, not "the recent past". That is a real
  change: period cars, period clothing, a 1999 kiosk, a 1999 front page.
- **The fire was burning hard with high flames** when the children reached it,
  not smouldering. Stronger image, and the true one.
- **The forensic odontology is central**, not incidental. It is what identified
  her. S2-04 went from a hedge to the point of the segment.
- **Segment 4 was rebuilt** from an interrogation to the disposal.
- **New material worth having**: the fire brigade tenting the scene against the
  rain, the littered forest floor, the plaster casts, the petrol station stops,
  the washed floorboards in the kiosk.

### Where each shot's content comes from

The narration outranks everything, including research that is more detailed and
more interesting: this programme is a retelling of what a detective says
happened, so a shot built on a good fact from the wrong source is still a shot
the episode does not support. Every shot therefore records its own tier, and
the test suite enforces it.

| Tier | Meaning | Before | Now |
|---|---|---|---|
| `audio` | what is actually said — the only primary source | 0 | **20** |
| `notes` | Lasse's timecode notes; a human who listened | 6 | 3 |
| `description` | the episode's own published description | 7 | 0 |
| `case` | public reporting about the case, not this episode | 1 | 0 |
| `direction` | an art-direction decision, sourced to nothing | 9 | 1 |

That shift is the measure of whether the transcript did its job, and it is under
test: the suite fails if fewer than 60% of shots rest on the audio.

The three remaining `notes` shots are all of segment 5, and they are the honest
gap — **the transcript stops at 30 minutes**, so the prosecutor at 36:40 is not
in it. A test fails if any segment-5 shot claims the audio. The one `direction`
shot is police tape at the cordon, which nobody says and everybody has seen.

---

## 03:30–06:00 · children, the bonfire, the response
*"legede børn og bål og beredskab på gerningsstedet"*

Nothing in the fire is ever shown. The narration says what is in it; the picture
stays outside.

| | Shot | Src | Tier |
|---|---|---|---|
| **★ S1-01** | **A big bonfire burning hard with high flames down in a hollow off a forestry track, driving rain falling straight through it and turning to steam above.** | audio | **B, 6s** |
| S1-02 | Two children from behind at forty metres, stopped still on the wet track, a bicycle on its side beside them | audio | B |
| S1-03 | The forest floor close up — bottle caps, a crushed bottle, a soft cigarette packet trodden into the leaf mould, an evidence marker among them | audio | B |
| S1-04 | A tarpaulin rigged on poles over the hollow to keep the rain off the scene, lit from beneath by work lamps | audio | B |
| S1-05 | Police tape between two trunks, beaded with rain and sagging under it | direction | B |

S1-01 is the whole thesis in one frame: the most frightening thing in the
episode is happening in it, and none of it is visible. S1-03 answers something
the murder chief says at length — that the wood was full of rubbish and any
piece of it might have come from the killer, so there was no natural edge to the
scene. S1-04 is the fire brigade called for two jobs at once: put it out, and
tent it against the rain.

---

## 09:34–13:00 · the forensic pathologist
*"retsmediciner og kig på lig"*

Nothing here shows a body. The sequence is about **procedure** — cold rooms,
steel, instruments, routine — and procedure is more unsettling than anatomy.

| | Shot | Src | Tier |
|---|---|---|---|
| **★ S2-01** | **A gloved hand lifting the charred edge of a piece of carpet with forceps, the fabric coming away in a stiff burnt flake, everything beneath held out of frame.** | audio | **B, 5s** |
| S2-02 | The 1960s hospital block from the wet pavement across the road, one lit window | audio | B |
| S2-03 | Drabstuen: the empty steel table, drain slot, a film of water, surgical lights burning into the lens | audio | B |
| S2-04 | Dental radiographs on a backlit panel beside a paper dental chart, a gloved fingertip under one of them | audio | B |

S2-01 is what Hougen actually describes doing: lifting burnt fabric and carpet
away flake by flake before anything underneath could be read. S2-04 is no longer
a hedge — the teeth are what identified her, and a Copenhagen dentist
recognising a patient who stopped coming is the break in the case.

---

## 15:30–17:09 · the accelerant and the tyre print
*"tændvæske i bål, dæk aftryk"*

Two heroes, because Lasse's note names two things. This is where the picture can
carry actual evidence-reasoning — and where it is most tempting, and most
forbidden, to fake a forensic photograph.

| | Shot | Src | Tier |
|---|---|---|---|
| **★ S3-01** | **The scorched remains of a plastic bottle half sunk in wet ash, one side melted and slumped, label burnt away, a gloved hand lowering an evidence bag towards it.** | audio | **B, 5s** |
| S3-02 | A shelf of identical lighter-fluid bottles in a late-nineties petrol station, labels turned away, one gap in the row | audio | B, 4s |
| S3-03 | A sealed nylon evidence bag on a laboratory bench, condensation inside the plastic | audio | A, 4s |
| **★ S3-04** | **One tyre track pressed into soft forest floor, tread edge sharp and holding water, evidence scale beside it, raked by a technician's work lamp.** | audio | **B, 5s** |
| S3-05 | A set plaster cast lifting clear of the ground, wet loam still clinging where the tread came away in reverse | audio | B |

S3-02 is sourced to a specific line: lighter fluid was bought in quantity all
along the road from Copenhagen to Køge. S3-05 is the plaster casting the
forensic technician describes, and it is the most tactile shot in the episode —
evidence being physically lifted out of the ground.

S3-04 is the one piece of hard directional light in the whole programme, and it
comes from a police lamp physically in the scene, never from weather the episode
has ruled out.

---

## 20:17–21:05 · the disposal
*"sveder, drabsmænd, brandbart væske"*

**This segment was rebuilt.** It had been storyboarded as an interrogation — a
suspect sweating under questioning. The narration is the opposite: two men
working at night. *"Sveden løber fra panden, mens de arbejder. Løfter den døde,
pakker hende ind, gemmer hende væk."*

| | Shot | Src | Tier |
|---|---|---|---|
| **★ S4-01** | **A bare forearm and the back of a neck under a bare bulb, sweat standing on the skin and running into the collar, the head cropped away above, the room behind gone to black.** | audio | **B, 5s** |
| S4-02 | A duvet, a sleeping bag and a large woven sack laid out flat and empty on bare floorboards, in the order they will be used | audio | A, 6s |
| S4-03 | The open boot of a late-nineties hatchback at night in rain, interior bulb the only light, boot floor bare | audio | B |
| S4-04 | A petrol station forecourt at night in heavy rain from across the road, one car at a pump, nobody at it | audio | B, 6s |
| S4-05 | Cut branches and firewood stacked ready and unlit in the hollow, rain falling on it, torchlight low from one side | audio | B |

S4-01 is the proof of the thesis, and it survived the rebuild intact: two men
under pressure with no identifiable person in frame, and stronger than a face
would have been. S4-02 is the withheld version of the worst moment in the case —
the three things laid out empty, in order, before they are used.

---

## 36:40–39:36 · the prosecutor
*not in the transcript*

The free tier stopped at 30 minutes. These three stand on Lasse's note and on
the contributor list, and should be rewritten when the rest of the audio is
transcribed. A test fails if any of them claims the audio as its source.

| | Shot | Src | Tier |
|---|---|---|---|
| **★ S5-01** | **The empty courtroom in the morning before anyone comes in, high flat window light, rain running down the tall windows.** | notes | **B, 6s** |
| S5-02 | Case binders bound in red tape, edges furred, reading glasses on top | notes | A |
| S5-03 | A dark-suited shoulder at a lectern, thrown right out of focus; the sharp empty bench beyond | notes | B |

---

## Extra · two frames outside the five timecodes

| | Shot | Src | Tier |
|---|---|---|---|
| **★ X-01** | **A bundle of the next morning's papers on a wet pavement outside a shuttered kiosk, still strapped, the top copy printed side down so the whole front page is against the ground.** | audio | **B, 5s** |
| **★ X-02** | **Bare painted floorboards in the back room, scrubbed noticeably cleaner than the skirting around them, and one clean rectangle in the dust where a cabinet was pulled from the wall.** | audio | **A, 6s** |

X-01 is the Ekstra Bladet front page of 30 September 1999, withheld. The episode
turns on the decision to print a dead woman's burnt face so that someone would
name her; that photograph is the one image this production will never generate,
and the frame carries the weight of the decision without reproducing a pixel of
it. A programme asking whether it was right to publish a dead woman's face
cannot itself manufacture one.

X-02 is the same move applied to evidence. Blood had run between those
floorboards and the floor had been washed — the forensic technician's line is
that it *looked like it had been rained on*. The washed floor is the evidence.
Nothing red is in frame.

## What to look for when the frames come back

In review order, because this is what decides whether the format works:

1. **Do the six heroes look like the same day?** Not just the same grade — the
   same weather, the same hour, the same wet. If a cut from the wood to the
   mortuary jars, that is the continuity block failing, not the model.
2. **Does S4-01 land without a face?** If it does, the thesis holds and
   character consistency never becomes a cost.
3. **Does S2-03 survive a 5-second hold?** Generated stills often fall apart on
   a hold; this sets the cutting rhythm for the whole format.
4. **Is S3-01 the only warm frame, and S3-04 the only hard-lit one?** Amber or
   directional light leaking anywhere else is the earliest sign of drift.
