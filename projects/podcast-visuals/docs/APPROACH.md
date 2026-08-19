# Approach — why this will not look like AI slop

The genre's whole currency is trust. A viewer who thinks "that's AI" has
stopped listening to the detective and started auditing the pictures, and you
do not get them back. So the bar is not "impressive for AI". The bar is that
the audience never thinks about the images at all.

Everything below is aimed at that one thing.

## 1. The withheld frame

**Never show a face. Never show the body. Never show the act.** Show the
periphery: hands, backs, silhouettes at distance, the object, the aftermath,
the weather, the empty room.

Lasse arrived at this himself — he said the characters do not need to be
consistent — and it turns out to be the single most load-bearing decision in
the project, because it solves three problems with one rule:

- **Quality.** Faces are what generative models are worst at and what viewers
  are best at spotting. Texture, weather, light and objects are what the models
  are best at. Withholding the face means never asking the tool to do the thing
  it fails at.
- **Consistency.** There is no character to keep consistent across 300 shots,
  so the hardest engineering problem in the field simply does not arise.
- **Ethics and law.** Every AI controversy in this genre has been about a
  depicted person — Netflix's *What Jennifer Did* and its manipulated images of
  a real woman, the AI-voiced Gabby Petito, the synthetic interviewees in *The
  Investigation of Lucy Letby*. None of them were about a shot of rain on a
  window. See [RAILS.md](RAILS.md).

It is also simply how the good stuff is already shot. Restraint reads as
authority in this genre; explicitness reads as cheap.

## 2. Shoot it, don't illustrate it

Every prompt is written as a camera report, not a caption. Not *"a forensic
pathologist examines a body"* — that is a brief for an illustration, and it
comes back as one. Instead: *85mm at f/1.8, camera at trolley height, a wet
gloved hand lifting an instrument from a green cloth, hard 4000K overhead,
everything else falling away into green-grey.*

Same beat, but now it is a frame someone stood up and lit. The discipline is
enforced in the shot format itself: `subject`, `camera`, `light`, `atmosphere`
are separate fields, so a shot cannot be written without saying where the
camera is.

## 3. One world, not three hundred pictures

What makes a set of AI images read as a set of AI images is drift — the grade,
the light and the lens language changing slightly from frame to frame.

So the look is written **once** and pasted byte-identical into every prompt,
and recurring places live in a registry and are inserted verbatim rather than
re-described. Both are under test (`test_the_look_block_is_byte_identical_across_shots`,
`test_entity_descriptions_are_inserted_verbatim`), because this is precisely
the kind of discipline that erodes at 23:00 the night before delivery.

The upside: the look is also a single dial. Change one line in
[STYLE-BIBLE.md](STYLE-BIBLE.md), re-render, and the whole episode moves.

## 4. Motion that cannot fail

"Lidt bevægelse" is exactly right, and it is also the technically correct
answer. Generative video fails in proportion to how much it has to invent. A
clip asking for smoke to drift comes back usable most of the time. A clip
asking for a person to walk, turn and speak does not.

So every shot gets **one physical event and one camera move**, no more, at 4–6
seconds. And the shots are split across three tiers so that the failure-prone
technique is only used where it earns its place:

| Tier | Technique | Fails? | Share |
|---|---|---|---|
| **A** | 2.5D parallax — depth map plus a camera push, done in post | Never. It is deterministic. | ~40% |
| **B** | Image-to-video, one event, 4–6s | Sometimes. Re-roll is cheap. | ~50% |
| **C** | Full generative shot | Often. Hero moments only. | ~10% |

Mixing tiers has a second benefit: an episode where every shot breathes with
the same generative wobble announces itself. An episode where most shots are
mechanically-correct camera moves over stills, with occasional real motion,
reads as an edit.

## 5. The tells are removed in the grade, not the prompt

The AI look is *too clean*: too symmetric, too lit, too resolved, no dirt. Some
of that is fought in the prompt (see `ANTI_SLOP` in `prompt_builder.py` — no
symmetry, no bloom, no drone shots, no orange-and-teal). The rest is fought in
post, which is more reliable: real 35mm grain plated over the top, a hair of
gate weave, slight underexposure, a touch of halation, and never a perfectly
steady frame.

## 6. Leave room for the voice

The programme is a detective talking. The picture's job is to hold attention
without competing — slower cuts, darker frames, more empty space. This is the
rare case where the cheaper choice and the better choice are the same one.

## What this does not solve

It cannot show you what happened. It can show you the place it happened, the
weather it happened in, and the objects left behind. If the edit needs the
moment itself, that is still a shoot — or, better, it is a moment the narration
should carry alone over black.
