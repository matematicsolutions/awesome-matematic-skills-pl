#!/usr/bin/env python3
"""Rejestry dla KYC kancelarii: KRS, biala lista VAT, listy sankcyjne (ONZ, UE, MSWiA).

Do rejestrow wychodzi wylacznie numer KRS albo NIP. Listy sankcyjne sa pobierane
w calosci na dysk i porownywane LOKALNIE - nazwiska klienta nie opuszczaja komputera.
Stdlib, bez kluczy API. Kod wyjscia: 0 OK, 10 UWAGI, 20 BLOKADA.

  python rejestry.py pobierz --krs 0000123456 [--nip 1234567890] --out TECZKA_DIR
  python rejestry.py sankcje-aktualizuj [--cache DIR]
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import html
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

WERSJA = "0.1.0"
OK, UWAGI, BLOKADA = 0, 10, 20
UA = {"User-Agent": "Mozilla/5.0 (kyc-kancelaria-pl)"}
CACHE_DOMYSLNY = Path.home() / ".cache" / "kyc-kancelaria-pl"

URL_KRS = "https://api-krs.ms.gov.pl/api/krs/OdpisAktualny/{krs}?rejestr={rej}&format=json"
URL_VAT = "https://wl-api.mf.gov.pl/api/search/nip/{nip}?date={data}"
URL_ONZ = "https://scsanctions.un.org/resources/xml/en/consolidated.xml"
URL_UE = ("https://webgate.ec.europa.eu/fsd/fsf/public/files/xmlFullSanctionsList_1_1/"
          "content?token=dG9rZW4tMjAxNw")
URL_MSWIA = "https://www.gov.pl/web/mswia/lista-osob-i-podmiotow-objetych-sankcjami"

FORMY = {"sp", "z", "o", "oo", "sa", "s", "a", "spolka", "akcyjna", "ograniczona",
         "odpowiedzialnoscia", "llc", "ltd", "limited", "ooo", "oao", "pao", "zao", "ao",
         "jsc", "gmbh", "ag", "inc", "corp", "co", "company", "plc", "bv", "sro", "kft"}


# --- siec ---------------------------------------------------------------

def _pobierz(url: str, timeout: int = 90) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


# --- normalizacja nazw --------------------------------------------------

def normalizuj(nazwa: str, podmiot: bool = False) -> str:
    s = nazwa.replace("ł", "l").replace("Ł", "L")
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    s = re.sub(r"[^\w\s]", " ", s.lower())
    tokeny = [t for t in s.split() if t]
    if podmiot:
        tokeny = [t for t in tokeny if t not in FORMY]
    return " ".join(sorted(tokeny))


# --- KRS ----------------------------------------------------------------

def _osoba_krs(o: dict) -> str:
    imiona = o.get("imiona") or {}
    nazwisko = o.get("nazwisko") or {}
    czesci = [imiona.get("imie"), imiona.get("imieDrugie"), nazwisko.get("nazwiskoICzlon"),
              nazwisko.get("nazwiskoCzlonDrugi")]
    return " ".join(c for c in czesci if c)


def zamaskowane(nazwa: str) -> bool:
    """Publiczne API KRS maskuje dane osob: zostaje pierwsza litera, reszta to '*'."""
    return "*" in (nazwa or "")


def pasuje_do_maski(pelne: str, maska: str) -> bool:
    """Czy pelne imie i nazwisko pasuja do maski KRS (pierwsza litera + dlugosc kazdego czlonu)."""
    def klucze(s, separator):
        return sorted((normalizuj(t[0]), len(t)) for t in re.split(separator, s.strip()) if t)
    if not pelne.strip() or not maska.strip():
        return False
    cel = klucze(maska, r"\s+")
    # nazwisko dwuczlonowe bywa w KRS jednym polem (z lacznikiem) albo dwoma
    return klucze(pelne, r"\s+") == cel or klucze(pelne, r"[\s-]+") == cel


def parsuj_krs(j: dict) -> dict:
    o = j.get("odpis") or {}
    nag, dane = o.get("naglowekA") or {}, o.get("dane") or {}
    d1, d2, d6 = dane.get("dzial1") or {}, dane.get("dzial2") or {}, dane.get("dzial6") or {}
    dp = d1.get("danePodmiotu") or {}
    rep = d2.get("reprezentacja") or {}
    sklad = [{"osoba": _osoba_krs(s), "funkcja": s.get("funkcjaWOrganie"),
              "zawieszona": bool(s.get("czyZawieszona"))} for s in rep.get("sklad") or []]
    prok = [{"osoba": _osoba_krs(p), "rodzaj": p.get("rodzajProkury")} for p in d2.get("prokurenci") or []]
    wspolnicy = []
    for w in d1.get("wspolnicySpzoo") or []:
        nazwa = _osoba_krs(w) or (w.get("nazwa") or "")
        if nazwa:
            wspolnicy.append(nazwa)
    zdarzenia = sorted(k for k in d6 if re.search(r"likwid|upad|restruktur|zawiesz|wykresl|zarzad.?przymus", k, re.I))
    return {
        "krs": nag.get("numerKRS"), "rejestr": nag.get("rejestr"), "stan_z_dnia": nag.get("stanZDnia"),
        "nazwa": dp.get("nazwa"), "forma": dp.get("formaPrawna"),
        "nip": (dp.get("identyfikatory") or {}).get("nip"), "regon": (dp.get("identyfikatory") or {}).get("regon"),
        "wykreslony": bool(nag.get("dataWykreslenia") or nag.get("dataWykresleniaZRejestru")),
        "zdarzenia_dzial6": zdarzenia,
        "organ": rep.get("nazwaOrganu"), "sposob_reprezentacji": rep.get("sposobReprezentacji"),
        "sklad": sklad, "prokurenci": prok, "wspolnicy": wspolnicy,
    }


def pobierz_krs(krs: str) -> tuple[dict, bytes, str]:
    ostatni = None
    for rej in ("P", "S"):
        try:
            b = _pobierz(URL_KRS.format(krs=krs, rej=rej))
            return parsuj_krs(json.loads(b)), b, rej
        except urllib.error.HTTPError as e:
            ostatni = e
    raise ostatni or RuntimeError("KRS: brak odpowiedzi")


# --- biala lista VAT ------------------------------------------------------

def parsuj_vat(j: dict) -> dict:
    r = j.get("result") or {}
    s = r.get("subject") or {}
    return {"status_vat": s.get("statusVat"), "nazwa": s.get("name"), "nip": s.get("nip"),
            "krs": s.get("krs"), "rachunki": len(s.get("accountNumbers") or []),
            "request_id": r.get("requestId"), "data_zapytania": r.get("requestDateTime"),
            "znaleziony": bool(s)}


# --- listy sankcyjne -----------------------------------------------------

def _lokalna(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parsuj_onz(b: bytes) -> list[dict]:
    wyn = []
    root = ET.fromstring(b)
    for el in root.iter():
        t = _lokalna(el.tag)
        if t not in ("INDIVIDUAL", "ENTITY"):
            continue
        get = lambda n: (el.findtext(n) or "").strip()
        if t == "INDIVIDUAL":
            glowna = " ".join(x for x in (get("FIRST_NAME"), get("SECOND_NAME"), get("THIRD_NAME"), get("FOURTH_NAME")) if x)
        else:
            glowna = get("FIRST_NAME")
        aliasy = []
        for a in el.iter():
            if _lokalna(a.tag) in ("INDIVIDUAL_ALIAS", "ENTITY_ALIAS") and (a.findtext("ALIAS_NAME") or "").strip():
                # ONZ skleja kilka aliasow w jednym polu: "X; Y b) Z" - rozdzielamy
                for czesc in re.split(r";|\b[a-z]\)\s", a.findtext("ALIAS_NAME")):
                    if len(czesc.strip()) > 2:
                        aliasy.append(czesc.strip())
        if glowna:
            wyn.append({"lista": "ONZ", "id": get("REFERENCE_NUMBER") or get("DATAID"),
                        "typ": "osoba" if t == "INDIVIDUAL" else "podmiot", "nazwy": [glowna] + aliasy})
    return wyn


def parsuj_ue(b: bytes) -> list[dict]:
    wyn = []
    root = ET.fromstring(b)
    for el in root.iter():
        if _lokalna(el.tag) != "sanctionEntity":
            continue
        typ = "podmiot"
        nazwy = []
        for c in el:
            t = _lokalna(c.tag)
            if t == "subjectType" and (c.get("code") or "").lower() == "person":
                typ = "osoba"
            if t == "nameAlias":
                n = (c.get("wholeName") or " ".join(x for x in (c.get("firstName"), c.get("middleName"), c.get("lastName")) if x)).strip()
                if n:
                    nazwy.append(n)
        if nazwy:
            wyn.append({"lista": "UE", "id": el.get("logicalId") or el.get("euReferenceNumber"), "typ": typ, "nazwy": nazwy})
    return wyn


def _komorki(wiersz: str) -> list[str]:
    return [re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", c))).strip()
            for c in re.findall(r"<t[hd][^>]*>(.*?)</t[hd]>", wiersz, re.S)]


def parsuj_mswia(tekst: str) -> list[dict]:
    wyn = []
    for tabela in re.findall(r"<table.*?</table>", tekst, re.S):
        wiersze = re.findall(r"<tr.*?</tr>", tabela, re.S)
        if not wiersze:
            continue
        naglowek = " ".join(_komorki(wiersze[0])).lower()
        if "data umieszczenia" not in naglowek:
            continue
        typ = "podmiot" if "podmiot" in naglowek else "osoba"
        for i, w in enumerate(wiersze[1:], 1):
            k = _komorki(w)
            if len(k) < 6 or not k[0]:
                continue
            if k[5] and re.search(r"\d", k[5]):      # data wykreslenia - nieaktualny wpis
                continue
            nazwy = [n.strip() for n in re.split(r"[()\[\]/;]|\s{2,}", k[0]) if len(n.strip()) > 2]
            wyn.append({"lista": "MSWiA", "id": f"{typ}-{i}", "typ": typ, "nazwy": nazwy or [k[0]]})
    return wyn


def aktualizuj_sankcje(cache: Path) -> int:
    cache.mkdir(parents=True, exist_ok=True)
    wpisy, meta, stan = [], {"pobrano": dt.datetime.now().isoformat(timespec="seconds"), "listy": {}}, OK
    for lista, url, parser, tekst in (("ONZ", URL_ONZ, parsuj_onz, False), ("UE", URL_UE, parsuj_ue, False),
                                      ("MSWiA", URL_MSWIA, parsuj_mswia, True)):
        try:
            b = _pobierz(url, timeout=180)
            w = parser(b.decode("utf-8", "replace") if tekst else b)
            if not w:
                raise ValueError("pusta lista po parsowaniu")
            wpisy += w
            meta["listy"][lista] = {"wpisow": len(w), "sha256": hashlib.sha256(b).hexdigest()[:16], "stan": "ok"}
        except Exception as e:  # noqa: BLE001 - kazda awaria listy to BLOKADA, nie cichy sukces
            meta["listy"][lista] = {"wpisow": 0, "stan": f"blad: {type(e).__name__}"}
            stan = BLOKADA
    (cache / "sankcje.json").write_text(json.dumps({"meta": meta, "wpisy": wpisy}, ensure_ascii=False), encoding="utf-8")
    for lista, m in meta["listy"].items():
        print(f"{lista}: {m['stan']}, wpisow {m['wpisow']}")
    print(f"STAN: {'OK' if stan == OK else 'BLOKADA'} (cache: {cache / 'sankcje.json'})")
    return stan


# --- dopasowanie ---------------------------------------------------------

def szukaj(nazwa: str, wpisy: list[dict], podmiot: bool = False) -> list[dict]:
    """Zwraca trafienia: 'dokladne' (ten sam zbior tokenow) albo 'podobne' (do recznej weryfikacji)."""
    from difflib import SequenceMatcher
    if zamaskowane(nazwa):
        raise ValueError("nazwa zamaskowana (API KRS) - przesiew niemozliwy, potrzebne pelne dane")
    cel = normalizuj(nazwa, podmiot)
    if not cel:
        return []
    tok_cel = {t for t in cel.split() if len(t) > 1}
    wyn = []
    for w in wpisy:
        if (w["typ"] == "podmiot") != podmiot:
            continue
        najlepsze = None
        for n in w["nazwy"]:
            kand = normalizuj(n, podmiot)
            if not kand:
                continue
            if kand == cel:
                najlepsze = "dokladne"
                break
            tok = {t for t in kand.split() if len(t) > 1}
            podzbior = len(tok_cel) >= 2 and len(tok) >= 2 and (tok_cel <= tok or tok <= tok_cel)
            if podzbior or SequenceMatcher(None, kand, cel).ratio() >= 0.9:
                najlepsze = najlepsze or "podobne"
        if najlepsze:
            wyn.append({"lista": w["lista"], "id": w["id"], "rodzaj": najlepsze, "nazwa_na_liscie": w["nazwy"][0]})
    return wyn


# --- CLI -----------------------------------------------------------------

def _cmd_pobierz(a) -> int:
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    stan, wynik = OK, {"pobrano": dt.datetime.now().isoformat(timespec="seconds"), "wersja": WERSJA}
    try:
        krs, surowe, rej = pobierz_krs(a.krs)
        (out / "krs-odpis.json").write_bytes(surowe)
        wynik["krs"] = krs | {"zrodlo": URL_KRS.format(krs=a.krs, rej=rej), "sha256": hashlib.sha256(surowe).hexdigest()[:16]}
    except Exception as e:  # noqa: BLE001
        wynik["krs"] = {"blad": type(e).__name__}
        stan = BLOKADA
    nip = a.nip or (wynik.get("krs") or {}).get("nip")
    if nip:
        try:
            b = _pobierz(URL_VAT.format(nip=nip, data=dt.date.today().isoformat()))
            (out / "vat.json").write_bytes(b)
            wynik["vat"] = parsuj_vat(json.loads(b))
        except Exception as e:  # noqa: BLE001
            wynik["vat"] = {"blad": type(e).__name__}
            stan = max(stan, UWAGI)
    else:
        wynik["vat"] = {"blad": "brak NIP"}
        stan = max(stan, UWAGI)
    (out / "rejestry.json").write_text(json.dumps(wynik, ensure_ascii=False, indent=1), encoding="utf-8")
    k = wynik.get("krs") or {}
    print(f"KRS: {'blad ' + k['blad'] if 'blad' in k else 'ok, sklad organu ' + str(len(k.get('sklad', []))) + ', prokurentow ' + str(len(k.get('prokurenci', [])))}")
    v = wynik["vat"]
    print(f"VAT: {'blad ' + v['blad'] if 'blad' in v else 'status ' + str(v.get('status_vat'))}")
    print(f"STAN: {'OK' if stan == OK else 'UWAGI' if stan == UWAGI else 'BLOKADA'} -> {out / 'rejestry.json'}")
    return stan


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Rejestry KYC kancelarii (KRS, VAT, sankcje)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pobierz")
    p.add_argument("--krs", required=True)
    p.add_argument("--nip")
    p.add_argument("--out", required=True)
    s = sub.add_parser("sankcje-aktualizuj")
    s.add_argument("--cache", default=str(CACHE_DOMYSLNY))
    a = ap.parse_args(argv)
    if a.cmd == "pobierz":
        if not re.fullmatch(r"\d{10}", a.krs):
            print("BLOKADA: numer KRS musi miec 10 cyfr")
            return BLOKADA
        return _cmd_pobierz(a)
    return aktualizuj_sankcje(Path(a.cache))


if __name__ == "__main__":
    sys.exit(main())
