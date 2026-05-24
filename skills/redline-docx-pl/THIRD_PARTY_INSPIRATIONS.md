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

## Powiazania

- [[let-it-be]] - anonimizacja TRESCI (PII PL); adeu sanitize czysci METADANE pliku.
  Dwie rozne warstwy, lancuch: let-it-be tresc -> redline -> adeu sanitize metadane.
