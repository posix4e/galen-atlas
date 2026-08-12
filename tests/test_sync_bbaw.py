import hashlib
import pathlib
import unittest

from tools import sync_bbaw


class BbawSyncTests(unittest.TestCase):
    def setUp(self):
        self.fixture = pathlib.Path(__file__).parent / "fixtures" / "bbaw-catalogue.html"

    def make_large_fixture(self):
        rows = []
        for number in range(1, 101):
            english = "Singer (1997) (en)" if number == 1 else ""
            rows.append(
                f'<tr><td id="gtl3">Work {number}</td><td id="gq">I, {number} K.</td>'
                f'<td id="de"></td><td id="en">{english}</td><td id="fr"></td>'
                '<td id="it"></td><td id="es"></td><td id="we"></td>'
                f'<td id="fi">{number:03d}</td></tr>'
            )
        return ("<html><body><table>" + "".join(rows) + "</table></body></html>").encode()

    def test_parser_normalizes_translation_columns(self):
        source = self.make_large_fixture()
        document = sync_bbaw.parse_catalogue(source, "2026-08-12")
        self.assertEqual(document["record_count"], 100)
        self.assertTrue(document["records"][0]["translation_columns"]["english"])
        self.assertFalse(document["records"][1]["translation_columns"]["english"])
        self.assertEqual(document["source"]["sha256"], hashlib.sha256(source).hexdigest())

    def test_short_or_duplicate_catalogue_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "at least 100"):
            sync_bbaw.parse_catalogue(self.fixture.read_bytes(), "2026-08-12")

        source = self.make_large_fixture().replace(b">100</td></tr>", b">099</td></tr>")
        with self.assertRaisesRegex(ValueError, "duplicate BBAW record id"):
            sync_bbaw.parse_catalogue(source, "2026-08-12")

    def test_live_shape_fixture_fields_are_preserved(self):
        parser = sync_bbaw.CatalogueParser()
        parser.feed(self.fixture.read_text())
        records = [row for row in parser.rows if row.get("gtl3")]
        self.assertEqual(records[0]["gtl3"], "De antidotis")
        self.assertEqual(records[0]["en"], "")
        self.assertEqual(records[0]["de"], "Winkler (1980) (de)")
        self.assertEqual(records[1]["es"], "Alfageme (2003) (es)")

    def test_source_checksum_is_full_sha256(self):
        source = self.fixture.read_bytes()
        self.assertEqual(len(hashlib.sha256(source).hexdigest()), 64)

    def test_unchanged_source_preserves_retrieval_date(self):
        current = {"retrieved_on": "2026-08-12", "source": {"sha256": "a" * 64}}
        update = {"retrieved_on": "2026-08-19", "source": {"sha256": "a" * 64}}
        self.assertEqual(sync_bbaw.preserve_retrieval_date(update, current)["retrieved_on"], "2026-08-12")

    def test_changed_source_uses_new_retrieval_date(self):
        current = {"retrieved_on": "2026-08-12", "source": {"sha256": "a" * 64}}
        update = {"retrieved_on": "2026-08-19", "source": {"sha256": "b" * 64}}
        self.assertEqual(sync_bbaw.preserve_retrieval_date(update, current)["retrieved_on"], "2026-08-19")


if __name__ == "__main__":
    unittest.main()
