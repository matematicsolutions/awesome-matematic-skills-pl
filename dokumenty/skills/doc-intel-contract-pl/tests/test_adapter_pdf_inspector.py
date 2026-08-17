"""Testy adaptera pdf-inspector (szczebel 1.5).

Zero-dep: fixtury to syntetyczny JSON w formacie `pdfi_extract.py`, wiec testy
nie potrzebuja ani biblioteki, ani prawdziwego PDF. Wartosci wspolrzednych
odtwarzaja ZMIERZONY uklad: TextItem przychodzi w ukladzie PDF (origin lewy-DOL),
kontrakt wymaga lewy-GORA.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
from adapters import pdf_inspector as pdfi  # noqa: E402

A4 = [595.0, 842.0]


def _item(page=1, x=50.0, y=800.0, w=100.0, h=10.0, text="tresc", fs=10.0, bold=False):
    return {"page": page, "x": x, "y": y, "width": w, "height": h,
            "text": text, "font_size": fs, "is_bold": bold, "item_type": "text"}


def _doc(items, **kw):
    d = {"engine": "pdf-inspector", "pdf_type": "text_based", "page_count": 1,
         "page_size": A4, "confidence": 1.0, "has_encoding_issues": False,
         "pages_needing_ocr": [], "ocr_reasons_by_page": {},
         "pages_with_tables": [], "pages_with_columns": [], "items": items}
    d.update(kw)
    return d


def test_strona_do_ocr_dostaje_jawny_blok_zamiast_ciszy():
    """Rdzen adaptera: nieczytelna strona NIE MOZE zniknac z kontraktu."""
    d = _doc([], page_count=3, pages_needing_ocr=[2],
             ocr_reasons_by_page={"2": ["scanned"]})
    blocks = pdfi.to_blocks(d)
    ocr = [b for b in blocks if "needs_ocr" in b.flags]
    assert len(ocr) == 1
    b = ocr[0]
    assert b.page == 2 and b.text == "" and b.confidence == 0.0
    assert "scanned" in b.flags and "partial" in b.flags
    assert b.block_type == "unknown"


def test_confidence_zero_kieruje_strone_ocr_do_czlowieka():
    """confidence 0.0 < prog 0.85 -> blok musi wpasc do review_required."""
    from contract import build_contract
    d = _doc([], page_count=1, pages_needing_ocr=[1],
             ocr_reasons_by_page={"1": ["scanned"]})
    c = build_contract(pdfi.to_blocks(d), engine="pdf-inspector", raw=b"{}", pages=1)
    assert c["gating"]["review_required"] == ["b0001"]
    assert c["gating"]["auto_approved"] == []


def test_bbox_jest_normalizowany_i_odwraca_os_y():
    """y=800,h=10 przy H=842 -> gora strony, czyli y0 blisko 0."""
    blocks = pdfi.to_blocks(_doc([_item(y=800.0, h=10.0, x=0.0, w=595.0)]))
    x0, y0, x1, y1 = blocks[0].bbox
    assert (x0, x1) == (0.0, 1.0)
    assert abs(y0 - (842 - 810) / 842) < 1e-4      # gorna krawedz
    assert abs(y1 - (842 - 800) / 842) < 1e-4
    assert y0 < y1 < 0.1                            # naprawde przy gorze


def test_bez_wymiarow_strony_nie_ma_bbox_tylko_flaga():
    """Konwencja skillu: zadnych wspolrzednych z sufitu."""
    blocks = pdfi.to_blocks(_doc([_item()], page_size=None))
    assert blocks[0].bbox is None
    assert "partial" in blocks[0].flags


def test_przerwa_pionowa_dzieli_bloki():
    items = [_item(y=800.0, text="linia 1"), _item(y=788.0, text="linia 2"),
             _item(y=600.0, text="daleko nizej")]
    blocks = pdfi.to_blocks(_doc(items))
    assert len(blocks) == 2
    assert blocks[0].text == "linia 1\nlinia 2"
    assert blocks[1].text == "daleko nizej"


def test_naglowek_i_stopka_po_polozeniu():
    top = pdfi.to_blocks(_doc([_item(y=820.0, h=10.0, text="Strona 1 z 4")]))
    bottom = pdfi.to_blocks(_doc([_item(y=10.0, h=8.0, text="stopka")]))
    assert top[0].block_type == "header"
    assert bottom[0].block_type == "footer"


def test_tytul_po_pogrubieniu():
    items = [_item(y=500.0, text="POSTANOWIENIE", bold=True)]
    assert pdfi.to_blocks(_doc(items))[0].block_type == "title"


def test_bledy_kodowania_scinaja_confidence_i_dodaja_flage():
    """Tekst jest, ale moze byc przeklamany - ma trafic pod prog, nie udawac pewnego."""
    blocks = pdfi.to_blocks(_doc([_item()], has_encoding_issues=True))
    assert blocks[0].confidence == 0.5
    assert "encoding_issues" in blocks[0].flags


def test_tabela_jest_cecha_strony_a_nie_typem_bloku():
    blocks = pdfi.to_blocks(_doc([_item()], pages_with_tables=[1]))
    assert "page_has_table" in blocks[0].flags
    assert blocks[0].block_type != "table"   # nie zgadujemy typu z cechy strony


def test_bbox_available_rozpoznaje_brak_wymiarow():
    """Sygnal dla operatora: bez wymiarow strony nie ma groundingu cytatu."""
    assert pdfi.bbox_available(_doc([_item()])) is True
    assert pdfi.bbox_available(_doc([_item()], page_size=None)) is False


def test_brak_bbox_nie_wpycha_wszystkiego_do_kolejki_czlowieka():
    """Degradacja ZDOLNOSCI != degradacja TRESCI. Blok ma flage, ale tekst jest pewny.
    Wpychanie setek blokow do review nauczyloby kolejke ignorowac (linia Goodharta)."""
    from contract import build_contract
    blocks = pdfi.to_blocks(_doc([_item(y=800.0), _item(y=500.0)], page_size=None))
    c = build_contract(blocks, engine="pdf-inspector", raw=b"{}", pages=1)
    assert all("partial" in b.flags for b in blocks)
    assert c["gating"]["review_required"] == []


def test_ocr_gap_i_page_count():
    d = _doc([], page_count=10, pages_needing_ocr=[3, 7])
    assert pdfi.ocr_gap(d) == (2, 10)
    assert pdfi.page_count(d) == 10


def test_zle_wejscie_jest_glosne():
    import pytest
    with pytest.raises(ValueError):
        pdfi.to_blocks({"cos": "innego"})
