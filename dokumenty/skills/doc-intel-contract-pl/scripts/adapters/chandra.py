"""Adapter: Chandra OCR (datalab-to/chandra) -> list[Block].

Format REALNY Chandry 2 (zweryfikowany w upstream chandra/output.py, 2026-08-05):
parse_chunks() zwraca PLASKA liste blokow:
  [{"bbox": [x1,y1,x2,y2] (piksele int), "label": "Text|Section-Header|...",
    "content": "<p>...</p>" (HTML)}]
- BEZ confidence (model generatywny) -> kazdy blok dostaje flage "partial",
  confidence-gating kieruje CALOSC do przegladu czlowieka (jak gaius).
- bbox w pikselach obrazu strony; bez wymiarow strony nie normalizujemy
  (flaga "partial").
- 19 etykiet: Caption, Footnote, Equation-Block, List-Group, Page-Header,
  Page-Footer, Image, Section-Header, Table, Text, Complex-Block, Code-Block,
  Form, Table-Of-Contents, Figure, Chemical-Block, Diagram, Bibliography,
  Blank-Page.

UWAGA: CLI Chandry NIE zapisuje tego JSON (zapisuje .md/.html + _metadata.json
bez blokow). Liste chunkow bierze sie z API Pythona (parse_chunks) i najlepiej
opakowac per strona: {"pages":[{"page":N,"width":W,"height":H,"blocks":[...]}]}
- wtedy zachowujemy numeracje stron i normalizacje bbox przez wymiary strony.

Wstecznie akceptujemy tez format hipotetyczny v1 tego adaptera
(pages/blocks z polami type/lines/conf) oraz plaska liste stron.

Guard cichej niekompletnosci: niepuste wejscie, ktore daje 0 blokow, to
ValueError (normalize.py -> exit 2), nie pusty sukces.
"""
from __future__ import annotations

import html as _html
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from contract import Block  # noqa: E402

# taksonomia layoutu Chandry (v1 + pelne 19 etykiet Chandry 2) -> nasze block_type
_TYPE_MAP = {
    "text": "paragraph", "plaintext": "paragraph", "caption": "paragraph",
    "footnote": "paragraph", "code-block": "paragraph", "bibliography": "paragraph",
    "section-header": "title", "title": "title",
    "page-header": "header", "page-footer": "footer",
    "table": "table", "form": "table",
    "list-group": "list", "table-of-contents": "list",
    "image": "figure", "figure": "figure", "diagram": "figure",
    "chemical-block": "figure",
    "equation-block": "equation", "equation": "equation",
    "complex-block": "unknown", "blank-page": "unknown",
    "signature": "signature", "stamp": "stamp",
}

_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(content: str) -> str:
    """HTML bloku Chandry -> plaski tekst (stdlib, bez parsera zaleznego)."""
    text = _TAG_RE.sub(" ", content)
    text = _html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def _norm_bbox(bbox, w, h):
    if not bbox or len(bbox) != 4:
        return None
    x0, y0, x1, y1 = bbox
    pixels = any(abs(v) > 1.0 for v in bbox)
    if pixels:
        if not w or not h:
            return None  # piksele bez wymiarow strony -> nie umiemy znormalizowac
        return [round(x0 / w, 5), round(y0 / h, 5), round(x1 / w, 5), round(y1 / h, 5)]
    return [round(x0, 5), round(y0, 5), round(x1, 5), round(y1, 5)]


def _is_flat_chunk_list(data) -> bool:
    """Realny format Chandry 2: plaska lista {bbox,label,content} bez 'blocks'."""
    return (
        isinstance(data, list)
        and bool(data)
        and all(isinstance(x, dict) for x in data)
        and not any("blocks" in x for x in data)
        and any("label" in x or "content" in x for x in data)
    )


def _iter_pages(data):
    if isinstance(data, dict) and "pages" in data:
        yield from data["pages"]
    elif isinstance(data, dict) and "blocks" in data:
        yield data  # pojedyncza strona
    elif _is_flat_chunk_list(data):
        yield {"page": 1, "blocks": data}  # parse_chunks() bez opakowania
    elif isinstance(data, list):
        for i, page in enumerate(data, start=1):
            page.setdefault("page", i)
            yield page


def to_blocks(data) -> list[Block]:
    blocks: list[Block] = []
    counter = 0
    for page in _iter_pages(data):
        pno = int(page.get("page", page.get("page_number", 1)))
        w, h = page.get("width"), page.get("height")
        for raw in page.get("blocks", []):
            counter += 1
            label = raw.get("type") or raw.get("label") or ""
            btype = _TYPE_MAP.get(str(label).lower(), "unknown")
            bbox = _norm_bbox(raw.get("bbox"), w, h)
            lines = raw.get("lines", [])
            if lines:
                text = " ".join(str(ln.get("text", "")) for ln in lines).strip()
                confs = [ln.get("conf") for ln in lines if ln.get("conf") is not None]
                conf = round(min(confs), 5) if confs else None
            elif "content" in raw:  # Chandra 2: HTML, bez confidence
                text = _strip_html(str(raw.get("content", "")))
                conf = None
            else:
                text = str(raw.get("text", "")).strip()
                c = raw.get("conf", raw.get("confidence"))
                conf = float(c) if c is not None else None
            flags = []
            if bbox is None:
                flags.append("partial")
            if conf is None:
                flags.append("partial")
            blocks.append(Block(
                id=f"b{counter:04d}", page=pno, bbox=bbox,
                block_type=btype, text=text, confidence=conf,
                flags=sorted(set(flags)),
            ))
    if not blocks and data:
        raise ValueError(
            "Chandra: wejscie niepuste, ale 0 blokow - nieznany format "
            "albo pusty wynik OCR (guard cichej niekompletnosci)"
        )
    return blocks


def page_count(data) -> int:
    return sum(1 for _ in _iter_pages(data))
