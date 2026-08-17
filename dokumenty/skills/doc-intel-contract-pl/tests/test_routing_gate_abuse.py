"""Fixtury naduzyc dla bramki routingu (wzorzec: firecrawl/anydoc tests/fixtures/abuse).

Bramka otwiera pliki Z ZEWNATRZ - z sadu, od klienta, z zalacznika maila. Kazdy
limit musi miec fixture, ktora go WYWOLUJE, inaczej limit jest deklaracja, nie
zabezpieczeniem (regula: "regula bez bramki nie trzyma" - tu w wersji "limit bez
fixtury nie trzyma").

Fixtury sa generowane w pamieci - zadnych zlosliwych plikow na dysku WM.
Kazdy test sprawdza JEDEN limit i oczekuje `failed` + nazwy limitu, bo tylko
nazwany limit da sie pozniej dyskutowac i podniesc.
"""
from __future__ import annotations

import os
import sys
import zipfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import routing_gate as rg  # noqa: E402

OK_XML = b'<?xml version="1.0"?><root><a>tresc</a></root>'


def _zip(path, parts: dict[str, bytes], compress=zipfile.ZIP_DEFLATED):
    with zipfile.ZipFile(path, "w", compress) as z:
        for name, data in parts.items():
            z.writestr(name, data)
    return str(path)


def _limit_of(v):
    return v["reasons"][0].get("limit")


def test_bomba_zip_lapana_po_wspolczynniku_dekompresji(tmp_path):
    """1 MB zer pakuje sie ~1000x - to nie jest ksztalt dokumentu."""
    p = _zip(tmp_path / "bomba.docx", {"[Content_Types].xml": OK_XML,
                                       "word/document.xml": b"\x00" * (1024 * 1024)})
    v = rg.check(p)
    assert v["status"] == rg.STATUS_FAILED
    assert _limit_of(v) == "max_expansion_ratio"


def test_bomba_encji_odrzucana_przed_parsowaniem(tmp_path):
    """billion laughs: ElementTree rozwija encje wewnetrzne, wiec nie dajemy mu szansy."""
    evil = (b'<?xml version="1.0"?><!DOCTYPE lolz [<!ENTITY lol "lol">'
            b'<!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">'
            b']><lolz>&lol2;</lolz>')
    p = _zip(tmp_path / "encje.docx", {"[Content_Types].xml": OK_XML, "word/document.xml": evil})
    v = rg.check(p)
    assert v["status"] == rg.STATUS_FAILED
    assert _limit_of(v) == "entity_declaration"


def test_za_duzo_wpisow(tmp_path, monkeypatch):
    monkeypatch.setattr(rg, "MAX_ENTRY_COUNT", 5)
    parts = {f"word/p{i}.xml": OK_XML for i in range(9)}
    v = rg.check(_zip(tmp_path / "duzo.docx", parts))
    assert v["status"] == rg.STATUS_FAILED
    assert _limit_of(v) == "max_entry_count"


def test_pojedyncza_czesc_za_duza(tmp_path, monkeypatch):
    monkeypatch.setattr(rg, "MAX_ENTRY_BYTES", 1024)
    monkeypatch.setattr(rg, "MAX_EXPANSION_RATIO", 10**9)  # izolujemy JEDEN limit
    p = _zip(tmp_path / "gruba.docx", {"word/document.xml": b"a" * 4096})
    v = rg.check(p)
    assert v["status"] == rg.STATUS_FAILED
    assert _limit_of(v) == "max_entry_bytes"


def test_laczny_rozmiar_za_duzy(tmp_path, monkeypatch):
    monkeypatch.setattr(rg, "MAX_TOTAL_BYTES", 2048)
    monkeypatch.setattr(rg, "MAX_EXPANSION_RATIO", 10**9)
    parts = {f"word/p{i}.xml": b"a" * 900 for i in range(4)}
    v = rg.check(_zip(tmp_path / "suma.docx", parts))
    assert v["status"] == rg.STATUS_FAILED
    assert _limit_of(v) == "max_total_bytes"


def test_zwykly_dokument_nie_jest_falszywie_blokowany(tmp_path):
    """Kontrola przeciwna: limity nie moga blokowac normalnych pism."""
    parts = {"[Content_Types].xml": OK_XML,
             "word/document.xml": b'<?xml version="1.0"?><d>' + b"tresc pisma. " * 500 + b"</d>",
             "word/styles.xml": OK_XML}
    v = rg.check(_zip(tmp_path / "pismo.docx", parts))
    assert v["status"] == rg.STATUS_OK


def test_limity_sa_nazwane_i_dodatnie():
    """Limit bez nazwy jest nieuzywalny w rozmowie o incydencie."""
    for n in ("MAX_ENTRY_COUNT", "MAX_ENTRY_BYTES", "MAX_TOTAL_BYTES", "MAX_EXPANSION_RATIO"):
        assert getattr(rg, n) > 0
