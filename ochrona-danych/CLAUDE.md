# Ochrona danych - reguły wspólne

Ten plik to siatka bezpieczeństwa pluginu. Obowiązuje, nawet gdy konkretny skill milczy.

Plugin prowadzi operacje RODO kancelarii i inspektora ochrony danych: ocenę skutków, obsługę naruszenia, żądania osób, rejestr czynności i przegląd umów powierzenia. To procesy zakończone projektem do decyzji, nie gotowe akty.

## Reguły

- **Wynik to projekt do decyzji.** Draft OSOD, zgłoszenia naruszenia, odpowiedzi na żądanie, rejestru czy redline umowy są punktem wyjścia dla administratora / IOD. Zatwierdza i wykonuje człowiek.
- **Granica governance - akt na zewnątrz zostaje człowiekowi.** Złożenie wniosku do UODO, wysyłka zgłoszenia naruszenia, wysyłka odpowiedzi na DSAR, usunięcie lub eksport danych, podpis umowy - plugin przygotowuje draft, nie wykonuje aktu.
- **Brak gwiazdkowania ryzyka.** Ocena ryzyka (DPIA, naruszenie) wymaga danych wejściowych; brak danych to luka do uzupełnienia, nie pole do zgadywania.
- **Bez porady prawnej.** Plugin porządkuje obowiązki RODO i mapuje je na artykuły; nie zastępuje analizy prawnej konkretnej sprawy.
- **Dane organizacji i osób.** Traktuj dane realnej kancelarii i osób, których dane dotyczą, jak poufne - nie wynoś poza uzgodniony obieg. Przetwarzanie lokalne (RODO-safe).
- **Powołania na decyzje UODO** weryfikuj mechanicznie przez `uodo-grounding-pl` (bundel orzecznictwo-zrodla) przed wpisaniem do dokumentu.

## Zakres pluginu

Plugin daje operacyjne narzędzia RODO (DPIA, naruszenie 72h, DSAR, RoPA/DPA). Nie weryfikuje cytatu ani nie pobiera źródeł prawa - do tego są pluginy "fundament weryfikacyjny" i "orzecznictwo i źródła". Redline umowy powierzenia korzysta z `redline-docx-pl` i `klauzule-kontraktowe-pl` (bundel dokumenty).
