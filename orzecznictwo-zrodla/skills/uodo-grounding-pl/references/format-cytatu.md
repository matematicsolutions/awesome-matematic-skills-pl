# Format cytatu - decyzje UODO i RODO

## Decyzja Prezesa UODO

- **Wzór:** `decyzja Prezesa UODO z dnia <data> r., sygn. <sygnatura>`.
  Przykład: `decyzja Prezesa UODO z dnia 30 listopada 2023 r., sygn. DKN.5131.13.2022`.
- Organ: pełna nazwa „Prezes Urzędu Ochrony Danych Osobowych" (silnik rozwija skrót `UODO`).
- **Sygnatury:** `DKN.5131.<nr>.<rok>` (kontrolne/sankcyjne), `DS.<...>` (skargowe),
  `DKE.<...>` (egzekucyjne); starsze GIODO: `ZSPU/ZSPR/...`. Człon środkowy koduje typ.
- **GIODO przed 25.05.2018** - „decyzja Generalnego Inspektora Ochrony Danych Osobowych", inny organ
  i podstawa (patrz `traps.md` pkt 1). Nie pisz „Prezes UODO" dla decyzji sprzed cezury.

## Skarga do sądu administracyjnego

- WSA w Warszawie (I instancja) - wyrok z sygnaturą WSA; NSA (kasacja) - sygnatura NSA. To inne
  dokumenty niż decyzja UODO (`traps.md` pkt 4). Cytuj jako wyrok sądu, nie decyzję UODO.

## Przepisy

- **RODO:** `art. 5 ust. 1 lit. f RODO`, `art. 6 ust. 1 RODO`, `art. 32 RODO`, `art. 33`, `art. 34`,
  `art. 83 ust. 5 RODO` (kary). Pełna nazwa przy pierwszym powołaniu: rozporządzenie (UE) 2016/679.
- **Ustawa krajowa:** `art. <N> ustawy z dnia 10 maja 2018 r. o ochronie danych osobowych`. Nie myl
  z RODO - kary administracyjne są w RODO, nie w ustawie krajowej (`traps.md` pkt 2).

## Co weryfikujemy mechanicznie

- `cytat_doslowny` → string-match w tekście decyzji (FRAGMENT) - wymaga pobranego tekstu/PDF.
- `stanowisko_sadu`/`parafraza` → pokrycie terminów + osąd (TREŚĆ); rozróżnij rozstrzygnięcie
  Prezesa UODO od twierdzeń strony.
- `fakt_proceduralny`/`powolanie` → kotwica `sygnatura` (+ data, organ) przez uodo.gov.pl (ISTNIENIE).
