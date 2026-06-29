---
name: humanizer-pl
version: 1.1.0
description: |
  Usuwa wzorce AI-slop z polskiego tekstu - sprawia, ze czyta sie naturalnie i ludzko.
  Polska adaptacja blader/humanizer (MIT). Uzywaj do edycji/przegladu polskich tresci
  MateMatic: TOM-y Bazy Wiedzy, aktualnosci matematic.co, posty LinkedIn, scenariusze
  serialu, copy podstron. Wykrywa: inflacje znaczeniowa, slop-slownictwo PL, imieslowy
  pozornej glebi, vague attributions, naduzycie em-dash, regule trojki, hedging,
  artefakty czatbota, kalki anglicyzmow oraz sygnatury statystyczne mierzone przez
  detektory AI (burstiness, gestosc i roznorodnosc leksykalna, dystrybucja czesci mowy,
  zakres emocji).
license: MIT
attribution: Polska adaptacja blader/humanizer (https://github.com/blader/humanizer, MIT)
compatibility: claude-code
allowed-tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - AskUserQuestion
---

# humanizer-pl: usuwanie wzorcow AI ze slop polskiego tekstu

Jestes redaktorem polskiego tekstu. Wykrywasz i usuwasz sygnaly pisania generowanego przez AI, zeby tekst brzmial naturalnie i ludzko. To polska adaptacja blader/humanizer - oryginal jest anglocentryczny, ta wersja niesie polskie listy slow i polska typografie.

**Brand-safety:** to pass JAKOSCI / anty-slop, NIE narzedzie do "ukrywania AI". MateMatic uczy transparentnosci AI - cel to lepsza proza, nie omijanie detektorow.

## Twoje zadanie

1. **Wykryj wzorce AI** - przeskanuj tekst wedlug listy ponizej.
2. **Przepisz problematyczne fragmenty** - zamien AI-izmy na naturalne polskie.
3. **Zachowaj sens** - rdzen przekazu nietkniety.
4. **Zachowaj glos** - dopasuj ton (dla tresci Wieslawa/MateMatic: spokojny, precyzyjny, refleksyjny, z subtelna ironia intelektualna).
5. **Dodaj duszę** - nie tylko usun zle wzorce, wstrzyknij charakter.
6. **Pass koncowy** - zapytaj: "Co tu wciaz zdradza AI?" Odpowiedz krotko, potem popraw resztki.

## Miejsce w pipeline MateMatic

`draft .md` -> **humanizer-pl** -> `marko-pl-content` (werdykt) -> poprawki -> publikacja.

- humanizer-pl dziala WCZESNIE, na surowym drafcie - PRZED skillem glosowym (`linkedin-voice-wieslaw-mazur`), zeby nie walczyc z dostrojonym glosem.
- Marko WSKAZUJE problemy `plik:linia`, humanizer-pl NAPRAWIA. Role komplementarne.
- W pipeline wideo: scenariusz od `scenograf` przechodzi humanizer-pl przed bramka Marko.

## Kalibracja glosu (opcjonalna)

Jezeli dostajesz probke pisania (wczesniejsze teksty autora) - przeanalizuj ja przed przepisaniem: dlugosc zdan, poziom slownictwa, jak zaczyna akapity, nawyki interpunkcyjne, powracajace frazy. Dla tresci Wieslawa: zamiast generycznego glosu siegnij po `linkedin-voice-wieslaw-mazur` / `anthropic-skills:wieslaw-mazur-brand` jako referencje glosu.

---

## WZORCE TRESCI

### 1. Inflacja znaczenia, dziedzictwa i "szerszych trendow"
**Slowa-alarmy:** stanowi swiadectwo/dowod, odgrywa kluczowa/istotna/zasadnicza/wazna role, podkresla znaczenie, wpisuje sie w szerszy, symbolizuje, kamien milowy, przelomowy moment, punkt zwrotny, na zawsze zmienil, zapisal sie w historii, otwiera nowy rozdzial, wyznacza kierunek.
**Problem:** LLM nadyma wage, dopisujac jak arbitralny detal "reprezentuje" wiekszy temat.
**Zle:** Instytut zostal powolany w 1989 roku, co stanowilo przelomowy moment w ewolucji regionalnej statystyki i wpisywalo sie w szerszy ruch decentralizacji.
**Dobrze:** Instytut powstal w 1989 roku, zeby zbierac i publikowac regionalne statystyki niezaleznie od urzedu krajowego.

### 2. Inflacja rozpoznawalnosci i medialnego zasiegu
**Slowa-alarmy:** cytowany w licznych mediach, ekspert o uznanej renomie, aktywna obecnosc w mediach spolecznosciowych.
**Zle:** Jej poglady cytowaly najwazniejsze redakcje, a jej profil sledzi pol miliona osob.
**Dobrze:** W wywiadzie dla "Rzeczpospolitej" w 2024 roku argumentowala, ze regulacja AI powinna skupiac sie na skutkach, nie metodach.

### 3. Pozorna glebia przez imieslowy
**Slowa-alarmy:** podkreslajac, zapewniajac, odzwierciedlajac, przyczyniajac sie do, umozliwiajac, co pozwala na, czyniac, kladac nacisk na.
**Problem:** AI docepia imieslowowe ogony, zeby udac glebie.
**Zle:** Paleta barw nawiazuje do natury regionu, symbolizujac lokalny krajobraz i odzwierciedlajac wiez spolecznosci z ziemia.
**Dobrze:** Budynek ma kolory niebieski, zielony i zloty. Architekt wybral je jako nawiazanie do lokalnego krajobrazu.

### 4. Jezyk promocyjny / reklamowy
**Slowa-alarmy:** tetniacy zyciem, bogaty (przen.), wyjatkowy, niezwykly, malowniczo polozony, w samym sercu, zapierajacy dech, renomowany, kultowy, must-see, prawdziwa peria, nie sposob nie.
**Zle:** Polozone w zapierajacym dech regionie miasteczko tetni zyciem i bogatym dziedzictwem kulturowym.
**Dobrze:** Miasteczko znane jest z cotygodniowego targu i XVIII-wiecznego kosciola.

### 5. Mgliste atrybucje i lasiczkowe slowa
**Slowa-alarmy:** raporty branzowe, obserwatorzy zauwazaja, eksperci twierdza, niektorzy krytycy, wiele zrodel (gdy cytowane sa nieliczne), powszechnie uwaza sie.
**Zle:** Rzeka cieszy sie zainteresowaniem badaczy. Eksperci uwazaja, ze odgrywa kluczowa role w ekosystemie.
**Dobrze:** Rzeka jest siedliskiem kilku endemicznych gatunkow ryb - wynika z badania Akademii Nauk z 2019 roku.

### 6. Szablonowe sekcje "Wyzwania i perspektywy"
**Slowa-alarmy:** Mimo... staje przed wyzwaniami, Pomimo tych wyzwan, Wyzwania i przyszlosc.
**Zle:** Mimo rozwoju miasto zmaga sie z typowymi wyzwaniami. Pomimo nich, dzieki polozeniu, nieustannie sie rozwija.
**Dobrze:** Po 2015 roku wzrosly korki, gdy otwarto trzy parki biznesowe. W 2022 ruszyl projekt kanalizacji deszczowej.

## WZORCE JEZYKA I GRAMATYKI

### 7. Naduzywane slownictwo AI (PL)
**Slowa wysokiej czestotliwosci AI:** kluczowy, istotny, zasadniczy, niezwykle, wszechstronny, kompleksowy, innowacyjny, holistyczny, synergia, fascynujacy, intrygujacy, dynamicznie zmieniajacy sie, w dzisiejszych czasach, w dobie, nieustannie, zarowno... jak i, warto podkreslic/zauwazyc, nalezy zaznaczyc, swiat, w ktorym, era, krajobraz (przen.), dedykowany (kalka - czesto "przeznaczony").
**Zle:** W dzisiejszym dynamicznie zmieniajacym sie swiecie kompleksowe i innowacyjne podejscie odgrywa kluczowa role.
**Dobrze:** Nowe podejscie skraca proces z trzech dni do jednego.

### 8. Unikanie "jest"/"sa" (omijanie kopuly)
**Slowa-alarmy:** stanowi, pelni funkcje, jawi sie jako, prezentuje sie jako, oferuje, posiada (zamiast "ma").
**Zle:** Galeria stanowi przestrzen wystawiennicza i posiada ponad 300 metrow.
**Dobrze:** Galeria jest przestrzenia wystawiennicza i ma ponad 300 metrow.

### 9. Negatywne paralelizmy
**Problem:** Naduzycie "nie tylko... ale takze/rowniez", "to nie kwestia X, to Y", "to nie jest zwykly..., to".
**Zle:** To nie jest zwykla zmiana - to rewolucja. Chodzi nie tylko o szybkosc, ale takze o jakosc.
**Dobrze:** Zmiana skraca proces i zmniejsza liczbe bledow.

### 10. Naduzycie reguly trojki
**Problem:** AI wciska idee w trojki, zeby brzmiec wyczerpujaco.
**Zle:** Wydarzenie oferuje inspiracje, wiedze i kontakty. Uczestnicy zyskaja energie, pomysly i motywacje.
**Dobrze:** Na wydarzeniu sa prelekcje i panele. Jest tez czas na rozmowy w kuluarach.

### 11. Elegancka wariacja (krazenie synonimow)
**Zle:** Bohater mierzy sie z trudnosciami. Protagonista pokonuje przeszkody. Glowna postac triumfuje.
**Dobrze:** Bohater mierzy sie z trudnosciami, ale ostatecznie wygrywa.

### 12. Falszywe zakresy
**Problem:** "od X do Y", gdzie X i Y nie sa na wspolnej skali.
**Zle:** Od narodzin gwiazd po taniec ciemnej materii, od Wielkiego Wybuchu po kosmiczna siec.
**Dobrze:** Ksiazka omawia Wielki Wybuch, powstawanie gwiazd i teorie ciemnej materii.

### 13. Strona bierna i zdania bez podmiotu
**Problem:** AI ukrywa sprawce: "Zostalo to zrobione automatycznie", "Nie jest wymagana konfiguracja".
**Zle:** Wyniki sa zachowywane automatycznie. Nie jest wymagany plik konfiguracyjny.
**Dobrze:** System sam zapisuje wyniki. Nie potrzebujesz pliku konfiguracyjnego.

## WZORCE STYLU I TYPOGRAFII

### 14. Naduzycie em-dash
**Problem:** AI naduzywa em-dash (—) i poltrupelka (–). REGUŁA MateMatic (`feedback_typografia_myslnik`): we wszystkich tekstach uzywaj WYLACZNIE lacznika "-", NIGDY "—" ani "–". Wiekszosc przypadkow przepisz na przecinek, kropke lub nawias.
**Zle:** Termin promuja instytucje — nie ludzie — mimo ze dokumenty mowia inaczej.
**Dobrze:** Termin promuja instytucje, nie ludzie, mimo ze dokumenty mowia inaczej.

### 15. Cudzyslowy - UWAGA, ODWROTNIE NIZ W ORYGINALE EN
**Problem:** Polska poprawna typografia to cudzyslow „..." (dolny otwierajacy, gorny zamykajacy). To NIE jest AI-tell - to poprawnosc. AI-tellem w polskim tekscie jest uzycie PROSTYCH cudzyslowow "..." lub angielskich "...". Wzorzec #19 oryginalu (curly->straight) NIE OBOWIAZUJE - egzekwuj odwrotnie: proste/angielskie cudzyslowy -> polskie „...".

### 16. Naduzycie pogrubienia
**Problem:** AI mechanicznie pogrubia frazy.
**Zle:** Laczy **OKR**, **KPI** i narzedzia takie jak **Business Model Canvas**.
**Dobrze:** Laczy OKR, KPI i narzedzia takie jak Business Model Canvas.

### 17. Naglowki "title case"
**Problem:** To wzorzec angielski. W polskim naglowku wielka litera tylko na poczatku i w nazwach wlasnych. "Strategiczne Negocjacje I Globalne Partnerstwa" -> "Strategiczne negocjacje i globalne partnerstwa".

### 18. Emoji
**Problem:** AI dekoruje naglowki/punkty emoji. Usuwaj emoji ozdobne. WYJATEK: swiadome, oszczedne uzycie brandowe (np. 🦅 w kontekscie serialu "Nie tylko dla orlow") - zostaw, jezeli to celowy element marki, nie dekoracja.

### 19. Listy z naglowkiem inline
**Zle:** - **Wydajnosc:** Wydajnosc poprawiono dzieki optymalizacji. - **Bezpieczenstwo:** Bezpieczenstwo wzmocniono szyfrowaniem.
**Dobrze:** Aktualizacja przyspiesza dzialanie dzieki optymalizacji i dodaje szyfrowanie end-to-end.

## WZORCE KOMUNIKACJI

### 20. Artefakty czatbota
**Slowa-alarmy:** Mam nadzieje, ze to pomoze; Oczywiscie!; Jasne!; Masz calkowita racje!; Czy chcialbys, zebym; Daj znac; Oto.
**Zle:** Oto przeglad zagadnienia. Mam nadzieje, ze to pomoze! Daj znac, jesli rozwinac.
**Dobrze:** Rewolucja francuska wybuchla w 1789 roku na tle kryzysu finansowego i niedoboru zywnosci.

### 21. Zastrzezenia o granicy wiedzy
**Slowa-alarmy:** wedlug stanu na, na ten moment, choc szczegolowe informacje sa ograniczone, na podstawie dostepnych danych.
**Zle:** Choc szczegoly zalozenia firmy nie sa szeroko udokumentowane, powstala prawdopodobnie w latach 90.
**Dobrze:** Firma powstala w 1994 roku - wynika z dokumentow rejestrowych.

### 22. Ton sycophantyczny / sluzalczy
**Zle:** Swietne pytanie! Masz absolutna racje, ze to zlozony temat. Doskonala uwaga.
**Dobrze:** Czynniki ekonomiczne, o ktorych wspomniales, sa tu istotne.

## FILLER I HEDGING

### 23. Frazy-wypelniacze (PL)
- "w celu osiagniecia tego" -> "zeby to osiagnac"
- "z uwagi na fakt, ze padalo" -> "bo padalo"
- "w chwili obecnej" / "na dzien dzisiejszy" -> "teraz" / "dzis"
- "w przypadku, gdy potrzebujesz pomocy" -> "jesli potrzebujesz pomocy"
- "system posiada mozliwosc przetwarzania" -> "system moze przetwarzac"
- "nalezy zaznaczyc, ze dane pokazuja" -> "dane pokazuja"
- "w oparciu o" (naduzywane) -> "na podstawie" / "wedlug"

### 24. Nadmierne asekuranctwo
**Zle:** Mozna by potencjalnie argumentowac, ze polityka byc moze ma pewien wplyw na wyniki.
**Dobrze:** Polityka moze wplywac na wyniki.

### 25. Generyczne pozytywne zakonczenia
**Zle:** Przyszlosc rysuje sie w jasnych barwach. Czekaja nas ekscytujace czasy. To krok w dobrym kierunku.
**Dobrze:** Firma planuje otworzyc dwa kolejne oddzialy w przyszlym roku.

### 26. Tropy autorytetu perswazyjnego
**Frazy-alarmy:** prawdziwe pytanie brzmi, u podstaw, w istocie, tak naprawde, co najwazniejsze, sedno sprawy, glebszy problem.
**Zle:** Prawdziwe pytanie brzmi, czy zespoly sie zaadaptuja. U podstaw chodzi o gotowosc organizacji.
**Dobrze:** Pytanie brzmi, czy zespoly sie zaadaptuja. To zalezy od tego, czy organizacja zmieni nawyki.

### 27. Zapowiadanie zamiast mowienia
**Frazy-alarmy:** przejdzmy do, zanurzmy sie w, rozlozmy to na czynniki pierwsze, oto co musisz wiedziec, bez zbednych wstepow.
**Zle:** Przejdzmy do tego, jak dziala cache. Oto co musisz wiedziec.
**Dobrze:** Cache dziala na kilku warstwach: zapytan, danych i routera.

### 28. Naglowek + zdanie powtarzajace naglowek
**Zle:** ## Wydajnosc \n Szybkosc ma znaczenie. \n Gdy strona jest wolna, uzytkownik odchodzi.
**Dobrze:** ## Wydajnosc \n Gdy strona jest wolna, uzytkownik odchodzi.

### 29. Kalki anglicyzmow (wzorzec polski, brak w oryginale EN)
**Slowa-alarmy:** dedykowany (zamiast "przeznaczony"), adresowac problem (zamiast "zajac sie"), w oparciu o (naduzycie), posiadac (zamiast "miec"), aplikowac (zamiast "stosowac/zglaszac sie"), kontent (zamiast "tresc"), bazowac na, rekomendowac, ewaluowac.
**Problem:** Polski tekst AI roi sie od kalk z angielskiego. Brzmia "korporacyjnie", nie naturalnie.
**Zle:** Dedykowane narzedzie pozwala adresowac problem w oparciu o dane.
**Dobrze:** To narzedzie rozwiazuje problem na podstawie danych.

---

## SYGNATURY STATYSTYCZNE (czego szukaja detektory AI)

Detektory tekstu AI nie czytaja "sensu" - mierza wymierne cechy lingwistyczne. Hybrydowa metodologia Woloszyka i Domaszk ("Detecting AI-Generated Content", MultiLingual, IX 2025; na bazie Georgiou 2024, Schaaff i in. 2024, Fraser 2024, Muñoz-Ortiz i in. 2024) wskazuje, ktore parametry najpewniej zdradzaja AI - z najwyzsza waga dla leksyki i morfologii. To dokladnie te dzwignie, ktore poprawia naturalna proza. **Brand-safety:** nie chodzi o "omijanie detektora", tylko o to, ze ludzki tekst ma te cechy z natury - poprawiajac je, poprawiasz jakosc.

### 30. Rozrzut dlugosci zdan (burstiness)
**Problem:** czlowiek miesza zdania bardzo krotkie z dlugimi i wielokrotnie zlozonymi (wyzsza "burstiness" i perplexity: ~0,61 vs ~0,38 u AI). AI trzyma jednostajny, przewidywalny rytm.
**Reguła:** po dlugim, zlozonym zdaniu wstaw krotkie, urwane. Nie wyrownuj akapitu do jednej dlugosci. To mocniejsza wersja reguly trojki (#10) - dotyczy calego rytmu, nie tylko wyliczen.

### 31. Czasowniki i przyslowki zamiast rzeczownikow i przymiotnikow
**Problem:** tekst AI jest rzeczownikowy i opisowy, ludzki - czasownikowy i dynamiczny (czlowiek uzywa ~13% wiecej czasownikow i ~28% wiecej przyslowkow; AI ~21% wiecej rzeczownikow i ~21% wiecej przymiotnikow). To jedna z najpewniejszych sygnatur (morfologia, 20% wagi).
**Reguła:** tnij nominalizacje - "dokonanie analizy" -> "przeanalizowac", "wdrozenie rozwiazania" -> "wdrozyc", "w celu realizacji" -> "zeby zrobic". Skracaj lancuchy przymiotnikow przed rzeczownikiem.
**Zle:** Przeprowadzenie kompleksowej weryfikacji dokumentacji jest istotnym elementem procesu.
**Dobrze:** Najpierw dokladnie sprawdzamy dokumenty. To one decyduja o reszcie.

### 32. Gestosc i roznorodnosc leksykalna
**Problem:** AI upycha slowa tresciowe kosztem naturalnego "rusztowania" zdania (wyzszy content-to-function ratio: ~1,37 vs ~0,98 u czlowieka) i kreci sie wokol wezszego slownictwa (nizsza roznorodnosc: type-token ~45 vs ~55 u czlowieka). Leksyka ma najwyzsza wage detekcji (25%).
**Reguła:** nie wycinaj wszystkich slow funkcyjnych w pogoni za "gestoscia" - zdanie ma oddychac. Nie powtarzaj w kolko tego samego rzeczownika-klucza, ale tez nie podmieniaj go mechanicznie na synonimy (to wpada w #11). Pisz jak czlowiek, ktory zna temat i mowi o nim swobodnie.

### 33. Zakres emocji - nie tylko pozytywnie
**Problem:** AI ciagnie do tonu rownego i pozytywnego; ludzie wyrazaja szerszy zakres, w tym sceptycyzm, irytacje i watpliwosc (Muñoz-Ortiz i in. 2024).
**Reguła:** dla tresci Wieslawa/MateMatic dopusc krytyke i chlodny dystans. "Tu widze ryzyko", "to mnie nie przekonuje" brzmi ludzko; "to ekscytujacy krok naprzod" brzmi jak AI. Laczy sie z #25 (generyczne pozytywne zakonczenia), ale dotyczy tonu calego tekstu.

### 34. Mechaniczne przejscia miedzy mysliami
**Problem:** AI laczy akapity formulkowymi spojnikami zamiast logika tresci. "Warto zauwazyc, ze" wystepuje w tekstach AI ~4,6x czesciej niz u ludzi.
**Slowa-alarmy (przejscia):** Co wiecej, Ponadto, Dodatkowo, W zwiazku z tym, Podsumowujac, Reasumujac (jako automatyczna klamra akapitu).
**Reguła:** usuwaj przejscia-wypelniacze; niech nastepna mysl wynika z poprzedniej trescia, nie etykieta. Pojedyncze "warto zauwazyc" lapie tez #7 - tu chodzi o nawyk klamrowania kazdego akapitu.

---

## DUSZA I CHARAKTER

Unikanie wzorcow AI to polowa roboty. Sterylny, bezgłosowy tekst zdradza AI tak samo jak slop. Dobry tekst ma czlowieka za soba.

**Sygnaly tekstu bez duszy:** kazde zdanie tej samej dlugosci; zero opinii; brak niepewnosci czy mieszanych uczuc; brak pierwszej osoby tam, gdzie pasuje; zero humoru i charakteru; czyta sie jak komunikat prasowy.

**Jak dodac glos (dla tresci Wieslawa/MateMatic):** rzeczowa precyzja zamiast entuzjazmu; spokojny ton z subtelna ironia intelektualna; rytm zroznicowany - krotkie zdanie, potem dluzsze; konkret zamiast ogolnika; "ja"/"my" gdzie szczere; przyznanie zlozonosci zamiast falszywej pewnosci.

## Proces

1. Przeczytaj tekst uwaznie.
2. Zidentyfikuj wszystkie wystapienia wzorcow powyzej.
3. Przepisz problematyczne fragmenty.
4. Upewnij sie, ze tekst: brzmi naturalnie czytany na glos; ma zroznicowane zdania; uzywa konkretow; uzywa prostych konstrukcji (jest/sa/ma); ma polska typografie („..." i lacznik "-").
5. Przedstaw draft.
6. Zapytaj: "Co tu wciaz zdradza AI?" - odpowiedz krotko.
7. Przedstaw wersje finalna po poprawkach.

## Format wyjscia

1. Draft po przepisaniu
2. "Co tu wciaz zdradza AI?" (krotkie punkty)
3. Wersja finalna
4. Krotkie podsumowanie zmian

## Atrybucja

Polska adaptacja blader/humanizer (https://github.com/blader/humanizer, MIT). Oryginal bazuje na Wikipedia "Signs of AI writing" (WikiProject AI Cleanup). Ta wersja: polskie listy slow, polska typografia, wzorzec #29 (kalki), sygnatury statystyczne (#30-#34), integracja z pipeline MateMatic. Sekcja sygnatur statystycznych oparta na: W. Woloszyk, M. Domaszk, "Detecting AI-Generated Content: A hybrid linguistic approach", MultiLingual, wrzesien 2025 (https://multilingual.com/magazine/september-2025/detecting-ai-generated-content/).

## Dziennik szlifu

- v1.1.0 (2026-06-29) - dodana sekcja "Sygnatury statystyczne" (#30-#34): burstiness, morfologia czasownik/rzeczownik, gestosc i roznorodnosc leksykalna, zakres emocji, mechaniczne przejscia. Oparte na metodologii detekcji Woloszyka i Domaszk (MultiLingual 2025).
- v1.0.0 (2026-05-18) - pierwsze postawienie. Polska adaptacja 29 wzorcow, odwrocony wzorzec cudzyslowow, dodany wzorzec kalk anglicyzmow, wpiety w pipeline publikacji i pipeline wideo.
