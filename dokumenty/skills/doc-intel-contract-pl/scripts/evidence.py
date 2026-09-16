# -*- coding: utf-8 -*-
"""Warstwa dowodowa: RODZAJ dowodu x ROZDZIELCZOSC lokalizacji.

Zastepuje jedna liczbe `confidence` dwoma ortogonalnymi, wyliczalnymi osiami.
Prawnik musi widziec roznice miedzy "znalazlem to slowo doslownie, strona 4,
znaki 1200-1240" a "model to wywnioskowal z calosci". Skalar 0..1 tego nie mowi.

Zasada naczelna (za docling-graph, MIT/IBM): **fail-empty, never fail-wrong**.
Lepiej nie zwrocic kotwicy niz zwrocic zla. Ale w odroznieniu od upstreamu
NIE milczymy przy odrzuceniu - kazdy wynik niesie `match_count`, czyli pelny
mianownik trafien, i `skipped_reason`. Cisza bez powodu uczy ignorowac raporty.

Zero zaleznosci, zero sieci (Article I konstytucji). Python 3.11+ stdlib.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass, field

# --- Os 1: RODZAJ dowodu ----------------------------------------------------
# verbatim   - cytat wystepuje w tekscie bloku bajt w bajt, bez normalizacji
# normalized - wystepuje po normalizacji typograficznej (cudzyslowy, dywizy,
#              miekki dywiz, fold wielkosci liter, zwiniete biale znaki).
#              Nadal DOSLOWNA lokalizacja z dokladnym zakresem w ORYGINALE,
#              ale glify zrodla roznia sie od cytatu - prawnik przepisujacy
#              to do pisma musi o tym wiedziec.
# observed   - widziany w dokumencie, ale nie w jednym bloku: przechodzi przez
#              granice blokow albo trafia w zbyt wiele, by wskazac jeden.
# derived    - brak lokalizacji doslownej; przypisanie do dokumentu jako calosci.
KIND_STRENGTH: dict[str, int] = {
    "verbatim": 4,
    "normalized": 3,
    "observed": 2,
    # 1 zarezerwowane na "reconciled" (scalenie z wielu zrodel)
    "derived": 0,
}
ANCHOR_KINDS = tuple(KIND_STRENGTH)

# --- Os 2: ROZDZIELCZOSC lokalizacji ---------------------------------------
RESOLUTION_STRENGTH: dict[str, int] = {
    "span": 4,      # zakres znakowy w konkretnym bloku
    "block": 3,     # konkretny blok, bez zakresu
    "page": 2,      # strona, bez bloku
    "document": 1,  # caly dokument
    "none": 0,      # nic
}
RESOLUTION_LEVELS = tuple(RESOLUTION_STRENGTH)

# --- Bramki dystynktywnosci (fail-empty) -----------------------------------
MIN_LEN = 3               # krotsze niz 3 znaki po normalizacji - nie lokalizujemy
MIN_DIGIT_ONLY_LEN = 4    # "12" trafia wszedzie; sygnatura "123/45" juz nie
MAX_MATCH_BLOCKS = 6      # trafienie w wiecej blokach = termin niedystynktywny

# --- Znaki -----------------------------------------------------------------
# Kasowane bez sladu: niewidzialne w PDF, obecne w warstwie tekstowej.
_DROP = frozenset(
    [
        "­",  # miekki dywiz - w justowanym PDF WEWNATRZ slowa
        "​", "‌", "‍",  # zerowa szerokosc
        "﻿",  # BOM
        "⁠",  # word joiner
    ]
)

# Ujednolicane do jednego znaku.
_QUOTE_SOURCES = [
    "„", "“", "”", "‟",   # „ “ ” ‟
    "«", "»", "‹", "›",   # « » ‹ ›
    "‘", "’", "‚", "‛",   # ‘ ’ ‚ ‛
    "`", "´", "'",             # ` ´ '
]
# PELNA rodzina kresek. U+2011 i U+2212 to ZMIERZONE luki starego normalize():
# EUR-Lex pisze U+2011, my szukalismy U+002D.
_DASH_SOURCES = [
    "‐", "‑", "‒", "–",   # ‐ ‑ ‒ –
    "—", "―", "−", "⁃",   # — ― − ⁃
    "－",                                  # －
]

_MAP: dict[str, str] = {}
for _c in _QUOTE_SOURCES:
    _MAP[_c] = '"'
for _c in _DASH_SOURCES:
    _MAP[_c] = "-"
# wielokropek jako jeden znak vs trzy kropki rozjezdza dopasowanie
_MAP["…"] = "..."

# Kreski, ktore na koncu linii znacza PRZENIESIENIE WYRAZU. Miekki dywiz U+00AD
# jest tu mimo obecnosci w _DROP: on ZNACZY punkt przeniesienia i renderuje sie
# wylacznie wtedy, gdy linia sie w tym miejscu lamie. Sprawdzenie przeniesienia
# musi wiec wyprzedzic kasowanie, inaczej "postano<U+00AD>\nwienie" daje
# "postano wienie" - slowo rozciete spacja (zmierzone 2026-08-30).
_HYPHENS = frozenset(["-", "­"] + _DASH_SOURCES)


@dataclass(frozen=True)
class Anchor:
    """Jedna kotwica: gdzie w zrodle znaleziono cytat."""

    block_id: str
    page: int
    kind: str                       # ANCHOR_KINDS
    resolution: str                 # RESOLUTION_LEVELS
    span: tuple | None              # offsety znakowe w ORYGINALNYM text bloku
    bbox: list | None               # bbox bloku (wizualne podswietlenie)

    def as_dict(self) -> dict:
        return {
            "block_id": self.block_id,
            "page": self.page,
            "kind": self.kind,
            "resolution": self.resolution,
            "span": list(self.span) if self.span else None,
            "bbox": self.bbox,
        }


@dataclass
class Evidence:
    """Wynik lokalizacji jednego cytatu. ZAWSZE niesie mianownik trafien."""

    kind: str = "derived"
    resolution: str = "none"
    anchors: list = field(default_factory=list)
    match_count: int = 0               # w ilu blokach cytat wystapil
    skipped_reason: str | None = None  # czemu NIE zwrocilismy kotwicy

    @property
    def strength(self) -> tuple:
        return (
            KIND_STRENGTH.get(self.kind, 0),
            RESOLUTION_STRENGTH.get(self.resolution, 0),
        )

    def as_dict(self) -> dict:
        return {
            "kind": self.kind,
            "resolution": self.resolution,
            "kind_strength": KIND_STRENGTH.get(self.kind, 0),
            "resolution_strength": RESOLUTION_STRENGTH.get(self.resolution, 0),
            "anchors": [a.as_dict() for a in self.anchors],
            "match_count": self.match_count,
            "skipped_reason": self.skipped_reason,
        }


# ---------------------------------------------------------------------------
# Normalizacja Z MAPA OFFSETOW
# ---------------------------------------------------------------------------
def normalize_with_map(text: str) -> tuple:
    """Znormalizuj tekst zachowujac przeliczenie offsetow na ORYGINAL.

    Zwraca (norm, src_start, src_end): znormalizowany znak o indeksie k powstal
    ze znakow [src_start[k], src_end[k]) w `text`. Dzieki temu trafienie w
    przestrzeni znormalizowanej daje DOKLADNY zakres w oryginale - to warunek
    konieczny rozdzielczosci `span`.

    Stary normalize() w grounding_bridge zwijal biale znaki i kasowal
    przeniesienia wyrazow BEZ mapy, wiec offsety dryfowaly i most mogl podac
    tylko bbox CALEGO bloku (zmierzone: 27 znakow -> 24).

    Decyzje, kazda mierzalna:
    - NFC skladamy GRUPAMI (znak bazowy + znaki laczace), bo NFC na pojedynczym
      znaku nic nie sklada; grupa mapuje sie na swoj pelny zakres zrodlowy.
      Obsluguje wejscie w NFD, gdzie 'o' + U+0301 ma byc rowne 'o'. Uwaga:
      'l' U+0142 NIE MA dekompozycji i idzie druga droga - fold musi dzialac
      dla OBU, inaczej mamy "osiem z dziewieciu".
    - casefold moze rozszerzyc znak (ss <- sz-ostre); rozszerzenie jest
      dopuszczone, wszystkie znaki wyjsciowe wskazuja ten sam zakres zrodlowy.
    - przeniesienie wyrazu (dywiz + lamanie linii) kasujemy w calosci i BEZ
      wstawiania spacji - "postano-\\nwienie" ma sie rownac "postanowienie".
    """
    text = text or ""
    norm: list = []
    src_start: list = []
    src_end: list = []
    n = len(text)
    i = 0
    pending_space_from = None  # zwijanie bialych znakow

    def emit(chars: str, start: int, end: int) -> None:
        for c in chars:
            norm.append(c)
            src_start.append(start)
            src_end.append(end)

    def flush_space() -> None:
        nonlocal pending_space_from
        if pending_space_from is not None:
            emit(" ", pending_space_from, pending_space_from + 1)
            pending_space_from = None

    while i < n:
        # 1) grupa: znak bazowy + nastepujace znaki laczace -> NFC
        j = i + 1
        while j < n and unicodedata.combining(text[j]):
            j += 1
        group = unicodedata.normalize("NFC", text[i:j])

        # 2) przeniesienie wyrazu: dywiz + (spacje) + lamanie linii -> kasuj cale
        if len(group) == 1 and group in _HYPHENS:
            k = j
            while k < n and text[k] in " \t":
                k += 1
            if k < n and text[k] in "\r\n":
                while k < n and text[k] in "\r\n \t":
                    k += 1
                pending_space_from = None  # przeniesienie NIE zostawia spacji
                i = k
                continue

        out_chars = []
        for ch in group:
            if ch in _DROP:
                continue
            out_chars.append(_MAP.get(ch, ch))
        piece = "".join(out_chars)

        if piece == "":
            i = j
            continue

        # 3) biale znaki: zwijamy w jedna spacje, wiodace pomijamy
        if piece.strip() == "":
            if norm or pending_space_from is not None:
                if pending_space_from is None:
                    pending_space_from = i
            i = j
            continue

        flush_space()

        # 4) fold wielkosci liter - dopuszczamy rozszerzenie dlugosci
        emit(piece.casefold(), i, j)
        i = j

    # koncowa spacja wiszaca nie jest emitowana
    return "".join(norm), src_start, src_end


def normalize(text: str) -> str:
    """Sam tekst znormalizowany, bez mapy - do porownan i testow."""
    return normalize_with_map(text)[0]


# ---------------------------------------------------------------------------
# Bramka dystynktywnosci
# ---------------------------------------------------------------------------
def distinctiveness_veto(needle_norm: str):
    """Powod odrzucenia cytatu jako lokalizatora, albo None gdy sie nadaje."""
    if len(needle_norm) < MIN_LEN:
        return "za_krotki(<%d)" % MIN_LEN
    bare = needle_norm.replace(" ", "")
    if bare.isdigit() and len(bare) < MIN_DIGIT_ONLY_LEN:
        return "krotka_liczba(<%d)" % MIN_DIGIT_ONLY_LEN
    return None


# ---------------------------------------------------------------------------
# Lokalizator
# ---------------------------------------------------------------------------
def _verbatim_span(needle: str, haystack: str):
    pos = haystack.find(needle)
    return (pos, pos + len(needle)) if pos != -1 else None


def locate(quote: str, blocks: list, *, max_match_blocks: int = MAX_MATCH_BLOCKS) -> Evidence:
    """Zlokalizuj cytat w blokach kontraktu. Deterministyczne, zero LLM.

    Drabinka od najmocniejszego: verbatim/span -> normalized/span ->
    observed/document -> derived/none.

    Fail-empty: cytat niedystynktywny albo trafiajacy w wiecej niz
    `max_match_blocks` blokow NIE dostaje kotwicy - ale `match_count` i
    `skipped_reason` mowia dlaczego.
    """
    stripped = (quote or "").strip().strip('"„“”«» ')
    nq = normalize(stripped).strip()

    veto = distinctiveness_veto(nq)
    if veto:
        return Evidence(kind="derived", resolution="none", match_count=0, skipped_reason=veto)

    # Przebieg 1: zbierz WSZYSTKIE bloki z trafieniem (mianownik przed decyzja)
    hits = []
    for b in blocks:
        text = b.get("text", "") or ""
        vspan = _verbatim_span(stripped, text) if stripped else None
        if vspan:
            hits.append((b, "verbatim", vspan))
            continue
        nb, s_start, s_end = normalize_with_map(text)
        pos = nb.find(nq)
        if pos != -1:
            hits.append((b, "normalized", (s_start[pos], s_end[pos + len(nq) - 1])))

    match_count = len(hits)

    if match_count == 0:
        # Przebieg 2: czy cytat przechodzi przez granice blokow?
        joined = normalize("\n\n".join((b.get("text", "") or "") for b in blocks))
        if nq in joined:
            return Evidence(
                kind="observed", resolution="document", match_count=0,
                skipped_reason="przez_granice_blokow",
            )
        return Evidence(
            kind="derived", resolution="none", match_count=0,
            skipped_reason="brak_w_dokumencie",
        )

    if match_count > max_match_blocks:
        return Evidence(
            kind="observed", resolution="document", match_count=match_count,
            skipped_reason="niedystynktywny(trafien=%d>%d)" % (match_count, max_match_blocks),
        )

    # Kotwice: po jednej na blok, pierwsze wystapienie w bloku.
    # Rodzaj CALOSCI = najslabszy z kotwic. Jedna kotwica `normalized` oznacza,
    # ze glify zrodla nie sa identyczne z cytatem - i tak trzeba to zaraportowac.
    anchors = [
        Anchor(
            block_id=b.get("id", ""), page=int(b.get("page", 0)), kind=kind,
            resolution="span", span=span, bbox=b.get("bbox"),
        )
        for b, kind, span in hits
    ]
    weakest = min(anchors, key=lambda a: KIND_STRENGTH[a.kind]).kind
    return Evidence(kind=weakest, resolution="span", anchors=anchors, match_count=match_count)
