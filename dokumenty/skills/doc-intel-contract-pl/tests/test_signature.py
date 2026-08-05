"""US3 / T032: testy heurystyki podpisu/pieczatki."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

import contract as C  # noqa: E402
import signature as S  # noqa: E402


def _blk(**kw):
    base = dict(id="b1", page=1, bbox=[0.6, 0.85, 0.9, 0.95],
                block_type="unknown", text="(podpis)", confidence=0.4)
    base.update(kw)
    return C.Block(**base)


class TestHeuristic(unittest.TestCase):
    def test_bottom_lowconf_short_is_candidate(self):
        self.assertTrue(S.is_signature_like(_blk()))

    def test_typed_signature_always_true(self):
        self.assertTrue(S.is_signature_like(_blk(block_type="signature")))
        self.assertTrue(S.is_signature_like(_blk(block_type="stamp")))

    def test_top_of_page_not_candidate(self):
        self.assertFalse(S.is_signature_like(_blk(bbox=[0.1, 0.05, 0.9, 0.1])))

    def test_long_confident_text_not_candidate(self):
        self.assertFalse(S.is_signature_like(_blk(
            text="Dlugi akapit uzasadnienia " * 5, confidence=0.98)))

    def test_no_bbox_not_candidate(self):
        self.assertFalse(S.is_signature_like(_blk(bbox=None)))

    def test_paragraph_type_at_bottom_lowconf_is_candidate(self):
        self.assertTrue(S.is_signature_like(_blk(block_type="paragraph")))

    def test_table_type_excluded(self):
        self.assertFalse(S.is_signature_like(_blk(block_type="table")))


class TestApply(unittest.TestCase):
    def test_apply_flags_and_returns_candidate(self):
        blocks = [_blk(id="b1"), _blk(id="b2", bbox=[0.1, 0.05, 0.9, 0.1])]
        cands = S.apply(blocks)
        self.assertEqual(cands, ["b1"])
        self.assertIn("signature_suspected", blocks[0].flags)
        self.assertNotIn("signature_suspected", blocks[1].flags)

    def test_injected_detector_confirms(self):
        blocks = [_blk(id="b1")]
        S.apply(blocks, detector=lambda b: True)
        self.assertIn("signature_confirmed", blocks[0].flags)

    def test_detector_error_is_captured_not_raised(self):
        blocks = [_blk(id="b1")]
        def boom(b):
            raise RuntimeError("vision down")
        S.apply(blocks, detector=boom)  # nie rzuca
        self.assertIn("signature_detector_error", blocks[0].flags)


class TestZeroNetwork(unittest.TestCase):
    def test_no_network_imports(self):
        with open(os.path.join(_ROOT, "scripts", "signature.py"), encoding="utf-8") as fh:
            src = fh.read()
        for f in ("socket", "urllib", "requests", "httpx"):
            self.assertNotIn(f"import {f}", src)


if __name__ == "__main__":
    unittest.main()
