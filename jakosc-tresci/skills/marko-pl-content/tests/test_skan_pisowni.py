"""Testy skanera pisowni 2026.

Kontrola pozytywna jest obowiazkowa: skaner, ktorego nie widzielismy na czerwono, nie jest
bramka. Dlatego obok syntetycznej starej pisowni lezy pietnascie bledow w stylu tekstu
wygenerowanego przez model - kazdy musi dac kandydata.
"""
from __future__ import annotations

import io
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import skan_pisowni as sp  # noqa: E402

FIX = Path(__file__).parent / "fixtures"


def _kandydaci(nazwa):
    ok, powod, k = sp.skanuj_plik(FIX / nazwa)
    assert ok, powod
    return k


def test_stara_pisownia_zapala_kazda_regule():
    reguly = {w["regula"] for w in _kandydaci("stara_pisownia.html")}
    assert reguly == {
        "R4_nie_imieslow", "R11_nie_stopien_wyzszy", "R11_nie_przymiotnik", "R11_nie_przyslowek",
        "R3_czyby_lacznie", "R1_mieszkaniec_mala_litera", "R6_pol_rozdzielnie", "R10_niby_quasi",
        "R9_przedrostek_lacznik", "R8c_obiekt_mala_litera", "R8e_nagroda_mala_litera",
    }


def test_nowa_pisownia_nie_daje_kandydatow():
    assert _kandydaci("nowa_pisownia.html") == []


def test_skrypt_w_html_jest_pomijany():
    trafienia = [w["kontekst"] for w in _kandydaci("stara_pisownia.html")]
    assert not any("skrypcie" in t for t in trafienia)


def test_numer_linii_przez_akapit_wieloliniowy():
    k = {w["trafienie"]: w["linia"] for w in _kandydaci("stara_pisownia.html")}
    assert k["nie działający"] == 3
    assert k["nie opisane"] == 4
    assert k["czyby"] == 6


def test_pietnascie_realistycznych_bledow():
    k = _kandydaci("bledy_realistyczne.md")
    assert len(k) == 15
    assert sorted(w["linia"] for w in k) == list(range(3, 18))
    assert {w["regula"] for w in k} <= {"R4_nie_imieslow", "R11_nie_stopien_wyzszy"}


def test_przeciwstawienie_zostaje_kandydatem_z_sygnalem():
    k = {w["trafienie"]: w for w in _kandydaci("poprawne_wyjatki.md")}
    for forma in ("nie darmowe", "nie techniczna", "nie zatwierdzony", "nie przesunięta"):
        assert forma in k, forma
        assert k[forma]["sygnal_przeciwstawienia"], forma


def test_zaimek_i_kod_nie_sa_kandydatami():
    k = _kandydaci("poprawne_wyjatki.md")
    assert not any(w["trafienie"] == "nie szybciej" for w in k)
    assert not any("działający" in w["trafienie"] for w in k)
    assert len(k) == 4


def test_czasownik_o_koncowce_imieslowu_nie_jest_kandydatem():
    # "nikt nie zapamieta" to czasownik, nie imieslow
    assert sp.skanuj([(1, "Nikt się nie obrazi, nikt nie zapamięta.")]) == []


def test_angielskie_zlozenia_nie_sa_kandydatami():
    seg = [(1, "Etap post-deployment, architektura multi-agent, faza pre-launch.")]
    assert sp.skanuj(seg) == []
    seg = [(1, "Po post-walidacji zapisujemy mini-bazę i pre-ustawiony próg.")]
    assert len(sp.skanuj(seg)) == 3


def test_przedrostek_na_poczatku_zdania_i_wielka_litera_po_laczniku():
    # przedrostek wielka litera na poczatku zdania to blad; wielka litera PO laczniku - poprawne (pkt 9a)
    assert len(sp.skanuj([(1, "Pre-ustawiony próg odcięcia.")])) == 1
    assert sp.skanuj([(1, "Tag #Cyber-Ubezpieczenia przy tomie.")]) == []


def test_obiekt_publiczny_bez_falszywki_na_angielskim():
    # angielskie "most AI" w pliku bez oznaczenia jezyka nie jest nazwa obiektu
    assert sp.skanuj([(1, "This region has most AI compute in one place.")]) == []
    assert len(sp.skanuj([(1, "Spotkanie przy most Poniatowskiego.")])) == 1


def test_strona_w_innym_jezyku_jest_pominieta_i_policzona(capsys):
    kod = sp.main([str(FIX / "angielski.html")])
    assert kod == 2
    assert "lang=en" in capsys.readouterr().out


def test_pusty_mianownik_to_blokada(tmp_path, capsys):
    assert sp.main([str(tmp_path)]) == 2
    assert "BLOKADA" in capsys.readouterr().out


def test_trojstan_kodu_wyjscia():
    assert sp.main([str(FIX / "nowa_pisownia.html")]) == 0
    assert sp.main([str(FIX / "stara_pisownia.html")]) == 1


def test_tekst_wklejony_przez_stdin(monkeypatch, capsys):
    monkeypatch.setattr(sys, "stdin", io.StringIO("Druga linia.\nDane nie sprawdzone przez nikogo."))
    assert sp.main(["-"]) == 1
    assert "<stdin>:2" in capsys.readouterr().out
