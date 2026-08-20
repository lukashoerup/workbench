# What the first generation pass actually showed

19–20 Aug 2026. 54 stills and 2 clips, Nano Banana Pro (`gemini-3-pro-image`)
and Veo 3.1 Fast, both on one Gemini key. **58 kr of a 200 kr budget.**
Selected frames are in [`../stills/`](../stills).

## The short version

It works. The frames read as photographed, not as renders, and they read as one
programme rather than as a set of pictures — the locked palette, the continuity
block and the withheld frame all landed on the first attempt.

What took the work was not making them beautiful. It was stopping the model
from quietly adding things the case does not contain.

## Four breaches the rails did not have, found by looking

Every one of these was invisible in the prompt and obvious in the output. None
would have been caught by reasoning harder beforehand.

**1. A car appeared on the forest track.** Twice, unprompted — a period estate,
parked by the fire. Nobody reads a vehicle at a crime scene as set dressing: it
is the killer's car or a police car, and this case's was a VW Golf belonging to
a friend. An invented object that carries a claim is a rails breach, not a
composition note. → `FORBIDDEN` now includes *nothing in frame that is not
described above*.

**2. The model burned a timecode into the frame.** "LATE SEPTEMBER 1999 /
02:14 AM", bottom left, in the forensic institute. It asserts a time nothing
supports and it makes the image read as surveillance footage — the exact thing
[RAILS.md](RAILS.md) forbids. The cause is instructive: the continuity block
says "late September 1999", and the model rendered the world state as a
caption. → *no burned-in timecode, no date stamp, no caption, no overlay*.

**3. Handprints, in the drawn look.** On walls and floors, in three frames of
four. Pure horror-film borrowing, and an evidential claim. → forbidden, and see
below, because forbidding it did not work.

**4. Letterboxing.** Several frames came back with black bars inside the 16:9
frame — a film-scan affectation that silently crops the deliverable. → *the
image fills the 16:9 frame edge to edge*.

## Three things about how these models behave

**A negative does not defeat a strong genre prior; a positive statement does.**
The handprints survived an explicit "no handprints, no smears, no marks of a
struggle". They vanished when the drawn look instead *asserted* what is there:
"every wall, floor, door and surface is plain, bare and completely unmarked —
the only marks anywhere are the marks of the pencil itself." Same intent,
opposite grammar, completely different result. Worth reaching for whenever the
model keeps supplying something the genre expects.

**A reference image hijacks a tight subject shot.** Attaching the approved
kiosk anchor to S4-01 — a close-up of a man's neck — produced the *kiosk*, with
no man in it. References anchor a place beautifully when the new shot is also a
view of that place (S3-04's forest matched its anchor exactly), and they
overwrite the subject when it is a close-up. So: anchor wides, and let
close-ups run free.

**Generated video needs to be told that almost nothing should change.** The
first clip started as the approved frame and ended with the bonfire swallowed
by a wall of white smoke. The motion brief said "the fire holds"; six seconds
was enough for the model to invent a weather event. Adding one clause to the
frozen motion grammar — *the last frame must be recognisably the same picture
as the first; nothing grows, spreads, billows, engulfs or fills the frame* —
fixed it outright. First and last frames of both attempts are in `stills/`.

## The rails caught me twice, which is the system working

X-01 was written as a newspaper lying "face-down"; S4-01 as "no part of the
face is anywhere in the picture". Both were rejected by the face check, which
does not read context. Both cost a rewording. That is the trade the check was
designed for, and it is the right one.

## The two looks

**Våd aske (photographic)** is the stronger and the more controllable. It holds
the palette, the weather and the period without argument, and the corrections
it needs are ordinary director's notes — bigger, further back, colder, shallower.

**Kul og blæk (charcoal)** is a real alternative and it is genuinely unsettling,
but it is measurably harder to hold. It drifted twice: interiors came back more
finished than landscapes, and rust-orange leaked indoors as something that read
as blood. Both needed look-level corrections that the photographic look never
needed. If it is chosen, budget more supervision per frame, not less.

The case for it is unchanged and still strong: a drawing cannot be mistaken for
archive, which removes most of the regulatory weight in one move.

## The frame to look at first

**S4-01.** A man under pressure, sweating, and there is no identifiable person
in the picture. It took three passes — the first was too warm with crushed
blacks, the second showed too much of the head, the third is right. The crop
still wants one more notch tighter, which is free at the edit stage.

If that frame works on a television, the thesis holds and consistent characters
never become an expense in this format.

## The coverage audit, 20 Aug

Lukas asked whether everything Lasse described was actually in the material.
It was not, and the gap was in the first note.

His first timecode reads **"legede børn og bål og beredskab på gerningsstedet"**
— three things. Only the bonfire had been generated. The children and the fire
brigade existed as lines in the shot list and as nothing else. Same in the third
note: the tyre print was there, the lighter fluid was not. Eight of twenty-four
shots existed; seven of them happened to be the ones chosen as heroes.

The lesson is dull and worth writing down anyway: **a hero frame per timecode is
not coverage of that timecode.** Lasse's notes are not shot requests, they are
lists of what he heard, and each one has to be answered element by element.

All 24 now exist. Seven needed a second pass after the first contact sheet, and
they are a useful catalogue of what these models get wrong:

- **The children were standing at a burnt-out fire** rather than the burning one
  from the previous shot — a continuity break the model invented on its own,
  because "children find a bonfire" reads as aftermath.
- **Danish police tape came back yellow and black**, which is hazard tape. It is
  blue and white here.
- **Dental X-rays came back as vials on a light box.** Fixed by describing the
  object rather than naming it: "a little rectangle of grey and black showing a
  handful of teeth in silhouette".
- **The plaster cast came back as a log**, twice, until it was described as
  physical matter: "a flat rectangular slab of chalk-white plaster of Paris,
  about the size and thickness of a paving stone".
- **Lighter fluid came back as motor oil**, twice, for the same reason — a shelf
  of bottles in a petrol station is overwhelmingly motor oil in the training
  data. Naming the shape and the contents beat naming the product.
- **The stacked wood was already alight** in the shot that exists to show it
  before it was lit.
- **The prosecutor had a readable profile.** That is a rails breach, not a note.
  Fixed by pushing the figure to "closer to a silhouette than to a person".

Four of those seven are the same failure: **naming a thing is weaker than
describing it.** Where the model has a strong prior about what a named object
looks like — a cast, lighter fluid, dental films — the prior wins. Describing
the physical object as if to someone who has never seen one wins back.

## What it actually cost, with the waste in

The number that matters is not what the kept frames cost. It is what the whole
pass cost, failures included:

| | |
|---|---|
| Images generated | **86** |
| Images kept | 24 |
| Waste factor | **3.6×** |
| Clips generated / kept | 5 / 4 |
| **Total machine time** | **~100 kr** |

Scaled with the same waste, a 45-minute episode at roughly 324 shots is about
**2,400 kr of machine time**. That is generation only — no edit, no grade, no
human hours; those are the producer's numbers, not ours.

The 3.6× is high because this was the first pass: the look was being invented
while it ran, and seven shots needed a second attempt because the model
delivered a tractor tyre instead of a car tyre, motor oil instead of lighter
fluid, and a log instead of a plaster cast. Once the look is fixed the factor
drops; half of it is a fair expectation from episode two.

## What full coverage would actually cost

Worth stating because it changes the budget conversation. Lasse's five segments
run 11:19 in total. At a five-second average a finished cut of just those five
would need roughly **135 shots**. We have made 24 — enough to show what each
sequence would be, not a finished cut of them. `docs/../stills/` holds all 24.

## What was not tested

Motion in the drawn look. The 30:00–44:37 segment, so the prosecutor's frames
are still unverified against the audio. And nothing has yet been judged on a
television, which is the only judgement that counts.
