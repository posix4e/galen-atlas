#!/usr/bin/env python3
"""Report English-status disagreements between Pergamap and its BBAW crosswalk."""

from __future__ import annotations

import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parent.parent


def check(root: pathlib.Path = ROOT) -> tuple[list[str], list[str]]:
    works = {work["id"]: work for work in json.loads((root / "data/works.json").read_text())["works"]}
    records = {
        record["id"]: record
        for record in json.loads((root / "data/bbaw-galen-translations.json").read_text())["records"]
    }
    mappings = json.loads((root / "data/bbaw-crosswalk.json").read_text())["mappings"]
    errors: list[str] = []
    notices: list[str] = []
    for mapping in mappings:
        refs = mapping["bbaw_record_ids"]
        if not refs:
            continue
        work = works[mapping["work_id"]]
        bbaw_has_english = any(records[ref]["translation_columns"]["english"] for ref in refs)
        pergamap_has_english = work["english"]["status"] in {"full", "partial"}
        disagrees = bbaw_has_english != pergamap_has_english
        review = mapping.get("english_status_review")
        if disagrees and not review:
            errors.append(
                f"{mapping['work_id']}: Pergamap is {work['english']['status']!r}, "
                f"but BBAW English is {'listed' if bbaw_has_english else 'empty'}; "
                "add an english_status_review"
            )
        elif disagrees:
            notices.append(
                f"{mapping['work_id']}: {review['status']} — {review['note']}"
            )
        elif review:
            errors.append(
                f"{mapping['work_id']}: english_status_review is stale because the catalogues now agree"
            )
    return errors, notices


def main() -> None:
    errors, notices = check()
    for notice in notices:
        print("REVIEW:", notice)
    if errors:
        print(f"FAIL: {len(errors)} unreviewed BBAW drift problem(s)")
        for error in errors:
            print(" -", error)
        raise SystemExit(1)
    print(f"OK: BBAW drift checked; {len(notices)} documented disagreement(s)")


if __name__ == "__main__":
    main()
