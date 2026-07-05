# Dokumenty - reguły wspólne

Ten plik to siatka bezpieczeństwa pluginu. Obowiązuje, nawet gdy konkretny skill milczy.

Plugin obsługuje dokumenty: konwersję do Markdown, redlining .docx i anonimizację danych osobowych. Część operacji dotyka danych wrażliwych, więc reguła ochrony danych jest tu pierwsza.

## Ochrona danych

- **Anonimizacja przed wysyłką** - gdy dokument zawiera dane osobowe, oczyść je lokalnie (skill `let-it-be`), zanim treść trafi do modelu. Dane osobowe nie powinny wychodzić do API. To zasada minimalizacji (RODO).
- **Metadane przy wysyłce** - redlining .docx czyści też metadane autora; sprawdź je przed przekazaniem pliku na zewnątrz.
- **Próg poufności** - materiał objęty tajemnicą lub szczególnie wrażliwy oceniaj osobno, czy w ogóle wnosić do narzędzia. Przy wątpliwości nie przekazuj.

## Operacje nieodwracalne

Niektóre operacje są nieodwracalne (anonimizacja w trybie nieodwracalnym, zaakceptowanie wszystkich zmian w .docx). Skille oznaczają je jawnie - wykonuj je dopiero po potwierdzeniu przez człowieka.

## Bramka człowieka

Wynik to projekt. Nic nie zostaje wysłane ani złożone, zanim sprawdzi to uprawniony człowiek. Plugin przygotowuje plik, nie wykonuje aktu wysyłki.

## Zakres pluginu

Plugin daje narzędzia na dokumentach (konwersja, redline, anonimizacja). Nie ocenia treści prawnej ani nie weryfikuje cytatu - tę warstwę daje plugin "fundament weryfikacyjny".
