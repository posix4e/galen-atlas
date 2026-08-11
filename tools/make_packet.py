#!/usr/bin/env python3
"""Generate a versioned translation packet from pinned First1KGreek TEI."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys
import unicodedata
import urllib.request
import xml.etree.ElementTree as ET


ROOT = pathlib.Path(__file__).resolve().parent.parent
CACHE = ROOT / ".cache"
FIRST1K_COMMIT = "bfea9acd07ee1b7cea70cdd927c8f092d5637695"
TEI_URL = (
    "https://raw.githubusercontent.com/OpenGreekAndLatin/First1KGreek/"
    f"{FIRST1K_COMMIT}/data/tlg0057/{{work}}/tlg0057.{{work}}.1st1K-grc1.xml"
)
NS = "{http://www.tei-c.org/ns/1.0}"
SCAN_URL = "https://archive.org/details/b29339339_00{volume:02d}"
NETWORK_TIMEOUT = 30


def fetch_tei(work: str, cache_dir: pathlib.Path = CACHE) -> tuple[pathlib.Path, str]:
    """Fetch immutable upstream bytes and return the cache path and SHA-256."""
    cache_dir.mkdir(exist_ok=True)
    path = cache_dir / f"{work}-{FIRST1K_COMMIT[:12]}.xml"
    if not path.exists():
        url = TEI_URL.format(work=work)
        print(f"downloading {url}")
        with urllib.request.urlopen(url, timeout=NETWORK_TIMEOUT) as response:
            path.write_bytes(response.read())
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return path, digest


def extract_from_path(path: pathlib.Path, book: str, chapter: str) -> list[tuple[str, str]]:
    """Extract one chapter as ``(Kühn page, Greek text)`` segments."""
    root = ET.parse(path).getroot()
    book_div = next(
        (
            element
            for element in root.iter(NS + "div")
            if element.get("subtype") == "book" and element.get("n") == str(book)
        ),
        None,
    )
    if book_div is None:
        raise ValueError(f"book {book} not found")

    page = None
    volume = None
    segments: list[tuple[str, str]] = []
    buffer: list[str] = []
    inside = False

    def flush() -> None:
        text = re.sub(r"\s+", " ", "".join(buffer)).strip()
        if text:
            segments.append((page or "start", unicodedata.normalize("NFC", text)))
        buffer.clear()

    def walk(element: ET.Element) -> None:
        nonlocal page, volume, inside
        for child in element:
            tag = child.tag.replace(NS, "")
            is_chapter = tag == "div" and child.get("subtype") == "chapter"
            if tag == "pb":
                marker = child.get("n") or ""
                if "." in marker:
                    volume, page_number = marker.split(".", 1)
                else:
                    page_number = marker
                if inside:
                    flush()
                page = f"{volume}.{page_number}" if volume else page_number
            if is_chapter:
                if child.get("n") == str(chapter):
                    inside = True
                    if child.text:
                        buffer.append(child.text)
                    walk(child)
                    flush()
                    inside = False
                else:
                    walk(child)
            else:
                if inside and child.text:
                    buffer.append(child.text)
                walk(child)
            if inside and child.tail:
                buffer.append(child.tail)

    walk(book_div)
    return segments


def _page_key(value: str, default_volume: int | None) -> tuple[int, int]:
    parts = value.split(".")
    try:
        if len(parts) == 2:
            return int(parts[0]), int(parts[1])
        if len(parts) == 1 and default_volume is not None:
            return default_volume, int(parts[0])
    except ValueError as exc:
        raise ValueError(f"invalid page marker {value!r}") from exc
    raise ValueError(f"page marker {value!r} needs a volume")


def select_page_range(
    segments: list[tuple[str, str]], start_page: str | None, end_page: str | None
) -> list[tuple[str, str]]:
    pages = [page for page, _ in segments if page != "start"]
    default_volume = int(pages[0].split(".", 1)[0]) if pages and "." in pages[0] else None
    start = _page_key(start_page, default_volume) if start_page else None
    end = _page_key(end_page, default_volume) if end_page else None
    if start and end and start > end:
        raise ValueError("start page must not follow end page")
    selected = []
    for page, text in segments:
        if page == "start":
            if start is None:
                selected.append((page, text))
            continue
        key = _page_key(page, default_volume)
        if start is not None and key < start:
            continue
        if end is not None and key > end:
            continue
        selected.append((page, text))
    return selected


def build_packet(
    *,
    work: str,
    chunk_id: str,
    segments: list[tuple[str, str]],
    source_sha256: str,
    volume: int | None,
) -> dict:
    if not segments:
        raise ValueError("no text extracted for the requested range")
    pages = [page for page, _ in segments if page != "start"]
    kuhn_range = f"{pages[0]}–{pages[-1]}" if pages else "unknown"
    heading = re.match(r"\[([^]]+)]", segments[0][1])
    return {
        "schema_version": 2,
        "id": chunk_id,
        "work": work,
        "chapter_head": heading.group(1) if heading else None,
        "kuhn_range": kuhn_range,
        "status": "open",
        "contributors": {"translator": None, "reviewer": None},
        "source": {
            "text_url": TEI_URL.format(work=work),
            "upstream_commit": FIRST1K_COMMIT,
            "retrieved_on": dt.date.today().isoformat(),
            "sha256": source_sha256,
            "edition": "Kühn, Claudii Galeni Opera Omnia (1821–1833), via First1KGreek",
            "license": "CC BY-SA 4.0",
        },
        "witnesses": {
            "kuhn_latin": {
                "status": "unaligned",
                "note": "Compare Kühn's facing Latin for every segment.",
                "scan_url": SCAN_URL.format(volume=volume) if volume else None,
            },
            "arabic": {
                "status": "unknown",
                "note": "Identify and cite any relevant Arabic version before review. "
                        "Versions are indirect tradition: where one diverges, state which "
                        "underlying Greek reading would account for it, and whether you are "
                        "claiming a variant or a construal.",
            },
        },
        "segmentation": "one segment per Kühn page; split or merge at argument boundaries",
        "segments": [
            {"kuhn": page, "grc": text, "eng": "", "rationale": "", "refs": [], "notes": ""}
            for page, text in segments
        ],
    }


def ensure_writable(
    output: pathlib.Path, registry_entries: list[dict], chunk_id: str, force: bool
) -> None:
    registered = any(entry.get("id") == chunk_id for entry in registry_entries)
    if not force and (output.exists() or registered):
        raise FileExistsError(
            f"chunk {chunk_id!r} already exists; use --force only when replacement is intentional"
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--work", required=True)
    parser.add_argument("--book", required=True)
    parser.add_argument("--chapter", required=True)
    parser.add_argument("--id", required=True, help="chunk id, for example cml-1-3a")
    parser.add_argument("--volume", type=int, default=None, help="Kühn volume for the scan link")
    parser.add_argument("--start-page", help="first Kühn page, for example 12.427 or 427")
    parser.add_argument("--end-page", help="last Kühn page, inclusive")
    parser.add_argument("--force", action="store_true", help="replace an existing packet intentionally")
    args = parser.parse_args()

    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", args.id):
        parser.error("--id must contain lowercase letters, digits, and hyphens only")
    source_path, source_hash = fetch_tei(args.work)
    try:
        segments = extract_from_path(source_path, args.book, args.chapter)
        segments = select_page_range(segments, args.start_page, args.end_page)
        packet = build_packet(
            work=args.work,
            chunk_id=args.id,
            segments=segments,
            source_sha256=source_hash,
            volume=args.volume,
        )
    except ValueError as exc:
        parser.error(str(exc))

    registry_path = ROOT / "data" / "chunks.json"
    registry = json.loads(registry_path.read_text())
    if registry.get("schema_version") != 2 or not isinstance(registry.get("chunks"), list):
        raise SystemExit("data/chunks.json is not a schema-v2 registry")
    output = ROOT / "translations" / "chunks" / f"{args.id}.json"
    try:
        ensure_writable(output, registry["chunks"], args.id, args.force)
    except FileExistsError as exc:
        raise SystemExit(str(exc)) from exc

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(packet, ensure_ascii=False, indent=2) + "\n")
    registry["chunks"] = [entry for entry in registry["chunks"] if entry.get("id") != args.id]
    registry["chunks"].append(
        {
            "id": args.id,
            "work": args.work,
            "kuhn_range": packet["kuhn_range"],
            "status": "open",
            "file": f"translations/chunks/{args.id}.json",
        }
    )
    registry["chunks"].sort(key=lambda entry: entry["id"])
    registry["updated"] = dt.date.today().isoformat()
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {output.relative_to(ROOT)}: {len(segments)} segments, Kühn {packet['kuhn_range']}")


if __name__ == "__main__":
    main()
