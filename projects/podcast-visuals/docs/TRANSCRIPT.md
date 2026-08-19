# The transcript — what to produce, and what happens when it lands

Lukas is producing this with whatever tool suits him. The format is not ours to
dictate, so `transcript.py` reads the shapes that actually turn up: SRT, WebVTT,
`[00:03:30] text`, `00:03:30  text`, and `3:30` short clocks, with or without
speaker prefixes, and with wrapped lines joined back onto their cue.

## The one thing that is not optional

**Timestamps.** Without them the transcript cannot be tied to Lasse's
timecodes, which is the entire reason for having it — and that is exactly the
failure that would not announce itself, because a transcript with no timestamps
still reads perfectly well. So the reader refuses one outright rather than
accepting it and going quiet.

Ask the tool for **SRT** if it offers a choice. It is the most common export,
it carries times per line, and it survives being pasted into a document.

## Everything else is a bonus

- **Speaker labels** are worth having. There are five voices — Stine Bolther
  hosting, plus Isager-Nielsen, Hytholm Jensen, Hougen and Stürup — and knowing
  who is speaking tells us which of Lasse's five segments we are in without
  guessing from content.
- **Danish accuracy** varies a lot by tool. The good ones sit around 96–99% on
  Danish. Names will be wrong regardless; that does not matter here, because we
  are mining the transcript for *what is described*, not quoting it.

## Where to put it

A Google Doc in Drive, the way the RSS feed arrived. That path is proven
between us and needs no keys, no new dependencies and no approval. Paste the
SRT straight in — the reader does not mind the document formatting.

## What happens then

1. **Coverage check first.** `coverage()` compares the last timestamp against
   the episode's 44:37. A transcript that quietly stops at minute twenty is the
   expensive failure — it parses, it reads fine, and the missing half is the
   half nobody checked.
2. **The five windows get sliced out**, with padding so a sentence that starts
   just before a timecode is not lost:

   | Lasse's timecode | Sliced with padding |
   |---|---|
   | 03:30–06:00 | 03:00–06:30 |
   | 09:34–13:00 | 09:00–13:30 |
   | 15:30–17:09 | 15:00–17:40 |
   | 20:17–21:05 | 19:45–21:35 |
   | 36:40–39:36 | 36:10–40:10 |

3. **The identification is settled.** If 03:30 is children and a bonfire and
   20:17 is a suspect under pressure, this is Lasse's episode and the question
   is closed. See the certainty note in [STORYBOARD.md](STORYBOARD.md).
4. **Subject lines get rewritten against what is actually said**, and each
   shot's `source` is upgraded from `notes` / `description` / `case` to
   `audio`. The suite currently forbids any shot claiming `audio`; that guard
   is lifted in the same commit that adds the transcript, and not before.
5. **The nine art-direction shots get revisited.** Several should be replaced
   by shots the narration actually supports. Expect that count to fall — it is
   the single clearest measure of whether the transcript did its job.
6. **The weather gets checked.** The wet grey day is a choice, not a fact. If
   the narration says otherwise, the look changes — one line, and all 23 shots
   move with it.

## What the transcript will not change

The visual grammar, the rails, the continuity discipline and the anchor
mechanism are all independent of what is said. Only the shot *content* is
downstream of the transcript. That separation is deliberate: it is why the look
could be locked before the words arrived.
