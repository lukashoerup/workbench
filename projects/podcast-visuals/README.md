# Podcast visuals — can AI imagery carry a true crime programme?

A proof of concept, not a product. Lasse Eskildsen (Bull House Media) sent a
reference episode of *Danske Drabssager* and five timecodes he wanted to see a
frame for. The question behind it: can generated imagery with a little motion
replace shot reconstruction well enough to make a podcast into television, and
at what cost.

**Scope: six frames, flagship models, quality maximised.** Cost is not a
constraint at POC size, so nothing here trades quality for price. The pipeline
and series economics are documented because the answer matters, but none of it
gets built until six frames have been judged on a television.

## Status — 19 Aug 2026

| Piece | State |
|---|---|
| Episode identified, then **confirmed against the audio** | done |
| Five segments turned into a shot list, 24 shots, 20 of them from the audio | done |
| Production-grade prompts for every shot, still + motion | done |
| Visual grammar and style bible | done |
| Reference-anchoring, so a location holds across shots | done |
| Continuity locked and enforced — one weather, one year, every scene | done |
| Motion grammar: slight slow motion, frozen across every clip | done |
| A second look — charcoal and ink — to test against the photographic one | done |
| Source recorded per shot, with the audio outranking everything | done |
| POC plan — model bake-off and how to judge it | done |
| Cost model, POC and full episode | done |
| Approval workflow — where Lasse steers, what automates | done |
| Editorial and legal rails | done |
| **Frames actually generated** | **done — 54 stills, 2 clips, 58 kr** |
| Findings from looking at the output | [docs/FINDINGS.md](docs/FINDINGS.md) |

**The episode.** "Det Brændende Lig", *Danske Drabssager* s6e5, 29 March 2022,
44:37 — confirmed against the show's own feed, which Lukas exported to Drive.
The audio is at
`bauernordic-pods.sharp-stream.com/dk/1103/dd_s6_ep5_det_brndende_lig_913db409_normal.mp3`.

**The transcript arrived 19 Aug** (TurboScribe free tier, via Drive) and settled
the identification: four of Lasse's five timecodes are matched by content, in
his order. It also corrected a real mistake — the 20:17 segment is the disposal,
not an interrogation — and confirmed the weather, which had been a guess.

It covers the first 30 minutes only, the free tier's ceiling, so segment 5 (the
prosecutor at 36:40) still rests on Lasse's note. See
[docs/TRANSCRIPT.md](docs/TRANSCRIPT.md). The transcript itself stays in Drive:
it is a verbatim transcript of a commercial podcast and this repo is public.

**What blocks the frames.** Until there is a transcript, every shot rests on
the episode's published description, Lasse's notes, or art direction — recorded
per shot and enforced (see [docs/STORYBOARD.md](docs/STORYBOARD.md)). And there
is no image or video generation account attached, so nothing can be rendered.
See [docs/WORKFLOW.md](docs/WORKFLOW.md#what-is-needed-to-run-the-first-pass).

Everything else is finished and the prompts are ready to paste into a generator
by hand today.

## Read in this order

| Document | What it answers |
|---|---|
| [docs/FINDINGS.md](docs/FINDINGS.md) | **What the first pass showed — read this first** |
| [docs/REVIEW-LASSE.md](docs/REVIEW-LASSE.md) | **The pitch reviewed in character as Lasse, and what it cost us** |
| [stills/](stills) | The frames themselves |
| [clips/](clips) | Four clips, Veo 3.1 Fast, first-frame-conditioned |
| [docs/START-HERE.md](docs/START-HERE.md) | Which programs, what to paste, in what order |
| [docs/POC.md](docs/POC.md) | The test itself — which models, how to judge |
| [docs/APPROACH.md](docs/APPROACH.md) | Why this will not look like AI slop |
| [docs/STYLE-BIBLE.md](docs/STYLE-BIBLE.md) | The locked look — Lasse's steering wheel |
| [docs/STORYBOARD.md](docs/STORYBOARD.md) | The five segments, shot by shot |
| [docs/SCENEOVERSIGT.md](docs/SCENEOVERSIGT.md) | The Danish scene list handed to Lasse — timecodes and file names |
| [docs/PROMPT-PACK.md](docs/PROMPT-PACK.md) | The exact prompts, photographic look (generated) |
| [docs/PROMPT-PACK-DRAWN.md](docs/PROMPT-PACK-DRAWN.md) | The same shots, charcoal-and-ink look (generated) |
| [docs/COSTS.md](docs/COSTS.md) | What a full episode costs |
| [docs/WORKFLOW.md](docs/WORKFLOW.md) | Who approves what, what runs by itself |
| [docs/RAILS.md](docs/RAILS.md) | What we never generate, and why |
| [docs/TRANSCRIPT.md](docs/TRANSCRIPT.md) | What to produce, and what happens then |

## Commands

```bash
GEMINI_API_KEY=... python3 generate.py            # the hero frames, for real
GEMINI_API_KEY=... python3 animate.py S1-01 --frame stills/S1-01-photo.jpg
python3 render.py                  # the hero frames, photographic look
python3 render.py --look drawn     # the same frames, charcoal and ink
python3 render.py --all            # all 24 shots
python3 render.py --json           # machine-readable
uv run pytest tests/ -o addopts=""
```

## Where the code lives

`prompt_builder.py` is the reusable core: it turns a shot plus the frozen look
plus the world registry into a prompt, and refuses shots that break the rails.
`episode.py` is the data for this one episode. `render.py` prints it.

This should graduate to its own repo once it stops being a test. It sits inside
`workbench` for now because that is where the branch was opened, and because
nothing here is worth a repo until Lasse has seen frames.

## What ImageBooks contributed

The earlier ImageBooks POC built prompts from a scene plus a registry of
character descriptions. That separation is the right one and is reused here,
with the registry holding **places and objects** instead of characters. Two
things carried over as lessons rather than code: the effort that went into
character consistency is not needed here — and is in fact the part to avoid
(see [docs/RAILS.md](docs/RAILS.md)) — and ImageBooks stubbed its generation
and never proved the output, which is the one thing this test must not repeat.
