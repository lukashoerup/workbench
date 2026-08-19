# Task: AI visuals for a true crime podcast — proof of concept

Lasse Eskildsen (Bull House Media, Lukas's uncle) is testing whether a true
crime podcast can be made into television using generated imagery instead of
shot reconstruction. He sent a reference episode of *Danske Drabssager* and
five timecodes he wants to see a frame for. Lukas's brief: **POC only,
state-of-the-art models, push the quality as far as it goes.**

Lives in `projects/podcast-visuals/`. It should graduate to its own repo once
frames have been judged — it is in `workbench` because that is where the branch
was opened, and nothing here is worth a repo until the format is proven.

## Done

- [x] Reference episode and Lasse's five timecodes located (two mails,
      19 Aug 2026, `le@bullhouse.dk`)
- [x] **Episode identified and confirmed** — "Det Brændende Lig", s6e5,
      29 Mar 2022, 44:37. Lukas exported the show's feed to Drive; of 219
      episodes it is the only one whose length and description fit the five
      timecodes. Its description gives the case directly, and its four
      contributors — Isager-Nielsen, Hytholm Jensen, Hougen, Stürup — are
      exactly Lasse's five markers
- [x] Fact, art direction and guess separated in the docs. The weather is a
      choice, not a source. The dental-identification detail is from *Dødens
      detektiver* and is marked as unconfirmed
- [x] X-01 added: the newspaper bundle, printed side down. The episode turns on
      a photograph of the dead woman's face being published — the one image we
      will never generate, and the best possible demonstration of the rule
- [x] Continuity frozen and enforced — one wet grey autumn day across every
      scene, with a check that rejects a shot fighting it. Caught a real error:
      the tyre print had been written with low sun and now takes its relief
      from a technician's work lamp
- [x] Five segments turned into a 22-shot storyboard, six of them hero frames
- [x] `prompt_builder.py` — shot + frozen look + world registry → prompt.
      The ImageBooks `promptBuilder` separation, with the registry holding
      places and objects instead of characters
- [x] Editorial rails enforced in code: `check_shot()` rejects a shot naming a
      face, a portrait, a body or a wound, and the whole shot list is
      re-checked by the suite on every commit
- [x] Reference anchoring — an approved anchor frame conditions every later
      shot in the same location; prompt pack is ordered anchors-first
- [x] Style bible, POC plan with a five-model bake-off, cost model, approval
      workflow, legal and editorial rails — all under `docs/`
- [x] Source tier recorded per shot — audio > Lasse's notes > the episode's
      description > case reporting > art direction — with tests forbidding any
      shot from claiming the audio while no transcript exists, and forbidding a
      hero frame sourced to art direction alone. Current split: 0 / 6 / 7 / 1 / 9
- [x] `transcript.py` — tolerant reader for SRT, VTT, bracketed and plain
      timestamps, refusing a transcript with none; window slicing by clock; a
      coverage check against the episode's 44:37 to catch the quiet failure
      where a transcript stops halfway
- [x] 345 tests green

## Generated, 19–20 Aug

- [x] Gemini key from Lukas; Nano Banana Pro **and Veo 3.1** both on it, so
      Google Flow was never needed
- [x] `generate.py` and `animate.py` — stdlib, key from the environment, never
      written to disk; every image and clip logged to a manifest with model,
      prompt and time, which is what AI Act disclosure will want
- [x] 54 stills, 2 clips, **58 kr of 200**. Selected frames in `stills/`
- [x] Four rails breaches found by *looking* — an invented car, a burned-in
      timecode, handprints, letterboxing — all now closed. See `docs/FINDINGS.md`
- [x] Motion grammar gained a no-net-change clause after the first clip ended
      with the bonfire swallowed by a smoke plume

## Blocked — needs Lukas

Neither is solvable from a cloud session; both are small.

1. **The transcript.** The mp3 is in Drive (45 MB) but unreachable from a
   cloud session: the Drive connector caps downloads at 10 MB, and every
   speech-model weight host — OpenAI's, Hugging Face, Vosk, Google, the CDNs —
   is blocked by egress policy, so there is no ASR here even with the bytes.
   Splitting the file would deliver audio and still not deliver words.
   **Decided with Lukas 19 Aug: he transcribes the full episode himself and
   puts it in Drive as a document**, the way the RSS feed arrived. Format spec
   and what happens next: `docs/TRANSCRIPT.md`.
2. **A generation account.** No image or video model is reachable from here and
   none of Lukas's keys are attached. Google AI Studio covers both Nano Banana
   Pro and Veo with one key. Budget for the whole POC: about 1,000 DKK for the
   full bake-off, 150 DKK for a single model.

With (1) the shot list becomes real. With (2) the six frames get rendered,
which is the actual test.

## Next, once unblocked

- [x] Transcript read from Drive; identification **confirmed** — four of five
      timecodes matched by content, in Lasse's order
- [x] Shot list rewritten against the audio: 20 of 24 shots now `audio`, up
      from 0. Segment 4 rebuilt from an interrogation to the disposal; the look
      moved to late September 1999; the weather confirmed rather than assumed
- [ ] **Transcribe 30:00–44:37** — the free tier stopped at 30 min, so segment 5
      is still on Lasse's note. Cut a clip and run it as a second file, or use a
      paid tier once
- [ ] Then rewrite S5-01..03 against the audio and re-source them
- [ ] Run the bake-off in `docs/POC.md`; judge on a television, not a laptop
- [ ] Record the result in `docs/POC.md` and the winning model in
      `context/STACK.md`
- [ ] Only then decide whether to build the pipeline in `docs/WORKFLOW.md`

## Notes

- The no-faces rule came from Lasse ("der behøver ikke være konsistente
  karakterer") and turns out to be load-bearing three times over: it is what the
  models are best at, it removes character consistency as a problem entirely,
  and it stays clear of every AI controversy this genre has had. Documented in
  `docs/APPROACH.md` and `docs/RAILS.md`.
- EU AI Act Article 50 has applied since **2 August 2026** — visible disclosure
  at first exposure plus machine-readable marking. This is a live delivery
  requirement, not a future one.
- ImageBooks' real lesson was the one it failed at: it stubbed generation and
  never proved the output. Do not build the pipeline before the frames are
  judged.
