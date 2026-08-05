# Tasks: Document Intelligence Output Contract - MVP

Format: `[ID] [P?] [Story] Opis`. `[P]` = parallel-safe (rozne pliki, brak zaleznosci).

## Phase 1 - Setup
- [x] T001 Struktura katalogow + .matematic (konstytucja/spec/plan/tasks)
- [x] T002 [P] contract/contract.schema.json - JSON Schema kontraktu v1.0.0

## Phase 2 - Foundational (BLOKUJE user stories)
- [x] T003 scripts/contract.py - dataclass Block + Contract, doc_id SHA256, to_json, validate() wobec schematu, gating(threshold)

## Phase 3 - US1 (P1, MVP) - Normalizacja + gating  [DONE 2026-07-01, 16 testow]
- [x] T010 [P] [US1] scripts/adapters/opendataloader.py - JSON opendataloader -> list[Block] (bbox->0-1, block_type map, confidence)
- [x] T011 [P] [US1] scripts/adapters/pdftotext.py - plain -> list[Block] (bbox=null, confidence=null, flaga partial)
- [x] T012 [US1] scripts/normalize.py - CLI (--engine, --threshold, plik|stdin, --pretty), exit 0/2
- [x] T013 [P] [US1] tests/fixtures/ - opendataloader.sample.json + plain.sample.txt
- [x] T014 [US1] tests/test_contract.py - determinizm doc_id, gating wg progu, schema-valid, zero-net, pdftotext=partial

**Checkpoint US1:** OSIAGNIETY - `normalize.py --engine opendataloader fixture.json` zwraca kontrakt z gating (review: table 0.62 + signature 0.41; auto: reszta). MVP deployowalne.

## Phase 4 - US2 (P2) - Typed blocks + PII  [DONE 2026-07-01, +12 testow]
- [x] T020 [P] [US2] scripts/pii_flags.py - regex PL (PESEL/NIP/REGON + checksum, IBAN, email, nr dowodu) -> flagi
- [x] T021 [US2] normalize.py: redaction_candidates[] wpiete (annotate przed build_contract), --no-pii opt-out
- [x] T022 [P] [US2] tests/test_pii.py (checksum PESEL/NIP/REGON pozytywne+negatywne, annotate, schema-valid)

## Phase 5 - US3 (P3) - Grounding + vision podpis  [DONE 2026-07-01]
- [x] T030 [P] [US3] scripts/grounding_bridge.py - kontrakt -> zadanie citation-grounding-pl; lokalizuje cytat w blokach + anchor_resolved {page,bbox,block_id} (7 testow, E2E OK)
- [x] T031 [US3] scripts/adapters/chandra.py - Chandra OCR (layout DOM) -> Block; bbox 0-1 (piksele/norm), block conf = MIN linii, degradacja. +testy
- [x] T032 [US3] scripts/signature.py - heurystyka podpisu/pieczatki (dol strony+krotki+low-conf); detektor vision wstrzykiwalny (opt-in, poza domyslna sciezka). +testy

## Phase 5b - EXTRA (poza pierwotnym spec) - OCR PATRONa
- [x] T033 scripts/adapters/gaius.py - OCR PATRONa/Gaius-Lex /ocr/poll {text,engine} -> Block (tekstowy, partial); engine_variant=default|google_doc_ai. Schemat: enum +gaius, pole engine_variant. +testy

## Phase N - Polish  [DONE]
- [x] T040 [P] SKILL.md (trigger, workflow, przyklad) + humanizer-pl + marko-pl (werdykt: przecietne -> naprawiony dryf engine/flags)
- [x] T041 [P] README.md + humanizer-pl (czysto: zero em-dash/kalk)
- [x] T042 wpis do drabinki PDF w CLAUDE.md (krok 6 normalizacji) + humanizer-en na poscie EN (bramka OK)

## Wynik koncowy
57 testow zielonych, 4 silniki (opendataloader/chandra/gaius/pdftotext), 11 modulow, zero-dep stdlib.
Trojkat domkniety: confidence-gating + redaction_candidates (PII+podpis) + grounding (cytat->region).
POZOSTAJE tylko runtime: potwierdzenie vision podpisu na realnym skanie (detektor wstrzykiwalny gotowy).

## Parallel Opportunities
- Runda A (po T003): T010 ‖ T011 ‖ T013 (rozne pliki).
- Runda B (US2): T020 ‖ T022.
- Runda C (US3): T030 ‖ T031.
