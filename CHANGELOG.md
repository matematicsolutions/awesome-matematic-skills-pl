# CHANGELOG

Wszystkie istotne zmiany w hubie sa odnotowywane w tym pliku.

Format zgodny z [Keep a Changelog 1.1.0](https://keepachangelog.com/pl/1.1.0/).
Wersjonowanie: CalVer dla calego hubu (`YYYY.MM.DD`), SemVer per-skill.

## [0.3.0] - 2026-05-24

Iteracja 2 - dodanie 3 skilli produktowych / metodologicznych + audyt prywatnosci.

### Dodano

- `matematic-konstytucja-ai` v1.0.0 - generator dokumentu governance dla kancelarii (15-40k PLN deployment, AI Implementation Playbook 6-8 tygodni). Cherry-pick patternu github/spec-kit (MIT).
- `matematic-expert-panel` v1.0.0 - 90-min warsztat decyzyjny multi-perspective dla zarzadu kancelarii (7 person). Cherry-pick z SuperClaude-Org/SuperClaude_Framework (MIT).
- `matematic-spec-driven` v0.1.0 - Spec-Driven Development dla wewnetrznych projektow MateMatic (4 fazy + Constitution Check GATE). Cherry-pick z github/spec-kit (MIT).

### Zmieniono

- README sekcja "Strategia / Produkty" dodana (poprzednio brak kategorii produktowych)
- Bundle 14 → 17 skilli

### Sanitization (audyt prywatnosci 2026-05-24 wieczor)

- 108 typograficznych em-dash (`—`) zastapiono ASCII lacznikiem (`-`) w 7 plikach (eu-sparql-search SKILL i references, opendataloader-pdf SKILL, markitdown SKILL, szukaj-orzeczen-v2 SKILL + 2 scripts). 5 didactic / regex em-dash zachowano (humanizer-pl wzorce + regex normalizatorow w citation-grounding-pl i deliverable-fidelity-pl skrypts).
- 11 wiki-links `[[X]]` w matematic-spec-driven/SKILL.md zamienione na markdown inline code lub opisowy tekst.
- 6 wiki-links `[[X]]` w 5 plikach (legal-ai-audit-bundle, legal-data-hunter-pl, matematic-konstytucja-ai, redline-docx-pl + 2 powiazane) zamienione: 3x `[[ADR-0031 PATRON]]` -> markdown link do publicznego ADR-0031, 1x `[[citation-grounding-pl]]` -> backtick, 3x `[[let-it-be]]` -> link do `matematic-anonimizacja-pl`, 1x `[[knowledge-graph-law-firms]]` -> opisowo.
- W AGENTS.md:84 pozostaje cytat wzorca `[[wiki-links]]` jako inline code w instrukcji "nie wpinaj `[[wiki-links]]` do prywatnych memory" - nie wiki-link, tylko cytowany przyklad.

## [0.2.0] - 2026-05-24

Foundation + differentiation.

### Dodano

- AGENTS.md (Linux Foundation standard)
- SECURITY.md (polityka security report + RODO scope)
- NOTICE (atrybucja per-skill licenses)
- THIRD_PARTY_INSPIRATIONS.md (kanon cherry-pick)
- CITATION.cff (citation metadata dla naukowcow prawa)
- scripts/check-marketplace.mjs (zero-deps Node walidator)
- examples/pipeline-end-to-end.md (6-warstwowy lancuch krok po kroku)
- README +6 badges
- CODE_OF_CONDUCT.md (Contributor Covenant 2.1 PL + 3 dodatki MateMatic)
- .github/workflows/check-marketplace.yml (CI GitHub Actions na PR i push)
- .github/ISSUE_TEMPLATE/skill-submission.md i bug-report.md

## [0.1.0] - 2026-05-24

Pierwsze wydanie publiczne. Hub kuratorski 14 umiejetnosci Agent Skills dla polskiego prawa.

### Dodano

- **Warstwa walidacji outputu LLM (6 skilli)**:
  - `legal-request-router-pl` v1.0.0 - klasyfikator zadania, decyduje ktora sciezka weryfikacji uruchomic
  - `intake-sufficiency-pl` v1.0.0 - ocena czy zlecenie ma dosc kontekstu
  - `citation-grounding-pl` v1.0.0 - mechaniczny weryfikator cytatu, anti-halucynacja
  - `adversarial-legal-review-pl` v1.0.0 - czerwony zespol dla pisma wysokiej stawki
  - `deliverable-fidelity-pl` v1.0.0 - weryfikator wiernosci finalnego dokumentu do analizy
  - `legal-ai-audit-bundle` v1.0.0 - paczka audytowa zgodna z AI Act art. 12
- **Warstwa umow / redline (1 skill)**:
  - `redline-docx-pl` v2026.05.22 - natywne Word Track Changes w polskich .docx + sanitize metadanych RODO
- **Warstwa orzecznictwa PL / UE (4 skille)**:
  - `saos-orzecznictwo` v2026.05.24 - sady powszechne, SN, TK, KIO via SAOS REST API
  - `szukaj-orzeczen-v2` v2.0.0 - wyszukiwanie orzeczen PL + grupowanie tematyczne
  - `eu-sparql-search` v2026.05.24 - EUR-Lex / Cellar SPARQL, akty UE i orzecznictwo TSUE
  - `legal-data-hunter-pl` v2026.05.22 - katalog i bulk-harvest dla 11 zrodel polskiego prawa
- **Warstwa konwersji dokumentow (2 skille)**:
  - `markitdown` v2026.04.21 - Microsoft MarkItDown
  - `opendataloader-pdf` v2026.04.21 - PDF -> JSON/MD dla AI z reading order, tabele, headings
- **Warstwa higieny tresci (1 skill)**:
  - `humanizer-pl` v1.0.0 - 29 wzorcow AI-slop w polszczyznie

### Infrastruktura

- `.claude-plugin/marketplace.json` - manifest plugin marketplace dla Claude Code
- README z taksonomia PL i linkami do 14 pokrewnych repo MateMatic
- CONTRIBUTING.md z formatem SKILL.md + walidacja PRZED PR (citation-grounding-pl, humanizer-pl, marko-pl-content)
- LICENSE MIT (kuratorska)
- AGENTS.md (Linux Foundation standard)
- SECURITY.md - polityka security report
- NOTICE - atrybucja per-skill licenses
- THIRD_PARTY_INSPIRATIONS.md - kanon cherry-pick
- CITATION.cff - citation metadata dla naukowcow prawa
- scripts/check-marketplace.mjs - walidator spojnosci marketplace.json vs filesystem
- examples/pipeline-end-to-end.md - jak 6-warstwowy lancuch dziala krok po kroku

### Zasady

- 4 bramki kanonu MateMatic: licencja / anty-OS / jakosc / strategia
- Tajemnica zawodowa: zero danych z akt klienckich w publicznym repo (art. 6 PrAdw, art. 3 RadcPrU)
- RODO-safe by default per-skill
- Vendor-agnostic (Claude Code / Cowork / Claude.ai / OpenAI Codex CLI / Gemini CLI / Manus / Mistral Vibe)
- Format Agent Skills (Anthropic open standard)

### Nie dodano (swiadomie pominiete w v0.1.0)

- `matematic-stack-zero-cloud` - skill zawiera dane sprzedazowe specyficzne dla kancelarii, zostaje prywatny w `~/.claude/skills/`
- Skille produktowe (`matematic-konstytucja-ai`, `matematic-expert-panel`, `matematic-readiness`) - planowane w iteracji 2 po sanitization

## [Wcześniej]

Brak. To pierwsze publiczne wydanie.
