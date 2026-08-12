#!/usr/bin/env python3
"""Download and summarize the BBAW/CMG catalogue of Galen translations.

The website consumes a committed metadata index, never the remote HTML. To
respect BBAW's publication terms the index includes only record identifiers,
titles, Kühn references, and presence flags for language columns; bibliographic
strings remain on BBAW's authoritative page.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import sys
from html.parser import HTMLParser
from urllib.request import Request, urlopen


ROOT = pathlib.Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "data" / "bbaw-galen-translations.json"
SOURCE_URL = "https://cmg.bbaw.de/startseite/arbeitsmittel/werkverzeichnisse/galenus-uebersetzungen/"
USER_AGENT = "Pergamap BBAW catalogue sync/1.0 (+https://pergamap.com/)"
LANGUAGE_COLUMNS = {
    "de": "german",
    "en": "english",
    "fr": "french",
    "it": "italian",
    "es": "spanish",
    "we": "other",
}


def clean_text(value: str) -> str:
    return " ".join(value.split())


class CatalogueParser(HTMLParser):
    """Read BBAW's semantic cell IDs with no third-party parser dependency."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[dict[str, str]] = []
        self._row: list[dict[str, object]] | None = None
        self._cell: dict[str, object] | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        values = dict(attrs)
        if tag == "tr":
            self._row = []
        elif tag in {"td", "th"} and self._row is not None:
            self._cell = {"id": values.get("id"), "text": []}
            self._row.append(self._cell)
        elif tag == "br" and self._cell is not None:
            self._cell["text"].append(" ")

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell["text"].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"}:
            self._cell = None
        elif tag == "tr" and self._row is not None:
            row = {
                str(cell["id"]): clean_text("".join(cell["text"]))
                for cell in self._row
                if cell["id"]
            }
            self.rows.append(row)
            self._row = None


def parse_catalogue(source: bytes, retrieved_on: str) -> dict:
    parser = CatalogueParser()
    parser.feed(source.decode("utf-8"))
    parser.close()

    rows = [row for row in parser.rows if row.get("gtl3")]
    if len(rows) < 100:
        raise ValueError(f"expected at least 100 Galen catalogue rows, found {len(rows)}")

    records = []
    seen_ids: set[str] = set()
    for row in rows:
        record_id = row.get("fi", "")
        if not re.fullmatch(r"[0-9]{3}", record_id):
            raise ValueError(f"invalid or missing BBAW record id {record_id!r}")
        if record_id in seen_ids:
            raise ValueError(f"duplicate BBAW record id {record_id}")
        seen_ids.add(record_id)
        records.append(
            {
                "id": record_id,
                "title": row["gtl3"],
                "kuhn": row.get("gq", ""),
                "translation_columns": {
                    name: bool(row.get(column, ""))
                    for column, name in LANGUAGE_COLUMNS.items()
                },
            }
        )

    return {
        "schema_version": 1,
        "retrieved_on": retrieved_on,
        "source": {
            "publisher": "Berlin-Brandenburg Academy of Sciences and Humanities (BBAW)",
            "title": "Corpus Medicorum Graecorum: Galenus — Übersetzungen",
            "url": SOURCE_URL,
            "terms_url": "https://cmg.bbaw.de/startseite/impressum/",
            "sha256": hashlib.sha256(source).hexdigest(),
        },
        "language_columns": {
            "german": "German",
            "english": "English",
            "french": "French",
            "italian": "Italian",
            "spanish": "Spanish",
            "other": "Other languages",
        },
        "record_count": len(records),
        "records": records,
    }


def fetch(timeout: float) -> bytes:
    request = Request(
        SOURCE_URL,
        headers={"Accept": "text/html", "User-Agent": USER_AGENT},
    )
    with urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise RuntimeError(f"BBAW returned HTTP {response.status}")
        return response.read()


def serialized(document: dict) -> str:
    return json.dumps(document, ensure_ascii=False, indent=2) + "\n"


def preserve_retrieval_date(document: dict, current: dict | None) -> dict:
    """Keep identical source bytes from producing a date-only commit."""
    if (
        isinstance(current, dict)
        and current.get("source", {}).get("sha256") == document["source"]["sha256"]
        and current.get("retrieved_on")
    ):
        document["retrieved_on"] = current["retrieved_on"]
    return document


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=pathlib.Path, help="parse a local HTML fixture instead of downloading")
    parser.add_argument("--date", help="retrieval date for fixtures (defaults to today)")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--check", action="store_true", help="fail if the committed snapshot differs")
    args = parser.parse_args()

    retrieved_on = args.date or dt.date.today().isoformat()
    source = args.input.read_bytes() if args.input else fetch(args.timeout)
    current = None
    if OUTPUT.exists():
        try:
            current = json.loads(OUTPUT.read_text())
        except json.JSONDecodeError:
            pass
    document = preserve_retrieval_date(parse_catalogue(source, retrieved_on), current)
    output = serialized(document)
    if args.check:
        current = OUTPUT.read_text() if OUTPUT.exists() else ""
        if current != output:
            print(f"{OUTPUT.relative_to(ROOT)} is not current", file=sys.stderr)
            raise SystemExit(1)
        print(f"OK: {OUTPUT.relative_to(ROOT)} is current")
        return
    OUTPUT.write_text(output)
    print(f"Wrote {OUTPUT.relative_to(ROOT)} with {document['record_count']} BBAW records")


if __name__ == "__main__":
    main()
