# Rails — what we never generate, and why

These are not style preferences. They are the difference between a format that
can be sold to a broadcaster and one that becomes the story itself.

## The hard rules

1. **No recognisable human face.** No portraits, no eye contact, no close-ups
   of a person. Hands, backs, silhouettes beyond ~30m, and out-of-focus figures
   are fine.
2. **No depiction of the victim, the body, wounds or blood.** Show the room,
   the instrument, the aftermath, or nothing.
3. **No synthetic material presented as, or mistakable for, archive.** No fake
   police photographs, fake evidence photos, fake press cuttings, fake CCTV.
   The imagery is evocative; it is never evidentiary.
4. **No AI voices of real people**, living or dead.
5. **No legible text in frame.** Partly because models still fumble it, mostly
   because a generated document is a fabricated document.
6. **Nothing that identifies a real private individual** — a real address, a
   real number plate, a real house that can be found.

Rules 1 and 2 are enforced in code: `check_shot()` in `prompt_builder.py`
rejects a shot whose subject, atmosphere or motion names a face, a portrait, a
body or a wound, and the whole shot list is re-checked by the test suite on
every commit. The check is deliberately blunt. A false positive costs a
rewording; a false negative is a real person's face in a programme about a real
killing.

## Why — the recent record

Every AI controversy in this genre has been about a depicted **person**:

- **Netflix, *What Jennifer Did* (2024)** — AI-manipulated images of a real
  woman used among archive material, unlabelled. Netflix subsequently issued AI
  guidelines to production partners.
- **Netflix, *American Murder: Gabby Petito*** — AI recreation of a murdered
  woman's voice reading her own writing.
- **Netflix, *The Investigation of Lucy Letby* (2026)** — synthetic
  "digitally anonymised" interviewees, widely described as distracting and
  unsettling, and read by critics as a betrayal of the genre's contract with
  its audience.

None of them were about a shot of ash, or blue light on a hedge, or rain on a
courthouse step. The line the audience polices is *people*, and the withheld
frame stays on the safe side of it by construction.

## The regulation

The EU AI Act's transparency obligations (Article 50) **apply from 2 August
2026** — already in force. For a programme carrying generated imagery this
means, in practice:

- Content must be **machine-readable marked** as synthetic. Google's image
  models already embed SynthID; keep whatever the chosen model provides and do
  not strip it in the grade or the export.
- The audience must be **told, at first exposure**. An end-credit line is not
  enough on its own — plan a visible disclosure at the top of the programme,
  and a consistent on-screen treatment for generated sequences.
- The Commission's guidelines expect deployers in a production and
  distribution chain to take **proportionate measures** so the disclosure
  survives to the audience — i.e. it belongs in the delivery spec and the
  distribution contract, not only in the master.
- Penalties run to €15m or 3% of worldwide turnover, so this is a
  production-compliance item, not a courtesy.
- The lighter regime for artistic and creative work is to be read **strictly**,
  and a factual programme about a real killing is not going to qualify.

Two practical consequences worth deciding early, because they are cheap now and
expensive later: agree the on-screen label treatment with the broadcaster
before the edit locks, and keep a per-shot record of model, prompt, seed and
date. The pipeline produces that record for free.

**Not legal advice.** Someone with a media-law practice should sign off the
disclosure wording and the delivery spec before a first transmission, and
should also be asked about Danish likeness rules — the no-faces rule almost
certainly sidesteps them, but "almost certainly" is not a clearance.

## The editorial position, in one line

*The pictures show the world the case happened in. They never show the case.*

If someone can watch a sequence and come away believing they have seen
something that happened, the sequence is wrong — no matter how good it looks.
