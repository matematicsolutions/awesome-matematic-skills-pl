"""Ekstraktor: PDF -> JSON posrednie dla adaptera `pdf-inspector`.

Jedyny plik w tym skillu, ktory wymaga zaleznosci zewnetrznej (`pdf-inspector`,
PyPI, MIT). Sciezka normalizacji (`normalize.py` + `adapters/`) pozostaje
zero-dep stdlib - dlatego ekstrakcja i normalizacja sa rozdzielone, tak samo
jak przy opendataloaderze i Chandrze.

Co wyciaga (i czego NIE gubi):
  * pozycjonowane linie tekstu (TextItem: x/y/w/h, font, font_size, is_bold),
  * strony wymagajace OCR + MASZYNOWY powod (scanned / suspected_garbled_text /
    vector_text / no_text) - te strony trafiaja do JSON jako jawne pozycje,
    a nie jako cisza. To jest cel calego pliku: strona, ktorej nie da sie
    przeczytac, MUSI byc widoczna w kontrakcie.
  * pewnosc klasyfikacji, flage bledow kodowania, strony z tabelami/kolumnami.

Dwie pulapki API, zmierzone 2026-08-08 (uwaga przy aktualizacji biblioteki):
  1. `extract_text_with_positions` numeruje strony od 1, a `classify_pdf` zwraca
     `pages_needing_ocr` od 0. Zla konwencja NIE daje bledu - daje PUSTA liste.
     Tu wszystko jest sprowadzone do 1-indeksowania.
  2. `TextItem` ma uklad wspolrzednych PDF (origin lewy-DOL), mimo ze API regionow
     jest udokumentowane jako lewy-GORA. Konwersja do gory robi adapter.

Wymiary strony: biblioteka ich NIE wystawia (luka upstream - kandydat na PR).
Czytamy `/MediaBox` ze zrodla; w PDF-ach ze skompresowanymi strumieniami obiektow
bywa nieczytelny (zmierzone: 1 z 3 plikow WM). Wtedy `page_size` = null, a adapter
zgodnie z konwencja skillu daje `bbox=None` + flage - nigdy zgadywanych liczb.

Uzycie:
    python scripts/pdfi_extract.py AKTA.pdf > akta.json
    python scripts/pdfi_extract.py AKTA.pdf | python scripts/normalize.py --engine pdf-inspector -
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

MEDIABOX = re.compile(rb"/MediaBox\s*\[\s*([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)\s+([\d.\-]+)")


def page_size(path: str):
    """[w, h] gdy WSZYSTKIE MediaBox sa zgodne, inaczej None (bez zgadywania).

    None znaczy wylacznie "MediaBoxy niezgodne albo nieczytelne ze strumienia" - to
    uczciwe "nie wiem". Bledu I/O NIE lapiemy: wolajacy (extract) otworzyl juz ten plik
    przez pdf_inspector, wiec OSError tutaj to wyscig albo utrata uprawnien miedzy
    dwoma otwarciami i ma byc widoczny, nie zamieniony na None.
    """
    with open(path, "rb") as fh:
        data = fh.read()
    boxes = set()
    for m in MEDIABOX.finditer(data):
        x0, y0, x1, y1 = (float(v) for v in m.groups())
        boxes.add((round(abs(x1 - x0), 2), round(abs(y1 - y0), 2)))
    if len(boxes) != 1:
        return None  # brak albo rozne rozmiary stron -> nie normalizujemy
    w, h = boxes.pop()
    return [w, h] if w > 0 and h > 0 else None


def extract(path: str) -> dict:
    import pdf_inspector  # zaleznosc opcjonalna - brak = glosny blad, nie ciche zero

    path = os.path.abspath(path)
    res = pdf_inspector.process_pdf(path)

    reasons = {int(r.page): list(r.reasons) for r in res.ocr_reasons_by_page}
    need_ocr = sorted(int(p) for p in res.pages_needing_ocr)  # 1-indeksowane

    items = []
    for it in pdf_inspector.extract_text_with_positions(path):
        if not it.text.strip():
            continue
        items.append({
            "page": int(it.page), "x": round(it.x, 2), "y": round(it.y, 2),
            "width": round(it.width, 2), "height": round(it.height, 2),
            "text": it.text, "font_size": round(it.font_size, 2),
            "is_bold": bool(it.is_bold), "item_type": it.item_type,
        })

    return {
        "source": os.path.basename(path),
        "engine": "pdf-inspector",
        "pdf_type": res.pdf_type,
        "page_count": int(res.page_count),
        "page_size": page_size(path),
        "confidence": round(float(res.confidence), 4),
        "has_encoding_issues": bool(res.has_encoding_issues),
        "pages_needing_ocr": need_ocr,
        "ocr_reasons_by_page": reasons,
        "pages_with_tables": sorted(int(p) for p in res.pages_with_tables),
        "pages_with_columns": sorted(int(p) for p in res.pages_with_columns),
        "items": items,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="PDF -> JSON posrednie (pdf-inspector)")
    ap.add_argument("path")
    ap.add_argument("--pretty", action="store_true")
    a = ap.parse_args(argv)
    try:
        out = extract(a.path)
    except ImportError:
        print("BLAD: brak pakietu 'pdf-inspector' (pip install pdf-inspector). "
              "Bez niego nie ma ekstrakcji - swiadomie NIE zwracam pustego wyniku.",
              file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001
        print(f"BLAD ekstrakcji: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(out, ensure_ascii=False, indent=2 if a.pretty else None))
    return 0


if __name__ == "__main__":
    sys.exit(main())
