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

Where a work survives in more than one tradition — Greek manuscripts, Arabic translations, medieval or Renaissance Latin — each can preserve valuable evidence. Their weight is passage-specific and depends on manuscript lineage, translation technique, editorial intervention, and date. Arabic versions may reflect Greek exemplars older than surviving direct witnesses, while also carrying a translator's interpretation.

1. **Enumerate the witnesses** for your work. The packet lists what's known; add what you find.
2. **Work from all accessible witnesses side by side.** The packet's base text is whichever tradition is sufficiently edited and digitized, usually Greek. That is a practical starting point, not a verdict on every reading.
3. **Compare every segment against every accessible witness** — not only where the base text looks wrong. Agreement is evidence too; record it.
4. **Reference what you consulted.** Every consultation goes in `refs`, with its use explained in `rationale`, cited precisely enough to re-check.
5. **Treat divergence as evidence.** When witnesses disagree, present the disagreement and argue for the selected reading without treating any tradition as automatically decisive.

Two honest caveats. Access is asymmetric today: for most works the Greek is digitized while the Arabic sits in unedited manuscripts, so the Greek often ends up as the packet's base text by default — a practical limit to push against, imposed by the tooling rather than by any priority among the witnesses. And a translation-witness like Ḥunayn's carries its translator's interpretation — which is also its value: it preserves how a brilliant ninth-century reader, holding better manuscripts than ours, understood the sentence.

## Validation

`tools/validate.py` is stdlib-only and offline. It checks schema-v2 catalogue data, registry↔packet consistency, contributor and review state, rationale and citations, URL safety, Arabic manifest coverage and checksums, and XML well-formedness. CI runs it and the unit tests on every push and PR.
