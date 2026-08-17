"""Adapter: pdf-inspector (JSON z pdfi_extract.py) -> list[Block].

Szczebel 1.5 drabinki. Pierwszy silnik, ktory daje bbox + confidence dla PDF-ow
TEKSTOWYCH (dotad mielismy je tylko z Chandry i opendataloadera, czyli z drozszej
polowy drabinki). Zero-dep stdlib - zaleznosc siedzi w `pdfi_extract.py`.

Dwie rzeczy, ktorych ten adapter pilnuje ponad zwykla konwersje:

1. **Strona nieczytelna MUSI byc widoczna w kontrakcie.** Strona wymagajaca OCR
   nie ma pozycji tekstowych, wiec bez tego wypadlaby z wyjscia po cichu i
   dokument wygladalby na kompletny (dokladnie defekt zmierzony na anydoc
   2026-08-08). Dlatego kazda taka strona dostaje JAWNY blok-zastepnik:
   `text=""`, `confidence=0.0`, `flags=["needs_ocr", "<powod>"]`. Prog
   confidence w contract.py kieruje go do kolejki `review_required`.

2. **Bez wymiarow strony nie ma bbox.** Konwencja skillu (jak w adapterze
   chandra): brak wymiarow -> `bbox=None` + flaga `partial`, nigdy liczby
   z sufitu. `TextItem` przychodzi w ukladzie PDF (origin lewy-DOL) i jest tu
   przeliczany na lewy-GORA, spojnie z reszta kontraktu.
"""
from __future__ import annotations

import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from contract import Block  # noqa: E402

# Blok konczy sie, gdy pionowa przerwa przekroczy tyle median wysokosci linii.
LINE_BREAK_FACTOR = 1.8
# Pas przy krawedzi strony uznawany za zywa pagine / stopke.
EDGE_BAND = 0.07


def page_count(raw) -> int:
    data = _parse(raw)
    return int(data.get("page_count") or 0)


def ocr_gap(raw) -> tuple[int, int]:
    """(ile stron wymaga OCR, ile stron ogolem) - do glosnego ostrzezenia."""
    data = _parse(raw)
    return len(data.get("pages_needing_ocr") or []), int(data.get("page_count") or 0)


def bbox_available(raw) -> bool:
    """Czy da sie w ogole wyliczyc wspolrzedne (znane wymiary strony).

    Brak bbox to degradacja ZDOLNOSCI, nie tresci - tekst jest dobry, tylko nie da
    sie go zakotwiczyc w regionie strony. Nie kierujemy z tego powodu bloku do
    czlowieka (113 blokow w kolejce nauczyloby ja ignorowac - „blokada na liczniku
    to fabryka liczb"), ale operator MUSI uslyszec, ze grounding cytatu jest dla
    tego dokumentu niedostepny. Inaczej dowie sie o tym dopiero wtedy, gdy
    citation-grounding-pl nie znajdzie ani jednego regionu.
    """
    return bool(_parse(raw).get("page_size"))


def _parse(raw) -> dict:
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8")
    if isinstance(raw, str):
        data = json.loads(raw)
    else:
        data = raw
    if not isinstance(data, dict) or "items" not in data:
        raise ValueError("oczekiwano JSON z pdfi_extract.py (klucz 'items')")
    return data


def _bbox(items, size):
    """Union bbox items -> [x0,y0,x1,y1] 0-1, origin lewy-GORA. None bez wymiarow."""
    if not size:
        return None
    w, h = size
    if not w or not h:
        return None
    x0 = min(i["x"] for i in items)
    x1 = max(i["x"] + i["width"] for i in items)
    y_bottom = min(i["y"] for i in items)
    y_top = max(i["y"] + i["height"] for i in items)
    return [
        round(max(0.0, x0 / w), 5),
        round(max(0.0, (h - y_top) / h), 5),   # gora: odwrocenie osi Y
        round(min(1.0, x1 / w), 5),
        round(min(1.0, (h - y_bottom) / h), 5),
    ]


def _block_type(items, size, median_size) -> str:
    text = " ".join(i["text"] for i in items).strip()
    if size:
        h = size[1]
        y_top_norm = (h - max(i["y"] + i["height"] for i in items)) / h
        y_bot_norm = (h - min(i["y"] for i in items)) / h
        if y_top_norm < EDGE_BAND:
            return "header"
        if y_bot_norm > 1 - EDGE_BAND:
            return "footer"
    if len(text) <= 120 and len(items) <= 2:
        bold = all(i["is_bold"] for i in items)
        bigger = median_size and statistics.median(i["font_size"] for i in items) > median_size * 1.12
        if bold or bigger or (text == text.upper() and any(c.isalpha() for c in text)):
            return "title"
    return "paragraph"


def to_blocks(raw) -> list[Block]:
    data = _parse(raw)
    size = data.get("page_size")
    doc_conf = data.get("confidence")
    encoding_issues = bool(data.get("has_encoding_issues"))
    need_ocr = set(data.get("pages_needing_ocr") or [])
    reasons = {int(k): v for k, v in (data.get("ocr_reasons_by_page") or {}).items()}
    with_tables = set(data.get("pages_with_tables") or [])
    with_columns = set(data.get("pages_with_columns") or [])

    by_page: dict[int, list] = {}
    for it in data["items"]:
        by_page.setdefault(int(it["page"]), []).append(it)

    blocks: list[Block] = []
    counter = 0
    pages = sorted(set(by_page) | need_ocr | {p for p in range(1, int(data.get("page_count", 0)) + 1)})

    for page in pages:
        if page in need_ocr:
            # Strona bez uzytecznej warstwy tekstowej: jawny slad zamiast ciszy.
            counter += 1
            why = reasons.get(page) or ["needs_ocr"]
            blocks.append(Block(
                id=f"b{counter:04d}", page=page, bbox=None, block_type="unknown",
                text="", confidence=0.0,
                flags=sorted({"needs_ocr", "partial", *why}),
            ))
            continue

        items = sorted(by_page.get(page, []), key=lambda i: (-i["y"], i["x"]))
        if not items:
            continue
        median_h = statistics.median(i["height"] for i in items) or 1.0
        median_fs = statistics.median(i["font_size"] for i in items) or None
        gap_limit = median_h * LINE_BREAK_FACTOR

        group: list = []
        for it in items:
            if group:
                prev_bottom = group[-1]["y"]
                if prev_bottom - (it["y"] + it["height"]) > gap_limit:
                    counter += 1
                    blocks.append(_make(counter, page, group, size, median_fs, doc_conf,
                                        encoding_issues, with_tables, with_columns))
                    group = []
            group.append(it)
        if group:
            counter += 1
            blocks.append(_make(counter, page, group, size, median_fs, doc_conf,
                                encoding_issues, with_tables, with_columns))
    return blocks


def _make(counter, page, group, size, median_fs, doc_conf, encoding_issues,
          with_tables, with_columns) -> Block:
    bbox = _bbox(group, size)
    flags = []
    if bbox is None:
        flags.append("partial")          # brak wymiarow strony -> brak wspolrzednych
    if encoding_issues:
        flags.append("encoding_issues")  # tekst moze byc przeklamany mimo obecnosci
    if page in with_tables:
        flags.append("page_has_table")   # UWAGA: to cecha STRONY, nie typ bloku
    if page in with_columns:
        flags.append("page_has_columns")
    # Confidence dokumentu, sciete gdy kodowanie jest podejrzane - blok trafi
    # wtedy pod prog i do kolejki czlowieka, zamiast udawac pewny.
    conf = None if doc_conf is None else round(min(float(doc_conf), 0.5 if encoding_issues else 1.0), 4)
    return Block(
        id=f"b{counter:04d}", page=page, bbox=bbox,
        block_type=_block_type(group, size, median_fs),
        text="\n".join(i["text"] for i in group).strip(),
        confidence=conf, flags=sorted(set(flags)),
    )
