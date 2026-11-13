#!/usr/bin/env python3
"""Smoke test silnika adeu na dlugiej, syntetycznej umowie PL (zero danych z akt).

Uruchamiaj po kazdej zmianie wersji adeu:

    python scripts/smoke_adeu.py                 # wersja z pinu ponizej
    python scripts/smoke_adeu.py --wersja 3.2.1  # kandydat do podniesienia pinu

Dokument jest dluzszy niz jedna syntetyczna strona adeu, a zmiana idzie w OSTATNI
paragraf, wiec test czerwienieje, gdy extract odda tylko strone 1 albo gdy zmiana
nie zostanie naniesiona poza nia. Kontrola pozytywna: `--bez-page-all` wymusza
`--page 1` i musi dac BLOKADE (bramki, ktorej nie widzialo sie na czerwono, sie nie ma).

UWAGA (nie blokada) = znane ograniczenie danej wersji, poprawione w nowszej:
numery list w extract (od 3.2.2), `-o` bez `--page` oddaje caly dokument (od 3.2.2),
komunikat na stderr przy czesciowym wyniku (od 3.2.2).

Wyjscie: trojstan OK / UWAGI / BLOKADA z pelnym mianownikiem. Kod: 0 / 10 / 20.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

PIN = "1.30.0"
LICZBA_PARAGRAFOW = 600
AUTOR = "Kancelaria Smoke"
METADANE_AUTORA = "Jan Testowy"
TRESC = (
    "Strona zobowiązuje się do wykonania usługi zgodnie z harmonogramem, a druga "
    "strona do zapłaty wynagrodzenia w terminie określonym w niniejszej umowie. "
)
ZNACZNIK = re.compile(r"ZNACZNIK-\d{5}")

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
CONTENT_TYPES = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
    "</Types>"
)
RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
    "</Relationships>"
)
CORE = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
    'xmlns:dc="http://purl.org/dc/elements/1.1/">'
    f"<dc:creator>{METADANE_AUTORA}</dc:creator>"
    f"<cp:lastModifiedBy>{METADANE_AUTORA}</cp:lastModifiedBy>"
    "</cp:coreProperties>"
)


def zbuduj_docx(sciezka: Path) -> None:
    akapity = []
    for i in range(1, LICZBA_PARAGRAFOW + 1):
        tekst = f"§ {i}. ZNACZNIK-{i:05d} " + TRESC * 3
        akapity.append(
            f'<w:p><w:r><w:t xml:space="preserve">{escape(tekst)}</w:t></w:r></w:p>'
        )
    dokument = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W_NS}"><w:body>' + "".join(akapity) + "</w:body></w:document>"
    )
    with zipfile.ZipFile(sciezka, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)
        z.writestr("docProps/core.xml", CORE)
        z.writestr("word/document.xml", dokument)


class Smoke:
    def __init__(self, wersja: str, katalog: Path) -> None:
        uvx = shutil.which("uvx")
        if not uvx:
            print("BLOKADA: brak uvx na PATH")
            sys.exit(20)
        self.komenda = [uvx, "--from", f"adeu=={wersja}", "adeu"]
        self.katalog = katalog
        self.wyniki: list[tuple[str, bool, str, bool]] = []

    def adeu(self, *argumenty: str) -> subprocess.CompletedProcess:
        env = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
        return subprocess.run(
            [*self.komenda, *argumenty],
            cwd=self.katalog,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=300,
        )

    def zapisz(self, nazwa: str, ok: bool, szczegol: str, uwaga: bool = False) -> None:
        """`uwaga=True`: porazka to znane ograniczenie wersji (UWAGI), nie BLOKADA."""
        self.wyniki.append((nazwa, ok, szczegol, uwaga))


def xml(sciezka: Path, czesc: str = "word/document.xml") -> str:
    return zipfile.ZipFile(sciezka).read(czesc).decode("utf-8")


def znaczniki(sciezka: Path) -> set[str]:
    if not sciezka.exists():
        return set()
    return set(ZNACZNIK.findall(sciezka.read_text(encoding="utf-8")))


def przebieg(s: Smoke, bez_page_all: bool) -> None:
    baza = "umowa.docx"
    zbuduj_docx(s.katalog / baza)

    # Warunek testu: dokument MUSI wychodzic poza strone 1, inaczej nic nie mierzymy.
    r = s.adeu("extract", baza, "--page", "1", "-o", "strona1.md")
    z1 = znaczniki(s.katalog / "strona1.md")
    s.zapisz(
        "dokument dluzszy niz strona 1",
        r.returncode == 0 and 0 < len(z1) < LICZBA_PARAGRAFOW,
        f"exit {r.returncode}, strona 1 = {len(z1)}/{LICZBA_PARAGRAFOW} paragrafow",
    )
    komunikat = any(k in r.stderr.lower() for k in ("page 1 of", "partial", "--page all"))
    s.zapisz("extract --page 1: komunikat o czesci na stderr", komunikat, r.stderr.strip()[:90] or "stderr pusty", uwaga=True)

    r = s.adeu("extract", baza, "-o", "domyslnie.md")
    zd = znaczniki(s.katalog / "domyslnie.md")
    s.zapisz("extract -o bez --page: caly dokument", r.returncode == 0 and len(zd) == LICZBA_PARAGRAFOW, f"{len(zd)}/{LICZBA_PARAGRAFOW}", uwaga=True)

    argumenty = ["extract", baza, "--page", "1" if bez_page_all else "all", "-o", "calosc.md"]
    r = s.adeu(*argumenty)
    z = znaczniki(s.katalog / "calosc.md")
    tekst = (s.katalog / "calosc.md").read_text(encoding="utf-8") if z else ""
    s.zapisz(
        "extract: caly dokument",
        r.returncode == 0 and len(z) == LICZBA_PARAGRAFOW,
        f"exit {r.returncode}, {len(z)}/{LICZBA_PARAGRAFOW} paragrafow",
    )
    s.zapisz("extract: polskie znaki", "zobowiązuje" in tekst and "zapłaty" in tekst, "diakrytyki w tekscie")

    cel = f"ZNACZNIK-{LICZBA_PARAGRAFOW:05d}"
    (s.katalog / "edits.json").write_text(
        json.dumps(
            [{"type": "modify", "target_text": cel, "new_text": "ZNACZNIK-ZMIANA-KOŃCOWA", "comment": "Smoke."}],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    r = s.adeu("apply", baza, "edits.json", "-o", "redline.docx", "--author", AUTOR)
    redline = s.katalog / "redline.docx"
    if r.returncode == 0 and redline.exists():
        x = xml(redline)
        wstawienia = len(re.findall(r"<w:ins[ >]", x))
        usuniecia = len(re.findall(r"<w:del[ >]", x))
        del_text = len(re.findall(r"<w:delText", x))
        s.zapisz(
            "apply: sledzone zmiany w ostatnim paragrafie",
            wstawienia > 0 and usuniecia > 0 and del_text > 0 and "ZMIANA-KOŃCOWA" in x,
            f"w:ins {wstawienia}, w:del {usuniecia}, w:delText {del_text}",
        )
        s.zapisz("apply: autor z --author", f'w:author="{AUTOR}"' in x, AUTOR)
    else:
        s.zapisz("apply: sledzone zmiany w ostatnim paragrafie", False, f"exit {r.returncode}: {r.stderr[-200:]}")
        return

    r = s.adeu("extract", "redline.docx", "--page", "all", "-o", "redline.md")
    widac = "ZMIANA-KOŃCOWA" in (s.katalog / "redline.md").read_text(encoding="utf-8") if r.returncode == 0 else False
    s.zapisz("extract widzi zmiane z apply", widac, f"exit {r.returncode}")

    r = s.adeu("sanitize", "redline.docx", "-o", "clean.docx", "--keep-markup", "--author", AUTOR, "--report")
    wyjscie = r.stdout + r.stderr
    clean = s.katalog / "clean.docx"
    s.zapisz("sanitize: Result: CLEAN", r.returncode == 0 and "Result: CLEAN" in wyjscie, f"exit {r.returncode}")
    if clean.exists():
        s.zapisz("sanitize: metadane autora usuniete", METADANE_AUTORA not in xml(clean, "docProps/core.xml"), "docProps/core.xml")
        s.zapisz("sanitize: zmiany zachowane", bool(re.search(r"<w:ins[ >]", xml(clean))), "--keep-markup")
    else:
        s.zapisz("sanitize: metadane autora usuniete", False, "brak clean.docx")
        s.zapisz("sanitize: zmiany zachowane", False, "brak clean.docx")


OBCY_AUTOR = "Druga Strona"
NUMBERING = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    f'<w:numbering xmlns:w="{W_NS}">'
    '<w:abstractNum w:abstractNumId="0"><w:lvl w:ilvl="0"><w:start w:val="1"/>'
    '<w:numFmt w:val="decimal"/><w:lvlText w:val="%1."/></w:lvl></w:abstractNum>'
    '<w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num></w:numbering>'
)
DOC_RELS = (
    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>'
    "</Relationships>"
)


def run(tekst: str, pogrubiony: bool = False) -> str:
    rpr = "<w:rPr><w:b/></w:rPr>" if pogrubiony else ""
    return f'<w:r>{rpr}<w:t xml:space="preserve">{escape(tekst)}</w:t></w:r>'


def zbuduj_format(sciezka: Path, kontrola: bool) -> None:
    """Umowa z formatowaniem. `kontrola` usuwa numeracje i cudze zmiany: te kontrole musza wtedy dac BLOKADE."""
    num = "" if kontrola else '<w:pPr><w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr></w:pPr>'
    lista = "".join(f"<w:p>{num}{run(f'ZNACZNIK-LISTA-{i} obowiązek strony numer {i}.')}</w:p>" for i in range(1, 4))
    komorka = lambda t: f"<w:tc><w:p>{run(t)}</w:p></w:tc>"  # noqa: E731
    tabela = (
        "<w:tbl><w:tblPr/><w:tblGrid><w:gridCol/><w:gridCol/></w:tblGrid>"
        f"<w:tr>{komorka('Pozycja')}{komorka('Wynagrodzenie')}</w:tr>"
        f"<w:tr>{komorka('ZNACZNIK-TABELA usługa')}{komorka('kwota 100 zł netto')}</w:tr></w:tbl>"
    )
    data = 'w:date="2026-01-15T10:00:00Z"'
    if kontrola:
        obce = run("Początek ZNACZNIK-WSTAWKA-OBCA ZNACZNIK-USUNIETY-OBCY dalszy tekst.")
    else:
        obce = (
            run("Początek ")
            + f'<w:ins w:id="901" w:author="{OBCY_AUTOR}" {data}>{run("ZNACZNIK-WSTAWKA-OBCA ")}</w:ins>'
            + f'<w:del w:id="902" w:author="{OBCY_AUTOR}" {data}><w:r><w:delText xml:space="preserve">ZNACZNIK-USUNIETY-OBCY </w:delText></w:r></w:del>'
            + run("dalszy tekst.")
        )
    rozbity = run("Termin: ZNACZNIK-", pogrubiony=True) + run("ROZBITY zapłaty wynosi 30 dni.")
    dokument = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{W_NS}"><w:body>{lista}{tabela}<w:p>{obce}</w:p><w:p>{rozbity}</w:p></w:body></w:document>'
    )
    typy = CONTENT_TYPES.replace(
        "</Types>",
        '<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/></Types>',
    )
    with zipfile.ZipFile(sciezka, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", typy)
        z.writestr("_rels/.rels", RELS)
        z.writestr("docProps/core.xml", CORE)
        z.writestr("word/document.xml", dokument)
        z.writestr("word/numbering.xml", NUMBERING)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)


def akapit_z(x: str, tekst: str) -> str:
    for p in re.findall(r"<w:p[ >].*?</w:p>", x, re.S):
        if tekst in p:
            return p
    return ""


def przebieg_format(s: Smoke, kontrola: bool) -> None:
    baza = "format.docx"
    zbuduj_format(s.katalog / baza, kontrola)
    r = s.adeu("extract", baza, "--page", "all", "-o", "format.md")
    md = (s.katalog / "format.md").read_text(encoding="utf-8") if r.returncode == 0 else ""
    if md:
        (Path(s.podglad) / f"format_{s.wersja}.md").write_text(md, encoding="utf-8") if s.podglad else None
    for nazwa, znak in [("lista", "ZNACZNIK-LISTA-2"), ("tabela", "kwota 100"), ("cudze wstawienie", "ZNACZNIK-WSTAWKA-OBCA"), ("cudze usuniecie", "ZNACZNIK-USUNIETY-OBCY")]:
        s.zapisz(f"format extract: {nazwa}", znak in md, f"exit {r.returncode}")
    numery = all(re.search(rf"^{i}\. ZNACZNIK-LISTA-{i}\b", md, re.M) for i in (1, 2, 3))
    s.zapisz("format extract: numery listy 1-2-3", numery, "rozwiazana numeracja OOXML", uwaga=True)

    def zastosuj(nazwa: str, cel: str, nowy: str) -> Path | None:
        (s.katalog / f"{nazwa}.json").write_text(
            json.dumps([{"type": "modify", "target_text": cel, "new_text": nowy}], ensure_ascii=False), encoding="utf-8"
        )
        wy = f"{nazwa}.docx"
        r = s.adeu("apply", baza, f"{nazwa}.json", "-o", wy, "--author", AUTOR)
        ok = r.returncode == 0 and (s.katalog / wy).exists()
        s.zapisz(f"format apply: {nazwa}", ok, f"exit {r.returncode} {(r.stdout + r.stderr).strip()[-140:] if not ok else ''}".strip())
        return s.katalog / wy if ok else None

    p = zastosuj("tabela", "kwota 100 zł", "kwota 250 zł")
    if p:
        kom = [t for t in re.findall(r"<w:tc[ >].*?</w:tc>", xml(p), re.S) if "250" in t]
        s.zapisz("format tabela: zmiana sledzona w komorce", any(re.search(r"<w:ins[ >]", t) for t in kom), f"komorek ze zmiana {len(kom)}")
        s.zapisz("format tabela: tabela nienaruszona", xml(p).count("<w:tc>") + xml(p).count("<w:tc ") == 4, "4 komorki")

    p = zastosuj("lista", "ZNACZNIK-LISTA-2 obowiązek", "ZNACZNIK-LISTA-2 uprawnienie")
    if p:
        x = xml(p)
        s.zapisz("format lista: zmiana sledzona", "uprawnienie" in x and bool(re.search(r"<w:ins[ >]", x)), "w:ins")
        s.zapisz("format lista: numeracja zachowana", x.count("<w:numPr>") == 3, f"w:numPr {x.count('<w:numPr>')}/3")
        s.zapisz("format cudze zmiany: autor zachowany", x.count(f'w:author="{OBCY_AUTOR}"') == 2, f"{x.count(f'w:author={chr(34)}{OBCY_AUTOR}{chr(34)}')}/2")
        s.zapisz("format cudze zmiany: usuniecie w w:delText", bool(re.search(r"<w:delText[^>]*>ZNACZNIK-USUNIETY-OBCY", x)), "w:delText")

    p = zastosuj("rozbity", "ZNACZNIK-ROZBITY zapłaty wynosi 30", "ZNACZNIK-ROZBITY zapłaty wynosi 60")
    if p:
        ak = akapit_z(xml(p), "ROZBITY")
        s.zapisz("format rozbity tekst: zmiana sledzona", "60" in re.sub(r"<[^>]+>", "", ak) and bool(re.search(r"<w:ins[ >]", ak)), "akapit z pogrubieniem")
        s.zapisz("format rozbity tekst: pogrubienie zachowane", "<w:b/>" in ak, "w:b")
        r = s.adeu("sanitize", p.name, "-o", "format_clean.docx", "--keep-markup", "--author", AUTOR, "--report")
        s.zapisz("format sanitize: Result: CLEAN", r.returncode == 0 and "Result: CLEAN" in r.stdout + r.stderr, f"exit {r.returncode}")
        c = s.katalog / "format_clean.docx"
        if c.exists():
            x = xml(c)
            s.zapisz("format sanitize: cudzy autor podmieniony", OBCY_AUTOR not in x, "brak nazwy drugiej strony")
            s.zapisz("format sanitize: cudze usuniecie zostalo", bool(re.search(r"<w:delText[^>]*>ZNACZNIK-USUNIETY-OBCY", x)), "--keep-markup")
        else:
            s.zapisz("format sanitize: plik wynikowy", False, "brak format_clean.docx")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--wersja", default=PIN, help=f"wersja adeu (domyslnie pin {PIN})")
    p.add_argument("--bez-page-all", action="store_true", help="kontrola pozytywna: wymusza --page 1, musi dac BLOKADE")
    p.add_argument("--kontrola-formatu", action="store_true", help="kontrola pozytywna scenariusza formatowania: musi dac BLOKADE")
    p.add_argument("--podglad", help="katalog na podglad markdownu z extract (diagnostyka)")
    a = p.parse_args()

    with tempfile.TemporaryDirectory(prefix="smoke_adeu_") as t:
        s = Smoke(a.wersja, Path(t))
        s.wersja, s.podglad = a.wersja, a.podglad
        przebieg(s, a.bez_page_all)
        przebieg_format(s, a.kontrola_formatu)

    zdane = sum(1 for _, ok, _, _ in s.wyniki if ok)
    blokady = sum(1 for _, ok, _, uw in s.wyniki if not ok and not uw)
    uwagi = sum(1 for _, ok, _, uw in s.wyniki if not ok and uw)
    for nazwa, ok, szczegol, uw in s.wyniki:
        print(f"[{'OK' if ok else ('UWAGA' if uw else 'BLOKADA')}] {nazwa} - {szczegol}")
    stan = "BLOKADA" if not s.wyniki or blokady else ("UWAGI" if uwagi else "OK")
    print(f"\nadeu {a.wersja}: {zdane}/{len(s.wyniki)} kontroli, uwagi {uwagi}, blokady {blokady}. Stan: {stan}")
    return {"OK": 0, "UWAGI": 10, "BLOKADA": 20}[stan]


if __name__ == "__main__":
    raise SystemExit(main())
