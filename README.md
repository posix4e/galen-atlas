# Pergamap

**Most of Galen has never been translated into English.** Galen of Pergamon (129 – c. 216 CE) is the largest surviving author of antiquity — roughly three million words. This project is:

1. **An atlas** — [`data/works.json`](data/works.json) tracks the corpus: the language each work survives in (Greek / Arabic / Latin / fragments), where the text is digitized, whether an English translation exists, and how confident we are in that status. Coverage today: the 97 works digitized by First1KGreek plus 11 added by hand; roughly two dozen more surviving works still need entries.
2. **A roadmap** — a phased plan for translating the untranslated, with targets picked by public vote.
3. **A working translation** — published chunk by chunk with the source text alongside, starting with Book 1 of *On the Composition of Drugs According to Places* (baldness cures, hair dyes, dandruff, lice — Kühn XII 378 ff.), which has waited ~1,800 years for English.

Live site: https://pergamap.com/

## Data honesty

Every entry in `works.json` carries a `confidence` field:

- `checked` — verified against sources during this project
- `recalled` — from general scholarship, **needs a citation check**
- `unknown` — nobody has checked yet; a great first contribution

The translation-status data is a living draft. If you find an error, [open an issue](../../issues) with your source — that's the project working as intended.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md): verify a catalog entry, vote on the first campaign, or claim a translation chunk.

## Sources & licenses

- Greek texts: [First1KGreek](https://github.com/OpenGreekAndLatin/First1KGreek) / [Digital Corpus for Graeco-Arabic Studies](https://www.graeco-arabic-studies.org/) (CC BY-SA), digitized from Kühn, *Claudii Galeni Opera Omnia* (1821–33, public domain; [scans](https://archive.org/details/b29339339_0012) via Wellcome Library).
- Site content and translations: CC BY-SA 4.0.
