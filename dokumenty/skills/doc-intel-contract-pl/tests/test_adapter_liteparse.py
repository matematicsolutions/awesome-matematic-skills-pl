"""Testy adaptera liteparse (OCR skanow na CPU).

Zero-dep: fixtury to syntetyczny JSON w formacie `liteparse_extract.py`. Kazdy test
odtwarza ZMIERZONE zachowanie biblioteki (liteparse 2.14.6, 2026-09-21), nie teze.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from adapters import liteparse as ltp  # noqa: E402
from contract import build_contract, validate  # noqa: E402


def _w(text, x, y, conf=0.96, w=None, h=10.0):
    return {"text": text, "x": x, "y": y, "w": w or 6.0 * len(text), "h": h, "conf": conf}


def _page(num, items, image=True, blocks=None, residual=0):
    return {"number": num, "width": 595.0, "height": 842.0, "text": " ".join(i["text"] for i in items),
            "image": image, "full_page_image": image, "ocr": any(i["conf"] is not None for i in items),
            "items": items, "blocks": blocks or [], "residual_alnum": residual}


def _doc(pages, total=None):
    return {"parser": {"name": "liteparse"}, "total_pages": total if total is not None else len(pages),
            "page_errors": [], "warnings": [], "pages": pages}


def test_obciete_strony_dostaja_jawne_bloki_missing_page():
    """Zmierzone: domyslny limit 1000 stron, page_errors=0. Brak strony nie moze byc cisza."""
    d = _doc([_page(1, [_w("Sygn.", 60, 40)])], total=3)
    blocks = ltp.to_blocks(d)
    missing = [b for b in blocks if "missing_page" in b.flags]
    assert [b.page for b in missing] == [2, 3]
    assert all(b.confidence == 0.0 for b in missing)
    assert ltp.coverage(d) == (1, 3)


def test_strona_z_obrazem_bez_tekstu_jest_nieczytelna_a_nie_pusta():
    d = _doc([_page(1, [], image=True), _page(2, [], image=False)])
    blocks = ltp.to_blocks(d)
    assert len(blocks) == 1 and blocks[0].page == 1
    assert {"needs_ocr", "unreadable"} <= set(blocks[0].flags)


def test_paragraf_czytany_jako_dolar_naprawiony_z_flaga():
    d = _doc([_page(1, [_w("art.", 60, 100), _w("410", 90, 100), _w("$", 115, 100),
                        _w("2", 122, 100), _w("i", 130, 100), _w("$", 138, 100), _w("la", 146, 100)])])
    b = ltp.to_blocks(d)[0]
    assert "§ 2" in b.text and "§ 1a" in b.text and "$" not in b.text
    assert "repaired_paragraf" in b.flags


def test_dolar_bez_liczby_zostaje():
    fixed, n = ltp.repair_paragraf("kwota w $ USD oraz $")
    assert n == 0 and fixed == "kwota w $ USD oraz $"


def test_tekst_natywny_nie_dostaje_pewnosci_z_sufitu():
    d = _doc([_page(1, [_w("Sygn. akt II K 1/24", 60, 40, conf=None)], image=False)])
    b = ltp.to_blocks(d)[0]
    assert b.confidence is None and "native_text" in b.flags
    fixed = ltp.to_blocks(_doc([_page(1, [_w("$", 60, 40, conf=None), _w("2", 70, 40, conf=None)], image=False)]))[0]
    assert "$" in fixed.text, "naprawa paragrafu tylko dla OCR"


def test_pewnosc_bloku_to_niski_percentyl_a_slabe_slowo_ma_flage():
    words = [_w(f"slowo{i}", 60 + 40 * (i % 10), 100 + 12 * (i // 10), conf=0.97) for i in range(40)]
    words[5]["conf"] = 0.40
    b = ltp.to_blocks(_doc([_page(1, words)]))[0]
    assert b.confidence >= 0.9, "jedno slabe slowo nie wysyla calego akapitu do kolejki"
    assert "weak_word" in b.flags


def test_bloki_ukladu_uzyte_gdy_bezstratne_a_odrzucone_gdy_gubia_litery():
    items = [_w("WYROK", 250, 100), _w("Sad", 60, 140), _w("uznal", 90, 140)]
    lay = [{"kind": "heading", "text": "WYROK", "bbox": [250, 100, 30, 10]},
           {"kind": "paragraph", "text": "Sad uznal", "bbox": [60, 140, 60, 10]}]
    ok = ltp.to_blocks(_doc([_page(1, items, blocks=lay)]))
    assert [b.block_type for b in ok] == ["title", "paragraph"]
    lossy = ltp.to_blocks(_doc([_page(1, items, blocks=lay[:1], residual=8)]))
    assert all("layout_blocks_lossy" in b.flags for b in lossy)
    assert "uznal" in " ".join(b.text for b in lossy), "strata w blokach -> tekst z calej strony"


def test_kontrakt_liteparse_przechodzi_schemat():
    d = _doc([_page(1, [_w("UZASADNIENIE", 240, 90), _w("Sad", 60, 140)]), _page(2, [], image=True)])
    c = build_contract(ltp.to_blocks(d), engine="liteparse", raw=b"{}", pages=2)
    assert validate(c) == []
    assert c["gating"]["verdict"] != "ok", "strona nieczytelna nie moze dac zielonego"
