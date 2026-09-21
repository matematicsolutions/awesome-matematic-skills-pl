"""Akta przeszukiwalne / searchable case files: folder PDF-ow (takze skanow) -> tekst z numerami
stron + wyszukiwarka + raport. Wszystko lokalnie: OCR na CPU (LiteParse + Tesseract), bez chmury.

    python scripts/akta.py FOLDER                       # wynik obok: FOLDER-tekst/ (EN: FOLDER-text/)
    python scripts/akta.py FOLDER --wynik KATALOG       # alias: --out
    python scripts/akta.py FOLDER --jezyk eng           # alias: --lang; domyslnie z scripts/DEFAULT_LANG
    python scripts/akta.py FOLDER --tessdata KATALOG    # przypiete modele OCR (praca offline)

Ten sam kod sluzy bliźniakom akta-przeszukiwalne-pl i searchable-case-files-en; rozni je tylko
plik scripts/DEFAULT_LANG. Jezyk decyduje o modelu OCR, jezyku raportu i o naprawie znaku
paragrafu: `$` przed liczba -> `§` TYLKO dla `pol` (w angielskich aktach `$ 5,000` to kwota).

Oryginaly nie sa zmieniane. Wynik: <dokument>.txt, RAPORT.md / REPORT.md, szukaj.py + indeks.sqlite.
Przerwany przebieg mozna wznowic - gotowe dokumenty sa pomijane.
Kod wyjscia: 0 = komplet, 10 = komplet z uwagami, 20 = cos niekompletne (szczegoly w raporcie).
Na ekran trafiaja wylacznie liczby - tresc akt zostaje w plikach wyniku.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

OK, UWAGI, BLOKADA = "ok", "uwagi", "blokada"
EXIT = {OK: 0, UWAGI: 10, BLOKADA: 20}
HEADER_SHA = re.compile(r"^# sha256 ([0-9a-f]{64})$", re.M)
PAGE_SPLIT = re.compile(r"^===== (?:strona|page) \d+ =====$", re.M)

T = {
    "pol": dict(
        page="strona", suffix="-tekst", report="RAPORT.md", complete="# KOMPLET",
        unreadable="[STRONA NIECZYTELNA - sprawdz oryginal]", missing="[STRONA POMINIETA PRZEZ PARSER]",
        note="OCR lokalny: liteparse {v}, 300 dpi, jezyk pol. Tekst sluzy do WYSZUKIWANIA - cytat porownaj z oryginalem.",
        e_notdir="BLAD: {p} nie jest katalogiem",
        e_inside="BLAD: katalog wyniku nie moze lezec w folderze akt - oryginaly zostaja nietkniete",
        e_nopdf="BLAD: zero plikow PDF w {p} - nie ma czego przeczytac",
        e_dll=("BLAD: Windows zablokowal biblioteke OCR (niepodpisane pliki pdfium.dll / _liteparse.pyd).\n"
               "Najczestsza przyczyna: Smart App Control (Zabezpieczenia Windows -> Kontrola aplikacji i przegladarki).\n"
               "Decyzje o zmianie ustawien podejmuje wlasciciel komputera."),
        e_missing=("BLAD: brak biblioteki OCR. Zainstaluj:  python -m pip install liteparse==2.14.6\n"
                   "(python -m pip, nie samo pip - Smart App Control blokuje pip.exe)"),
        r_title="# Raport: akta przeszukiwalne", r_src="Zrodlo", r_state="Stan",
        r_warn="Tekst z OCR sluzy do wyszukiwania. Przed zacytowaniem porownaj fragment z oryginalem PDF.",
        r_cols="| plik | stan | stron | strony nieczytelne | § naprawiony |",
        r_dup="duplikat pliku", r_err="BLAD",
        r_same_h="## Ten sam tekst w roznych plikach",
        r_same_p=("Pliki roznia sie bajtami, ale maja IDENTYCZNY tekst. Czesto to ten sam dokument zapisany dwa razy - "
                  "albo plik o mylacej nazwie, a dokumentu z nazwy w aktach brakuje. Sprawdz."),
        r_same="ta sama tresc co", r_native="## Pliki z warstwa tekstowa (bez OCR)",
        r_noidx="**Indeks wyszukiwarki NIE zostal zbudowany** - uruchom `python szukaj.py --buduj`.",
        r_search="## Wyszukiwanie\n\n    python szukaj.py \"opinia bieglej\"\n    python szukaj.py \"art 190a\" --dokladnie\n",
        states={OK: "OK", UWAGI: "UWAGI", BLOKADA: "BLOKADA"},
        rows={"gotowy": "gotowy", "wznowiony": "wznowiony", "niekompletny": "NIEKOMPLETNY"}),
    "eng": dict(
        page="page", suffix="-text", report="REPORT.md", complete="# COMPLETE",
        unreadable="[UNREADABLE PAGE - check the original]", missing="[PAGE SKIPPED BY THE PARSER]",
        note="Local OCR: liteparse {v}, 300 dpi, language eng. The text is for SEARCHING - check any quote against the original.",
        e_notdir="ERROR: {p} is not a folder",
        e_inside="ERROR: the output folder cannot be inside the case folder - originals stay untouched",
        e_nopdf="ERROR: no PDF files in {p} - nothing to read",
        e_dll=("ERROR: Windows blocked the OCR library (unsigned pdfium.dll / _liteparse.pyd).\n"
               "Most common cause: Smart App Control (Windows Security -> App & browser control).\n"
               "Whether to change that setting is the computer owner's decision."),
        e_missing=("ERROR: OCR library not installed. Install:  python -m pip install liteparse==2.14.6\n"
                   "(use python -m pip, not pip alone - Smart App Control blocks pip.exe)"),
        r_title="# Report: searchable case files", r_src="Source", r_state="Status",
        r_warn="OCR text is for searching. Compare any passage with the original PDF before quoting it.",
        r_cols="| file | status | pages | unreadable pages | § repaired |",
        r_dup="duplicate file", r_err="ERROR",
        r_same_h="## Same text in different files",
        r_same_p=("The files differ byte-wise but contain IDENTICAL text. Often it is the same document saved twice - "
                  "or a misnamed file, and the document the name promises is missing from the set. Check."),
        r_same="same text as", r_native="## Files with a text layer (no OCR)",
        r_noidx="**The search index was NOT built** - run `python szukaj.py --buduj`.",
        r_search="## Search\n\n    python szukaj.py \"expert report\"\n    python szukaj.py \"section 12\" --prefix\n",
        states={OK: "OK", UWAGI: "NOTES", BLOKADA: "BLOCKED"},
        rows={"gotowy": "done", "wznowiony": "resumed", "niekompletny": "INCOMPLETE"}),
}

# `$` przed liczba w OCR `pol` to zle odczytany `§` (pomiar: 28/28 na wyroku SN).
# KOPIA reguly z doc-intel-contract-pl/scripts/adapters/liteparse.py - parytet w testach.
_PARAGRAF = re.compile(r"(?<![\w$])\$(\$?)(\s*)(?=\d)")
_PARAGRAF_L = re.compile(r"(?<![\w$])\$(\s*)[lI](?=[a-z]?\b)")


def default_lang() -> str:
    try:
        lang = open(os.path.join(HERE, "DEFAULT_LANG"), encoding="utf-8").read().strip()
    except OSError:
        return "pol"
    return lang if lang in T else "pol"


def repair_paragraf(text: str) -> tuple[str, int]:
    n = 0

    def _num(m):
        nonlocal n
        n += 1
        return "§" + ("§" if m.group(1) else "") + m.group(2)

    def _l(m):
        nonlocal n
        n += 1
        return "§" + m.group(1) + "1"

    return _PARAGRAF_L.sub(_l, _PARAGRAF.sub(_num, text)), n


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def content_key(pages: list[str]) -> str:
    """Odcisk TRESCI: ten sam tekst w innym pliku PDF (inny sha256) = duplikat po tresci."""
    return hashlib.sha256(re.sub(r"\s+", " ", "\n".join(pages)).strip().encode("utf-8")).hexdigest()


def load_extractor(t: dict):
    """Import LiteParse z czytelnym komunikatem zamiast 'DLL load failed'."""
    try:
        import liteparse_extract  # noqa: PLC0415
        import liteparse  # noqa: F401,PLC0415
        return liteparse_extract
    except ImportError as exc:
        raise SystemExit(t["e_dll"] if "dll" in str(exc).lower() else t["e_missing"])


def read_done(txt_path: str, t: dict) -> tuple[str | None, list[str]]:
    """Wznowienie: sha zrodla i strony z gotowego pliku .txt (albo None)."""
    if not os.path.exists(txt_path):
        return None, []
    body = open(txt_path, encoding="utf-8").read()
    m = HEADER_SHA.search(body)
    # Znacznik kompletnosci w DOWOLNYM jezyku: przebieg po polsku, wznowienie po angielsku
    # (albo odwrotnie) nie moze czytac akt od nowa (zlapane testem blizniaka 09-21).
    if not m or not any(re.search("^" + re.escape(x["complete"]) + "$", body, re.M) for x in T.values()):
        return None, []
    return m.group(1), [p.strip() for p in PAGE_SPLIT.split(body)[1:]]


def process_pdf(ext, path: str, tessdata: str | None, lang: str, t: dict) -> dict:
    data = ext.extract(path, tessdata=tessdata, lang=lang)
    pages, unreadable, repaired = [], [], 0
    for p in data["pages"]:
        text = p.get("text") or ""
        if p.get("ocr") and lang == "pol":
            text, n = repair_paragraf(text)
            repaired += n
        if not text.strip() and p.get("image"):
            unreadable.append(p["number"])
            text = t["unreadable"]
        pages.append(text.strip())
    returned = len(data["pages"])
    pages += [t["missing"]] * max(0, data["total_pages"] - returned)
    return {"pages": pages, "total": data["total_pages"], "returned": returned,
            "unreadable": unreadable, "repaired": repaired if lang == "pol" else None,
            "page_errors": len(data["page_errors"]), "version": data["parser"]["version"],
            "ocr": any(p.get("ocr") for p in data["pages"])}


def write_txt(txt_path: str, src: str, digest: str, r: dict, t: dict) -> None:
    complete = r["returned"] == r["total"] and not r["page_errors"]
    with open(txt_path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(f"# {os.path.basename(src)}\n# sha256 {digest}\n# {t['note'].format(v=r['version'])}\n")
        if complete:
            fh.write(t["complete"] + "\n")
        for i, text in enumerate(r["pages"], 1):
            fh.write(f"\n===== {t['page']} {i} =====\n{text}\n")


def unique_name(stem: str, used: set) -> str:
    name, k = stem, 2
    while name.lower() in used:
        name, k = f"{stem} ({k})", k + 1
    used.add(name.lower())
    return name


def run(src: str, out: str, tessdata: str | None, lang: str | None = None) -> int:
    lang = lang or default_lang()
    t = T[lang]
    src, out = os.path.abspath(src), os.path.abspath(out)
    if not os.path.isdir(src):
        print(t["e_notdir"].format(p=src), file=sys.stderr)
        return 20
    if out == src or out.startswith(src + os.sep):
        print(t["e_inside"], file=sys.stderr)
        return 20
    pdfs = sorted((os.path.join(d, f) for d, _, fs in os.walk(src) for f in fs if f.lower().endswith(".pdf")),
                  key=os.path.getsize)
    if not pdfs:
        print(t["e_nopdf"].format(p=src), file=sys.stderr)
        return 20
    os.makedirs(out, exist_ok=True)
    ext = None
    by_sha, by_content, used, rows = {}, {}, set(), []
    for path in pdfs:
        rel = os.path.relpath(path, src)
        digest = sha256(path)
        if digest in by_sha:
            rows.append({"plik": rel, "stan": "duplikat_bajty", "jak": by_sha[digest]})
            continue
        name = unique_name(os.path.splitext(os.path.basename(path))[0], used)
        by_sha[digest] = name
        txt = os.path.join(out, name + ".txt")
        done_sha, pages = read_done(txt, t)
        t0 = time.perf_counter()
        if done_sha == digest:
            row = {"plik": rel, "wynik": name, "stan": "wznowiony", "stron": len(pages),
                   "nieczytelne": [i for i, p in enumerate(pages, 1) if p == t["unreadable"]],
                   "paragraf": None, "ocr": None}
        else:
            ext = ext or load_extractor(t)
            try:
                r = process_pdf(ext, path, tessdata, lang, t)
            except Exception as exc:  # noqa: BLE001 - kazdy blad widoczny w raporcie
                rows.append({"plik": rel, "stan": "blad", "blad": type(exc).__name__})
                print(json.dumps({"n": len(rows), "stan": "blad"}), flush=True)
                continue
            write_txt(txt, path, digest, r, t)
            pages = r["pages"]
            incomplete = r["returned"] != r["total"] or r["page_errors"]
            row = {"plik": rel, "wynik": name, "stan": "niekompletny" if incomplete else "gotowy",
                   "stron": r["total"], "nieczytelne": r["unreadable"], "paragraf": r["repaired"], "ocr": r["ocr"]}
        key = content_key(pages)
        if key in by_content:
            row["ta_sama_tresc_co"] = by_content[key]
        else:
            by_content[key] = name
        row["min"] = round((time.perf_counter() - t0) / 60, 1)
        rows.append(row)
        print(json.dumps({"n": len(rows), "stan": row["stan"], "stron": row["stron"],
                          "nieczytelne": len(row["nieczytelne"]), "min": row["min"]}), flush=True)

    shutil.copy2(os.path.join(HERE, "szukaj.py"), os.path.join(out, "szukaj.py"))
    idx = subprocess.run([sys.executable, os.path.join(out, "szukaj.py"), "--buduj", "--lang", lang],
                         capture_output=True, text=True, encoding="utf-8")
    status = write_report(out, src, rows, idx.returncode, t)
    docs = [r for r in rows if r["stan"] in ("gotowy", "wznowiony", "niekompletny")]
    print(json.dumps({"stan": status, "jezyk": lang, "dokumentow": len(docs), "stron": sum(r["stron"] for r in docs),
                      "duplikaty_bajty": sum(r["stan"] == "duplikat_bajty" for r in rows),
                      "duplikaty_tresc": sum("ta_sama_tresc_co" in r for r in rows),
                      "bledy": sum(r["stan"] in ("blad", "niekompletny") for r in rows),
                      "indeks": "ok" if idx.returncode == 0 else "BLAD", "wynik": out}, ensure_ascii=False))
    return EXIT[status]


def write_report(out: str, src: str, rows: list, index_rc: int, t: dict) -> str:
    bad = any(r["stan"] in ("blad", "niekompletny") for r in rows) or index_rc != 0
    notes = any(r["stan"] == "duplikat_bajty" or r.get("nieczytelne") or "ta_sama_tresc_co" in r
                or r.get("ocr") is False for r in rows)
    status = BLOKADA if bad else (UWAGI if notes else OK)
    L = [t["r_title"] + "\n", f"{t['r_src']}: `{src}`  ", f"{t['r_state']}: **{t['states'][status]}**\n",
         t["r_warn"] + "\n", t["r_cols"], "|---|---|---|---|---|"]
    for r in rows:
        if r["stan"] == "duplikat_bajty":
            L.append(f"| {r['plik']} | {t['r_dup']} -> {r['jak']} | | | |")
        elif r["stan"] == "blad":
            L.append(f"| {r['plik']} | {t['r_err']} ({r['blad']}) | | | |")
        else:
            nc = ", ".join(map(str, r["nieczytelne"][:15])) + (" ..." if len(r["nieczytelne"]) > 15 else "")
            L.append(f"| {r['plik']} | {t['rows'][r['stan']]} | {r['stron']} | {nc or '-'} | "
                     f"{'-' if r['paragraf'] is None else r['paragraf']} |")
    same = [r for r in rows if "ta_sama_tresc_co" in r]
    if same:
        L += ["\n" + t["r_same_h"] + "\n", t["r_same_p"] + "\n"]
        L += [f"- `{r['plik']}` = {t['r_same']} `{r['ta_sama_tresc_co']}`" for r in same]
    native = [r for r in rows if r.get("ocr") is False]
    if native:
        L += ["\n" + t["r_native"] + "\n"] + [f"- `{r['plik']}`" for r in native]
    if index_rc != 0:
        L.append("\n" + t["r_noidx"])
    L.append("\n" + t["r_search"])
    open(os.path.join(out, t["report"]), "w", encoding="utf-8", newline="\n").write("\n".join(L) + "\n")
    return status


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("folder", help="folder z aktami / case folder (PDF, takze skany)")
    ap.add_argument("--wynik", "--out", dest="wynik", help="katalog wyniku / output folder")
    ap.add_argument("--jezyk", "--lang", dest="jezyk", choices=sorted(T), help="pol | eng")
    ap.add_argument("--tessdata", help="przypiety katalog modeli OCR *.traineddata")
    a = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    lang = a.jezyk or default_lang()
    out = a.wynik or os.path.abspath(a.folder).rstrip("\\/") + T[lang]["suffix"]
    return run(a.folder, out, a.tessdata or os.environ.get("DOC_INTEL_TESSDATA"), lang)


if __name__ == "__main__":
    sys.exit(main())
