# Start here — copy-paste, no API keys

Everything below can be done by hand today, for nothing. APIs come later, and
only once the frames have been judged; wiring them up before that is building a
factory before knowing whether the product is any good.

## The two programs

| | | |
|---|---|---|
| **Stills** | **Google AI Studio** — `aistudio.google.com` | Free. Sign in with a Google account. The generous free tier is on the standard Gemini image model; the Pro tier is a couple of images a day free, so save it for the heroes once the look is settled. Takes reference images, which is the whole game here |
| **Motion** | **Google Flow** — `labs.google/flow` | 50 free credits a day without a subscription. Runs Veo, and takes a still as the first frame, which is exactly the tier B pattern |

Two others worth knowing, neither needed to start: **Kling** (`klingai.com`) has
free daily credits and is the cheapest per second by a distance if the format
goes to series. **Midjourney** has the best instinct for cinematic light of
anything, but it is subscription-only and takes reference images less
comfortably, so it is a later comparison rather than a starting point.

## The order matters

Four of the frames are **anchors** — the first image from each location. They
get generated cold and approved, and then attached as reference images to
everything else in that place. Words hold a look; only an image holds a *place*.
All four anchors happen to be in the hero set, so the order falls out neatly:

**First, cold, no references:**

| | Where |
|---|---|
| **S1-01** | the forest and the bonfire |
| **S2-01** | the forensic institute |
| **X-02** | the kiosk |
| **S5-01** | the courtroom |

**Then, with the approved anchor attached as a reference image:**
S3-01 and S3-04 (attach S1-01), S4-01 (attach X-02), X-01 (no anchor needed).

`docs/PROMPT-PACK.md` is already in this order and says, per shot, which frame
to attach.

## In AI Studio, per frame

1. Paste the **Still** prompt from the pack. Paste all of it — the long tail of
   negatives is doing as much work as the description.
2. Aspect ratio **16:9**. Highest resolution offered.
3. Generate **eight to sixteen variants**, not four. At eight frames this costs
   nothing and it is the difference between learning the model *can* do it and
   seeing that it *did*.
4. For a dependent shot, attach the approved anchor image first, then paste.
5. Keep the seed of anything good. A neighbouring seed is a variation; a new
   prompt is a lottery.
6. A frame that is 90% right gets the one wrong thing edited out — ask for the
   change in follow-up rather than re-rolling and losing the 90%.

## Two looks, same frames

There are two prompt packs, and they differ in exactly one thing: the medium.

- **`docs/PROMPT-PACK.md`** — *Våd aske*. Photographic. 500T pulled, wet forest
  greens, one cold cyan in the shadows.
- **`docs/PROMPT-PACK-DRAWN.md`** — *Kul og blæk*. Charcoal, graphite and ink
  wash on grey paper, in the tradition of courtroom sketch rather than
  illustration.

Run the **four anchors in both looks** before anything else. That is 8 frames
and it is the cheapest decisive comparison available: same case, same weather,
same year, same framing, same rails — only the medium changes.

The drawn look is not only a taste question. A drawing cannot be mistaken for
archive, which removes most of the regulatory and ethical weight in one move; it
has no uncanny valley to fall into; and it does not look like everyone else's
AI. Against it: it can slide into "true crime comic", and it is harder to
intercut with real talking heads. Which is why it is a test.

## Then the motion, in Flow

Only for frames that have been approved. Video costs roughly ten times a still,
so nothing gets animated on spec.

1. Upload the approved still as the **first frame**.
2. Paste the **Motion** prompt from the same entry in the pack.
3. 16:9, 5–6 seconds, no audio — the podcast is the audio, and silent output is
   billed lower everywhere.

**Everything moves in slight slow motion**, about half real speed, and that is
written into every motion prompt from one frozen block so it cannot drift shot
to shot. It suits the genre, and it is also the technically safer choice:
less change between frames means fewer of the artefacts that give AI video away.
The camera is exempt — slowing the move as well turns every push into a drift
and every drift into nothing.

Tier **A** shots are not generated at all. They are a still with a slow camera
move added in the edit — free, deterministic, and impossible to get wrong. Do
at least one of them by hand as the control. **If a parallax push on a great
still is indistinguishable from a generated clip at television size, that is
the most valuable finding in the whole test.**

## Judge it on a television

Not a laptop. Laptop screens forgive things a 65-inch panel does not, and this
is a broadcast deliverable. Each frame held for its full intended length, and
played against the actual podcast audio. The rubric is in
[POC.md](POC.md#how-to-judge--the-rubric).

The frame to look at first is **S4-01** — the forearm and the neck under the
bare bulb. If that lands without an identifiable person in it, the whole thesis
holds, and consistent characters never become an expense in this format.
