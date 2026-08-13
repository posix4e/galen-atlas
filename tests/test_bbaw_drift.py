import json
import pathlib
import tempfile
import unittest

from tools import check_bbaw_drift


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value) + "\n")


class BbawDriftTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name)
        self.work = {
            "id": "tlg001",
            "titles": {"latin": "Opus", "english": "Work"},
            "english": {"status": "none"},
        }
        self.record = {
            "id": "001",
            "translation_columns": {"english": False},
        }
        self.mapping = {
            "work_id": "tlg001",
            "bbaw_record_ids": ["001"],
            "relation": "same-work",
        }
        self.save()

    def tearDown(self):
        self.temp.cleanup()

    def save(self):
        write_json(self.root / "data/works.json", {"works": [self.work]})
        write_json(self.root / "data/bbaw-galen-translations.json", {"records": [self.record]})
        write_json(self.root / "data/bbaw-crosswalk.json", {"mappings": [self.mapping]})

    def test_agreement_passes(self):
        self.assertEqual(check_bbaw_drift.check(self.root), ([], []))

    def test_unreviewed_disagreement_fails(self):
        self.record["translation_columns"]["english"] = True
        self.save()
        errors, notices = check_bbaw_drift.check(self.root)
        self.assertEqual(notices, [])
        self.assertTrue(any("add an english_status_review" in error for error in errors))

    def test_documented_disagreement_is_reported(self):
        self.record["translation_columns"]["english"] = True
        self.mapping["english_status_review"] = {
            "status": "needs-source-check",
            "note": "The catalogues disagree.",
        }
        self.save()
        errors, notices = check_bbaw_drift.check(self.root)
        self.assertEqual(errors, [])
        self.assertTrue(any("needs-source-check" in notice for notice in notices))

    def test_stale_review_fails(self):
        self.mapping["english_status_review"] = {
            "status": "explained",
            "note": "Former disagreement.",
        }
        self.save()
        errors, _ = check_bbaw_drift.check(self.root)
        self.assertTrue(any("review is stale" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
