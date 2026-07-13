# Changelog - adversarial-legal-review-pl

Format: [Keep a Changelog](https://keepachangelog.com/), wersjonowanie [SemVer](https://semver.org/).

## [1.2.0] - 2026-07-13

### Added
- **Panel rozbieżności (dissent) jako moduł OPCJONALNY (sekcja 4c).** Dla 1-2
  filarów NOŚNYCH przy wysokiej stawce: pytanie interpretacyjne multiple-choice
  (2-4 opcje) do co najmniej 2 niezależnych ocen (drugi model / drugi przebieg
  z innym promptem bez transkryptu debaty / człowiek). Split = FINDING pierwszej
  klasy, cytowany verbatim w deliverable, nie ukrywany. Pętla rozstrzygania:
  dociągnięcie autorytetu (saos-orzecznictwo / ISAP / eu-sparql-search) → jedna
  runda re-vote → split, który przetrwał dowody, idzie do human gate jako
  NIEPEWNE. Jawna bramka kosztu (domyślnie 0 pytań panelu).
- Spójność z v1.1.0: split nierozstrzygnięty wpina się w werdykt NIEPEWNE
  (sekcja 3) i wagę 0.25 funkcji werdyktu (sekcja 4b); re-vote panelu nie
  konsumuje limitu 2 rund rewizji (sekcja 4a).

### Attribution
- Wzorzec z AnttiHero/lavern (Apache 2.0, `src/mcp/tools/dissent.ts`),
  adaptacja od zera - polskie i unijne źródła autorytetu zamiast CourtListener,
  wpięcie w istniejące sekcje zamiast osobnego rejestru panelistów.

## [1.1.0] - 2026-07-13

### Added
- **NIEPEWNE jako werdykt pierwszej klasy (sekcja 3).** Synthesizer obok
  przetrwał/osłabiony/obalony ma czwartą kategorię z podkategoriami
  NIEWYSTARCZAJĄCY_DOWÓD / DOKUMENT_NIEJEDNOZNACZNY i obowiązkiem wskazania,
  jakiego dowodu brakuje. Zakaz cichego podciągania niepewności pod "przetrwał".
- **Pętla rewizji z twardym limitem 2 rund (sekcja 4a).** Trzeci fail verifiera
  nie jest kolejną iteracją, tylko obowiązkową eskalacją do człowieka z listą
  nierozstrzygniętych zarzutów. Licznik rund w raporcie.
- **Deterministyczna funkcja werdyktu (sekcja 4b).** Warunki krytyczne -> FAIL;
  score ważony po filarach (przetrwał 1.0 / osłabiony 0.5 / NIEPEWNE 0.25 /
  obalony 0.0) < 0.6 -> FAIL; 2+ filary osłabione lub NIEPEWNE -> najwyżej
  WYŚLIJ_WARUNKOWO. Jawne wagi i progi = odtwarzalność werdyktu pod art. 12 AI Act.
- Przykład Output zaktualizowany o wiersz NIEPEWNE, licznik rund i wyliczenie score.

### Attribution
- Wszystkie trzy wzorce z AnttiHero/lavern (Apache 2.0), adaptacja od zera -
  podkategorie, wagi, progi i polska semantyka to opracowanie MateMatic.

## [1.0.0] - 2026-05-24

### Added
- Pierwsze wydanie: bramka kosztu high-stakes, 4 role (builder / attacker /
  synthesizer / verifier), 10-punktowa kontrola końcowa, integracja z
  citation-grounding-pl i legal-ai-audit-bundle.
