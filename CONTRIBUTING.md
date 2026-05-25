# Jak dodac umiejetnosc do hubu

Hub jest otwarty dla polskich prawnikow, in-house counseli, naukowcow prawa, legaltechow i kazdej osoby, ktora chce udostepnic dzialajacy schemat pracy z LLM w polskiej praktyce.

## Co przyjmujemy

- Skille AI w formacie [Agent Skills](https://github.com/anthropics/skills) (SKILL.md + ewentualne `references/`, `scripts/`, `assets/`).
- Skille dzialajace zarowno w Claude Code, Claude Cowork, Claude.ai, OpenAI Codex CLI, Gemini CLI, Manus, Mistral Vibe (write once, use anywhere).
- Skille pod polskie prawo, polskie organy (UODO, UOKiK, KNF, KIO, NSA, SN, TK), polskie procedury (KPC, KPK, KSH, KP) lub prawo UE z polska perspektywa.
- Skille tooling/utility uzyteczne w kancelarii (konwersja dokumentow, anonimizacja, redline, audit-bundle, walidacja outputu LLM).

## Co odrzucamy

- Skille bez licencji w frontmatter.
- Skille naruszajace RODO (np. wymagajace wysylki danych klienta do US bez DPA / SCC).
- Skille naruszajace tajemnice zawodowa (art. 6 PrAdw / art. 3 RadcPrU) - czyli cokolwiek co domyslnie wysyla klient-data do hostowanego LLM bez izolacji.
- Skille reklamowe konkretnego komercyjnego SaaS bez warstwy abstrakcji (vendor-lock-in).
- Skille z halucynowanymi cytatami (Art. X / sygnatura Y) bez weryfikacji - sprawdz cytat przez `citation-grounding-pl` ZANIM zglosisz PR.

## Format SKILL.md

```yaml
---
name: nazwa-skilla-pl
description: >
  Jednoakapitowy opis co skill robi, dla kogo, kiedy uruchomic. Konkretne
  triggery (frazy uzytkownika ktore uruchamiaja skill). Jezyk polski lub
  bilingualny PL/EN.
metadata:
  author: Twoje Imie / Twoja kancelaria
  version: 2026.05.24       # CalVer rekomendowany
  license: Apache-2.0       # lub MIT / CC-BY-SA-4.0 / AGPL-3.0
  inspiration: opcjonalnie - skad pomysl (atrybucja kanonu cherry-pick)
  companion_skills: opcjonalnie - inne skille z hubu z ktorymi sie spina
---

# Tytul skilla

## Uzycie
## Pipeline
## Przyklady
## Ograniczenia
```

## Walidacja PRZED PR

Zanim zglosisz PR uruchom u siebie:

1. **citation-grounding-pl** na wszystkich cytatach prawnych w SKILL.md (Art. X, sygnatury, ELI URI).
2. **Korekta tekstu PL** - czy tekst czyta sie naturalnie, bez naduzywania em-dash, hedging, kalek anglicyzmow, oczywistej reguly trojki.
3. **Test trigger phrases** - czy skill aktywuje sie na frazach z `description`.

## Jak zglosic

1. Fork repo.
2. Dodaj swoj skill jako `./skills/<nazwa-autor>/` (nazwa kebab-case + Twoj suffix dla disambiguation, np. `dpia-pl-jan-kowalski`).
3. Dodaj wpis w `.claude-plugin/marketplace.json`.
4. Dodaj entry w `README.md` pod odpowiednia kategoria.
5. PR z opisem: dla kogo skill, jaka stawka (high-stakes/low-stakes), ile razy uzyles w realnej praktyce.

## Pytania

[Wieslaw Mazur](https://www.linkedin.com/in/wieslawmazur/) / MateMatic Solutions / [matematic.co](https://matematic.co)
