#!/usr/bin/env python3
"""Validate works.json, the chunk registry, and every chunk packet.

Stdlib only, no network — safe for CI. Exit code 1 on any failure.
"""
import json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
errors = []


def err(msg):
    errors.append(msg)


def main():
    works = json.loads((ROOT / 'data' / 'works.json').read_text())
    ids = set()
    for w in works:
        wid = w.get('id', '<missing id>')
        ids.add(wid)
        for field in ('title_lat', 'survival', 'english', 'confidence'):
            if not w.get(field):
                err(f'works.json {wid}: missing {field}')
        if w.get('english') not in ('none', 'full', 'partial', 'unknown'):
            err(f'works.json {wid}: bad english value {w.get("english")!r}')
        if w.get('survival') not in ('greek', 'arabic', 'latin', 'fragments'):
            err(f'works.json {wid}: bad survival value {w.get("survival")!r}')
        if w.get('confidence') not in ('checked', 'recalled', 'unknown'):
            err(f'works.json {wid}: bad confidence value {w.get("confidence")!r}')
    if len(ids) != len(works):
        err('works.json: duplicate ids')

    regp = ROOT / 'data' / 'chunks.json'
    reg = json.loads(regp.read_text()) if regp.exists() else []
    reg_files = set()
    for e in reg:
        f = ROOT / e.get('file', '')
        reg_files.add(f.resolve())
        if not f.exists():
            err(f'chunks.json {e.get("id")}: file {e.get("file")} does not exist')
        if e.get('status') not in ('open', 'claimed', 'draft', 'reviewed'):
            err(f'chunks.json {e.get("id")}: bad status {e.get("status")!r}')
        if e.get('work') not in ids:
            err(f'chunks.json {e.get("id")}: work {e.get("work")!r} not in works.json')

    chunk_dir = ROOT / 'translations' / 'chunks'
    for path in sorted(chunk_dir.glob('*.json')) if chunk_dir.exists() else []:
        if path.resolve() not in reg_files:
            err(f'{path.name}: chunk file has no registry entry in data/chunks.json')
        c = json.loads(path.read_text())
        cid = c.get('id', path.stem)
        if c.get('id') != path.stem:
            err(f'{path.name}: id {cid!r} does not match filename')
        if c.get('status') not in ('open', 'claimed', 'draft', 'reviewed'):
            err(f'{path.name}: bad status {c.get("status")!r}')
        if c.get('work') not in ids:
            err(f'{path.name}: work {c.get("work")!r} not in works.json')
        segs = c.get('segments', [])
        if not segs:
            err(f'{path.name}: no segments')
        for i, s in enumerate(segs):
            for field in ('kuhn', 'grc', 'eng', 'trace', 'refs', 'notes'):
                if field not in s:
                    err(f'{path.name} segment {i}: missing field {field!r}')
            if not isinstance(s.get('refs', []), list):
                err(f'{path.name} segment {i}: refs must be a list of citations')
            if not s.get('grc', '').strip():
                err(f'{path.name} segment {i}: empty Greek')
        if c.get('status') in ('draft', 'reviewed'):
            untranslated = sum(1 for s in segs if not s.get('eng', '').strip())
            if untranslated:
                err(f'{path.name}: status {c["status"]} but {untranslated} segments untranslated')

    if errors:
        print(f'FAIL: {len(errors)} problem(s)')
        for e in errors:
            print(' -', e)
        sys.exit(1)
    print(f'OK: {len(works)} works, {len(reg)} chunks validated')


if __name__ == '__main__':
    main()
