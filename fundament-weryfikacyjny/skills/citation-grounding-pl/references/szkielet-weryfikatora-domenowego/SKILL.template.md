---
name: <domena>-grounding-pl
description: >
  Mechaniczny weryfikator cytatu dla <DOMENA PRAWNA> po polsku z gradientem
  weryfikacji (ISTNIENIE / TREŚĆ / FRAGMENT). Sprawdza, czy cytat/parafraza/sygnatura
  z <typ źródła: orzeczenia KIO / decyzji UODO / aktu / ...> faktycznie istnieje
  i czy oddaje stanowisko organu. Przeciwdziała halucynacjom, RODO-safe (lokalnie).
  Używaj gdy: weryfikacja powołań w <typ deliverable> przed wysłaniem, "<trigger 1>",
  "<trigger 2>", "grounding <domena>", "czy AI to zmyśliło".
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.0.0
  inspiration: >
    Gradient i kalibracja - citation-grounding-pl (MateMatic) / Existence-Content-Paragraph
    Jeanne Sulzer (CC BY 4.0). Silnik współdzielony z citation-grounding-pl.
  companion_skills: <resolver-kotwicy np. saos-orzecznictwo / eu-sparql-search>, legal-ai-audit-bundle
  shared_engine: citation-grounding-pl/scripts/ground-citations.mjs
---

# <Domena> Grounding PL - weryfikator cytatu (gradient)

## Filozofia

Cytat niezweryfikowany mechanicznie = cytat zmyślony, dopóki nie udowodnisz inaczej. Weryfikacja
jest mechaniczna, nie semantyczna - string-match znormalizowanego cytatu wobec źródła. Pełna
doktryna gradientu: `../citation-grounding-pl/references/gradient-weryfikacji.md`.

## Specyfika domeny <domena>

- **Źródło autorytatywne:** <np. baza orzeczeń KIO na uzp.gov.pl / decyzje UODO>
- **Resolver kotwicy (ISTNIENIE):** <companion_skill + jak buduje anchor_resolved>
- **Jednostka cytowania:** <sygnatura/numer decyzji - format>
- **Pułapki domenowe:** patrz `references/traps.md` (CZYTAJ przed weryfikacją)

## Workflow

1. **Zbierz źródła i rozwiąż kotwice** przez <resolver>; przy awarii pracuj `references/drabinka-zrodel.md`.
2. **Sklasyfikuj każde twierdzenie** `claim_type` (macierz: `../citation-grounding-pl/references/gradient-weryfikacji.md`).
3. **Sprawdź pułapki domenowe** z `references/traps.md`.
4. **Weryfikacja mechaniczna:**
   ```bash
   node ../citation-grounding-pl/scripts/ground-citations.mjs <zadanie.json>
   ```
5. **Klasyfikuj** (🟢 ZWERYFIKOWANY / 🟡 ZMODYFIKOWANY / 🟡 WYMAGA_OSADU / 🟠 KALIBRACJA / 🔴 NIEZWERYFIKOWANY / ⛔ BRAK ŹRÓDŁA).
6. **Raport** - 🔴/⛔ blokada, 🟠/🟡 decyzja człowieka. Nigdy nie przepuszczaj 🔴 milcząco.

## Twarde reguły

1. Brak cytatu/parafrazy z pamięci - weryfikuj w rozmowie wobec <źródła autorytatywnego>.
2. Output nie twierdzi mocniej, niż sięga weryfikacja (kalibracja).
3. <reguła domenowa 1 - np. wersja językowa / stan prawny na datę / wersja redakcyjna>.
4. Materiały objęte tajemnicą: pseudonimizuj przez `let-it-be` przed weryfikacją.
5. Awaria bezpośredniego fetcha = pracuj drabinkę, nie porzucaj realnego cytatu.

## Atrybucja

Silnik i gradient: `citation-grounding-pl` (MateMatic). Idea gradientu Existence/Content/Paragraph:
Jeanne Sulzer / Impact Litigation Lab (CC BY 4.0). Pułapki domenowe i drabinka napisane pod <domena>.
