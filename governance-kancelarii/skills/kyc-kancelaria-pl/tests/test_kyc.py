"""Testy KYC kancelarii. Wszystkie dane w fixtures sa fikcyjne."""
import copy
import datetime as dt
import json
import sys
from pathlib import Path

import pytest

TU = Path(__file__).parent
F = TU / "fixtures"
sys.path.insert(0, str(TU.parent / "scripts"))
import bramka_kyc as b  # noqa: E402
import rejestry as r  # noqa: E402

DZIS = dt.date(2026, 10, 2)


def _sankcje(pobrano="2026-10-02T06:00:00", braki=()):
    wpisy = r.parsuj_onz((F / "un.xml").read_bytes()) + r.parsuj_ue((F / "eu.xml").read_bytes()) \
        + r.parsuj_mswia((F / "mswia.html").read_text(encoding="utf-8"))
    listy = {l: {"stan": "blad: URLError" if l in braki else "ok", "wpisow": 1} for l in ("ONZ", "UE", "MSWiA")}
    return {"meta": {"pobrano": pobrano, "listy": listy}, "wpisy": wpisy}


def _rejestry():
    return {"pobrano": "2026-10-01T09:00:00",
            "krs": r.parsuj_krs(json.loads((F / "krs-odpis.json").read_text(encoding="utf-8"))),
            "vat": r.parsuj_vat(json.loads((F / "vat.json").read_text(encoding="utf-8")))}


def _klient():
    return {
        "klient": {"typ": "spolka", "krs": "999001", "nazwa": "Delta Testowa Sp. z o.o."},
        "osoby_dzialajace": [{"osoba": "Anna Fikcyjna", "rola": "prezes"}, {"osoba": "Bogdan Przykładowy", "rola": "członek zarządu"}],
        "organ_pelne_dane": [{"osoba": "Anna Fikcyjna", "zrodlo": "odpis-krs.pdf s. 3"},
                             {"osoba": "Bogdan Przykładowy", "zrodlo": "odpis-krs.pdf s. 3"},
                             {"osoba": "Cezary Zawieszony", "zrodlo": "odpis-krs.pdf s. 3"}],
        "prokurenci_pelne_dane": [{"osoba": "Dorota Prokurencka", "zrodlo": "odpis-krs.pdf s. 4"}],
        "wspolnicy_pelne_dane": [{"osoba": "Łukasz Żółć", "zrodlo": "odpis-krs.pdf s. 2"}],
        "oswiadczenie_beneficjenci": {"zlozone": True, "beneficjenci": [{"osoba": "Łukasz Żółć", "obywatelstwo": "PL"}]},
        "crbr": {"data_wydruku": "2026-10-01", "beneficjenci": [{"osoba": "ZOLC LUKASZ", "obywatelstwo": "PL"}]},
        "pep": {"oswiadczenie_zlozone": True, "pep": False},
        "dokumenty_otrzymane": ["zlecenie_lub_pelnomocnictwo", "oswiadczenie_beneficjenci", "oswiadczenie_pep",
                                "wydruk_crbr", "dokument_tozsamosci_dzialajacego"],
    }


def _reguly(kraje=("IR", "KP")):
    d = json.loads(b.REGULY_DOMYSLNE.read_text(encoding="utf-8"))
    d["kraje_wysokiego_ryzyka"] = list(kraje)
    return d


def _ocen(klient=None, rejestry=None, sankcje=None, reguly=None):
    o, extra = b.ocen(klient or _klient(), rejestry or _rejestry(), sankcje or _sankcje(), reguly or _reguly(), DZIS)
    stany = {w["regula"]: w["_stan"] for w in o.wiersze}
    return o, extra, stany


# --- parsery i normalizacja ---

def test_parsery_list():
    s = _sankcje()["wpisy"]
    assert {(w["lista"], w["typ"]) for w in s} == {("ONZ", "osoba"), ("ONZ", "podmiot"), ("UE", "osoba"),
                                                   ("UE", "podmiot"), ("MSWiA", "osoba"), ("MSWiA", "podmiot")}
    assert not any("WYKRESLONY" in n for w in s for n in w["nazwy"]), "wykreslony z listy MSWiA nie moze byc aktywny"
    assert any("Тестович Ян" in w["nazwy"] for w in s), "transliteracja w nawiasie to alias"


def test_normalizacja_ogonki_kolejnosc_formy():
    assert r.normalizuj("Łukasz Żółć") == r.normalizuj("ZOLC LUKASZ")
    assert r.normalizuj("Sigma Sp. z o.o.", True) == r.normalizuj("SIGMA", True)


def test_krs_parser_widzi_maski_i_zawieszonego():
    k = _rejestry()["krs"]
    assert k["krs"] == "0000999001" and len(k["sklad"]) == 3 and k["sklad"][2]["zawieszona"] is True
    assert k["wspolnicy"] == ["Ł***** Ż***"] and all(r.zamaskowane(s["osoba"]) for s in k["sklad"])


def test_maska_krs():
    assert r.pasuje_do_maski("Anna Fikcyjna", "A*** F*******")
    assert r.pasuje_do_maski("Łukasz Żółć", "Ł***** Ż***")
    assert not r.pasuje_do_maski("Ana Fikcyjna", "A*** F*******"), "literowka w przepisaniu"
    assert not r.pasuje_do_maski("Anna Fikcyjna", "B*** F*******")
    assert r.pasuje_do_maski("Ewa Nowak-Kos", "E** N********"), "nazwisko z lacznikiem jako jedno pole"
    assert r.pasuje_do_maski("Ewa Nowak-Kos", "E** N**** K**"), "nazwisko dwuczlonowe jako dwa pola"


def test_szukaj_odmawia_maski():
    with pytest.raises(ValueError):
        r.szukaj("A*** F*******", _sankcje()["wpisy"])


# --- sciezka zielona i pelny mianownik ---

def test_czysty_klient_bez_zastrzezen():
    o, extra, stany = _ocen()
    assert o.stan == b.OK and extra["dyspozycja"] == "bez_zastrzezen"
    assert sorted(stany) == [f"R{i:02d}" for i in range(1, 14)], "kazda regula w raporcie, takze zdane"
    assert extra["osob_nieprzesianych"] == 0 and extra["osob_przesianych"] >= 6


# --- maskowanie KRS: brak pelnych danych to NIE przesiew ---

def test_bez_pelnych_danych_nieprzesiane_i_uzupelnij():
    k = _klient()
    for pole in ("organ_pelne_dane", "prokurenci_pelne_dane", "wspolnicy_pelne_dane"):
        k.pop(pole)
    o, extra, stany = _ocen(klient=k)
    assert stany["R13"] == b.UWAGI and stany["R08"] == b.UWAGI and stany["R04"] == b.UWAGI
    assert extra["osob_nieprzesianych"] == 5 and extra["dyspozycja"] == "uzupelnij"


def test_blad_przepisania_pelnych_danych_blokada():
    k = _klient(); k["organ_pelne_dane"][0]["osoba"] = "Ana Fikcyjna"
    o, extra, stany = _ocen(klient=k)
    assert stany["R13"] == b.BLOKADA


def test_czlonek_organu_na_liscie_tylko_przez_pelne_dane():
    rej = _rejestry()
    rej["krs"]["sklad"].append({"osoba": "I*** T*****", "funkcja": "CZŁONEK ZARZĄDU", "zawieszona": False})
    k = _klient(); k["organ_pelne_dane"].append({"osoba": "Ivan Testov", "zrodlo": "odpis-krs.pdf s. 3"})
    o, extra, stany = _ocen(klient=k, rejestry=rej)
    assert stany["R08"] == b.BLOKADA and any(t["rola"] == "organ" for t in extra["trafienia"])


def test_domyslne_reguly_wymagaja_konfiguracji_krajow():
    o, extra, stany = _ocen(reguly=_reguly(kraje=()))
    assert stany["R10"] == b.UWAGI and extra["dyspozycja"] == "uzupelnij"


# --- kontrola pozytywna: bramka musi umiec byc czerwona ---

def test_beneficjent_na_liscie_onz_blokada():
    k = _klient()
    k["oswiadczenie_beneficjenci"]["beneficjenci"].append({"osoba": "Testov Ivan", "obywatelstwo": "RU"})
    k["crbr"]["beneficjenci"].append({"osoba": "IVAN TESTOV", "obywatelstwo": "RU"})
    o, extra, stany = _ocen(klient=k)
    assert stany["R08"] == b.BLOKADA and extra["dyspozycja"] == "eskalacja"
    assert any(t["lista"] == "ONZ" and t["rodzaj"] == "dokladne" for t in extra["trafienia"])


def test_klient_podmiot_na_liscie_mswia_blokada():
    rej = _rejestry(); rej["krs"]["nazwa"] = "SIGMA SPÓŁKA Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ"
    o, extra, stany = _ocen(rejestry=rej)
    assert stany["R08"] == b.BLOKADA and any(t["lista"] == "MSWiA" for t in extra["trafienia"])


def test_podobne_nazwisko_uwagi():
    k = _klient()
    k["inne_osoby_do_przesiewu"] = [{"osoba": "Piotr Przykład"}]
    o, extra, stany = _ocen(klient=k)
    assert stany["R08"] == b.UWAGI and extra["trafienia"][0]["rodzaj"] == "podobne"


def test_rozbieznosc_crbr_blokada():
    k = _klient(); k["crbr"]["beneficjenci"] = [{"osoba": "Inna Osoba", "obywatelstwo": "PL"}]
    o, extra, stany = _ocen(klient=k)
    assert stany["R07"] == b.BLOKADA and extra["dyspozycja"] == "eskalacja"


def test_podpisujacy_spoza_organu_blokada():
    k = _klient(); k["osoby_dzialajace"] = [{"osoba": "Cezary Zawieszony", "rola": "czlonek zarzadu"}]
    o, extra, stany = _ocen(klient=k)
    assert stany["R04"] == b.BLOKADA, "zawieszony czlonek zarzadu nie reprezentuje"


def test_prokurent_samoistny_dziala_sam_ok():
    k = _klient(); k["osoby_dzialajace"] = [{"osoba": "Dorota Prokurencka", "rola": "prokurent"}]
    o, extra, stany = _ocen(klient=k)
    assert stany["R04"] == b.OK


def test_reprezentacja_laczna_jedna_osoba_uwagi():
    k = _klient(); k["osoby_dzialajace"] = [{"osoba": "Anna Fikcyjna", "rola": "prezes"}]
    o, extra, stany = _ocen(klient=k)
    assert stany["R04"] == b.UWAGI


def test_listy_nieswieze_blokada():
    o, extra, stany = _ocen(sankcje=_sankcje(pobrano="2026-09-28T06:00:00"))
    assert stany["R08"] == b.BLOKADA and extra["dyspozycja"] == "nie_mozna_ocenic"


def test_brak_jednej_listy_blokada():
    o, extra, stany = _ocen(sankcje=_sankcje(braki=("MSWiA",)))
    assert stany["R08"] == b.BLOKADA and extra["dyspozycja"] == "nie_mozna_ocenic"


def test_brak_krs_blokada():
    rej = _rejestry(); rej["krs"] = {"blad": "HTTPError"}
    o, extra, stany = _ocen(rejestry=rej)
    assert stany["R01"] == b.BLOKADA and extra["dyspozycja"] == "nie_mozna_ocenic"


def test_wykreslony_blokada():
    rej = _rejestry(); rej["krs"]["wykreslony"] = True
    o, extra, stany = _ocen(rejestry=rej)
    assert stany["R03"] == b.BLOKADA


# --- UWAGI ---

def test_pep_uwagi_eskalacja():
    k = _klient(); k["pep"]["pep"] = True
    o, extra, stany = _ocen(klient=k)
    assert stany["R09"] == b.UWAGI and extra["dyspozycja"] == "eskalacja"


def test_vat_niezarejestrowany_uwagi():
    rej = _rejestry(); rej["vat"]["status_vat"] = "Niezarejestrowany"
    o, extra, stany = _ocen(rejestry=rej)
    assert stany["R05"] == b.UWAGI


def test_brak_crbr_uzupelnij():
    k = _klient(); k["crbr"] = None; k["dokumenty_otrzymane"].remove("wydruk_crbr")
    o, extra, stany = _ocen(klient=k)
    assert stany["R07"] == b.UWAGI and stany["R11"] == b.UWAGI and extra["dyspozycja"] == "uzupelnij"


# --- CLI: na ekran tylko liczby ---

def test_cli_bez_nazwisk_na_ekranie(tmp_path, capsys):
    for n, d in (("klient.json", _klient()), ("rejestry.json", _rejestry()), ("sankcje.json", _sankcje()),
                 ("reguly.json", _reguly())):
        (tmp_path / n).write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    rc = b.main(["--klient", str(tmp_path / "klient.json"), "--rejestry", str(tmp_path / "rejestry.json"),
                 "--sankcje", str(tmp_path / "sankcje.json"), "--reguly", str(tmp_path / "reguly.json"), "--dzis", "2026-10-02"])
    ekran = capsys.readouterr().out
    assert rc == b.OK and "13 regul = 13 OK" in ekran
    assert "Fikcyjna" not in ekran and "Żółć" not in ekran
    assert (tmp_path / "wynik-kyc.md").exists()
