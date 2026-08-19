# Style bible — "Kold Sankt Hans"

This is the steering wheel. Every prompt in the episode carries this block
word for word; change a line here and re-render, and all 22 shots move
together. Nothing else in the pipeline has that reach.

The name is the idea: a midsummer bonfire site — the most harmless place in the
Danish calendar — read cold.

## The locked block

| | |
|---|---|
| **Stock** | Kodak Vision3 500T rated at 320, processed normal, scanned flat and graded down |
| **Palette** | Wet greens desaturated towards grey, ash white, weathered timber, one cold cyan in the shadows. Amber **only** where a real flame or sodium lamp is putting it there |
| **Light** | One dominant, motivated source per frame and nothing else. Flat overcast outdoors, hard 4000K fluorescent in institutional rooms, sodium or firelight at night. Shadows stay open; blacks lift to charcoal |
| **Lenses** | 35 / 50 / 85mm spherical primes worked near wide open. Nothing wider than 28mm, nothing longer than 135mm |
| **Texture** | Fine 35mm grain, faint halation on highlights, a trace of lens breathing, focus falling off fast |
| **Format** | 16:9 broadcast, composed with clear space on one side for lower-thirds |

Held in `episode.py` as `LOOK`. The wording there is the master; this table is
the readable copy of it.

## Why each line is doing work

**500T rated at 320** is a tungsten stock pulled slightly — it gives cool,
open, slightly milky images rather than the contrasty digital look that reads
as "AI cinematic". **Graded down** blocks the model's instinct to deliver a
finished, punchy picture.

**Amber only from a real source** is the single most useful line in the block.
Generated images drift towards a warm key light because most training images
have one. Forbidding unmotivated warmth is what keeps the Danish weather in the
frame, and it means the one moment of actual fire lands.

**Nothing wider than 28mm** kills the AI wide-angle sweep, and **nothing longer
than 135mm** keeps it from becoming a wildlife documentary. Working near wide
open gives shallow focus, which hides the parts of a generated frame that do
not survive scrutiny.

**Blacks lift to charcoal** is both a look and a defence: crushed blacks are a
tell, and open shadows leave the colourist somewhere to go.

**Space on one side** means lower-thirds and the detective's name do not have
to be cut into the middle of a composition later.

## Anti-tells, applied to every prompt automatically

Held as `ANTI_SLOP` in `prompt_builder.py`, appended to every image prompt:

not symmetrical · not centred · not a hero composition · no HDR glow · no bloom
· no lens flare · no rim-light halo · no glossy plastic surfaces · no
over-clean textures · no drone or god's-eye viewpoint · no crushed blacks · no
orange-and-teal grade

## Finished in post, not in the prompt

The last 20% of "this is footage" is not promptable and should not be
attempted:

- Real 35mm grain plated over the top, matched across the episode
- A hair of gate weave and lens breathing on stills that hold
- Half a stop under, consistently
- Slight handheld drift on tier A moves — a perfectly steady push is a tell
- One grade for the whole programme, generated and shot material together

## How to change the look

Rewrite the line in `episode.py`, run `python3 render.py --all`, regenerate.
Do not adjust the look shot by shot — that is drift, and drift is the thing
this document exists to prevent. If one sequence genuinely needs its own
world (a flashback, a different decade), give it its own `Look` and say so.

## Variants worth testing before locking

The block above is a considered first proposal, not a finding. Three
alternatives are cheap to test against the same six hero frames, and the
comparison is the real output of the first generation pass:

1. **Colder and flatter** — drop the amber allowance entirely, push cyan.
   More Nordic, risks monotony across 45 minutes.
2. **Period** — if the case is pre-2005, move to a grainier 200T look with
   period-correct cars and clothing in the entity descriptions.
3. **Higher contrast, more shadow** — closer to the American true-crime norm.
   Reads more expensive, and less honest.
