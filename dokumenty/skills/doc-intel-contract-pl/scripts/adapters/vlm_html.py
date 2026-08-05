"""Adapter: constrained-HTML z dowolnego VLM -> list[Block].

Wzorzec prompt-kontraktu z datalab-to/chandra (Apache-2.0): zamiast osobnej
warstwy detekcji layoutu, MODEL jest promptem zmuszony do emisji HTML z
allowlista tagow i atrybutami layoutu. Szablon promptu:
references/prompt_vlm_ocr_pl.md; render skanu do obrazu (flatten + DPI):
references/render_skanu_pl.md. Nasz wariant wyjscia:

  <div data-page="1">
    <div data-label="title" data-bbox="80 50 920 90">POSTANOWIENIE</div>
    <div data-label="paragraph" data-bbox="80 120 920 340"><p>...</p></div>
  </div>

- data-label = NASZA taksonomia kontraktu (title|paragraph|table|list|equation|
  signature|stamp|figure|header|footer|unknown) - VLM etykietuje podpisy i
  pieczatki wprost (Chandra tego nie ma, my potrzebujemy pod redakcje RODO).
- data-bbox = "x0 y0 x1 y1" w skali 0-1000 (jak BBOX_SCALE Chandry) ->
  normalizujemy /1000 do 0-1; brak/bledny bbox -> None + flaga partial.
- confidence: brak (model generatywny) -> None -> flaga partial -> CALOSC
  do review_required (konserwatywnie, jak silnik gaius).
- wrapper data-page opcjonalny (bez niego wszystko = strona 1).

Guard cichej niekompletnosci: niepuste wejscie i 0 blokow -> ValueError
(normalize.py -> exit 2), nie pusty sukces.

Zero zaleznosci: html.parser ze stdlib.
"""
from __future__ import annotations

import re
import sys
import os
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from contract import Block, BLOCK_TYPES  # noqa: E402

_BBOX_SCALE = 1000.0
# tagi puste (bez tagu zamykajacego) - nie liczyc do glebokosci zagniezdzenia
_VOID_TAGS = {"br", "img", "hr", "input", "wbr", "col", "source"}


def _parse_bbox(value: str | None):
    if not value:
        return None
    parts = value.replace(",", " ").split()
    if len(parts) != 4:
        return None
    try:
        nums = [float(p) for p in parts]
    except ValueError:
        return None
    return [round(v / _BBOX_SCALE, 5) for v in nums]


class _BlokParser(HTMLParser):
    """Zbiera bloki <div data-label=...> (plaskie, bez zagniezdzonych blokow)."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.raw_blocks: list[dict] = []
        self.pages_seen: set[int] = set()
        self._page = 1
        self._cur: dict | None = None
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in _VOID_TAGS:
            if self._cur is not None and tag == "br":
                self._cur["parts"].append(" ")
            return
        a = dict(attrs)
        if self._cur is not None:
            self._depth += 1
            return
        if "data-page" in a:
            try:
                self._page = int(a["data-page"])
            except (TypeError, ValueError):
                pass
            self.pages_seen.add(self._page)
            return
        if "data-label" in a:
            self._cur = {
                "label": str(a.get("data-label", "")).strip().lower(),
                "bbox": a.get("data-bbox"),
                "page": self._page,
                "parts": [],
            }
            self._depth = 0
            self.pages_seen.add(self._page)

    def handle_startendtag(self, tag, attrs):
        if self._cur is not None and tag == "br":
            self._cur["parts"].append(" ")

    def handle_endtag(self, tag):
        if self._cur is None:
            return
        if tag in _VOID_TAGS:
            return
        if self._depth > 0:
            self._depth -= 1
            return
        self.raw_blocks.append(self._cur)
        self._cur = None

    def handle_data(self, data):
        if self._cur is not None:
            self._cur["parts"].append(data)

    def close(self):
        super().close()
        if self._cur is not None:  # niedomkniety blok na koncu (ucieta generacja)
            self._cur["truncated"] = True
            self.raw_blocks.append(self._cur)
            self._cur = None


def _parse(html_text: str) -> _BlokParser:
    p = _BlokParser()
    p.feed(html_text)
    p.close()
    return p


def to_blocks(html_text: str) -> list[Block]:
    parser = _parse(html_text)
    blocks: list[Block] = []
    for i, raw in enumerate(parser.raw_blocks, start=1):
        btype = raw["label"] if raw["label"] in BLOCK_TYPES else "unknown"
        bbox = _parse_bbox(raw["bbox"])
        text = re.sub(r"\s+", " ", "".join(raw["parts"])).strip()
        flags = ["partial"]  # brak confidence z modelu generatywnego
        if raw.get("truncated"):
            flags.append("degenerate_tail")
        blocks.append(Block(
            id=f"b{i:04d}", page=raw["page"], bbox=bbox,
            block_type=btype, text=text, confidence=None,
            flags=sorted(set(flags)),
        ))
    if not blocks and html_text.strip():
        raise ValueError(
            "vlm-html: wejscie niepuste, ale 0 blokow data-label - model nie "
            "zastosowal prompt-kontraktu albo format jest inny "
            "(guard cichej niekompletnosci)"
        )
    return blocks


def page_count(html_text: str) -> int:
    parser = _parse(html_text)
    return max(len(parser.pages_seen), 1 if parser.raw_blocks else 0)
