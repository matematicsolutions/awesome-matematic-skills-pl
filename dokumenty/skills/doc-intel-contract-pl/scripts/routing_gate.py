"""Bramka routingu dokumentu -> szczebel drabinki + werdykt trojstanowy.

Powod istnienia (pomiar 2026-08-08, firecrawl/anydoc + pdf-inspector):
konwertery tej klasy zwracaja `Ok` i exit 0 nawet wtedy, gdy pominely tresc.
Zmierzone bojowo:
  * anydoc: uszkodzony `word/charts/chart1.xml` w .docx -> exit 0, stderr 0 bajtow
    (przy RUST_LOG=trace), a z wyjscia znika CALA tabela danych. Zdarzenia
    "skipping ..." (42 miejsca w zrodle) ida do fasady `log`, a repo NIGDZIE nie
    rejestruje loggera - komunikat nie ma dokad trafic.
  * anydoc/pdf: `pdf_inspector` zwraca `pages_needing_ocr` i `page_count`, po czym
    anydoc zamienia to na `log::warn!("{} of {} pages ...")` i oddaje `Ok(String)`.
    100-stronicowe akta z 40 skanami wygladaja na kompletne.

Ta bramka odwraca defekt: liczy PELNY MIANOWNIK, nazywa powod maszynowo i nigdy
nie milczy. Zero-cloud, bez LLM. PDF wymaga `pdf-inspector` (PyPI, MIT); jego BRAK
daje `failed`, nigdy cichego `ok`. Sciezka OOXML jest zero-dep (stdlib).

Uzycie:
    python scripts/routing_gate.py AKTA.pdf
    python scripts/routing_gate.py pismo.docx --pretty
    python scripts/routing_gate.py *.pdf --quiet   # tylko status != ok

Kod wyjscia: 0 = ok, 10 = degraded, 20 = failed (bramka CI moze na tym stanac).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import zipfile
import xml.etree.ElementTree as ET

# --- Szczeble drabinki z CLAUDE.md (zrodlo prawdy dla trasowania) ------------
RUNG_PDFTOTEXT = "1/pdftotext"
RUNG_ANYDOC = "1.5/anydoc"
RUNG_MARKITDOWN = "2/markitdown"
RUNG_OPENDATALOADER = "3/opendataloader-pdf"
RUNG_OCR = "4/chandra-ocr"
RUNG_VISION = "5/Read (vision)"

# Formaty, ktorych szczeble 1-3 NIE otwieraja, a anydoc otwiera (zmierzone:
# markitdown na binarnym .doc z Portalu Orzeczen -> UnsupportedFormatException).
ANYDOC_ONLY = {".doc", ".rtf", ".ppt", ".pps", ".pot", ".odt", ".odp", ".ods", ".epub", ".xls"}
OOXML_EXT = {".docx", ".docm", ".pptx", ".pptm", ".ppsx", ".xlsx", ".xlsm"}

STATUS_OK, STATUS_DEGRADED, STATUS_FAILED = "ok", "degraded", "failed"
EXIT = {STATUS_OK: 0, STATUS_DEGRADED: 10, STATUS_FAILED: 20}

# --- Limity zasobow (wzorzec: firecrawl/anydoc `package/limits.rs`, MIT) ------
# Bramka otwiera PLIKI Z ZEWNATRZ - z sadu, od klienta, z maila. Parser bez
# limitow jest wektorem DoS, a "zawiesilo sie na aktach" to takze awaria.
# Limity sa NAZWANE i w jednym miejscu, zeby dalo sie o nich rozmawiac.
MAX_ENTRY_COUNT = 10_000          # wpisow w paczce
MAX_ENTRY_BYTES = 64 * 1024 * 1024   # rozmiar po dekompresji jednej czesci
MAX_TOTAL_BYTES = 256 * 1024 * 1024  # laczny rozmiar po dekompresji
MAX_EXPANSION_RATIO = 200         # dekompresja x200 = bomba zip, nie dokument
# Prog liczymy od rozmiaru PO ROZPAKOWANIU, nie przed. Pierwsza wersja miala prog
# na rozmiarze skompresowanym i tworzyla martwe pole: im lepsza bomba (mniejszy
# zip), tym pewniej omijala kontrole. Zlapala to dopiero fixtura naduzycia.
MIN_EXPANDED_FOR_RATIO = 256 * 1024


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _verdict(path, kind, status, reasons, rung, note, total=None, usable=None, confidence=None):
    """Jedno wyjscie dla kazdej sciezki - zawsze z mianownikiem, nigdy puste."""
    return {
        "path": os.path.abspath(path),
        "sha256": _sha256(path),
        "kind": kind,
        "status": status,
        "reasons": reasons,
        "coverage": {"unit": "pages" if kind == "pdf" else "parts",
                     "total": total, "usable": usable},
        "confidence": confidence,
        "route": {"rung": rung, "note": note},
    }


# --- PDF: klasyfikacja skan-vs-tekst -----------------------------------------
def check_pdf(path: str) -> dict:
    try:
        import pdf_inspector  # noqa: PLC0415
    except ImportError:
        return _verdict(
            path, "pdf", STATUS_FAILED,
            [{"code": "gate_unavailable",
              "detail": "brak pakietu 'pdf-inspector' (pip install pdf-inspector) - "
                        "bez niego nie da sie odroznic skanu od tekstu, wiec bramka "
                        "NIE przepuszcza dokumentu zamiast zgadywac"}],
            RUNG_OCR, "zainstaluj bramke albo zdecyduj recznie")

    # Uwaga integracyjna (zmierzone): classify_pdf zwraca pages_needing_ocr
    # 0-indeksowane, ale extract_text_with_positions oczekuje stron 1-indeksowanych
    # i przy zlej konwencji oddaje PUSTA liste bez bledu. Trzymamy sie 1-indeksowania
    # w raporcie, bo tak numeruje strony czlowiek czytajacy akta.
    try:
        c = pdf_inspector.classify_pdf(os.path.abspath(path))
    except Exception as e:  # noqa: BLE001 - kazdy blad ma byc widoczny, nie polkniety
        return _verdict(path, "pdf", STATUS_FAILED,
                        [{"code": "classify_error", "detail": str(e)}],
                        RUNG_VISION, "klasyfikator odmowil - obejrzyj dokument")

    total = int(c.page_count)
    need_ocr = sorted(int(p) + 1 for p in c.pages_needing_ocr)
    usable = total - len(need_ocr)
    conf = round(float(c.confidence), 3)
    reasons = []

    if need_ocr:
        reasons.append({
            "code": "pages_need_ocr",
            "detail": f"{len(need_ocr)} z {total} stron bez uzytecznej warstwy tekstowej "
                      f"(strony: {need_ocr if len(need_ocr) <= 12 else str(need_ocr[:12]) + ' ...'})",
        })

    if usable == 0:
        # Pelny skan. Na tej maszynie brak GPU -> to jest decyzja czlowieka.
        return _verdict(path, "pdf", STATUS_FAILED, reasons, RUNG_OCR,
                        "pelny skan: warstwy tekstowej NIE MA. Chandra wymaga GPU - eskalacja do WM",
                        total, usable, conf)

    if need_ocr:
        # Najgrozniejszy przypadek i ten, ktorego dzis nikt nie lapie: dokument
        # mieszany wyglada na kompletny po kazdym konwerterze tekstowym.
        return _verdict(path, "pdf", STATUS_DEGRADED, reasons, RUNG_OPENDATALOADER,
                        f"dokument MIESZANY: {usable} stron ekstrahowalnych, {len(need_ocr)} do OCR. "
                        "Kazde wyjscie tekstowe bedzie NIEPELNE - nie cytuj bez domkniecia skanow",
                        total, usable, conf)

    layout = getattr(c, "pdf_type", "")
    if conf < 0.85:
        reasons.append({"code": "low_confidence",
                        "detail": f"pewnosc klasyfikacji {conf} < 0.85"})
        return _verdict(path, "pdf", STATUS_DEGRADED, reasons, RUNG_OPENDATALOADER,
                        "niska pewnosc - potwierdz wynik drugim silnikiem", total, usable, conf)

    return _verdict(path, "pdf", STATUS_OK, reasons, RUNG_PDFTOTEXT,
                    f"warstwa tekstowa kompletna ({layout}). Tabele/kolumny (KRS, postanowienia) "
                    f"-> {RUNG_OPENDATALOADER} albo {RUNG_ANYDOC}", total, usable, conf)


# --- OOXML: kontrola integralnosci paczki PRZED konwersja --------------------
def check_ooxml(path: str) -> dict:
    """Kazda uszkodzona czesc XML = tresc, ktora konwerter po cichu pominie.

    Zmierzone: anydoc na .docx z jednym uszkodzonym `chart1.xml` gubi cala tabele
    i nie mowi ani slowa. Tu ta czesc jest nazwana ZANIM ktokolwiek zaufa wyjsciu.
    """
    try:
        zf = zipfile.ZipFile(path)
    except zipfile.BadZipFile as e:
        return _verdict(path, "ooxml", STATUS_FAILED,
                        [{"code": "bad_package", "detail": str(e)}],
                        RUNG_VISION, "paczka nie jest czytelnym ZIP")

    with zf:
        infos = zf.infolist()
        # --- limity liczone Z NAGLOWKOW, przed jakimkolwiek odczytem ---------
        if len(infos) > MAX_ENTRY_COUNT:
            return _limit(path, "max_entry_count", f"{len(infos)} wpisow > {MAX_ENTRY_COUNT}")
        total = sum(i.file_size for i in infos)
        if total > MAX_TOTAL_BYTES:
            return _limit(path, "max_total_bytes", f"{total} B po dekompresji > {MAX_TOTAL_BYTES}")
        for i in infos:
            if i.file_size > MAX_ENTRY_BYTES:
                return _limit(path, "max_entry_bytes", f"{i.filename}: {i.file_size} B > {MAX_ENTRY_BYTES}")
            if (i.file_size >= MIN_EXPANDED_FOR_RATIO
                    and i.file_size > max(i.compress_size, 1) * MAX_EXPANSION_RATIO):
                return _limit(path, "max_expansion_ratio",
                              f"{i.filename}: x{i.file_size // max(i.compress_size, 1)} > x{MAX_EXPANSION_RATIO}")

        if zf.testzip() is not None:
            return _verdict(path, "ooxml", STATUS_FAILED,
                            [{"code": "bad_package", "detail": f"uszkodzony wpis: {zf.testzip()}"}],
                            RUNG_VISION, "CRC paczki nie zgadza sie")
        xml_parts = [n for n in zf.namelist()
                     if n.lower().endswith((".xml", ".rels")) and not n.endswith("/")]
        broken = []
        for name in xml_parts:
            data = zf.read(name)
            # Deklaracja encji w czesci OOXML = bomba encji (billion laughs).
            # ElementTree rozwija encje wewnetrzne, wiec odrzucamy PRZED parsowaniem;
            # zaden legalny .docx/.xlsx tego nie potrzebuje.
            head = data[:4096].lower()
            if b"<!entity" in head or b"<!doctype" in head:
                return _limit(path, "entity_declaration",
                              f"{name}: deklaracja DOCTYPE/ENTITY w czesci OOXML")
            try:
                ET.fromstring(data)
            except ET.ParseError as e:
                broken.append({"part": name, "detail": str(e)})

    total, usable = len(xml_parts), len(xml_parts) - len(broken)
    if broken:
        return _verdict(
            path, "ooxml", STATUS_DEGRADED,
            [{"code": "malformed_part",
              "detail": f"{len(broken)} z {total} czesci XML nie parsuje sie: "
                        + ", ".join(b["part"] for b in broken[:6])}],
            RUNG_ANYDOC,
            "konwerter POMINIE te czesci bez ostrzezenia (wykres/diagram/tabela znika z wyjscia)",
            total, usable)

    return _verdict(path, "ooxml", STATUS_OK, [], RUNG_MARKITDOWN,
                    f"{total} czesci XML poprawnych", total, usable)


def _limit(path: str, limit: str, detail: str) -> dict:
    """Twardy limit = zawsze `failed`. Nigdy 'sprobujmy mimo wszystko'."""
    return _verdict(path, "ooxml", STATUS_FAILED,
                    [{"code": "resource_limit", "limit": limit, "detail": detail}],
                    RUNG_VISION,
                    "paczka przekracza limit bezpieczenstwa - NIE parsujemy jej automatycznie")


def check_legacy(path: str, ext: str) -> dict:
    return _verdict(path, "legacy-office", STATUS_OK, [], RUNG_ANYDOC,
                    f"format {ext}: szczeble 1-3 go NIE otwieraja (zmierzone: markitdown "
                    "na binarnym .doc konczy sie UnsupportedFormatException)")


def check(path: str) -> dict:
    if not os.path.isfile(path):
        return _verdict_missing(path)
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return check_pdf(path)
    if ext in OOXML_EXT:
        return check_ooxml(path)
    if ext in ANYDOC_ONLY:
        return check_legacy(path, ext)
    return _verdict(path, "other", STATUS_FAILED,
                    [{"code": "unknown_format", "detail": f"rozszerzenie {ext or '(brak)'}"}],
                    RUNG_VISION, "poza drabinka - decyzja czlowieka")


def _verdict_missing(path: str) -> dict:
    return {"path": os.path.abspath(path), "sha256": None, "kind": "other",
            "status": STATUS_FAILED,
            "reasons": [{"code": "not_a_file", "detail": "sciezka nie wskazuje pliku"}],
            "coverage": {"unit": None, "total": None, "usable": None},
            "confidence": None, "route": {"rung": None, "note": "sprawdz sciezke"}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Bramka routingu dokumentu (trojstanowa)")
    ap.add_argument("paths", nargs="+")
    ap.add_argument("--pretty", action="store_true")
    ap.add_argument("--quiet", action="store_true", help="pokaz tylko status != ok")
    a = ap.parse_args(argv)

    worst, out = STATUS_OK, []
    for p in a.paths:
        v = check(p)
        out.append(v)
        if v["status"] == STATUS_FAILED:
            worst = STATUS_FAILED
        elif v["status"] == STATUS_DEGRADED and worst != STATUS_FAILED:
            worst = STATUS_DEGRADED

    shown = [v for v in out if not a.quiet or v["status"] != STATUS_OK]
    print(json.dumps(shown if len(a.paths) > 1 else (shown[0] if shown else {}),
                     ensure_ascii=False, indent=2 if a.pretty else None))
    return EXIT[worst]


if __name__ == "__main__":
    sys.exit(main())
