"""Testy podzialu teczki (split_packet.py).

Kazdy przypadek to ZMIERZONA pulapka z benchmarku 09-21 (teczki z publicznych
orzeczen, rozdzial dev/test), a nie teza. Zero-dep: strony jako tekst.
"""
from __future__ import annotations

import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(HERE, "scripts"))
import split_packet as sp  # noqa: E402

RULES = sp.load_rules(sp.DEFAULT_RULES)
PROSE = ("Sad zwazyl, co nastepuje. Zgodnie z utrwalona linia orzecznicza okreslenie wysokosci "
         "zadoscuczynienia stanowi uprawnienie sadu merytorycznie rozstrzygajacego sprawe.\n") * 6


def _p(n, text, image=False):
    return {"number": n, "text": text, "image": image}


def _starts(res):
    return [s["pages"][0] for s in res["segments"]]


def test_pokrycie_kazda_strona_dokladnie_raz():
    pages = [_p(1, "Sygn. akt II K 1/24\nWYROK\n" + PROSE), _p(2, PROSE), _p(3, "Sygn. akt II K 9/23\nPOSTANOWIENIE\n" + PROSE)]
    res = sp.split(pages, RULES)
    assert [p for s in res["segments"] for p in s["pages"]] == [1, 2, 3]
    assert res["coverage"] == {"unit": "pages", "total": 3, "assigned": 3}


def test_dwa_sasiednie_pisma_tej_samej_kategorii_to_dwa_segmenty():
    pages = [_p(1, "Sygn. akt III KK 1/22\nPOSTANOWIENIE\n" + PROSE + "SSN Jan Nowak"),
             _p(2, "Sygn. akt III KK 7/22\nPOSTANOWIENIE\n" + PROSE)]
    res = sp.split(pages, RULES)
    assert _starts(res) == [1, 2]
    assert [s["category"] for s in res["segments"]] == ["postanowienie", "postanowienie"]


def test_sygnatura_cytowana_w_prozie_nie_otwiera_pisma():
    """Dev 09-21: 43 z ~100 falszywych granic = cudza sygnatura/data w zdaniu."""
    pages = [_p(1, "Sygn. akt I C 5/20\nWYROK\n" + PROSE),
             _p(2, "Postanowieniem z dnia 25 lipca 2001 r., sygn. akt VI GCo 134/01, Sad Rejonowy nadal klauzule.\n" + PROSE)]
    assert _starts(sp.split(pages, RULES)) == [1]


def test_uzasadnienie_w_srodku_strony_pod_sentencja_to_nie_nowe_pismo():
    pages = [_p(1, "Sygn. akt II K 3/21\nWYROK\n" + PROSE),
             _p(2, "IV.\nna podstawie art. 627 kpk zasadza koszty\nUZASADNIENIE\nSygn. akt II K 3/21\n" + PROSE)]
    assert _starts(sp.split(pages, RULES)) == [1]


def test_uzasadnienie_w_pierwszej_linii_otwiera_pismo_z_flaga_przegladu():
    """Dev 09-21: naglowek w 1. linii bez sygnatury = poczatek pisma w 11 z 12."""
    pages = [_p(1, "Sygn. akt II K 3/21\nWYROK\n" + PROSE + "Przewodniczacy SSR Anna Kowalska"),
             _p(2, "UZASADNIENIE\nSad Okregowy wyrokiem z dnia 19 lutego 2016 r. uznal oskarzona za winna.\n" + PROSE)]
    res = sp.split(pages, RULES)
    assert _starts(res) == [1, 2]
    assert res["status"] == "degraded", "decyzja z jednego sygnalu idzie do oka"


def test_powtorzony_naglowek_formularza_to_stopka_nie_nowe_pismo():
    head = "UZASADNIENIE\nFormularz UK 2\nSygnatura akt\nVI Ka 1249/21\n"
    pages = [_p(1, head + PROSE), _p(2, head + PROSE)]
    assert _starts(sp.split(pages, RULES)) == [1]


def test_strona_nieczytelna_to_failed_nie_kategoria_inne():
    pages = [_p(1, "Sygn. akt II K 1/24\nWYROK\n" + PROSE), _p(2, "", image=True)]
    res = sp.split(pages, RULES)
    assert res["status"] == "failed"
    assert any(r["code"] == "pages_unreadable" for r in res["reasons"])


def test_pusta_strona_zostaje_w_segmencie_i_nie_otwiera_pisma():
    pages = [_p(1, "Sygn. akt II K 1/24\nWYROK\n" + PROSE), _p(2, "", image=False), _p(3, PROSE)]
    res = sp.split(pages, RULES)
    assert res["segments"][0]["pages"] == [1, 2, 3]
    assert res["status"] == "degraded"


def test_puste_wejscie_i_puste_reguly_blokuja(tmp_path):
    assert sp.split([], RULES)["status"] == "failed"
    empty = tmp_path / "r.json"
    empty.write_text(json.dumps({"categories": []}), encoding="utf-8")
    with pytest.raises(ValueError):
        sp.load_rules(str(empty))


def test_kontrola_pozytywna_bramka_widziana_na_czerwono():
    """Zlamany niezmiennik pokrycia musi dac failed - bramki bez czerwieni nie ma."""
    pages = [_p(1, "Sygn. akt II K 1/24\nWYROK\n" + PROSE), _p(2, PROSE)]
    orig = sp.build_segments
    try:
        sp.build_segments = lambda d: [{"id": "pismo-001", "category": "wyrok", "pages": [1],
                                        "heading": None, "sygnatura": None}]
        res = sp.split(pages, RULES)
    finally:
        sp.build_segments = orig
    assert res["status"] == "failed"
    assert any(r["code"] == "coverage_violation" for r in res["reasons"])


def test_cli_kod_wyjscia(tmp_path):
    f = tmp_path / "strony.json"
    f.write_text(json.dumps({"pages": [_p(1, "Sygn. akt II K 1/24\nWYROK\n" + PROSE), _p(2, "", image=True)]}),
                 encoding="utf-8")
    assert sp.main([str(f), "--bez-decyzji"]) == 20


def test_obciecie_przez_parser_to_failed_a_nie_komplet():
    """Przebieg 09-21: parser zwrocil mniej stron niz ma zrodlo, a pokrycie liczone od
    zwroconych stron zglosilo komplet. Mianownik zrodla musi wygrac."""
    pages = [_p(1, "Sygn. akt II K 1/24\nWYROK\n" + PROSE), _p(2, PROSE)]
    res = sp.split(pages, RULES, total_pages=5)
    assert res["status"] == "failed"
    assert res["coverage"]["total"] == 5 and res["coverage"]["assigned"] == 2
    assert any("NIEPELNY" in r["detail"] for r in res["reasons"])


def test_sciezka_pdf_uzywa_ekstraktora_z_jawnym_limitem():
    """Straznik max_pages zyje w liteparse_extract - druga sciezka nie moze go omijac."""
    import inspect
    src = inspect.getsource(sp.pages_from_pdf)
    assert "liteparse_extract" in src and "LiteParse(" not in src
