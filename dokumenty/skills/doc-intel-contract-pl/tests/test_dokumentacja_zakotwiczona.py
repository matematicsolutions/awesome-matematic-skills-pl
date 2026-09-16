# -*- coding: utf-8 -*-
"""KOTWICA DOKUMENTACJI: SKILL.md nie moze zdryfowac od kodu.

Mechanizm zabrany z docling-graph (MIT/IBM), gdzie `tests/test_architecture_doc.py`
importuje kazdy symbol z tabeli w ARCHITECTURE.md, a linter mapuje kazda regule
na akapit dokumentacji. U nas dotad kotwica byla miekka - "grep na main".
Tu jest twarda: dokumentacja jest
CZYTANA i konfrontowana z kodem, wiec nie da sie zmienic jednego bez drugiego.

Sprawdzane jest SIEDEM twierdzen SKILL.md:
  D1 numer wersji kontraktu (naglowek i przyklad JSON)
  D2 enum silnikow w przykladzie == enum w schemacie
  D3 tabela rodzajow dowodu == KIND_STRENGTH
  D4 tabela rozdzielczosci  == RESOLUTION_STRENGTH
  D5 kody wyjscia werdyktu  == contract.GATING_EXIT
  D6 flagi CLI z blokow bash sa znane parserowi
  D7 pliki i symbole wymienione w tekscie istnieja

Test celowo NIE sprawdza stylu prozy - tylko twierdzenia weryfikowalne
mechanicznie. Reszta zostaje dla czlowieka.
"""
import io
import os
import re
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

import contract as C  # noqa: E402
import evidence as E  # noqa: E402
import grounding_bridge as GB  # noqa: E402

_SKILL = io.open(os.path.join(_ROOT, "SKILL.md"), encoding="utf-8").read()


def _tabela_sil(naglowek_kolumny: str) -> dict:
    """Wyciagnij z SKILL.md pary `nazwa` -> sila z tabeli markdown.

    Szuka wierszy postaci:  | `nazwa` ... | <liczba> | ...
    w obrebie tabeli, ktorej naglowek zawiera `naglowek_kolumny`.
    """
    out = {}
    w_tabeli = False
    for line in _SKILL.splitlines():
        if naglowek_kolumny in line and line.strip().startswith("|"):
            w_tabeli = True
            continue
        if w_tabeli:
            if not line.strip().startswith("|"):
                break
            komorki = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(komorki) < 2:
                continue
            m_nazwa = re.search(r"`([a-z_]+)`", komorki[0])
            m_sila = re.fullmatch(r"\d+", komorki[1])
            if m_nazwa and m_sila:
                out[m_nazwa.group(1)] = int(m_sila.group(0))
    return out


class TestKotwicaDokumentacji(unittest.TestCase):

    def test_D1_wersja_kontraktu_zgodna(self):
        ver = C.CONTRACT_VERSION
        self.assertIn("## Kontrakt (v%s)" % ver, _SKILL,
                      "naglowek SKILL.md nie nadaza za CONTRACT_VERSION=%s" % ver)
        self.assertIn('"contract_version": "%s"' % ver, _SKILL,
                      "przyklad JSON w SKILL.md ma inna wersje niz kod")

    def test_D2_enum_silnikow_zgodny_ze_schematem(self):
        schemat = set(C.load_schema()["properties"]["source"]["properties"]["engine"]["enum"])
        m = re.search(r'"engine": "([a-z0-9|\-]+)"', _SKILL)
        self.assertIsNotNone(m, "brak przykladu enum silnikow w SKILL.md")
        udokumentowane = set(m.group(1).split("|"))
        self.assertEqual(
            udokumentowane, schemat,
            "SKILL.md wymienia inne silniki niz schemat: tylko_w_doc=%s tylko_w_schemacie=%s"
            % (udokumentowane - schemat, schemat - udokumentowane),
        )

    def test_D3_tabela_rodzajow_dowodu_zgodna_z_kodem(self):
        udok = _tabela_sil("rodzaj dowodu")
        self.assertTrue(udok, "nie znalazlem tabeli rodzajow dowodu w SKILL.md")
        self.assertEqual(
            udok, E.KIND_STRENGTH,
            "tabela `kind` w SKILL.md rozjechala sie z evidence.KIND_STRENGTH",
        )

    def test_D4_tabela_rozdzielczosci_zgodna_z_kodem(self):
        udok = _tabela_sil("rozdzielczosc")
        self.assertTrue(udok, "nie znalazlem tabeli rozdzielczosci w SKILL.md")
        self.assertEqual(
            udok, E.RESOLUTION_STRENGTH,
            "tabela `resolution` w SKILL.md rozjechala sie z evidence.RESOLUTION_STRENGTH",
        )

    def test_D5_kody_wyjscia_werdyktu_zgodne(self):
        m = re.search(r"`ok`/`degraded`/`failed` = `(\d+)`/`(\d+)`/`(\d+)`", _SKILL)
        self.assertIsNotNone(m, "SKILL.md nie podaje kodow wyjscia werdyktu")
        udok = {"ok": int(m.group(1)), "degraded": int(m.group(2)), "failed": int(m.group(3))}
        self.assertEqual(udok, C.GATING_EXIT)

    def test_D6_flagi_CLI_sa_znane_parserowi(self):
        """Kazda flaga `--x` pokazana przy grounding_bridge.py musi istniec."""
        znane = set()
        for akcja in GB.build_parser()._actions:
            znane.update(akcja.option_strings)
        udokumentowane = set()
        for blok in re.findall(r"```bash\n(.*?)```", _SKILL, re.S):
            for linia in blok.splitlines():
                # per LINIA, nie per blok: jeden blok bash miesza wywolania
                # roznych skryptow (normalize.py ma wlasne flagi)
                if "grounding_bridge.py" not in linia:
                    continue
                udokumentowane.update(re.findall(r"(--[a-z][a-z\-]*)", linia))
        self.assertTrue(udokumentowane, "brak przykladow CLI mostu w SKILL.md")
        nieznane = udokumentowane - znane
        self.assertFalse(nieznane, "SKILL.md pokazuje flagi, ktorych parser nie zna: %s" % nieznane)

    def test_D7_wymienione_pliki_istnieja(self):
        sciezki = set(re.findall(r"`(scripts/[a-z_]+\.py|tests/fixtures/[a-z_]+\.sample\.json)`", _SKILL))
        self.assertTrue(sciezki, "SKILL.md nie wymienia zadnych plikow")
        for rel in sorted(sciezki):
            self.assertTrue(os.path.exists(os.path.join(_ROOT, rel)),
                            "SKILL.md wskazuje nieistniejacy plik: %s" % rel)

    # Symbole, ktore SKILL.md nazywa wprost - musza istniec W OBIE STRONY:
    # nazwa w dokumentacji bez symbolu w kodzie i symbol bez opisu sa oba bledem.
    SYMBOLE_NAZWANE = [
        (C, "GATING_EXIT"),
        (C, "CONTRACT_VERSION"),
        (E, "normalize_with_map"),
        (GB, "gate"),
    ]
    # Publiczna powierzchnia, ktora musi ISTNIEC, ale nie musi byc nazwana
    # w prozie (opisana jest przez tabele albo przyklady CLI).
    SYMBOLE_PUBLICZNE = [
        (E, "KIND_STRENGTH"), (E, "RESOLUTION_STRENGTH"), (E, "locate"),
        (E, "Anchor"), (E, "Evidence"),
        (GB, "build_parser"), (GB, "build_task"), (GB, "BRIDGE_VERSION"),
    ]

    def test_D7b_symbole_nazwane_w_doc_istnieja_i_odwrotnie(self):
        for modul, symbol in self.SYMBOLE_NAZWANE:
            self.assertTrue(
                hasattr(modul, symbol),
                "%s.%s nazwany w SKILL.md, ale nie istnieje" % (modul.__name__, symbol),
            )
            self.assertIn(
                symbol, _SKILL,
                "%s istnieje w kodzie, ale SKILL.md przestal go nazywac" % symbol,
            )

    def test_D7c_publiczna_powierzchnia_istnieje(self):
        for modul, symbol in self.SYMBOLE_PUBLICZNE:
            self.assertTrue(
                hasattr(modul, symbol),
                "%s.%s zniknal z publicznej powierzchni" % (modul.__name__, symbol),
            )


def _policz_testy(kat: str) -> int:
    """Policz metody/funkcje testowe przez AST - zero-dep i deterministycznie.

    `unittest.discover` NIE widzi testow zapisanych jako funkcje modulowe
    (czesc naszych plikow tak je pisze), wiec dalby zanizona liczbe 166 tam,
    gdzie pytest zbiera 195. Mianownik podany w dokumentacji ma byc tym samym
    mianownikiem, ktory widzi narzedzie uruchamiajace.
    """
    import ast

    n = 0
    for nazwa in sorted(os.listdir(kat)):
        if not (nazwa.startswith("test_") and nazwa.endswith(".py")):
            continue
        drzewo = ast.parse(io.open(os.path.join(kat, nazwa), encoding="utf-8").read())
        for wezel in drzewo.body:
            if isinstance(wezel, (ast.FunctionDef, ast.AsyncFunctionDef)) and wezel.name.startswith("test"):
                n += 1
            elif isinstance(wezel, ast.ClassDef):
                n += sum(
                    1 for m in wezel.body
                    if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)) and m.name.startswith("test")
                )
    return n


class TestLicznikTestowNieGnije(unittest.TestCase):
    """SKILL.md od dawna glosil "83 testy zielone" przy realnych 195.

    Liczba w dokumentacji, ktorej nikt nie liczy, starzeje sie po cichu i
    zaczyna sluzyc za dowod czegos, co nieprawda. Tu jest liczona.
    """

    def test_liczba_testow_w_doc_zgodna_z_rzeczywistoscia(self):
        rzeczywista = _policz_testy(os.path.join(_ROOT, "tests"))
        m = re.search(r"\*\*(\d+) testow zielonych\*\*", _SKILL)
        self.assertIsNotNone(m, "SKILL.md nie podaje liczby testow w formacie '**N testow zielonych**'")
        self.assertEqual(
            int(m.group(1)), rzeczywista,
            "SKILL.md glosi %s testow, a jest %d" % (m.group(1), rzeczywista),
        )

    def test_licznik_widzi_obie_konwencje(self):
        """Kontrola pozytywna: licznik musi widziec i klasy, i funkcje modulowe."""
        self.assertGreater(_policz_testy(os.path.join(_ROOT, "tests")), 100)


class TestKotwicaSamaDziala(unittest.TestCase):
    """Kontrola POZYTYWNA: czy parser tabel w ogole cokolwiek widzi.

    Bramka, ktora nic nie znajduje, przechodzi zawsze - wiec sprawdzamy,
    ze mianownik jest niepusty i ma spodziewany rozmiar.
    """

    def test_parser_tabel_widzi_wszystkie_wiersze(self):
        self.assertEqual(len(_tabela_sil("rodzaj dowodu")), len(E.KIND_STRENGTH))
        self.assertEqual(len(_tabela_sil("rozdzielczosc")), len(E.RESOLUTION_STRENGTH))

    def test_parser_tabel_daje_pustke_na_nieistniejacym_naglowku(self):
        self.assertEqual(_tabela_sil("naglowek ktorego nie ma"), {})


if __name__ == "__main__":
    unittest.main()
