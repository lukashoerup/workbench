# Workflow — where Lasse steers, what runs by itself

The design problem is not "how much can be automated". It is **where a
producer's judgement is worth most per hour**, and putting the gates exactly
there. Everything between gates should run unattended.

## The pipeline

```
episode audio
   ↓  transcribe            automatic   Danish, diarised, word timestamps
transcript
   ↓  beat sheet            automatic   narration split into visual beats
beats
   ↓  shot list             automatic   1–3 shots per beat, drafted
┌─────────────────────────────────────────────────────────┐
│  GATE 1 — Lasse reads and rewrites the shot list        │  2–3 h
└─────────────────────────────────────────────────────────┘
   ↓  prompt build          automatic   shot + locked look + registry
   ↓  stills, 4 variants    automatic   ~2 h unattended
┌─────────────────────────────────────────────────────────┐
│  GATE 2 — Lasse picks, rejects, re-rolls (contact sheet)│  3–4 h
└─────────────────────────────────────────────────────────┘
   ↓  motion assign         automatic   tier A / B / C
   ↓  clips                 automatic   approved frames only
   ↓  assembly              automatic   EDL/XML into Premiere or Resolve
edit
```

## Gate 1 — the shot list. This is where quality is decided.

A table: timecode, what is said, what we will show, motion tier. Lasse edits
the "what we will show" column, deletes shots, adds shots, changes the order.

It costs nothing. Not a single credit has been spent when this gate opens,
which is the entire point of putting it first — **90% of whether the episode is
any good is decided here, at zero marginal cost.** A wrong idea rejected at
gate 1 costs three minutes. The same idea rejected after rendering costs a
morning.

If Lasse only ever has time for one gate, it is this one.

## Gate 2 — the selects. This is where the money is protected.

A contact sheet: four variants per shot, click to approve, reject or re-roll
with a note.

The gate sits deliberately **between stills and video**, because video costs
roughly ten times what a still costs. Only approved frames get animated, so a
rejected frame costs $0.13 instead of $1.50. Everything that makes this format
affordable comes from that ordering.

## The third control: the style bible

Not a gate — a dial, and the one with the longest reach. One line in
[STYLE-BIBLE.md](STYLE-BIBLE.md) changes all 324 shots at once. If Lasse says
"colder, and stop the amber", that is one edit and a re-render, not 324 notes.

Watch for the failure mode where notes that belong in the style bible get given
as per-shot notes instead. Three shots asking for the same correction is a
style bible change, and treating it as three notes is how drift starts.

## Division of labour

| | Lasse | The machine | The editor |
|---|---|---|---|
| What the sequence is *about* | ● | | |
| Which beats get pictures | ● | drafts it | |
| What is in frame | ● | drafts it | |
| Camera, lens, light | | ● | |
| Consistency across 324 shots | | ● | |
| Which variant is the one | ● | | ● |
| Rhythm, cutting, grade, sound | | | ● |
| Rails compliance | audits | ● enforced in code | |

The machine never decides what a sequence means, and Lasse never writes a
prompt. Both of those boundaries matter: the first is editorial, the second is
just a bad use of a producer's afternoon.

## What is needed to run the first pass

Three things, none of them large:

1. **The episode audio** as a file — mp3 or m4a. Dropping it in Google Drive is
   enough; a session can read it from there. This session's network policy
   blocks the podcast hosts, so the file cannot be fetched from the feed here.
2. **An image generation account.** Google AI Studio is the cheapest route to
   Nano Banana Pro and needs a card on file, no negotiation. Budget for the
   test: under 200 DKK.
3. **A video generation account** — the same Google key covers Veo; Kling is a
   separate signup and cheaper.

With (1) alone the transcript and a real shot list can be produced. With (2)
the six hero frames can be rendered — that is the actual test. (3) only matters
once the frames are approved.

## Once it works — what a series looks like

Per episode, the recurring human cost is gate 1 plus gate 2, about six hours of
Lasse's time. Everything else is either automatic or normal edit work.

Two things get cheaper with every episode and are worth building deliberately:

- **The entity registry.** Recurring Danish locations — a police station
  corridor, a courtroom, a motorway at night, a summer field — are written
  once and reused across the series. By episode five most shots draw on
  descriptions that already exist and have already been approved on screen.
- **The accept rate.** Prompts that produced good frames are the training set
  for the next episode's drafting pass. This is the compounding part.

## Not yet built

The pipeline above is the design. What exists in this repo today is the part
that determines quality — the prompt builder, the rails, the style bible and
the shot list — plus `render.py`, which produces the prompts for hand-pasting.
The transcription, generation and assembly stages are specified but not coded,
deliberately: writing them before a single frame has been judged would be
building a factory before knowing whether the product is any good.
