# Changelog - redline-docx-pl

## bez zmiany wersji - 2026-08-05

Pomiar wendorowanego silnika `vendor/docx-engine` (GenOffice, Apache-2.0).
Workflow bez zmian - skill nadal stoi w calosci na adeu.

- **Sledzone zmiany zmierzone** (71 pism, `verify/revision-vs-adeu.ts`):
  `SaveBlock.revision` nie produkuje Word Track Changes - `w:ins`/`w:del`
  laduja w `w:body` owijajac `w:p`, tekst usuniety zostaje w `w:t` zamiast
  `w:delText`, `adeu extract` nie widzi zmiany 0/71, LibreOffice widzi
  wstawienie ale nie usuniecie. Sciezka `Run.ins`/`Run.del` jest poprawna
  (70/71 rozpoznane), ale nie daje przewagi nad adeu.
- **Tabele zmierzone** (`verify/table-roundtrip.ts`): otoczenie tabeli
  bezpieczne 24/24, ale `patchTableCellTexts` odbudowuje komorke - runy
  splaszczone w 5/24, akapity i `w:br` utracone w 2/24, tekst inny niz
  zamierzony w 1/24.
- **Rekomendacja**: nie wpinac do sciezki zapisu; ewentualnie opcjonalna
  bramka ODCZYTU po `adeu apply`. Decyzja u WM - THIRD_PARTY_INSPIRATIONS.md.
- Harness metryk-only rozszerzony o dwa skrypty; nowe nie wypisuja nawet nazw
  plikow, wiec pomiar idzie na aktach.

## v0.2.0 - 2026-07-13

Harvest wzorcow z evolsb/legal-redline-tools (MIT) - pattern, kod od zera.

- **Memo negocjacyjne** (`scripts/memo_negocjacyjne.py`, zero-dep): schemat
  edits.json rozszerzony o opcjonalne pola `tier` (1-3), `rationale`,
  `walkaway`, `precedent`; memo Markdown grupuje zmiany wg tierow z naglowkiem
  poufnosci. Walidacja: tier 1 bez walkaway = exit 1. Opcja `--adeu` odcina
  pola memo przed `adeu apply`. Granica governance: memo = draft do rozmowy,
  negocjacje prowadzi czlowiek.
- **Skaner placeholderow** (`scripts/skan_placeholder.py`, zero-dep): bramka
  "czy draft nie wychodzi z dziurami" - `[...]`, `[wstaw/insert ...]`, `TBD`,
  `DO UZUPELNIENIA`, `$X`, `___`, `NN/RR`, puste daty i kwoty; raport
  `plik:pozycja` dla .docx (zipfile, paragrafy + naglowki/stopki) i tekstu.
  Exit 1 przy znaleziskach.
- **Framework Tier 1-3** (kategorie ryzyka) - sekcja w SKILL.md z regulami
  negocjacyjnymi per tier.
- Smoke test: memo (4 pozycje, 4 grupy), walidacja (2 bledy wykryte),
  skaner (wszystkie podlozone dziury wykryte - 16 zgloszen w .docx i .md,
  czesc dziur lapia dwa wzorce naraz; czysty plik exit 0) - PASS.

## v0.1.0 - 2026-05-22

Pierwsza wersja. Skill-wrapper nad **adeu** 1.7.5 (MIT, (c) 2026 Dealfluence Oy).

- Workflow 4-krokowy: extract -> edits.json -> apply (natywne Track Changes) -> sanitize.
- Smoke test na polskim .docx: extract / apply (`w:ins`+`w:del`) / sanitize (`Result: CLEAN`) - PASS.
- Integracja z [`let-it-be`](../let-it-be): tresc (PII) vs metadane (sanitize) jako dwie warstwy.
- Atrybucja adeu w 3 miejscach: SKILL.md, THIRD_PARTY_INSPIRATIONS.md, ten plik.

Zrodlo discovery: awesome-legaltech (Vaquill) -> sekcja MCP Servers.
