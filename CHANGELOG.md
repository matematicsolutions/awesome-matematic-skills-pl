# CHANGELOG

Wszystkie istotne zmiany w hubie sa odnotowywane w tym pliku.

Format zgodny z [Keep a Changelog 1.1.0](https://keepachangelog.com/pl/1.1.0/).
Wersjonowanie: CalVer dla calego hubu (`YYYY.MM.DD`), SemVer per-skill.


## [2026.06.30-2] - 2026-06-30

### Added

- `rodo-naruszenie-72h-pl` 1.0.0 -> 1.1.0 i `rodo-dsar-pl` 1.0.0 -> 1.1.0: deterministyczny kalkulator terminow `scripts/gdpr_deadlines.py` (offline, zero zaleznosci, RODO-safe). Liczy 72h od stwierdzenia (art. 33) oraz termin miesieczny z poprawna arytmetyka wg rozporzadzenia EWG 1182/71 (wplyw 31 I -> koniec 28/29 II, przeskok roku, klamrowanie +3mc). Narzedzie agent-native - skill przestaje liczyc termin "na oko".

## [2026.06.30] - 2026-06-30

Nowy bundel `ochrona-danych` - operacje RODO dla kancelarii i inspektora ochrony danych. Cztery skille ugruntowane w artykulach rozporzadzenia i wytycznych EROD/UODO, kazdy konczy draftem do decyzji (granica governance: akt na zewnatrz zostaje czlowiekowi). Nisza potwierdzona discovery (legaltech-scout): istniejace skille DPIA/DSAR/breach sa generyczne-EN i slabo instalowane - tu wersja EU/PL-grounded.

### Added

- Plugin `ochrona-danych` (4 skille): rodo-dpia-pl 1.0.0 (DPIA/OSOD, art. 35-36), rodo-naruszenie-72h-pl 1.0.0 (naruszenie 72h, art. 33-34), rodo-dsar-pl 1.0.0 (zadania osob, art. 12, 15-22), rodo-ropa-dpa-pl 1.0.0 (RoPA + DPA, art. 30, 28). `CLAUDE.md` + `.claude-plugin/plugin.json` + badge'e SVG. Licencja Apache-2.0.

### Changed

- Pakiet: 24 umiejetnosci w 6 bundlach -> 28 umiejetnosci w 7 bundlach. Parytet z hubem EN (`data-protection`).

## [2026.06.29] - 2026-06-29

Nowy bundel `jakosc-tresci` - hub osiaga parytet z hubem EN (`content-quality`). Narzedzia jakosci tekstu polskiego, neutralne tematycznie, bez konektorow.

### Added

- Plugin `jakosc-tresci` (2 skille): humanizer-pl 1.1.0, marko-pl-content 1.0.0. `CLAUDE.md` + `.claude-plugin/plugin.json` + badge'e SVG. Licencja MIT.

### Changed

- `humanizer-pl` 1.0.0 -> 1.1.0: nowa sekcja "Sygnatury statystyczne" (wzorce #30-#34) - cechy mierzone przez detektory AI: rozrzut dlugosci zdan (burstiness), morfologia czasownik/rzeczownik, gestosc i roznorodnosc leksykalna, zakres emocji, mechaniczne przejscia. Oparte na metodologii detekcji Woloszyka i Domaszk (MultiLingual, IX 2025).
- Pakiet: 22 umiejetnosci w 5 bundlach -> 24 umiejetnosci w 6 bundlach.

## [2026.06.26-2] - 2026-06-26

US2 - dokonczenie migracji do bundli. Pozostale 12 plaskich skilli spiete w bundle domenowe; `./skills/` zniknal, marketplace to wylacznie bundle (5 pluginow).

### Added

- Plugin `dokumenty` (4 skille): markitdown, opendataloader-pdf, redline-docx-pl, let-it-be. Bez konektorow.
- Plugin `governance-kancelarii` (3 skille): matematic-konstytucja-ai, matematic-expert-panel, matematic-workspace-backup. Bez konektorow.
- Plugin `dev-mcp` (4 skille, advanced): matematic-spec-driven, matematic-mcp-fastmcp-instructions-pl, matematic-patron-pr-review-pl, matematic-marketplace-installer. Bez konektorow.
- `CLAUDE.md` + `.claude-plugin/plugin.json` w kazdym nowym bundlu.

### Changed

- `orzecznictwo-zrodla` 4 -> 5 skilli: doszedl `webwright-legal-pl` (pobieranie orzeczen spoza MCP przez Playwright), wczesniej plaski.
- 12 skilli przeniesionych z `./skills/` do bundli; katalog `./skills/` usuniety.
- `marketplace.json` 14 -> 5 wpisow (same bundle), wersja `2026.06.26-2`.
- README: sekcja pakietu przebudowana na 5 bundli; instalacja pokazuje wszystkie 5; usunieto zdublowany wpis marketplace-installer.

## [2026.06.26] - 2026-06-26

Restruktura z modelu plaskiego (1 skill = 1 plugin) na bundle domenowe. Major bump: sciezki skilli sie zmieniaja. Inspiracja architektura "Claude for Legal Finland" (Aku Nikkola, MIT) - bierzemy pakowanie, dokladamy nasza multi-jurysdykcje.

### Added

- Plugin `fundament-weryfikacyjny` - bundle instaluj-zawsze z 6 skillami rdzenia weryfikacyjnego, bez konektorow, neutralny jurysdykcyjnie.
- Plugin `orzecznictwo-zrodla` - bundle z 4 skillami zrodlowymi + `.mcp.json` (konektory `saos`/`krs`/`eu-sparql` przez npx).
- Katalog `references/` - wspolne standardy dziedziczone przez skille: `styl-cytatu.md` (tagi pewnosci), `odpowiedzialnosc-i-rodo.md` (5 warstw ochrony), `wdrozenie-w-kancelarii.md`.
- `CLAUDE.md` i `.claude-plugin/plugin.json` w kazdym bundlu. CLAUDE.md samowystarczalny (inline rdzen regul, bo root-owe references nie instaluja sie z pluginem).
- `.matematic/` - konstytucja projektu + spec 001 (model spec-driven).

### Changed

- 10 skilli przeniesionych z `./skills/` do katalogow bundli (`fundament-weryfikacyjny/skills/`, `orzecznictwo-zrodla/skills/`). Linki w README zaktualizowane.
- `marketplace.json` - major bump na `2026.06.26`, 2 wpisy bundli + 12 plaskich skilli (8 zachowanych + 4 z v0.6.0; mieszany layout, wspierany przez Claude Code).
- `scripts/check-marketplace.mjs` przepisany pod model bundle + plaski.
- Instalacja: one-command `/plugin marketplace add` + `/plugin install <bundle>@matematic-skills-pl`.

### Roadmap

- US2: pozostale 8 skilli w bundle (dokumenty / governance-kancelarii / dev-mcp).
- US3: plugin `multi-jurysdykcja-ue` (9 konektorow EU przez uvx) + walidacja w CI.


## [0.6.0] - 2026-05-27

Iteracja 4 - sprint architektury (Safety Tiers R/M/D + references/ offload) + 4 nowe skille z trzech roznych warstw produktowych. Inspiracja wzorcami z google/skills (Safety Tiers, references/ skill leanness, Skill Registry semantic search).

### Dodano

- `let-it-be` v1.0.0 - silnik anonimizacji i pseudonimizacji polskich danych osobowych (PESEL, NIP, REGON, KRS, IBAN, dowod osobisty, telefon, e-mail, imiona z gazetteera ~120, firmy z forma prawna, adres). RODO-safe, offline, deterministyczny, zero zaleznosci (Node >=20). Dwa tryby: `anonimizuj` (nieodwracalne, RODO motyw 26) i `pseudonimizuj`+`odwroc` (odwracalne przez mape, RODO art. 4 pkt 5). Bramka "no PII leaves" (przerwie operacje gdy oryginal przezyl podmiane). Detekcja checksumowa (PESEL/NIP/REGON/KRS/IBAN) + heurystyczna. Lustro `redline-docx-pl` w lancuchu: `let-it-be` czysci tresc -> redline -> `adeu sanitize` czysci metadane.
- `webwright-legal-pl` v1.0.0 - pobiera orzeczenia i akty prawne z polskich serwisow sadowych niedostepnych przez MCP (orzeczenia.ms.gov.pl, sn.pl po 2016, trybunal.gov.pl, EUR-Lex PL) uzywajac Microsoft Webwright (Playwright Firefox, code-as-action). Wrapper kierunkowany pod polskie domeny. Trzy tryby - pobierz po sygnaturze, szukaj po slowie kluczowym, pobierz akt prawny EU/PL po CELEX/ELI. Adresuje luke gdy mcp-saos / mcp-eu-sparql nie pokrywaja danego serwisu.
- `matematic-workspace-backup` v1.0.0 - konfiguracja szyfrowanego backupu Google Workspace dla kancelarii prawnych przez gogcli (steipete/gogcli, MIT) + age (X25519) + prywatne repo Git. Adresuje RODO art. 32 (ciaglosc i odpornosc), ryzyko lockoutu Google i ransomware. Pozycjonowanie: edukator (nie odsprzedajemy gogcli, uczymy klienta z niego korzystac). Safety Tiers R/M/D.
- `matematic-marketplace-installer` v1.0.0 - generuje skrypt instalacyjny MateMatic Marketplace dla prawnikow (Windows .bat, bez Git/npm). Rozpowszechnianie skilli MateMatic do docelowych uzytkownikow (kancelarie) bez wiedzy technicznej. Komenda `/marketplace install`. Safety Tiers R/M/D.

### Zmieniono

- Bundle 18 -> 22 skilli (badge counter README + sekcja "Pakiet 22 umiejetnosci" + marketplace.json plugins[])
- `redline-docx-pl` 2026.05.22 -> 2026.05.27 - dodano Safety Tiers R/M/D dla operacji `sanitize --accept-all` (Tier D nieodwracalne)
- `saos-orzecznictwo` refaktor architektury - SKILL.md 252 -> 125 linii, Python inline wyciagniety do `references/api.md`. Wzorzec references/ offload z google/skills (lean SKILL.md, ciezkie referencje on-demand).
- `szukaj-orzeczen-v2` refaktor architektury - SKILL.md 460 -> 60 linii, 4 pliki references/ (api-saos.md, json-schemat.md, raport-tematyczny.md, tryb-wyszukiwanie.md). Najdrastyczniejszy slim-down w bundle.
- Nowa kategoria README "Higiena tresci / RODO operacyjne" (anonimizacja PII).
- Sekcja "Narzedzia" zmieniona na "Narzedzia - konwersja dokumentow i operacyjne" (dodanie matematic-workspace-backup).
- Sekcja "Orzecznictwo PL / UE" rozszerzona o webwright-legal-pl.
- Sekcja "Metodologia wewnetrzna" rozszerzona o matematic-marketplace-installer.
- `.claude-plugin/marketplace.json` v2026.05.25-2 -> v2026.05.27, +4 wpisy plugins[].
- `assets/badge-*.svg` 18 -> 22 (regeneracja przez `scripts/generate-badges.ps1`).

### Wzorce zaadoptowane z google/skills (MIT)

- **Safety Tiers R/M/D** - 5 skilli oznaczonych poziomami ryzyka operacji (Read-only / Modifies / Destructive). Tier D wymaga jawnego "potwierdzam" od uzytkownika. Wdrozone: redline-docx-pl, matematic-workspace-backup, let-it-be, matematic-marketplace-installer, plus rezerwacja w innych skillach gdzie operacje destruktywne nie wystepuja (R+M wystarczy).
- **references/ offload** - 3 skille z refaktorem (saos-orzecznictwo, szukaj-orzeczen-v2, geo). SKILL.md staje sie lean (~60-125 linii), ciezkie referencje (API spec, skrypty Python, troubleshooting) przeniesione do `references/*.md`. Czytane on-demand przez Read tool, nie w prompcie.
- **Skill Registry semantic search** - rezerwacja koncepcji (nie wdrazana w v0.6.0, kandydat na osobny release).

### Kontekst

google/skills (przewodnik wzorcow dla Claude Agent skills) opublikowany przez Google w maju 2026 dostarczyl trzech wzorcow architektury skilli. Dwa z nich (Safety Tiers, references/ offload) zostaly zaadoptowane do hubu MateMatic w tej iteracji. Trzeci (Skill Registry semantic search) wymaga osobnego workflow i pozostaje w rezerwacji.

## [0.5.0] - 2026-05-25

Sanityzacja - wycofanie wewnetrznego skilla z bundle. Hub pozostaje pelnowartosciowy: 18 skilli zewnetrznych otwartego LegalTech.

### Removed

- Skill anti-slop dla polszczyzny wycofany z bundle (folder + badge SVG + wpis marketplace.json + wszystkie referencje w README, AGENTS.md, CONTRIBUTING.md, NOTICE, CITATION.cff, THIRD_PARTY_INSPIRATIONS.md, generate-badges.ps1, ISSUE_TEMPLATE).
- Skill pozostaje internal-only narzedziem QA maintainerow MateMatic; konwencja MateMatic dla wewnetrznych narzedzi (anti-slop + senior review) jest opisana ogolnie jako "wewnetrzny pipeline QA" bez nazw konkretnych skilli.

### Changed

- Bundle 19 -> 18 skilli (badge counter README, sekcja "Pakiet 18 umiejetnosci", marketplace.json)
- Sekcja "Higiena tresci" w README usunieta (po wycofaniu jedynego skilla w kategorii)
- Sciezki walidacji w CONTRIBUTING.md / ISSUE_TEMPLATE.md / AGENTS.md - "wewnetrzny pipeline QA" zamiast nazw skilli

### Kontekst

Konwencja MateMatic: wewnetrzne narzedzia QA dla tekstow polskich (anti-slop + senior review) sa **internal-only** i NIE pojawiaja sie w publicznych artefaktach organizacji - nie w bundle, nie w README, nie w marketplace. Maintainerzy uzywaja ich przed publikacja, ale slug/persona/wzorce pozostaja prywatne.

## [0.4.0] - 2026-05-25

Iteracja 3 - dodanie 2 skilli metodologicznych (kanon MCP + PR review LegalTech). Cherry-pick z dograh-hq/dograh v1.31.0 (BSD-2).

### Dodano

- `matematic-mcp-fastmcp-instructions-pl` v1.0.0 - kanon dla MCP serverow MateMatic. 5 elementow (instructions w Server constructor, drift test, dwukanalowy auth X-API-Key LUB Bearer, OTel atrybut org_id per-tenant, ToolAnnotations dla read-only). Walidowany na dograh-hq/dograh v1.31.0 i 6 wlasnych MCP MateMatic (mcp-eu-compliance v0.2.0 + mcp-saos/mcp-eu-sparql/mcp-isap/mcp-nsa/mcp-krs v1.1.0). Examples Python (server.py + instructions.py + auth.py + test_instructions_drift.py) jako template.
- `matematic-patron-pr-review-pl` v1.0.0 - recenzent PR/diffow dla LegalTech AI agentow. 14 sekcji (12 z dograh review-pr + 2 MateMatic-specific: PII/audit_log AI Act + drift konstytucji). Format findings `file:line -> problem -> correct pattern`, 3 buckets Blocker/Should-fix/Nit.

### Zmieniono

- Bundle 17 -> 19 skilli
- README badge counter + sekcja "Pakiet 19 umiejetnosci" + 2 wpisy w "Metodologia wewnetrzna"
- `.claude-plugin/marketplace.json` v2026.05.24 -> v2026.05.25, +2 wpisy plugins[]

### Sanitization (audyt prywatnosci 2026-05-25)

- 18 wiki-links `[[X]]` w 2 nowych skillach zamienione na publiczne markdown linki lub opisowy tekst (zgodnie z polityka anty-wiki-link dla publicznych repo).
- Linki do prywatnych memory MateMatic zamienione na opisowy tekst.
- Linki do innych skilli w hubie -> relative markdown links (`../<skill>`).

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

- 108 typograficznych em-dash (`—`) zastapiono ASCII lacznikiem (`-`) w 7 plikach (eu-sparql-search SKILL i references, opendataloader-pdf SKILL, markitdown SKILL, szukaj-orzeczen-v2 SKILL + 2 scripts). 5 didactic / regex em-dash zachowano (regex normalizatorow w citation-grounding-pl i deliverable-fidelity-pl skrypts).
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
### Infrastruktura

- `.claude-plugin/marketplace.json` - manifest plugin marketplace dla Claude Code
- README z taksonomia PL i linkami do pokrewnych repo MateMatic
- CONTRIBUTING.md z formatem SKILL.md + walidacja PRZED PR (citation-grounding-pl + korekta PL)
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

- Internal zero-cloud blueprint skill - zawiera dane sprzedazowe specyficzne dla kancelarii, zostaje prywatny w `~/.claude/skills/`
- Skille produktowe (`matematic-konstytucja-ai`, `matematic-expert-panel`, `matematic-readiness`) - planowane w iteracji 2 po sanitization

## [Wcześniej]

Brak. To pierwsze publiczne wydanie.
