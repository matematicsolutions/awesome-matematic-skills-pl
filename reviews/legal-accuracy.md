# Rejestr weryfikacji merytorycznej (legal-accuracy)

Sprawdzany mechanicznie przez `scripts/legal-accuracy-gate.py`: kazda jednostka
redakcyjna z ZMIENIONYCH linii SKILL.md musi byc pokryta wpisem w sekcji
`## <nazwa-skilla>` ponizej. Pokrycie to czesc mechaniczna; werdykt w wierszu
to warstwa osadu (adversarial review) i musi odzwierciedlac sprawdzenie
faktycznie wykonane wobec tekstu zrodla, nie z pamieci.

Format wpisu: `- <jednostka> - <werdykt> - <jak sprawdzono>`

## rodo-dsar-pl

Przeglad 2026-08-07 (backport flag codex z PR #16 mike-workflows).

- art. 12 ust. 6 - ok - podstawa weryfikacji tozsamosci; tekst RODO pozwala zadac dodatkowych informacji, nie przewiduje bezwarunkowego zawieszenia terminu.
- Wytycznych EROD 01/2022 - ok - zweryfikowane u zrodla EROD 2026-08-07: zawieszenie tylko gdy informacja niezbedna ORAZ zazadana bez zbednej zwloki; wytyczne przyjete 18.01.2022.
- art. 12 ust. 1 - ok - wymog prostego jezyka odpowiedzi; teza niezmieniona, ponownie odczytana z tekstu.
- art. 15 - ok - prawo dostepu obejmuje kopie danych przetwarzanych (art. 15 ust. 3); metadane z RCP nie sa kopia danych.
- art. 15 ust. 1 lit. g - ok - "wszelkie dostepne informacje o ich zrodle" gdy dane nie od osoby - stad "dostepne informacje o zrodle", nie bezwarunkowa lista zrodel.

## rodo-ropa-dpa-pl

Przeglad 2026-08-07 (backport flag codex z PR #16 mike-workflows).

- art. 30 ust. 2 - ok - zakres rejestru procesora; lista pol przepisana na pelne wyliczenie ustawowe (lit. a-d).
- art. 30 ust. 5 - ok - test zwolnienia; kazda przeslanka niezalezna (sporadycznosc, ryzyko, art. 9 ust. 1, art. 10).
- art. 9 ust. 1 - ok - szczegolne kategorie jako jedna z przeslanek wylaczajacych 30 ust. 5.
- art. 10 - ok - dane o wyrokach skazujacych i czynach zabronionych; osobna przeslanka wylaczajaca, wczesniej pominieta - flaga codex, ktora uruchomila ten rejestr.

## klauzule-kontraktowe-pl

Przeglad 2026-08-07 (backport flag codex z PR #16 mike-workflows).

- art. 483 - ok - kara umowna tylko za zobowiazanie niepieniezne (art. 483 § 1 KC); wiersz przykladowy tabeli, kotwica niezmieniona, ponownie odczytana z KC.
