# Feature: Marketplace bundling - pluginy domenowe + fundament + references

**Branch:** `001-marketplace-bundling`
**Date:** 2026-06-26
**Status:** Clarified (4 forki rozstrzygnięte przez WM 2026-06-26)

## Problem statement

`awesome-matematic-skills-pl` ma działający `marketplace.json`, ale w modelu PŁASKIM: 1 skill = 1 plugin (19 wpisów `source:./skills/X`), bez bundlowania, fundamentu, agentów ani konektorów. Konkurenci z tej samej fali (Aku Nikkola FI, niemiecki prawnik v397) instalują **bundle domenowe jedną komendą** z fundamentem "instaluj zawsze". Nasza substancja (rdzeń weryfikacyjny + 9 konektorów EU live) jest mocniejsza, ale forma pakowania zostaje w tyle. Cel: dorównać formie PRZY wykorzystaniu naszej przewagi - multi-jurysdykcja, której FI-only Aku nie ma.

## Rozstrzygnięte decyzje (forki WM)

1. **Taksonomia: FUNKCJONALNA** (nie praktyki prawa). Nasze skille to funkcje. Half-measure praktyk = cargo-cult. ALE manifest zostawia jawny placeholder "praktyki prawa - roadmap".
2. **Konektory: OBA Z GŁOWĄ.** Fundament bez `.mcp.json` (zero tarcia, instaluj-zawsze). Bundel domenowy niesie konektory, których jego user realnie używa (PL: saos/krs/eu-sparql, lekkie TS/npx). 9 konektorów EU (Python/uvx) = osobny opt-in plugin "Multi-jurysdykcja UE", nie domyślny ciężar.
3. **Wersjonowanie: MAJOR BUMP**, czysta restruktura `./skills/*` -> `./<plugin>/skills/*`. Stary płaski tag zostaje w historii gita.
4. **MVP = US1:** Fundament + references/ + jeden bundle (Orzecznictwo & Źródła z konektorami PL). Reszta domen i 9 EU w kolejnych iteracjach.

## Model docelowy taksonomii (pełny, do referencji - NIE cały w MVP)

| Plugin | Skille | .mcp.json | Iteracja |
|---|---|---|---|
| **fundament-weryfikacyjny** (instaluj zawsze) | legal-request-router-pl, intake-sufficiency-pl, citation-grounding-pl, adversarial-legal-review-pl, deliverable-fidelity-pl, legal-ai-audit-bundle | BRAK (celowo) | US1 |
| **orzecznictwo-zrodla** | saos-orzecznictwo, szukaj-orzeczen-v2, eu-sparql-search, legal-data-hunter-pl | saos, krs, eu-sparql (PL, npx) | US1 |
| **dokumenty** | markitdown, opendataloader-pdf, redline-docx-pl | BRAK | US2 |
| **governance-kancelarii** | matematic-konstytucja-ai, matematic-expert-panel | BRAK | US2 |
| **dev-mcp** (advanced) | matematic-spec-driven, matematic-mcp-fastmcp-instructions-pl, matematic-patron-pr-review-pl | BRAK | US2 |
| **multi-jurysdykcja-ue** (opt-in, leapfrog) | (brak skilli / opis) | de/at/es/fi/ie/nl/se/fr/lu eli-mcp (uvx) | US3 |
| *(praktyki prawa - placeholder roadmap)* | *(do zbudowania)* | - | przyszłość |

## User Stories

### US1 (P1, MVP) - Fundament + references + bundle Orzecznictwo
**Jako** prawnik instalujący nasz marketplace **chcę** jedną komendą wziąć fundament weryfikacyjny i bundel orzecznictwa z konektorami PL **żeby** mieć rdzeń anti-halucynacji + źródła bez składania 10 skilli ręcznie.

**Acceptance Criteria:**
- [ ] AC1.1: `marketplace.json` (major bump) ma wpis pluginu `fundament-weryfikacyjny` z 6 skillami, BEZ `.mcp.json`.
- [ ] AC1.2: `marketplace.json` ma wpis `orzecznictwo-zrodla` z 4 skillami + `.mcp.json` deklarującym saos/krs/eu-sparql (npx).
- [ ] AC1.3: Pliki skilli fizycznie przeniesione do `./fundament-weryfikacyjny/skills/*` i `./orzecznictwo-zrodla/skills/*` (treść SKILL.md niezmieniona).
- [ ] AC1.4: Każdy plugin ma `CLAUDE.md` (fallback-safety odwołujący się do references/).
- [ ] AC1.5: `references/` zawiera 3 wspólne standardy (styl-cytatu, odpowiedzialnosc-i-rodo, wdrozenie-w-kancelarii), a CLAUDE.md pluginów się do nich odwołuje.
- [ ] AC1.6: `.mcp.json` w orzecznictwo-zrodla używa komend, które realnie działają (npx dla TS konektorów); zweryfikowane że schemat jest poprawny.
- [ ] AC1.7: Walidacja struktury (skrypt) potwierdza, że każdy `source` w marketplace.json istnieje na dysku i ma SKILL.md w środku.

**Independent Test:** `/plugin marketplace add` lokalnie na tym repo + `/plugin install fundament-weryfikacyjny` i `orzecznictwo-zrodla` instalują się bez błędu; fundament działa bez żadnego MCP; orzecznictwo widzi konektory PL.

### US2 (P2) - Pozostałe bundle funkcjonalne
**Jako** user **chcę** też dokumenty / governance / dev-mcp jako bundle **żeby** cała oferta była spójnie spakowana.
**AC:** pluginy dokumenty, governance-kancelarii, dev-mcp w marketplace.json + przeniesione skille + CLAUDE.md każdy.
**Independent Test:** każdy z 3 instaluje się osobno.

### US3 (P3) - Multi-jurysdykcja UE (leapfrog) + walidacja CI + tagi pewności
**Jako** prawnik pracujący transgranicznie **chcę** opcjonalnie plugin z 9 konektorami EU **żeby** jedną komendą mieć prawo 9 krajów.
**AC:** plugin multi-jurysdykcja-ue z `.mcp.json` (uvx, 9 EU); README ostrzega o wymogu `uv`; CI waliduje strukturę marketplace na każdy commit; (stretch) konwencja widocznych tagów pewności w references/.
**Independent Test:** instalacja opt-in nie psuje fundamentu; CI czerwone gdy source nie istnieje.

## Non-Goals (anti-scope)
- NIE budujemy nowych skilli substancjalnych (praktyki prawa) - tylko placeholder roadmap.
- NIE Drift-Watch EU (Säädösvahti x9) - to OSOBNY projekt (drugi ruch), nie ta iteracja.
- NIE zmieniamy treści SKILL.md poza dodaniem sekcji negative-scope (i to jako polish, nie blocker MVP).
- NIE cennik, NIE gating - Article VII konstytucji.
- NIE publikacja na origin bez zielonego WM + leak-scan.

## Open Questions / NEEDS CLARIFICATION
- [ ] Q-A: Czy `.mcp.json` w pluginie ma odpalać konektory przez `npx @matematicsolutions/mcp-saos` (published npm) czy lokalny path? (Tier-3: mcp-isap/saos/nsa/krs/eu-sparql są na npm jako @matematicsolutions/*). Rekomendacja: npx published - przenośne. Weryfikacja nazw paczek w fazie plan.
- [ ] Q-B: Czy fundament-weryfikacyjny promuje adversarial-legal-review do `agents/*.md` (wzór Aku), czy zostaje skillem? Rekomendacja MVP: zostaje skillem, agenty w osobnej iteracji.
- [ ] Q-C: Czy `dev-mcp` w ogóle na publicznym marketplace dla prawników, czy to wewnętrzne? Rekomendacja: zostaje (są darmowe, Article VII), ale oznaczyć "advanced/dev".
