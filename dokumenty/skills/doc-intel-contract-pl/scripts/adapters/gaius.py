"""Adapter: OCR PATRONa / Gaius-Lex API (GET /api/v1/ocr/poll/<id>) -> list[Block].

Wynik poll: { "text": "...", "file_name": "...", "file_type": "...", "engine": "default|google_doc_ai" }
(zrodlo: skill gaius-api-ocr, legalgpt/gaius/api/views/ocr.py). API zwraca GLOWNIE
plaski tekst - z perspektywy kontraktu to silnik tekstowy: bbox=null, confidence=null,
flaga partial (Article V). Zachowujemy engine jako engine_variant (default vs google_doc_ai).

Uwaga governance: adapter przyjmuje JUZ POBRANY wynik poll (dict lub {text}). NIE wola
API (Article I - zero sieci w warstwie kontraktu). Pobranie z api.gaius-lex.pl robi
warstwa PATRONa/klient, nie ten skill.
"""
from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from contract import Block  # noqa: E402


def _guess_type(text: str) -> str:
    s = text.strip()
    if len(s) <= 80 and s == s.upper() and any(c.isalpha() for c in s):
        return "title"
    return "paragraph"


def to_blocks(result: dict) -> list[Block]:
    """result: dict z pola 'text' (wynik /ocr/poll). Bloki = akapity, strony = \\f."""
    text = str(result.get("text", "")).replace("\r\n", "\n").replace("\r", "\n")
    blocks: list[Block] = []
    counter = 0
    for pidx, page in enumerate(text.split("\f"), start=1):
        for para in page.split("\n\n"):
            para = para.strip()
            if not para:
                continue
            counter += 1
            blocks.append(Block(
                id=f"b{counter:04d}", page=pidx, bbox=None,
                block_type=_guess_type(para), text=para,
                confidence=None, flags=["partial"],
            ))
    return blocks


def variant(result: dict) -> str | None:
    """Podsilnik Gaius: 'default' albo 'google_doc_ai' -> engine_variant kontraktu."""
    return result.get("engine")


def page_count(result: dict) -> int:
    return len(str(result.get("text", "")).split("\f"))
