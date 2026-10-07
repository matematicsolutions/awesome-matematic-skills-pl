#!/usr/bin/env python3
"""Bramka KYC kancelarii: siatka regul na teczce klienta, rejestrach i listach sankcyjnych.

Bramka NICZEGO nie zatwierdza - punktuje i kieruje. Decyzje podejmuje osoba
odpowiedzialna w kancelarii. Kazda regula ma wynik (spelniona / niespelniona / nd)
i stan (OK / UWAGI / BLOKADA); raport zawiera pelny mianownik, takze reguly zdane.

  python bramka_kyc.py --klient klient.json --rejestry rejestry.json \
      --sankcje ~/.cache/kyc-kancelaria-pl/sankcje.json [--reguly reguly.json] [--out DIR]

Kod wyjscia: 0 OK, 10 UWAGI, 20 BLOKADA. Na ekran trafiaja tylko liczby i numery regul.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from rejestry import normalizuj, pasuje_do_maski, szukaj, zamaskowane  # noqa: E402

WERSJA = "0.1.0"
OK, UWAGI, BLOKADA = 0, 10, 20
NAZWA = {OK: "OK", UWAGI: "UWAGI", BLOKADA: "BLOKADA"}
LISTY = ("ONZ", "UE", "MSWiA")
REGULY_DOMYSLNE = Path(__file__).parent.parent / "reguly-domyslne.json"


class Ocena:
    def __init__(self) -> None:
        self.wiersze: list[dict] = []

    def dodaj(self, rid: str, opis: str, wynik: str, stan: int, dowod: str, kierunek: str = "") -> None:
        self.wiersze.append({"regula": rid, "opis": opis, "wynik": wynik, "stan": NAZWA[stan],
                             "_stan": stan, "dowod": dowod, "kierunek": kierunek})

    @property
    def stan(self) -> int:
        return max((w["_stan"] for w in self.wiersze), default=BLOKADA)


def _wiek_dni(znacznik: str | None, dzis: dt.date) -> int | None:
    if not znacznik:
        return None
    try:
        return (dzis - dt.date.fromisoformat(str(znacznik)[:10])).days
    except ValueError:
        return None


def _zbior(osoby) -> set[str]:
    return {normalizuj(o.get("osoba", "")) for o in osoby or [] if o.get("osoba")}


def _tokeny(nazwa: str) -> set[str]:
    return set(normalizuj(nazwa).split())


def _ta_sama_osoba(krotsze: str, pelne: str) -> bool:
    """Osoba z dokumentu (czesto bez drugiego imienia) to ta sama co pelne dane z odpisu."""
    a, b = _tokeny(krotsze), _tokeny(pelne)
    return len(a) >= 2 and a <= b


def _czesciowo_z_maska(nazwa: str, maska: str) -> bool:
    """Kazdy czlon nazwy ma odpowiednik w masce (pierwsza litera + dlugosc); maska moze miec wiecej czlonow."""
    import re as _re
    m = [(normalizuj(t[0]), len(t)) for t in _re.split(r"\s+", maska.strip()) if t]
    n = [(normalizuj(t[0]), len(t)) for t in _re.split(r"\s+", nazwa.strip()) if t]
    for k in n:
        if k in m:
            m.remove(k)
        else:
            return False
    return len(n) >= 2


def _uzgodnij_pelne(pelne: list[dict], maski: list[dict]) -> tuple[list[tuple[dict, dict]], list[dict]]:
    """Paruje pelne dane (z odpisu PDF) z maskami z API KRS. Zwraca (pary, niepasujace)."""
    wolne, pary, zle = list(maski), [], []
    for p in pelne:
        m = next((x for x in wolne if pasuje_do_maski(p.get("osoba", ""), x["osoba"])), None)
        if m is None:
            zle.append(p)
        else:
            wolne.remove(m)
            pary.append((p, m))
    return pary, zle


def ocen(klient: dict, rejestry: dict, sankcje: dict, reguly: dict, dzis: dt.date) -> tuple[Ocena, dict]:
    o = Ocena()
    krs = rejestry.get("krs") or {}
    vat = rejestry.get("vat") or {}
    dekl = klient.get("klient") or {}
    typ = dekl.get("typ", "spolka")

    # R01 - odpis KRS
    if "blad" in krs or not krs.get("krs"):
        o.dodaj("R01", "Odpis aktualny KRS pobrany", "niespelniona", BLOKADA,
                f"KRS: {krs.get('blad', 'brak danych')}", "nie_mozna_ocenic")
    else:
        o.dodaj("R01", "Odpis aktualny KRS pobrany", "spelniona", OK, f"KRS {krs['krs']}, stan z dnia {krs.get('stan_z_dnia')}")

    # R02 - zgodnosc deklaracji z KRS
    if krs.get("krs"):
        zgodny_nr = str(dekl.get("krs", "")).zfill(10) == str(krs["krs"])
        zgodna_nazwa = normalizuj(dekl.get("nazwa", ""), True) == normalizuj(krs.get("nazwa", ""), True)
        if zgodny_nr and zgodna_nazwa:
            o.dodaj("R02", "Nazwa i numer KRS z dokumentow zgodne z rejestrem", "spelniona", OK, "zgodne")
        else:
            o.dodaj("R02", "Nazwa i numer KRS z dokumentow zgodne z rejestrem", "niespelniona", UWAGI,
                    f"numer {'zgodny' if zgodny_nr else 'NIEZGODNY'}, nazwa {'zgodna' if zgodna_nazwa else 'NIEZGODNA'}", "eskalacja")
    else:
        o.dodaj("R02", "Nazwa i numer KRS z dokumentow zgodne z rejestrem", "nd", UWAGI, "brak odpisu KRS")

    # R03 - status podmiotu
    if krs.get("wykreslony"):
        o.dodaj("R03", "Podmiot nie jest wykreslony ani w likwidacji/upadlosci", "niespelniona", BLOKADA, "wykreslony z KRS", "eskalacja")
    elif krs.get("zdarzenia_dzial6"):
        o.dodaj("R03", "Podmiot nie jest wykreslony ani w likwidacji/upadlosci", "niespelniona", UWAGI,
                f"dzial 6: {', '.join(krs['zdarzenia_dzial6'])}", "eskalacja")
    elif krs.get("krs"):
        o.dodaj("R03", "Podmiot nie jest wykreslony ani w likwidacji/upadlosci", "spelniona", OK, "brak wpisow likwidacji/upadlosci w dziale 6")
    else:
        o.dodaj("R03", "Podmiot nie jest wykreslony ani w likwidacji/upadlosci", "nd", UWAGI, "brak odpisu KRS")

    # R13 - pelne dane organu i prokurentow (API KRS je maskuje) zgodne z maska rejestru
    sklad, prokurenci = krs.get("sklad") or [], krs.get("prokurenci") or []
    maskowane = any(zamaskowane(x["osoba"]) for x in sklad + prokurenci)
    pelne_org, pelne_prok = klient.get("organ_pelne_dane") or [], klient.get("prokurenci_pelne_dane") or []
    pary_org, zle_org = _uzgodnij_pelne(pelne_org, sklad)
    pary_prok, zle_prok = _uzgodnij_pelne(pelne_prok, prokurenci)
    if not krs.get("krs"):
        o.dodaj("R13", "Pelne dane organu zgodne z maska KRS", "nd", UWAGI, "brak odpisu KRS")
    elif not maskowane:
        o.dodaj("R13", "Pelne dane organu zgodne z maska KRS", "nd", OK, "odpis bez maskowania - porownanie zbedne")
    elif zle_org or zle_prok:
        o.dodaj("R13", "Pelne dane organu zgodne z maska KRS", "niespelniona", BLOKADA,
                f"{len(zle_org) + len(zle_prok)} os. nie pasuje do maski KRS (pierwsza litera / dlugosc) - blad przepisania albo inny odpis",
                "eskalacja")
    elif len(pary_org) < len(sklad) or len(pary_prok) < len(prokurenci):
        o.dodaj("R13", "Pelne dane organu zgodne z maska KRS", "niespelniona", UWAGI,
                f"API KRS maskuje dane; pelne dane: organ {len(pary_org)}/{len(sklad)}, prokurenci {len(pary_prok)}/{len(prokurenci)} "
                "- przepisz brakujace z odpisu KRS (PDF z wyszukiwarki KRS)", "uzupelnij_dokumenty")
    else:
        o.dodaj("R13", "Pelne dane organu zgodne z maska KRS", "spelniona", OK,
                f"organ {len(pary_org)}/{len(sklad)}, prokurenci {len(pary_prok)}/{len(prokurenci)} zgodni z maska")

    # R04 - umocowanie osob dzialajacych
    organ_pelne = [p for p, m in pary_org if not m.get("zawieszona")]
    prok_pelne = [p for p, _ in pary_prok]
    organ_maski = [m for m in sklad if not m.get("zawieszona")]
    dzialajacy = klient.get("osoby_dzialajace") or []
    if not dzialajacy:
        o.dodaj("R04", "Osoby dzialajace za klienta umocowane w KRS", "niespelniona", UWAGI,
                "teczka nie wskazuje, kto podpisuje zlecenie", "uzupelnij_dokumenty")
    elif krs.get("krs"):
        w_organie, w_prokurze, tylko_maska, bez = 0, 0, 0, 0
        for d in dzialajacy:
            n = d.get("osoba", "")
            if any(_ta_sama_osoba(n, p["osoba"]) for p in organ_pelne) or any(normalizuj(n) == normalizuj(m["osoba"]) for m in organ_maski if not zamaskowane(m["osoba"])):
                w_organie += 1
            elif any(_ta_sama_osoba(n, p["osoba"]) for p in prok_pelne) or any(normalizuj(n) == normalizuj(m["osoba"]) for m in prokurenci if not zamaskowane(m["osoba"])):
                w_prokurze += 1
            elif any(_czesciowo_z_maska(n, m["osoba"]) for m in organ_maski + prokurenci if zamaskowane(m["osoba"])):
                tylko_maska += 1
            elif not d.get("pelnomocnictwo"):
                bez += 1
        sposob = (krs.get("sposob_reprezentacji") or "").upper()
        if bez:
            o.dodaj("R04", "Osoby dzialajace za klienta umocowane w KRS", "niespelniona", BLOKADA,
                    f"{bez} os. spoza organu i prokury, bez pelnomocnictwa (zawieszeni nie reprezentuja)", "eskalacja")
        elif tylko_maska:
            o.dodaj("R04", "Osoby dzialajace za klienta umocowane w KRS", "niespelniona", UWAGI,
                    f"{tylko_maska} os. zgodnych tylko z maska KRS (pierwsza litera + dlugosc) - potwierdz w pelnym odpisie", "uzupelnij_dokumenty")
        elif "ŁĄCZNIE" in sposob and w_organie == 1 and not w_prokurze:
            o.dodaj("R04", "Osoby dzialajace za klienta umocowane w KRS", "niespelniona", UWAGI,
                    "reprezentacja laczna w KRS, a dziala jedna osoba z organu [DO WERYFIKACJI: sposob reprezentacji - ocenia prawnik]", "eskalacja")
        else:
            o.dodaj("R04", "Osoby dzialajace za klienta umocowane w KRS", "spelniona", OK,
                    f"organ {w_organie}, prokura {w_prokurze}; sposob reprezentacji do potwierdzenia przez prawnika")
    else:
        o.dodaj("R04", "Osoby dzialajace za klienta umocowane w KRS", "nd", UWAGI, "brak odpisu KRS")

    # R05 - status VAT
    if "blad" in vat:
        o.dodaj("R05", "Status na bialej liscie VAT akceptowalny", "nd", UWAGI, f"VAT: {vat['blad']}", "eskalacja")
    elif vat.get("status_vat") in reguly.get("statusy_vat_ok", ["Czynny"]):
        o.dodaj("R05", "Status na bialej liscie VAT akceptowalny", "spelniona", OK, f"{vat['status_vat']}, requestId {vat.get('request_id')}")
    else:
        o.dodaj("R05", "Status na bialej liscie VAT akceptowalny", "niespelniona", UWAGI,
                f"status: {vat.get('status_vat') or 'nie znaleziono'}", "eskalacja")

    # R06 / R07 - beneficjenci rzeczywisci
    osw = klient.get("oswiadczenie_beneficjenci") or {}
    crbr = klient.get("crbr")
    if not osw.get("zlozone"):
        o.dodaj("R06", "Oswiadczenie klienta o beneficjentach rzeczywistych", "niespelniona", UWAGI, "brak oswiadczenia", "uzupelnij_dokumenty")
    else:
        o.dodaj("R06", "Oswiadczenie klienta o beneficjentach rzeczywistych", "spelniona", OK, f"{len(osw.get('beneficjenci') or [])} beneficjentow")
    if not crbr:
        o.dodaj("R07", "Beneficjenci z oswiadczenia zgodni z CRBR", "nd", UWAGI,
                "brak wydruku z CRBR (pobiera prawnik z portalu CRBR)", "uzupelnij_dokumenty")
    elif osw.get("zlozone"):
        a, b = _zbior(osw.get("beneficjenci")), _zbior(crbr.get("beneficjenci"))
        wiek = _wiek_dni(crbr.get("data_wydruku"), dzis)
        if a != b:
            o.dodaj("R07", "Beneficjenci z oswiadczenia zgodni z CRBR", "niespelniona", BLOKADA,
                    f"rozbieznosc: tylko w oswiadczeniu {len(a - b)}, tylko w CRBR {len(b - a)} "
                    "[DO WERYFIKACJI: obowiazek zgloszenia rozbieznosci do CRBR - przepis wskazuje prawnik]", "eskalacja")
        elif wiek is None or wiek > reguly.get("max_wiek_rejestrow_dni", 7):
            o.dodaj("R07", "Beneficjenci z oswiadczenia zgodni z CRBR", "spelniona", UWAGI,
                    f"zgodni, ale wydruk CRBR {'bez daty' if wiek is None else f'sprzed {wiek} dni'}", "uzupelnij_dokumenty")
        else:
            o.dodaj("R07", "Beneficjenci z oswiadczenia zgodni z CRBR", "spelniona", OK, f"{len(a)} zgodnych, wydruk sprzed {wiek} dni")
    else:
        o.dodaj("R07", "Beneficjenci z oswiadczenia zgodni z CRBR", "nd", UWAGI, "brak oswiadczenia do porownania", "uzupelnij_dokumenty")

    # R08 - listy sankcyjne
    meta = sankcje.get("meta") or {}
    wiek_list = _wiek_dni(meta.get("pobrano"), dzis)
    braki = [l for l in LISTY if (meta.get("listy") or {}).get(l, {}).get("stan") != "ok"]
    # osoby z KRS: pelne dane z odpisu PDF zastepuja maski; maska bez pelnych danych = NIEPRZESIANA
    osoby, nieprzesiane = [], 0
    for rola, maski, pary in (("organ", sklad, pary_org), ("prokurent", prokurenci, pary_prok)):
        sparowane = {id(m) for _, m in pary}
        osoby += [(rola, p["osoba"], False) for p, _ in pary]
        for m in maski:
            if id(m) in sparowane:
                continue
            if zamaskowane(m["osoba"]):
                nieprzesiane += 1
            else:
                osoby.append((rola, m["osoba"], False))
    pelni_wspolnicy = klient.get("wspolnicy_pelne_dane") or []
    for n in krs.get("wspolnicy") or []:
        if not zamaskowane(n):
            osoby.append(("wspolnik", n, False))
        elif not any(pasuje_do_maski(p.get("osoba", ""), n) for p in pelni_wspolnicy):
            nieprzesiane += 1
    osoby += [("wspolnik", p["osoba"], False) for p in pelni_wspolnicy if p.get("osoba")]
    for zrodlo, lista in (("beneficjent-oswiadczenie", osw.get("beneficjenci")), ("beneficjent-crbr", (crbr or {}).get("beneficjenci")),
                          ("dzialajacy", dzialajacy), ("inna", klient.get("inne_osoby_do_przesiewu"))):
        osoby += [(zrodlo, x["osoba"], False) for x in lista or [] if x.get("osoba")]
    nazwa_podmiotu = krs.get("nazwa") or dekl.get("nazwa")
    if nazwa_podmiotu:
        osoby.append(("klient", nazwa_podmiotu, True))
    unikalne = {}
    for zr, n, pod in osoby:
        if zamaskowane(n):          # maska wpisana do teczki - nie da sie jej przesiac
            nieprzesiane += 1
            continue
        unikalne.setdefault((normalizuj(n, pod), pod), (zr, n, pod))
    trafienia = []
    if braki or wiek_list is None or wiek_list > reguly.get("max_wiek_list_dni", 1):
        o.dodaj("R08", "Przesiew sankcyjny ONZ + UE + MSWiA", "nd", BLOKADA,
                f"listy nieswieze albo niepelne (wiek {wiek_list} dni, brak: {', '.join(braki) or '-'}) - uruchom: rejestry.py sankcje-aktualizuj",
                "nie_mozna_ocenic")
    elif not unikalne:
        o.dodaj("R08", "Przesiew sankcyjny ONZ + UE + MSWiA", "nd", BLOKADA, "pusta lista osob do przesiewu", "nie_mozna_ocenic")
    else:
        wpisy = sankcje.get("wpisy") or []
        for zr, n, pod in unikalne.values():
            for t in szukaj(n, wpisy, pod):
                trafienia.append({"kto": n, "rola": zr} | t)
        dokladne = [t for t in trafienia if t["rodzaj"] == "dokladne"]
        if dokladne:
            o.dodaj("R08", "Przesiew sankcyjny ONZ + UE + MSWiA", "niespelniona", BLOKADA,
                    f"{len(unikalne)} nazw, trafienia dokladne {len(dokladne)} - weryfikacja tozsamosci (data urodzenia, obywatelstwo)", "eskalacja")
        elif trafienia:
            o.dodaj("R08", "Przesiew sankcyjny ONZ + UE + MSWiA", "niespelniona", UWAGI,
                    f"{len(unikalne)} nazw, trafienia podobne {len(trafienia)} - reczna weryfikacja"
                    + (f"; NIEPRZESIANE {nieprzesiane} os. z KRS (zamaskowane)" if nieprzesiane else ""), "eskalacja")
        elif nieprzesiane:
            o.dodaj("R08", "Przesiew sankcyjny ONZ + UE + MSWiA", "niespelniona", UWAGI,
                    f"przesiano {len(unikalne)} nazw, 0 trafien; NIEPRZESIANE {nieprzesiane} os. z KRS - API maskuje dane, "
                    "uzupelnij pelne dane z odpisu KRS (R13)", "uzupelnij_dokumenty")
        else:
            o.dodaj("R08", "Przesiew sankcyjny ONZ + UE + MSWiA", "spelniona", OK,
                    f"{len(unikalne)} nazw x {sum((meta.get('listy') or {}).get(l, {}).get('wpisow', 0) for l in LISTY)} wpisow, 0 trafien; listy z {str(meta.get('pobrano'))[:10]}")

    # R09 - PEP
    pep = klient.get("pep") or {}
    if not pep.get("oswiadczenie_zlozone"):
        o.dodaj("R09", "Oswiadczenie o statusie PEP", "niespelniona", UWAGI, "brak oswiadczenia PEP", "uzupelnij_dokumenty")
    elif pep.get("pep"):
        o.dodaj("R09", "Oswiadczenie o statusie PEP", "niespelniona", UWAGI,
                "zadeklarowano PEP [DO WERYFIKACJI: wzmozone srodki - zakres wskazuje prawnik]", "eskalacja")
    else:
        o.dodaj("R09", "Oswiadczenie o statusie PEP", "spelniona", OK, "oswiadczenie: nie PEP")

    # R10 - kraje wysokiego ryzyka (lista z konfiguracji kancelarii - nie zaszywamy jej w kodzie)
    kraje = set(reguly.get("kraje_wysokiego_ryzyka") or [])
    obyw = {(b.get("obywatelstwo") or "").upper() for b in (osw.get("beneficjenci") or []) + ((crbr or {}).get("beneficjenci") or [])} - {""}
    if not kraje:
        o.dodaj("R10", "Beneficjenci spoza krajow wysokiego ryzyka", "nd", UWAGI,
                "kancelaria nie skonfigurowala listy krajow wysokiego ryzyka (reguly.json)", "konfiguracja")
    elif obyw & kraje:
        o.dodaj("R10", "Beneficjenci spoza krajow wysokiego ryzyka", "niespelniona", UWAGI, f"kraje: {', '.join(sorted(obyw & kraje))}", "eskalacja")
    else:
        o.dodaj("R10", "Beneficjenci spoza krajow wysokiego ryzyka", "spelniona", OK, f"obywatelstwa: {', '.join(sorted(obyw)) or 'brak danych'}")

    # R11 - wymagane dokumenty
    wymagane = (reguly.get("wymagane_dokumenty") or {}).get(typ, [])
    mam = set(klient.get("dokumenty_otrzymane") or [])
    brak = [d for d in wymagane if d not in mam]
    if brak:
        o.dodaj("R11", "Komplet dokumentow wymaganych przez kancelarie", "niespelniona", UWAGI, f"brak: {', '.join(brak)}", "uzupelnij_dokumenty")
    else:
        o.dodaj("R11", "Komplet dokumentow wymaganych przez kancelarie", "spelniona", OK, f"{len(wymagane)} z {len(wymagane)}")

    # R12 - swiezosc danych z rejestrow
    wiek_rej = _wiek_dni(rejestry.get("pobrano"), dzis)
    if wiek_rej is None or wiek_rej > reguly.get("max_wiek_rejestrow_dni", 7):
        o.dodaj("R12", "Dane z KRS i VAT swieze", "niespelniona", UWAGI, f"wiek: {wiek_rej}", "uzupelnij_dokumenty")
    else:
        o.dodaj("R12", "Dane z KRS i VAT swieze", "spelniona", OK, f"pobrane {wiek_rej} dni temu")

    kierunki = {w["kierunek"] for w in o.wiersze if w["_stan"] != OK}
    if "nie_mozna_ocenic" in kierunki:
        dyspozycja = "nie_mozna_ocenic"
    elif "eskalacja" in kierunki:
        dyspozycja = "eskalacja"
    elif kierunki & {"uzupelnij_dokumenty", "konfiguracja"}:
        dyspozycja = "uzupelnij"
    else:
        dyspozycja = "bez_zastrzezen"
    return o, {"dyspozycja": dyspozycja, "trafienia": trafienia, "osob_przesianych": len(unikalne),
               "osob_nieprzesianych": nieprzesiane}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Bramka KYC kancelarii")
    ap.add_argument("--klient", required=True, type=Path)
    ap.add_argument("--rejestry", required=True, type=Path)
    ap.add_argument("--sankcje", required=True, type=Path)
    ap.add_argument("--reguly", type=Path, default=REGULY_DOMYSLNE)
    ap.add_argument("--out", type=Path)
    ap.add_argument("--dzis", help="data oceny RRRR-MM-DD (testy)")
    a = ap.parse_args(argv)
    try:
        klient = json.loads(a.klient.read_text(encoding="utf-8"))
        rejestry = json.loads(a.rejestry.read_text(encoding="utf-8"))
        sankcje = json.loads(a.sankcje.read_text(encoding="utf-8")) if a.sankcje.exists() else {}
        reguly = json.loads(a.reguly.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        print(f"BLOKADA: nie da sie wczytac wejscia: {type(e).__name__}")
        return BLOKADA
    dzis = dt.date.fromisoformat(a.dzis) if a.dzis else dt.date.today()
    o, extra = ocen(klient, rejestry, sankcje, reguly, dzis)
    out = a.out or a.klient.parent
    out.mkdir(parents=True, exist_ok=True)
    wynik = {"wersja": WERSJA, "data_oceny": dzis.isoformat(), "stan": NAZWA[o.stan], "dyspozycja": extra["dyspozycja"],
             "reguly": [{k: v for k, v in w.items() if k != "_stan"} for w in o.wiersze],
             "trafienia_sankcyjne": extra["trafienia"], "osob_przesianych": extra["osob_przesianych"],
             "osob_nieprzesianych": extra["osob_nieprzesianych"],
             "uwaga": "Bramka nie zatwierdza klienta. Decyzje podejmuje osoba odpowiedzialna w kancelarii."}
    (out / "wynik-kyc.json").write_text(json.dumps(wynik, ensure_ascii=False, indent=1), encoding="utf-8")
    md = [f"# Wynik KYC (bramka v{WERSJA}) - {dzis.isoformat()}", "",
          "[SZKIC AI - nie jest decyzja o przyjeciu klienta; decyduje osoba odpowiedzialna w kancelarii]", "",
          f"STAN: {wynik['stan']} | dyspozycja: {wynik['dyspozycja']} | osob przesianych: {extra['osob_przesianych']}", "",
          "| Regula | Opis | Wynik | Stan | Dowod |", "|---|---|---|---|---|"]
    md += [f"| {w['regula']} | {w['opis']} | {w['wynik']} | {w['stan']} | {w['dowod'].replace('|', '/')} |" for w in o.wiersze]
    if extra["trafienia"]:
        md += ["", "## Trafienia sankcyjne (do weryfikacji tozsamosci)", "", "| Osoba / podmiot | Rola | Lista | Id | Rodzaj | Nazwa na liscie |", "|---|---|---|---|---|---|"]
        md += [f"| {t['kto']} | {t['rola']} | {t['lista']} | {t['id']} | {t['rodzaj']} | {t['nazwa_na_liscie']} |" for t in extra["trafienia"]]
    (out / "wynik-kyc.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    stany = [w["_stan"] for w in o.wiersze]
    print(f"bramka KYC v{WERSJA}: {len(stany)} regul = {stany.count(OK)} OK + {stany.count(UWAGI)} UWAGI + {stany.count(BLOKADA)} BLOKADA")
    for s in (BLOKADA, UWAGI):
        r = [w["regula"] for w in o.wiersze if w["_stan"] == s]
        if r:
            print(f"{NAZWA[s]}: {', '.join(r)}")
    print(f"Przesiew: {extra['osob_przesianych']} nazw, nieprzesiane {extra['osob_nieprzesianych']}, trafien {len(extra['trafienia'])}")
    print(f"Dyspozycja: {extra['dyspozycja']} (decyduje czlowiek)")
    print(f"Raport: {out / 'wynik-kyc.md'}")
    print(f"STAN: {NAZWA[o.stan]}")
    return o.stan


if __name__ == "__main__":
    sys.exit(main())
