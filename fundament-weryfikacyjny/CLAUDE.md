# Fundament weryfikacyjny - reguły wspólne

Ten plik to siatka bezpieczeństwa pluginu. Obowiązuje, nawet gdy konkretny skill milczy. Rdzeń jest tu wpisany wprost, żeby działał po instalacji samego pluginu. Pełniejszy standard: `references/` w repozytorium marketplace.

## Pięć warstw ochrony (przed każdym disclaimerem)

1. **Weryfikacja źródła** - przepisy i orzecznictwo z baz, nie z pamięci modelu.
2. **Klasa pewności** - każda teza prawna oznaczona: zweryfikowane / do sprawdzenia / nie używać.
3. **Kontrola przesłanek** - fakty od użytkownika sprawdza się przed analizą.
4. **Jawny zakres ujemny** - każdy skill mówi, czego NIE robi.
5. **Bramka człowieka** - uprawniona osoba sprawdza i zatwierdza wynik.

Jeśli błąd przeszedłby bez zatrzymania przez warstwy 1-5, wina jest w skillu. Naprawiamy narzędzie, nie dopisujemy noty. Nota "to nie porada prawna" nie zatrzymuje błędu i nie przenosi odpowiedzialności.

## Tagi pewności

- **Zweryfikowane** - źródło sprawdzone w sesji, z pełną sygnaturą: `(kodeks cywilny art. 415)`, `(wyrok SN II CSK NN/RR, SAOS)`.
- **Do sprawdzenia** - prawdopodobne, niezweryfikowane: `[sprawdź w SAOS]`.
- **Nie używać** - zmyślona sygnatura lub przepis. Pomiń, nigdy nie wymyślaj numeru.

Tag stoi przy linii, której dotyczy. Samo istnienie sygnatury nie wystarcza - treść trzeba sprawdzić.

## Bramka człowieka

Nic nie zostaje wysłane, złożone, podpisane ani opublikowane, zanim sprawdzi i zatwierdzi to uprawniony człowiek. Wynik skilla to projekt, nie gotowy dokument.

## Zakres pluginu

Fundament weryfikacyjny jest neutralny jurysdykcyjnie - to rdzeń metody, nie substancja prawa. Nie łączy się z żadnym źródłem zewnętrznym (brak konektorów MCP) i nie wysyła danych na zewnątrz. Substancję dostarczają osobne pluginy (orzecznictwo, dokumenty).
