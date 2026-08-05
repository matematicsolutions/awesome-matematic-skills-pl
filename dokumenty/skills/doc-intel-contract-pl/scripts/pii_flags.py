"""US2: deterministyczne flagi PII PL + typed-block wrazliwe -> redaction_candidates.

Zero LLM, zero sieci (Article I/IV). Reguly regex + walidacja sum kontrolnych
(PESEL, NIP, REGON) zeby ograniczyc false-positive. Wynik = PROPOZYCJA do
redakcji (Article III - czlowiek decyduje, skill nie redaguje).
"""
from __future__ import annotations

import re

# --- wzorce PII PL ---------------------------------------------------------
_RE_PESEL = re.compile(r"\b\d{11}\b")
_RE_NIP = re.compile(r"\b\d{3}-?\d{3}-?\d{2}-?\d{2}\b|\b\d{10}\b")
_RE_REGON = re.compile(r"\b\d{9}\b|\b\d{14}\b")
_RE_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_RE_IBAN_PL = re.compile(r"\bPL\d{26}\b|\b\d{2}(?:\s?\d{4}){6}\b")
_RE_DOWOD = re.compile(r"\b[A-Z]{3}\s?\d{6}\b")  # nr dowodu osobistego PL
_RE_PHONE = re.compile(r"\b(?:\+48\s?)?(?:\d{3}[\s-]?){3}\b")

_BLOCK_SENSITIVE = {"signature", "stamp"}


def _valid_pesel(d: str) -> bool:
    if len(d) != 11 or not d.isdigit():
        return False
    w = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    s = sum(int(d[i]) * w[i] for i in range(10))
    return (10 - s % 10) % 10 == int(d[10])


def _valid_nip(raw: str) -> bool:
    d = re.sub(r"\D", "", raw)
    if len(d) != 10:
        return False
    w = [6, 5, 7, 2, 3, 4, 5, 6, 7]
    return sum(int(d[i]) * w[i] for i in range(9)) % 11 == int(d[9])


def _valid_regon(d: str) -> bool:
    d = re.sub(r"\D", "", d)
    if len(d) == 9:
        w = [8, 9, 2, 3, 4, 5, 6, 7]
        return sum(int(d[i]) * w[i] for i in range(8)) % 11 % 10 == int(d[8])
    if len(d) == 14:
        w = [2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8]
        return sum(int(d[i]) * w[i] for i in range(13)) % 11 % 10 == int(d[13])
    return False


def detect(text: str) -> list[str]:
    """Zwraca posortowana liste kategorii PII wykrytych w tekscie."""
    hits: set[str] = set()
    for m in _RE_PESEL.findall(text):
        if _valid_pesel(m):
            hits.add("pesel")
    for m in _RE_NIP.findall(text):
        if _valid_nip(m):
            hits.add("nip")
    for m in _RE_REGON.findall(text):
        if _valid_regon(m):
            hits.add("regon")
    if _RE_EMAIL.search(text):
        hits.add("email")
    if _RE_IBAN_PL.search(text):
        hits.add("iban")
    if _RE_DOWOD.search(text):
        hits.add("dowod")
    return sorted(hits)


def annotate(blocks) -> list[str]:
    """Dodaje flagi PII do blokow (in-place) i zwraca redaction_candidates (id).

    Kandydat = blok z wykryta PII LUB blok typu signature/stamp.
    """
    candidates: list[str] = []
    for b in blocks:
        pii = detect(b.text)
        sensitive = b.block_type in _BLOCK_SENSITIVE
        if pii:
            b.flags = sorted(set(b.flags) | {"pii_suspected"} | {f"pii:{p}" for p in pii})
        if sensitive:
            b.flags = sorted(set(b.flags) | {"sensitive_block"})
        if pii or sensitive:
            candidates.append(b.id)
    return candidates
