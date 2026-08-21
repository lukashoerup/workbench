# The POC — six frames, flagship models, no compromises

The proof of concept is **six frames and six clips**. Not an episode, not a
pipeline, not a tool. Six frames good enough that a broadcaster looks at them
and does not ask what they were made with.

Cost is not a constraint at this size — the full five-model bake-off below
renders for roughly **1,000 DKK**, and about 150 DKK if you skip the bake-off
and back one model ([COSTS.md](COSTS.md)). So every decision here is made for
quality and nothing else, and the cheap-tier thinking that belongs in a series
budget is deliberately absent.

## Step 1 — bake off the image models

Do not assume a winner. Run the **same anchor prompt** (S1-01) through every
flagship model at its highest setting, then judge blind.

| Model | Why it is in the test |
|---|---|
| **Nano Banana Pro** (Gemini 3 Pro Image) | Up to ten reference images, localised edits, native 4K, SynthID. The most *controllable*, which over 300 shots matters more than raw beauty |
| **Imagen 4 Ultra** | Currently the hardest to tell from a photograph — skin, fabric, reflections |
| **Midjourney V7** | The best instinct for cinematic light and texture of anything available |
| **FLUX.2 pro** | Built for consistent production output; strong at grain and stock emulation |
| **Seedream v5** | The value benchmark — worth knowing how close it gets |

**16 variants per model, not 4.** At six frames the extra generations cost tens
of kroner and they are the difference between "the model can do this" and "the
model did this once".

Judge on a **television**, not a laptop. This is a broadcast deliverable and
laptop screens forgive things a 65-inch panel does not.

## Step 2 — the anchor, then everything else

The winner generates **S1-01** cold. That frame gets picked, fixed and
approved — and then becomes the reference image for every other shot at the
bonfire site.

This is the largest quality lever in the whole project and it is already built
into the prompt pack: [PROMPT-PACK.md](PROMPT-PACK.md) is ordered anchors-first
and tells you which approved frame to attach to each dependent shot. Words hold
a look; only an image holds a *place*.

Anchors for this test: S1-01 (field and bonfire site), S2-01 (forensic
institute), S4-02 (interview room), S5-01 (courtroom).

## Step 3 — squeeze the frame

In this order, because each step is cheaper than the one before it is worth:

1. **Generate at the model's native maximum** (4K where offered). Never
   generate small and upscale to fake it.
2. **Localised edit before re-roll.** A frame that is 90% right gets the one
   wrong object edited out. Re-rolling throws away the 90%.
3. **Keep the seed** of anything good. A neighbouring seed is a variation; a
   new prompt is a lottery.
4. **Then post.** Real 35mm grain plated over the top, half a stop under, a
   hair of gate weave. This is where the last 20% of "this is footage" comes
   from and it is not promptable — see [STYLE-BIBLE.md](STYLE-BIBLE.md).

## Step 4 — bake off the motion

Same approved still, three models, same 4–6 second brief:

| Model | |
|---|---|
| **Veo 3.1 Standard** ($0.40/s) | Top of the market. Silent output is billed lower and the podcast is the audio |
| **Runway Gen-4.5** ($0.20/s) | The best control surface and the only film-production ecosystem around it |
| **Kling 3.0** (~$0.10/s) | Punches well above its price; if it holds up here the series budget changes |

Also render **tier A** (2.5D parallax in post) on the same frame, as the
control. If a parallax push on a great still is indistinguishable from a
generated clip at broadcast size, that is the most valuable finding in the
entire test — it is free, deterministic and never needs a re-roll.

## How to judge — the rubric

Blind, on a TV, each frame held for its full intended duration. Not "is it
impressive", but:

1. **Does it read as photographed?** First instinct only. If anyone says "nice
   render", it failed.
2. **Does it survive the hold?** Generated stills often fall apart when looked
   at for five seconds. This sets the cutting rhythm for the whole format.
3. **Any tell?** Symmetry, texture repetition, impossible light, melted detail
   at the edges, that faint plastic sheen.
4. **Is it on the bible?** Right palette, right lens language, amber only where
   a real flame puts it.
5. **Does it work under narration?** Play it against the actual podcast audio.
   A frame that pulls focus from the detective is a bad frame however good it
   is.

## What a pass looks like

- **S4-02** — the duvet, the sleeping bag and the sack, laid out empty — lands
  without a person in it. That is the whole thesis, and it is the frame to show
  first. (S4-01 held this place until it was retired; see
  [FINDINGS.md](FINDINGS.md#the-shot-that-broke-the-thesis-was-the-one-that-bent-the-rule).)
- The six frames read as one programme rather than six pictures.
- At least one clip is indistinguishable from a locked-off shot at TV size.

## What a fail looks like, and what to do

- **Everything is beautiful but nothing matches** → the look is not locked hard
  enough. Style bible problem, not a model problem; tighten and re-render.
- **Stills are good, motion is not** → move the tier A share up. A programme of
  excellent stills with disciplined parallax is a real format; a programme of
  wobbling generated clips is not.
- **Institutional interiors fail** (mortuary, interview room) → these are the
  hardest and most generic-prone. Fix with harder reference anchoring and real
  Danish location photographs as references.

## What is deliberately not in the POC

No transcription pipeline, no batch runner, no assembly, no tool. All of it is
specified in [WORKFLOW.md](WORKFLOW.md) and none of it should be built until
six frames have been judged on a television. Building the factory before
knowing whether the product is any good is exactly the mistake ImageBooks made,
and it is the one lesson from that repo worth carrying forward.
