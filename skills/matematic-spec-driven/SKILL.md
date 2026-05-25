---
name: matematic-spec-driven
description: Spec-Driven Development dla wewnetrznych projektow MateMatic (PATRON, KGLF, POAS, skille, mikroprodukty, aplikacje). Cherry-pick + adaptacja patternu github/spec-kit (MIT) - 4 fazy (Konstytucja -> Specyfikacja -> Plan -> Zadania) plus opcjonalna walidacja. Tone polski, project-types rozszerzone o claude-skill/video-pipeline/desktop-app/mcp-server/MateMatic-mikroprodukt. Wbudowany Constitution Check GATE z 4 bramkami MateMatic (licencja / ToS-antyOS / jakosc / strategia). Marker `[P]` dla zadan parallel-safe (fan-out subagentow). SEMVER konstytucji per projekt. Uzywaj gdy zaczynasz nowy projekt MateMatic, dodajesz duza ficzer do PATRON/KGLF, planujesz odcinek serialu wymagajacy formalnego rozbicia zadan, projektujesz nowy mikroprodukt (Biblioteka EPUB v3, kolejny dashboard), lub gdy chcesz audytowac istniejacy projekt pod katem zgodnosci z konstytucja MateMatic. Trigger - "spec-driven", "konstytucja projektu", "rozplanuj projekt", "rozbij na zadania", "zaplanuj ficzer", "spec dla projektu", "plan implementacji", "tasks z markerem P", "audyt projektu MateMatic", "Constitution Check". NIE uzywaj dla sprzedazy klientom kancelaria (do tego jest `matematic-konstytucja-ai` - produkt 15-40k PLN).
metadata:
  author: Wieslaw Mazur / MateMatic
  version: 0.1.0
  ratified: 2026-05-20
  project: MateMatic Internal Dev Pipeline
  source_pattern: github/spec-kit (MIT) v0.8.12.dev0 - 4-phase methodology, marker [P], Constitution Check GATE
  related_skill: matematic-konstytucja-ai (sprzedazowy produkt dla kancelarii, NIE myl)
  delivery_format: pliki markdown w katalogu projektu (.matematic/spec/<feature>/)
---

# MateMatic Spec-Driven - dev pipeline dla naszych projektow

Spec-Driven Development dla **wewnetrznych** projektow MateMatic. NIE produkt sprzedazowy dla kancelarii (tym jest `matematic-konstytucja-ai`). Tutaj: my, dla siebie, do PATRON / KGLF / POAS / skilli / mikroproduktow / aplikacji / serialu.

**Source pattern:** github/spec-kit (MIT) v0.8.12 - 4-fazowa methodology Constitution -> Specify -> Plan -> Tasks z marker `[P]` i Constitution Check GATE. Cherry-pick wybranych elementow + adaptacja pod MateMatic project types.

**Status:** v0.1.0 - faza C adopcji spec-kit (po fazie B = sandbox install 2026-05-20). Walidacja w boju przy 1-2 projektach (rekomendacja: nowy konektor SAOS w PATRON albo Biblioteka EPUB v3).

---

## Kiedy uzywac

✅ **TAK:**
- Nowy projekt MateMatic od zera (nowy mikroprodukt, aplikacja, agent)
- Duza ficzer w istniejacym projekcie (PATRON / KGLF / www-matematic)
- Skill ktory ma 4+ podkomendy i zaleznosci (np. matematic-video-pipeline)
- Odcinek serialu "Nie tylko dla orlow" wymagajacy formalnego rozbicia (6-9 scen, fan-out subagentow)
- Audyt istniejacego projektu - czy ma konstytucje? czy ficzer zgadza sie z konstytucja?

❌ **NIE:**
- Sprzedaz kancelarii (uzyj `matematic-konstytucja-ai`)
- Krotki post LI / aktualnosc BW (uzyj `edit-article` albo `linkedin-voice-wieslaw-mazur`)
- Pojedynczy bugfix / refactor w juz dzialajacym module
- MEMO Ej Aj (uzyj `memo-production-pipeline`)

---

## 4 fazy + walidacja

### Faza 1 - `/mspec-konstytucja` (Constitution)

**Output:** `.matematic/konstytucja.md` (jeden plik per projekt, SEMVER versioning).

Konstytucja projektu = niezmienne zasady, na ktore wszystkie downstream artefakty musza sie powolac. **NIE myl** z konstytucja AI dla kancelarii (tamta dotyczy ORGANIZACJI klienta, ta - PROJEKTU MateMatic).

Struktura:

```markdown
# [Nazwa projektu] - Konstytucja

## Mission (1 zdanie)
[Po co ten projekt istnieje, w kontekscie MateMatic]

## Core Principles (3-7 articles)

### Article I - [Nazwa]
[Imperatyw MUST / MUST NOT / SHOULD]

### Article II - [Nazwa]
...

## Boundaries (granice)
- Co projekt **robi**
- Czego projekt **nie robi** (anty-zakres)
- Z czym wspolpracuje (zaleznosci na inne projekty MateMatic)

## Governance (kto decyduje)
- Owner: Wieslaw Mazur
- Reviewers: [wewnetrzny senior review dla content, security-review dla kodu, etc.]
- Amendment process: [jak zmieniac konstytucje]

## Compliance Map (mapowanie na zewnetrzne wymogi)
- AI Act art. ... (jesli dotyczy)
- RODO art. ... (jesli dotyczy)
- AGPL / MIT / CC BY-SA (licencja projektu)

**Version:** 0.1.0 | **Ratified:** YYYY-MM-DD | **Last Amended:** YYYY-MM-DD
```

**Bramki MateMatic** (zawsze pytaj zanim ratifikujesz konstytucje, per regule "discovery to nie rekomendacja" - 4 bramki kanonu):

1. **Licencja** - jaka licencja projektu? Czy zgadza sie z licencjami zaleznosci?
2. **ToS / anty-OS** - czy projekt nie omija ToS dostawcow? Czy nie jest brand-toxic?
3. **Jakosc** - czy mamy kapitalu na utrzymanie? Czy nie zaczynamy 50 projektow na raz?
4. **Strategia MateMatic** - czy pasuje do drabinki sprzedazowej / vault Wieslawa / pozycjonowania?

### Faza 2 - `/mspec-spec <nazwa-feature>` (Specify)

**Output:** `.matematic/spec/<###-nazwa-feature>/spec.md`

User stories + acceptance criteria. Bez kodu, bez tech stacku.

Struktura:

```markdown
# Feature: [Nazwa]

**Branch:** `###-nazwa-feature` (sequential numbering: 001, 002, ...)
**Date:** YYYY-MM-DD
**Status:** Draft | Clarified | Planned | Implemented | Validated

## Problem statement (1 paragraf)
[Co boli, czyje zycie sie poprawi]

## User Stories (priorytety P1, P2, P3...)

### US1 (P1, MVP) - [Nazwa]
**Jako** [persona] **chce** [funkcja] **zeby** [korzysc].

**Acceptance Criteria:**
- [ ] AC1.1: ...
- [ ] AC1.2: ...

**Independent Test:** [jak sprawdzic ze TYLKO US1 dziala, bez US2/US3]

### US2 (P2) - ...
### US3 (P3) - ...

## Non-Goals (anti-scope)
- Tego NIE robimy w tej iteracji
- ...

## Open Questions / NEEDS CLARIFICATION
- [ ] Pytanie 1
- [ ] Pytanie 2
```

Markery `NEEDS CLARIFICATION` przechodza do `/mspec-clarify` (opcjonalna pomocnicza komenda).

### Faza 3 - `/mspec-plan` (Plan)

**Output:** `.matematic/spec/<###-nazwa-feature>/plan.md` + opcjonalnie `research.md`, `data-model.md`, `contracts/`

Technical Context + struktura projektu. **Tu wybierasz project type.**

**Project types MateMatic** (rozszerzone wobec spec-kit):

| Project type | Kiedy | Struktura referencyjna |
|---|---|---|
| `claude-skill` | Nowy skill `~/.claude/skills/<name>/` | `SKILL.md` + ewent. helpers |
| `video-pipeline` | Odcinek serialu / Akademii / MEMO | sceny per katalog, subagenci, ledger |
| `MateMatic-mikroprodukt` | EPUB Biblioteka, NotebookLM pack | input -> processing -> output, manifest |
| `desktop-app` | POAS, lokalne narzedzia kancelaryjne | Tauri/Electron + Rust/Python core + UI |
| `web-app` | PATRON UI, KGLF dashboard, www-matematic | backend/ + frontend/ + tests/ |
| `mobile-app` | Jeszcze brak, ale gotowi | Native iOS/Android albo Capacitor |
| `mcp-server` | matematicsolutions/mcp-saos, nowe konektory | server.py + tools/ + manifest |
| `library/cli` | uv tool, gh extension, helper CLI | src/ + tests/ + pyproject.toml |
| `agent-product` | PATRON jako produkt, agent multi-kancelaria | core/ + agents/ + skills/ + memory/ |

Struktura `plan.md`:

```markdown
# Plan: [Feature]

**Spec:** [link do spec.md]
**Project Type:** [wybor z tabeli wyzej]

## Technical Context
- **Language/Version:** Python 3.13, TypeScript 5.x, ... lub NEEDS CLARIFICATION
- **Primary Dependencies:** ...
- **Storage:** Supabase / SQLite / qdrant / .matematic-RAG / N/A
- **Testing:** pytest / vitest / playwright / brak
- **Target Platform:** Windows-first / Linux server / cross-platform
- **Performance Goals:** [domain-specific]
- **Constraints:** [RODO-safe / offline-capable / low-latency / ...]
- **Scale/Scope:** [n uzytkownikow, m dokumentow]

## Constitution Check (GATE - musi przejsc przed dalszym researchem)

| Bramka konstytucji | Status | Notatka |
|---|---|---|
| Mission alignment | [PASS/FAIL] | Czy projekt sluzy Mission MateMatic? |
| Article I (RODO-safe) | [PASS/FAIL/N/A] | ... |
| Article II (...) | [PASS/FAIL/N/A] | ... |
| Bramka licencji | [PASS/FAIL] | ... |
| Bramka ToS / anty-OS | [PASS/FAIL] | ... |
| Bramka jakosci | [PASS/FAIL] | ... |
| Bramka strategii | [PASS/FAIL] | ... |

Jesli `FAIL` - albo zmien feature, albo udokumentuj w **Complexity Tracking** ponizej.

## Project Structure
[Drzewo katalogow ad-hoc dla wybranego project type]

## Research notes
[Co sprawdzilismy - alternatywy, benchmarki, ocena repo]

## Complexity Tracking (tylko jesli violations)

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| ... | ... | ... |
```

### Faza 4 - `/mspec-zadania` (Tasks)

**Output:** `.matematic/spec/<###-nazwa-feature>/tasks.md`

Format: `[ID] [P?] [Story] Description`

- **`[P]`** = parallel-safe (different files, no dependencies). Dla MateMatic = mozna zlecic rownoleglemu subagentowi.
- **`[US1]`** = story tag dla traceability.
- Sciezki plikow MUSZA byc absolutne lub relatywne do roota projektu.

5 faz wykonania:

```markdown
## Phase 1 - Setup
- [ ] T001 Init projektu / branch / katalogi
- [ ] T002 [P] Konfiguracja linterow
- [ ] T003 [P] Setup test runner

## Phase 2 - Foundational (BLOKUJE wszystkie user stories)
- [ ] T004 Schema bazy / wspolne modele
- [ ] T005 [P] Auth / autoryzacja
- [ ] T006 Logger / observability

## Phase 3 - US1 (P1, MVP) - [nazwa]
- [ ] T010 [P] [US1] Model w src/models/...
- [ ] T011 [US1] Service w src/services/... (depends T010)
- [ ] T012 [US1] Endpoint / komenda / UI

**Checkpoint:** US1 niezaleznie testowalne, deployowalne jako MVP.

## Phase 4 - US2 (P2) - ...
## Phase 5 - US3 (P3) - ...

## Phase N - Polish
- [ ] TXXX [P] Dokumentacja / README
- [ ] TXXX Performance tuning
- [ ] TXXX Wewnetrzny senior review (jesli tresc tekstowa)
- [ ] TXXX [P] Security review

## Parallel Opportunities
[Eksplicite ktore taski mozna odpalic na raz - dla orchestratora subagentow]
```

**Wazne dla MateMatic:**

- Markery `[P]` w `tasks.md` to formalny input dla wewnetrznego orchestratora pipeline'a wideo MateMatic - mowi orchestratorowi ktore subagenty palic rownolegle (zamiast manualnie projektowac graf questow).
- `US1` jako MVP = zawsze pierwsza ratowalna wartosc, nawet jesli reszta poslizgnie sie.
- Phase 2 (Foundational) BLOKUJE - to bardzo wazne, nie pomijac, inaczej downstream taski sie sypia (jak w PATRON gdzie wpierw brakowalo Supabase self-host).

### Walidacja (opcjonalne) - `/mspec-analyze`

**Output:** `.matematic/spec/<###-nazwa-feature>/analyze-report.md`

Cross-artifact consistency check. Uruchamiac po `/mspec-zadania`, przed implementacja. Sprawdza:

- Czy wszystkie AC z `spec.md` maja odpowiadajace taski w `tasks.md`?
- Czy plan.md respektuje konstytucja.md (re-check Constitution Check GATE)?
- Czy taski oznaczone `[P]` faktycznie nie maja shared-file conflicts?
- Czy projekt nie ma niezamknietych `NEEDS CLARIFICATION`?

---

## SEMVER konstytucji

Za kazdym razem gdy zmieniamy `konstytucja.md`:

- **MAJOR** (1.x.x -> 2.0.0) - usuniecie/zmiana fundamentalnego Article
- **MINOR** (x.1.x -> x.2.0) - dodanie nowego Article lub Section
- **PATCH** (x.x.1 -> x.x.2) - doprecyzowanie istniejacego Article bez zmiany semantyki

Footer:

```markdown
**Version:** 1.2.0 | **Ratified:** 2026-05-20 | **Last Amended:** 2026-06-15
```

Plus changelog `## Amendments` w samej konstytucji (audyt-friendly per AI Act art. 12).

---

## Konwencje plikow

```
<project-root>/
├── .matematic/
│   ├── konstytucja.md                        # SEMVER, ratifikowana
│   └── spec/
│       ├── 001-pierwsza-ficzura/
│       │   ├── spec.md
│       │   ├── plan.md
│       │   ├── research.md       (opcjonalnie)
│       │   ├── data-model.md     (opcjonalnie)
│       │   ├── contracts/        (opcjonalnie - API/MCP/CLI)
│       │   ├── tasks.md
│       │   └── analyze-report.md (opcjonalnie)
│       ├── 002-druga-ficzura/
│       └── ...
└── (reszta projektu)
```

**NIE myl** z `.specify/` (to katalog spec-kit CLI z sandbox). My uzywamy `.matematic/` zeby nie mieszac.

`.gitignore` - **nic z `.matematic/` nie ignorujemy** (artefakty governance = first-class).

---

## Czego ten skill NIE robi

- NIE instaluje specify-cli (to wczesniejsza faza B - sandbox install).
- NIE generuje plikow automatycznie - Claude (ty) piszesz `konstytucja.md`/`spec.md`/`plan.md`/`tasks.md` na podstawie templates w tej instrukcji, w rozmowie z Wieslawem.
- NIE wymaga `.claude/skills/speckit-*` w projekcie - to skill samowystarczalny.
- NIE zastapuje `matematic-konstytucja-ai` - tamten = sprzedaz, ten = wewnetrzny dev.
- NIE zastapuje wewnetrznego pipeline'a wideo MateMatic - tamten = orkiestracja runtime, ten = projekt artefaktow planu. Wspolpraca: `tasks.md` z `[P]` jest INPUTEM dla pipeline'a.

---

## Powiazania z reszta stack MateMatic

| Skill / proces | Jak wspolpracuje |
|---|---|
| `matematic-konstytucja-ai` | Brat-blizniak (produkt klient vs dev nasz). Wspolny rdzen, inny target audience. |
| matematic video pipeline (internal) | `tasks.md` -> graf questow orchestratora. `[P]` markery -> fan-out subagentow. |
| `matematic-video-governance` | 4 fazy validation (pre-compose / render / post / distribution) wbudowane w `/mspec-analyze` dla projektow video-pipeline. |
| wewnetrzny senior review MateMatic | Auto-dorzucany jako reviewer w `## Governance` konstytucji projektow tresciowych. |
| `anthropic-skills:matematic-reviewer` | Auto-dorzucany dla projektow kodowych (PATRON / KGLF / POAS). |
| KGLF (Knowledge Graph for Law Firms) | KGLF jako Reference Implementation - juz ma ADR-y, jest dobrym kandydatem na pierwszy projekt z `.matematic/konstytucja.md` (rozszerzajacy ADR-y SEMVER konstytucja). |

---

## Pierwsze 2 walidacje w boju (rekomendacja)

1. **Nowy konektor SAOS w PATRON** (planowany od 2026-05-19) - czysty greenfield, dobry test dla `/mspec-spec` + `/mspec-plan` z project type `mcp-server`.
2. **Biblioteka EPUB v3** (jesli planujemy 3-ci tom) - prosta domena, test dla project type `MateMatic-mikroprodukt`.

NIE testowac na PATRON core ani KGLF (oba juz maja ADR-y, ryzyko podwojnego trackingu).

---

## Dziennik szlifu

- **2026-05-20 - v0.1.0 - ratyfikacja.** Skill powstal po fazie B (sandbox install spec-kit). Decyzja: dwa osobne skille (sprzedazowy `matematic-konstytucja-ai` + dev `matematic-spec-driven`) zamiast jednego rozszerzonego. Project types rozszerzone o `claude-skill / video-pipeline / desktop-app / mcp-server / MateMatic-mikroprodukt` (korekta Wieslawa: "aplikacje też możemy zacząć robić, nie ograniczaj nas"). Walidacja w boju czeka.
