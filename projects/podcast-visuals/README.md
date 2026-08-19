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
| Episode identified and confirmed against the show's own feed | done |
| Five segments turned into a shot list, 23 shots | done |
| Production-grade prompts for every shot, still + motion | done |
| Visual grammar and style bible | done |
| Reference-anchoring, so a location holds across shots | done |
| Continuity locked and enforced — one weather, one hour, every scene | done |
| Source recorded per shot, with the audio outranking everything | done |
| POC plan — model bake-off and how to judge it | done |
| Cost model, POC and full episode | done |
| Approval workflow — where Lasse steers, what automates | done |
| Editorial and legal rails | done |
| **Frames actually generated** | **not done — blocked** |

**The episode.** "Det Brændende Lig", *Danske Drabssager* s6e5, 29 March 2022,
44:37 — confirmed against the show's own feed, which Lukas exported to Drive.
The audio is at
`bauernordic-pods.sharp-stream.com/dk/1103/dd_s6_ep5_det_brndende_lig_913db409_normal.mp3`.

The mp3 is now in Lukas's Drive. This session still cannot read it: the Drive
connector caps downloads at 10 MB and the file is 45 MB, and every speech-model
weight host is blocked here too. **Transcription has to happen somewhere else** —
`lenovo` or a paid API — which is a dependency decision for Lukas, not one to
take unilaterally.

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
| [docs/POC.md](docs/POC.md) | **The test itself — which models, how to judge** |
| [docs/APPROACH.md](docs/APPROACH.md) | Why this will not look like AI slop |
| [docs/STYLE-BIBLE.md](docs/STYLE-BIBLE.md) | The locked look — Lasse's steering wheel |
| [docs/STORYBOARD.md](docs/STORYBOARD.md) | The five segments, shot by shot |
| [docs/PROMPT-PACK.md](docs/PROMPT-PACK.md) | The exact prompts (generated) |
| [docs/COSTS.md](docs/COSTS.md) | What a full episode costs |
| [docs/WORKFLOW.md](docs/WORKFLOW.md) | Who approves what, what runs by itself |
| [docs/RAILS.md](docs/RAILS.md) | What we never generate, and why |

## Commands

```bash
python3 render.py            # the six hero frames, as prompts
python3 render.py --all      # all 22 shots
python3 render.py --json     # machine-readable
uv run pytest tests/test_podcast_prompt_builder.py -o addopts=""
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
