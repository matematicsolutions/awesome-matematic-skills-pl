"""Adapter: LiteParse (JSON z liteparse_extract.py) -> list[Block].

Szczebel OCR na CPU. Zero-dep stdlib - zaleznosc siedzi w `liteparse_extract.py`.

Czego pilnuje ponad zwykla konwersje:

1. **Mianownik stron.** `total_pages` z biblioteki porownany z liczba zwroconych
   stron. Brakujace strony dostaja JAWNE bloki-zastepniki (`missing_page`) -
   biblioteka domyslnie obcina do 1000 stron bez bledu (zmierzone 09-21).
2. **Pusta vs nieczytelna.** Strona z rastrem i bez tekstu to `needs_ocr` +
   `unreadable`, confidence 0.0 -> kolejka czlowieka. Strona bez rastra i bez
   tekstu to strona pusta: bez bloku, jak w pozostalych adapterach.
3. **`§` czytany jako `$`.** Tesseract `pol` myli paragraf z dolarem
   systematycznie (28/28 na wyroku SN). Naprawiamy TYLKO `$` przed liczba albo
   przed `l`/`I` udajacym jedynke ("§ 1a" -> "$ la"), a blok dostaje flage
   `repaired_paragraf` - surowy odczyt zostaje w JSON-ie ekstraktora do audytu.
   Na tekscie z warstwy tekstowej adapter nic nie zmienia (brak pewnosci OCR),
   a pewnosc bloku to None + `native_text`.
4. **Pewnosc bloku = 10. percentyl pewnosci slow**, nie srednia i nie minimum.
   Srednia rozmywa zly fragment; minimum na akapicie ze 100 slow wysyla do
   czlowieka niemal kazdy blok (zmierzone 09-21: 4/4 bloki pod progiem), a
   kolejka ze 100% blokow uczy ja ignorowac. Pojedyncze slowo ponizej 0,6
   dostaje flage `weak_word` - ryzyko zostaje widoczne bez zalewania kolejki.
"""
from __future__ import annotations

import json
import os
import re
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from contract import Block  # noqa: E402

PARA_GAP = 0.8               # przerwa miedzy wierszami > 0.8 mediany wysokosci wiersza = nowy akapit
CONF_PCT = 0.10              # pewnosc bloku = 10. percentyl pewnosci slow
WEAK_WORD = 0.60             # slowo ponizej = flaga `weak_word` (nie zmienia pewnosci bloku)
EDGE_BAND = 0.07

# `$` przed cyfra (opcjonalnie drugi `$` = `§§`), albo `$ la` / `$ Ia` = `§ 1a`
_PARAGRAF = re.compile(r"(?<![\w$])\$(\$?)(\s*)(?=\d)")
_PARAGRAF_L = re.compile(r"(?<![\w$])\$(\s*)[lI](?=[a-z]?\b)")


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

    text = _PARAGRAF.sub(_num, text)
    text = _PARAGRAF_L.sub(_l, text)
    return text, n


def _parse(raw) -> dict:
    if isinstance(raw, (bytes, bytearray)):
        raw = raw.decode("utf-8")
    data = json.loads(raw) if isinstance(raw, str) else raw
    if not isinstance(data, dict) or "pages" not in data or "total_pages" not in data:
        raise ValueError("oczekiwano JSON z liteparse_extract.py (klucze 'pages', 'total_pages')")
    return data


def coverage(raw) -> tuple[int, int]:
    """(zwrocone strony, total_pages) - rozjazd = wynik niekompletny."""
    d = _parse(raw)
    return len(d["pages"]), int(d["total_pages"])


def to_blocks(raw) -> list[Block]:
    data = _parse(raw)
    blocks: list[Block] = []
    counter = 0
    seen = set()
    for page in data["pages"]:
        num = int(page["number"])
        seen.add(num)
        items = [i for i in page.get("items", []) if i.get("text", "").strip()]
        if not items:
            if page.get("image"):
                counter += 1
                blocks.append(Block(id=f"b{counter:04d}", page=num, bbox=None, block_type="unknown",
                                    text="", confidence=0.0,
                                    flags=["needs_ocr", "partial", "unreadable"]))
            continue
        w, h = page.get("width"), page.get("height")
        lossy = int(page.get("residual_alnum") or 0) > 0
        if page.get("blocks") and not lossy:
            # Struktura z ukladu biblioteki (odporny na obrot skanu), pewnosc ze slow w bboxie.
            for lb in page["blocks"]:
                counter += 1
                blocks.append(_from_layout(counter, num, lb, items, w, h))
        else:
            # Brak blokow albo bloki zgubily litery/cyfry -> wlasne grupowanie z calego tekstu.
            for group in _paragraphs(_rows(items)):
                counter += 1
                blk = _make(counter, num, group, w, h)
                if lossy:
                    blk.flags = sorted(set(blk.flags) | {"layout_blocks_lossy"})
                blocks.append(blk)
    for missing in sorted(set(range(1, int(data["total_pages"]) + 1)) - seen):
        counter += 1
        blocks.append(Block(id=f"b{counter:04d}", page=missing, bbox=None, block_type="unknown",
                            text="", confidence=0.0, flags=["missing_page", "partial"]))
    return blocks


def _rows(items: list) -> list[list]:
    """Fragmenty (slowa) -> wiersze po wspolrzednej Y, w wierszu po X."""
    rows: list[list] = []
    for it in sorted(items, key=lambda i: (i["y"], i["x"])):
        if rows and abs(it["y"] - rows[-1][0]["y"]) <= max(2.0, it["h"] * 0.5):
            rows[-1].append(it)
        else:
            rows.append([it])
    return [sorted(r, key=lambda i: i["x"]) for r in rows]


def _paragraphs(rows: list[list]) -> list[list]:
    """Wiersze -> akapity: nowy blok, gdy pusta przestrzen miedzy wierszami
    przekracza PARA_GAP x mediana wysokosci wiersza (pomiar 09-21: prog
    1.8 liczony na slowach dawal jeden blok na cala strone)."""
    if not rows:
        return []
    heights = [max(i["y"] + i["h"] for i in r) - min(i["y"] for i in r) for r in rows]
    med = statistics.median(heights) or 1.0
    groups, cur = [], [rows[0]]
    for prev, row in zip(rows, rows[1:]):
        gap = min(i["y"] for i in row) - max(i["y"] + i["h"] for i in prev)
        if gap > med * PARA_GAP:
            groups.append(cur); cur = []
        cur.append(row)
    groups.append(cur)
    return groups


def _lines(group: list[list]) -> str:
    return "\n".join(" ".join(i["text"].strip() for i in row) for row in group)


def _from_layout(counter: int, page: int, lb: dict, items: list, w, h) -> Block:
    x, y, bw, bh = lb["bbox"]
    inside = [i for i in items
              if x - 1 <= i["x"] + i["w"] / 2 <= x + bw + 1 and y - 1 <= i["y"] + i["h"] / 2 <= y + bh + 1]
    blk = _make(counter, page, [inside] if inside else [[]], w, h, text=lb["text"],
                bbox_src=(x, y, x + bw, y + bh))
    kind = lb.get("kind")
    if kind == "heading":
        blk.block_type = "title"
    elif kind == "table":
        blk.block_type = "table"
    elif kind == "list_item":
        blk.block_type = "list"
    return blk


def _make(counter: int, page: int, rows: list[list], w, h, text: str | None = None,
          bbox_src: tuple | None = None) -> Block:
    group = [i for r in rows for i in r]
    text = _lines(rows) if text is None else text
    flags = []
    confs = [i["conf"] for i in group if i.get("conf") is not None]
    ocr = bool(confs)
    if ocr:
        text, n = repair_paragraf(text)
        if n:
            flags.append("repaired_paragraf")
        flags.append("ocr")
    bbox = None
    btype = "paragraph"
    if w and h and (group or bbox_src):
        if bbox_src:
            x0, y0, x1, y1 = bbox_src
        else:
            x0 = min(i["x"] for i in group); y0 = min(i["y"] for i in group)
            x1 = max(i["x"] + i["w"] for i in group); y1 = max(i["y"] + i["h"] for i in group)
        bbox = [round(max(0.0, x0 / w), 5), round(max(0.0, y0 / h), 5),
                round(min(1.0, x1 / w), 5), round(min(1.0, y1 / h), 5)]
        if bbox[1] < EDGE_BAND:
            btype = "header"
        elif bbox[3] > 1 - EDGE_BAND:
            btype = "footer"
    else:
        flags.append("partial")
    if btype == "paragraph" and len(text) <= 120 and text == text.upper() and any(c.isalpha() for c in text):
        btype = "title"
    # OCR: minimum pewnosci fragmentow. Tekst natywny: biblioteka pewnosci NIE daje,
    # wiec None + flaga - konwencja skillu, nigdy liczby z sufitu (tekst natywny
    # czytaj szczeblem pdf-inspector, ktory ma pewnosc klasyfikacji).
    if not ocr:
        flags.append("native_text")
    if ocr and min(confs) < WEAK_WORD:
        flags.append("weak_word")
    conf = round(sorted(confs)[int(len(confs) * CONF_PCT)], 4) if ocr else None
    return Block(id=f"b{counter:04d}", page=page, bbox=bbox, block_type=btype,
                 text=text.strip(), confidence=conf, flags=sorted(set(flags)))
