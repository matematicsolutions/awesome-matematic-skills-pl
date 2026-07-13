# Changelog - deliverable-fidelity-pl

Format: [Keep a Changelog](https://keepachangelog.com/), wersjonowanie [SemVer](https://semver.org/).

## [1.1.0] - 2026-07-13

### Added
- **Deterministyczna funkcja werdyktu z jawnymi wagami i progami.** Trzy kroki:
  (A) warunki krytyczne - pominiete lub zbagatelizowane RED, brakujace
  rozstrzygniecie RED -> FAIL; (B) score wazony pokrycia (RED 5 / YELLOW 2 /
  GREEN 1) < 0.85 -> FAIL; (C) 3+ pominietych YELLOW -> najwyzej
  CONDITIONAL_PASS z lista do decyzji czlowieka. Jawne wagi i progi =
  odtwarzalnosc werdyktu z samych liczb pod art. 12 AI Act.
- Przyklad Output zaktualizowany o wyliczenie funkcji werdyktu.

### Attribution
- Wzorzec funkcji werdyktu z AnttiHero/lavern (Apache 2.0), adaptacja od zera -
  wagi severity, prog 0.85 i regula CONDITIONAL_PASS to opracowanie MateMatic.

## [1.0.0] - 2026-05-22

### Added
- Pierwsze wydanie: mechaniczny check reprezentacji ustalen
  (scripts/fidelity-check.mjs, zero-dep) + kontrola wyrywkowa LLM najciezszych
  RED, pominiete RED = blokada.
