# Contributing to Galen Atlas

Three ways in, smallest first. No Greek required for the first two.

## 1. Verify a catalog entry (15 minutes, no Greek)

Most entries in [`data/works.json`](data/works.json) are marked `recalled` (needs a citation check) or `unknown` (never checked). Pick one and answer: **does a published English translation of this work exist?**

Good places to look: the *Oxford Handbook of Galen*'s list of works, the Corpus Medicorum Graecorum catalog (cmg.bbaw.de), WorldCat, Loeb Classical Library, Brill's Galen translations.

Then open an issue (or PR against `works.json`) with the work's `id`, what you found, and your source. Set `confidence` to `checked` in a PR only if you cite where you checked.

## 2. Vote and propose

- Vote for the first full translation campaign in [issue #1](../../issues/1) — 👍 the candidate comments.
- Propose a different target by commenting there. The criteria (see the [roadmap](https://posix4e.github.io/galen-atlas/roadmap.html)): no existing English, digitized source, finishable, humanly interesting.

## 3. Translate or review a chunk

A **chunk** is a passage anchored to Kühn page numbers (typically one chapter or a few pages). The pipeline:

1. **Claim** a chunk by opening an issue ("Claim: CML 1.2, Kühn XII 381–403").
2. **Greek source**: extract from the First1KGreek TEI XML (`data/tlg0057/` in their repo). Keep the Kühn page anchors.
3. **Draft**: translate into plain, readable English. AI assistance is welcome and normal here; you are responsible for the result. When the Greek is ambiguous, consult Kühn's facing Latin and say so in a note.
4. **Notes**: flag every uncertainty honestly. Identify drug/plant names via LSJ ([Logeion](https://logeion.uchicago.edu/)) rather than guessing.
5. **PR**: one HTML file per chunk in `translations/`, following the structure of [`translations/cml-1-1.html`](translations/cml-1-1.html) (Greek and English paired paragraph by paragraph, notes at the end). Mark it `draft — awaiting reviewer`.
6. **Review**: a second reader with Greek checks the draft against the source; disagreements are argued in the PR with the Greek quoted. Review removes the draft flag.

### House style

- Readable modern English over word-for-word crib; but never smooth away what the Greek actually says.
- Keep Galen's voice — he complains, he boasts, he digresses. That's the good part.
- Transliterate technical terms on first use with a gloss: *krasis* ("mixture"), *achōr* (scalp sore).
- Weights and measures: keep the Greek units (drachma, kotylē) with a footnote, don't convert.

## Ground rules

- Everything is CC BY-SA 4.0; by contributing you agree.
- Be kind in review; everyone here is an amateur or acting like one on purpose.
- Cite sources for factual claims about the corpus. "I checked X and found nothing" is a valid, useful citation.
