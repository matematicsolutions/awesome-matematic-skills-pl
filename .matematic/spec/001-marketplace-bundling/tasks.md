# Tasks: Marketplace bundling (001)

Format: `[ID] [P?] [Story] Opis`. `[P]` = parallel-safe (różne pliki, brak zależności).

**BRAMKA STAŁA (każdy polski tekst):** zanim jakikolwiek nowy PL tekst (references/, CLAUDE.md, opisy w marketplace.json, README) trafi do repo - kolejno **humanizer-pl** (zdjęcie slopu) -> **marko-pl-content** (werdykt + zarzuty plik:linia) -> obsługa zarzutów. Dotyczy T010, T011, T012, T021b, T023, T030 (opisy), T071. Nie czekać z tym do T072.

## Phase 1 - Setup
- [ ] T001 Branch `001-marketplace-bundling` (odbić od aktualnego main repo).
- [ ] T002 [P] Research: potwierdzić dokładne nazwy paczek npm konektorów PL (saos/krs/eu-sparql) - `npm view @matematicsolutions/<name>`; zapisać w plan.md research notes. BLOKUJE T021.
- [ ] T003 [P] Snapshot obecnego płaskiego marketplace.json do CHANGELOG (dowód migracji + dla pinned userów).

## Phase 2 - Foundational (BLOKUJE US1)
- [ ] T010 references/styl-cytatu.md - styl cytatu PL (orzeczenie/ustawa/dziennik) + 3-stopniowe tagi pewności (Zweryfikowane/Do sprawdzenia/Nie używać), tag przy linii. Wzór: Aku viittaustyyli.md, treść PL własna.
- [ ] T011 [P] references/odpowiedzialnosc-i-rodo.md - 5 warstw ochrony przed disclaimerem, tajemnica zawodowa, DPA gdy chmura, anonimizacja lokalna, output=draft (AI Act art.50).
- [ ] T012 [P] references/wdrozenie-w-kancelarii.md - wdrożenie: ocena danych wrażliwych, DPA art.28 RODO, audit trail, kiedy NIE wnosić materiału do narzędzia.
- [ ] T013 Schemat docelowy + szkielet validate.mjs: zdefiniować kontrakt walidacji bundla (source istnieje / skills>=1 SKILL.md / .mcp.json poprawny JSON / CLAUDE.md jest). BLOKUJE T040.

## Phase 3 - US1 (P1, MVP)

### Fundament (bez MCP)
- [ ] T020 [US1] Utworzyć `fundament-weryfikacyjny/` + przenieść 6 skilli (`git mv ./skills/{legal-request-router-pl,intake-sufficiency-pl,citation-grounding-pl,adversarial-legal-review-pl,deliverable-fidelity-pl,legal-ai-audit-bundle}` -> `fundament-weryfikacyjny/skills/`). Treść SKILL.md NIETKNIĘTA.
- [ ] T021b [US1] `fundament-weryfikacyjny/CLAUDE.md` - fallback-safety odsyłający do references/ (3 standardy), BEZ .mcp.json (świadomie - zero tarcia, instaluj-zawsze).

### Orzecznictwo (z konektorami PL)
- [ ] T021 [US1] Utworzyć `orzecznictwo-zrodla/` + przenieść 4 skille (`git mv ./skills/{saos-orzecznictwo,szukaj-orzeczen-v2,eu-sparql-search,legal-data-hunter-pl}`). Zależy od T002 (nazwy paczek).
- [ ] T022 [US1] `orzecznictwo-zrodla/.mcp.json` - saos/krs/eu-sparql przez `npx -y @matematicsolutions/mcp-<name>` (nazwy z T002).
- [ ] T023 [US1] `orzecznictwo-zrodla/CLAUDE.md` - fallback + odwołanie references/ + nota o konektorach (read-only publiczne API).

### Manifest (major bump)
- [ ] T030 [US1] Przepisać `.claude-plugin/marketplace.json`: version major bump (np. 2026.07.0), wpisy 2 bundli (fundament-weryfikacyjny, orzecznictwo-zrodla) z `source` na dir bundla; usunąć płaskie wpisy 19 skilli; dodać komentarz/pole placeholder "praktyki prawa - roadmap" jeśli schema pozwala (inaczej w README). Zależy T020,T021,T022.

## Phase 4 - Walidacja US1
- [ ] T040 [US1] Rozszerzyć `scripts/validate.mjs` o kontrakt bundla (T013); uruchomić - zielone na 2 nowych pluginach.
- [ ] T041 [US1] Test ręczny: `/plugin marketplace add ./` lokalnie + `/plugin install fundament-weryfikacyjny` i `orzecznictwo-zrodla`; potwierdzić: fundament działa bez MCP, orzecznictwo widzi konektory. (AC1-Independent Test)
- [ ] T042 [US1] leak-scan repo przed jakimkolwiek push (RODO/sekrety) - bramka konstytucji.

**Checkpoint US1:** 2 bundle instalowalne jedną komendą, fundament frictionless, references dziedziczone, walidacja zielona. Ratowalna wartość = MVP do shipu.

## Phase 5 - US2 (P2) - pozostałe bundle
- [ ] T050 [P] [US2] Plugin `dokumenty` (markitdown, opendataloader-pdf, redline-docx-pl) + CLAUDE.md.
- [ ] T051 [P] [US2] Plugin `governance-kancelarii` (matematic-konstytucja-ai, matematic-expert-panel) + CLAUDE.md.
- [ ] T052 [P] [US2] Plugin `dev-mcp` (matematic-spec-driven, matematic-mcp-fastmcp-instructions-pl, matematic-patron-pr-review-pl) + CLAUDE.md, oznaczony "advanced".
- [ ] T053 [US2] Dopisać 3 bundle do marketplace.json; validate.mjs zielone.

## Phase 6 - US3 (P3) - leapfrog + CI + tagi
- [ ] T060 [US3] Plugin `multi-jurysdykcja-ue`: `.mcp.json` z 9 EU (`uvx <pkg>`); README ostrzega o wymogu `uv`; opis = leapfrog multi-jurysdykcja.
- [ ] T061 [P] [US3] CI `.github/workflows`: validate.mjs na każdy push (czerwone gdy source nie istnieje).
- [ ] T062 [P] [US3] (stretch) Konwencja widocznych tagów pewności udokumentowana w references/styl-cytatu.md jako standard outputu.

## Phase 7 - Polish
- [ ] T070 [P] Sekcja "Czego NIE robi" (negative scope) w każdym SKILL.md gdzie brakuje (Article V).
- [ ] T071 README.md + CHANGELOG.md: opis modelu bundli, instrukcja instalacji, mapa migracji płaski->bundle.
- [ ] T072 marko-pl-content review opisów pluginów + README (PL).
- [ ] T073 Bramka publikacji: zielone WM + leak-scan -> push origin.

## Parallel Opportunities
- T002, T003 równolegle (Phase 1).
- T010, T011, T012 równolegle (3 references, różne pliki).
- T020 (fundament) i T021/T022/T023 (orzecznictwo) - różne katalogi, równolegle PO T002. T030 (manifest) czeka na oba.
- US2: T050, T051, T052 pełny fan-out (3 subagenty, różne pluginy).
- US3: T061, T062 równolegle.

## Mapa AC -> Tasks (traceability)
- AC1.1 -> T020,T021b,T030 · AC1.2 -> T021,T022,T030 · AC1.3 -> T020,T021 · AC1.4 -> T021b,T023 · AC1.5 -> T010,T011,T012,T021b,T023 · AC1.6 -> T002,T022,T041 · AC1.7 -> T013,T040
