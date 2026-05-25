---
name: Zgloszenie nowego skilla
about: Propozycja dodania umiejetnosci do hubu (nie PR, tylko zgloszenie do dyskusji)
title: '[SKILL] '
labels: ['skill-submission', 'needs-triage']
assignees: ''
---

## Co skill robi

W jednym akapicie - co robi, dla kogo, kiedy uruchomic. Trzymaj sie konkretu, bez marketingowego belkotu.

## Kontekst prawny / branzowy

- **Jurysdykcja**: PL / UE / inna (wymien)
- **Obszar prawa**: KPC / KPK / KSH / RODO / AI Act / inne
- **Organ / regulator** (jezeli dotyczy): UODO / UOKiK / KIO / NSA / KNF / SN / TK / inne

## Trigger phrases

3-5 polskich fraz, ktore powinny aktywowac skill. Przyklad: "DPIA", "ocena skutkow", "art. 35 RODO".

## Format

- [ ] Skill ma frontmatter z polami: `name`, `description`, `metadata.author`, `metadata.version`, `metadata.license`
- [ ] Licencja: Apache-2.0 / MIT / inna (deklaruj jasno)
- [ ] Skill dziala w Claude Code (testowane na min. 1 realnym przypadku)
- [ ] Brak danych z akt prawdziwych spraw (tajemnica zawodowa, patrz [SECURITY.md](../SECURITY.md))

## Walidacja PRZED PR

- [ ] `citation-grounding-pl` na cytatach prawnych w SKILL.md (jezeli sa)
- [ ] Tekst PL przeszedl korekte / review pod katem czytelnosci i poprawnosci

## Powiazane skille

Jezeli twoj skill spina sie z istniejacymi z hubu - wymien (`citation-grounding-pl`, `saos-orzecznictwo` etc.).

## Doswiadczenie wlasne

Ile razy uzylas/uzyles tego skilla w realnej praktyce? Co dziala, co zawodzi?

## Stawka

- [ ] low-stakes (analizy wewnetrzne, draft pomocniczy)
- [ ] mid-stakes (deliverable do klienta wewnetrznego)
- [ ] high-stakes (pismo procesowe, opinia wysokiej wartosci) - **wymaga companion z warstwami walidacji**

## Cokolwiek innego

Cokolwiek waznego, co nie pasuje do powyzszych.
