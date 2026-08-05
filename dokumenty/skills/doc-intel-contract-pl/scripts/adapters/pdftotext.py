"""Adapter: pdftotext (plain text) -> list[Block].

Najubozszy silnik (rung 1). Brak bbox i confidence -> None + flaga partial.
Strony dzielone form-feed (\\f, standard pdftotext). Bloki = akapity
(rozdzielone pusta linia). Heurystyka typu: krotka linia w caps -> title.
Article V (degradacja lagodna).
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from contract import Block  # noqa: E402


def _guess_type(text: str) -> str:
    stripped = text.strip()
    if len(stripped) <= 80 and stripped == stripped.upper() and any(c.isalpha() for c in stripped):
        return "title"
    return "paragraph"


def to_blocks(text: str) -> list[Block]:
    blocks: list[Block] = []
    counter = 0
    text = text.replace("\r\n", "\n").replace("\r", "\n")  # CRLF (Windows pdftotext) -> LF
    pages = text.split("\f")
    for pidx, page in enumerate(pages, start=1):
        for para in page.split("\n\n"):
            para = para.strip()
            if not para:
                continue
            counter += 1
            blocks.append(Block(
                id=f"b{counter:04d}",
                page=pidx,
                bbox=None,
                block_type=_guess_type(para),
                text=para,
                confidence=None,
                flags=["partial"],
            ))
    return blocks


def page_count(text: str) -> int:
    return len(text.split("\f"))
