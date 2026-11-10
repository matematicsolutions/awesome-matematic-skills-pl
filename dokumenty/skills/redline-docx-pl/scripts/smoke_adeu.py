#!/usr/bin/env python3
"""Smoke test silnika adeu na dlugiej, syntetycznej umowie PL (zero danych z akt).

Uruchamiaj po kazdej zmianie wersji adeu:

    python scripts/smoke_adeu.py                 # wersja z pinu ponizej
    python scripts/smoke_adeu.py --wersja 3.2.1  # kandydat do podniesienia pinu

Dokument jest dluzszy niz jedna syntetyczna strona adeu, a zmiana idzie w OSTATNI
paragraf, wiec test czerwienieje, gdy extract odda tylko strone 1 albo gdy zmiana
nie zostanie naniesiona poza nia. Kontrola pozytywna: `--bez-page-all` musi dac
BLOKADE (bramki, ktorej nie widzialo sie na czerwono, sie nie ma).

Wyjscie: trojstan OK / BLOKADA z pelnym mianownikiem. Kod: 0 = OK, 20 = BLOKADA.
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
        self.wyniki: list[tuple[str, bool, str]] = []

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

    def zapisz(self, nazwa: str, ok: bool, szczegol: str) -> None:
        self.wyniki.append((nazwa, ok, szczegol))


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
    r = s.adeu("extract", baza, "-o", "strona1.md")
    z1 = znaczniki(s.katalog / "strona1.md")
    s.zapisz(
        "dokument dluzszy niz strona 1",
        r.returncode == 0 and 0 < len(z1) < LICZBA_PARAGRAFOW,
        f"exit {r.returncode}, strona 1 = {len(z1)}/{LICZBA_PARAGRAFOW} paragrafow",
    )

    argumenty = ["extract", baza, "-o", "calosc.md"]
    if not bez_page_all:
        argumenty[2:2] = ["--page", "all"]
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


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--wersja", default=PIN, help=f"wersja adeu (domyslnie pin {PIN})")
    p.add_argument("--bez-page-all", action="store_true", help="kontrola pozytywna: musi dac BLOKADE")
    a = p.parse_args()

    with tempfile.TemporaryDirectory(prefix="smoke_adeu_") as t:
        s = Smoke(a.wersja, Path(t))
        przebieg(s, a.bez_page_all)

    zdane = sum(1 for _, ok, _ in s.wyniki if ok)
    for nazwa, ok, szczegol in s.wyniki:
        print(f"[{'OK' if ok else 'BLOKADA'}] {nazwa} - {szczegol}")
    stan = "OK" if s.wyniki and zdane == len(s.wyniki) else "BLOKADA"
    print(f"\nadeu {a.wersja}: {zdane}/{len(s.wyniki)} kontroli. Stan: {stan}")
    return 0 if stan == "OK" else 20


if __name__ == "__main__":
    raise SystemExit(main())
