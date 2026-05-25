# AGENTS.md - awesome-matematic-skills-pl

Plik standardu [agents.md](https://agents.md) (Linux Foundation / Agentic AI Foundation) - kanoniczne instrukcje dla agentow AI pracujacych z tym repozytorium. Czytany natywnie przez Cursor, Codex (OpenAI), Jules (Google), Devin / Windsurf, Aider, Amp, Factory, GitHub Copilot, Claude Code.

## Cel projektu

To repo to **polski hub kuratorski Agent Skills dla prawa**. Dwie warstwy:

- `./skills/` - pakiet 14 skilli zainstalowanych lokalnie (bundle bezposrednio uzywalny).
- README + `.claude-plugin/marketplace.json` - awesome list i manifest plugin marketplace.

To **nie jest produkt komercyjny** - kanon kuratorski MIT. Wartoscia jest uporzadkowana mapa polskich umiejetnosci AI dla prawa, ktora pozwala kancelariom i NGO wpiac gotowe klocki w swoja praktyke bez budowania ich od zera.

## Kontekst MateMatic (TWARDE OGRANICZENIA)

[MateMatic Solutions](https://matematic.co) = lokalne RODO-safe narzedzia AI dla polskich kancelarii prawnych. Zero-cloud self-host, vendor-neutral, audytowalne.

Hub musi byc:

- **Polski lub bilingualny** - tytuly skilli, opisy, triggery zaczynaja od polskiej praktyki, prawo polskie/UE.
- **RODO-safe by default** - kazdy skill nie wysyla danych klienta cloud bez izolacji lub DPA / SCC.
- **Vendor-agnostic** - format Agent Skills (Anthropic open standard) dziala w Claude Code, Cowork, Claude.ai, OpenAI Codex CLI, Gemini CLI, Manus, Mistral Vibe.
- **Bez halucynacji cytatu** - kazdy cytat prawny w SKILL.md MUSI przejsc `citation-grounding-pl` przed PR.

## Struktura repo

```
.claude-plugin/
  marketplace.json     - manifest plugin marketplace (14 wpisow)
.github/
  (issue templates - planowane)
skills/
  <name>/
    SKILL.md           - frontmatter + body
    references/        - lazy-loaded dokumentacja
    scripts/           - kod wykonujacy
    THIRD_PARTY_INSPIRATIONS.md  - per-skill kanon cherry-pick (jezeli istnieje)
scripts/
  check-marketplace.mjs - walidator spojnosci marketplace.json vs ./skills/
examples/
  pipeline-end-to-end.md - jak 6-warstwowy lancuch dziala krok po kroku
README.md              - kuratorska lista + bundle bundle 14 skilli
CONTRIBUTING.md        - jak dodac umiejetnosc
LICENSE                - MIT (kuratorska)
NOTICE                 - atrybucja per-skill licenses
CHANGELOG.md           - kalendarz zmian
SECURITY.md            - polityka security
THIRD_PARTY_INSPIRATIONS.md - kanon cherry-pick na poziomie repo
CITATION.cff           - citation metadata dla naukowcow prawa
AGENTS.md              - ten plik
```

## Build i test

Brak kompilacji.

**Test spojnosci** = `node scripts/check-marketplace.mjs` - waliduje, ze:
- kazdy wpis w `.claude-plugin/marketplace.json` ma odpowiadajacy folder w `./skills/<name>/`
- kazdy folder w `./skills/` jest deklarowany w marketplace.json
- kazdy SKILL.md ma frontmatter z `name`, `description`
- nazwy w marketplace.json = nazwy folderow

**Test wizualny** = otworz `README.md` w GitHub web i sprawdz, czy tabele renderuja sie poprawnie.

## Zasady pisania (CRITICAL)

### Tajemnica zawodowa
- **NIGDY** danych z akt prawdziwych spraw w README, SKILL.md, CONTRIBUTING ani w opisach w marketplace.json. Tajemnica adwokacka (art. 6 PrAdw) + radcowska (art. 3 RadcPrU). Patrz polityka opisana w SECURITY.md.
- Zero kwot, dat dziennych, sygnatur, inicjalow, nazw firm z realnych spraw. Wzory testowe: `Jan Kowalski` / `Anna Nowak` (polski John Doe).

### Tresc
- **Polski jezyk** w opisach SKILL.md i README. EN dopuszczalne w trigger keywords i SKILL.md dla skilli ktore z natury sa EN-first (np. saos-orzecznictwo description ma fragmenty EN).
- **Bez em-dash** (`—`) - tylko lacznik `-`.
- **Bez polskich znakow w commit messages**.
- **Bez emoji ozdobnych** - swiadome brand emoji OK (np. 🦅 w kontekscie cyklu serialowego).
- **Polskie cudzyslowy** „..." nie proste angielskie "...".

### Walidacja
- **Wewnetrzny pipeline QA dla tekstow PL** ZAWSZE przed commitem zmian w plikach PL (README, CONTRIBUTING, SKILL.md, CHANGELOG, NOTICE). Maintainerzy MateMatic uzywaja wlasnych narzedzi QA przed publikacja - kontrybutorzy zewnetrzni odpowiadaja za czytelnosc i poprawnosc tekstu PL.

## Czego NIE robic (twarde reguly)

- **NIE dodawaj danych klientow**, leadow, cen specyficznych dla kancelarii, planow sprzedazowych - to memory prywatne, nie publiczne repo.
- **NIE wpinaj `[[wiki-links]]`** do prywatnych memory plikow MateMatic - to martwe linki w publicznym repo.
- **NIE wstawiaj sales-marketingu** ("rewolucyjny", "game changer", "must-have") - GitHub buyer to technical / legal buyer, nie marketing.
- **NIE kopiuj tresci skilli CC-BY-NC-ND ani AGPL** do tego repo (kuratorska licencja MIT) - tylko pattern + wlasna tresc. Patrz `THIRD_PARTY_INSPIRATIONS.md`.
- **NIE zostawiaj outdated linkow** - jezeli skill zmienia nazwe lub zostaje wyciagniety, fix natychmiast.

## Powiazane repo MateMatic (utrzymuj synchronizacje)

| Repo | Licencja | Zastosowanie |
|---|---|---|
| [patron](https://github.com/matematicsolutions/patron) | AGPL-3.0 | Lokalny agent AI - moze wykorzystywac skille z tego hubu |
| [matematic-legal-verify-pl](https://github.com/matematicsolutions/matematic-legal-verify-pl) | Apache 2.0 | Plugin pakujacy 4 z 6 warstw walidacji w jeden install |
| [matematic-anonimizacja-pl](https://github.com/matematicsolutions/matematic-anonimizacja-pl) | Apache 2.0 | Silnik anonimizacji PII PL - companion do skilli grounding |
| [matematic-contract-review-pl](https://github.com/matematicsolutions/matematic-contract-review-pl) | Apache 2.0 | Bulk audit umow - pipeline uzywa redline-docx-pl |
| [matematic-pomoc-prawna-pl](https://github.com/matematicsolutions/matematic-pomoc-prawna-pl) | Apache 2.0 | Plugin dla NGO - uzywa intake-sufficiency-pl pattern |
| [lpm-pl](https://github.com/matematicsolutions/lpm-pl) | Apache 2.0 | Legal Project Management - companion do audit-bundle |
| [mcp-saos](https://github.com/matematicsolutions/mcp-saos) | MIT | Konektor MCP - dane zrodlowe dla saos-orzecznictwo skill |
| [mcp-nsa](https://github.com/matematicsolutions/mcp-nsa) | MIT | Konektor MCP NSA - dane zrodlowe |
| [mcp-isap](https://github.com/matematicsolutions/mcp-isap) | MIT | Konektor MCP Sejm ELI |
| [mcp-krs](https://github.com/matematicsolutions/mcp-krs) | MIT | Konektor MCP KRS |
| [mcp-eu-sparql](https://github.com/matematicsolutions/mcp-eu-sparql) | MIT | Konektor MCP EUR-Lex - dane zrodlowe dla eu-sparql-search |
| [mcp-eu-compliance](https://github.com/matematicsolutions/mcp-eu-compliance) | MIT | Offline korpus EU law |
| [praxis](https://github.com/matematicsolutions/praxis) | CC BY-SA 4.0 | Przewodniki LegalTech |
| [matematic-readiness](https://github.com/matematicsolutions/matematic-readiness) | CC BY-SA 4.0 | Audyt gotowosci kancelarii |
| [.github](https://github.com/matematicsolutions/.github) | CC BY-SA 4.0 | Profile organizacji |

## Kompatybilnosc agentow

Standard [AGENTS.md](https://agents.md). Dla Claude Code dodatkowo plik [CLAUDE.md](./CLAUDE.md) (jezeli istnieje - obecnie ten AGENTS.md wystarcza, Claude Code czyta `AGENTS.md` natywnie).

Skille w tym repo trzymaja sie [Agent Skills format](https://github.com/anthropics/skills) - format otwarty, niezalezny od dostawcy LLM.

## Licencja

- Kuratorska (README, taksonomia, marketplace.json, ten AGENTS.md): **MIT**
- Per-skill: licencja zadeklarowana w `SKILL.md` frontmatter i `marketplace.json`. W bundle v0.1.0 wszystkie skille sa Apache-2.0 lub MIT (patrz NOTICE).

## Kontakt

- **Maintainer**: [Wieslaw Mazur](https://www.linkedin.com/in/wieslawmazur/)
- **Strona**: [matematic.co](https://matematic.co)
- **Email**: kontakt@matematic.co
