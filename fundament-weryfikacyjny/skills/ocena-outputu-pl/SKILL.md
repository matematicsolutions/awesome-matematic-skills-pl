---
name: ocena-outputu-pl
description: >
  Ocenia jakość outputu prawnego AI przed wysyłką w dwóch warstwach: obiektywnej
  (sprawdzalne mechanicznie - czy cytaty istnieją, czy przepisy i sygnatury realne)
  oraz subiektywnej (LLM-as-judge wg rubryki 1-5: poprawność prawna, kompletność,
  jasność, zgodność z jurysdykcją, ugruntowanie/anty-halucynacja). Zwraca kartę ocen
  i decyzję: wyślij / popraw / pełna weryfikacja. Warstwa nad deliverable - nie pisze
  pisma, ocenia gotowe. Pairuje z legal-request-router-pl (routing), citation-grounding-pl
  (obiektywne sprawdzenie), deliverable-fidelity-pl (czy nic nie wypadlo) i
  adversarial-legal-review-pl (atak). Uzywaj gdy: "oceń ten output", "scoring opinii",
  "czy to gotowe do wysyłki", "jakość odpowiedzi prawnej", "karta ocen deliverable",
  "rubryka jakości", przed wysłaniem pisma/opinii/memo do klienta.
license: Apache-2.0
allowed-tools: [Read]
data-residency: local
requires-human-approval: false
pii-egress: none
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.0.0
  inspiration: >
    Metoda dwuwarstwowa (obiektywne dopasowanie + subiektywna rubryka LLM-as-judge,
    skala 1-5) oparta na DISC-Law-Eval z DISC-LawLLM (Fudan DISC Lab), licencja
    Apache-2.0 (https://github.com/FudanDISC/DISC-LawLLM). Chińskie dane egzaminacyjne
    i model-sędzia porzucone; rubryka, wymiary i kotwice PL napisane od zera.
  companion_skills: legal-request-router-pl, citation-grounding-pl, deliverable-fidelity-pl, adversarial-legal-review-pl
---

# Ocena outputu PL - karta ocen przed wysyłką

## Filozofia

**Zanim wyślesz, oceń - i oddziel to, co sprawdzalne, od tego, co trzeba osądzić.** Output AI bywa
gładki i przekonujący, a mimo to błędny. Ten skill ocenia go w dwóch warstwach: obiektywnej
(fakty, które da się sprawdzić mechanicznie) i subiektywnej (jakość, którą trzeba osądzić wg jawnej
rubryki). Dwie warstwy, bo mylenie ich to źródło fałszywej pewności - „brzmi dobrze" nie znaczy
„cytaty się zgadzają".

Skill **ocenia**, nie poprawia i nie wysyła. Decyzję podejmuje prawnik; karta ocen daje podstawę.

## Warstwa 1 - obiektywna (sprawdzalne mechanicznie)

Deleguj do narzędzi, nie zgaduj:
- **Cytaty i przepisy** - czy istnieją w źródle słowo w słowo (citation-grounding-pl), czy wszystkie
  wyłapane (ekstraktor-cytatow-pl).
- **Sygnatury / ELI** - czy realne i poprawnie zapisane.
- **Kompletność ustaleń** - czy żadna flaga RED nie wypadła z podsumowania (deliverable-fidelity-pl).

Wynik obiektywny jest binarny per pozycja: zgadza się / nie zgadza. Choćby jeden niezgodny cytat =
output nie jest gotowy, niezależnie od oceny subiektywnej.

## Warstwa 2 - subiektywna (rubryka 1-5, LLM-as-judge)

Oceń wg jawnej rubryki, każdy wymiar 1-5 z jednozdaniowym uzasadnieniem:

| Wymiar | 1 | 5 |
|---|---|---|
| Poprawność prawna | teza błędna lub nieoparta | teza trafna i oparta na normie |
| Kompletność | pomija istotne kwestie | obejmuje wszystko, co istotne dla pytania |
| Jasność | mętne, niespójne | precyzyjne, czytelne dla odbiorcy |
| Zgodność z jurysdykcją | myli porządki/przepisy | trafne dla prawa polskiego/UE |
| Ugruntowanie (anty-halucynacja) | twierdzenia bez podstawy | każde twierdzenie ma oparcie |

## Decyzja

- **Wyślij** - warstwa 1 czysta i średnia subiektywna ≥ 4, żaden wymiar < 3.
- **Popraw** - warstwa 1 czysta, ale któryś wymiar subiektywny 2-3 (wskaż który).
- **Pełna weryfikacja** - warstwa 1 ma niezgodność albo wymiar = 1 -> skieruj do
  legal-request-router-pl (grounding / adversarial / paczka audytowa).

## Format wyjścia

```
WARSTWA 1 (obiektywna): cytaty OK/X | przepisy OK/X | sygnatury OK/X | kompletność OK/X
WARSTWA 2 (rubryka 1-5):
  Poprawność prawna: 4 - <uzasadnienie>
  Kompletność: 3 - <...>
  Jasność: 5 - <...>
  Zgodność z jurysdykcją: 4 - <...>
  Ugruntowanie: 4 - <...>
  Średnia: 4.0
DECYZJA: Popraw (Kompletność 3 - brak omówienia przedawnienia)
```

## Granice

- Ocena subiektywna to osąd modelu wg rubryki, nie wyrocznia - przy wysokiej stawce ostateczna
  ocena należy do prawnika, a karta jest dowodem należytej staranności (do legal-ai-audit-bundle).
- Warstwa 1 nie zastępuje narzędzi, które wywołuje - jest ich agregatorem do jednej decyzji.
- Skill ocenia output, nie tworzy go i nie poprawia.

## Atrybucja

Metoda dwuwarstwowa (obiektywne dopasowanie + subiektywna rubryka LLM-as-judge w skali 1-5) oparta na
**DISC-Law-Eval** z projektu DISC-LawLLM (Fudan DISC Lab), licencja **Apache-2.0**. Chińskie dane
egzaminacyjne i model-sędzia porzucone; wymiary rubryki, progi decyzji i kotwice PL to oryginalne
opracowanie MateMatic. Interpretacja MateMatic, nie stanowisko NRA ani KRRP.
