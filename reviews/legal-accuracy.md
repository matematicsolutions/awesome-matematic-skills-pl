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

Przeglad 2026-10-10 (przejscie gotowosci: wszystkie jednostki redakcyjne skilla i skryptu, pelny mianownik, sprawdzone wobec tekstu zrodla; wady poprawione w tym samym przejsciu; blizniak gdpr-*-en sprawdzony tego samego dnia).

- art. 12 ust. 3 - POPRAWIONE, potem ok - tekst: "bez zbednej zwloki - a w kazdym razie w terminie miesiaca od otrzymania zadania"; przedluzenie "o kolejne dwa miesiace z uwagi na skomplikowany charakter zadania lub liczbe zadan", informacja w terminie miesiaca "z podaniem przyczyn opoznienia". Skill pisal "1 miesiac" bez "bez zbednej zwloki", opis frontmattera "przy zlozonosci" bez liczby zadan; oba uzupelnione. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 12 ust. 4 - POPRAWIONE, potem ok - przy niepodjeciu dzialan administrator "niezwlocznie - najpozniej w terminie miesiaca od otrzymania zadania" informuje o powodach, skardze i srodkach ochrony prawnej przed sadem. Skill mial tresc, bez terminu; dodany. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 12 ust. 5 - POPRAWIONE, potem ok - ustawowe brzmienie to "ewidentnie nieuzasadnione lub nadmierne, w szczegolnosci ze wzgledu na swoj ustawiczny charakter"; skill pisal "ewidentnie bezzasadne" - zmienione na brzmienie przepisu, dodane "rozsadna oplata" i "obowiazek wykazania spoczywa na administratorze". EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 17 ust. 3 - POPRAWIONE, potem ok - piec wylaczen: a) wolnosc wypowiedzi i informacji, b) obowiazek prawny / zadanie w interesie publicznym / wladza publiczna, c) zdrowie publiczne (art. 9 ust. 2 lit. h i i oraz ust. 3), d) cele archiwalne, badania naukowe lub historyczne, statystyka (art. 89 ust. 1), e) roszczenia. Tabela wymieniala trzy, czytane jako komplet; teraz piec. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 3 ust. 4 - ok (nazwane ograniczenie) - rozporzadzenie 1182/71: termin wyrazony inaczej niz w godzinach, ktorego ostatni dzien to swieto, niedziela lub sobota, konczy sie z uplywem ostatniej godziny nastepnego dnia roboczego. Skrypt tego nie stosuje; skill i skrypt to mowia i ze wynik moze byc tylko wczesniejszy od terminu prawnego. EUR-Lex CELEX:31971R1182 (HTML pobrany 2026-10-10, komplet 6 artykulow).

## rodo-ropa-dpa-pl

Przeglad 2026-08-07 (backport flag codex z PR #16 mike-workflows).

- art. 30 ust. 2 - ok - zakres rejestru procesora; lista pol przepisana na pelne wyliczenie ustawowe (lit. a-d).
- art. 30 ust. 5 - ok - test zwolnienia; kazda przeslanka niezalezna (sporadycznosc, ryzyko, art. 9 ust. 1, art. 10).
- art. 9 ust. 1 - ok - szczegolne kategorie jako jedna z przeslanek wylaczajacych 30 ust. 5.
- art. 10 - ok - dane o wyrokach skazujacych i czynach zabronionych; osobna przeslanka wylaczajaca, wczesniej pominieta - flaga codex, ktora uruchomila ten rejestr.

Przeglad 2026-10-10 (przejscie gotowosci: wszystkie jednostki redakcyjne skilla i skryptu, pelny mianownik, sprawdzone wobec tekstu zrodla; wady poprawione w tym samym przejsciu; blizniak gdpr-*-en sprawdzony tego samego dnia).

- art. 30 ust. 1 - POPRAWIONE, potem ok - rejestr zawiera "wszystkie nastepujace informacje" lit. a-g, ale lit. e "gdy ma to zastosowanie", a lit. f i g "jezeli jest to mozliwe". Skill nazywal wszystkie siedem bezwarunkowymi "polami obowiazkowymi"; teraz kazda niesie swoj warunek. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 30 ust. 1 lit. a-g - POPRAWIONE, potem ok - lit. a: imie i nazwisko lub nazwa oraz dane kontaktowe administratora i wszelkich wspoladministratorow, a gdy ma to zastosowanie - przedstawiciela administratora oraz IOD; brakowalo przedstawiciela. Lit. e: nazwa panstwa trzeciego lub organizacji i dokumentacja zabezpieczen przy przekazaniach z art. 49 ust. 1 akapit drugi. Pozostale litery zgodne. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 49 ust. 1 - ok - powolany wylacznie jako przypadek z art. 30 ust. 1 lit. e (akapit drugi). EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 32 - ok - bezpieczenstwo przetwarzania; tresc art. 28 ust. 3 lit. c ("podejmuje wszelkie srodki wymagane na mocy art. 32") i lit. f (art. 32-36). EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 32 ust. 1 - ok - art. 30 ust. 1 lit. g odsyla do "srodkow bezpieczenstwa, o ktorych mowa w art. 32 ust. 1"; skill cytuje teraz ust. 1. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 28 - ok - umowa bez wymaganych postanowien nie spelnia art. 28 ust. 3. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 28 ust. 3 - POPRAWIONE, potem ok - zdanie pierwsze: przedmiot i czas trwania, charakter i cel, rodzaj danych, kategorie osob "obowiazki i prawa administratora" - ostatniego elementu brakowalo (skill i notka skryptu); dodany. Akapit drugi: procesor "niezwlocznie informuje administratora, jezeli jego zdaniem wydane mu polecenie stanowi naruszenie" - dodane przy lit. h. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 28 ust. 3 lit. a-h - POPRAWIONE, potem ok - lit. a: wyjatek "chyba ze obowiazek taki naklada na niego prawo Unii lub prawo panstwa czlonkowskiego" z obowiazkiem uprzedzenia administratora "o ile prawo to nie zabrania" - dodany; lit. g: "zaleznie od decyzji administratora usuwa lub zwraca mu wszelkie dane osobowe oraz usuwa wszelkie ich istniejace kopie, chyba ze prawo ... nakazuja przechowywanie" - dodane. Lit. b-f i h zgodne. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).

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
- art. 415 - ok - wystepuje tylko jako przyklad formatu tagu Zweryfikowane, `(kodeks cywilny art. 415)`, we wspolnych regulach wtyczki fundament-weryfikacyjny (SHARED-RULES.md, skopiowane do kazdego skilla 2026-10-06). Sprawdzone u zrodla 2026-10-06 w Repertorium (verify_citations): eli:DU/1964/93, "Ustawa z dnia 23 kwietnia 1964 r. - Kodeks cywilny", art. 415, status no_known_changes_after_date, snapshot pl-2026-08. Przyklad nie przypisuje przepisowi zadnej tresci poza jego istnieniem i numerem.

## atak-przeciwnika-pl

Przeglad 2026-10-06 (dodany blok wspolnych regul wtyczki).

- art. 415 - ok - wystepuje tylko jako przyklad formatu tagu Zweryfikowane, `(kodeks cywilny art. 415)`, we wspolnych regulach wtyczki fundament-weryfikacyjny (SHARED-RULES.md, skopiowane do kazdego skilla 2026-10-06). Sprawdzone u zrodla 2026-10-06 w Repertorium (verify_citations): eli:DU/1964/93, "Ustawa z dnia 23 kwietnia 1964 r. - Kodeks cywilny", art. 415, status no_known_changes_after_date, snapshot pl-2026-08. Przyklad nie przypisuje przepisowi zadnej tresci poza jego istnieniem i numerem.

## citation-grounding-pl

Przeglad 2026-10-06 (dodany blok wspolnych regul wtyczki).

- art. 415 - ok - wystepuje tylko jako przyklad formatu tagu Zweryfikowane, `(kodeks cywilny art. 415)`, we wspolnych regulach wtyczki fundament-weryfikacyjny (SHARED-RULES.md, skopiowane do kazdego skilla 2026-10-06). Sprawdzone u zrodla 2026-10-06 w Repertorium (verify_citations): eli:DU/1964/93, "Ustawa z dnia 23 kwietnia 1964 r. - Kodeks cywilny", art. 415, status no_known_changes_after_date, snapshot pl-2026-08. Przyklad nie przypisuje przepisowi zadnej tresci poza jego istnieniem i numerem.

## deliverable-fidelity-pl

Przeglad 2026-10-06 (dodany blok wspolnych regul wtyczki).

- art. 415 - ok - wystepuje tylko jako przyklad formatu tagu Zweryfikowane, `(kodeks cywilny art. 415)`, we wspolnych regulach wtyczki fundament-weryfikacyjny (SHARED-RULES.md, skopiowane do kazdego skilla 2026-10-06). Sprawdzone u zrodla 2026-10-06 w Repertorium (verify_citations): eli:DU/1964/93, "Ustawa z dnia 23 kwietnia 1964 r. - Kodeks cywilny", art. 415, status no_known_changes_after_date, snapshot pl-2026-08. Przyklad nie przypisuje przepisowi zadnej tresci poza jego istnieniem i numerem.

## ekstraktor-cytatow-pl

Przeglad 2026-10-06 (dodany blok wspolnych regul wtyczki).

- art. 415 - ok - wystepuje tylko jako przyklad formatu tagu Zweryfikowane, `(kodeks cywilny art. 415)`, we wspolnych regulach wtyczki fundament-weryfikacyjny (SHARED-RULES.md, skopiowane do kazdego skilla 2026-10-06). Sprawdzone u zrodla 2026-10-06 w Repertorium (verify_citations): eli:DU/1964/93, "Ustawa z dnia 23 kwietnia 1964 r. - Kodeks cywilny", art. 415, status no_known_changes_after_date, snapshot pl-2026-08. Przyklad nie przypisuje przepisowi zadnej tresci poza jego istnieniem i numerem.

## intake-sufficiency-pl

Przeglad 2026-10-06 (dodany blok wspolnych regul wtyczki).

- art. 415 - ok - wystepuje tylko jako przyklad formatu tagu Zweryfikowane, `(kodeks cywilny art. 415)`, we wspolnych regulach wtyczki fundament-weryfikacyjny (SHARED-RULES.md, skopiowane do kazdego skilla 2026-10-06). Sprawdzone u zrodla 2026-10-06 w Repertorium (verify_citations): eli:DU/1964/93, "Ustawa z dnia 23 kwietnia 1964 r. - Kodeks cywilny", art. 415, status no_known_changes_after_date, snapshot pl-2026-08. Przyklad nie przypisuje przepisowi zadnej tresci poza jego istnieniem i numerem.

## legal-ai-audit-bundle

Przeglad 2026-10-06 (dodany blok wspolnych regul wtyczki).

- art. 415 - ok - wystepuje tylko jako przyklad formatu tagu Zweryfikowane, `(kodeks cywilny art. 415)`, we wspolnych regulach wtyczki fundament-weryfikacyjny (SHARED-RULES.md, skopiowane do kazdego skilla 2026-10-06). Sprawdzone u zrodla 2026-10-06 w Repertorium (verify_citations): eli:DU/1964/93, "Ustawa z dnia 23 kwietnia 1964 r. - Kodeks cywilny", art. 415, status no_known_changes_after_date, snapshot pl-2026-08. Przyklad nie przypisuje przepisowi zadnej tresci poza jego istnieniem i numerem.

## legal-request-router-pl

Przeglad 2026-10-06 (dodany blok wspolnych regul wtyczki).

- art. 415 - ok - wystepuje tylko jako przyklad formatu tagu Zweryfikowane, `(kodeks cywilny art. 415)`, we wspolnych regulach wtyczki fundament-weryfikacyjny (SHARED-RULES.md, skopiowane do kazdego skilla 2026-10-06). Sprawdzone u zrodla 2026-10-06 w Repertorium (verify_citations): eli:DU/1964/93, "Ustawa z dnia 23 kwietnia 1964 r. - Kodeks cywilny", art. 415, status no_known_changes_after_date, snapshot pl-2026-08. Przyklad nie przypisuje przepisowi zadnej tresci poza jego istnieniem i numerem.

## ocena-outputu-pl

Przeglad 2026-10-06 (dodany blok wspolnych regul wtyczki).

- art. 415 - ok - wystepuje tylko jako przyklad formatu tagu Zweryfikowane, `(kodeks cywilny art. 415)`, we wspolnych regulach wtyczki fundament-weryfikacyjny (SHARED-RULES.md, skopiowane do kazdego skilla 2026-10-06). Sprawdzone u zrodla 2026-10-06 w Repertorium (verify_citations): eli:DU/1964/93, "Ustawa z dnia 23 kwietnia 1964 r. - Kodeks cywilny", art. 415, status no_known_changes_after_date, snapshot pl-2026-08. Przyklad nie przypisuje przepisowi zadnej tresci poza jego istnieniem i numerem.

## pierwsze-wrazenie-sedziego-pl

Przeglad 2026-10-06 (dodany blok wspolnych regul wtyczki).

- art. 415 - ok - wystepuje tylko jako przyklad formatu tagu Zweryfikowane, `(kodeks cywilny art. 415)`, we wspolnych regulach wtyczki fundament-weryfikacyjny (SHARED-RULES.md, skopiowane do kazdego skilla 2026-10-06). Sprawdzone u zrodla 2026-10-06 w Repertorium (verify_citations): eli:DU/1964/93, "Ustawa z dnia 23 kwietnia 1964 r. - Kodeks cywilny", art. 415, status no_known_changes_after_date, snapshot pl-2026-08. Przyklad nie przypisuje przepisowi zadnej tresci poza jego istnieniem i numerem.

## subsumpcja-pl

Przeglad 2026-10-06 (dodany blok wspolnych regul wtyczki).

- art. 415 - ok - wystepuje tylko jako przyklad formatu tagu Zweryfikowane, `(kodeks cywilny art. 415)`, we wspolnych regulach wtyczki fundament-weryfikacyjny (SHARED-RULES.md, skopiowane do kazdego skilla 2026-10-06). Sprawdzone u zrodla 2026-10-06 w Repertorium (verify_citations): eli:DU/1964/93, "Ustawa z dnia 23 kwietnia 1964 r. - Kodeks cywilny", art. 415, status no_known_changes_after_date, snapshot pl-2026-08. Przyklad nie przypisuje przepisowi zadnej tresci poza jego istnieniem i numerem.

## rodo-naruszenie-72h-pl

Przeglad 2026-10-10 (przejscie gotowosci: wszystkie jednostki redakcyjne skilla i skryptu, pelny mianownik, sprawdzone wobec tekstu zrodla; wady poprawione w tym samym przejsciu; blizniak gdpr-*-en sprawdzony tego samego dnia).

- art. 4 - ok - art. 4 pkt 12: "naruszenie bezpieczenstwa prowadzace do przypadkowego lub niezgodnego z prawem zniszczenia, utracenia, zmodyfikowania, nieuprawnionego ujawnienia lub nieuprawnionego dostepu"; skill zgodny (podzial poufnosc/integralnosc/dostepnosc z wytycznych EROD). EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 33 - ok - zgloszenie organowi nadzorczemu; tytul i zakres zgodne. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 33 ust. 1 - POPRAWIONE, potem ok - "bez zbednej zwloki - w miare mozliwosci, nie pozniej niz w terminie 72 godzin po stwierdzeniu naruszenia ... chyba ze jest malo prawdopodobne, by naruszenie to skutkowalo ryzykiem"; po 72 godzinach "wyjasnienie przyczyn opoznienia". Skill i skrypt podawaly "Termin: 72 godziny" bezwarunkowo - obowiazek warunkowy zapisany jako plaski cel 72h. Teraz: bez zbednej zwloki, 72h jako granica. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 33 ust. 3 - POPRAWIONE, potem ok - "musi co najmniej": a) charakter, "w miare mozliwosci" kategorie i przyblizona liczba osob i wpisow, b) "imie i nazwisko oraz dane kontaktowe inspektora ochrony danych lub oznaczenie innego punktu kontaktowego", c) mozliwe konsekwencje, d) srodki, "w tym w stosownych przypadkach" minimalizujace skutki. Skill mial "dane kontaktowe IOD" (bez innego punktu kontaktowego) i bez "w miare mozliwosci"; poprawione. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 33 ust. 4 - ok - informacje mozna udzielac "sukcesywnie bez zbednej zwloki"; dopisane. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 33 ust. 5 - ok - dokumentowanie wszelkich naruszen: okolicznosci, skutki, dzialania zaradcze - zgodne z "KAZDE naruszenie (nawet niezgloszone)". EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 34 - ok - zawiadomienie osoby przy wysokim ryzyku, "bez zbednej zwloki". Ust. 2: jasny i prosty jezyk, charakter naruszenia oraz informacje z art. 33 ust. 3 lit. b, c, d - stad "IOD lub inny punkt kontaktowy". EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 34 ust. 3 - POPRAWIONE, potem ok - a) srodki ochrony "zastosowane do danych osobowych, ktorych dotyczy naruszenie" (np. szyfrowanie), b) srodki "eliminujace prawdopodobienstwo wysokiego ryzyka", c) "niewspolmiernie duzy wysilek" - wtedy "publiczny komunikat lub ... podobny srodek ... w rownie skuteczny sposob". Dodane zastosowanie do danych naruszenia i warunek rownej skutecznosci. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- wytyczne EROD 9/2022 - POPRAWIONE, potem ok - czesc "B. Factors to consider when assessing risk": typ naruszenia; charakter, wrazliwosc i wolumen; latwosc identyfikacji; waga skutkow; cechy szczegolne osoby; cechy szczegolne administratora (pkt 117: "a medical organisation"); liczba osob; uwagi ogolne. Skill pomijal czynnik administratora; dodany z przykladem z wytycznych. Wytyczne opisuja sie jako zaktualizowana wersja WP250 (rev.01). Sprawdzone na wersji EN (wersji PL v2.0 nie pobrano). EDPB Guidelines 9/2022 v2.0 (przyjete 28.03.2023), PDF z edpb.europa.eu, pelny tekst przeczytany 2026-10-10.
- art. 3 ust. 1 - ok (nazwane ograniczenie) - rozporzadzenie 1182/71: przy terminie w godzinach liczonym od zdarzenia "godziny, w ktorej nastapilo to zdarzenie, nie wlicza sie" do terminu. Skrypt liczy moment stwierdzenia + 72h, co nigdy nie wypada pozniej niz tak liczony termin; skill i skrypt to mowia. Nie twierdzimy, ze 1182/71 rzadzi terminami RODO. EUR-Lex CELEX:31971R1182 (HTML pobrany 2026-10-10, komplet 6 artykulow).

## rodo-dpia-pl

Przeglad 2026-10-10 (przejscie gotowosci: wszystkie jednostki redakcyjne skilla i skryptu, pelny mianownik, sprawdzone wobec tekstu zrodla; wady poprawione w tym samym przejsciu; blizniak gdpr-*-en sprawdzony tego samego dnia).

- art. 35 - ok - ocena skutkow dla ochrony danych; tytul i zakres zgodne. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 35 ust. 1 - ok - przy "z duzym prawdopodobienstwem ... wysokim ryzyku" administrator "przed rozpoczeciem przetwarzania" dokonuje oceny; dopisane "przed rozpoczeciem przetwarzania". EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 35 ust. 2 - ok - konsultacja z IOD, "jezeli zostal on wyznaczony"; brzmienie dostosowane. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 35 ust. 3 - POPRAWIONE, potem ok - lit. a: "systematycznej, kompleksowej oceny czynnikow osobowych ... ktora opiera sie na zautomatyzowanym przetwarzaniu, w tym profilowaniu, i jest podstawa decyzji wywolujacych skutki prawne ... lub w podobny sposob znaczaco wplywajacych"; lit. b: dane z art. 9 ust. 1 lub art. 10 na duza skale; lit. c: systematyczny monitoring na duza skale miejsc dostepnych publicznie. Skill i etykieta skryptu mialy lit. a jako "systematyczna i kompleksowa ocena (profilowanie)" - bez warunku skutkow decyzji, co zawyza przypadek obligatoryjny. Poprawione w obu. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 9 ust. 1 - ok - szczegolne kategorie danych jako kategoria z art. 35 ust. 3 lit. b. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 10 - ok - dane o wyrokach skazujacych i czynach zabronionych jako kategoria z art. 35 ust. 3 lit. b. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 22 - ok - powolany przy kryterium 2 WP248 ("Automated-decision making with legal or similar significant effect"); WP248 odsyla do art. 22 przy kryterium 9. WP29 WP248 rev.01 (przyjete 4.04.2017, zmienione 4.10.2017), PDF z ec.europa.eu, pelny tekst przeczytany 2026-10-10.
- art. 35 ust. 4 - POPRAWIONE, potem ok - "organ nadzorczy ustanawia i podaje do publicznej wiadomosci wykaz rodzajow operacji przetwarzania podlegajacych wymogowi dokonania oceny skutkow dla ochrony danych". Skill opisywal polski wykaz jako "rodzaje operacji zawsze wymagajacych DPIA" - nieprawda: Komunikat Prezesa UODO (M.P. 2019 poz. 666) to wykaz kryteriow z przykladami, w ktorym "co do zasady przetwarzanie spelniajace przynajmniej dwa z nizej wymienionych kryteriow bedzie wymagac oceny", a "w niektorych przypadkach" wystarczy jedno; przyklady "maja charakter wylacznie ilustracyjny"; kryterium monitoringu wylacza zwykly monitoring wizyjny nagrywany na potrzeby incydentow. Opis przepisany; ten sam blad w blizniaku EN poprawiony. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow); Repertorium eli:MP/2019/666 (Komunikat Prezesa UODO z 17.06.2019, M.P. 2019 poz. 666), tekst odczytany 2026-10-10.
- art. 35 ust. 7 - ok - "co najmniej" a) systematyczny opis i cele, w tym gdy ma to zastosowanie prawnie uzasadnione interesy, b) niezbednosc i proporcjonalnosc, c) ryzyko, d) srodki. Rozwiniecie przy lit. b to opracowanie, nie teza o brzmieniu. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 36 - ok - uprzednie konsultacje; tytul i zakres zgodne. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- art. 36 ust. 1 - ok z atrybucja - tekst: konsultacja, gdy ocena wskazuje, ze przetwarzanie powodowaloby wysokie ryzyko, "gdyby administrator nie zastosowal srodkow w celu zminimalizowania tego ryzyka". "Ryzyko szczatkowe pozostaje wysokie" to odczytanie WP248 ("Whenever the data controller cannot find sufficient measures to reduce the risks to an acceptable level ... consultation ... is required"); skill przypisuje je teraz WP248. EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow); WP29 WP248 rev.01 (przyjete 4.04.2017, zmienione 4.10.2017), PDF z ec.europa.eu, pelny tekst przeczytany 2026-10-10.
- art. 36 ust. 3 - ok - zawartosc wniosku lit. a-f, powolana tylko jako "zakres z art. 36 ust. 3". EUR-Lex CELEX:32016R0679, wersja PL (HTML pobrany 2026-10-10, komplet 99 artykulow).
- WP248 - POPRAWIONE, potem ok - dziewiec kryteriow potwierdzone; regula "In most cases ... meeting two criteria would require a DPIA" oraz "in some cases ... only one". Poprawione: skill przypisywal WP248 EROD (to dokument Grupy Roboczej Art. 29); regula ">=2" ma teraz "w wiekszosci przypadkow"; przyklady kryterium 8 sa z WP248 (odciski palcow z rozpoznawaniem twarzy, Internet rzeczy) zamiast dopisanego "AI". Logika werdyktu skryptu (1 kryterium = zalecane, 2+ = wymagane) zgodna. WP29 WP248 rev.01 (przyjete 4.04.2017, zmienione 4.10.2017), PDF z ec.europa.eu, pelny tekst przeczytany 2026-10-10.
- Art. 29 - ok - nie jednostka przepisu: "Grupa Robocza Art. 29", autor WP248 (strona tytulowa WP248 rev.01). WP29 WP248 rev.01 (przyjete 4.04.2017, zmienione 4.10.2017), PDF z ec.europa.eu, pelny tekst przeczytany 2026-10-10.
