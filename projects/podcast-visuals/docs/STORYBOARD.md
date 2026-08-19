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

### How certain is the identification?

Practically certain. Not verified. The distinction matters, so here it is
plainly.

**For:** of 219 episodes in the feed, only 44 run to 40 minutes or more, which a
timecode of 36:40–39:36 requires. Of those, exactly one describes children, a
bonfire, lighter fluid, a tyre track in the forest floor and a prosecutor. Its
four contributors map one-to-one onto Lasse's five markers: pathologist at
09:34, forensic technician at 15:30, murder chief at 20:17, prosecutor at
36:40. Five independent coincidences would be needed for this to be the wrong
episode.

**Against:** nobody has resolved Apple's episode id `1000555640897` — the thing
Lasse actually sent — to a title. Apple is blocked from this machine and the
feed does not carry Apple ids. And nobody has listened to the audio.

**Two checks that would settle it**, either of which takes under a minute: open
Lasse's original link and read the episode title; or open the mp3 and skip to
03:30 and 20:17 and hear whether it is children and a bonfire, then a suspect
under pressure.

### Where each shot's content comes from

The narration outranks everything, including research that is more detailed and
more interesting: this programme is a retelling of what a detective says
happened, so a shot built on a good fact from the wrong source is still a shot
the episode does not support. Every shot therefore records its own tier, and
the test suite enforces it.

| Tier | Meaning | Shots |
|---|---|---|
| `audio` | what is actually said — the only primary source | **0** |
| `notes` | Lasse's timecode notes; a human who listened, paraphrasing | 6 |
| `description` | the episode's own published description | 7 |
| `case` | public reporting about the case, not about this episode | 1 |
| `direction` | an art-direction decision, sourced to nothing | 9 |

Two consequences worth saying out loud. **No shot may claim the audio until a
transcript exists** — a test fails if one does, which is what stops a vivid
research detail quietly becoming something "the episode said". And **no hero
frame may rest on art direction alone**: atmosphere may be invented, but the
frame that says what happened may not. Also under test.

The nine `direction` shots are the honest number to watch. They are atmosphere
— tape, corridors, empty rooms — and several should be replaced by shots the
narration actually supports once there is a transcript. Expect that count to
fall.

The weather is `direction` too, at the look level rather than per shot: a wet
grey day suits the material and gives the episode one world to sit in, but it
is chosen, not known. Check it against the audio before locking the look.

The odontologist and the dental identification are the single `case` shot.
That detail is from *Dødens detektiver* ep. 1, which looks like the same case
but has not been shown to be, so S2-04 is written to work either way.

---

## 03:30–06:00 · children, the bonfire, the response
*"legede børn og bål og beredskab på gerningsstedet"*

The job of this sequence is to make an ordinary walk in a wood ordinary — right
up until the smoke. Nothing in the fire is ever shown. The narration says what
is in it; the picture stays outside.

| | Shot | Tier |
|---|---|---|
| **★ S1-01** | **A low wide bonfire burning badly in steady rain in a forest clearing, more smoke than flame, the smoke hanging low and refusing to rise through the wet air. From the track, twenty metres back.** | **B, 6s** |
| S1-02 | Two children from behind at forty metres, stopped still on the wet track, a bicycle on its side beside them. 85mm, compressed | B |
| S1-03 | Close on the edge of the heap — wet branches steaming as much as burning, water running off bark into ash | B |
| S1-04 | Blue light pulsing through wet spruce trunks. The vehicle never in frame | B |
| S1-05 | Police tape between two trunks, beaded with rain and sagging under it | B |

S1-01 is the whole thesis in one frame: the most frightening thing in the
episode is happening in it, and none of it is visible.

---

## 09:34–13:00 · the forensic pathologist
*"retsmediciner og kig på lig"*

The hardest segment and the one that most needs the rails. Nothing here shows a
body. The sequence is about **procedure** — cold rooms, steel, instruments,
routine — and procedure is more unsettling than anatomy.

| | Shot | Tier |
|---|---|---|
| **★ S2-01** | **A wet gloved hand lifting an instrument from a folded green cloth. 85mm at f/1.8, hard overhead 4000K, the room falling away into green-grey.** | **B, 5s** |
| S2-02 | Empty institutional corridor, one heavy door ajar at the end. Slow push | A, 6s |
| S2-03 | Empty steel table, drain slot, a film of water. A drop travels the slot | B |
| S2-04 | A row of small dental radiographs on a backlit panel, a gloved fingertip under one of them | B |

S2-04 is written as small radiographs on a light box rather than specifically
dental ones, because the odontologist detail is not confirmed for this episode.
Either way it is the safest possible way to show an identification: abstract
grey shapes, and a hand.

---

## 15:30–17:09 · the accelerant and the tyre print
*"tændvæske i bål, dæk aftryk"*

Two heroes, because Lasse's note names two things: the fire was helped, and
something drove away. This is where the picture can carry actual
evidence-reasoning — and where it is most tempting, and most forbidden, to fake
a forensic photograph.

| | Shot | Tier |
|---|---|---|
| **★ S3-01** | **One patch of the heap burning hard and clean in the rain while everything around it only smoulders — a bright wrong heat in a single place.** | **B, 5s** |
| S3-02 | A scorched plastic bottle at the ash edge, one side melted and slumped, label burnt away | B, 4s |
| S3-03 | Macro: char broken open, the burn running deeper along one line than anywhere around it | B, 4s |
| **★ S3-04** | **One tyre track pressed into soft forest floor where a vehicle turned off the track, tread edge sharp and holding water, evidence scale beside it. Raked by a technician's work lamp.** | **B, 5s** |
| S3-05 | The forestry track running away between wet spruce walls into flat mist. Slow push | A, 6s |

S3-01 is the only place in the programme where amber is allowed, which is
exactly why the style bible forbids it everywhere else. And S3-04 is the one
piece of hard directional light in the episode — from a police lamp physically
in the scene, never from weather the episode has ruled out.

---

## 20:17–21:05 · the interview
*"sveder, drabsmænd, brandbart væske"*

The segment that would traditionally need actors. It does not.

| | Shot | Tier |
|---|---|---|
| **★ S4-01** | **Two hands on scratched laminate, fingers interlaced too tightly, knuckles pale, an untouched cup of water. Above the wrists, only a dark unlit mass.** | **B, 5s** |
| S4-02 | The room before anyone is in it. A blade of blind-light creeps across the table | A, 6s |
| S4-03 | Wall recorder, one red indicator, dust on the housing | B, 4s |
| S4-04 | A garage shelf of dusty tins and bottles — and one clean gap where something round was lifted out | B |

S4-01 is the proof of the whole thesis: a shot of a suspect under pressure with
no suspect in it, and a stronger frame than a face would have been. S4-04 is
the same trick applied to an object — the evidence is the absence.

---

## 36:40–39:36 · the prosecutor
*"anklager"*

Institutional, still, deliberately slow. The pace change after the interview is
the point.

| | Shot | Tier |
|---|---|---|
| **★ S5-01** | **The empty courtroom in the morning before anyone comes in. Pale birch, plain chairs, high flat window light, dust in the air.** | **B, 6s** |
| S5-02 | Case binders bound in red tape, edges furred, reading glasses on top. Slow drift | A |
| S5-03 | A dark-suited shoulder at a lectern, thrown right out of focus; the sharp empty bench beyond | B |
| S5-04 | Courthouse steps in rain, 135mm across traffic, umbrellas too far to read | B |

---

## Extra · the decision that felt brutal
*not one of Lasse's five timecodes*

The description's hardest line is a photograph of a dead woman's battered face,
printed in a newspaper to get her identified — and the brutal decision behind
it. It is the most charged image in the case, and we will never generate it.

| | Shot | Tier |
|---|---|---|
| **★ X-01** | **A bundle of the next morning's papers dropped on a wet pavement outside a shuttered kiosk, still bound with strapping, the top copy printed side down so the whole front page is against the ground.** | **B, 5s** |

Include it in the test. It is the strongest possible demonstration of the rule,
because this episode is *itself* about the ethics of showing a face — and the
frame carries the weight of that photograph without reproducing a pixel of it.

If the real front page is used at all, it is used as archive, cleared and
labelled. We do not make a version of it.

---

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
