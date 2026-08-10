import hashlib
import json
import pathlib
import tempfile
import unittest

from tools import validate


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name)
        (self.root / "translations" / "chunks").mkdir(parents=True)
        (self.root / "sources" / "arabic").mkdir(parents=True)
        self.works = {
            "schema_version": 2,
            "updated": "2026-08-09",
            "status": "preliminary",
            "sources": [
                {
                    "id": "catalogue",
                    "title": "Catalogue",
                    "url": "https://example.test/catalogue",
                    "accessed": "2026-08-09",
                }
            ],
            "works": [
                {
                    "id": "tlg001",
                    "urn": "urn:cts:greekLit:tlg0057.tlg001",
                    "titles": {"latin": "Opus", "english": "Work"},
                    "kuhn": "I",
                    "survival": {"languages": ["greek"], "extent": "unspecified"},
                    "digital_texts": [
                        {"language": "greek", "provider": "Example", "url": "https://example.test/text"}
                    ],
                    "english": {
                        "status": "partial",
                        "citations": [
                            {"label": "A translation", "url": "https://example.test/translation", "scope": "partial"}
                        ],
                        "verification": {
                            "status": "checked",
                            "checked_on": "2026-08-09",
                            "source_ids": ["catalogue"],
                        },
                    },
                    "notes": None,
                }
            ],
        }
        self.registry = {
            "schema_version": 2,
            "updated": "2026-08-09",
            "chunks": [
                {
                    "id": "sample-1",
                    "work": "tlg001",
                    "kuhn_range": "1.1–1.2",
                    "status": "draft",
                    "file": "translations/chunks/sample-1.json",
                }
            ],
        }
        self.packet = {
            "schema_version": 2,
            "id": "sample-1",
            "work": "tlg001",
            "kuhn_range": "1.1–1.2",
            "status": "draft",
            "contributors": {"translator": {"name": "Translator"}, "reviewer": None},
            "source": {
                "text_url": "https://example.test/source.xml",
                "upstream_commit": "a" * 40,
                "retrieved_on": "2026-08-09",
                "sha256": "b" * 64,
                "edition": "Edition",
                "license": "CC BY-SA 4.0",
            },
            "segments": [
                {
                    "kuhn": "1.1",
                    "grc": "λόγος",
                    "eng": "account",
                    "rationale": "Context supports this rendering.",
                    "refs": ["Edition, p. 1"],
                    "notes": "",
                }
            ],
        }
        self.xml_path = self.root / "sources" / "arabic" / "sample.xml"
        self.xml_path.write_text("<TEI><text>نص</text></TEI>\n")
        digest = hashlib.sha256(self.xml_path.read_bytes()).hexdigest()
        self.manifest = {
            "schema_version": 2,
            "description": "Fixture",
            "source": {
                "id": "dcgas",
                "title": "DCGAS",
                "url": "https://example.test/",
                "license": "CC BY-SA 4.0",
                "retrieved_on": "2026-08-09",
                "url_pattern": "https://example.test/{stem}.xml",
            },
            "counts": {"translation": 1, "summary": 0, "catalogue": 0},
            "duplicates": [],
            "texts": [
                {
                    "file": "sample.xml",
                    "kind": "translation",
                    "author": "Galen",
                    "title_latin": "Opus",
                    "title_arabic": None,
                    "of_work": "Opus",
                    "work_ids": ["tlg001"],
                    "arabic_characters": 3,
                    "edition_ids": [],
                    "source_url": "https://example.test/sample.xml",
                    "source_sha256": digest,
                    "local_sha256": digest,
                    "local_changes": [],
                }
            ],
        }
        self.transmission = {
            "schema_version": 1,
            "updated": "2026-08-10",
            "status": "curated",
            "methodology": {
                "scope": "Fixture scope",
                "direct_relation": "Fixture direct relation",
                "influence_relation": "Fixture influence relation",
                "work_identity": "Fixture work identity distinction",
                "surviving_tradition": "Fixture surviving tradition distinction",
                "translation_route": "Fixture translation-route distinction",
            },
            "sources": [
                {
                    "id": "transmission-source",
                    "title": "Transmission source",
                    "publisher": "Example",
                    "url": "https://example.test/transmission",
                    "accessed": "2026-08-10",
                }
            ],
            "upstream": [],
            "receptions": [
                {
                    "id": "later-version",
                    "title": "Later version",
                    "date": "12th century",
                    "language": "latin",
                    "kind": "translation",
                    "relation": "translation-from-arabic",
                    "certainty": "documented",
                    "work_ids": ["tlg001"],
                    "witness_files": ["sample.xml"],
                    "description": "A source-backed fixture route.",
                    "url": "https://example.test/later",
                    "source_ids": ["transmission-source"],
                }
            ],
            "context": [],
        }
        self.save()

    def tearDown(self):
        self.temp.cleanup()

    def save(self):
        write_json(self.root / "data" / "works.json", self.works)
        write_json(self.root / "data" / "chunks.json", self.registry)
        write_json(self.root / "translations" / "chunks" / "sample-1.json", self.packet)
        write_json(self.root / "sources" / "arabic" / "manifest.json", self.manifest)
        write_json(self.root / "data" / "transmission.json", self.transmission)

    def assert_error_contains(self, phrase):
        errors = validate.validate(self.root)
        self.assertTrue(any(phrase in error for error in errors), errors)

    def test_valid_fixture(self):
        self.assertEqual(validate.validate(self.root), [])

    def test_duplicate_work_id(self):
        self.works["works"].append(dict(self.works["works"][0]))
        self.save()
        self.assert_error_contains("duplicate work id")

    def test_missing_packet_file(self):
        self.registry["chunks"][0]["file"] = "translations/chunks/missing.json"
        self.save()
        self.assert_error_contains("file is missing")

    def test_unsafe_url(self):
        self.works["works"][0]["digital_texts"][0]["url"] = "javascript:alert(1)"
        self.save()
        self.assert_error_contains("unsafe or invalid URL")

    def test_registry_packet_drift(self):
        self.packet["status"] = "reviewed"
        self.packet["contributors"]["reviewer"] = {"name": "Reviewer"}
        self.save()
        self.assert_error_contains("registry/packet status mismatch")

    def test_missing_translator(self):
        self.packet["contributors"]["translator"] = None
        self.save()
        self.assert_error_contains("requires translator attribution")

    def test_incomplete_reviewed_packet(self):
        self.registry["chunks"][0]["status"] = "reviewed"
        self.packet["status"] = "reviewed"
        self.packet["contributors"]["reviewer"] = {"name": "Reviewer"}
        self.packet["segments"][0]["eng"] = ""
        self.packet["segments"][0]["rationale"] = ""
        self.packet["segments"][0]["refs"] = []
        self.save()
        errors = validate.validate(self.root)
        self.assertTrue(any("empty English segment" in error for error in errors), errors)
        self.assertTrue(any("requires rationale" in error for error in errors), errors)
        self.assertTrue(any("requires citations" in error for error in errors), errors)

    def test_checksum_mismatch(self):
        self.manifest["texts"][0]["local_sha256"] = "0" * 64
        self.save()
        self.assert_error_contains("local checksum mismatch")

    def test_malformed_xml(self):
        self.xml_path.write_text("<TEI><text></TEI>\n")
        digest = hashlib.sha256(self.xml_path.read_bytes()).hexdigest()
        self.manifest["texts"][0]["source_sha256"] = digest
        self.manifest["texts"][0]["local_sha256"] = digest
        self.save()
        self.assert_error_contains("XML is not well-formed")

    def test_transmission_unknown_work(self):
        self.transmission["receptions"][0]["work_ids"] = ["missing-work"]
        self.save()
        self.assert_error_contains("work_ids contains an unknown work")

    def test_transmission_unknown_witness(self):
        self.transmission["receptions"][0]["witness_files"] = ["missing.xml"]
        self.save()
        self.assert_error_contains("witness_files contains an unknown Arabic file")

    def test_transmission_requires_route_methodology(self):
        self.transmission["methodology"]["translation_route"] = ""
        self.save()
        self.assert_error_contains("methodology is incomplete")

    def test_repository_data_is_valid(self):
        self.assertEqual(validate.validate(validate.ROOT), [])


if __name__ == "__main__":
    unittest.main()
