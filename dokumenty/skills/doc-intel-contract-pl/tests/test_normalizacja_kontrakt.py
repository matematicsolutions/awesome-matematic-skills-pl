# -*- coding: utf-8 -*-
"""KONFORMANCJA: `evidence.normalize` przeciw WSPOLNEJ tablicy prawdy.

Regula normalizacji tekstu ma jeden dom - `contract/normalizacja.cases.json` -
i dwoch czytelnikow:
  * ten test (Python, evidence.normalize)
  * `citation-grounding-pl/scripts/test-grounding.mjs` (Node, normalize)

Powod istnienia (zmierzone 2026-08-30): kazda strona miala wlasna implementacje
i wlasne luki. Python gubil U+2011 i U+00AD, JS gubil SZESC z osmiu badanych
znakow. Skutek po stronie JS byl gorszy niz przeoczenie - poziom FRAGMENT
orzekal "cytatu nie ma w zrodle" o cytacie, ktory tam byl, czyli stawial zarzut
halucynacji przez blad normalizacji.

Ten sam fakt w dwoch domach rozjezdza sie po cichu, a zgodnosc formatu mierzy sie
CUDZYM czytnikiem.
"""
import io
import json
import os
import sys
import unicodedata
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

import evidence as E  # noqa: E402

_TABLICA = os.path.join(_ROOT, "contract", "normalizacja.cases.json")


def _tablica():
    return json.load(io.open(_TABLICA, encoding="utf-8"))


class TestTablicaPrawdyJestSprawna(unittest.TestCase):
    """Kontrola POZYTYWNA bramki: bramka bez mianownika przechodzi zawsze."""

    def test_tablica_istnieje_i_jest_niepusta(self):
        self.assertTrue(os.path.exists(_TABLICA), "brak tablicy prawdy: %s" % _TABLICA)
        d = _tablica()
        self.assertGreater(len(d["przypadki"]), 20,
                           "tablica zbyt uboga, zeby cokolwiek dowodzic")

    def test_kazdy_przypadek_ma_komplet_pol(self):
        for c in _tablica()["przypadki"]:
            self.assertIn("nazwa", c)
            self.assertIn("wejscie", c)
            self.assertIn("oczekiwane", c)

    def test_nazwy_przypadkow_sa_unikalne(self):
        nazwy = [c["nazwa"] for c in _tablica()["przypadki"]]
        self.assertEqual(len(nazwy), len(set(nazwy)), "zduplikowana nazwa przypadku")

    def test_przypadki_NFD_sa_naprawde_w_NFD(self):
        """Fixture wierny ZJAWISKU: przypadek 'NFD' zapisany w NFC nie testuje nic."""
        nfd = [c for c in _tablica()["przypadki"] if c["nazwa"].startswith("NFD")]
        self.assertTrue(nfd, "brak przypadkow NFD - luka zmierzona mutacja M5")
        for c in nfd:
            w = c["wejscie"]
            self.assertEqual(unicodedata.normalize("NFD", w), w,
                             "przypadek %r nie jest w NFD" % c["nazwa"])
            self.assertGreater(len(w), len(unicodedata.normalize("NFC", w)),
                               "przypadek %r w NFD nie jest dluzszy niz w NFC - "
                               "czyli nie zawiera znaku laczacego" % c["nazwa"])

    def test_tablica_pokrywa_znaki_zmierzone_jako_luki(self):
        """Kazdy znak, ktory realnie nas przewrocil, MUSI miec swoj przypadek."""
        wszystkie = "".join(c["wejscie"] for c in _tablica()["przypadki"])
        for nazwa, znak in [
            ("dywiz nielamliwy U+2011", "\u2011"),
            ("miekki dywiz U+00AD", "\u00ad"),
            ("minus U+2212", "\u2212"),
            ("zerowa szerokosc U+200B", "\u200b"),
            ("wielokropek U+2026", "\u2026"),
            ("spacja nielamliwa U+00A0", "\u00a0"),
            ("BOM U+FEFF", "\ufeff"),
        ]:
            self.assertIn(znak, wszystkie, "tablica nie pokrywa %s" % nazwa)


class TestPythonZgodnyZTablica(unittest.TestCase):
    def test_kazdy_przypadek_z_osobna(self):
        d = _tablica()
        rozjazdy = []
        for c in d["przypadki"]:
            got = E.normalize(c["wejscie"])
            if got != c["oczekiwane"]:
                rozjazdy.append("%s: got=%r want=%r" % (c["nazwa"], got, c["oczekiwane"]))
        self.assertFalse(
            rozjazdy,
            "evidence.normalize rozjechal sie z tablica prawdy v%s:\n  %s"
            % (d.get("_wersja"), "\n  ".join(rozjazdy)),
        )

    def test_normalizacja_jest_idempotentna(self):
        """normalize(normalize(x)) == normalize(x) - inaczej wynik zalezy od
        tego, ile razy ktos ja przepusci przez pipeline."""
        for c in _tablica()["przypadki"]:
            raz = E.normalize(c["wejscie"])
            self.assertEqual(E.normalize(raz), raz, "nieidempotentne dla %r" % c["nazwa"])

    def test_normalize_i_normalize_with_map_daja_ten_sam_tekst(self):
        """Dwie sciezki tej samej reguly nie moga sie rozjechac."""
        for c in _tablica()["przypadki"]:
            self.assertEqual(E.normalize(c["wejscie"]),
                             E.normalize_with_map(c["wejscie"])[0],
                             "rozjazd sciezek dla %r" % c["nazwa"])


if __name__ == "__main__":
    unittest.main()
