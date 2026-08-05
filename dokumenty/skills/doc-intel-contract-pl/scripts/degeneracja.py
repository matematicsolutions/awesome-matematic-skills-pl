"""Detektor zdegenerowanego (zapetlonego) wyjscia modelu generatywnego.

Adaptacja algorytmu detect_repeat_token z datalab-to/chandra (Apache-2.0),
przeniesiona z tokenow modelu na tokeny bialych znakow (zero zaleznosci).

Po co: generatywny OCR/LLM, ktory wpadl w petle, konczy sukcesem (exit 0)
z ucietym, powtarzajacym sie ogonem - to mechanizm CICHEJ NIEKOMPLETNOSCI.
Ten modul robi z niej glosna flage.

Algorytm: bierzemy ostatnie `window` tokenow; dla kazdej dlugosci sekwencji
1..window/2 liczymy, ile razy sekwencja z konca powtarza sie bezposrednio
przed soba. Prog jest dynamiczny:

    max_repeats = int(base_max_repeats * (1 + scaling_factor / seq_len))

czyli krotkie sekwencje (naturalne w jezyku) musza powtorzyc sie duzo razy
(seq_len=1 -> prog 16), dlugie - kilka (seq_len=10 -> prog 5), zeby uznac
wyjscie za zapetlone.
"""
from __future__ import annotations

DOMYSLNE_OKNO = 500
DOMYSLNE_MAX_POWTORZEN = 4
DOMYSLNY_WSPOLCZYNNIK = 3.0


def wykryj_zapetlenie(
    text: str,
    *,
    window: int = DOMYSLNE_OKNO,
    base_max_repeats: int = DOMYSLNE_MAX_POWTORZEN,
    scaling_factor: float = DOMYSLNY_WSPOLCZYNNIK,
) -> bool:
    """True = ogon tekstu wyglada na petle generacji (wynik podejrzany)."""
    tokens = text.split()
    if len(tokens) > window:
        tokens = tokens[-window:]
    n = len(tokens)
    for seq_len in range(1, n // 2 + 1):
        seq = tokens[n - seq_len:]
        repeats = 1
        i = n - seq_len
        while i - seq_len >= 0 and tokens[i - seq_len:i] == seq:
            repeats += 1
            i -= seq_len
        max_repeats = int(base_max_repeats * (1 + scaling_factor / seq_len))
        if repeats > max_repeats:
            return True
    return False
