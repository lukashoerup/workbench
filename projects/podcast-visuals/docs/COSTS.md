# What a full episode costs

Prices checked 19 Aug 2026 and moving fast in this market — re-verify before
anyone budgets against them. Converted at roughly 6.4 DKK to the dollar.

## The short answer

| | Compute | Labour | All-in |
|---|---|---|---|
| **The POC — six frames, one model, flagship settings** | **~150 DKK** | half a day | — |
| **The POC with the full five-model bake-off** ([POC.md](POC.md)) | **~1,000 DKK** | 1–2 days | — |
| **One 45-minute episode, settled** | **~3,000 DKK** | 2–3 person-days | **~12,000–25,000 DKK** |

The compute is close to a rounding error. **The cost of this format is human
attention, not GPU time** — which is the single most important thing to
understand before planning around it. Doubling the render budget changes almost
nothing; halving the number of shots that need a human eye changes everything.

For the POC this has a direct consequence: **use the best model at its highest
setting and generate far more variants than a series budget would allow.**
Sixteen variants per frame instead of four costs tens of kroner at this size,
and it is the difference between learning that a model *can* produce the frame
and learning that it *did*.

## The POC, itemised

Five image models × 6 hero frames × 16 variants = 480 stills, at flagship
settings (mixed pricing, Nano Banana Pro at 4K down to Imagen 4 Ultra) ≈ **$90**.
Localised edits and re-rolls ≈ **$20**. Three video models × 6 clips × 5s,
silent, with a retry allowance ≈ **$42**. A Midjourney month, if it is in the
bake-off, **$30**.

**≈ $180 · 1,150 DKK** for the whole comparison. Backing one model and skipping
the bake-off brings it to about 150 DKK.

Below this line is the series economics — relevant for planning, not for the
POC.

## What the episode is assumed to be

A 45-minute programme, 60% generated picture and 40% detective on camera or
archive. At an average 5-second shot that is **324 shots**, 27 minutes of
picture.

Working assumptions, all of them worth revising after the first real episode:

- **4 variants generated per shot** to select from, plus a re-roll on about a
  quarter of shots after notes → **~1,620 images**
- Motion split 40% tier A (parallax, done in post, no API cost) / 50% tier B /
  10% tier C → **194 clips**, 970 seconds
- **~55% of clips usable first time** → **~1,750 seconds billed**
- **No generated audio.** The podcast is the audio. Every video model prices
  silent output well below its audio tier, and this halves the video line.

## Three tiers

**Workshop** — for testing, offline cuts, and deciding the look.

| | | |
|---|---|---|
| Images | Seedream v5 Lite, 2048² | $42 |
| Video | Veo 3.1 Lite, 1080p, silent | $88 |
| Transcript + language model | | $11 |
| | | **≈ $140 · 900 DKK** |

**Broadcast — the recommended tier.**

| | | |
|---|---|---|
| Images | Nano Banana Pro (Gemini 3 Pro Image), 2K | $217 |
| Video | Kling 3.0 at $0.10/s | $175 |
| Transcript (diarised, word timestamps) + language model | | $31 |
| | | **≈ $425 · 2,700 DKK** |

Substituting Veo 3.1 Fast for Kling takes it to ≈ $470 · 3,000 DKK.

**Premium** — flagship everything, for a pilot that has to sell the format.

| | | |
|---|---|---|
| Images | Nano Banana Pro at 4K | $389 |
| Video | Runway Gen-4.5 at $0.20/s, or Veo 3.1 Standard at $0.40/s | $350–700 |
| | | **≈ $750–1,100 · 4,800–7,000 DKK** |

## Why Nano Banana Pro for the stills

Not because it is the prettiest — Imagen 4 Ultra is arguably more photoreal at
$0.08, and Midjourney V7 has the better instinct for cinematic light. Because
of three things this format specifically needs:

- **Up to ten reference images** steering style and structure, which is how the
  locked look gets enforced by example and not only by words — and how the
  bonfire site stays the same site across a dozen shots.
- **Localised edits** — moving one object, changing one light — so a
  nearly-right frame gets fixed instead of re-rolled. At scale this is a bigger
  saving than the per-image price difference.
- **SynthID marking** already embedded, which is a live compliance requirement
  as of 2 August 2026 ([RAILS.md](RAILS.md)).

At 324 shots the gap between $0.08 and $0.134 an image is about $90 an episode.
Controllability is worth far more than that.

## Where the money actually goes

A settled episode, once the style bible is locked and the pipeline runs:

| | Who | Time |
|---|---|---|
| Transcript and beat sheet review | Lasse | 2 h |
| **Shot list review — gate 1** | Lasse | 2–3 h |
| Generation | nobody — runs unattended | 2–4 h wall clock |
| **Select session — gate 2** | Lasse + editor | 3–4 h |
| Re-rolls and fixes | editor | 1–2 h |
| Assembly, grade, sound | editor | 1–1.5 days |
| | | **≈ 2–3 person-days** |

The first episode is 5–8 days, because the style bible, the entity registry and
the review habits are all being built at once. That cost is paid once per
series, not per episode.

At a Danish freelance edit rate that is roughly **8,000–18,000 DKK of labour**
per settled episode on top of the compute.

## Against the alternative

Rough industry orders of magnitude — Lasse will have far better numbers than
this, and should replace them:

| | Per episode |
|---|---|
| Shot reconstruction: actors, location, crew, at least 2 days | 100,000–300,000 DKK |
| Licensed archive and stills, where any exists | varies, often unavailable |
| **This approach, settled** | **12,000–25,000 DKK** |

The honest comparison is not quality-for-quality — a good reconstruction with
actors is still better than this. The comparison is that for cases where there
is no archive and no budget for a shoot, the realistic alternative is not a
reconstruction; it is a static photo of a courthouse held for forty seconds, or
nothing at all. That is the bar this clears easily.

## What would change these numbers most

1. **Shot length.** Going from 5-second to 7-second average cuts the shot count
   by 30% and takes the human review time down with it. Slower cutting also
   suits the material.
2. **The tier A share.** Every shot moved from generative motion to parallax is
   free, deterministic, and never needs a re-roll. If tier A can carry 60%
   rather than 40%, the video line roughly halves and the retry risk with it.
3. **First-time accept rate.** Currently assumed at 55%. Better prompts and a
   locked look should push this up over a series; each 10 points is worth
   about 15% of the video budget.
