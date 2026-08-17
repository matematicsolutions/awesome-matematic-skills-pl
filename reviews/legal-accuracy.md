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


## matematic-patron-pr-review-pl

Przeglad 2026-08-08 (skrocenie description pod limit 1024 rejestru Smithery Skills; jednostka w zmienionej linii bez zmiany tresci).

- art. 12 - ok - AI Act (rozp. UE 2024/1689) art. 12 "Rejestrowanie zdarzen": systemy AI wysokiego ryzyka musza automatycznie rejestrowac zdarzenia w calym cyklu zycia; etykieta "record-keeping" w description poprawna. Zweryfikowane u zrodla EUR-Lex CELEX:32024R1689 (PL) 2026-08-08.
## adversarial-legal-review-pl

Przeglad 2026-08-17 (v1.3.0 - port mechanizmow z bliznika EN: petla rewizji z cofnieciem po regresji, poziomy dostepu recenzentow, stany koncowe).

- art. 12 - ok - AI Act (2024/1689) art. 12 ust. 1: "High-risk AI systems shall technically allow for the automatic recording of events (logs) over the lifetime of the system"; ust. 2 wiaze logi z identyfikowalnoscia dzialania. Teza skilla: transkrypt wszystkich wersji v1..vN jako dowod ograniczonej rewizji i ewentualnego cofniecia. Zgodne. Zweryfikowane u zrodla: EUR-Lex CELEX:32024R1689 (HTML skonsolidowany), 2026-08-17.
- art. 14 - ok - art. 14 ust. 1: system ma byc zaprojektowany tak, "that they can be effectively overseen by natural persons during the period in which they are in use". Teza skilla: decyzja "wyslac mimo wymuszonego wyjscia z blokerami" zostaje przy czlowieku, skill nie wysyla. Zgodne. To samo zrodlo, ta sama data.
