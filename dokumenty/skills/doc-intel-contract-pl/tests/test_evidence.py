# -*- coding: utf-8 -*-
"""Testy warstwy dowodowej (kind x resolution) i lokalizatora z mapa offsetow.

Uklad wzorowany na naszej regule: NAJPIERW pokaz problem, potem lek.
Klasa `TestCzerwienStarejWarstwy` dokumentuje trzy defekty wersji 1.x na
fixture wiernym zjawisku - gdyby ktos kiedys "uproscil" normalizacje albo
przywrocil pierwsze-trafienie-wygrywa, te testy zapala sie na czerwono.
"""
import io
import json
import os
import sys
import unicodedata
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

import contract as C  # noqa: E402
import evidence as E  # noqa: E402
import grounding_bridge as GB  # noqa: E402
from adapters import opendataloader as odl  # noqa: E402

_FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixtures")


def _kontrakt_pl():
    with open(os.path.join(_FIX, "pismo_pl_typografia.sample.json"), "rb") as fh:
        raw = fh.read()
    blocks = odl.to_blocks(json.loads(raw.decode("utf-8")))
    return C.build_contract(blocks, engine="opendataloader", raw=raw)


# ---------------------------------------------------------------------------
# 1. Normalizacja: znaki, ktore polski PDF wstawia naprawde
# ---------------------------------------------------------------------------
class TestNormalizacjaZnakowPL(unittest.TestCase):
    def test_dywiz_nielamliwy_u2011(self):
        """U+2011 to ZMIERZONA luka wersji 1.x (ta sama co kiedys na EUR-Lex)."""
        self.assertEqual(E.normalize("Rzeszow‑Zachod"), "rzeszow-zachod")

    def test_minus_u2212(self):
        self.assertEqual(E.normalize("−5 stopni"), "-5 stopni")

    def test_miekki_dywiz_u00ad_znika(self):
        """W justowanym PDF U+00AD siedzi WEWNATRZ slowa i lamie dopasowanie."""
        self.assertEqual(E.normalize("postano­wienie"), "postanowienie")

    def test_zerowa_szerokosc_znika(self):
        self.assertEqual(E.normalize("Sad​Rejonowy"), "sadrejonowy")

    def test_spacja_nielamliwa_to_spacja(self):
        self.assertEqual(E.normalize("art. 1"), "art. 1")

    def test_przeniesienie_wyrazu_bez_spacji(self):
        self.assertEqual(E.normalize("postano-\nwienie"), "postanowienie")

    def test_wielokropek_rozwijany(self):
        self.assertEqual(E.normalize("tresc…"), "tresc...")

    def test_cudzyslowy_drukarskie_ujednolicone(self):
        self.assertEqual(E.normalize("„tresc”"), '"tresc"')

    def test_kazda_polska_litera_osobno(self):
        """Nasza regula: testuj KAZDA litere osobno.

        'l' U+0142 nie ma dekompozycji i idzie inna sciezka niz reszta - to
        dokladnie ten uklad, w ktorym cos dziala dla osmiu z dziewieciu.
        """
        for ch in "acelnoszzACELNOSZZąćęłńóśźż":
            nfc = unicodedata.normalize("NFC", ch)
            nfd = unicodedata.normalize("NFD", ch)
            self.assertEqual(
                E.normalize(nfc), E.normalize(nfd),
                "NFC i NFD musza dac ten sam wynik dla %r (U+%04X)" % (ch, ord(ch)),
            )

    def test_nfd_calego_wyrazu_rowne_nfc(self):
        for word in ["ŁÓDŹ", "SĄD", "ŚCIŚLE"]:
            self.assertEqual(
                E.normalize(unicodedata.normalize("NFC", word)),
                E.normalize(unicodedata.normalize("NFD", word)),
            )


# ---------------------------------------------------------------------------
# 2. Mapa offsetow - warunek konieczny rozdzielczosci `span`
# ---------------------------------------------------------------------------
class TestMapaOffsetow(unittest.TestCase):
    PROBKI = [
        "Sad Rejonowy w Warszawie",
        "Sad Rejonowy\n\n   w  Warszawie, dnia 5 maja",
        "Wydano postano-\nwienie w sprawie",
        unicodedata.normalize("NFD", "SAD OKREGOWY w LODZI"),
        "sygn. akt II‑CSK 123/45 z dnia",
        "Poucze­nie o srodkach",
        "",
        "   ",
        "­​",
    ]

    def test_niezmiennik_dlugosci_mapy(self):
        for src in self.PROBKI:
            norm, ss, se = E.normalize_with_map(src)
            self.assertEqual(len(norm), len(ss))
            self.assertEqual(len(norm), len(se))

    def test_mapa_jest_niemalejaca(self):
        for src in self.PROBKI:
            _, ss, _ = E.normalize_with_map(src)
            self.assertEqual(list(ss), sorted(ss), "offsety musza rosnac dla %r" % src)

    def test_span_wraca_na_oryginal(self):
        """Wyciety zakres, ponownie znormalizowany, musi dac szukana igle."""
        przypadki = [
            ("Sad Rejonowy w Warszawie", "rejonowy"),
            ("Sad Rejonowy\n\n   w  Warszawie", "w warszawie"),
            ("Wydano postano-\nwienie w sprawie", "postanowienie"),
            ("sygn. akt II‑CSK 123/45", "ii-csk 123/45"),
            ("Poucze­nie o srodkach", "pouczenie"),
        ]
        for src, needle in przypadki:
            norm, ss, se = E.normalize_with_map(src)
            pos = norm.find(needle)
            self.assertNotEqual(pos, -1, "igla %r nie w %r" % (needle, norm))
            span = (ss[pos], se[pos + len(needle) - 1])
            self.assertEqual(E.normalize(src[span[0]:span[1]]).strip(), needle)

    def test_pusty_wejscie_nie_wybucha(self):
        for src in ["", None, "   ", "­"]:
            norm, ss, se = E.normalize_with_map(src)
            self.assertEqual(norm, "")
            self.assertEqual(ss, [])
            self.assertEqual(se, [])


# ---------------------------------------------------------------------------
# 3. Dwie osie i ich uporzadkowanie
# ---------------------------------------------------------------------------
class TestDwieOsie(unittest.TestCase):
    def test_osie_sa_uporzadkowane(self):
        self.assertGreater(E.KIND_STRENGTH["verbatim"], E.KIND_STRENGTH["normalized"])
        self.assertGreater(E.KIND_STRENGTH["normalized"], E.KIND_STRENGTH["observed"])
        self.assertGreater(E.KIND_STRENGTH["observed"], E.KIND_STRENGTH["derived"])
        self.assertGreater(E.RESOLUTION_STRENGTH["span"], E.RESOLUTION_STRENGTH["block"])
        self.assertGreater(E.RESOLUTION_STRENGTH["block"], E.RESOLUTION_STRENGTH["page"])
        self.assertGreater(E.RESOLUTION_STRENGTH["page"], E.RESOLUTION_STRENGTH["document"])
        self.assertGreater(E.RESOLUTION_STRENGTH["document"], E.RESOLUTION_STRENGTH["none"])

    def test_osie_sa_ortogonalne(self):
        """observed/document i normalized/span to rozne, niezalezne twierdzenia."""
        bl = _kontrakt_pl()["blocks"]
        mocny = E.locate("art. 385 k.p.c.", bl)
        slaby = E.locate("wyrok Trybunalu Konstytucyjnego", bl)
        self.assertEqual((mocny.kind, mocny.resolution), ("verbatim", "span"))
        self.assertEqual((slaby.kind, slaby.resolution), ("derived", "none"))
        self.assertGreater(mocny.strength, slaby.strength)

    def test_bramka_wymaga_OBU_osi(self):
        self.assertTrue(GB.gate({"kind": "verbatim", "resolution": "span"}))
        # mocny rodzaj, slaba rozdzielczosc -> NIE przechodzi
        self.assertFalse(GB.gate({"kind": "verbatim", "resolution": "document"}))
        # slaby rodzaj, mocna rozdzielczosc -> NIE przechodzi
        self.assertFalse(GB.gate({"kind": "observed", "resolution": "span"}))

    def test_bramka_odrzuca_wieloznacznosc_mimo_mocnych_osi(self):
        """Mocny dowod na PIEC miejsc nie jest mocnym dowodem na jedno.

        Znalezione w przebiegu bojowym: "Sadu Okregowego" mial verbatim/span
        i przechodzil bramke, majac 5 kandydatow i anchor_resolved=None.
        """
        wieloznaczny = {
            "kind": "verbatim", "resolution": "span", "match_count": 5,
            "anchors": [{"block_id": "b%d" % i} for i in range(5)],
        }
        self.assertFalse(GB.gate(wieloznaczny))
        self.assertTrue(GB.gate(wieloznaczny, require_unambiguous=False))

    def test_bramka_przepuszcza_jednoznaczny(self):
        jednoznaczny = {
            "kind": "verbatim", "resolution": "span", "match_count": 1,
            "anchors": [{"block_id": "b1"}],
        }
        self.assertTrue(GB.gate(jednoznaczny))

    def test_bramka_konczy_sie_zgodnie_z_anchor_resolved(self):
        """Niezmiennik: co przeszlo bramke, MA jedna kotwice w wyjsciu mostu."""
        kontrakt = _kontrakt_pl()
        quotes = ["art. 385 k.p.c.", "II-CSK 118/24", "Sadu Okregowego",
                  "prawa materialnego", "wyrok Trybunalu Konstytucyjnego"]
        for it in GB.build_task(kontrakt, quotes)["items"]:
            if GB.gate(it["evidence"]):
                self.assertIsNotNone(
                    it["anchor_resolved"],
                    "cytat %r przeszedl bramke bez jednej kotwicy" % it["quote"],
                )

    def test_bramka_z_pustym_dowodem_nie_przechodzi(self):
        """Nasza regula: bramka z pusta lista przechodzi zawsze - tu nie moze."""
        self.assertFalse(GB.gate({}))
        self.assertFalse(GB.gate({"kind": None, "resolution": None}))


# ---------------------------------------------------------------------------
# 4. Bramki dystynktywnosci: fail-empty, ale NIGDY po cichu
# ---------------------------------------------------------------------------
class TestFailEmptyZMianownikiem(unittest.TestCase):
    def setUp(self):
        self.bl = _kontrakt_pl()["blocks"]

    def test_za_krotki_cytat_odrzucony_z_powodem(self):
        ev = E.locate("24", self.bl)
        self.assertEqual(ev.resolution, "none")
        self.assertEqual(ev.anchors, [])
        self.assertIn("za_krotki", ev.skipped_reason)

    def test_krotka_liczba_odrzucona_z_powodem(self):
        ev = E.locate("118", self.bl)
        self.assertEqual(ev.anchors, [])
        self.assertIn("krotka_liczba", ev.skipped_reason)

    def test_niedystynktywny_termin_nie_dostaje_kotwicy_ale_podaje_liczbe(self):
        """Powyzej progu: zero kotwic, ale mianownik trafien JAWNY."""
        ev = E.locate("Sadu Okregowego", self.bl, max_match_blocks=2)
        self.assertEqual(ev.anchors, [])
        self.assertEqual(ev.kind, "observed")
        self.assertEqual(ev.match_count, 5)
        self.assertIn("niedystynktywny", ev.skipped_reason)

    def test_brak_w_dokumencie_ma_nazwany_powod(self):
        ev = E.locate("wyrok Trybunalu Konstytucyjnego", self.bl)
        self.assertEqual(ev.kind, "derived")
        self.assertEqual(ev.match_count, 0)
        self.assertEqual(ev.skipped_reason, "brak_w_dokumencie")

    def test_przez_granice_blokow_to_observed_nie_derived(self):
        """Cytat sklejajacy dwa bloki istnieje w dokumencie - to nie 'brak'."""
        ev = E.locate("jest prawomocne z chwila wydania. Od orzeczenia", self.bl)
        self.assertEqual(ev.kind, "observed")
        self.assertEqual(ev.resolution, "document")
        self.assertEqual(ev.skipped_reason, "przez_granice_blokow")

    def test_kazdy_wynik_niesie_mianownik(self):
        """Nie ma wyniku bez match_count - cisza bez powodu uczy ignorowac raporty."""
        for q in ["24", "Sadu Okregowego", "art. 385 k.p.c.", "czegos takiego nie ma"]:
            ev = E.locate(q, self.bl)
            self.assertIsInstance(ev.match_count, int)
            self.assertTrue(ev.anchors or ev.skipped_reason,
                            "wynik bez kotwic MUSI podac powod (%r)" % q)


# ---------------------------------------------------------------------------
# 5. CZERWIEN: trzy defekty wersji 1.x, kazdy na fixture wiernym zjawisku
# ---------------------------------------------------------------------------
class TestCzerwienStarejWarstwy(unittest.TestCase):
    """Gdyby ktos przywrocil zachowanie 1.x, te testy zapala sie na czerwono."""

    def setUp(self):
        self.kontrakt = _kontrakt_pl()
        self.bl = self.kontrakt["blocks"]

    def test_defekt1_pierwsze_trafienie_nie_jest_juz_pewna_kotwica(self):
        """1.x: `anchor=b0003` z bbox. Prawda: termin jest w 5 blokach."""
        ev = E.locate("Sadu Okregowego", self.bl)
        self.assertEqual(ev.match_count, 5)
        self.assertEqual(len(ev.anchors), 5)
        task = GB.build_task(self.kontrakt, ["Sadu Okregowego"])
        item = task["items"][0]
        self.assertIsNone(item["anchor_resolved"],
                          "przy 5 kandydatach most NIE MOZE podac jednej kotwicy")
        self.assertIn("wieloznaczny", item["flags"])
        self.assertEqual(len(item["evidence"]["anchors"]), 5)

    def test_defekt2a_sygnatura_z_dywizem_nielamliwym_juz_sie_znajduje(self):
        """1.x gubila ten cytat i wpadala w fallback 'caly dokument'."""
        ev = E.locate("II-CSK 118/24", self.bl)
        self.assertEqual(ev.kind, "normalized")
        self.assertEqual(ev.resolution, "span")
        self.assertEqual(len(ev.anchors), 1)
        a = ev.anchors[0]
        src = next(b["text"] for b in self.bl if b["id"] == a.block_id)
        self.assertEqual(src[a.span[0]:a.span[1]], "II‑CSK 118/24")

    def test_defekt2b_miekki_dywiz_juz_sie_znajduje(self):
        ev = E.locate("prawa materialnego", self.bl)
        self.assertEqual(ev.resolution, "span")
        a = ev.anchors[0]
        src = next(b["text"] for b in self.bl if b["id"] == a.block_id)
        self.assertEqual(src[a.span[0]:a.span[1]], "prawa material­nego")

    def test_defekt3_rozdzielczosc_siega_znaku_nie_bloku(self):
        """1.x konczyla na bboxie CALEGO bloku - zakresu znakowego nie bylo."""
        task = GB.build_task(self.kontrakt, ["art. 385 k.p.c."])
        ar = task["items"][0]["anchor_resolved"]
        self.assertIsNotNone(ar["span"])
        self.assertEqual(len(ar["span"]), 2)
        self.assertLess(ar["span"][0], ar["span"][1])
        self.assertIsNotNone(ar["bbox"], "bbox zostaje - sluzy podswietleniu")

    def test_defekt4_dwuznakowa_liczba_nie_wskazuje_juz_bloku(self):
        """1.x: '24' trafialo w '118/24' i dawalo pewna kotwice b0002."""
        task = GB.build_task(self.kontrakt, ["24"])
        self.assertIsNone(task["items"][0]["anchor"])
        self.assertIsNone(task["items"][0]["anchor_resolved"])


# ---------------------------------------------------------------------------
# 6. Most: ksztalt wyjscia i zgodnosc wsteczna
# ---------------------------------------------------------------------------
class TestMostKontraktWyjscia(unittest.TestCase):
    def setUp(self):
        self.kontrakt = _kontrakt_pl()

    def test_klucze_1x_nadal_obecne(self):
        task = GB.build_task(self.kontrakt, ["art. 385 k.p.c."])
        for key in ("id", "source_id", "claim_type", "quote", "source_text",
                    "anchor", "anchor_resolved"):
            self.assertIn(key, task["items"][0])

    def test_nowe_klucze_dowodowe(self):
        task = GB.build_task(self.kontrakt, ["art. 385 k.p.c."])
        it = task["items"][0]
        self.assertIn("evidence", it)
        self.assertIn("flags", it)
        for key in ("kind", "resolution", "kind_strength", "resolution_strength",
                    "anchors", "match_count", "skipped_reason"):
            self.assertIn(key, it["evidence"])

    def test_glify_zrodla_inne_oflagowane(self):
        """Prawnik przepisujacy do pisma musi wziac tekst ZRODLA, nie cytat."""
        task = GB.build_task(self.kontrakt, ["II-CSK 118/24"])
        self.assertIn("glify_zrodla_inne", task["items"][0]["flags"])

    def test_verbatim_nie_jest_flagowany(self):
        task = GB.build_task(self.kontrakt, ["art. 385 k.p.c."])
        self.assertNotIn("glify_zrodla_inne", task["items"][0]["flags"])

    def test_podsumowanie_ma_pelny_mianownik(self):
        quotes = ["art. 385 k.p.c.", "Sadu Okregowego", "czegos takiego nie ma"]
        s = GB.build_task(self.kontrakt, quotes)["summary"]
        self.assertEqual(s["total"], 3)
        self.assertEqual(s["located_single"] + s["ambiguous"] + s["unlocated"], s["total"])

    def test_source_text_bloku_przy_jednym_trafieniu(self):
        task = GB.build_task(self.kontrakt, ["art. 385 k.p.c."])
        self.assertIn("art. 385", task["items"][0]["source_text"])
        self.assertNotIn("POSTANOWIENIE", task["items"][0]["source_text"])

    def test_source_text_calosci_przy_braku(self):
        task = GB.build_task(self.kontrakt, ["czegos takiego nie ma"])
        self.assertIn("POSTANOWIENIE", task["items"][0]["source_text"])

    def test_determinizm(self):
        """Te same wejscia -> identyczne wyjscie (bez znacznikow czasu)."""
        quotes = ["art. 385 k.p.c.", "Sadu Okregowego", "II-CSK 118/24"]
        a = json.dumps(GB.build_task(self.kontrakt, quotes), sort_keys=True, ensure_ascii=False)
        b = json.dumps(GB.build_task(self.kontrakt, quotes), sort_keys=True, ensure_ascii=False)
        self.assertEqual(a, b)


# ---------------------------------------------------------------------------
# 2b. NFD: luka znaleziona mutacja M5 (skrocenie zakresu do jednego znaku)
# ---------------------------------------------------------------------------
class TestMapaOffsetowNFD(unittest.TestCase):
    """Dla NFC grupa ma 1 znak, wiec mutacja skracajaca zakres jest
    nierozroznialna. Rozni je dopiero wejscie w NFD, gdzie znak bazowy plus
    laczacy to JEDNA grupa. Bez tej klasy mutacja M5 przechodzila na zielono.
    """

    def test_koniec_zakresu_obejmuje_znaki_laczace(self):
        src = unicodedata.normalize("NFD", "ŻÓŁW")  # ZOLW z diakrytykami
        norm, ss, se = E.normalize_with_map(src)
        self.assertEqual(norm, "żółw")
        self.assertEqual(se[0] - ss[0], 2, "z-kropka w NFD to 2 znaki zrodlowe")
        self.assertEqual(se[1] - ss[1], 2, "o-kreska w NFD to 2 znaki zrodlowe")
        # l-kreska NIE ma dekompozycji - osiem z dziewieciu
        self.assertEqual(se[2] - ss[2], 1, "l-kreska nie ma dekompozycji")

    def test_span_wraca_na_oryginal_dla_NFD(self):
        przypadki = [
            ("wyrok w sprawie ŁÓDŹ", "łódź"),
            ("SĄD OKRĘGOWY w ŁODZI", "okręgowy"),
            ("akta ŚCIŚLE tajne", "ściśle"),
            ("miasto ŁÓDŹ i okolice", "łódź"),
        ]
        for plain, igla in przypadki:
            src = unicodedata.normalize("NFD", plain)
            norm, ss, se = E.normalize_with_map(src)
            pos = norm.find(igla)
            self.assertNotEqual(pos, -1, "igla %r nie w %r" % (igla, norm))
            span = (ss[pos], se[pos + len(igla) - 1])
            self.assertEqual(
                E.normalize(src[span[0]:span[1]]).strip(), igla,
                "zakres NFD musi obejmowac znaki laczace (%r)" % igla,
            )

    def test_locate_na_dokumencie_w_NFD(self):
        """Cala sciezka: dokument w NFD, cytat w NFC - span ma wrocic."""
        bloki = [{
            "id": "b1", "page": 1, "bbox": [0, 0, 1, 1],
            "text": unicodedata.normalize("NFD", "Sąd Okręgowy w Łodzi orzekl"),
        }]
        ev = E.locate("Okręgowy w Łodzi", bloki)
        self.assertEqual(ev.resolution, "span")
        self.assertEqual(len(ev.anchors), 1)
        a = ev.anchors[0]
        wycinek = bloki[0]["text"][a.span[0]:a.span[1]]
        self.assertEqual(E.normalize(wycinek), E.normalize("Okręgowy w Łodzi"))


# ---------------------------------------------------------------------------
# 7. Gating dwuosiowy na poziomie kontraktu (pewnosc x ugruntowanie)
# ---------------------------------------------------------------------------
class TestGatingDwuosiowy(unittest.TestCase):
    @staticmethod
    def _blok(bid, conf, bbox):
        return C.Block(id=bid, page=1, bbox=bbox, block_type="paragraph",
                       text="tresc", confidence=conf, flags=[])

    def _kontrakt(self, blocks):
        return C.build_contract(blocks, engine="pdftotext", raw=b"x")

    def test_blok_pewny_ale_niecytowalny_jest_widoczny(self):
        """confidence 0.99 + bbox None: 1.1.0 mowilo auto_approved i tyle."""
        g = self._kontrakt([self._blok("b1", 0.99, None)])["gating"]
        self.assertIn("b1", g["auto_approved"])      # os pewnosci: przechodzi
        self.assertIn("b1", g["ungroundable"])       # os ugruntowania: nie
        self.assertEqual(g["verdict"], "degraded")

    def test_osie_moga_sie_rozjechac_w_obie_strony(self):
        g = self._kontrakt([
            self._blok("pewny_niecytowalny", 0.99, None),
            self._blok("niepewny_cytowalny", 0.10, [0, 0, 1, 1]),
        ])["gating"]
        self.assertEqual(g["auto_approved"], ["pewny_niecytowalny"])
        self.assertEqual(g["review_required"], ["niepewny_cytowalny"])
        self.assertEqual(g["ungroundable"], ["pewny_niecytowalny"])

    def test_pusta_lista_blokow_to_failed_nie_ok(self):
        """Bramka z pusta lista przechodzi zawsze - tu nie moze."""
        g = self._kontrakt([])["gating"]
        self.assertEqual(g["verdict"], "failed")
        self.assertEqual(g["counts"]["total"], 0)
        self.assertNotEqual(g["verdict"], "ok")

    def test_wszystko_pewne_i_ugruntowane_to_ok(self):
        g = self._kontrakt([self._blok("b1", 0.99, [0, 0, 1, 1])])["gating"]
        self.assertEqual(g["verdict"], "ok")

    def test_werdykt_ma_kod_wyjscia_zgodny_z_routing_gate(self):
        self.assertEqual(C.GATING_EXIT, {"ok": 0, "degraded": 10, "failed": 20})

    def test_mianownik_sie_zgadza(self):
        blocks = [self._blok("b%d" % i, 0.9 if i % 2 else 0.1,
                             [0, 0, 1, 1] if i % 3 else None) for i in range(9)]
        g = self._kontrakt(blocks)["gating"]
        self.assertEqual(g["counts"]["total"], 9)
        self.assertEqual(g["counts"]["review_required"] + g["counts"]["auto_approved"], 9)
        self.assertEqual(g["counts"]["ungroundable"], len(g["ungroundable"]))

    def test_kontrakt_z_nowym_gatingiem_przechodzi_walidacje_schematu(self):
        k = self._kontrakt([self._blok("b1", 0.99, [0, 0, 1, 1])])
        self.assertEqual(C.validate(k), [])

    def test_schemat_wymaga_nowych_pol(self):
        """Schemat musi WYMAGAC nowych pol, inaczej stary produkt przejdzie."""
        k = self._kontrakt([self._blok("b1", 0.99, [0, 0, 1, 1])])
        del k["gating"]["verdict"]
        self.assertTrue(C.validate(k), "brak verdict musi byc bledem walidacji")

    def test_wersja_kontraktu_podniesiona(self):
        self.assertEqual(C.CONTRACT_VERSION.split(".")[:2], ["1", "2"])


class TestBezSieci(unittest.TestCase):
    def test_zero_importow_sieciowych(self):
        for mod in ("evidence.py", "grounding_bridge.py"):
            src = io.open(os.path.join(_ROOT, "scripts", mod), encoding="utf-8").read()
            for f in ("socket", "urllib", "requests", "httpx"):
                self.assertNotIn("import %s" % f, src, "%s importuje %s" % (mod, f))

    def test_evidence_bez_zaleznosci_zewnetrznych(self):
        src = io.open(os.path.join(_ROOT, "scripts", "evidence.py"), encoding="utf-8").read()
        for line in src.splitlines():
            s = line.strip()
            if s.startswith("import ") or s.startswith("from "):
                self.assertTrue(
                    any(s.startswith(p) for p in
                        ("import unicodedata", "from dataclasses", "from __future__")),
                    "nieoczekiwany import: %s" % s,
                )


if __name__ == "__main__":
    unittest.main()
