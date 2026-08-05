"""Testy adapterow chandra (bogaty) + gaius (OCR PATRONa, tekstowy)."""
import json
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

import contract as C  # noqa: E402
from adapters import chandra as chd  # noqa: E402
from adapters import gaius as gai  # noqa: E402

_FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def _load(name):
    with open(os.path.join(_FIX, name), "rb") as fh:
        return fh.read()


class TestChandra(unittest.TestCase):
    def setUp(self):
        self.raw = _load("chandra.sample.json")
        self.data = json.loads(self.raw.decode("utf-8"))
        self.blocks = chd.to_blocks(self.data)

    def test_block_count_and_pages(self):
        self.assertEqual(len(self.blocks), 4)
        self.assertEqual(chd.page_count(self.data), 2)

    def test_type_mapping(self):
        self.assertEqual(self.blocks[0].block_type, "title")   # section-header
        self.assertEqual(self.blocks[2].block_type, "table")

    def test_confidence_is_min_of_lines(self):
        # blok 2: linie 0.96 i 0.55 -> min 0.55 (konserwatywnie)
        self.assertEqual(self.blocks[1].confidence, 0.55)

    def test_bbox_already_normalized_kept(self):
        for v in self.blocks[0].bbox:
            self.assertLessEqual(v, 1.0)

    def test_bbox_pixels_normalized_by_page_dims(self):
        # strona 2: bbox pikselowy [80,60,920,220] / 1000x1400
        b = self.blocks[3]
        self.assertAlmostEqual(b.bbox[0], 0.08, places=3)
        self.assertAlmostEqual(b.bbox[2], 0.92, places=3)

    def test_gating_routes_low_conf(self):
        contract = C.build_contract(self.blocks, engine="chandra", raw=self.raw, threshold=0.85)
        g = contract["gating"]
        self.assertIn("b0002", g["review_required"])  # 0.55
        self.assertIn("b0003", g["review_required"])  # 0.71
        self.assertIn("b0001", g["auto_approved"])     # 0.99
        self.assertEqual(C.validate(contract), [])


class TestChandra2RealFormat(unittest.TestCase):
    """Realny format Chandry 2: plaska lista {bbox,label,content-HTML}, bez conf."""

    def setUp(self):
        self.raw = _load("chandra2.sample.json")
        self.data = json.loads(self.raw.decode("utf-8"))
        self.blocks = chd.to_blocks(self.data)

    def test_flat_list_is_single_page(self):
        self.assertEqual(len(self.blocks), 5)
        self.assertEqual(chd.page_count(self.data), 1)
        for b in self.blocks:
            self.assertEqual(b.page, 1)

    def test_label_mapping_chandra2(self):
        types = [b.block_type for b in self.blocks]
        self.assertEqual(types, ["title", "paragraph", "table", "footer", "unknown"])

    def test_html_stripped_and_entities_unescaped(self):
        self.assertIn("oddalił wniosek", self.blocks[1].text)
        self.assertNotIn("<", self.blocks[1].text)
        self.assertIn("Oplata", self.blocks[2].text)

    def test_no_confidence_all_partial_to_review(self):
        for b in self.blocks:
            self.assertIsNone(b.confidence)
            self.assertIn("partial", b.flags)
        contract = C.build_contract(self.blocks, engine="chandra", raw=self.raw)
        self.assertEqual(contract["gating"]["auto_approved"], [])
        self.assertEqual(C.validate(contract), [])

    def test_pixel_bbox_without_page_dims_is_none(self):
        self.assertIsNone(self.blocks[0].bbox)

    def test_wrapped_pages_normalize_bbox(self):
        wrapped = {"pages": [{"page": 3, "width": 1240, "height": 1754,
                              "blocks": self.data[:2]}]}
        blocks = chd.to_blocks(wrapped)
        self.assertEqual(blocks[0].page, 3)
        self.assertAlmostEqual(blocks[0].bbox[0], 112 / 1240, places=4)
        self.assertNotIn(None, blocks[0].bbox)

    def test_guard_nonempty_input_zero_blocks_raises(self):
        # dawna cicha sciezka: nierozpoznany format -> 0 blokow -> exit 0
        with self.assertRaises(ValueError):
            chd.to_blocks({"chunks": [{"foo": "bar"}]})


class TestGaius(unittest.TestCase):
    def setUp(self):
        self.raw = _load("gaius.sample.json")
        self.result = json.loads(self.raw.decode("utf-8"))
        self.blocks = gai.to_blocks(self.result)

    def test_partial_text_engine(self):
        for b in self.blocks:
            self.assertIsNone(b.bbox)
            self.assertIsNone(b.confidence)
            self.assertIn("partial", b.flags)

    def test_variant_captured(self):
        self.assertEqual(gai.variant(self.result), "google_doc_ai")

    def test_contract_records_engine_variant(self):
        contract = C.build_contract(
            self.blocks, engine="gaius", raw=self.raw,
            engine_variant=gai.variant(self.result),
        )
        self.assertEqual(contract["source"]["engine"], "gaius")
        self.assertEqual(contract["source"]["engine_variant"], "google_doc_ai")
        self.assertEqual(C.validate(contract), [])

    def test_all_partial_go_to_review(self):
        contract = C.build_contract(self.blocks, engine="gaius", raw=self.raw)
        self.assertEqual(contract["gating"]["auto_approved"], [])


class TestAdaptersZeroNetwork(unittest.TestCase):
    def test_no_network_imports(self):
        for mod in ("adapters/chandra.py", "adapters/gaius.py"):
            with open(os.path.join(_ROOT, "scripts", mod), encoding="utf-8") as fh:
                src = fh.read()
            for f in ("socket", "urllib", "requests", "httpx"):
                self.assertNotIn(f"import {f}", src, f"{mod} importuje {f}")


if __name__ == "__main__":
    unittest.main()
