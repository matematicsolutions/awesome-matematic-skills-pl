"""Testy adaptera vlm-html (prompt-kontrakt VLM) + detektora degeneracji."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

import contract as C  # noqa: E402
import degeneracja  # noqa: E402
from adapters import vlm_html as vlm  # noqa: E402

_FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def _load_text(name):
    with open(os.path.join(_FIX, name), encoding="utf-8") as fh:
        return fh.read()


class TestVlmHtml(unittest.TestCase):
    def setUp(self):
        self.text = _load_text("vlm_html.sample.html")
        self.blocks = vlm.to_blocks(self.text)

    def test_blocks_and_pages(self):
        self.assertEqual(len(self.blocks), 8)
        self.assertEqual(vlm.page_count(self.text), 2)
        self.assertEqual(self.blocks[6].page, 2)

    def test_taxonomy_direct_no_mapping(self):
        types = [b.block_type for b in self.blocks]
        self.assertEqual(types, ["header", "title", "paragraph", "table",
                                 "signature", "stamp", "paragraph", "footer"])

    def test_signature_stamp_first_class(self):
        # przewaga nad Chandra: VLM etykietuje podpis/pieczatke wprost
        self.assertIn("podpis odreczny", self.blocks[4].text)
        self.assertIn("Wydzial II Karny", self.blocks[5].text)

    def test_bbox_scale_0_1000_normalized(self):
        b = self.blocks[1]  # title "80 60 920 100"
        self.assertEqual(b.bbox, [0.08, 0.06, 0.92, 0.1])

    def test_entities_and_inner_tags(self):
        self.assertIn("oddalił wniosek obrońcy", self.blocks[2].text)
        self.assertNotIn("<", self.blocks[2].text)

    def test_all_partial_all_to_review(self):
        raw = self.text.encode("utf-8")
        contract = C.build_contract(self.blocks, engine="vlm-html", raw=raw)
        self.assertEqual(contract["gating"]["auto_approved"], [])
        self.assertEqual(len(contract["gating"]["review_required"]), 8)
        self.assertEqual(C.validate(contract), [])

    def test_bad_bbox_is_none(self):
        blocks = vlm.to_blocks('<div data-label="paragraph" data-bbox="zle">x</div>')
        self.assertIsNone(blocks[0].bbox)
        self.assertIn("partial", blocks[0].flags)

    def test_unknown_label_maps_to_unknown(self):
        blocks = vlm.to_blocks('<div data-label="wynalazek">x</div>')
        self.assertEqual(blocks[0].block_type, "unknown")

    def test_truncated_generation_flagged(self):
        # generacja ucieta w polowie bloku -> blok domkniety flaga degenerate_tail
        blocks = vlm.to_blocks('<div data-label="paragraph" data-bbox="0 0 10 10">urwane w pol')
        self.assertEqual(len(blocks), 1)
        self.assertIn("degenerate_tail", blocks[0].flags)

    def test_guard_nonempty_input_zero_blocks_raises(self):
        with self.assertRaises(ValueError):
            vlm.to_blocks("<p>zwykly html bez data-label</p>")


class TestDegeneracja(unittest.TestCase):
    def test_normal_legal_text_clean(self):
        text = ("Sad Rejonowy w Warszawie po rozpoznaniu w dniu 5 sierpnia 2026 r. "
                "sprawy z wniosku obroncy postanowil oddalic wniosek i zasadzic "
                "od wnioskodawcy koszty postepowania wedlug norm przepisanych.")
        self.assertFalse(degeneracja.wykryj_zapetlenie(text))

    def test_single_token_loop_detected(self):
        text = "Poczatek dokumentu " + "art. " * 40
        self.assertTrue(degeneracja.wykryj_zapetlenie(text))

    def test_phrase_loop_detected(self):
        text = "Naglowek " + "w ocenie Sadu wniosek nie zasluguje " * 8
        self.assertTrue(degeneracja.wykryj_zapetlenie(text))

    def test_legit_repetition_below_threshold(self):
        # naturalne powtorzenie krotkiej frazy nie moze byc false-positive
        text = ("Powod wnosil o zaplate. Pozwany wnosil o oddalenie. "
                "Swiadek zeznal. Powod wnosil o zaplate odsetek.")
        self.assertFalse(degeneracja.wykryj_zapetlenie(text))

    def test_empty_text_clean(self):
        self.assertFalse(degeneracja.wykryj_zapetlenie(""))


if __name__ == "__main__":
    unittest.main()
