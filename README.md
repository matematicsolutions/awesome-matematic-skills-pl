# awesome-matematic-skills-pl

[![License](https://img.shields.io/badge/license-MIT-brightgreen.svg)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-14-blue.svg)](#pakiet---14-umiejetnosci-w-skills)
[![Plugin](https://img.shields.io/badge/Claude%20Code-plugin%20marketplace-orange.svg)](.claude-plugin/marketplace.json)
[![AGENTS.md](https://img.shields.io/badge/AGENTS.md-Linux%20Foundation-black.svg)](AGENTS.md)
[![Polish law](https://img.shields.io/badge/jurysdykcja-PL%20%2B%20UE-red.svg)](#dlaczego-polski-hub)
[![RODO-safe](https://img.shields.io/badge/RODO--safe-by%20default-green.svg)](#dlaczego-polski-hub)

Polski hub umiejetnosci AI dla prawa - kuratorska lista i pakiet umiejetnosci agentowych (Agent Skills), ktore dzialaja w polskiej praktyce kancelaryjnej, in-house, naukowej i NGO.

Maintainer: [Wieslaw Mazur](https://www.linkedin.com/in/wieslawmazur/) / [MateMatic Solutions](https://matematic.co).
Licencja kuratorska: **MIT** (umiejetnosci w `./skills/` zachowuja wlasne licencje deklarowane w SKILL.md).

> **Po co kolejny hub?** Bo prawo polskie ma wlasna jurysdykcje, wlasne organy (UODO, UOKiK, KNF, KIO, NSA, SN, TK), wlasne procedury (KPC, KPK, KSH, KP) i wlasna konstrukcje obowiazku tajemnicy zawodowej. Globalne huby zostaja na poziomie „GDPR + NDA" - tu schodzimy do przepisow KPC/KPK, sygnatur KIO, ELI URI dziennika ustaw i hash-chain audit-bundle dla AI Act art. 12.

## Co tu znajdziesz

1. **Pakiet 17 umiejetnosci** zainstalowanych w `./skills/` - gotowe do uzycia w Claude Code / Claude Cowork / Claude.ai jako plugin marketplace (`.claude-plugin/marketplace.json`).
2. **Awesome list** - linki do 14 pokrewnych repo produktowych w ekosystemie MateMatic: 6 konektorow MCP, 5 pluginow Claude Code dla praktyki PL, lokalny agent Patron, audyt gotowosci Readiness, przewodniki Praxis.
3. **Standard frontmatter** dla skilli PL (autor, wersja CalVer, licencja per-skill, companion_skills, inspiration) - patrz [CONTRIBUTING.md](CONTRIBUTING.md).

## Lancuch walidacji outputu LLM

W odroznieniu od zachodnich hubow (np. lawve.ai), ktore wystawiaja atomowe klocki, ten hub porzadkuje szesc warstw weryfikacji outputu LLM dla pisma prawnego w jeden lancuch: intake na wejsciu, router decyzyjny, mechaniczny grounding cytatu, kontradyktoryjny adversarial, fidelity koncowy i audit-bundle archiwizacyjny.

```
zlecenie / brief
      |
      v
+-----------+        +-----------------+
| intake-   |------->| legal-request-  |
| sufficien |        | router-pl       |
| cy-pl     |        +-----------------+
+-----------+                |
                              v (decyzja: ktora sciezka)
            +-----------+-----------+-----------+
            |           |           |           |
            v           v           v           v
       szybka      grounding   adversarial  audit-bundle
       odpowiedz   cytatu      red-team     AI Act art. 12
                   citation    review        legal-ai-
                   grounding   adversarial   audit-
                   -pl         -legal-       bundle
                                review-pl
                                  |
                                  v
                          deliverable-fidelity-pl
                          (czy nic nie wypadlo)
                                  |
                                  v
                          deliverable + audit
```

Plugin Claude Code [matematic-legal-verify-pl](https://github.com/matematicsolutions/matematic-legal-verify-pl) pakuje cztery z szesciu warstw (router + grounding + adversarial + audit-bundle) w jeden install dla kancelarii.

---

## Pakiet - 17 umiejetnosci w `./skills/`

### Walidacja outputu LLM (6 warstw)

| Skill | Opis | Licencja | Wersja |
|---|---|---|---|
| [legal-request-router-pl](./skills/legal-request-router-pl) | Klasyfikator zadania - decyduje, ktora sciezka weryfikacji uruchomic. Warstwa NAD walidacja. | Apache-2.0 | 1.0.0 |
| [intake-sufficiency-pl](./skills/intake-sufficiency-pl) | Ocena czy zlecenie/brief MA dosc kontekstu, by zaczac. Generuje pytania do klienta. | Apache-2.0 | 1.0.0 |
| [citation-grounding-pl](./skills/citation-grounding-pl) | Mechaniczny weryfikator cytatu - string-match cytatu prawnego w zrodle. Anti-halucynacja. | Apache-2.0 | 1.0.0 |
| [adversarial-legal-review-pl](./skills/adversarial-legal-review-pl) | Czerwony zespol dla pisma wysokiej stawki - builder/attacker/synthesizer/verifier. | Apache-2.0 | 1.0.0 |
| [deliverable-fidelity-pl](./skills/deliverable-fidelity-pl) | Czy zadna flaga RED nie wypadla z podsumowania - sprawdza wiernosc finalnego pisma do analizy. | Apache-2.0 | 1.0.0 |
| [legal-ai-audit-bundle](./skills/legal-ai-audit-bundle) | Artefakt audytowy AI Act art. 12 - deliverable + slad + log kosztu + manifest SHA256. | Apache-2.0 | 1.0.0 |

### Umowy / Redline

| Skill | Opis | Licencja | Wersja |
|---|---|---|---|
| [redline-docx-pl](./skills/redline-docx-pl) | Natywne Word Track Changes w polskich .docx + sanitize metadanych autora (RODO przy wysylce). | MIT | 2026.05.22 |

### Orzecznictwo PL / UE

| Skill | Opis | Licencja | Wersja |
|---|---|---|---|
| [saos-orzecznictwo](./skills/saos-orzecznictwo) | Polish case law search via SAOS REST API - sady powszechne, SN, TK, KIO. | Apache-2.0 | 2026.05.24 |
| [szukaj-orzeczen-v2](./skills/szukaj-orzeczen-v2) | Wyszukiwanie orzeczen PL + opcjonalne grupowanie tematyczne (klastrowanie, raport DOCX). | Apache-2.0 | 2.0.0 |
| [eu-sparql-search](./skills/eu-sparql-search) | EUR-Lex / Cellar SPARQL - akty UE i orzecznictwo TSUE, CELEX, ELI URI. | Apache-2.0 | 2026.05.24 |
| [legal-data-hunter-pl](./skills/legal-data-hunter-pl) | Catalog + bulk-harvest dla 11 polskich zrodel prawnych (UODO, UOKiK, KNF, KIO, NSA, TK, SN, Sejm ELI). | Apache-2.0 | 2026.05.22 |

### Narzedzia - konwersja dokumentow

| Skill | Opis | Licencja | Wersja |
|---|---|---|---|
| [markitdown](./skills/markitdown) | Microsoft MarkItDown - PDF/Word/Excel/PPT/HTML/EPUB/audio/obrazy/YouTube -> Markdown. | MIT | 2026.04.21 |
| [opendataloader-pdf](./skills/opendataloader-pdf) | Wysokiej jakosci PDF -> JSON/MD: reading order, tabele, headings. Krytyczne dla KRS i postanowien. | Apache-2.0 | 2026.04.21 |

### Higiena treści

| Skill | Opis | Licencja | Wersja |
|---|---|---|---|
| [humanizer-pl](./skills/humanizer-pl) | Usuwa wzorce AI-slop z polskiego tekstu - 29 zdefiniowanych wzorcow obejmujacych slownictwo, gramatyke, typografie, kalki anglicyzmow. | MIT | 1.0.0 |

### Produkty MateMatic (sprzedazowe)

| Skill | Opis | Licencja | Wersja |
|---|---|---|---|
| [matematic-konstytucja-ai](./skills/matematic-konstytucja-ai) | Generuje "Konstytucje AI" - dokument governance dla kancelarii (6 sekcji + AI Implementation Playbook 6-8 tygodni). Cherry-pick patternu github/spec-kit. | Apache-2.0 | 1.0.0 |
| [matematic-expert-panel](./skills/matematic-expert-panel) | Generuje 90-min warsztat multi-perspective dla zarzadu kancelarii - 7 person (compliance / IT security / etyk / partner / junior / klient / regulator). | Apache-2.0 | 1.0.0 |

### Metodologia wewnetrzna (dev pipeline)

| Skill | Opis | Licencja | Wersja |
|---|---|---|---|
| [matematic-spec-driven](./skills/matematic-spec-driven) | Spec-Driven Development dla wewnetrznych projektow MateMatic - 4 fazy (Konstytucja / Specyfikacja / Plan / Zadania) + Constitution Check GATE. | Apache-2.0 | 0.1.0 |

---

## Pokrewne repozytoria - reszta ekosystemu MateMatic

Pakiet wyzej to warstwa walidacji outputu i narzedzia konwersji. Pelny ekosystem to 15 publicznych repo na [github.com/matematicsolutions](https://github.com/matematicsolutions).

### Konektory MCP polskiego i unijnego prawa

| Repo | Co indeksuje |
|---|---|
| [mcp-saos](https://github.com/matematicsolutions/mcp-saos) | Orzecznictwo PL z API SAOS (536k orzeczen powszechnych) |
| [mcp-nsa](https://github.com/matematicsolutions/mcp-nsa) | NSA + 16 WSA via CBOSA (prawo administracyjne, RODO, podatki) |
| [mcp-isap](https://github.com/matematicsolutions/mcp-isap) | Sejm ELI (Dziennik Ustaw + Monitor Polski, 96k+ aktow od 1918) |
| [mcp-krs](https://github.com/matematicsolutions/mcp-krs) | KRS via API MS (spolki, KRS-y, sprawozdania) |
| [mcp-eu-sparql](https://github.com/matematicsolutions/mcp-eu-sparql) | EUR-Lex / Cellar SPARQL (prawo UE) |
| [mcp-eu-compliance](https://github.com/matematicsolutions/mcp-eu-compliance) | Offline korpus EU law (GDPR, AI Act, DORA, NIS2, eIDAS 2.0, CRA) - lokalna SQLite FTS5 |

### Pluginy Claude Code

| Repo | Zastosowanie |
|---|---|
| [matematic-legal-verify-pl](https://github.com/matematicsolutions/matematic-legal-verify-pl) | 4 skille walidacji w jednym plugin: router / grounding / adversarial / audit-bundle |
| [matematic-anonimizacja-pl](https://github.com/matematicsolutions/matematic-anonimizacja-pl) | Silnik anonimizacji PESEL/NIP/REGON/KRS/imion/firm - offline, RODO-safe |
| [matematic-contract-review-pl](https://github.com/matematicsolutions/matematic-contract-review-pl) | Bulk audit portfela umow (NDA/M&A/dostawcze/RODO) - tabular review, pseudonimizacja PII przed LLM |
| [matematic-pomoc-prawna-pl](https://github.com/matematicsolutions/matematic-pomoc-prawna-pl) | Plugin dla nieodplatnej pomocy prawnej, klinik prawa, fundacji i NGO |
| [lpm-pl](https://github.com/matematicsolutions/lpm-pl) | Legal Project Management - status raporty z RAG, scope-change, RAID ryzyk |

### Inne

| Repo | Co to |
|---|---|
| [patron](https://github.com/matematicsolutions/patron) | Lokalny RODO-safe agent AI dla polskich kancelarii. Self-host, audit trail hash-chain, bring-your-own-model. |
| [matematic-readiness](https://github.com/matematicsolutions/matematic-readiness) | Audyt gotowosci kancelarii do AI - 30 pytan, 5 wymiarow, scoring 1-5 + framework Build vs Buy. CC BY-SA 4.0. |
| [praxis](https://github.com/matematicsolutions/praxis) | Praktyczne przewodniki LegalTech/AI governance. CC BY-SA 4.0. |

---

## Instalacja

### Claude Code (plugin marketplace)

```bash
# Sklonuj repo lokalnie
git clone https://github.com/matematicsolutions/awesome-matematic-skills-pl
cd awesome-matematic-skills-pl

# Claude Code wykryje .claude-plugin/marketplace.json automatycznie
# (sprawdz README poszczegolnych skilli w ./skills/<nazwa>/SKILL.md)
```

### Pojedynczy skill jako symlink do ~/.claude/skills/

```powershell
# PowerShell - przyklad citation-grounding-pl
New-Item -ItemType SymbolicLink `
  -Path "$env:USERPROFILE\.claude\skills\citation-grounding-pl" `
  -Target "C:\sciezka\do\awesome-matematic-skills-pl\skills\citation-grounding-pl"
```

```bash
# Bash / WSL
ln -s "$(pwd)/skills/citation-grounding-pl" ~/.claude/skills/citation-grounding-pl
```

---

## Dlaczego polski hub

1. **Polskie organy maja wlasna semantyke.** UODO nie jest tylko ICO/CNIL. KIO ma wlasny tryb 23-dniowy. NSA orzeka kasacyjnie inaczej niz Bundesverwaltungsgericht. Globalny „GDPR + NDA review" tego nie pokrywa.
2. **Tajemnica zawodowa.** Art. 6 PrAdw + art. 3 RadcPrU + tajemnica notarialna + tajemnica komornicza. Wysylka cloud do US bez SCC = naruszenie. Wszystkie nasze skille sa **RODO-safe by default** (lokalna inference albo izolacja).
3. **AI Act art. 12 + art. 13.** Obowiazek prowadzenia rejestru zdarzen (art. 12) i transparency duty (art. 13). [legal-ai-audit-bundle](./skills/legal-ai-audit-bundle) pakuje to natywnie. Zachodnie huby dopiero o tym dyskutuja.
4. **Polski jezyk.** Modele LLM popelniaja inne bledy w polszczyznie (kalki anglicyzmow, naduzycie em-dash, hedging). [humanizer-pl](./skills/humanizer-pl) usuwa to mechanicznie.

---

## Kontrybucje

Patrz [CONTRIBUTING.md](CONTRIBUTING.md). Hub jest otwarty dla polskich prawnikow, in-house counseli, naukowcow prawa, legaltechow i NGO.

Triage PR-ow przez [Wieslaw Mazur](https://www.linkedin.com/in/wieslawmazur/).

## Gdzie dzialaja te skille

Skille trzymaja sie [formatu Agent Skills](https://github.com/anthropics/skills) (Anthropic, otwarty standard). Dzialaja w:

- Claude Code, Claude Cowork, Claude.ai
- OpenAI Codex CLI
- Gemini CLI
- Manus
- Mistral Vibe
- Dowolny IDE/CLI ktory implementuje format

Wybor modelu LLM nalezy do uzytkownika. Hub jest vendor-agnostic z zalozenia.

## Licencja

- Kuratorska (README, taksonomia, marketplace.json): **MIT**
- Per-skill: licencja deklarowana w `SKILL.md` frontmatter (default Apache-2.0 dla MateMatic, MIT lub CC-BY-SA-4.0 dla niektorych komponentow)
- Cytaty prawne i orzecznictwo: copyright wlasciwy zrodlu (Lex/Legalis/SAOS/CBOSA/ELI)

## Kontakt

[matematic.co](https://matematic.co) | [LinkedIn Wieslaw Mazur](https://www.linkedin.com/in/wieslawmazur/) | [github.com/matematicsolutions](https://github.com/matematicsolutions)
