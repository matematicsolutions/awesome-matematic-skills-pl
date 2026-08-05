"""Testy regresyjne kontraktu Document Intelligence (US1 MVP).

Uruchom:
  cd ~/.claude/skills/doc-intel-contract-pl
  python -m unittest discover -s tests -v
"""
import json
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

import contract as C  # noqa: E402
from adapters import opendataloader as odl  # noqa: E402
from adapters import pdftotext as ptt  # noqa: E402

_FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def _load(name, mode="r"):
    with open(os.path.join(_FIX, name), mode, encoding=None if "b" in mode else "utf-8") as fh:
        return fh.read()


class TestDeterminism(unittest.TestCase):
    def test_doc_id_deterministic(self):
        raw = b"identyczne wejscie"
        self.assertEqual(C.compute_doc_id(raw), C.compute_doc_id(raw))

    def test_doc_id_is_sha256_hex(self):
        did = C.compute_doc_id(b"x")
        self.assertEqual(len(did), 64)
        int(did, 16)  # rzuci jesli nie hex

    def test_doc_id_differs_on_change(self):
        self.assertNotEqual(C.compute_doc_id(b"a"), C.compute_doc_id(b"b"))


class TestOpendataloaderAdapter(unittest.TestCase):
    def setUp(self):
        self.raw = _load("opendataloader.sample.json", "rb")
        self.data = json.loads(self.raw.decode("utf-8"))
        self.blocks = odl.to_blocks(self.data)

    def test_block_count(self):
        self.assertEqual(len(self.blocks), 5)

    def test_bbox_normalized_0_1(self):
        for b in self.blocks:
            for v in b.bbox:
                self.assertGreaterEqual(v, 0.0)
                self.assertLessEqual(v, 1.0)

    def test_block_type_mapping(self):
        self.assertEqual(self.blocks[0].block_type, "title")
        self.assertEqual(self.blocks[2].block_type, "table")
        self.assertEqual(self.blocks[3].block_type, "signature")

    def test_gating_splits_by_threshold(self):
        contract = C.build_contract(
            self.blocks, engine="opendataloader", raw=self.raw, threshold=0.85,
        )
        g = contract["gating"]
        # table 0.62 i signature 0.41 < 0.85 -> review
        self.assertIn("b0003", g["review_required"])
        self.assertIn("b0004", g["review_required"])
        # title 0.99 i teksty 0.97/0.95 -> auto
        self.assertIn("b0001", g["auto_approved"])
        self.assertEqual(
            set(g["review_required"]) | set(g["auto_approved"]),
            {b.id for b in self.blocks},
        )

    def test_schema_valid(self):
        contract = C.build_contract(self.blocks, engine="opendataloader", raw=self.raw)
        self.assertEqual(C.validate(contract), [])

    def test_page_count(self):
        self.assertEqual(odl.page_count(self.data), 2)


class TestPdftotextAdapter(unittest.TestCase):
    def setUp(self):
        self.raw = _load("plain.sample.txt", "rb")
        self.text = self.raw.decode("utf-8")
        self.blocks = ptt.to_blocks(self.text)

    def test_partial_flag_and_nulls(self):
        for b in self.blocks:
            self.assertIsNone(b.bbox)
            self.assertIsNone(b.confidence)
            self.assertIn("partial", b.flags)

    def test_partial_all_go_to_review(self):
        contract = C.build_contract(self.blocks, engine="pdftotext", raw=self.raw)
        g = contract["gating"]
        self.assertEqual(g["auto_approved"], [])
        self.assertEqual(len(g["review_required"]), len(self.blocks))

    def test_title_heuristic(self):
        self.assertEqual(self.blocks[0].block_type, "title")  # POSTANOWIENIE (caps)

    def test_schema_valid(self):
        contract = C.build_contract(self.blocks, engine="pdftotext", raw=self.raw)
        self.assertEqual(C.validate(contract), [])


class TestSchemaValidatorCatchesBad(unittest.TestCase):
    def test_missing_required_detected(self):
        bad = {"doc_id": "x"}  # brak reszty wymaganych
        errors = C.validate(bad)
        self.assertTrue(any("brak wymaganego pola" in e for e in errors))

    def test_bad_block_type_detected(self):
        blk = C.Block(id="b1", page=1, bbox=None, block_type="paragraph", text="t", confidence=0.9)
        contract = C.build_contract([blk], engine="pdftotext", raw=b"x")
        contract["blocks"][0]["block_type"] = "NIEISTNIEJACY"
        errors = C.validate(contract)
        self.assertTrue(any("enum" in e for e in errors))


class TestZeroNetwork(unittest.TestCase):
    """Article I: warstwa kontraktu nie importuje bibliotek sieciowych."""
    def test_no_network_imports(self):
        forbidden = {"socket", "urllib", "http", "requests", "httpx", "urllib3"}
        for mod in ("contract", "normalize"):
            src = _load(os.path.join(_ROOT, "scripts", f"{mod}.py"))
            for f in forbidden:
                self.assertNotIn(f"import {f}", src, f"{mod}.py importuje {f}")


if __name__ == "__main__":
    unittest.main()
