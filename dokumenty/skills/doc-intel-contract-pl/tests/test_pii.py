"""US2: testy detekcji PII PL + redaction_candidates."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

import contract as C  # noqa: E402
import pii_flags as P  # noqa: E402


class TestPeselChecksum(unittest.TestCase):
    def test_valid_pesel_detected(self):
        # 44051401359 - kanoniczny poprawny PESEL (przyklad z dokumentacji GUS)
        self.assertIn("pesel", P.detect("PESEL: 44051401359"))

    def test_invalid_pesel_rejected(self):
        # zla suma kontrolna -> nie flagujemy (ograniczenie false-positive)
        self.assertNotIn("pesel", P.detect("numer 44051401358"))


class TestOtherPII(unittest.TestCase):
    def test_nip_valid(self):
        self.assertIn("nip", P.detect("NIP 5252248481"))  # poprawny NIP

    def test_nip_invalid_rejected(self):
        self.assertNotIn("nip", P.detect("1234567890"))

    def test_email(self):
        self.assertIn("email", P.detect("kontakt: jan.kowalski@example.pl"))

    def test_iban_pl(self):
        self.assertIn("iban", P.detect("PL61109010140000071219812874"))

    def test_dowod(self):
        self.assertIn("dowod", P.detect("dowod ABC123456"))

    def test_clean_text_no_pii(self):
        self.assertEqual(P.detect("Sad oddalil wniosek."), [])


class TestAnnotate(unittest.TestCase):
    def test_pii_block_becomes_candidate(self):
        blocks = [
            C.Block(id="b1", page=1, bbox=None, block_type="paragraph",
                    text="jan@example.pl", confidence=0.9),
            C.Block(id="b2", page=1, bbox=None, block_type="paragraph",
                    text="czysty tekst", confidence=0.9),
        ]
        cands = P.annotate(blocks)
        self.assertEqual(cands, ["b1"])
        self.assertIn("pii_suspected", blocks[0].flags)
        self.assertIn("pii:email", blocks[0].flags)
        self.assertEqual(blocks[1].flags, [])

    def test_signature_block_is_sensitive_candidate(self):
        blocks = [C.Block(id="b1", page=1, bbox=None, block_type="signature",
                          text="(podpis)", confidence=0.4)]
        cands = P.annotate(blocks)
        self.assertEqual(cands, ["b1"])
        self.assertIn("sensitive_block", blocks[0].flags)

    def test_contract_carries_redaction_and_stays_schema_valid(self):
        blocks = [C.Block(id="b1", page=1, bbox=None, block_type="paragraph",
                          text="PESEL 44051401359", confidence=0.9)]
        cands = P.annotate(blocks)
        contract = C.build_contract(blocks, engine="pdftotext", raw=b"x",
                                    redaction_candidates=cands)
        self.assertEqual(contract["redaction_candidates"], ["b1"])
        self.assertEqual(C.validate(contract), [])


class TestPiiZeroNetwork(unittest.TestCase):
    def test_no_network_imports(self):
        with open(os.path.join(_ROOT, "scripts", "pii_flags.py"), encoding="utf-8") as fh:
            src = fh.read()
        for f in ("socket", "urllib", "requests", "httpx"):
            self.assertNotIn(f"import {f}", src)


if __name__ == "__main__":
    unittest.main()
