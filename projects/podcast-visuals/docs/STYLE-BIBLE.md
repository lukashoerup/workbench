# Style bible — "Våd aske"

This is the steering wheel. Every prompt in the episode carries these blocks
word for word; change a line here and re-render, and all 22 shots move
together. Nothing else in the pipeline has that reach.

The name is the scene: a fire burning badly in the rain, ash going to slurry.

## The two frozen blocks

**The look** — how it is photographed.

| | |
|---|---|
| **Stock** | Kodak Vision3 500T rated at 320, processed normal, scanned flat and graded down |
| **Palette** | Soaked forest greens desaturated towards grey, wet black bark, the grey-white of sodden ash, one cold cyan in the shadows. Amber **only** where a real flame is putting it there |
| **Light** | One dominant, motivated source per frame and nothing else. Flat grey daylight through a soaked canopy outdoors, hard 4000K fluorescent in institutional rooms, firelight where something is actually burning. Shadows stay open; blacks lift to charcoal |
| **Lenses** | 35 / 50 / 85mm spherical primes worked near wide open. Nothing wider than 28mm, nothing longer than 135mm |
| **Texture** | Fine 35mm grain, faint halation on highlights, a trace of lens breathing, focus falling off fast |
| **Format** | 16:9 broadcast, composed with clear space on one side for lower-thirds |

**The continuity** — what world it is photographed in.

> The whole episode is one continuous wet grey day in late autumn, some time in
> the recent past: rain falling or just fallen, no sun anywhere, no blue in the
> sky, standing water on every horizontal surface, and the same soaked flat
> light indoors and out. Interiors carry the same cold cyan in the shadows and
> the same open blacks as the forest, so a cut from the wood to a tiled room
> does not jar.

Both are held in `episode.py` as `LOOK`. The wording there is the master; this
page is the readable copy.

## Consistency is enforced, not encouraged

Consistency across scenes is the whole difference between one programme and
three hundred pictures, and it never fails in the style bible — it fails one
plausible-sounding shot at a time, at 23:00, three weeks in. So four mechanisms
carry it, and three of them are under test:

1. **The look block is byte-identical in every prompt.** Not regenerated per
   shot, not paraphrased. `test_the_look_block_is_byte_identical_across_shots`
   fails if that ever stops being true.
2. **The continuity block is in every prompt too**, and a shot that fights it
   is rejected before a prompt is even built. Write "low raking sun" into an
   episode established as overcast and the suite stops you.
   *This caught a real error during drafting: the tyre-print shot had been
   written with a shaft of low sun for the relief. It now gets that relief from
   a technician's work lamp — motivated inside the scene, and more accurate,
   because raking lamp light is how tyre impressions are actually photographed.*
3. **Recurring places are pasted verbatim from a registry**, never re-described
   per shot. `test_entity_descriptions_are_inserted_verbatim`.
4. **Anchor frames.** Words hold a look; only an image holds a *place*. The
   first frame from each location is approved and then attached as a reference
   to every later shot there. The prompt pack is ordered anchors-first and the
   ordering is under test.

## Why each line is doing work

**500T rated at 320** is a tungsten stock pulled slightly — cool, open,
slightly milky, rather than the contrasty digital look that reads as "AI
cinematic". **Graded down** blocks the model's instinct to hand back a
finished, punchy picture.

**Amber only from a real source** is the single most useful line in the block.
Generated images drift towards a warm key because most training images have
one. Forbidding unmotivated warmth is what keeps Danish November in the frame,
and it means the one place the fire burns clean actually lands.

**One cold cyan in the shadows, everywhere** is the bridge. It is what lets a
cut from a soaked spruce plantation to a tiled mortuary read as the same
programme rather than as two stock libraries.

**Nothing wider than 28mm** kills the AI wide-angle sweep; **nothing longer
than 135mm** stops it becoming a wildlife documentary. Near wide open gives
shallow focus, which hides what does not survive scrutiny.

**Blacks lift to charcoal** is both a look and a defence: crushed blacks are a
tell, and open shadows leave the colourist somewhere to go.

## The genre grammar

True crime has a visual language and it is mostly about restraint. What makes
an image read as this genre rather than as drama:

- **Locked off, or barely moving.** The camera does not perform. One slow push
  or drift per shot, or nothing.
- **Held long.** Shots run past the point where a drama would cut. The
  discomfort is the effect.
- **The subject is small in frame**, and often at the edge. Wide, empty, and
  patient beats close and busy.
- **Return to the place.** The same clearing at different hours is the genre's
  oldest move and it is why the entity registry matters.
- **Nothing is heroic.** No hero angles, no symmetry, no beauty shots. If a
  frame looks like a poster, it is wrong.
- **The picture never explains.** It sets the room the voice is speaking in.

## Anti-tells, applied to every prompt automatically

not symmetrical · not centred · not a hero composition · no HDR glow · no bloom
· no lens flare · no rim-light halo · no glossy plastic surfaces · no
over-clean textures · no drone or god's-eye viewpoint · no crushed blacks · no
orange-and-teal grade

## Finished in post, not in the prompt

The last 20% of "this is footage" is not promptable and should not be
attempted: real 35mm grain plated over the top and matched across the episode,
a hair of gate weave, half a stop under consistently, slight handheld drift on
the parallax moves, and one grade for the whole programme — generated and shot
material together, in the same pass.

## How to change it

Rewrite the line in `episode.py`, run `python3 render.py --all`, regenerate.
Never adjust the look shot by shot: that is drift, and drift is what this
document exists to prevent. Three shots asking for the same correction is a
style bible change, not three notes. If one sequence genuinely needs its own
world — a flashback, a different decade — give it its own `Look` and say so out
loud.
