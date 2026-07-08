# Przykład - weryfikacja end-to-end (realne sygnatury UODO)

Sygnatury autentyczne (potwierdzone na uodo.gov.pl / przez WebSearch): **DKN.5131.29.2023**
(kara 238 345 zł na Res-Gastro M. Gaweł sp.k., Kolbuszowa) oraz **DKN.5131.13.2022** (decyzja
z 30 listopada 2023 r. - niewdrożenie odpowiednich środków technicznych i organizacyjnych).

## Krok 1 - rozwiąż kotwicę

Sygnaturę/datę/organ potwierdzasz na uodo.gov.pl (lista decyzji lub strona-streszczenie). Serwis
jest wrogi botom (500/JS) - dlatego ISTNIENIE potwierdzasz z listingu/streszczenia, a pełny tekst
do FRAGMENT wymaga PDF/Chrome/użytkownika (`references/drabinka-zrodel.md`). `anchor_resolved.organ`
= "Prezes Urzędu Ochrony Danych Osobowych" (silnik rozwija `UODO`).

## Krok 2-4 - zadanie i weryfikacja współdzielonym silnikiem

```bash
node ../citation-grounding-pl/scripts/ground-citations.mjs zadanie-uodo.json
```

```json
{
  "items": [
    { "id": "U1-fakt-kara", "source_id": "DKN.5131.29.2023", "claim_type": "fakt_proceduralny",
      "anchor":          { "sygnatura": "DKN.5131.29.2023", "organ": "Prezes UODO" },
      "anchor_resolved": { "sygnatura": "DKN.5131.29.2023", "organ": "Prezes Urzędu Ochrony Danych Osobowych" } },
    { "id": "U2-powolanie", "source_id": "DKN.5131.13.2022", "claim_type": "powolanie",
      "anchor":          { "sygnatura": "DKN.5131.13.2022", "data": "30.11.2023", "organ": "Prezes UODO" },
      "anchor_resolved": { "sygnatura": "DKN.5131.13.2022", "data": "2023-11-30", "organ": "Prezes Urzędu Ochrony Danych Osobowych" } },
    { "id": "U3-cytat-bez-tekstu", "source_id": "DKN.5131.29.2023", "claim_type": "cytat_doslowny",
      "quote": "administrator nie wdrożył odpowiednich środków technicznych i organizacyjnych" },
    { "id": "U4-halucynacja-sygn", "source_id": "DKN.9999.99.2099", "claim_type": "fakt_proceduralny",
      "anchor":          { "sygnatura": "DKN.9999.99.2099", "organ": "Prezes UODO" },
      "anchor_resolved": { "sygnatura": "DKN.5131.29.2023", "organ": "Prezes Urzędu Ochrony Danych Osobowych" } }
  ]
}
```

## Wynik (faktyczny output silnika)

| ID | Typ | Wym.→Osiąg. | Status | Uwaga |
|----|-----|-------------|--------|-------|
| U1-fakt-kara | fakt_proceduralny | ISTNIENIE→ISTNIENIE | 🟢 ZWERYFIKOWANY | kotwica OK (`Prezes UODO`=`Prezes Urzędu Ochrony Danych Osobowych`) |
| U2-powolanie | powolanie | ISTNIENIE→ISTNIENIE | 🟢 ZWERYFIKOWANY | sygnatura + data potwierdzone |
| U3-cytat-bez-tekstu | cytat_doslowny | FRAGMENT→BRAK | ⛔ BRAK ŹRÓDŁA | brak pobranego tekstu decyzji - pobierz PDF, nie zgaduj |
| U4-halucynacja-sygn | fakt_proceduralny | ISTNIENIE→BRAK | 🔴 NIEZWERYFIKOWANY | rozbieżność sygnatury (DKN.9999… vs DKN.5131.29.2023) - falszerstwo |

`blokada: true` (U3, U4). Exit 1.

**Lekcja domenowa:** U3 to typowy przypadek UODO - mamy realną decyzję, ale bez pobranego tekstu
NIE da się zweryfikować cytatu dosłownego. Status ⛔, nie „prawdopodobnie ok". To NIE porażka -
to uczciwy stan: zejdź po drabince (PDF/Chrome/user) albo złagodź do `powolanie` (ISTNIENIE).
U4 pokazuje, że tożsamość niesie sygnatura: zmyślony numer DKN łapie się nawet przy poprawnym organie.
