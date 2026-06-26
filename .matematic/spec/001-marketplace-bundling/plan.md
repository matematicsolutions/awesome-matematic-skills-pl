# Plan: Marketplace bundling

**Spec:** ./spec.md
**Project Type:** `claude-skill / marketplace-repo` (repo dystrybucyjne pluginów Claude Code; nie aplikacja)

## Technical Context
- **Format:** JSON (`marketplace.json` wg schematu `json.schemastore.org/claude-plugin-marketplace.json`) + Markdown (SKILL.md, CLAUDE.md, references/).
- **Plugin layout (cel):** `./<plugin>/{CLAUDE.md, .mcp.json?, skills/<skill>/SKILL.md, agents/<agent>.md?}` - wzór z działającego repo Aku (akunikkola/claude-for-legal-finland).
- **Konektory MCP w .mcp.json:** PL przez `npx` z published npm (Tier-3): `@matematicsolutions/mcp-saos`, `@matematicsolutions/mcp-krs`, `@matematicsolutions/mcp-eu-sparql` (5 TS live na npm; nazwy do potwierdzenia w T-research). 9 EU przez `uvx <pkg>` z PyPI (US3).
- **Storage:** pliki w repo, brak bazy.
- **Testing:** skrypt walidacyjny Node (`scripts/validate.mjs` JUŻ ISTNIEJE w repo - rozszerzyć o check bundli) + ręczny `/plugin install` lokalny.
- **Target Platform:** Claude Code + Cowork (cross-platform), Windows-first dev.
- **Constraints:** RODO-safe (fundament lokalny bez MCP), kompatybilność łamana świadomie (major bump), zero gatingu.
- **Scale/Scope:** 19 skilli -> 5 pluginów funkcjonalnych (US1: 2) + 1 opt-in EU (US3).

## Constitution Check (GATE)

| Bramka konstytucji | Status | Notatka |
|---|---|---|
| Mission alignment | PASS | Wprost: "instalowalny jedną komendą hub", forma dorównuje EU. |
| Article I (suoja mekanismeista) | PASS | Fundament = rdzeń weryfikacyjny; references/ niosą mechanizmy. |
| Article II (RODO-safe) | PASS | Fundament BEZ .mcp.json = nic nie wychodzi; konektory tylko read-only publiczne API. |
| Article III (vendor-agnostic) | PASS | Plugin format Claude Code, metoda przenośna. |
| Article IV (metoda/substancja) | PASS | Fundament neutralny; konektory per-jurysdykcja; 9 EU opt-in. |
| Article V (negative scope) | PARTIAL | Sekcja "Czego NIE robi" dodawana jako polish (P3), nie wszystkie skille mają dziś. Dopuszczone - nie blokuje MVP. |
| Article VI (output=draft) | PASS | Bez zmian w treści skilli; zasada zachowana. |
| Article VII (generosity) | PASS | Pełne, darmowe, zero bramek. |
| Bramka licencji | PASS | Per-skill Apache/MIT zachowane w nowych wpisach; marketplace nie nadpisuje. |
| Bramka ToS / anty-OS | PASS | Oficjalny mechanizm `/plugin marketplace`. |
| Bramka jakości | PASS (z MVP) | Wąski MVP (1 bundle) adresuje koszt utrzymania; wzorzec replikowalny. |
| Bramka strategii | PASS | Domyka lukę Aku, zasila Boutique-funnel + PATRON. |

**GATE: PASS** (Article V = świadome PARTIAL, udokumentowane, nie violation wymagający Complexity Tracking).

## Project Structure (cel po US1)

```
awesome-matematic-skills-pl/
├── .claude-plugin/
│   └── marketplace.json            # major bump, wpisy bundli (nie płaskie skille)
├── references/                     # NOWE - wspólne standardy
│   ├── styl-cytatu.md              # + 3-stopniowe tagi pewności
│   ├── odpowiedzialnosc-i-rodo.md  # 5 warstw, tajemnica, DPA, output=draft
│   └── wdrozenie-w-kancelarii.md   # anonimizacja, audit, DPA art.28
├── fundament-weryfikacyjny/        # NOWY plugin (US1)
│   ├── CLAUDE.md                   # fallback -> references/
│   └── skills/                     # przeniesione z ./skills/
│       ├── legal-request-router-pl/SKILL.md
│       ├── intake-sufficiency-pl/SKILL.md
│       ├── citation-grounding-pl/SKILL.md
│       ├── adversarial-legal-review-pl/SKILL.md
│       ├── deliverable-fidelity-pl/SKILL.md
│       └── legal-ai-audit-bundle/SKILL.md
├── orzecznictwo-zrodla/            # NOWY plugin (US1)
│   ├── CLAUDE.md
│   ├── .mcp.json                   # saos/krs/eu-sparql przez npx
│   └── skills/
│       ├── saos-orzecznictwo/SKILL.md
│       ├── szukaj-orzeczen-v2/SKILL.md
│       ├── eu-sparql-search/SKILL.md
│       └── legal-data-hunter-pl/SKILL.md
├── scripts/
│   └── validate.mjs                # ROZSZERZYĆ o walidację bundli
├── (./skills/ pozostałe 9 - migrowane w US2)
└── README.md / CHANGELOG.md        # opis nowego modelu + migracja
```

## Research notes
- **Działający wzór:** repo Aku (MIT) potwierdza, że plugin = dir z `CLAUDE.md` + `.mcp.json` + `skills/*/SKILL.md` + `agents/*.md` ładuje się przez `/plugin marketplace add`. Kopiujemy strukturę, nie treść.
- **Nasz manifest** już używa poprawnego `$schema`; rozszerzamy semantykę wpisu (source -> dir bundla zamiast dir skilla).
- **Konektory npm** (Tier-3, pamięć): @matematicsolutions/mcp-isap@1.1.1 + saos/nsa/krs/eu-sparql na npm z provenance. POTWIERDZIĆ dokładne nazwy paczek (mcp-saos vs saos) w T002 przed wpisaniem do .mcp.json.
- **validate.mjs** istnieje (z płaskiego modelu) - przerobić na walidację: każdy plugin.source istnieje, ma skills/ z >=1 SKILL.md, .mcp.json (jeśli jest) to poprawny JSON, CLAUDE.md istnieje.

## Complexity Tracking
(brak violations wymagających uzasadnienia - GATE PASS)
