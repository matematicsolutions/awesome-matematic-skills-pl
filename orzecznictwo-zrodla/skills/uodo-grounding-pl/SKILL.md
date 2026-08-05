---
name: uodo-grounding-pl
description: >
  Mechaniczny weryfikator cytatu dla decyzji Prezesa UODO (ochrona danych osobowych / RODO)
  po polsku, z gradientem weryfikacji ISTNIENIE / TREŚĆ / FRAGMENT. Sprawdza, czy cytat,
  parafraza lub sygnatura decyzji UODO faktycznie istnieje i czy oddaje jej rozstrzygnięcie -
  zamiast wierzyć modelowi "na oko". Krytyczne pułapki domeny: GIODO (przed 25.05.2018) vs
  Prezes UODO (po), RODO (rozporządzenie UE 2016/679) vs krajowa ustawa o ochronie danych
  osobowych, oraz strona uodo.gov.pl wroga botom (drabinka źródeł). RODO-safe (lokalnie).
  Używaj gdy: weryfikacja powołań decyzji UODO w opinii / skardze do WSA / memo RODO przed
  wysłaniem, "sprawdź decyzję UODO", "czy ta sygnatura DKN istnieje", "grounding RODO",
  "czy UODO to nałożyło", "weryfikacja kary RODO", "czy AI zmyśliło decyzję UODO".
license: Apache-2.0
allowed-tools: [Bash, Read, Grep, WebFetch]
data-residency: local
requires-human-approval: false
pii-egress: none
attribution:
  relationship: original
  note: >
    Brak źródła trzeciej strony. Drugi weryfikator domenowy zbudowany z własnego szablonu
    citation-grounding-pl/references/szkielet-weryfikatora-domenowego; silnik współdzielony.
    Dowód generalizacji na domenie bez resolvera w SAOS (decyzje na uodo.gov.pl).
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.0.0
  companion_skills: citation-grounding-pl, eu-sparql-search, saos-orzecznictwo, let-it-be, legal-ai-audit-bundle
  shared_engine: citation-grounding-pl/scripts/ground-citations.mjs
---

# UODO Grounding PL - weryfikator cytatu decyzji Prezesa UODO

## Filozofia

Cytat niezweryfikowany mechanicznie = cytat zmyślony, dopóki nie udowodnisz inaczej. Weryfikacja
mechaniczna (string-match), nie semantyczna. Doktryna gradientu:
`../citation-grounding-pl/references/gradient-weryfikacji.md`. Ten skill **reużywa ten sam silnik**
co `citation-grounding-pl`, dokłada specyfikę ochrony danych.

## Specyfika domeny - czym różni się od KIO

- **Brak resolvera w SAOS.** Decyzje Prezesa UODO publikuje **uodo.gov.pl** (`/decyzje/<sygnatura>`),
  nie SAOS (w SAOS są dopiero wyroki WSA/NSA ze skarg - i to ubogo). To dowód, że szablon działa
  poza SAOS: resolver kotwicy to WebFetch/byob na uodo.gov.pl + ewentualny PDF decyzji.
- **Strona uodo.gov.pl jest WROGA BOTOM** - `/decyzje/` zwraca 500 dla curl, treść renderowana JS,
  TLS bywa niespójny. Dlatego **drabinka źródeł jest tu centralna** (`references/drabinka-zrodel.md`):
  często tekst decyzji dostępny tylko jako PDF / przez realny Chrome / od użytkownika.
- **Sygnatura:** `DKN.5131.<nr>.<rok>` (postępowania kontrolne/sankcyjne), `DS.<...>` (skargowe),
  `DKE.<...>` (egzekucyjne). Człon środkowy koduje typ postępowania. Format: `references/format-cytatu.md`.
- **PUŁAPKI: czytaj `references/traps.md` PRZED weryfikacją.** Najważniejsze: GIODO vs Prezes UODO
  (cezura 25.05.2018) oraz RODO (UE) vs krajowa ustawa o ochronie danych osobowych.

## Workflow

1. **Rozwiąż kotwicę** - potwierdź sygnaturę/datę/organ na uodo.gov.pl (lista decyzji / strona
   decyzji). Zbuduj `anchor_resolved` (`organ` = "Prezes Urzędu Ochrony Danych Osobowych"; silnik
   rozwija skrót `UODO`). Tekst do TREŚĆ/FRAGMENT: pobierz PDF/HTML - przy awarii drabinka.
2. **Sklasyfikuj twierdzenia** `claim_type` (`../citation-grounding-pl/references/gradient-weryfikacji.md`).
3. **Sprawdź pułapki** z `references/traps.md` (zwłaszcza GIODO/UODO i RODO/ustawa krajowa).
4. **Weryfikacja mechaniczna** współdzielonym silnikiem:
   ```bash
   node ../citation-grounding-pl/scripts/ground-citations.mjs <zadanie.json>
   ```
5. **Klasyfikuj:** 🟢 ZWERYFIKOWANY / 🟡 ZMODYFIKOWANY / 🟡 WYMAGA_OSADU / 🟠 KALIBRACJA / 🔴 NIEZWERYFIKOWANY / ⛔ BRAK ŹRÓDŁA.
6. **Raport:** 🔴/⛔ blokada; 🟠/🟡 decyzja człowieka. Bez tekstu decyzji cytat dosłowny = ⛔ BRAK
   ŹRÓDŁA (NIE „prawdopodobnie ok") - to częsty przypadek przy UODO, patrz przykład.

Przykłady na realnych sygnaturach: `examples/przyklad-weryfikacja.md`, `examples/przyklad-audyt.md`.

## Twarde reguły

1. Brak cytatu/parafrazy/sygnatury UODO z pamięci - weryfikuj wobec uodo.gov.pl.
2. Output nie twierdzi mocniej, niż sięga weryfikacja (kalibracja).
3. **GIODO ≠ Prezes UODO.** Decyzje sprzed 25.05.2018 wydawał Generalny Inspektor Ochrony Danych
   Osobowych (GIODO) na podstawie ustawy z 1997 r. Po 25.05.2018 - Prezes UODO na podstawie RODO +
   ustawy z 10.05.2018. Nie przypisuj decyzji GIODO „Prezesowi UODO" ani odwrotnie. Patrz `traps.md`.
4. **RODO ≠ krajowa ustawa.** RODO = rozporządzenie UE 2016/679 (art. 5, 6, 32, 33, 83…). Ustawa o
   ochronie danych osobowych z 10 maja 2018 r. to akt KRAJOWY uzupełniający. Nie myl podstawy prawnej.
5. **Dane osobowe = tajemnica.** Materiały sprawy pseudonimizuj przez `let-it-be` PRZED weryfikacją.
6. Awaria fetcha uodo.gov.pl = pracuj drabinkę (PDF / Chrome / user), nie porzucaj realnej decyzji.

## Czym ten skill NIE jest

- Nie porada prawna - narzędzie badawcze/redakcyjne dla osób znających prawo ochrony danych.
- Nie zastępuje pełnego tekstu decyzji ani analizy stanu prawnego (RODO/ustawa, GIODO/UODO).

## Atrybucja

Silnik i gradient: `citation-grounding-pl` (MateMatic). Idea gradientu Existence/Content/Paragraph:
Jeanne Sulzer / Impact Litigation Lab (CC BY 4.0). Pułapki domenowe, format sygnatur DKN i drabinka
napisane pod decyzje Prezesa UODO / RODO od zera.
