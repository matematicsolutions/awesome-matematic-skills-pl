#!/usr/bin/env python3
"""Bramka lokatorow dla chronologii akt i zestawienia stanowisk.

Sprawdza mechanicznie (bez LLM, bez sieci), czy kazdy wpis chronologii albo
zestawienia stanowisk wskazuje plik i strone, ktore istnieja w tekscie akt
(wynik akta-przeszukiwalne-pl), i czy cytat naprawde stoi na tej stronie.

Kod wyjscia: 0 = OK, 10 = UWAGI, 20 = BLOKADA. Pusta lista wpisow = BLOKADA.
Na ekran trafiaja wylacznie liczby i identyfikatory wpisow; tresc akt zostaje
w pliku raportu obok pliku JSON.

Uzycie:
  python bramka_lokatorow.py WYNIK.json AKTA_TEKST_DIR [--csv OUT.csv]
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import sys
import unicodedata
from pathlib import Path

WERSJA = "0.1.0"
OK, UWAGI, BLOKADA = 0, 10, 20
NAZWA_STANU = {OK: "OK", UWAGI: "UWAGI", BLOKADA: "BLOKADA"}

PAGE_RE = re.compile(r"^===== (?:strona|page|página) (\d+) =====$", re.M)
NIECZYTELNA = "[STRONA NIECZYTELNA"

ENUM = {
    "pewnosc_daty": {"dokladna", "miesiac", "rok", "przedzial", "przyblizona", "sporna"},
    "rodzaj_daty": {"zdarzenia", "dokumentu", "nadania", "doreczenia", "wplywu", "posiedzenia"},
    "waga": {"kluczowe", "istotne", "tlo"},
    "status": {"dowod_bezposredni", "relacja", "twierdzenie_strony", "ustalenie_sadu",
               "zdarzenie_procesowe", "wniosek"},
    "pochodzenie": {"akta", "uzytkownik", "wiedza_modelu", "internet"},
    "tajemnica": {"ok", "flaga", "do_przegladu"},
    "postawa_tajemnicy": {"A", "B", "C"},
    "stanowisko_przeciwnika": {"przyznanie", "przyznanie_z_zastrzezeniem", "zaprzeczenie",
                               "brak_stanowiska", "nie_dotyczy"},
    "stan": {"wykazane", "czesciowo", "sporne", "luka", "do_uzupelnienia"},
}
DATA_RE = re.compile(r"^\d{4}(-\d{2}(-\d{2})?)?$")
FORMULA_START = ("=", "+", "-", "@", "\t", "\r")


# --- normalizacja tekstu -------------------------------------------------

def _norm(s: str) -> str:
    s = s.replace("\u00ad", "")                     # miekki dywiz
    s = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", s)    # przeniesienie wyrazu
    s = s.replace("\u201e", '"').replace("\u201d", '"').replace("\u201c", '"')
    s = s.replace("\u2019", "'").replace("\u2013", "-").replace("\u2014", "-")
    return re.sub(r"\s+", " ", s).strip().lower()


def _bez_ogonkow(s: str) -> str:
    s = s.replace("ł", "l").replace("Ł", "L")
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


# --- akta ----------------------------------------------------------------

def wczytaj_akta(katalog: Path) -> dict[str, dict[int, str]]:
    akta: dict[str, dict[int, str]] = {}
    for p in sorted(katalog.glob("*.txt")):
        tekst = p.read_text(encoding="utf-8", errors="replace")
        strony: dict[int, str] = {}
        znaczniki = list(PAGE_RE.finditer(tekst))
        for i, m in enumerate(znaczniki):
            koniec = znaczniki[i + 1].start() if i + 1 < len(znaczniki) else len(tekst)
            strony[int(m.group(1))] = tekst[m.end():koniec]
        if strony:
            akta[p.stem.lower()] = strony
    return akta


def _klucz_pliku(nazwa: str) -> str:
    n = Path(str(nazwa)).name
    for ext in (".txt", ".pdf"):
        if n.lower().endswith(ext):
            n = n[: -len(ext)]
    return n.lower()


# --- kontrole ------------------------------------------------------------

class Wynik:
    def __init__(self) -> None:
        self.znaleziska: list[tuple[int, str, str, str]] = []  # (stan, id, kod, opis)

    def dodaj(self, stan: int, wid: str, kod: str, opis: str) -> None:
        self.znaleziska.append((stan, wid, kod, opis))

    def stan_wpisu(self, wid: str) -> int:
        return max([s for s, i, _, _ in self.znaleziska if i == wid], default=OK)


def sprawdz_zrodlo(z: dict, akta: dict, wid: str, w: Wynik, pole: str) -> None:
    if not isinstance(z, dict):
        w.dodaj(BLOKADA, wid, "ZR00", f"{pole}: zrodlo nie jest obiektem")
        return
    plik, strona, cytat = z.get("plik"), z.get("strona"), (z.get("cytat") or "").strip()
    if not plik or strona is None:
        w.dodaj(BLOKADA, wid, "ZR01", f"{pole}: brak pliku albo strony")
        return
    klucz = _klucz_pliku(plik)
    if klucz not in akta:
        w.dodaj(BLOKADA, wid, "ZR02", f"{pole}: pliku '{klucz}' nie ma w tekscie akt")
        return
    try:
        strona = int(strona)
    except (TypeError, ValueError):
        w.dodaj(BLOKADA, wid, "ZR03", f"{pole}: strona '{strona}' nie jest liczba")
        return
    strony = akta[klucz]
    if strona not in strony:
        w.dodaj(BLOKADA, wid, "ZR04", f"{pole}: plik '{klucz}' nie ma strony {strona} (ma {len(strony)})")
        return
    tekst_strony = strony[strona]
    if NIECZYTELNA in tekst_strony:
        w.dodaj(UWAGI, wid, "ZR05", f"{pole}: strona {strona} pliku '{klucz}' nieczytelna w OCR - porownaj z oryginalem")
        return
    if len(cytat.split()) < 3:
        w.dodaj(BLOKADA, wid, "ZR06", f"{pole}: cytat krotszy niz 3 slowa - nie da sie go zakotwiczyc")
        return
    n_cyt, n_str = _norm(cytat), _norm(tekst_strony)
    if n_cyt in n_str:
        return
    if _bez_ogonkow(n_cyt) in _bez_ogonkow(n_str):
        w.dodaj(UWAGI, wid, "ZR07", f"{pole}: cytat zgadza sie tylko bez polskich znakow (blad OCR?) - plik '{klucz}' s. {strona}")
        return
    inne = [nr for nr, t in strony.items() if nr != strona and n_cyt in _norm(t)]
    if inne:
        w.dodaj(BLOKADA, wid, "ZR08", f"{pole}: cytat jest w pliku '{klucz}', ale na stronie {inne[0]}, nie {strona}")
    else:
        w.dodaj(BLOKADA, wid, "ZR09", f"{pole}: cytatu nie ma na stronie {strona} pliku '{klucz}'")


def _enum(wpis: dict, pole: str, wid: str, w: Wynik, wymagane: bool = True) -> None:
    v = wpis.get(pole)
    if v is None:
        if wymagane:
            w.dodaj(BLOKADA, wid, "SC01", f"brak pola '{pole}'")
        return
    if v not in ENUM[pole]:
        w.dodaj(BLOKADA, wid, "SC02", f"pole '{pole}' = '{v}' spoza listy {sorted(ENUM[pole])}")


def _data(wpis: dict, wid: str, w: Wynik) -> None:
    d = str(wpis.get("data") or "").strip()
    if not d:
        w.dodaj(BLOKADA, wid, "DT01", "brak daty (wpis bez daty nie nalezy do chronologii - wpisz go w luki)")
        return
    czesci = d.split("/")
    if len(czesci) > 2 or not all(DATA_RE.match(c) for c in czesci):
        w.dodaj(BLOKADA, wid, "DT02", f"data '{d}' nie jest w formacie RRRR[-MM[-DD]] ani przedzialem A/B")
        return
    for c in czesci:
        if len(c) == 10:
            try:
                dt.date.fromisoformat(c)
            except ValueError:
                w.dodaj(BLOKADA, wid, "DT03", f"data '{c}' nie istnieje w kalendarzu")
                return
    pewnosc = wpis.get("pewnosc_daty")
    if pewnosc == "dokladna" and (len(czesci) != 1 or len(czesci[0]) != 10):
        w.dodaj(UWAGI, wid, "DT04", "pewnosc 'dokladna', ale data nie jest pelnym dniem")
    if pewnosc == "przedzial" and len(czesci) != 2:
        w.dodaj(UWAGI, wid, "DT05", "pewnosc 'przedzial', ale data nie ma postaci A/B")


def _zrodla_lub_pochodzenie(wpis: dict, pole: str, akta: dict, wid: str, w: Wynik) -> None:
    zrodla = wpis.get(pole) or []
    pochodzenie = wpis.get("pochodzenie", "akta")
    if not zrodla:
        if pochodzenie == "akta":
            w.dodaj(BLOKADA, wid, "ZR10", f"{pole}: wpis 'z akt' bez zadnego zrodla")
        else:
            w.dodaj(UWAGI, wid, "ZR11", f"pochodzenie '{pochodzenie}' bez zrodla w aktach - zweryfikuj przed uzyciem")
        return
    for i, z in enumerate(zrodla):
        sprawdz_zrodlo(z, akta, wid, w, f"{pole}[{i}]")


def sprawdz_chronologie(dane: dict, akta: dict, w: Wynik) -> list[dict]:
    wpisy = dane.get("wpisy") or []
    postawa = dane.get("postawa_tajemnicy")
    for wpis in wpisy:
        wid = str(wpis.get("id") or "?")
        _data(wpis, wid, w)
        for pole in ("pewnosc_daty", "rodzaj_daty", "waga", "status"):
            _enum(wpis, pole, wid, w)
        _enum(wpis, "pochodzenie", wid, w, wymagane=False)
        if not (wpis.get("zdarzenie") or "").strip():
            w.dodaj(BLOKADA, wid, "SC03", "puste pole 'zdarzenie'")
        if postawa == "B":
            _enum(wpis, "tajemnica", wid, w)
        _zrodla_lub_pochodzenie(wpis, "zrodla", akta, wid, w)
    kluczowe = sum(1 for x in wpisy if x.get("waga") == "kluczowe")
    if len(wpisy) >= 10 and kluczowe > len(wpisy) / 2:
        w.dodaj(UWAGI, "*", "WG01", f"{kluczowe} z {len(wpisy)} wpisow 'kluczowe' - gdy wszystko jest kluczowe, nic nie jest")
    return wpisy


def sprawdz_zestawienie(dane: dict, akta: dict, w: Wynik) -> list[dict]:
    elementy = dane.get("elementy") or []
    for el in elementy:
        wid = str(el.get("id") or "?")
        if not (el.get("element") or "").strip():
            w.dodaj(BLOKADA, wid, "SC03", "puste pole 'element'")
        _enum(el, "stan", wid, w)
        _enum(el, "stanowisko_przeciwnika", wid, w)
        for pole in ("twierdzenia", "zrodla_stanowiska", "dowody_za", "dowody_przeciw"):
            for i, z in enumerate(el.get(pole) or []):
                sprawdz_zrodlo(z, akta, wid, w, f"{pole}[{i}]")
        stan, za = el.get("stan"), el.get("dowody_za") or []
        if stan == "wykazane" and not za:
            w.dodaj(BLOKADA, wid, "ST01", "stan 'wykazane' bez zadnego dowodu za")
        if stan == "luka" and za:
            w.dodaj(UWAGI, wid, "ST02", "stan 'luka', a sa dowody za - sprawdz, czy to nie 'czesciowo'")
        if el.get("stanowisko_przeciwnika") not in (None, "nie_dotyczy", "brak_stanowiska") \
                and not el.get("zrodla_stanowiska"):
            w.dodaj(BLOKADA, wid, "ST03", "stanowisko przeciwnika podane bez wskazania pisma, z ktorego wynika")
    return elementy


# --- eksport CSV ---------------------------------------------------------

def _bezpieczna(v) -> str:
    s = "" if v is None else str(v)
    return "'" + s if s.startswith(FORMULA_START) else s


def _lokatory(zrodla) -> str:
    return "; ".join(f"{_klucz_pliku(z.get('plik', ''))} s. {z.get('strona')}" for z in (zrodla or []) if isinstance(z, dict))


def eksport_csv(rodzaj: str, rekordy: list[dict], w: Wynik, out: Path) -> int:
    zneutralizowane = 0
    with out.open("w", encoding="utf-8-sig", newline="") as f:
        pisz = csv.writer(f, delimiter=";")
        if rodzaj == "chronologia":
            pisz.writerow(["id", "data", "pewnosc_daty", "rodzaj_daty", "kto", "zdarzenie", "waga",
                           "status", "tajemnica", "zrodla", "bramka"])
            for r in rekordy:
                wiersz = [r.get("id"), r.get("data"), r.get("pewnosc_daty"), r.get("rodzaj_daty"),
                          r.get("kto"), r.get("zdarzenie"), r.get("waga"), r.get("status"),
                          r.get("tajemnica", ""), _lokatory(r.get("zrodla")),
                          NAZWA_STANU[w.stan_wpisu(str(r.get("id")))]]
                bez = [_bezpieczna(x) for x in wiersz]
                zneutralizowane += sum(1 for a, b in zip(wiersz, bez) if str(a or "") != b)
                pisz.writerow(bez)
        else:
            pisz.writerow(["id", "element", "stan", "stanowisko_przeciwnika", "twierdzenia",
                           "dowody_za", "dowody_przeciw", "bramka"])
            for r in rekordy:
                wiersz = [r.get("id"), r.get("element"), r.get("stan"), r.get("stanowisko_przeciwnika"),
                          _lokatory(r.get("twierdzenia")), _lokatory(r.get("dowody_za")),
                          _lokatory(r.get("dowody_przeciw")), NAZWA_STANU[w.stan_wpisu(str(r.get("id")))]]
                bez = [_bezpieczna(x) for x in wiersz]
                zneutralizowane += sum(1 for a, b in zip(wiersz, bez) if str(a or "") != b)
                pisz.writerow(bez)
    return zneutralizowane


# --- main ----------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Bramka lokatorow chronologii i zestawienia stanowisk")
    ap.add_argument("wynik", type=Path, help="plik JSON z chronologia albo zestawieniem")
    ap.add_argument("akta", type=Path, help="katalog tekstu akt (wynik akta-przeszukiwalne-pl)")
    ap.add_argument("--csv", type=Path, help="eksport do CSV (komorki zneutralizowane przed formulami)")
    a = ap.parse_args(argv)

    w = Wynik()
    try:
        dane = json.loads(a.wynik.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"BLOKADA: nie da sie wczytac {a.wynik.name}: {type(e).__name__}")
        return BLOKADA
    akta = wczytaj_akta(a.akta) if a.akta.is_dir() else {}
    if not akta:
        print(f"BLOKADA: w katalogu akt nie ma plikow .txt z naglowkami stron")
        return BLOKADA

    rodzaj = dane.get("rodzaj")
    _enum(dane, "postawa_tajemnicy", "naglowek", w)
    if dane.get("postawa_tajemnicy") == "C":
        w.dodaj(BLOKADA, "naglowek", "TJ01", "postawa C - materialy nie przeszly przegladu tajemnicy; nie budujemy")
    if rodzaj == "chronologia":
        rekordy = sprawdz_chronologie(dane, akta, w)
    elif rodzaj == "zestawienie":
        rekordy = sprawdz_zestawienie(dane, akta, w)
    else:
        print(f"BLOKADA: pole 'rodzaj' musi byc 'chronologia' albo 'zestawienie'")
        return BLOKADA
    if not rekordy:
        w.dodaj(BLOKADA, "*", "PU01", "pusta lista wpisow - brak wyniku to nie sukces")

    ids = [str(r.get("id") or "?") for r in rekordy]
    for d in {x for x in ids if ids.count(x) > 1}:
        w.dodaj(BLOKADA, d, "SC04", "zdublowany identyfikator wpisu")

    stany = [w.stan_wpisu(i) for i in ids]
    globalny = max([s for s, *_ in w.znaleziska], default=OK)

    raport = a.wynik.with_suffix(".bramka.md")
    linie = [f"# Bramka lokatorow v{WERSJA} - {a.wynik.name}", "",
             f"Rodzaj: {rodzaj}. Akta: {len(akta)} plikow, {sum(len(s) for s in akta.values())} stron.",
             f"Mianownik: {len(rekordy)} = {stany.count(OK)} OK + {stany.count(UWAGI)} UWAGI + {stany.count(BLOKADA)} BLOKADA",
             f"STAN: {NAZWA_STANU[globalny]}", "", "| stan | wpis | kod | opis |", "|---|---|---|---|"]
    for s, wid, kod, opis in sorted(w.znaleziska, key=lambda x: (-x[0], x[1])):
        linie.append(f"| {NAZWA_STANU[s]} | {wid} | {kod} | {opis.replace('|', '/')} |")
    raport.write_text("\n".join(linie) + "\n", encoding="utf-8")

    print(f"bramka lokatorow v{WERSJA}: {rodzaj}, akta {len(akta)} plikow")
    print(f"Mianownik: {len(rekordy)} = {stany.count(OK)} OK + {stany.count(UWAGI)} UWAGI + {stany.count(BLOKADA)} BLOKADA")
    for s in (BLOKADA, UWAGI):
        dot = sorted({wid for st, wid, *_ in w.znaleziska if st == s})
        if dot:
            print(f"{NAZWA_STANU[s]}: {', '.join(dot)}")
    if a.csv:
        n = eksport_csv(rodzaj, rekordy, w, a.csv)
        print(f"CSV: {a.csv.name} (zneutralizowane komorki: {n})")
    print(f"Raport: {raport.name}")
    print(f"STAN: {NAZWA_STANU[globalny]}")
    return globalny


if __name__ == "__main__":
    sys.exit(main())
