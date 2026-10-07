"""Testy bramki lokatorow. Akta w fixtures sa fikcyjne (sprawa Beta v Alfa)."""
import copy
import csv
import json
import sys
from pathlib import Path

import pytest

TU = Path(__file__).parent
sys.path.insert(0, str(TU.parent / "scripts"))
import bramka_lokatorow as b  # noqa: E402

AKTA = TU / "fixtures" / "akta-tekst"


def _wczytaj(nazwa):
    return json.loads((TU / "fixtures" / nazwa).read_text(encoding="utf-8"))


def _uruchom(tmp_path, dane, *extra):
    p = tmp_path / "wynik.json"
    p.write_text(json.dumps(dane, ensure_ascii=False), encoding="utf-8")
    return b.main([str(p), str(AKTA), *extra]), p


def _kody(p):
    return p.with_suffix(".bramka.md").read_text(encoding="utf-8")


# --- sciezki zielone ---

def test_chronologia_czysta_ok(tmp_path):
    rc, _ = _uruchom(tmp_path, _wczytaj("chronologia.json"))
    assert rc == b.OK


def test_zestawienie_czyste_ok(tmp_path):
    rc, _ = _uruchom(tmp_path, _wczytaj("zestawienie.json"))
    assert rc == b.OK


# --- kontrola pozytywna: bramka musi umiec byc czerwona ---

def test_pusta_lista_to_blokada(tmp_path):
    d = _wczytaj("chronologia.json"); d["wpisy"] = []
    rc, p = _uruchom(tmp_path, d)
    assert rc == b.BLOKADA and "PU01" in _kody(p)


def test_cytat_zmyslony_blokada(tmp_path):
    d = _wczytaj("chronologia.json")
    d["wpisy"][0]["zrodla"][0]["cytat"] = "pozwany uznal roszczenie w calosci"
    rc, p = _uruchom(tmp_path, d)
    assert rc == b.BLOKADA and "ZR09" in _kody(p)


def test_cytat_z_innej_strony_blokada_ze_wskazowka(tmp_path):
    d = _wczytaj("chronologia.json")
    d["wpisy"][3]["zrodla"][0]["strona"] = 3
    rc, p = _uruchom(tmp_path, d)
    raport = _kody(p)
    assert rc == b.BLOKADA and "ZR08" in raport and "na stronie 2" in raport


def test_brak_pliku_blokada(tmp_path):
    d = _wczytaj("chronologia.json")
    d["wpisy"][0]["zrodla"][0]["plik"] = "protokol-odbioru.pdf"
    rc, p = _uruchom(tmp_path, d)
    assert rc == b.BLOKADA and "ZR02" in _kody(p)


def test_strona_spoza_pliku_blokada(tmp_path):
    d = _wczytaj("chronologia.json")
    d["wpisy"][0]["zrodla"][0]["strona"] = 9
    rc, p = _uruchom(tmp_path, d)
    assert rc == b.BLOKADA and "ZR04" in _kody(p)


def test_data_nieistniejaca_blokada(tmp_path):
    d = _wczytaj("chronologia.json"); d["wpisy"][0]["data"] = "2024-02-30"
    rc, p = _uruchom(tmp_path, d)
    assert rc == b.BLOKADA and "DT03" in _kody(p)


def test_wpis_z_akt_bez_zrodla_blokada(tmp_path):
    d = _wczytaj("chronologia.json"); d["wpisy"][1]["zrodla"] = []
    rc, p = _uruchom(tmp_path, d)
    assert rc == b.BLOKADA and "ZR10" in _kody(p)


def test_postawa_B_wymaga_flagi_tajemnicy(tmp_path):
    d = _wczytaj("chronologia.json"); del d["wpisy"][2]["tajemnica"]
    rc, p = _uruchom(tmp_path, d)
    assert rc == b.BLOKADA and "SC01" in _kody(p)


def test_postawa_C_blokuje_calosc(tmp_path):
    d = _wczytaj("chronologia.json"); d["postawa_tajemnicy"] = "C"
    rc, p = _uruchom(tmp_path, d)
    assert rc == b.BLOKADA and "TJ01" in _kody(p)


def test_zdublowany_id_blokada(tmp_path):
    d = _wczytaj("chronologia.json"); d["wpisy"][1]["id"] = "Z1"
    rc, p = _uruchom(tmp_path, d)
    assert rc == b.BLOKADA and "SC04" in _kody(p)


def test_wykazane_bez_dowodu_blokada(tmp_path):
    d = _wczytaj("zestawienie.json"); d["elementy"][0]["dowody_za"] = []
    rc, p = _uruchom(tmp_path, d)
    assert rc == b.BLOKADA and "ST01" in _kody(p)


def test_stanowisko_bez_pisma_blokada(tmp_path):
    d = _wczytaj("zestawienie.json"); d["elementy"][1]["zrodla_stanowiska"] = []
    rc, p = _uruchom(tmp_path, d)
    assert rc == b.BLOKADA and "ST03" in _kody(p)


# --- UWAGI: wolno czytac, nie wolno cytowac bez sprawdzenia ---

def test_strona_nieczytelna_uwagi(tmp_path):
    d = _wczytaj("chronologia.json")
    d["wpisy"][2]["zrodla"].append({"plik": "korespondencja.txt", "strona": 2, "cytat": "cokolwiek z tej strony"})
    rc, p = _uruchom(tmp_path, d)
    assert rc == b.UWAGI and "ZR05" in _kody(p)


def test_cytat_bez_ogonkow_uwagi(tmp_path):
    d = _wczytaj("chronologia.json")
    d["wpisy"][2]["zrodla"][0]["cytat"] = "Wzywamy do niezwlocznego dostarczenia brakujacych 80 palet"
    rc, p = _uruchom(tmp_path, d)
    assert rc == b.UWAGI and "ZR07" in _kody(p)


def test_fakt_od_uzytkownika_uwagi(tmp_path):
    d = _wczytaj("chronologia.json")
    d["wpisy"].append({"id": "Z5", "data": "2024-05", "pewnosc_daty": "miesiac", "rodzaj_daty": "zdarzenia",
                       "kto": "Beta", "zdarzenie": "Rozmowa telefoniczna o blokadzie granicy.",
                       "waga": "tlo", "status": "relacja", "tajemnica": "do_przegladu",
                       "pochodzenie": "uzytkownik", "zrodla": []})
    rc, p = _uruchom(tmp_path, d)
    assert rc == b.UWAGI and "ZR11" in _kody(p)


def test_luka_z_dowodem_uwagi(tmp_path):
    d = _wczytaj("zestawienie.json")
    d["elementy"][2]["dowody_za"] = copy.deepcopy(d["elementy"][2]["twierdzenia"])
    rc, p = _uruchom(tmp_path, d)
    assert rc == b.UWAGI and "ST02" in _kody(p)


# --- CSV: cytat z akt przeciwnika nie moze stac sie formula ---

def test_csv_neutralizuje_formuly(tmp_path):
    d = _wczytaj("chronologia.json")
    d["wpisy"][0]["zdarzenie"] = '=HYPERLINK("http://example.invalid","x")'
    out = tmp_path / "chron.csv"
    rc, _ = _uruchom(tmp_path, d, "--csv", str(out))
    assert rc == b.OK
    wiersze = list(csv.reader(out.open(encoding="utf-8-sig"), delimiter=";"))
    assert wiersze[1][5].startswith("'=")


def test_na_ekran_nie_trafia_tresc_akt(tmp_path, capsys):
    _uruchom(tmp_path, _wczytaj("chronologia.json"))
    ekran = capsys.readouterr().out
    assert "palet" not in ekran and "Mianownik: 4 = 4 OK" in ekran
