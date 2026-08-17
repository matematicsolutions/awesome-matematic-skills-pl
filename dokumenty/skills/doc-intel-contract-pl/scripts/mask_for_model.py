"""Maska dlugosciowa dla KOPII tekstu wysylanej do modelu (rung-5 vision / LLM-sedzia).

Gdzie to sie miesci w konstytucji
--------------------------------
Article III mowi: redakcja dokumentu = czlowiek. Ten modul NIE redaguje dokumentu.
Kontrakt, bloki i tekst zrodlowy zostaja nietkniete. Maskowana jest wylacznie kopia,
ktora ma wyjsc do modelu (Article IV dopuszcza LLM tylko w rung-5, jawnie oznaczony).
Wartosc PESEL, NIP, IBAN, e-maila albo klucza API nie ma powodu opuszczac maszyny po to,
zeby model ocenil, czy pod tekstem jest podpis.

Dlaczego TA SAMA DLUGOSC
------------------------
Kazdy znak sekretu -> `*`. Dlugosc tekstu, pozycje wszystkich pozostalych znakow i numery
linii sa identyczne przed i po. Dzieki temu wszystko, co model zwroci z offsetem
(„fragment od znaku 120 do 158"), da sie odniesc do ORYGINALU bez przeliczania, a bbox
z `grounding_bridge` dalej pasuje. Wzorzec z `secret_anonymizer.py` w
sandbox-quantum/flintai-cli (Apache-2.0 z Commons Clause, wylacznie idea, zero kodu) -
tam maskuja klucze w kodzie zrodlowym, tu maskujemy PII PL i sekrety w tekscie akt.

Co maskuje
----------
1. PII PL z pii_flags (PESEL/NIP/REGON z suma kontrolna, IBAN, e-mail, dowod osobisty).
   Reuzycie tych samych regexow i walidatorow - jedno zrodlo prawdy, zero dryfu.
2. Sekrety maszynowe: znane prefiksy kluczy (sk-, AIza, ghp_, glpat-, xox*) i `Bearer <token>`.
3. Przypisania `KEY/TOKEN/SECRET/PASSWORD = "..."` w tekscie (akta bywaja zalacznikami
   technicznymi).

Czego NIE maskuje (swiadomie)
-----------------------------
Imion, nazwisk, adresow, sygnatur spraw. To robi anonimizacja wlasciwa (matematic-anonimizacja-pl)
z decyzja czlowieka. Tutaj tylko to, co da sie rozpoznac deterministycznie i co nigdy nie jest
potrzebne modelowi do zadania z rung-5.

Zero LLM, zero sieci, stdlib. Funkcja czysta: ten sam input -> ten sam output (Article IV).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from pii_flags import _RE_DOWOD, _RE_EMAIL, _RE_IBAN_PL, _RE_NIP, _RE_PESEL, _RE_REGON
from pii_flags import _valid_nip, _valid_pesel, _valid_regon

_ZNAK = "*"

_RE_KLUCZ_PREFIKS = re.compile(
    r"(?<![A-Za-z0-9])("
    r"sk-[A-Za-z0-9\-_]{10,}"
    r"|AIza[A-Za-z0-9_\-]{35,}"
    r"|ghp_[A-Za-z0-9]{30,}"
    r"|gho_[A-Za-z0-9]{30,}"
    r"|glpat-[A-Za-z0-9\-_]{20,}"
    r"|xox[bpras]-[A-Za-z0-9\-]{10,}"
    r")"
)
_RE_BEARER = re.compile(r"(Bearer\s+)([A-Za-z0-9\-_.~+/]+=*)", re.IGNORECASE)
_RE_PRZYPISANIE = re.compile(
    r"""(\b\w*(?:API_?KEY|TOKEN|SECRET|PASSWORD|HASLO|CREDENTIAL|PRIVATE_KEY|CLIENT_SECRET)\w*\s*[=:]\s*)(["'])(.+?)(\2)""",
    re.IGNORECASE,
)


@dataclass
class WynikMaski:
    tekst: str
    zamaskowane: list[dict] = field(default_factory=list)  # {kategoria, start, koniec}

    @property
    def liczba(self) -> int:
        return len(self.zamaskowane)


def _zamaskuj_zakres(znaki: list[str], start: int, koniec: int) -> None:
    for i in range(start, koniec):
        if not znaki[i].isspace():  # spacje i lamania linii zostaja - to one trzymaja uklad
            znaki[i] = _ZNAK


def maskuj(tekst: str) -> WynikMaski:
    """Zwraca kopie tekstu z zamaskowanymi PII/sekretami. `len(wynik.tekst) == len(tekst)` zawsze."""
    znaki = list(tekst)
    trafienia: list[tuple[str, int, int]] = []

    def dodaj(kat: str, m: re.Match, grupa: int = 0) -> None:
        trafienia.append((kat, m.start(grupa), m.end(grupa)))

    for m in _RE_PESEL.finditer(tekst):
        if _valid_pesel(m.group(0)):
            dodaj("pesel", m)
    for m in _RE_NIP.finditer(tekst):
        if _valid_nip(m.group(0)):
            dodaj("nip", m)
    for m in _RE_REGON.finditer(tekst):
        if _valid_regon(m.group(0)):
            dodaj("regon", m)
    for m in _RE_IBAN_PL.finditer(tekst):
        dodaj("iban", m)
    for m in _RE_EMAIL.finditer(tekst):
        dodaj("email", m)
    for m in _RE_DOWOD.finditer(tekst):
        dodaj("dowod", m)
    for m in _RE_KLUCZ_PREFIKS.finditer(tekst):
        dodaj("klucz_api", m, 1)
    for m in _RE_BEARER.finditer(tekst):
        dodaj("bearer", m, 2)
    for m in _RE_PRZYPISANIE.finditer(tekst):
        dodaj("przypisanie_sekretu", m, 3)

    # dedup po zakresie (PESEL moze byc tez REGON-14 itp.), zachowaj pierwsza kategorie
    widziane: set[tuple[int, int]] = set()
    zamaskowane = []
    for kat, s, k in sorted(trafienia, key=lambda t: (t[1], -t[2])):
        if any(s < kk and k > ss for ss, kk in widziane):
            continue
        widziane.add((s, k))
        _zamaskuj_zakres(znaki, s, k)
        zamaskowane.append({"kategoria": kat, "start": s, "koniec": k})

    wynik = WynikMaski("".join(znaki), zamaskowane)
    assert len(wynik.tekst) == len(tekst), "maska zmienila dlugosc - to lamie offsety"
    return wynik


if __name__ == "__main__":  # pragma: no cover
    import json
    import sys

    dane = sys.stdin.read()
    w = maskuj(dane)
    sys.stdout.write(w.tekst)
    sys.stderr.write(json.dumps({"zamaskowane": w.liczba, "kategorie": sorted({z["kategoria"] for z in w.zamaskowane})}) + "\n")
