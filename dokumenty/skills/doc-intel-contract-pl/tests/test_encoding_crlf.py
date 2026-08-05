"""Regresja z realnych akt: CRLF (Windows pdftotext) + UTF-8 na stdout (polskie znaki).

Oba bugi wykryte na prawdziwych dokumentach spraw 2026-07-01.
"""
import json
import os
import subprocess
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

from adapters import pdftotext as ptt  # noqa: E402
from adapters import gaius as gai  # noqa: E402

_FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


class TestCRLF(unittest.TestCase):
    def test_pdftotext_crlf_splits_paragraphs(self):
        # przed fixem: "\n\n" nie lapal "\r\n\r\n" -> 1 blok zamiast 3
        blocks = ptt.to_blocks("Akapit A\r\n\r\nAkapit B\r\n\r\nAkapit C")
        self.assertEqual(len(blocks), 3)

    def test_gaius_crlf_splits_paragraphs(self):
        blocks = gai.to_blocks({"text": "A\r\n\r\nB\r\n\r\nC"})
        self.assertEqual(len(blocks), 3)

    def test_formfeed_pages_with_crlf(self):
        blocks = ptt.to_blocks("Str1\r\n\r\ntekst\fStr2\r\n\r\ntekst")
        self.assertEqual(max(b.page for b in blocks), 2)


class TestUtf8Stdout(unittest.TestCase):
    def test_normalize_emits_utf8_json_with_polish(self):
        # przed fixem: stdout w cp1250 -> odczyt utf-8 rzucal UnicodeDecodeError
        proc = subprocess.run(
            [sys.executable, os.path.join(_ROOT, "scripts", "normalize.py"),
             "--engine", "gaius", os.path.join(_FIX, "gaius_pl.sample.json")],
            capture_output=True,
        )
        self.assertEqual(proc.returncode, 0)
        data = json.loads(proc.stdout.decode("utf-8"))  # nie rzuca = UTF-8 OK
        joined = " ".join(b["text"] for b in data["blocks"])
        self.assertIn("SĄD", joined)
        self.assertIn("żółć", joined)


if __name__ == "__main__":
    unittest.main()
