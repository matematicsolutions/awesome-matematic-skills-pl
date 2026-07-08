# Przykład - tryb audytu

Dwa tryby, jak w bibliotece Sulzer - nie mieszaj.

## Tryb A - audyt roboczego draftu (cytaty to twierdzenia do sprawdzenia)

Wejście: opinia/memo RODO lub projekt skargi do WSA, powołujące decyzje UODO i przepisy RODO.

1. Wyodrębnij powołania, nadaj `claim_type`. Powołania samej decyzji → `powolanie`/`fakt_proceduralny`;
   cytaty z uzasadnienia → `cytat_doslowny`; relacje rozstrzygnięcia → `stanowisko_sadu`.
2. Rozwiąż kotwice na uodo.gov.pl; tekst do cytatów pobierz PDF/Chrome (drabinka). Bez tekstu → ⛔.
3. Uruchom silnik. 🔴/⛔ blokuje, 🟠/🟡 do decyzji.
4. **Checki domenowe poza groundingiem** (`traps.md`): (a) GIODO vs Prezes UODO wg daty decyzji;
   (b) podstawa RODO vs ustawa krajowa; (c) kwota/waluta kary (EUR maksimum vs PLN nałożone);
   (d) czy decyzja nie została uchylona przez WSA/NSA.

Typowe znaleziska: decyzja GIODO sprzed 2018 przypisana „Prezesowi UODO" (🟢 grounding sygnatury,
ale błąd organu - check domenowy); „art. 83 ustawy o ochronie danych osobowych" zamiast „art. 83 RODO"
(błędna podstawa); cytat dosłowny bez pobranego tekstu (⛔).

## Tryb B - audyt finalnej decyzji (decyzja wydana, cytaty są rekordem)

Wejście: gotowa decyzja Prezesa UODO. Zadanie: jak praca zależna (opinia, skarga, artykuł) jej używa.

1. Inwentarz powołań i przypisań.
2. Rozróżnij rozstrzygnięcie Prezesa UODO od twierdzeń strony / fragmentów opisowych.
3. Sprawdź, czy oddano podstawę (które artykuły RODO), kwotę i adresata kary.
4. Łańcuch instancji: czy decyzja prawomocna, czy zaskarżona/uchylona przez WSA/NSA - powołanie samej
   decyzji bez wzmianki o wyroku sądu bywa mylące.

Nie mieszaj trybów: w A cytat to hipoteza do obalenia; w B decyzja jest faktem, a audyt dotyczy
rzetelności jej użycia w dół strumienia.
