# The translation harness

Tooling that turns "I want to translate some Galen" into a five-minute setup. One command produces a **translation packet** — a JSON file holding everything one chunk needs: Greek with Kühn page anchors, immutable source provenance, witness pointers, and slots for English, translation rationale, citations, and notes.

## Quickstart

```bash
# 1. Generate a packet (downloads + caches the TEI XML automatically)
python3 tools/make_packet.py --work tlg076 --book 1 --chapter 3 --id cml-1-3a \
  --volume 12 --start-page 427 --end-page 434

# 2. Fill in translations/chunks/cml-1-3a.json: eng, rationale, refs, notes
# 3. Check your work
python3 tools/validate.py

# 4. Preview: serve the repo root and open translations/chunk.html?id=cml-1-3a
python3 -m http.server 8000

# 5. PR the JSON (registry entry in data/chunks.json is updated automatically)
```

Or skip step 1 entirely: pick any chunk with status `open` in [`data/chunks.json`](data/chunks.json) — its packet is already generated and waiting.

## The packet format

```jsonc
{
  "schema_version": 2,
  "id": "cml-1-2",
  "work": "tlg076",              // must exist in data/works.json
  "kuhn_range": "12.381–12.403",
  "status": "open",              // open → claimed → draft → reviewed
  "witnesses": { "kuhn_latin": { "status": "unaligned", "scan_url": "…" } },
  "segments": [
    { "kuhn": "12.381",
      "grc": "…the Greek…",
      "eng": "…your English…",
      "rationale": "…alternatives, evidence, and uncertainty…",
      "refs": ["…edition and page…"],
      "notes": "…reader-facing notes…" }
  ]
}
```

Segmentation starts at one segment per Kühn page and is **provisional**. Use `--start-page` and `--end-page` to keep a claim manageable, then split or merge segments at argument boundaries. Packet source URLs are pinned to a First1KGreek commit and carry a full checksum. Existing packet IDs are never overwritten unless `--force` is supplied deliberately.

## Translation rationale

Every translated segment must carry a concise `rationale` that another reader can audit:

- renderings you weighed and why the winner won;
- syntax you initially misread and how you caught it;
- which witnesses you consulted (Kühn's Latin, Arabic tradition) and whether they agreed;
- what you're still unsure about, plainly.

`rationale` is the evidence-based decision record; `notes` are reader-facing context. Do not publish hidden chain-of-thought or represent a concise rationale as a model's private reasoning.

## The witness protocol

The Greek manuscripts are the **direct tradition**. The Arabic and Latin versions are **indirect tradition**: evidence about the text that is not itself a copy of it, in the same class as quotations in a commentary, and therefore part of the reception history. That classification does not put them out of textual play. The Arabic manuscripts descend from Greek exemplars that differ from — and may antedate — the earliest surviving Greek witnesses, so a versional reading can come from an independent branch or corroborate a variant already attested in Greek. A version accordingly belongs in the stemma wherever one can be constructed.

The operative question is not how good the translator was. It is **which underlying Greek variant would account for the reading in front of you** — that is what places a version within the *stemma codicum*. Translation technique matters instrumentally rather than as a measure of worth: knowing how a particular translator worked is what makes retroversion to the Greek better than guesswork.

Two things a version can give you, and they must not be confused:

- **A variant.** The rendering is best explained by a Greek reading different from the printed text. This is stemmatic evidence and should be reported as such.
- **A construal.** The Greek is not in doubt, and the version records how a learned reader took an ambiguous word or construction. This is evidence about meaning, not about text. It is often the more useful kind for a translator — and must not be dressed up as the first.

1. **Enumerate the witnesses** for your work. The packet lists what's known; add what you find.
2. **Work from all accessible witnesses side by side.** The packet's base text is whichever tradition is sufficiently edited and digitized, usually Greek. That is a practical starting point, not a verdict on any reading.
3. **Compare every segment against every accessible witness** — not only where the base text looks wrong. Agreement is evidence too; record it.
4. **Ask what Greek would produce this.** Where a version diverges, state whether you are claiming a variant or a construal, and say which Greek reading would explain the rendering.
5. **Reference what you consulted.** Every consultation goes in `refs`, with its use explained in `rationale`, cited precisely enough to re-check.
6. **Treat divergence as evidence.** Present the disagreement and argue for the selected reading without treating any tradition as automatically decisive.

One honest caveat about access. For most works the Greek is digitized while the Arabic sits in unedited manuscripts, so the Greek becomes the packet's base text by default — a limit imposed by the tooling, not a judgement about the traditions.

*Revised August 2026 following guidance given in private correspondence by a scholar of the Greek-into-Arabic translation movement. We have not yet asked whether we may name them, so we do not. Any distortion of their advice is ours.*

## Validation

`tools/validate.py` is stdlib-only and offline. It checks schema-v2 catalogue data, registry↔packet consistency, contributor and review state, rationale and citations, URL safety, Arabic manifest coverage and checksums, and XML well-formedness. CI runs it and the unit tests on every push and PR.
