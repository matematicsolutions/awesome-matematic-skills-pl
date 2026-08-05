# Feature: Document Intelligence Output Contract - MVP

**Branch:** `001-output-contract-mvp`
**Date:** 2026-07-01
**Status:** Planned

## Problem statement
Nasza drabinka PDF (pdftotext -> markitdown -> opendataloader -> Chandra OCR ->
vision) daje piec roznych ksztaltow wyjscia. Nic tego nie ujednolica, wiec nie
mamy jednego miejsca, w ktorym da sie: (a) powiedziec "temu fragmentowi ufam w
0.4, niech spojrzy czlowiek", (b) znalezc blok podpisu/PII do redakcji, (c) podac
cytatowi wspolrzedne w dokumencie. Mistral OCR 4 pokazal kontrakt, ktory to robi -
odtwarzamy go na wlasnym, lokalnym stacku.

## User Stories

### US1 (P1, MVP) - Normalizacja do kontraktu + confidence-gating
**Jako** operator pipeline'u LegalTech **chce** przepuscic wyjscie silnika OCR/PDF
przez jedna funkcje i dostac kontrakt JSON `{blocks[], gating}` **zeby** od razu
wiedziec, ktore bloki ida do czlowieka, a ktore auto-approve.

**Acceptance Criteria:**
- [ ] AC1.1: Adapter mapuje wyjscie **opendataloader-pdf** (JSON) -> kontrakt.
- [ ] AC1.2: Adapter mapuje **pdftotext** (plain) -> kontrakt (bbox=null, flaga `partial`).
- [ ] AC1.3: Kontrakt zawiera per blok: `id, page, bbox, block_type, text, confidence, flags`.
- [ ] AC1.4: Confidence-gating: prog (domyslnie 0.85) -> `review_required[]` + `auto_approved[]`.
- [ ] AC1.5: `doc_id` = SHA256 wejscia; ten sam input = ten sam doc_id (determinizm).
- [ ] AC1.6: Walidacja kontraktu wzgledem JSON Schema (kontrakt niezgodny = blad, exit 2).
- [ ] AC1.7: Zero wywolan sieciowych (test to potwierdza).

**Independent Test:** podaj fixture opendataloader JSON -> dostajesz poprawny
kontrakt z niepustym `gating.review_required` dla bloku o confidence < progu.
Dziala bez US2/US3.

### US2 (P2) - Typed blocks + flagi wrazliwe (redakcja RODO)
**Jako** DPO/prawnik **chce** zeby kontrakt oznaczyl bloki typu `signature`/`stamp`
oraz `pii_suspected` **zeby** przygotowac liste do redakcji.

**Acceptance Criteria:**
- [ ] AC2.1: Reguly (regex/heurystyka) flaguja PII PL: PESEL, NIP, REGON, e-mail, IBAN, nr dowodu.
- [ ] AC2.2: Bloki z flaga trafiaja do `redaction_candidates[]` (propozycja, nie akt - Article III).
- [ ] AC2.3: Zero LLM (deterministyczne), zgodne z Chandra-lokalnie.

### US3 (P3) - Most do citation-grounding + vision dla podpisu
**Jako** autor opinii **chce** zeby cytat z dokumentu dostal `{page, bbox, block_id}`
**zeby** grounding wskazywal region, nie tylko string.

**Acceptance Criteria:**
- [ ] AC3.1: Eksport kontraktu do formatu wejsciowego [[citation-grounding-pl]].
- [ ] AC3.2: Detekcja podpisu/pieczatki: opcjonalny rung-5 (Read/vision) na blokach niskiej pewnosci, jawnie oznaczony `detector: vision` w metadanych.

## Non-Goals
- Wlasny silnik OCR.
- Automatyczna redakcja/anonimizacja (tylko lista kandydatow).
- Integracja UI PATRONa (osobny spec, po MVP).
- Cloud OCR.

## Open Questions / NEEDS CLARIFICATION
- [ ] Q1: bbox normalizowany 0-1 czy piksele? (propozycja: 0-1, przenosne miedzy DPI) - DECYZJA w plan.md.
- [ ] Q2: czy Chandra OCR daje word-confidence w naszej instalacji? (do sprawdzenia przy adapterze Chandra - US1 nie wymaga, opendataloader wystarcza na MVP).
