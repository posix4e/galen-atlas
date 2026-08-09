# The translation harness

Tooling that turns "I want to translate some Galen" into a five-minute setup. One command produces a **translation packet** — a JSON file holding everything one chunk needs: the Greek with Kühn page anchors, source links, witness pointers, and empty slots for the English, the reasoning, and notes.

## Quickstart

```bash
# 1. Generate a packet (downloads + caches the TEI XML automatically)
python3 tools/make_packet.py --work tlg076 --book 1 --chapter 3 --id cml-1-3 --volume 12

# 2. Fill in translations/chunks/cml-1-3.json: eng, trace, notes per segment
# 3. Check your work
python3 tools/validate.py

# 4. Preview: serve the repo root and open translations/chunk.html?id=cml-1-3
python3 -m http.server 8000

# 5. PR the JSON (registry entry in data/chunks.json is updated automatically)
```

Or skip step 1 entirely: pick any chunk with status `open` in [`data/chunks.json`](data/chunks.json) — its packet is already generated and waiting.

## The packet format

```jsonc
{
  "id": "cml-1-2",
  "work": "tlg076",              // must exist in data/works.json
  "kuhn_range": "12.381–12.403",
  "status": "open",              // open → claimed → draft → reviewed
  "witnesses": { "kuhn_latin": { "status": "unaligned", "scan_url": "…" } },
  "segments": [
    { "kuhn": "12.381",
      "grc": "…the Greek…",
      "eng": "…your English…",
      "trace": "…your working…",
      "notes": "…reader-facing notes…" }
  ]
}
```

Segmentation is one segment per Kühn page and **provisional** — split or merge segments to follow the argument; the page numbers serve only as anchors.

## Traces: show the working

Every translated segment should carry a `trace` — the translator's reasoning, the way an LLM shows its thinking. Not a polished essay; the actual working:

- renderings you weighed and why the winner won;
- syntax you initially misread and how you caught it;
- which witnesses you consulted (Kühn's Latin, Arabic tradition) and whether they agreed;
- what you're still unsure about, plainly.

`trace` is the audit trail (how we got here); `notes` are for the reader (what's interesting here). A translation whose reasoning can be checked is worth more than a prettier one that can't. AI-assisted drafts should preserve the model's actual deliberation for the tricky calls, in place of a tidied-up summary written after the fact.

## The peer-witness protocol

Where a work survives in more than one tradition — Greek manuscripts, Ḥunayn's Arabic, medieval or Renaissance Latin — those traditions are **peer witnesses to a lost original, of equal standing**. The surviving Greek copies are mostly 12th–15th century; Ḥunayn's 9th-century Arabic was made from Greek exemplars centuries older than anything behind Kühn's edition. Modern critical editors treat the Arabic tradition as testimony of equal — sometimes superior — standing. So do we.

1. **Enumerate the witnesses** for your work. The packet lists what's known; add what you find.
2. **Work from all accessible witnesses side by side.** The packet's base text is whichever tradition happens to be well edited and digitized — usually the Greek. That reflects only what is available in machine-readable form, and confers no priority among the witnesses.
3. **Compare every segment against every accessible witness** — not only where the base text looks wrong. Agreement is evidence too; record it.
4. **Reference what you consulted.** Every consultation goes in the segment's `refs` (and the reasoning in its `trace`), cited precisely enough to re-check: edition, page, or scan URL.
5. **Treat divergence as evidence.** When witnesses disagree, present the disagreement; if you follow the Arabic against the Greek — or vice versa — the trace argues why.

Two honest caveats. Access is asymmetric today: for most works the Greek is digitized while the Arabic sits in unedited manuscripts, so the Greek often ends up as the packet's base text by default — a practical limit to push against, imposed by the tooling rather than by any priority among the witnesses. And a translation-witness like Ḥunayn's carries its translator's interpretation — which is also its value: it preserves how a brilliant ninth-century reader, holding better manuscripts than ours, understood the sentence.

## Validation

`tools/validate.py` (stdlib-only, no network) checks works.json, the chunk registry, and every packet: required fields, status values, registry↔file consistency, and that `draft`/`reviewed` chunks have no untranslated segments. CI runs it on every push and PR.
