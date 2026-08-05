"""US3 / T032: heurystyka wykrywania podpisu/pieczatki (deterministyczna, zero-cloud).

Gdy silnik OCR NIE otypowal bloku jako signature/stamp, ta warstwa flaguje bloki
"podejrzane o podpis" na podstawie sygnalow layoutu: dolna czesc strony + niska/
brak pewnosci + krotki lub pusty tekst. Wynik = flaga `signature_suspected` +
kandydat do redakcji (Article III - PROPOZYCJA, nie akt).

Potwierdzenie wizualne (rung-5 vision) to KROK OPERATORA w runtime: operator
uruchamia Read/vision na wycinku bbox i potwierdza. Ta sciezka jest opt-in i
oznaczana `detector: vision` w meta - NIE jest czescia domyslnej sciezki zero-cloud
(Article I). Domyslnie dziala tylko heurystyka.

Detektor mozna wstrzyknac: apply(blocks, detector=callable). detector(block)->bool.
"""
from __future__ import annotations

# progi heurystyki (dolna czesc strony, krotki tekst, niska pewnosc)
_BOTTOM_Y0 = 0.60          # blok zaczyna sie ponizej 60% wysokosci strony
_SHORT_TEXT = 40           # <= tylu znakow = kandydat
_LOW_CONF = 0.75           # confidence < tego = sygnal
_CANDIDATE_TYPES = {"unknown", "paragraph", "figure"}


def is_signature_like(block) -> bool:
    """Deterministyczny sygnal podpisu na podstawie layoutu + tekstu."""
    if block.block_type in ("signature", "stamp"):
        return True  # silnik juz otypowal
    bbox = block.bbox
    if not bbox:
        return False
    if block.block_type not in _CANDIDATE_TYPES:
        return False
    y0 = bbox[1]
    short = len(block.text.strip()) <= _SHORT_TEXT
    low_conf = block.confidence is None or block.confidence < _LOW_CONF
    return y0 >= _BOTTOM_Y0 and short and low_conf


def apply(blocks, detector=None) -> list[str]:
    """Oznacz bloki podejrzane o podpis. Zwroc liste kandydatow (id).

    detector: opcjonalny callable(block)->bool (np. runtime vision). Gdy podany,
    tylko bloki potwierdzone przez detector dostaja flage `signature_confirmed`;
    heurystyka nadal daje `signature_suspected`.
    """
    candidates: list[str] = []
    for b in blocks:
        suspected = is_signature_like(b)
        if suspected:
            b.flags = sorted(set(b.flags) | {"signature_suspected"})
            candidates.append(b.id)
        if detector is not None and suspected:
            try:
                if detector(b):
                    b.flags = sorted(set(b.flags) | {"signature_confirmed"})
            except Exception:
                b.flags = sorted(set(b.flags) | {"signature_detector_error"})
    return candidates
