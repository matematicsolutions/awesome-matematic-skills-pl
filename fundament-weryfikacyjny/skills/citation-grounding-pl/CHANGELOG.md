# Changelog - citation-grounding-pl

Format: [Keep a Changelog](https://keepachangelog.com/), wersjonowanie [SemVer](https://semver.org/).

## [2.1.0] - 2026-07-04

### Added
- **Guard STRONY sprawy (ISTNIENIE) - „prawdziwy cytat, fałszywa teza" na poziomie kotwicy.**
  Gdy sygnatura się zgadza, ale nazwy stron zadeklarowane rozjeżdżają się ze stronami rozwiązanego
  źródła (`anchor.strony` / `anchor_resolved.strony`, alias `parties`), to sygnał, że realny cytat
  lub sygnaturę doczepiono do INNEJ sprawy. Miara: nakładanie zbiorów tokenów nośnych nazw stron
  (Jaccard), ze stop-listą form prawnych PL/EU (`sp. z o.o.`, `S.A.`, `przeciwko`, `v.`, `i inni`...).
  Progi: `< 0.30` (przy ≥2 tokenach) = 🔴 rozbieżność (BLOKADA); `0.30–0.50` = 🟡 miękka uwaga
  (możliwa różna forma nazwy tej samej strony). Kalibracja chroni przed fałszywym czerwonym przy
  różnym zapisie tej samej strony (`Bank Millennium S.A.` ≡ `Bank Millennium Spółka Akcyjna`).
- **Test-harness** `scripts/test-grounding.mjs` (zero-dep, rubryka PASS/FAIL, bramka CI) - guard STRONY
  + regresje rdzenia v2.

### Changed
- `ground-citations.mjs` można importować jako bibliotekę (`export verify/stronyOverlap/partyTokens`);
  `main()` odpala się tylko jako CLI (guard `import.meta.url`). Wstecznie kompatybilne.

### Attribution
- Wzorzec porównania nazw stron (Jaccard name-mismatch) zainspirowany `_is_name_mismatch`
  z `john-walkoe/courtlistener_citations_mcp` (MIT). Kod, stop-lista PL/EU i progi napisane od zera;
  logika walidacji reporterów US z tamtego repo NIE jest przenoszona (żyje server-side w CourtListener
  API, poza kontraktem zero-cloud).

## [2.0.0] - 2026-06-04

### Added
- **Gradient weryfikacji ISTNIENIE / TREŚĆ / FRAGMENT** (adaptacja Existence/Content/Paragraph
  z `jeannesulzer/international-criminal-tribunals-skills`, CC BY 4.0). Poziom weryfikacji
  dopasowany per twierdzenie, nie binarnie per dokument.
- **Weryfikacja kotwicy (ISTNIENIE)** - porównanie deklarowanej sygnatury/daty/organu z rozwiązaną
  (`anchor` vs `anchor_resolved`). Rozwijanie skrótów organów (SN/NSA/WSA/TK/TSUE/SA/SO/SR),
  normalizacja dat `DD.MM.YYYY`↔`YYYY-MM-DD`. Rozbieżna kotwica = 🔴 (możliwe falszerstwo).
- **Weryfikacja parafraz (TREŚĆ)** - pokrycie terminów nośnych w źródle (próg 0.7, stopwords PL).
  Status 🟡 `WYMAGA_OSADU` - mechaniczny pre-filtr, substancję rozstrzyga człowiek/paraphrase-judge.
  Zamyka lukę v1, która wprost zwalniała parafrazy z weryfikacji (problem „prawdziwy-cytat-fałszywa-teza").
- **Reguła kalibracji** - status 🟠 `KALIBRACJA`, gdy output twierdzi mocniej niż sięga weryfikacja.
- Macierz `claim_type → wymagany poziom` (`references/gradient-weryfikacji.md`).
- Polska drabinka źródeł / fallback ladder (`references/drabinka-zrodel-pl.md`).
- Szkielet weryfikatora domenowego - template marketplace (`references/szkielet-weryfikatora-domenowego/`).

### Changed
- Skrypt `ground-citations.mjs` przepisany na model wielopoziomowy; wstecznie kompatybilny
  (rekord bez `claim_type` traktowany jako `cytat_doslowny` = zachowanie v1).
- Output skryptu rozszerzony o `wymagany_poziom`, `osiagniety_poziom`, `wymaga_decyzji`.

### Blokada
- Twarda (exit 1): 🔴 NIEZWERYFIKOWANY, ⛔ BRAK ŹRÓDŁA.
- Miękka (decyzja człowieka): 🟠 KALIBRACJA, 🟡 WYMAGA_OSADU.

## [1.0.0]
- Mechaniczny string-match cytatu dosłownego wobec źródła (pattern inspirowany AnttiHero/lavern,
  Apache 2.0). Statusy ZWERYFIKOWANY / ZMODYFIKOWANY / NIEZWERYFIKOWANY / BRAK ŹRÓDŁA.
