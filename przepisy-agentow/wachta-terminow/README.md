# wachta-terminow - druga para oczu na terminy w aktach

Agent tła, który skanuje wskazane akta sprawy pod kątem zdarzeń uruchamiających
terminy (doręczenie wyroku → apelacja, wezwanie → odpowiedź, naruszenie → zgłoszenie
RODO 72h) i produkuje **listę terminów-kandydatów do sprawdzenia** przez osobę
odpowiedzialną za kalendarz.

## Jak to działa (3 poziomy, patrz ../README.md)

1. **czytelnik-akt** (Read/Grep, bez sieci) wyciąga z dokumentów zdarzenia + daty + źródło.
2. **licznik-terminow** (opcjonalnie MCP read-only) dokłada podstawę prawną i datę-kandydata
   z tagiem `[wyliczenie modelu - sprawdź]`. Podstawy z tabel skilla `terminy-procesowe-pl`
   albo ze źródła (ISAP) - nie z pamięci.
3. **redaktor-alertow** (jedyny Write) składa tabelę alertu z nagłówkiem „projekt do sprawdzenia".

## Czego ten przepis NIE robi

- **NIE zastępuje systemu terminowego kancelarii.** Uchybienie terminu to szkoda
  majątkowa i dyscyplinarka - żaden LLM nie może być jedynym mechanizmem pilnowania.
- **NIE potwierdza dat.** Data-kandydat = poszlaka; liczenie terminu (dni robocze,
  doręczenie zastępcze, przerwanie biegu) weryfikuje człowiek z aktami.
- **NIE czyta całego repozytorium spraw.** Dostaje jawnie wskazany zakres akt.

## Dopasowanie (minimum przed pierwszym uruchomieniem)

- źródło akt (katalog / DMS) + zakres,
- rytm (np. codziennie 07:00) i kanał alertu (plik / mail przez człowieka),
- typy pilnowanych terminów w konfiguracji licznika,
- pseudonimizacja: akta z danymi klienta przechodzą `let-it-be` PRZED czytelnikiem,
- ewaluacja na fixture'ach zanim zaufasz (kryteria behawioralne: podnosi zdarzenie,
  taguje wyliczenie, nie potwierdza terminu z pamięci).
