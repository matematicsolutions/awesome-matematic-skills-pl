---
name: tajemnica-preflight-pl
description: >-
  Pre-flight check treści prawnej PRZED wysłaniem jej do zewnętrznego, chmurowego
  narzędzia AI (czat w przeglądarce, asystent w pakiecie biurowym, dowolne API poza
  kontrolą kancelarii). Inwentaryzuje, co faktycznie siedzi w promptcie, ocenia pięć
  czynników ryzyka (identyfikowalność klienta, fakty objęte tajemnicą, strategia
  procesowa, dane osób trzecich, warunki dostawcy AI), wydaje werdykt pasmowy
  SAFE / CAUTION / STOP z tabelą czynników i skutkami ujawnienia, a przy CAUTION
  przygotowuje zredagowaną wersję promptu do zatwierdzenia przez człowieka.
  Niczego nie wysyła i nie redaguje ostatecznie. Używaj gdy: "czy mogę to wkleić
  do czata", "czy ten prompt narusza tajemnicę", "preflight przed wysłaniem do AI",
  "co zanonimizować", "czy to bezpieczne dla tajemnicy adwokackiej", audyt promptów
  kancelarii, ocena skutków ujawnienia przed użyciem chmurowego AI.
license: Apache-2.0
allowed-tools: [Read]
data-residency: local
requires-human-approval: true
pii-egress: none
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.0.0
  inspiration: "pattern 'privilege pre-flight' z ekosystemu legal-AI - koncepcja pasm SAFE/CAUTION/STOP; całość tekstu i podstawy prawne PL/UE napisane od zera"
  companion_skills: matematic-prompt-defense-pl, rodo-dpia-pl, doc-intel-contract-pl, legal-request-router-pl
---

# Tajemnica preflight PL - kontrola promptu przed wysłaniem do chmurowego AI

## Filozofia

**Prompt wklejony do cudzego czata to ujawnienie. Nie "użycie narzędzia" - ujawnienie.**

Prawnik nie zastanawia się, czy wysłać akta sprawy faksem do redakcji gazety. Ale ten
sam prawnik potrafi wkleić pół pozwu do darmowego czatu, bo "chciał tylko poprawić
styl". Różnica jest żadna: treść opuszcza kancelarię i trafia do podmiotu trzeciego,
na warunkach, których nikt nie przeczytał, z retencją, której nikt nie kontroluje.

Ten skill robi jedną rzecz: zatrzymuje rękę nad klawiszem Enter na czas jednej
kontroli. Nie zakazuje chmurowego AI - kancelarie z niego korzystają i będą
korzystać. Wymusza za to świadomą decyzję: co dokładnie wychodzi, do kogo,
na jakich warunkach i co się stanie, jeśli to kiedyś wypłynie.

Werdykt jest pasmowy, nie zero-jedynkowy. Większość promptów nie jest ani czysta,
ani zakazana - jest do zredagowania. Dlatego pasmo środkowe (CAUTION) kończy się
draftem wersji zredagowanej, a nie moralizowaniem.

## Kiedy używać / Czego NIE robi

**Używaj:**
- przed wklejeniem treści związanej ze sprawą klienta do zewnętrznego czatu AI,
- przy audycie promptów kancelarii (retrospektywnie: co ludzie wysyłali),
- przy pisaniu wewnętrznej polityki użycia AI - pasma SAFE/CAUTION/STOP nadają się
  wprost jako szkielet polityki,
- gdy współpracownik pyta "czy mogę to wrzucić do czata" - zamiast odpowiadać
  z intuicji, przepuść treść przez preflight.

**Czego NIE robi (jawny zakres ujemny):**
- NIE wysyła niczego nigdzie - werdykt i draft zostają na maszynie,
- NIE wykonuje redakcji ostatecznie - przygotowuje wersję zredagowaną jako projekt,
  człowiek ją czyta, poprawia i sam decyduje o wysłaniu,
- NIE ocenia jakości merytorycznej promptu (od tego inne skille),
- NIE zastępuje analizy RODO dla wdrożenia narzędzia AI w kancelarii - od tego
  jest `rodo-dpia-pl`; preflight to kontrola pojedynczej treści, nie procesu,
- NIE daje gwarancji - pasmo SAFE znaczy "nie znalazłem czynnika ryzyka",
  nie "ręczę, że ryzyka nie ma".

## Podstawy prawne (przywołuj z tagiem pewności)

Numer przepisu podawaj tylko wtedy, gdy jest pewny. Jeśli nie - opisz obowiązek
słowami i oznacz `[DO SPRAWDZENIA]`. Nigdy nie wymyślaj numeru.

- **Tajemnica adwokacka** - art. 6 ustawy Prawo o adwokaturze: obowiązek zachowania
  w tajemnicy wszystkiego, o czym adwokat dowiedział się w związku z udzielaniem
  pomocy prawnej; nieograniczony w czasie.
- **Tajemnica radcowska** - art. 3 ustawy o radcach prawnych (obowiązek zachowania
  tajemnicy co do wszystkiego, o czym radca dowiedział się w związku z udzielaniem
  pomocy prawnej).
- **Tajemnica doradcy podatkowego** - ustawa o doradztwie podatkowym, art. 37
  `[DO SPRAWDZENIA - potwierdź numer i brzmienie przed cytowaniem w deliverable]`.
- **RODO** - dane osobowe klienta i osób trzecich w promptcie to przetwarzanie:
  definicja danych (art. 4 pkt 1), relacja z dostawcą AI jako podmiotem
  przetwarzającym (art. 28), transfer poza EOG (rozdział V).
- **Tajemnica przedsiębiorstwa** - art. 11 ustawy o zwalczaniu nieuczciwej
  konkurencji; ochrona wymaga "działań w celu utrzymania poufności" - wklejenie
  do publicznego czatu może ten warunek podważyć wobec informacji klienta.
- **Ryzyko dyscyplinarne** - naruszenie tajemnicy zawodowej to delikt dyscyplinarny
  na gruncie ustaw korporacyjnych i kodeksów etyki; konkretny przepis dobierz do
  zawodu użytkownika `[DO SPRAWDZENIA]`.

## Pięć czynników oceny

Każdy czynnik oceniaj osobno na skali: CZYSTY / UWAGA / KRYTYCZNY.

**(a) Identyfikowalność klienta.** Bezpośrednia (nazwa, NIP, KRS, imię i nazwisko,
sygnatura sprawy) ORAZ mozaikowa: kombinacja branży, miasta, kwoty sporu i daty
zdarzenia potrafi wskazać klienta jednoznacznie, choć żaden element osobno nie
identyfikuje. Test mozaikowy: czy dziennikarz lokalny z dostępem do wyszukiwarki
poznałby, o kogo chodzi?

**(b) Fakty objęte tajemnicą.** Wszystko, czego prawnik dowiedział się w związku
z udzielaniem pomocy prawnej - także fakty pozornie neutralne (że klient w ogóle
szuka pomocy w danej sprawie, to już fakt objęty tajemnicą).

**(c) Strategia procesowa / work-product** (termin z praktyki amerykańskiej: materiały robocze pełnomocnika przygotowane na potrzeby sporu). Planowane zarzuty, ocena słabości
własnej pozycji, taktyka negocjacyjna, wewnętrzne notatki o wiarygodności świadków.
Ta kategoria jest najgroźniejsza - jej ujawnienie szkodzi nawet po pełnej
pseudonimizacji, bo wartość ma sama treść rozumowania, nie tożsamość stron.

**(d) Dane osobowe stron trzecich.** Świadkowie, przeciwnik, członkowie rodziny,
pracownicy klienta. Oni nie wybierali kancelarii i niczego nie akceptowali -
podstawa przetwarzania ich danych w chmurowym AI jest z reguły najsłabsza.

**(e) Dokąd trafia prompt.** Warunki dostawcy AI: czy treść promptów jest używana
do treningu modeli, jaka jest retencja (i czy da się ją wyłączyć), gdzie stoją
serwery, czy zachodzi transfer poza EOG i na jakiej podstawie, czy jest umowa
powierzenia (art. 28 RODO), plan darmowy czy biznesowy (warunki bywają skrajnie
różne). Jeśli użytkownik nie wie - przyjmij wariant najgorszy i powiedz to wprost.

## Workflow (krok po kroku)

### 1. Inwentaryzacja treści
Rozbierz prompt na elementy: kto jest wymieniony (podmioty, osoby), jakie fakty,
jakie liczby i daty, jakie fragmenty dokumentów, czy jest w nim rozumowanie
prawnika (ocena, taktyka), dokąd użytkownik chce to wysłać (nazwa narzędzia i plan).
Bez inwentaryzacji nie ma oceny - "mniej więcej wiem, co tam jest" nie wystarcza.

### 2. Ocena pięciu czynników
Każdy czynnik (a)-(e) dostaje ocenę CZYSTY / UWAGA / KRYTYCZNY plus jedno zdanie
uzasadnienia z przykładem z treści (cytuj fragment, który podbija ocenę).

### 3. Werdykt pasmowy
Reguła agregacji jest mechaniczna:
- jakikolwiek czynnik KRYTYCZNY -> **STOP**,
- brak KRYTYCZNYCH, co najmniej jeden UWAGA -> **CAUTION**,
- wszystkie CZYSTE -> **SAFE**.
Czynnik (c) strategia procesowa oceniony na UWAGA lub wyżej podnosi werdykt
do STOP, bo redakcja go nie leczy (patrz opis czynnika).

### 4. Ocena skutków ujawnienia
Dla werdyktu CAUTION i STOP: dwa-trzy zdania, co konkretnie się stanie, jeśli treść
wypłynie - wobec klienta (utrata zaufania, szkoda w sprawie), wobec prawnika
(dyscyplinarka, odpowiedzialność odszkodowawcza), wobec osób trzecich (roszczenia
z RODO). Bez straszenia na zapas - realistyczny scenariusz.

### 5. Redakcja - draft (tylko CAUTION)
Przygotuj wersję zredagowaną promptu: pseudonimizacja podmiotów i wartości
placeholderami [KLIENT], [KONTRAHENT], [OSOBA-1], [KWOTA], [DATA], [MIEJSCE],
[SYGNATURA]; usunięcie fragmentów zbędnych dla celu promptu (najtańsza redakcja
to wycięcie); sprawdzenie mozaiki PO redakcji - czy kombinacja pozostałych
elementów nadal wskazuje klienta. Przy STOP draftu nie rób - zredagowany prompt
strategii procesowej to nadal strategia procesowa.

### 6. Alternatywy (przy STOP)
Zawsze wskaż drogę wyjścia, nie tylko zakaz:
- środowisko lokalne zero-cloud (klasa rozwiązań typu PATRON - dane nie opuszczają
  maszyny kancelarii),
- model lokalny na sprzęcie kancelarii,
- przeformułowanie pytania na abstrakcyjne (pytanie o przepis zamiast o sprawę),
- wykonanie zadania bez AI, jeśli stawka tego wymaga.

### 7. Bramka człowieka
Prezentacja wyniku i zatrzymanie. Patrz sekcja "Bramka człowieka".

## Format wyniku (dosłowny szablon)

```
## Preflight tajemnicy - <robocza nazwa promptu>

Cel promptu: <po co użytkownik chce to wysłać>
Narzędzie docelowe: <nazwa + plan darmowy czy biznesowy, lub "nieznane - przyjęto wariant najgorszy">

| Czynnik                              | Ocena     | Uzasadnienie (fragment treści)        |
|--------------------------------------|-----------|---------------------------------------|
| (a) Identyfikowalność klienta        | UWAGA     | nazwa spółki + miasto + branża        |
| (b) Fakty objęte tajemnicą           | UWAGA     | przebieg negocjacji z kontrahentem    |
| (c) Strategia / work-product         | CZYSTY    | brak oceny taktycznej w treści        |
| (d) Dane osób trzecich               | UWAGA     | imię i nazwisko świadka               |
| (e) Warunki dostawcy                 | KRYTYCZNY | plan darmowy, trening na danych       |

WERDYKT: STOP

Skutki ujawnienia: <2-3 zdania realistycznego scenariusza>

Rekomendacja: <przy STOP - alternatywy; przy CAUTION - draft niżej; przy SAFE - można wysłać>

--- WERSJA ZREDAGOWANA (draft, tylko CAUTION - wymaga zatwierdzenia człowieka) ---
<treść z placeholderami [KLIENT], [KWOTA], [DATA]...>
--- KONIEC DRAFTU ---

Kontrola mozaiki po redakcji: <przeszła / nie przeszła + dlaczego>
Decyzja należy do człowieka. Skill niczego nie wysłał.
```

## Bramka człowieka

Wynik skilla to projekt, nie decyzja. Obowiązuje w całości bramka z fundamentu
weryfikacyjnego: nic nie zostaje wysłane, zanim uprawniony człowiek nie przeczyta
werdyktu, tabeli czynników i - przy CAUTION - całego draftu redakcji, linia po
linii. Człowiek zatwierdza, poprawia albo odrzuca; wysyła zawsze sam, własnym
działaniem, poza tym skillem.

Granica governance jest twarda: skill przygotowuje, człowiek wykonuje. Dotyczy to
także redakcji - placeholder wstawiony automatycznie może minąć się z kontekstem
(np. [KWOTA] w cytacie z umowy, gdzie kwota jest przedmiotem pytania). Dlatego
draft bez ludzkiej lektury jest bezwartościowy i nie wolno go traktować jako
"już zanonimizowany".

Pasmo SAFE też przechodzi przez bramkę: człowiek widzi tabelę czynników i sam
naciska Enter. SAFE skraca namysł, nie zdejmuje odpowiedzialności.

## Companion skills

- `matematic-prompt-defense-pl` - odporność system promptu na ataki; preflight
  patrzy na to, co wychodzi Z kancelarii, prompt-defense na to, co może zaatakować
  jej własne AI. Dwie strony tej samej higieny.
- `rodo-dpia-pl` - ocena skutków dla ochrony danych przy WDROŻENIU narzędzia AI
  jako procesu; preflight to kontrola jednostkowa. Jeśli preflight regularnie
  kończy się na CAUTION/STOP dla tego samego narzędzia - to sygnał, że potrzebna
  jest DPIA i decyzja systemowa, nie kolejne redakcje.
- `doc-intel-contract-pl` - gdy treść pochodzi z dokumentu: ekstrakcja z
  confidence-gatingiem i kandydatami do redakcji (PII z checksumami) daje
  preflightowi lepszy materiał wejściowy niż surowe kopiuj-wklej.
- `legal-request-router-pl` - routing zadania prawnego; preflight może być jego
  pierwszym przystankiem, zanim router w ogóle zdecyduje o ścieżce.
