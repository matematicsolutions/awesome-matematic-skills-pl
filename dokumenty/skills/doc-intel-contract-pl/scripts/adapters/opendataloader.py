"""Adapter: wyjscie opendataloader-pdf (JSON) -> list[Block].

Oczekiwany ksztalt wejscia (rung 3 drabinki PDF):
{
  "pages": [
    {"page_number": 1, "width": 595, "height": 842,
     "blocks": [
        {"type": "Title", "bbox": [x0,y0,x1,y1], "text": "...", "confidence": 0.98}
     ]}
  ]
}
bbox w pikselach -> normalizacja do 0-1 przez width/height strony.
Article V: brakujace pola (bbox/confidence) -> None + flaga partial.
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from contract import Block  # noqa: E402

# mapowanie typow opendataloader -> nasze block_type
_TYPE_MAP = {
    "title": "title", "heading": "title", "sectionheading": "title",
    "text": "paragraph", "paragraph": "paragraph", "plaintext": "paragraph",
    "table": "table",
    "list": "list", "listitem": "list",
    "formula": "equation", "equation": "equation",
    "figure": "figure", "image": "figure", "picture": "figure",
    "pageheader": "header", "header": "header",
    "pagefooter": "footer", "footer": "footer",
    "signature": "signature",
    "stamp": "stamp", "seal": "stamp",
}


def _norm_bbox(bbox, w, h):
    if not bbox or len(bbox) != 4 or not w or not h:
        return None
    x0, y0, x1, y1 = bbox
    return [round(x0 / w, 5), round(y0 / h, 5), round(x1 / w, 5), round(y1 / h, 5)]


def to_blocks(data: dict) -> list[Block]:
    blocks: list[Block] = []
    counter = 0
    for page in data.get("pages", []):
        pno = int(page.get("page_number", 1))
        w = page.get("width")
        h = page.get("height")
        for raw in page.get("blocks", []):
            counter += 1
            btype = _TYPE_MAP.get(str(raw.get("type", "")).lower().replace(" ", ""), "unknown")
            bbox = _norm_bbox(raw.get("bbox"), w, h)
            conf = raw.get("confidence")
            flags = []
            if bbox is None:
                flags.append("partial")
            if conf is None:
                flags.append("partial")
            blocks.append(Block(
                id=f"b{counter:04d}",
                page=pno,
                bbox=bbox,
                block_type=btype,
                text=str(raw.get("text", "")),
                confidence=float(conf) if conf is not None else None,
                flags=sorted(set(flags)),
            ))
    return blocks


def page_count(data: dict) -> int:
    return len(data.get("pages", []))
