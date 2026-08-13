# Contributing to Pergamap

Three ways in, smallest first. No Greek required for the first two.

## 1. Verify a catalog entry (15 minutes, no Greek)

Most entries in [`data/works.json`](data/works.json) have `english.verification.status` set to `recalled` (needs a citation check) or `unknown` (never checked). Pick one and answer: **does a published English translation of this work exist?**

Good places to look: the *Oxford Handbook of Galen*'s list of works, the Corpus Medicorum Graecorum catalog (cmg.bbaw.de), WorldCat, Loeb Classical Library, Brill's Galen translations.

Then open an issue (or PR against `works.json`) with the work's `id`, what you found, and your source. Set `english.verification.status` to `checked` only when `checked_on` and `source_ids` identify where you checked. Add the bibliographic source once to the document-level `sources` list and reference its ID from the work.

## 2. Vote and propose

- The corrected first-campaign shortlist was checked against the BBAW translation catalogue on 12 August 2026. Vote on [issue #1](https://github.com/posix4e/pergamap/issues/1), and please report any overlooked or unlisted English translation.
- Propose a different target by commenting there. The criteria (see the [roadmap](https://pergamap.com/roadmap.html)): no existing English, digitized source, finishable, humanly interesting.

## BBAW/CMG catalogue snapshot

`python3 tools/sync_bbaw.py` downloads the BBAW/CMG Galen translation catalogue and rewrites `data/bbaw-galen-translations.json`. A weekly GitHub Actions job runs the same importer and opens or updates a reviewable PR when the upstream catalogue changes. `data/bbaw-crosswalk.json` connects Pergamap work IDs to BBAW record IDs, and `python3 tools/check_bbaw_drift.py` flags new English-status disagreements. The index is source evidence; it deliberately does not overwrite the editorial judgments in `data/works.json`.

## 3. Translate or review a chunk

A **chunk** is a passage anchored to Kühn page numbers (typically one chapter or a few pages). The pipeline — see [HARNESS.md](HARNESS.md) for full details:

1. **Claim** a manageable range by opening an issue ("Claim: CML 1.3, Kühn XII 427–434").
2. **Get a packet**: pick an `open` chunk from the `chunks` list in [`data/chunks.json`](data/chunks.json), or generate one — `python3 tools/make_packet.py --work tlg076 --book 1 --chapter 3 --id cml-1-3a --volume 12 --start-page 427 --end-page 434`. The packet holds pinned source provenance, Greek with Kühn anchors, and empty slots for your work.
3. **Draft**: fill in `eng` per segment — plain, readable English. AI assistance is welcome; you remain responsible for the result. Compare every accessible witness. Where a version diverges, ask which underlying Greek reading would account for it, and say whether you are claiming a variant in the text or a construal of it — see the [witness protocol](HARNESS.md#the-witness-protocol).
4. **Rationale and references**: fill in `rationale` with a concise account of alternatives, syntax, evidence, and uncertainty. Fill in `refs` with a precise citation for every witness consulted. Do not include hidden chain-of-thought or claim that a summary is a model's private reasoning. Use `notes` for reader-facing context; identify drug and plant names via LSJ ([Logeion](https://logeion.uchicago.edu/)) rather than guessing.
5. **Validate and PR**: run `python3 tools/validate.py` and `python3 -m unittest discover -s tests -v`, set both registry and packet status to `draft`, add translator attribution, and PR the JSON. The page renders automatically at `translations/chunk.html?id=<your-id>`.
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
- Ancient remedies are historical material, not medical advice. Never encourage readers to prepare or use them.
