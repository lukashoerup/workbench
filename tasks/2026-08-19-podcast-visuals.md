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
- [x] 211 tests green

## Blocked — needs Lukas

Neither is solvable from a cloud session; both are small.

1. **The episode audio.** Known exactly now:
   `https://bauernordic-pods.sharp-stream.com/dk/1103/dd_s6_ep5_det_brndende_lig_913db409_normal.mp3`
   — this session's network policy blocks that host, so it has to be fetched by
   hand. **Open that link, save the mp3, drop it in Google Drive.** Subject
   lines currently come from the episode's published description, not from what
   is said in it.
2. **A generation account.** No image or video model is reachable from here and
   none of Lukas's keys are attached. Google AI Studio covers both Nano Banana
   Pro and Veo with one key. Budget for the whole POC: about 1,000 DKK for the
   full bake-off, 150 DKK for a single model.

With (1) the shot list becomes real. With (2) the six frames get rendered,
which is the actual test.

## Next, once unblocked

- [ ] Transcribe, diarised with word timestamps; rewrite the subject lines
      against what is actually said
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
