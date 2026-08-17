"""Testy bramki routingu.

Fixtury OOXML sa budowane w pamieci i ODTWARZAJA ZMIERZONY DEFEKT: 2026-08-08
anydoc dostal .docx z jednym uszkodzonym `word/charts/chart1.xml`, zwrocil exit 0
i pusty stderr (przy RUST_LOG=trace), a z wyjscia znikla cala tabela danych.
Test pilnuje, ze nasza bramka tego nie przepusci.

Testy PDF wymagaja pakietu `pdf-inspector` i sa pomijane, gdy go brak - ale
brak pakietu w SCIEZCE PRODUKCYJNEJ musi dawac `failed`, i to jest testowane
osobno (test_pdf_bez_biblioteki_nie_przepuszcza).
"""
from __future__ import annotations

import io
import os
import sys
import zipfile

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import routing_gate as rg  # noqa: E402

GOOD_XML = b'<?xml version="1.0"?><root><a>tresc</a></root>'
BROKEN_XML = b'<?xml version="1.0"?><c:chartSpace><UNCLOSED'


def _docx(tmp_path, parts: dict[str, bytes], name="pismo.docx") -> str:
    path = tmp_path / name
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for part, data in parts.items():
            z.writestr(part, data)
    return str(path)


def test_ooxml_poprawny_daje_ok(tmp_path):
    p = _docx(tmp_path, {"[Content_Types].xml": GOOD_XML, "word/document.xml": GOOD_XML})
    v = rg.check(p)
    assert v["status"] == rg.STATUS_OK
    assert v["coverage"] == {"unit": "parts", "total": 2, "usable": 2}


def test_uszkodzona_czesc_daje_degraded_i_nazywa_ja(tmp_path):
    """Dokladnie ten przypadek, ktory anydoc polyka bez slowa."""
    p = _docx(tmp_path, {
        "[Content_Types].xml": GOOD_XML,
        "word/document.xml": GOOD_XML,
        "word/charts/chart1.xml": BROKEN_XML,
    })
    v = rg.check(p)
    assert v["status"] == rg.STATUS_DEGRADED
    assert v["coverage"]["total"] == 3 and v["coverage"]["usable"] == 2
    assert v["reasons"][0]["code"] == "malformed_part"
    # Pelny mianownik i NAZWA czesci - inaczej raport jest bezuzyteczny.
    assert "word/charts/chart1.xml" in v["reasons"][0]["detail"]
    assert "3" in v["reasons"][0]["detail"]


def test_paczka_nie_bedaca_zipem_daje_failed(tmp_path):
    p = tmp_path / "nie-paczka.docx"
    p.write_bytes(b"to nie jest zip")
    v = rg.check(str(p))
    assert v["status"] == rg.STATUS_FAILED
    assert v["reasons"][0]["code"] == "bad_package"


def test_legacy_doc_trafia_na_szczebel_anydoc(tmp_path):
    p = tmp_path / "wyrok.doc"
    p.write_bytes(b"\xd0\xcf\x11\xe0")  # sygnatura OLE
    v = rg.check(str(p))
    assert v["status"] == rg.STATUS_OK
    assert v["route"]["rung"] == rg.RUNG_ANYDOC


def test_nieznany_format_nie_jest_cicho_przepuszczany(tmp_path):
    p = tmp_path / "cos.xyz"
    p.write_bytes(b"x")
    v = rg.check(str(p))
    assert v["status"] == rg.STATUS_FAILED
    assert v["reasons"][0]["code"] == "unknown_format"


def test_brak_pliku_daje_failed():
    v = rg.check("nie-ma-takiego-pliku.pdf")
    assert v["status"] == rg.STATUS_FAILED
    assert v["reasons"][0]["code"] == "not_a_file"


def test_pdf_bez_biblioteki_nie_przepuszcza(tmp_path, monkeypatch):
    """Brak bramki NIE moze konczyc sie zgadywaniem - ma konczyc sie failed."""
    p = tmp_path / "akta.pdf"
    p.write_bytes(b"%PDF-1.7\n")
    monkeypatch.setitem(sys.modules, "pdf_inspector", None)  # wymusza ImportError
    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__

    def fake_import(name, *a, **kw):
        if name == "pdf_inspector":
            raise ImportError("wymuszone")
        return real_import(name, *a, **kw)

    monkeypatch.setattr("builtins.__import__", fake_import)
    v = rg.check(str(p))
    assert v["status"] == rg.STATUS_FAILED
    assert v["reasons"][0]["code"] == "gate_unavailable"


def test_kody_wyjscia_sa_stabilne():
    """CI branchuje na tych liczbach - zmiana lamie kazdego konsumenta."""
    assert rg.EXIT == {"ok": 0, "degraded": 10, "failed": 20}


def _ma_pdf_inspector() -> bool:
    try:
        import pdf_inspector  # noqa: F401
        return True
    except ImportError:
        return False


@pytest.mark.skipif(not _ma_pdf_inspector(), reason="brak pdf-inspector")
def test_pdf_smieciowy_daje_failed_a_nie_wyjatek(tmp_path):
    p = tmp_path / "smieci.pdf"
    p.write_bytes(b"%PDF-1.7\nto nie jest prawdziwy pdf\n")
    v = rg.check(str(p))
    assert v["status"] == rg.STATUS_FAILED
