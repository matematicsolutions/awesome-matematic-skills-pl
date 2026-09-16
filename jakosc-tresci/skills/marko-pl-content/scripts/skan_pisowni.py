#!/usr/bin/env python3
"""Skan pisowni pod zmiany zasad ortografii obowiazujace od 1 stycznia 2026 r.

Zrodlo zmian: Komunikat Rady Jezyka Polskiego przy Prezydium PAN z 10 maja 2024 r.
wraz ze zmiana z 7 listopada 2025 r. (wycofany pkt 8b). Opis wlasnymi slowami:
references/pisownia-2026.md.

Skaner zwraca KANDYDATOW, nie werdykty. Ta sama forma bywa bledem albo poprawna
pisownia - "nie" rozdzielnie zostaje przy przeciwstawieniu ("tanie, nie darmowe"),
a "odpowiadam na nie szybciej" to zaimek, nie partykula. Kazdego kandydata ocenia
czlowiek albo recenzent w kontekscie.

Uzycie:
  python skan_pisowni.py PLIK_LUB_KATALOG [...] [--json]
  echo "tekst" | python skan_pisowni.py -

Kod wyjscia (trojstan):
  0 = przeskanowano >=1 plik PL, zero kandydatow
  1 = sa kandydaci do oceny
  2 = BLOKADA - nic nie przeskanowano (pusty mianownik to nie sukces)
Stdlib, bez sieci.
"""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

L = "a-ząćęłńóśźż"
U = "A-ZĄĆĘŁŃÓŚŹŻ"
ROZSZERZENIA = {".md", ".markdown", ".txt", ".html", ".htm"}
POMIJANE_KATALOGI = {".git", "node_modules", "__pycache__", ".venv", "venv"}
POMIJANE_TAGI = {"script", "style", "code", "pre", "noscript", "svg"}

_P = "(?:y|a|e|ego|ej|ych|ym|ymi)"
KONC_IMIESLOW = rf"(?:ąc|an|on|ęt|ut|yt|it|art|ert){_P}"
# stopien wyzszy: spolgloska albo "ej" przed "sz" - odcina czasowniki typu "pisze", "rusza"
KONC_WYZSZY = rf"(?:[bcćdfghklłmnńprśtwzźż]|ej)sz{_P}"
PRZYSL_WYZSZY = ("lepiej|gorzej|łatwiej|trudniej|szybciej|wolniej|taniej|drożej|prościej|częściej|"
                 "rzadziej|dłużej|krócej|mocniej|słabiej|dokładniej|pewniej|bezpieczniej|skuteczniej")
KONC_PRZYM = rf"(?:(?:n|ow|czn|aln|iw|liw|ist|ln|dn|pn|żn|wn){_P}|(?:sk|ck)(?:i|a|ie|iego|iej|ich|im|imi))"
PRZYSL = "często|rzadko|długo|łatwo|trudno|dużo|mało|dobrze|daleko|blisko|jasno|pewno"

# Czasowniki, rzeczowniki i zaimki o koncowce przymiotnika/imieslowu - heurystyka
# zbudowana na probce tekstow, nie slownik.
NIE_PRZYMIOTNIK = set("""
zna można ocena one powinna powinny powinno różni spina spóźni stanowi wspomina wzmocni zaczyna zmieni
chowa czyni domena godziny maszyny środowiska archiwa zmienia ochrania wyjaśnia przypomina zapomina
anegdota argumenty chroni czyta dlatego estymata klienta komunikaty lista ochroni przeczyta pyta
skorzysta teksty wykona zadzwoni zapyta zgłasza pogarsza wystarczy wystarcza wynika wymaga
pamięta zapamięta jedna jednego jeden jedno żadna żadne żadnego ona ono ani sama samo same tyle wiele tak
""".split())
PRZYIMEK_PRZED_ZAIMKIEM = re.compile(r"\b(?:na|za|przez|o|w|we|po|ponad|pod|nad|przed|między|dla)\s+$", re.I)

REGULY: list[tuple[str, str, re.Pattern]] = [
    ("R4_nie_imieslow", "pkt 4",
     re.compile(rf"\bnie\s+([{L}]+{KONC_IMIESLOW})\b", re.I)),
    ("R11_nie_stopien_wyzszy", "pkt 11",
     re.compile(rf"\bnie\s+((?:naj)?[{L}]+{KONC_WYZSZY}|(?:naj)?(?:{PRZYSL_WYZSZY}))\b", re.I)),
    ("R11_nie_przymiotnik", "pkt 11",
     re.compile(rf"\bnie\s+([{L}]+{KONC_PRZYM})\b", re.I)),
    ("R11_nie_przyslowek", "pkt 11",
     re.compile(rf"\bnie\s+({PRZYSL})\b", re.I)),
    ("R3_czyby_lacznie", "pkt 3",
     re.compile(r"\bczyby(?:m|ś|śmy|ście)?\b", re.I)),
    ("R1_mieszkaniec_mala_litera", "pkt 1",
     re.compile(rf"\b(?:warszawian|krakowian|poznaniak|poznanian|wrocławian|gdańszczan|łodzian|lublinian|"
                rf"szczecinian|katowiczan|bydgoszczan|gdynian|sopocian|torunian|białostoczan|rzeszowian|"
                rf"olsztynian|opolan)[{L}]*\b")),
    ("R6_pol_rozdzielnie", "pkt 6",
     re.compile(rf"\bpół\s+(żartem|serio|prywatnie|oficjalnie|żartu|zabawa|nauka|śpiąc)\b", re.I)),
    ("R10_niby_quasi", "pkt 10",
     re.compile(rf"\b(?:niby|quasi)(?:\s+|-)[{L}]", re.I)),
    # tylko polskie slowa po laczniku: znak diakrytyczny albo polska koncowka - angielskie
    # "post-deployment", "multi-agent" nie sa przedmiotem reguly
    ("R9_przedrostek_lacznik", "pkt 9a",
     re.compile(rf"\b(?i:super|ekstra|eko|wege|mini|maksi|midi|mega|makro|anty|cyber|mikro|multi|pseudo|post|pre|neo)"
                rf"-(?=[{L}]*[ąćęłńóśźż]|[{L}]+(?:acji|acją|acja|enia|enie|ania|anie|ości|ość|owy|owa|owe|owego|owej|owych|ów|ych|ami|ie|ony|ona|one|ego|ek)\b)[{L}]+")),
    ("R8c_obiekt_mala_litera", "pkt 8c",
     re.compile(rf"\b(?:aleja|alei|plac|placu|park|parku|most|mostu|pomnik|pomnika|pałac|pałacu|zamek|zamku|"
                rf"kościół|kościoła|cmentarz|cmentarza|bulwar|kopiec|brama|bramy)\s+[{U}][{L}]{{2,}}")),
    ("R8e_nagroda_mala_litera", "pkt 8e",
     re.compile(rf"\b(?:[nN]agrod[{L}]*|[oO]rder[{L}]*|[mM]edal[{L}]*)\s+(?:nobla|pulitzera)\b")),
]
NIEZMIERZONE = {
    "pkt 2": "egzemplarz wyrobu marki (czerwony Ford) - wymaga rozpoznania znaczenia",
    "pkt 5": "przymiotniki od nazw osobowych - wymaga slownika",
    "pkt 7": "pary rownorzedne - trzy warianty dopuszczone, nie ma bledu do wykrycia",
    "pkt 8a": "nazwy komet",
    "pkt 8d": "nazwy lokali uslugowych - wymaga rozpoznania nazwy",
}
KONTRAST_PO = re.compile(r"^\s*[,-]?\s*(?:lecz|ale|tylko|a|zaś)\b", re.I)
KONTRAST_PRZED = re.compile(r"(?:,|\s-|\ba|\bto)\s*$", re.I)


class _Html(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lang: str | None = None
        self.gleb = 0
        self.segmenty: list[tuple[int, str]] = []

    def handle_starttag(self, tag, attrs):
        if tag == "html":
            self.lang = dict(attrs).get("lang")
        if tag in POMIJANE_TAGI:
            self.gleb += 1

    def handle_endtag(self, tag):
        if tag in POMIJANE_TAGI and self.gleb:
            self.gleb -= 1

    def handle_data(self, data):
        if not self.gleb and data.strip():
            self.segmenty.append((self.getpos()[0], data))


def segmenty_html(tekst: str) -> tuple[str | None, list[tuple[int, str]]]:
    p = _Html()
    p.feed(tekst)
    return p.lang, p.segmenty


def segmenty_md(tekst: str) -> list[tuple[int, str]]:
    wynik, w_bloku = [], False
    for nr, linia in enumerate(tekst.splitlines(), start=1):
        if re.match(r"^\s*(```|~~~)", linia):
            w_bloku = not w_bloku
            continue
        if w_bloku:
            continue
        wynik.append((nr, re.sub(r"`[^`\n]*`", lambda m: " " * len(m.group(0)), linia)))
    return wynik


def _sklej(segmenty: list[tuple[int, str]]) -> tuple[str, list[tuple[int, int]]]:
    """Laczy segmenty w jeden tekst (dopasowanie moze przejsc przez koniec linii),
    zapamietujac offset poczatku kazdego segmentu i jego numer linii."""
    czesci, mapa, off = [], [], 0
    for linia, s in segmenty:
        mapa.append((off, linia, s))
        czesci.append(s)
        off += len(s) + 1
    return "\n".join(czesci), mapa


def _linia(mapa, pozycja: int) -> int:
    wynik = mapa[0][1] if mapa else 1
    for off, linia, s in mapa:
        if off > pozycja:
            break
        # linia wewnatrz segmentu wieloliniowego (np. akapit HTML)
        wynik = linia + s.count("\n", 0, pozycja - off)
    return wynik


def skanuj(segmenty: list[tuple[int, str]]) -> list[dict]:
    tekst, mapa = _sklej(segmenty)
    wyniki, zajete = [], set()
    for nazwa, punkt, rx in REGULY:
        for m in rx.finditer(tekst):
            if m.start() in zajete:
                continue
            przed = tekst[max(0, m.start() - 80):m.start()]
            po = tekst[m.end():m.end() + 80]
            if nazwa.startswith(("R4", "R11")):
                slowo = m.group(1).lower()
                if slowo in NIE_PRZYMIOTNIK or PRZYIMEK_PRZED_ZAIMKIEM.search(przed):
                    continue
            zajete.add(m.start())
            kontekst = re.sub(r"\s+", " ", przed[-60:] + "[[" + m.group(0) + "]]" + po[:60]).strip()
            wyniki.append({
                "linia": _linia(mapa, m.start()),
                "regula": nazwa,
                "punkt_komunikatu": punkt,
                "trafienie": re.sub(r"\s+", " ", m.group(0)),
                "sygnal_przeciwstawienia": bool(KONTRAST_PO.match(po) or KONTRAST_PRZED.search(przed)),
                "kontekst": kontekst,
            })
    return sorted(wyniki, key=lambda w: w["linia"])


def skanuj_plik(sciezka: Path) -> tuple[bool, str, list[dict]]:
    """Zwraca (czy_przeskanowano, powod_pominiecia, kandydaci)."""
    tekst = sciezka.read_text(encoding="utf-8", errors="replace")
    if sciezka.suffix.lower() in {".html", ".htm"}:
        lang, seg = segmenty_html(tekst)
        if lang and not lang.lower().startswith("pl"):
            return False, f"lang={lang}", []
    elif sciezka.suffix.lower() in {".md", ".markdown"}:
        seg = segmenty_md(tekst)
    else:
        seg = list(enumerate(tekst.splitlines(), start=1))
    return True, "", skanuj(seg)


def zbierz_pliki(argumenty: list[str]) -> list[Path]:
    pliki = []
    for a in argumenty:
        p = Path(a)
        if p.is_dir():
            pliki += sorted(x for x in p.rglob("*")
                            if x.is_file() and x.suffix.lower() in ROZSZERZENIA
                            and not POMIJANE_KATALOGI.intersection(x.parts))
        elif p.is_file():
            pliki.append(p)
    return pliki


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    jako_json = "--json" in argv
    cele = [a for a in argv if a != "--json"]
    raport, przeskanowane, pominiete = [], 0, {}

    if cele == ["-"]:
        przeskanowane = 1
        for w in skanuj(list(enumerate(sys.stdin.read().splitlines(), start=1))):
            raport.append({"plik": "<stdin>", **w})
    else:
        for p in zbierz_pliki(cele):
            ok, powod, kandydaci = skanuj_plik(p)
            if not ok:
                pominiete[powod] = pominiete.get(powod, 0) + 1
                continue
            przeskanowane += 1
            raport += [{"plik": p.as_posix(), **w} for w in kandydaci]

    kod = 2 if przeskanowane == 0 else (1 if raport else 0)
    if jako_json:
        print(json.dumps({"przeskanowane_pliki": przeskanowane, "pominiete": pominiete,
                          "kandydaci": raport, "niezmierzone": NIEZMIERZONE, "kod": kod},
                         ensure_ascii=False, indent=1))
        return kod

    for w in raport:
        znak = " [przeciwstawienie?]" if w["sygnal_przeciwstawienia"] else ""
        print(f"{w['plik']}:{w['linia']}  {w['regula']} ({w['punkt_komunikatu']}){znak}  {w['kontekst']}")
    print(f"MIANOWNIK: {przeskanowane} plik(ow) PL, pominiete: {pominiete or 'brak'}")
    print(f"KANDYDACI: {len(raport)} (to nie werdykty - kazdy ocen w kontekscie)")
    print("NIEZMIERZONE: " + ", ".join(NIEZMIERZONE))
    if kod == 2:
        print("BLOKADA: nic nie przeskanowano - brak werdyktu o pisowni")
    return kod


if __name__ == "__main__":
    sys.exit(main())
