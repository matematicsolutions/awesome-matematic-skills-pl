#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prototyp: WALIDACJA podpisu w przychodzacym PDF (pyHanko, MIT).

Granica governance: Patron NIE podpisuje. Zlozenie podpisu to akt nieodwracalny
i na zewnatrz - zostaje czlowiekowi. Ten modul jest read-only: bierze PDF,
ktory kancelaria DOSTALA, i mowi, co o nim wiadomo.

Zwraca strukture, nie prose - warstwa wyzej (skill/konektor MCP) formatuje.
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass, field
from typing import Any


# Werdykty laczone. Osobno podane "integralnosc: OK" i "pokrywa caly plik: nie"
# czyta sie jak dobra wiadomosc, a oznaczaja razem dokument dopisany po
# podpisaniu. Werdykt musi byc JEDEN i musi laczyc oba ustalenia.
WERDYKT_WAZNY = "PODPIS WAZNY w zakresie sprawdzonym"
WERDYKT_DOPISANO = "DOKUMENT ZMIENIONY PO PODPISANIU - podpis nie obejmuje calej tresci"
WERDYKT_NARUSZONY = "PODPIS NARUSZONY - tresc podpisana zostala zmieniona"
WERDYKT_NIEROZSTRZYGNIETY = "NIEROZSTRZYGNIETY - patrz uwagi"


@dataclass
class UstaleniePodpisu:
    numer: int
    werdykt: str = WERDYKT_NIEROZSTRZYGNIETY
    pole: str | None = None
    podpisujacy: str | None = None
    email: str | None = None
    wystawca: str | None = None
    numer_seryjny: str | None = None
    deklarowany_czas: str | None = None
    znacznik_czasu: str | None = None
    znacznik_czasu_obecny: bool = False
    integralnosc_ok: bool | None = None
    pokrywa_caly_dokument: bool | None = None
    modyfikacje_po_podpisaniu: str | None = None
    poziom_pades: str | None = None
    lancuch_zaufania: str | None = None
    uwagi: list[str] = field(default_factory=list)


@dataclass
class WynikWalidacji:
    plik: str
    czy_podpisany: bool
    liczba_podpisow: int
    werdykt_ogolny: str = WERDYKT_NIEROZSTRZYGNIETY
    podpisy: list[UstaleniePodpisu] = field(default_factory=list)
    zakres_sprawdzenia: list[str] = field(default_factory=list)
    bledy: list[str] = field(default_factory=list)


def _dn_pole(nazwa_obj: Any, klucz: str) -> str | None:
    try:
        wartosc = nazwa_obj.native.get(klucz)
    except Exception:
        return None
    if isinstance(wartosc, list):
        return ", ".join(str(x) for x in wartosc)
    return str(wartosc) if wartosc is not None else None


def _werdykt(u: UstaleniePodpisu) -> str:
    if u.integralnosc_ok is not True:
        return WERDYKT_NARUSZONY
    if u.pokrywa_caly_dokument is False:
        return WERDYKT_DOPISANO
    if u.pokrywa_caly_dokument is None:
        return WERDYKT_NIEROZSTRZYGNIETY
    return WERDYKT_WAZNY


def _najgorszy(werdykty: list[str]) -> str:
    for ciezki in (WERDYKT_NARUSZONY, WERDYKT_DOPISANO, WERDYKT_NIEROZSTRZYGNIETY):
        if ciezki in werdykty:
            return ciezki
    return WERDYKT_WAZNY


def waliduj(sciezka: str) -> WynikWalidacji:
    import logging

    from pyhanko.pdf_utils.reader import PdfFileReader
    from pyhanko.sign.validation import validate_pdf_signature
    from pyhanko_certvalidator import ValidationContext

    # pyhanko loguje nieudana budowe sciezki certyfikatu jako blad ze sladem
    # stosu. Dla nas to stan OCZEKIWANY (nie wgrywamy kotwic zaufania), a dla
    # prawnika czytajacego wyjscie - halas nie do odroznienia od awarii.
    # Ustalenie trafia do pola lancuch_zaufania, nie na stderr.
    logging.getLogger("pyhanko_certvalidator").setLevel(logging.CRITICAL)
    logging.getLogger("pyhanko.sign.validation").setLevel(logging.CRITICAL)
    logging.getLogger("pyhanko").setLevel(logging.CRITICAL)

    wynik = WynikWalidacji(plik=sciezka, czy_podpisany=False, liczba_podpisow=0)

    # Bez kotwic zaufania: sprawdzamy integralnosc, pokrycie i modyfikacje.
    # Rozstrzygniecie "czy podpis KWALIFIKOWANY w rozumieniu eIDAS" wymaga
    # unijnych list zaufanych (LOTL) - patrz zakres_sprawdzenia nizej.
    kontekst = ValidationContext(allow_fetching=False, revocation_mode="soft-fail")

    try:
        with open(sciezka, "rb") as fh:
            czytnik = PdfFileReader(fh)
            podpisy = list(czytnik.embedded_signatures)
            wynik.liczba_podpisow = len(podpisy)
            wynik.czy_podpisany = len(podpisy) > 0

            for i, osadzony in enumerate(podpisy, start=1):
                u = UstaleniePodpisu(numer=i)
                try:
                    # str() OBOWIAZKOWO: pyHanko zwraca TextStringObject, czyli
                    # podklase str trzymajaca referencje do otwartego czytnika
                    # pliku. Wyglada i porownuje sie jak tekst, ale przewraca
                    # serializacje JSON (asdict robi deepcopy -> "cannot pickle
                    # BufferedReader"). Bez tego rzutowania tryb --json padal,
                    # a tryb tekstowy dzialal - rozjazd nie do wytlumaczenia.
                    u.pole = str(osadzony.field_name)
                except Exception:
                    pass

                status = validate_pdf_signature(osadzony, signer_validation_context=kontekst)

                u.integralnosc_ok = bool(getattr(status, "intact", None)) and bool(
                    getattr(status, "valid", None)
                )

                cert = getattr(status, "signing_cert", None)
                if cert is not None:
                    u.podpisujacy = _dn_pole(cert.subject, "common_name")
                    u.email = _dn_pole(cert.subject, "email_address")
                    u.wystawca = _dn_pole(cert.issuer, "common_name")
                    try:
                        u.numer_seryjny = str(cert.serial_number)
                    except Exception:
                        pass

                czas = getattr(status, "signer_reported_dt", None)
                if czas is not None:
                    u.deklarowany_czas = czas.isoformat()

                ts = getattr(status, "timestamp_validity", None)
                u.znacznik_czasu_obecny = ts is not None
                if ts is not None:
                    ts_dt = getattr(ts, "timestamp", None)
                    if ts_dt is not None:
                        u.znacznik_czasu = ts_dt.isoformat()

                # Pokrycie: czy podpis obejmuje CALY plik, czy tylko jego czesc.
                pokrycie = getattr(status, "coverage", None)
                if pokrycie is not None:
                    nazwa = getattr(pokrycie, "name", str(pokrycie))
                    u.pokrywa_caly_dokument = nazwa == "ENTIRE_FILE"
                    if not u.pokrywa_caly_dokument:
                        u.uwagi.append(
                            f"podpis nie obejmuje calego pliku (pokrycie: {nazwa}) - "
                            "tresc poza zakresem podpisu mogla powstac pozniej"
                        )

                mod = getattr(status, "modification_level", None)
                if mod is not None:
                    u.modyfikacje_po_podpisaniu = getattr(mod, "name", str(mod))

                poziom = getattr(status, "pades_subfilter", None)
                if poziom is not None:
                    u.poziom_pades = getattr(poziom, "name", str(poziom))

                zaufanie = getattr(status, "trusted", None)
                if zaufanie is True:
                    u.lancuch_zaufania = "zaufany w podanym kontekscie"
                else:
                    u.lancuch_zaufania = (
                        "NIEROZSTRZYGNIETY - brak wgranych kotwic zaufania (listy UE)"
                    )

                u.werdykt = _werdykt(u)
                wynik.podpisy.append(u)

            if wynik.podpisy:
                wynik.werdykt_ogolny = _najgorszy([p.werdykt for p in wynik.podpisy])

    except FileNotFoundError:
        wynik.bledy.append(f"nie znaleziono pliku: {sciezka}")
    except Exception as exc:  # noqa: BLE001 - prototyp: raportujemy, nie ukrywamy
        wynik.bledy.append(f"{type(exc).__name__}: {exc}")

    wynik.zakres_sprawdzenia = [
        "SPRAWDZANE: obecnosc podpisu, integralnosc kryptograficzna, tozsamosc z "
        "certyfikatu, deklarowany czas, obecnosc znacznika czasu, pokrycie pliku, "
        "poziom modyfikacji po podpisaniu.",
        "NIE ROZSTRZYGANE bez unijnych list zaufanych (LOTL/TSL): czy podpis jest "
        "KWALIFIKOWANY w rozumieniu eIDAS. Do tego potrzebne sa kotwice zaufania "
        "panstw czlonkowskich - osobny krok wdrozeniowy.",
        "Patron nie podpisuje. Ten modul jest wylacznie odczytowy.",
    ]
    return wynik


def kod_wyjscia(wynik: WynikWalidacji) -> int:
    """
    JEDEN kontrakt kodu wyjscia dla obu trybow.

    Wczesniej tryb --json liczyl go osobno (`czy_podpisany and not bledy`) i przez
    to zwracal 0 dla dokumentu ZMIENIONEGO PO PODPISANIU - czyli dokladnie dla
    przypadku, ktory to narzedzie ma wykrywac, i akurat na sciezce przeznaczonej
    do kontroli automatycznej. Kod wyjscia musi wynikac z WERDYKTU, nie z tego,
    czy udalo sie cokolwiek odczytac.
    """
    if wynik.bledy:
        return 2
    if not wynik.czy_podpisany:
        return 1
    return 0 if wynik.werdykt_ogolny == WERDYKT_WAZNY else 1


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        sys.stderr.write("Uzycie: python waliduj_podpis.py <plik.pdf> [--json]\n")
        return 2

    wynik = waliduj(argv[1])

    if "--json" in argv:
        print(json.dumps(asdict(wynik), ensure_ascii=False, indent=2))
        return kod_wyjscia(wynik)

    print(f"Plik: {wynik.plik}")
    if wynik.bledy:
        for b in wynik.bledy:
            print(f"  BLAD: {b}")
        return 2
    if not wynik.czy_podpisany:
        print("  Dokument NIE zawiera podpisu elektronicznego.")
        return 1

    print(f"  Podpisow: {wynik.liczba_podpisow}")
    print(f"  WERDYKT:  {wynik.werdykt_ogolny}")
    for u in wynik.podpisy:
        print(f"\n  [{u.numer}] {u.werdykt}")
        print(f"      pole:             {u.pole}")
        print(f"      podpisujacy:      {u.podpisujacy or '(brak w certyfikacie)'}")
        print(f"      e-mail:           {u.email or '(brak)'}")
        print(f"      wystawca:         {u.wystawca or '(brak)'}")
        print(f"      deklarowany czas: {u.deklarowany_czas or '(brak)'}")
        print(f"      znacznik czasu:   {u.znacznik_czasu or ('brak' if not u.znacznik_czasu_obecny else '(obecny)')}")
        print(f"      integralnosc podpisanej rewizji: {'OK' if u.integralnosc_ok else 'NARUSZONA'}")
        print(f"      podpis obejmuje caly plik:       {'tak' if u.pokrywa_caly_dokument else 'NIE'}")
        print(f"      modyfikacje po:   {u.modyfikacje_po_podpisaniu}")
        print(f"      lancuch zaufania: {u.lancuch_zaufania}")
        for uwaga in u.uwagi:
            print(f"      UWAGA: {uwaga}")

    print("\n  Zakres sprawdzenia:")
    for z in wynik.zakres_sprawdzenia:
        print(f"    - {z}")
    return kod_wyjscia(wynik)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
