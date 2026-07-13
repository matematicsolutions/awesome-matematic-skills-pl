# Third-party inspirations / dependencies

## adeu (silnik redline)

- **Repo:** https://github.com/dealfluence/adeu
- **PyPI:** `adeu` | **npm:** `@adeu/core`, `@adeu/mcp-server`
- **Licencja:** MIT (c) 2026 Dealfluence Oy
- **Wersja sprawdzona:** 1.7.5 (2026-05-22)
- **Relacja:** ZALEZNOSC, nie cherry-pick kodu. `redline-docx-pl` to cienki wrapper
  workflow PL nad CLI adeu (`uvx adeu ...`). Nie kopiujemy kodu adeu - wolamy go.

### Snapshot licencji (naglowek MIT)

```
MIT License
Copyright (c) 2026 Dealfluence Oy
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction... [pelny tekst: repo/LICENSE]
```

MIT pozwala na uzycie komercyjne, modyfikacje i redystrybucje przy zachowaniu
noty o prawach autorskich. Wrapper spelnia warunek przez atrybucje w 3 miejscach
(SKILL.md, ten plik, CHANGELOG).

### Co adeu robi (czego python-docx nie potrafi)

- `.docx -> Markdown/CriticMarkup` z Semantic Appendix (defined terms, cross-refs, typos)
- wstrzykiwanie **natywnych Word Track Changes** (`w:ins`/`w:del`) bez niszczenia OOXML
- bramka walidacji - blokuje niejednoznaczne dopasowania zanim dotkna pliku
- `sanitize` - strip metadanych autora / last-modified-by / rsid / template / custom XML
- live MS Word (Windows + Word, backend Python)

## Smoke test PL (2026-05-22)

Testowane lokalnie na `umowa.docx` (polski, z metadanymi autora "Jan Kowalski",
last-modified-by "Anna Nowak"):

| Krok | Wynik |
|------|-------|
| `extract` | Polski tekst poprawnie do Markdown (diakrytyki OK) |
| `apply` (edits.json modify + comment) | 1x `w:ins` + 1x `w:del` natywne, autor podmieniony na `--author` |
| `sanitize --keep-markup` | creator + lastModifiedBy wyczyszczone do pustych; autorzy track-changes -> jedna nazwa; rsid/timestampy/template/custom XML usuniete; werdykt `Result: CLEAN` |

Wniosek: silnik dziala na polskim materiale, sanitize realnie domyka wyciek metadanych
Worda (istotne RODO przy wysylce pisma).

## evolsb / legal-redline-tools (wzorce memo + skan)

- **Repo:** https://github.com/evolsb/legal-redline-tools
- **Licencja:** MIT
- **Snapshot:** 2026-07-13
- **Relacja:** PATTERN, nie kod. Dwa wzorce zaadaptowane w v0.2.0:
  1. **Memo negocjacyjne** - pola `tier`/`rationale`/`walkaway`/`precedent`
     w redline JSON + memo grupowane wg tierow (ich `memo.py` generuje PDF
     z naglowkiem "attorney work product"; nasz `memo_negocjacyjne.py`
     generuje Markdown z polskim naglowkiem poufnosci, format wejscia =
     edits.json adeu).
  2. **Skan placeholderow** - bramka przed wysylka (ich `scan.py` lapie
     `$X`/`TBD`/puste nawiasy; nasz `skan_placeholder.py` dodaje wzorce PL:
     `DO UZUPELNIENIA`, `NN/RR`, `dnia __`, kwoty w zl, i raportuje
     `plik:pozycja`).

Kod obu skryptow napisany od zera (Python stdlib, zero zaleznosci). MIT
pozwala takze na kopiowanie kodu z atrybucja - nie skorzystano, bo ich kod
jest zwiazany z ich formatem redlines i python-docx, a nasz z adeu.

## Powiazania

- [`let-it-be`](../let-it-be) - anonimizacja TRESCI (PII PL); adeu sanitize czysci METADANE pliku.
  Dwie rozne warstwy, lancuch: let-it-be tresc -> redline -> adeu sanitize metadane.
