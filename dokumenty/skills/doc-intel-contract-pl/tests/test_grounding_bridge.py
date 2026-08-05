"""US3 / T030: testy mostu kontrakt -> citation-grounding-pl."""
import json
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

import contract as C  # noqa: E402
from adapters import opendataloader as odl  # noqa: E402
import grounding_bridge as GB  # noqa: E402

_FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def _contract_from_fixture():
    with open(os.path.join(_FIX, "opendataloader.sample.json"), "rb") as fh:
        raw = fh.read()
    data = json.loads(raw.decode("utf-8"))
    blocks = odl.to_blocks(data)
    return C.build_contract(blocks, engine="opendataloader", raw=raw)


class TestLocateResolvesRegion(unittest.TestCase):
    def setUp(self):
        self.contract = _contract_from_fixture()

    def test_found_quote_gets_bbox_anchor(self):
        task = GB.build_task(self.contract, ["Sad Rejonowy w Warszawie"])
        item = task["items"][0]
        self.assertIsNotNone(item["anchor_resolved"])
        self.assertEqual(item["anchor_resolved"]["page"], 1)
        self.assertEqual(item["anchor"], "b0002")
        self.assertIsInstance(item["anchor_resolved"]["bbox"], list)
        # source_text = tekst konkretnego bloku, nie caly dokument
        self.assertIn("Sad Rejonowy", item["source_text"])

    def test_missing_quote_falls_back_to_full_doc(self):
        task = GB.build_task(self.contract, ["cytat ktorego nie ma w dokumencie"])
        item = task["items"][0]
        self.assertIsNone(item["anchor_resolved"])
        self.assertIsNone(item["anchor"])
        # fallback: source_text = caly dokument (grounding uczciwie obnizy poziom)
        self.assertIn("POSTANOWIENIE", item["source_text"])

    def test_normalization_matches_despite_quotes_and_case(self):
        # rozne cudzyslowy + wielkosc liter nie psuja dopasowania
        task = GB.build_task(self.contract, ['„UZASADNIENIE. w OCENIE sadu”'])
        # w fixture blok 5 to "Uzasadnienie. W ocenie Sadu..."
        self.assertEqual(task["items"][0]["anchor"], "b0005")

    def test_default_claim_type_is_fragment_level(self):
        task = GB.build_task(self.contract, ["POSTANOWIENIE"])
        self.assertEqual(task["items"][0]["claim_type"], "cytat_doslowny")

    def test_source_id_defaults_to_doc_id(self):
        task = GB.build_task(self.contract, ["POSTANOWIENIE"])
        self.assertEqual(task["items"][0]["source_id"], self.contract["doc_id"])

    def test_task_shape_matches_grounding_input(self):
        task = GB.build_task(self.contract, ["POSTANOWIENIE", "brak"])
        self.assertIn("items", task)
        for it in task["items"]:
            for key in ("id", "source_id", "claim_type", "quote", "source_text", "anchor", "anchor_resolved"):
                self.assertIn(key, it)


class TestBridgeZeroNetwork(unittest.TestCase):
    def test_no_network_imports(self):
        with open(os.path.join(_ROOT, "scripts", "grounding_bridge.py"), encoding="utf-8") as fh:
            src = fh.read()
        for f in ("socket", "urllib", "requests", "httpx"):
            self.assertNotIn(f"import {f}", src)


if __name__ == "__main__":
    unittest.main()
