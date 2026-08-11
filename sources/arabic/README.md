# Arabic witnesses to Galen

Thirty-five TEI files: the Galen-related Arabic in the [Digital Corpus for Graeco-Arabic Studies](https://www.graeco-arabic-studies.org/) (DCGAS), retrieved 9 August 2026. The set contains seventeen translations, sixteen summaries and epitomes, and two catalogues associated with Ḥunayn ibn Isḥāq. All are CC BY-SA 4.0, as stated in each TEI header; `manifest.json` records titles, source URLs, edition anchors, full source and local checksums, and any local structural repair.

## Why these matter here

Ḥunayn and his circle worked at Baghdad in the ninth century from Greek exemplars that can preserve readings older than surviving direct witnesses. In the language of textual criticism these versions are indirect tradition — evidence about the text rather than copies of it — but because their exemplars may antedate the surviving Greek, a versional reading can come from an independent branch of the stemma. Of any divergence, ask which underlying Greek reading would account for it, and whether it is a variant in the text or a construal of it. These files are held for comparison with the direct Greek and other traditions under the [witness protocol](../../HARNESS.md#the-witness-protocol).

## Alignment

The commentaries are the tractable case. `gal_inhippaphor-transl-ar1.xml` carries `<pb edRef="#edKuhn17b">` anchors — the same Kühn pagination as the Greek — together with `<quote type="lemma" n="…">` for each Hippocratic lemma, so Greek and Arabic collate mechanically, lemma by lemma. Treatises are coarser: they paginate to their own printed edition (`#edSalim`, `#edIskandar`, `#edLyons`) and mark Kühn only at chapter divisions.

## Where Arabic is the primary witness

Five of the translations have no Greek counterpart in the corpus, the Greek being lost:

| File | Work | English |
|---|---|---|
| `gal_denominibusmedicis` | *De nominibus medicis* | none — German only (Meyerhof & Schacht 1931) |
| `gal_departhomoeomdiff` | *De partium homoeomerium differentia* | unverified |
| `gal_deoptmedcogn` | *De optimo medico cognoscendo* | Iskandar, CMG Suppl. Or. IV |
| `gal_departartismed` | *De partibus artis medicativae* | Lyons, CMG Suppl. Or. II |
| `gal_decausiscontent` | *De causis contentivis* | Lyons, CMG Suppl. Or. II |

## Notes on the files

- `gal_inhippaphor-transl-ar1.xml` is the whole commentary on the *Aphorisms*; `_pt1` and `_pt2` are the same text divided. Count it once — about 1.1 M Arabic characters across the seventeen translations, not 1.6 M.
- Summaries are filed under their compiler (`anon_gal_…`, `ibnzurah_gal_…`, `ibnridwan_gal_…`, `hunayn_gal_…`), being epitomes of Galen rather than Galen. “Summary” does not by itself imply Alexandrian origin.
- `anon_gal_detemp-summ_jumal-ar1.xml` arrived upstream with an unclosed outer `div1`. Pergamap inserts only that closing tag so the local TEI is well-formed; the manifest preserves the upstream hash, local hash, and repair description.
- `hunayn_risalah-orig-ar1.xml` is the *Risāla*, Ḥunayn's account of the 129 Galenic works he and his circle rendered into Syriac and Arabic — the contemporary index to the whole translation movement, and a source for the atlas.

## Retrieval

DCGAS serves each text as a static file:

```
https://www.graeco-arabic-studies.org/fileadmin/user_upload/xml_files/{stem}.xml
```

with `{stem}` of the form `{author}_{work}-{orig|transl|summ_<type>}-{gr|ar}{n}`. The full inventory is enumerable from the `texts` page, where every version is linked. `manifest.json` holds the URL each file came from.

These are vendored rather than fetched on demand — unlike the Greek, which `tools/make_packet.py` pulls from First1KGreek into a gitignored cache. The asymmetry is deliberate: this is a curated subset assembled by hand, small enough to keep, and worth pinning against changes upstream.
