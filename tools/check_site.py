#!/usr/bin/env python3
"""Offline checks for Pergamap HTML links, metadata, and CSP compatibility."""

from __future__ import annotations

import json
import pathlib
import sys
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit


ROOT = pathlib.Path(__file__).resolve().parent.parent


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = []
        self.title = False
        self.description = False
        self.canonical = False
        self.icon = False
        self.og_title = False
        self.og_description = False
        self.inline_script = False
        self.inline_style = False
        self._script_without_src = False

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            self.ids.append(values["id"])
        if "style" in values:
            self.inline_style = True
        if tag in {"a", "link"} and values.get("href"):
            self.links.append(values["href"])
        if tag in {"script", "img"} and values.get("src"):
            self.links.append(values["src"])
        if tag == "title":
            self.title = True
        if tag == "meta" and values.get("name") == "description":
            self.description = True
        if tag == "meta" and values.get("property") == "og:title":
            self.og_title = True
        if tag == "meta" and values.get("property") == "og:description":
            self.og_description = True
        if tag == "link" and values.get("rel") == "canonical":
            self.canonical = True
        if tag == "link" and values.get("rel") == "icon":
            self.icon = True
        if tag == "style":
            self.inline_style = True
        if tag == "script" and not values.get("src"):
            self._script_without_src = True

    def handle_endtag(self, tag):
        if tag == "script" and self._script_without_src:
            self.inline_script = True
            self._script_without_src = False


def target_for(page: pathlib.Path, href: str) -> pathlib.Path | None:
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or href.startswith(("#", "mailto:")):
        return None
    path = unquote(parsed.path)
    if not path:
        return None
    if path.startswith("/"):
        target = ROOT / path.lstrip("/")
    else:
        target = page.parent / path
    if path.endswith("/"):
        target /= "index.html"
    return target.resolve()


def check() -> list[str]:
    errors = []
    pages = sorted(ROOT.rglob("*.html"))
    for page in pages:
        parser = PageParser()
        try:
            parser.feed(page.read_text())
            parser.close()
        except Exception as exc:
            errors.append(f"{page.relative_to(ROOT)}: invalid HTML input: {exc}")
            continue
        label = page.relative_to(ROOT)
        if len(parser.ids) != len(set(parser.ids)):
            errors.append(f"{label}: duplicate id attribute")
        if parser.inline_script:
            errors.append(f"{label}: inline script violates the site CSP")
        if parser.inline_style:
            errors.append(f"{label}: inline style violates the site CSP")
        for field in ("title", "description", "icon", "og_title", "og_description"):
            if not getattr(parser, field):
                errors.append(f"{label}: missing {field.replace('_', ' ')} metadata")
        if page.name != "404.html" and not parser.canonical:
            errors.append(f"{label}: missing canonical URL")
        for href in parser.links:
            target = target_for(page, href)
            if target is None:
                continue
            try:
                target.relative_to(ROOT)
            except ValueError:
                errors.append(f"{label}: internal link escapes repository: {href}")
                continue
            if not target.exists():
                errors.append(f"{label}: broken internal link: {href}")
    for script in sorted((ROOT / "assets" / "js").glob("*.js")):
        source = script.read_text()
        for unsafe in (".innerHTML", "insertAdjacentHTML", "document.write"):
            if unsafe in source:
                errors.append(f"{script.relative_to(ROOT)}: unsafe DOM API {unsafe}")
    try:
        metadata = json.loads((ROOT / "data" / "catalogue-metadata.json").read_text())
        if metadata.get("@type") != "Dataset" or metadata.get("version") != "2":
            errors.append("data/catalogue-metadata.json: invalid Dataset metadata")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"data/catalogue-metadata.json: cannot read: {exc}")
    transmission_page = (ROOT / "transmission.html").read_text()
    transmission_script = (ROOT / "assets" / "js" / "transmission.js").read_text()
    for required in ("stage-composition", "stage-tradition", "stage-arabic", "source-language route not yet encoded"):
        if required not in transmission_page:
            errors.append(f"transmission.html: missing transmission distinction {required!r}")
    for required in ("work identity", "Later Greek manuscript tradition", "source route not yet encoded"):
        if required not in transmission_script:
            errors.append(f"assets/js/transmission.js: missing transmission distinction {required!r}")
    if "Galenic work" in transmission_page:
        errors.append("transmission.html: ambiguous 'Galenic work' stage label has returned")
    return errors


def main() -> None:
    errors = check()
    if errors:
        print(f"FAIL: {len(errors)} site problem(s)")
        for error in errors:
            print(" -", error)
        raise SystemExit(1)
    print("OK: site links, metadata, and CSP compatibility validated")


if __name__ == "__main__":
    main()
