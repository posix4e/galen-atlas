import pathlib
import tempfile
import unittest
from unittest import mock

from tools import make_packet


TEI = """<?xml version="1.0" encoding="UTF-8"?>
<TEI xmlns="http://www.tei-c.org/ns/1.0">
  <text><body>
    <div subtype="book" n="1">
      <div subtype="chapter" n="2">
        <pb n="12.381"/><p>[Heading] πρῶτον</p>
        <pb n="382"/><p>δεύτερον</p>
        <pb n="383"/><p>τρίτον</p>
      </div>
    </div>
  </body></text>
</TEI>
"""


class PacketGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name)
        self.tei = self.root / "fixture.xml"
        self.tei.write_text(TEI)

    def tearDown(self):
        self.temp.cleanup()

    def test_extract_and_page_range(self):
        segments = make_packet.extract_from_path(self.tei, "1", "2")
        self.assertEqual([page for page, _ in segments], ["12.381", "12.382", "12.383"])
        selected = make_packet.select_page_range(segments, "382", "12.383")
        self.assertEqual([page for page, _ in selected], ["12.382", "12.383"])

    def test_reversed_page_range_fails(self):
        segments = make_packet.extract_from_path(self.tei, "1", "2")
        with self.assertRaisesRegex(ValueError, "start page"):
            make_packet.select_page_range(segments, "383", "382")

    def test_packet_records_pinned_provenance(self):
        segments = make_packet.extract_from_path(self.tei, "1", "2")[:1]
        packet = make_packet.build_packet(
            work="tlg076",
            chunk_id="sample-1",
            segments=segments,
            source_sha256="a" * 64,
            volume=12,
        )
        self.assertEqual(packet["schema_version"], 2)
        self.assertEqual(packet["source"]["upstream_commit"], make_packet.FIRST1K_COMMIT)
        self.assertIn(make_packet.FIRST1K_COMMIT, packet["source"]["text_url"])
        self.assertEqual(packet["source"]["sha256"], "a" * 64)
        self.assertEqual(packet["segments"][0]["rationale"], "")

    def test_fetch_uses_timeout(self):
        with mock.patch("tools.make_packet.urllib.request.urlopen", side_effect=TimeoutError) as urlopen:
            with self.assertRaises(TimeoutError):
                make_packet.fetch_tei("tlg076", self.root / "cache")
        urlopen.assert_called_once_with(
            make_packet.TEI_URL.format(work="tlg076"), timeout=make_packet.NETWORK_TIMEOUT
        )

    def test_overwrite_requires_force(self):
        output = self.root / "sample.json"
        output.write_text("{}")
        with self.assertRaisesRegex(FileExistsError, "--force"):
            make_packet.ensure_writable(output, [], "sample-1", False)
        make_packet.ensure_writable(output, [], "sample-1", True)

    def test_registered_id_requires_force(self):
        output = self.root / "sample.json"
        with self.assertRaises(FileExistsError):
            make_packet.ensure_writable(output, [{"id": "sample-1"}], "sample-1", False)


if __name__ == "__main__":
    unittest.main()
