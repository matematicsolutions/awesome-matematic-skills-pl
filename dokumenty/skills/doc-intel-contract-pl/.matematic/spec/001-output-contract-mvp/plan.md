# Plan: Document Intelligence Output Contract - MVP

**Spec:** ./spec.md
**Project Type:** `claude-skill` (SKILL.md + scripts/, wzorzec jak matematic-prompt-defense-pl)

## Technical Context
- **Language/Version:** Python 3.13 (stdlib only: json, hashlib, re, argparse, dataclasses, unittest)
- **Primary Dependencies:** ZERO zewnetrznych (spojne z prompt-defense; przenosne do repo klienta)
- **Storage:** N/A (stdin/plik -> stdout/plik JSON)
- **Testing:** unittest (wbudowany), fixtures w tests/fixtures/
- **Target Platform:** Windows-first, cross-platform (czysty stdlib)
- **Performance Goals:** < 50ms per dokument (bez OCR - tylko normalizacja)
- **Constraints:** RODO-safe, offline (zero sieci), deterministyczne
- **Scale/Scope:** dokumenty do ~500 stron / kontrakt do ~50k blokow

## Constitution Check (GATE)

| Bramka | Status | Notatka |
|---|---|---|
| Mission alignment | PASS | ujednolica stack -> gating/redakcja/grounding |
| Article I (zero-cloud) | PASS | tylko stdlib, zero sieci; test AC1.7 pilnuje |
| Article II (idea nie waga) | PASS | wlasny kod MIT, zero wag/kodu Mistral |
| Article III (granica governance) | PASS | produkuje kolejki/kandydatow, nie akty |
| Article IV (determinizm/audyt) | PASS | doc_id SHA256, zero LLM w normalizacji |
| Article V (degradacja) | PASS | bbox/word-conf null + flaga partial |
| Bramka licencji | PASS | MIT, zaleznosci to lokalne CLI (osobne procesy) |
| Bramka ToS/anty-OS | PASS | nie omija ToS nikogo, nie dotyka wag vendora |
| Bramka jakosci | PASS | maly scope MVP, wzorzec sprawdzony (prompt-defense) |
| Bramka strategii | PASS | domyka citation-grounding + PATRON approval cards |

GATE: **PASS** - brak violations, Complexity Tracking niepotrzebny.

## Decyzje (zamkniete Open Questions)
- **Q1 bbox:** znormalizowany `[x0,y0,x1,y1]` w 0-1 (przenosny miedzy DPI/silnikami). Silnik bez bbox -> `null`.
- **Q2 Chandra word-conf:** poza MVP; adapter opendataloader wystarcza na US1. Adapter Chandra = osobny task w US1 z lagodna degradacja.

## Project Structure
```
~/.claude/skills/doc-intel-contract-pl/
├── SKILL.md                          # opis + trigger + workflow
├── .matematic/                       # governance (ten katalog)
├── contract/
│   └── contract.schema.json          # JSON Schema kontraktu (v1.0.0)
├── scripts/
│   ├── contract.py                   # model kontraktu + walidacja + gating (rdzen)
│   ├── adapters/
│   │   ├── opendataloader.py         # JSON opendataloader -> kontrakt
│   │   ├── pdftotext.py              # plain text -> kontrakt (partial)
│   │   └── chandra.py                # (US1 stretch / US3) Chandra -> kontrakt
│   ├── pii_flags.py                  # (US2) reguly PII PL + typed-block flagi
│   ├── grounding_bridge.py           # (US3) kontrakt -> citation-grounding-pl
│   └── normalize.py                  # CLI: --engine <e> <plik|-> [--threshold]
└── tests/
    ├── fixtures/                     # opendataloader.sample.json, plain.sample.txt
    └── test_contract.py              # unittest (determinizm, gating, schema, zero-net)
```

## Research notes
- Kontrakt = nadzbior pol Mistral OCR 4 (block_type, bbox, page/word confidence, dual-mode). [[reference_ocr_output_contract_from_mistral4]]
- Wzorzec pakietu (zero-dep Python CLI + testy + exit codes) skopiowany z matematic-prompt-defense-pl v1.1.1.
- opendataloader-pdf zwraca JSON z reading order + blokami + tabelami -> najbogatszy darmowy adapter na MVP.
