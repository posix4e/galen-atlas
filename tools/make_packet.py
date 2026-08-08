#!/usr/bin/env python3
"""Generate a translation packet: everything a translator needs for one chunk.

Usage:
  python3 tools/make_packet.py --work tlg076 --book 1 --chapter 2 --id cml-1-2

Downloads the work's TEI XML from First1KGreek (cached in .cache/), extracts the
chapter's Greek with Kühn page anchors, and writes:
  - translations/chunks/<id>.json   (the packet: segments awaiting translation)
  - data/chunks.json                (registry entry, status "open")

Segmentation is one segment per Kühn page. This is PROVISIONAL — translators
should split or merge segments to follow the argument, not the page turns.
"""
import argparse, json, pathlib, re, sys, unicodedata, urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / '.cache'
TEI_URL = ('https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/'
           'master/data/tlg0057/{w}/tlg0057.{w}.1st1K-grc1.xml')
NS = '{http://www.tei-c.org/ns/1.0}'
# Wellcome Library scans of Kühn on archive.org. Identifier pattern verified
# against vol XII only — confirm the title page before trusting other volumes.
SCAN_URL = 'https://archive.org/details/b29339339_00{vol:02d}'


def fetch_tei(work):
    CACHE.mkdir(exist_ok=True)
    path = CACHE / f'{work}.xml'
    if not path.exists():
        url = TEI_URL.format(w=work)
        print(f'downloading {url}')
        with urllib.request.urlopen(url) as r:
            raw = r.read().decode('utf-8')
        # First1KGreek files are NFD; normalize so searches and diffs behave.
        path.write_text(unicodedata.normalize('NFC', raw))
    return path


def extract(work, book, chapter):
    """Return (segments, pages) for one chapter: [(kuhn_page, text), ...]."""
    root = ET.parse(fetch_tei(work)).getroot()
    bdiv = next((d for d in root.iter(NS + 'div')
                 if d.get('subtype') == 'book' and d.get('n') == str(book)), None)
    if bdiv is None:
        sys.exit(f'book {book} not found in {work}')

    page, vol = None, None
    segs, buf, inside = [], [], False

    def flush():
        text = re.sub(r'\s+', ' ', ''.join(buf)).strip()
        if text:
            segs.append((page or 'start', text))
        buf.clear()

    def walk(el, chap_depth=False):
        nonlocal page, vol, inside
        for child in el:
            tag = child.tag.replace(NS, '')
            is_chap = tag == 'div' and child.get('subtype') == 'chapter'
            if tag == 'pb':
                n = child.get('n') or ''
                if '.' in n:
                    vol, p = n.split('.', 1)
                else:
                    p = n  # bare page number: volume carries over (e.g. pb n="497")
                if inside:
                    flush()
                page = f'{vol}.{p}' if vol else p
            if is_chap:
                if child.get('n') == str(chapter):
                    inside = True
                    if child.text:
                        buf.append(child.text)
                    walk(child)
                    flush()
                    inside = False
                else:
                    walk(child)  # still track pages through other chapters
            else:
                if inside and child.text:
                    buf.append(child.text)
                walk(child)
            if inside and child.tail:
                buf.append(child.tail)

    if bdiv.text:
        pass
    walk(bdiv)
    return segs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--work', required=True)
    ap.add_argument('--book', required=True)
    ap.add_argument('--chapter', required=True)
    ap.add_argument('--id', required=True, help='chunk id, e.g. cml-1-2')
    ap.add_argument('--volume', type=int, default=None,
                    help='Kühn volume number for the scan link (e.g. 12)')
    args = ap.parse_args()

    segs = extract(args.work, args.book, args.chapter)
    if not segs:
        sys.exit('no text extracted — check book/chapter numbers')

    pages = [p for p, _ in segs if p != 'start']
    kuhn_range = f'{pages[0]}–{pages[-1]}' if pages else 'unknown'
    head = re.match(r'\[([^\]]+)\]', segs[0][1])

    packet = {
        'id': args.id,
        'work': args.work,
        'chapter_head': head.group(1) if head else None,
        'kuhn_range': kuhn_range,
        'status': 'open',
        'translator': None,
        'reviewer': None,
        'source': {
            'tei': TEI_URL.format(w=args.work),
            'edition': 'Kühn, Claudii Galeni Opera Omnia (1821–33), via First1KGreek',
            'license': 'CC BY-SA',
        },
        # Witnesses are PEERS: surviving traditions testify to a lost original.
        # The Greek is this packet's base text because it is digitized, not
        # because it outranks the others. See HARNESS.md, peer-witness protocol.
        'witnesses': {
            'kuhn_latin': {
                'status': 'unaligned',
                'note': 'Kühn prints a facing Latin translation — compare it '
                        'at these page numbers for every segment.',
                'scan_url': SCAN_URL.format(vol=args.volume) if args.volume else None,
            },
            'arabic': {
                'status': 'unknown',
                'note': 'If a Ḥunayn-school Arabic version of this work survives, '
                        'it is a peer witness made from Greek exemplars older than '
                        'Kühn’s. Check editions/manuscripts and record what you find. '
                        'Start: https://www.graeco-arabic-studies.org/texts',
            },
        },
        'segmentation': 'one segment per Kühn page — provisional; split or merge freely',
        # trace = the translator's working, LLM-style: alternatives weighed, why a
        # rendering won, how witnesses compared. refs = citations for every witness
        # consulted (edition, page, or scan URL). Both are published with the text.
        'segments': [{'kuhn': p, 'grc': t, 'eng': '', 'trace': '', 'refs': [],
                      'notes': ''} for p, t in segs],
    }

    out = ROOT / 'translations' / 'chunks' / f'{args.id}.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(packet, ensure_ascii=False, indent=1))

    regp = ROOT / 'data' / 'chunks.json'
    reg = json.loads(regp.read_text()) if regp.exists() else []
    reg = [e for e in reg if e['id'] != args.id]
    reg.append({'id': args.id, 'work': args.work, 'kuhn_range': kuhn_range,
                'status': 'open', 'file': f'translations/chunks/{args.id}.json'})
    reg.sort(key=lambda e: e['id'])
    regp.write_text(json.dumps(reg, ensure_ascii=False, indent=1))

    print(f'wrote {out.relative_to(ROOT)}: {len(segs)} segments, Kühn {kuhn_range}')


if __name__ == '__main__':
    main()
