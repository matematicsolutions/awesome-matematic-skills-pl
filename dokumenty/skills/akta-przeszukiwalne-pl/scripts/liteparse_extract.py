# KOPIA z doc-intel-contract-pl/scripts/liteparse_extract.py - KANON tam, nie edytuj tutaj.
# Paczka musi dzialac samodzielnie (Boutique); zgodnosc pilnuje tests/test_akta.py::test_parytet_ekstraktora.
"""Ekstraktor: PDF (takze skan) -> JSON posrednie dla adaptera `liteparse`.

Szczebel OCR NA CPU. Do 2026-09-21 szczebel skanow stal na Chandra OCR, ktora
wymaga GPU - na maszynie bez GPU pelny skan konczyl sie `failed` i eskalacja.
LiteParse (run-llama/liteparse, Apache-2.0, Rust + PDFium + Tesseract) czyta
skany lokalnie, bez chmury, i daje bbox + pewnosc OCR per fragment.

Jedyny plik tej sciezki z zaleznoscia zewnetrzna (`liteparse`, PyPI). Adapter
(`adapters/liteparse.py`) pozostaje stdlib - jak przy pdf-inspector i Chandrze.

Zmierzone 2026-09-21 (liteparse 2.14.6) i wpisane tu jako bezpieczniki:

  1. `max_pages` ma DOMYSLNIE 1000. Na PDF-ie dluzszym niz 1000 stron biblioteka
     zwraca 1000 stron, `page_errors` = 0, zadnego wyjatku. Jedyny slad to
     `total_pages`. Ustawiamy limit jawnie i porownujemy mianownik - rozjazd
     = exit 20, nigdy cichy JSON.
  2. Markdown DOMYSLNIE wycina powtarzajace sie naglowki i stopki
     (`keep_headers_footers=False`) - na fixturze zniknela sygnatura akt ze
     WSZYSTKICH stron. Bierzemy `page.text` (nietkniete) i nie wolamy markdownu.
  3. Bez jawnego `dpi` OCR idzie w nizszej rozdzielczosci: CER 1,3% zamiast
     0,5% (300 dpi) na tym samym skanie. Domyslnie 300.
  4. Model jezyka Tesseract jest POBIERANY z GitHuba (tessdata_best) przy
     pierwszym uzyciu, do %APPDATA%/tesseract-rs/tessdata. U klienta offline to
     nie przejdzie, a pobieranie w locie to kod/dane, ktorych nikt nie widzial.
     `--tessdata` (albo zmienna DOC_INTEL_TESSDATA) przypina katalog; bez niego
     JSON niesie ostrzezenie. Kontrola pozytywna 09-21: z przypietym katalogiem
     OCR dziala po usunieciu kopii z %APPDATA% i niczego nie pobiera.
  5. Tryb `pol` czyta `§` jako `$` (28/28 na publicznym
     wyroku SN). Naprawa jest w adapterze, z flaga na bloku - nie tutaj, zeby
     surowy odczyt zostal do audytu.

Uzycie:
    python scripts/liteparse_extract.py SKAN.pdf > skan.json
    python scripts/liteparse_extract.py SKAN.pdf --tessdata C:/tessdata | python scripts/normalize.py --engine liteparse -

Kod wyjscia: 0 = JSON kompletny, 20 = biblioteka niedostepna / rozjazd stron / blad strony.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

MAX_PAGES = 100_000          # jawnie, bo domyslne 1000 obcina po cichu
DEFAULT_DPI = 300
DEFAULT_LANG = "pol"         # pol+eng: nie lepiej na ogonkach, 30-70% wolniej (pomiar 09-21)


def extract(path: str, *, dpi: int = DEFAULT_DPI, lang: str = DEFAULT_LANG,
            tessdata: str | None = None, workers: int | None = None) -> dict:
    import liteparse  # noqa: PLC0415 - zaleznosc tylko tutaj

    kwargs = dict(ocr_enabled=True, ocr_language=lang, dpi=dpi, max_pages=MAX_PAGES,
                  keep_headers_footers=True, continue_on_page_error=False, extract_blocks=True,
                  ocr_failure_fatal=True, include_complexity=True, quiet=True)
    if tessdata:
        kwargs["tessdata_path"] = tessdata
    if workers:
        kwargs["num_workers"] = workers
    result = liteparse.LiteParse(**kwargs).parse(path)

    warnings = []
    if not tessdata:
        warnings.append({"code": "tessdata_unpinned",
                         "detail": "model jezyka pobierany z GitHuba przy pierwszym uzyciu - "
                                   "u klienta offline przypnij --tessdata"})
    pages = []
    for p in result.pages:
        cx = p.complexity
        items = [{"text": t.text, "x": t.x, "y": t.y, "w": t.width, "h": t.height,
                  "conf": t.confidence} for t in p.text_items if t.text and t.text.strip()]
        blocks = []
        for b in (p.blocks or []):
            text = _block_text(b)
            if not text.strip() or b.bbox is None:
                continue
            blocks.append({"kind": b.kind, "text": text,
                           "bbox": [b.bbox.x, b.bbox.y, b.bbox.width, b.bbox.height]})
        # Bloki ukladu to ta sama dekompozycja, z ktorej biblioteka sklada markdown -
        # a markdown gubil tresc. Liczymy LITERY I CYFRY strony nieobecne w blokach
        # (dywizy z laczenia przeniesien i punktory nie sa trescia).
        residual = _alnum_residual(p.text, "".join(x["text"] for x in blocks))
        pages.append({
            "number": p.page_num, "width": p.width, "height": p.height,
            "text": p.text,
            "image": bool(cx and (cx.full_page_image or cx.has_substantial_images)),
            "full_page_image": bool(cx and cx.full_page_image),
            "ocr": any(i["conf"] is not None for i in items),
            "items": items,
            "blocks": blocks,
            "residual_alnum": residual,
        })
    return {
        "parser": {"name": "liteparse", "version": _version(), "dpi": dpi, "lang": lang,
                   "max_pages": MAX_PAGES, "tessdata": tessdata},
        "source_sha256": _sha256(path),
        "total_pages": int(result.total_pages),
        "page_errors": [{"page": getattr(e, "page_num", None), "detail": str(e)} for e in result.page_errors],
        "warnings": warnings,
        "pages": pages,
    }


def _block_text(b) -> str:
    parts = [(b.marker + " ") if b.marker else "", b.text or ""]
    parts += list(b.lines or [])
    for row in ([b.header] if b.header else []) + list(b.rows or []):
        parts.append(" | ".join(c.text for c in row))
    return "\n".join(x for x in parts if x).replace(" \n", " ")


def _alnum_residual(page_text: str, blocks_text: str) -> int:
    from collections import Counter  # noqa: PLC0415
    a = Counter(c for c in page_text if c.isalnum())
    b = Counter(c for c in blocks_text if c.isalnum())
    return sum((a - b).values())


def _version() -> str:
    try:
        from importlib.metadata import version  # noqa: PLC0415
        return version("liteparse")
    except Exception:  # noqa: BLE001
        return "unknown"


def _sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("pdf")
    ap.add_argument("--dpi", type=int, default=DEFAULT_DPI)
    ap.add_argument("--lang", default=DEFAULT_LANG)
    ap.add_argument("--tessdata", help="przypiety katalog z *.traineddata (offline)")
    ap.add_argument("--workers", type=int)
    a = ap.parse_args(argv)
    tessdata = a.tessdata or os.environ.get("DOC_INTEL_TESSDATA") or None
    try:
        data = extract(a.pdf, dpi=a.dpi, lang=a.lang, tessdata=tessdata, workers=a.workers)
    except ImportError:
        print("BLAD: brak pakietu 'liteparse' (pip install liteparse==2.14.6) - "
              "bez niego skan zostaje nieprzeczytany, nie zgaduje", file=sys.stderr)
        return 20
    except Exception as exc:  # noqa: BLE001 - kazdy blad widoczny
        print(f"BLAD liteparse: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 20
    json.dump(data, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    returned = len(data["pages"])
    if returned != data["total_pages"] or data["page_errors"]:
        print(f"BLAD: zwrocono {returned} z {data['total_pages']} stron, "
              f"bledy stron: {len(data['page_errors'])} - wynik NIEKOMPLETNY", file=sys.stderr)
        return 20
    return 0


if __name__ == "__main__":
    sys.exit(main())
