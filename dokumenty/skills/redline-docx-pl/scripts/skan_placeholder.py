#!/usr/bin/env python3
"""Skaner placeholderow - bramka "czy draft nie wychodzi z dziurami".

Wykrywa w .docx / .md / .txt niedokonczone pola: [...], [wstaw ...],
[insert ...], TBD, DO UZUPELNIENIA, $X, ___, NN/RR, puste daty i kwoty.
Raport plik:pozycja (paragraf w .docx, linia w tekscie) + kontekst.

Pattern (skan placeholderow przed wysylka): evolsb/legal-redline-tools (MIT).
Kod napisany od zera, zero zaleznosci (Python stdlib), wzorce rozszerzone
o polskie realia (DO UZUPELNIENIA, NN/RR, dnia __, kwoty w zl).

Uzycie:
    python skan_placeholder.py umowa.docx pismo.md
    python skan_placeholder.py umowa.docx --json

Exit: 0 = czysto, 1 = znaleziska, 2 = blad IO.
"""

import argparse
import json
import re
import sys
import zipfile

WZORCE = [
    ("nawias-pusty", re.compile(r"\[\s*\]|\[\s*\.\.\.\s*\]|\[\s*…\s*\]|\[_+\]")),
    ("nawias-instrukcja", re.compile(
        r"\[\s*(insert|enter|wstaw|uzupelnij|uzupełnij|podac|podać|"
        r"data|date|kwota|amount|nazwa|name|imie|imię|adres|nip|pesel|krs)\b[^\]]*\]",
        re.IGNORECASE)),
    ("tbd", re.compile(r"\bTBD\b|\bT\.B\.D\.\b")),
    ("do-uzupelnienia", re.compile(r"\bDO\s+UZUPEŁNIENIA\b|\bDO\s+UZUPELNIENIA\b", re.IGNORECASE)),
    ("kwota-x", re.compile(r"[$€]\s*[Xx_]{1,4}\b|\b[Xx]{2,4}\s*(zl|zł|PLN|EUR)\b")),
    ("podkreslenia", re.compile(r"_{3,}")),
    ("sygnatura-placeholder", re.compile(r"\bNN/RR\b")),
    ("pusta-data", re.compile(
        r"\bdnia\s+_+|\bdnia\s+\[|\[\s*(data|dzien|dzień)\s*\]|"
        r"\b__\.\d{2}\.\d{4}\b|\b\d{2}\.__\.\d{4}\b", re.IGNORECASE)),
    ("pusta-kwota", re.compile(
        r"\[\s*kwota[^\]]*\]|\b0[,.]00\s*(zl|zł|PLN|EUR)\b", re.IGNORECASE)),
]

RE_PARAGRAF = re.compile(r"<w:p[ >].*?</w:p>", re.DOTALL)
RE_TEKST_W = re.compile(r"<w:t[^>]*>(.*?)</w:t>", re.DOTALL)
RE_TAG = re.compile(r"<[^>]+>")


def akapity_docx(sciezka):
    """Zwraca liste (pozycja, tekst) dla paragrafow document.xml (+ naglowki/stopki)."""
    wyniki = []
    with zipfile.ZipFile(sciezka) as z:
        czesci = ["word/document.xml"]
        czesci += sorted(n for n in z.namelist()
                         if re.match(r"word/(header|footer)\d*\.xml$", n))
        for czesc in czesci:
            try:
                xml = z.read(czesc).decode("utf-8", errors="replace")
            except KeyError:
                continue
            etykieta = "par" if czesc == "word/document.xml" else czesc.split("/")[-1]
            for i, p in enumerate(RE_PARAGRAF.findall(xml), start=1):
                tekst = "".join(odkoduj(t) for t in RE_TEKST_W.findall(p))
                if tekst.strip():
                    wyniki.append(("%s %d" % (etykieta, i), tekst))
    return wyniki


def odkoduj(s):
    return (s.replace("&amp;", "&").replace("&lt;", "<")
             .replace("&gt;", ">").replace("&quot;", '"').replace("&apos;", "'"))


def linie_tekstu(sciezka):
    with open(sciezka, "r", encoding="utf-8", errors="replace") as f:
        return [("linia %d" % i, ln.rstrip("\n")) for i, ln in enumerate(f, start=1)]


def kontekst(tekst, start, koniec, margines=30):
    a = max(0, start - margines)
    b = min(len(tekst), koniec + margines)
    frag = tekst[a:b].strip()
    return ("..." if a > 0 else "") + frag + ("..." if b < len(tekst) else "")


def skanuj_plik(sciezka):
    znaleziska = []
    if sciezka.lower().endswith(".docx"):
        jednostki = akapity_docx(sciezka)
    else:
        jednostki = linie_tekstu(sciezka)
    for pozycja, tekst in jednostki:
        for nazwa, wzorzec in WZORCE:
            for m in wzorzec.finditer(tekst):
                znaleziska.append({
                    "plik": sciezka,
                    "pozycja": pozycja,
                    "wzorzec": nazwa,
                    "dopasowanie": m.group(0),
                    "kontekst": kontekst(tekst, m.start(), m.end()),
                })
    return znaleziska


def main():
    ap = argparse.ArgumentParser(description="Skan placeholderow w draftach")
    ap.add_argument("pliki", nargs="+", help=".docx / .md / .txt")
    ap.add_argument("--json", action="store_true", help="raport JSON zamiast tekstu")
    args = ap.parse_args()

    wszystkie = []
    for p in args.pliki:
        try:
            wszystkie.extend(skanuj_plik(p))
        except (OSError, zipfile.BadZipFile) as exc:
            print("BLAD IO: %s: %s" % (p, exc), file=sys.stderr)
            return 2

    if args.json:
        print(json.dumps(wszystkie, ensure_ascii=False, indent=2))
    else:
        for z in wszystkie:
            print("%s:%s  [%s]  %r  |  %s"
                  % (z["plik"], z["pozycja"], z["wzorzec"],
                     z["dopasowanie"], z["kontekst"]))
        print("---")
        if wszystkie:
            print("ZNALEZISKA: %d - draft NIE jest gotowy do wysylki." % len(wszystkie))
        else:
            print("CZYSTO: zero placeholderow w %d pliku/plikach." % len(args.pliki))

    return 1 if wszystkie else 0


if __name__ == "__main__":
    sys.exit(main())
