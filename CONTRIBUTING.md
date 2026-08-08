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

A **chunk** is a passage anchored to Kühn page numbers (typically one chapter or a few pages). The pipeline — see [HARNESS.md](HARNESS.md) for full details:

1. **Claim** a chunk by opening an issue ("Claim: CML 1.2, Kühn XII 381–403").
2. **Get a packet**: pick an `open` chunk from [`data/chunks.json`](data/chunks.json), or generate one — `python3 tools/make_packet.py --work tlg076 --book 1 --chapter 3 --id cml-1-3 --volume 12`. The packet holds the Greek with Kühn anchors and empty slots for your work.
3. **Draft**: fill in `eng` per segment — plain, readable English. AI assistance is welcome and normal here; you are responsible for the result. Compare every accessible witness (Kühn's facing Latin, the Arabic tradition where it survives) as **peers** — see the [peer-witness protocol](HARNESS.md#the-peer-witness-protocol).
4. **Trace and reference**: fill in `trace` per segment — your working, LLM-style: renderings weighed, syntax puzzles, how the witnesses compared — and `refs` with a citation for every witness consulted. We publish the reasoning alongside the result on purpose. Use `notes` for reader-facing color; identify drug/plant names via LSJ ([Logeion](https://logeion.uchicago.edu/)) rather than guessing.
5. **Validate and PR**: run `python3 tools/validate.py` (CI runs it too), set status to `draft`, and PR the JSON. The page renders automatically at `translations/chunk.html?id=<your-id>`.
6. **Review**: a second reader with Greek checks the draft against the source; disagreements are argued in the PR with the Greek quoted. Review flips status to `reviewed`.

### House style

- Readable modern English over word-for-word crib; but never smooth away what the Greek actually says.
- Keep Galen's voice — he complains, he boasts, he digresses. That's the good part.
- Transliterate technical terms on first use with a gloss: *krasis* ("mixture"), *achōr* (scalp sore).
- Weights and measures: keep the Greek units (drachma, kotylē) with a footnote, don't convert.

## Ground rules

- Everything is CC BY-SA 4.0; by contributing you agree.
- Be kind in review; everyone here is an amateur or acting like one on purpose.
- Cite sources for factual claims about the corpus. "I checked X and found nothing" is a valid, useful citation.
