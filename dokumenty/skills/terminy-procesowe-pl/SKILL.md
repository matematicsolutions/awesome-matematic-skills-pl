---
name: terminy-procesowe-pl
description: >-
  Metodyka obliczania terminów procesowych i materialnych w prawie polskim -
  klasyfikuje termin (ustawowy / sądowy / instrukcyjny, procesowy / materialny),
  wylicza go krok po kroku wg reguł KC (art. 110-116) z podstawą prawną i tagiem
  pewności przy KAŻDYM kroku, sprawdza dni wolne, flaguje pułapki (ogłoszenie vs
  doręczenie, wniosek o uzasadnienie, tydzień vs 7 dni) i wystawia kartę terminu
  DO ZATWIERDZENIA PRZEZ CZŁOWIEKA. Nigdy nie podaje samej daty - zawsze pełne
  wyliczenie. Fail-closed: niepewna reguła = STOP i weryfikacja przepisu przez
  sejm-eli-mcp, nie założenie. Używaj gdy: "do kiedy apelacja", "policz termin",
  "kiedy mija termin", "termin na odpowiedź na pozew", "czy termin zachowany",
  "przywrócenie terminu", "od kiedy liczyć termin", "czy sobota przesuwa termin",
  kontrola terminu przed wpisem do kalendarza kancelarii.
license: Apache-2.0
allowed-tools: [Read]
data-residency: local
requires-human-approval: true
pii-egress: none
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.0.0
  inspiration: >-
    idea "litigation deadline calendar" z ekosystemu legal-AI (MIT);
    metodyka i treść PL napisane od zera
  companion_skills: sejm-eli-mcp (konektor), hierarchia-zrodel-pl, intake-sufficiency-pl, legal-request-router-pl
---

# Terminy procesowe PL - wyliczenie krok po kroku, nigdy sama data

## Filozofia

**Termin procesowy to najwyższa stawka operacyjna kancelarii.** Uchybienie terminowi
to nie "błąd merytoryczny do poprawienia" - to szkoda klienta i odpowiedzialność
pełnomocnika. Apelacja wniesiona dzień po terminie jest odrzucana bez badania racji.

Dlatego trzy zasady, bez wyjątków:

1. **Nigdy sama data.** Skill nie odpowiada "termin mija 14 lipca". Odpowiada pełnym
   wyliczeniem: zdarzenie startowe -> reguła z podstawą prawną -> każdy krok rachunku ->
   data końcowa DRAFT -> flagi ryzyka. Data bez wyliczenia jest nieweryfikowalna,
   a nieweryfikowalna data terminu jest bezużyteczna.
2. **Fail-closed.** Brak pewności co do reguły (numer przepisu, aktualne brzmienie,
   czy sobota przesuwa, czy termin biegnie od ogłoszenia czy doręczenia) = STOP
   i weryfikacja przepisu w aktualnym brzmieniu, nie założenie "chyba tak było".
   Niepewny numer przepisu dostaje tag `[DO SPRAWDZENIA]` i blokuje status karty.
3. **Bramka człowieka jest częścią metody, nie disclaimerem.** Wynik skilla to
   brudnopis wyliczenia dla pełnomocnika, który sam zatwierdza datę i sam wpisuje
   ją do kalendarza. Karta bez zatwierdzenia nie jest terminem.

## Kiedy używać / Czego NIE robi

**Używaj gdy:**
- trzeba policzyć termin na czynność procesową (apelacja, zażalenie, sprzeciw,
  odpowiedź na pozew, uzupełnienie braków) lub termin materialny (przedawnienie,
  zawity),
- trzeba ocenić, czy termin został zachowany (data nadania vs data wpływu),
- rozważane jest przywrócenie terminu (przesłanki + termin na wniosek),
- pełnomocnik chce niezależnego, rozpisanego rachunku do skonfrontowania z własnym.

**Czego NIE robi:**
- NIE jest źródłem terminu - nie zastępuje kalendarza kancelarii ani decyzji pełnomocnika,
- NIE wpisuje niczego do kalendarza i NIE wysyła przypomnień (akt na zewnątrz = człowiek),
- NIE rozstrzyga sporów o datę doręczenia (to kwestia dowodowa - flaguje, nie przesądza),
- NIE liczy terminów zagranicznych ani unijnych (inne reguły; poza zakresem),
- NIE zgaduje reguł dla postępowań odrębnych (KIO, sądowoadministracyjne) - sygnalizuje
  odrębność i wymusza weryfikację właściwego przepisu.

## Reguły obliczania - rdzeń metodyki

### 1. Klasyfikacja terminu (zawsze pierwszy krok)

| Oś | Warianty | Dlaczego to ważne |
|---|---|---|
| Źródło | **ustawowy** (z przepisu, niezmienialny przez sąd) / **sądowy** (wyznaczony przez sąd, może być przedłużony lub skrócony) / **instrukcyjny** (dla organu, uchybienie bez skutku procesowego dla strony) | inna sztywność, inna droga ratunku |
| Natura | **procesowy** (uchybienie = bezskuteczność czynności, ale możliwe przywrócenie) / **materialny** (upływ = wygaśnięcie lub przedawnienie prawa; przywrócenie co do zasady NIEDOPUSZCZALNE) | pomylenie osi = katastrofa; termin materialny liczy się często INACZEJ i nie ratuje go art. 168 KPC |

Jeżeli klasyfikacja jest niejednoznaczna (np. termin z ustawy szczególnej) - STOP,
weryfikacja przepisu i doktryny, tag `[DO SPRAWDZENIA]` na karcie.

### 2. Rachunek terminu - KPC odsyła do KC (art. 110-116 KC)

- **Termin w dniach:** nie wlicza się dnia, w którym nastąpiło zdarzenie startowe;
  termin kończy się z upływem ostatniego dnia (art. 111 KC).
- **Termin w tygodniach, miesiącach, latach:** koniec z upływem dnia, który nazwą
  (dzień tygodnia) lub datą odpowiada początkowemu dniowi terminu; gdyby takiego dnia
  w ostatnim miesiącu nie było - w ostatnim dniu tego miesiąca (art. 112 KC).
- **Koniec w sobotę lub dzień ustawowo wolny od pracy:** termin upływa następnego dnia,
  który nie jest dniem wolnym ani sobotą (art. 115 KC). Uwaga: przesunięcie dotyczy
  KOŃCA terminu, nie dni pośrednich - dni wolne w środku biegu liczą się normalnie.
- **Pułapka "tydzień vs 7 dni":** termin tygodniowy liczony wg art. 112 KC kończy się
  w dniu o tej samej nazwie (doręczenie we wtorek -> koniec we wtorek); termin "7 dni"
  liczony wg art. 111 KC daje ten sam wynik kalendarzowo, ale ustawy używają OBU
  konwencji - zawsze cytuj brzmienie przepisu, nie zamieniaj jednej na drugą w pamięci.

### 3. Zachowanie terminu

- Oddanie pisma w polskiej placówce pocztowej operatora wyznaczonego jest równoznaczne
  z wniesieniem do sądu (art. 165 KPC) - data stempla, nie data wpływu. Kurier ani
  paczkomat NIE korzystają z tego skutku. Zakres placówek zagranicznych/UE oraz
  aktualne brzmienie [DO SPRAWDZENIA na dzień użycia].
- **E-doręczenia i portal informacyjny sądu:** stan prawny zmienia się dynamicznie
  (etapowanie obowiązku, reguły doręczeń pełnomocnikom przez portal) -
  [DO SPRAWDZENIA na dzień użycia, dynamiczne zmiany]. Nie zakładaj reguły z pamięci.

### 4. Doręczenie jako start terminu

- Termin biegnie zwykle od DORĘCZENIA, nie od daty pisma ani nadania przez sąd.
- **Fikcje doręczenia:** podwójne awizo (7 + 7 dni; skutek doręczenia z upływem
  ostatniego dnia drugiego terminu odbioru), doręczenie dorosłemu domownikowi,
  odmowa przyjęcia. Numery i aktualne brzmienie przepisów o doręczeniach KPC oraz
  reguły doręczeń komorniczych dla pozwanych [DO SPRAWDZENIA na dzień użycia].
- Sporna data doręczenia = flaga ryzyka na karcie; do wyliczenia przyjmij wariant
  NAJWCZEŚNIEJSZY (ostrożnościowo) i pokaż wariant alternatywny.

### 5. Przywrócenie terminu (art. 168-172 KPC)

- Tylko termin PROCESOWY; przesłanka: brak winy strony w uchybieniu.
- Wniosek w terminie **tygodnia od ustania przyczyny uchybienia**, wraz z wnioskiem
  dokonuje się uchybionej czynności.
- **Roczna granica:** po upływie roku od uchybionego terminu przywrócenie tylko
  w wypadkach wyjątkowych.
- Przywrócenie NIE dotyczy terminów materialnych - jeśli klasyfikacja z kroku 1
  wskazuje termin materialny, ta droga jest zamknięta (flaga na karcie).

### 6. Odrębności innych procedur - sygnalizuj, nie zgaduj

- **KPA (art. 57-60 KPA):** reguły liczenia podobne do KC (dzień zdarzenia nie liczy
  się, sobota i dzień wolny przesuwają koniec), ale różnice w szczegółach (m.in.
  zachowanie terminu, doręczenia elektroniczne) - przy sprawie administracyjnej licz
  wg KPA, nie wg KC, i zweryfikuj brzmienie.
- **KIO (zamówienia publiczne):** terminy na odwołanie bardzo krótkie, liczone od
  różnych zdarzeń (przesłanie informacji, publikacja ogłoszenia), z własnymi regułami
  dni wolnych - [DO SPRAWDZENIA właściwy przepis ustawy PZP na dzień użycia].
- **Sądowoadministracyjne (PPSA):** własne przepisy o terminach i przywróceniu -
  [DO SPRAWDZENIA właściwe artykuły PPSA na dzień użycia].
- Skill sygnalizuje odrębność i wymusza weryfikację - nie przenosi reguł KPC/KC
  na te postępowania przez analogię.

### 7. Typowe pułapki (checklist przed wystawieniem karty)

- [ ] Termin liczony od OGŁOSZENIA czy od DORĘCZENIA? (różne przepisy, różne tryby)
- [ ] Czy czynność wymaga WCZEŚNIEJSZEGO wniosku o uzasadnienie jako warunku
      (apelacja po wniosku o doręczenie wyroku z uzasadnieniem - art. 328 KPC
      [DO SPRAWDZENIA brzmienia po nowelizacjach], w tym opłata od wniosku)?
- [ ] Tydzień czy 7 dni - jak brzmi przepis dosłownie?
- [ ] Procesowy czy materialny - czy przywrócenie w ogóle wchodzi w grę?
- [ ] Czy tryb doręczenia (portal / e-doręczenia / awizo) nie zmienia daty startowej?
- [ ] Czy koniec nie wypada w sobotę / dzień wolny (i czy dana procedura przesuwa)?

## Workflow

1. **Zbierz wejście** (przy brakach - dopytaj, nie zakładaj; wzorzec: intake-sufficiency-pl):
   zdarzenie startowe + jego data, tryb doręczenia (osobiste / awizo / portal /
   e-doręczenia), rodzaj pisma / czynności, procedura (KPC / KPA / PZP / PPSA / inna).
2. **Sklasyfikuj termin** wg dwóch osi z sekcji "Reguły" pkt 1. Niejednoznaczne = STOP.
3. **Zweryfikuj regułę w aktualnym brzmieniu przepisu** - obowiązkowo przez konektor
   `sejm-eli-mcp` (ISAP/ELI): przepis źródłowy terminu + przepisy o liczeniu + przepisy
   o doręczeniach. Dopiero po weryfikacji tag pewności może brzmieć "zweryfikowane".
   Konektor niedostępny = całość na tagach `[DO SPRAWDZENIA]` i obowiązkowa flaga na karcie.
4. **Wylicz z pokazaniem KAŻDEGO kroku** - dzień po dniu lub regułą art. 112 KC,
   z podstawą prawną przy każdym kroku rachunku.
5. **Sprawdź dni wolne** na końcu biegu terminu. Stałe święta ustawowe PL:
   1 stycznia, 6 stycznia, 1 maja, 3 maja, 15 sierpnia, 1 listopada, 11 listopada,
   24 grudnia [DO SPRAWDZENIA - dodane od 2025, potwierdź obowiązywanie], 25 grudnia,
   26 grudnia; niedziele są dniami ustawowo wolnymi. Święta RUCHOME (Wielkanoc
   z poniedziałkiem, Zielone Świątki, Boże Ciało) - daty [DO SPRAWDZENIA w danym roku].
6. **Wystaw kartę terminu** wg szablonu poniżej - status zawsze
   `DO ZATWIERDZENIA PRZEZ CZŁOWIEKA`.
7. **Bramka człowieka** - pełnomocnik weryfikuje rachunek, zatwierdza datę i SAM
   wpisuje ją do kalendarza kancelarii. Bez tego kroku karta nie istnieje operacyjnie.

## Format wyniku - karta terminu (szablon dosłowny)

```
KARTA TERMINU - DRAFT (brudnopis wyliczenia, nie źródło terminu)

Zdarzenie startowe : [np. doręczenie wyroku z uzasadnieniem]
Data zdarzenia     : [RRRR-MM-DD] (źródło daty: [EPO / zwrotka / portal / oświadczenie klienta])
Procedura          : [KPC / KPA / PZP-KIO / PPSA]
Klasyfikacja       : [ustawowy / sądowy / instrukcyjny] + [procesowy / materialny]

Reguła             : [treść reguły] (podstawa: [przepis]) [zweryfikowane przez sejm-eli-mcp RRRR-MM-DD / [DO SPRAWDZENIA]]

Wyliczenie:
  krok 1: dzień zdarzenia [data] nie wlicza się (art. 111 KC) [tag]
  krok 2: bieg od [data] ... [rachunek dzień po dniu albo reguła art. 112 KC] [tag]
  krok 3: koniec nominalny [data, dzień tygodnia] [tag]
  krok 4: kontrola sobota/dzień wolny: [wynik; jeśli przesunięcie - art. 115 KC] [tag]

DATA KOŃCOWA (DRAFT): RRRR-MM-DD, [dzień tygodnia]

Flagi ryzyka:
  - [np. sporna data doręczenia - przyjęto wariant najwcześniejszy; alternatywa: RRRR-MM-DD]
  - [np. warunek: uprzedni wniosek o uzasadnienie - sprawdzono / NIE sprawdzono]
  - [np. święto ruchome w biegu terminu - data potwierdzona / do potwierdzenia]

STATUS: DO ZATWIERDZENIA PRZEZ CZŁOWIEKA
Zatwierdził(a): __________________  Data: __________  Wpis do kalendarza: TAK / NIE
```

Karta bez wypełnionej sekcji "Wyliczenie" jest nieważna - sama data końcowa nigdy
nie wychodzi ze skilla bez rachunku.

## Bramka człowieka - granice skilla

**SKILL NIE JEST ŹRÓDŁEM TERMINU. JEST BRUDNOPISEM WYLICZENIA.**

Źródłem terminu jest pełnomocnik, który zweryfikował rachunek, zatwierdził datę
i wpisał ją do kalendarza kancelarii.

To skill najwyższej stawki, więc bramka jest rozbudowana:

- **Zatwierdzenie jest czynne, nie milczące.** Pełnomocnik przechodzi rachunek krok
  po kroku i potwierdza każdą podstawę prawną. Brak reakcji ≠ zatwierdzenie.
- **Każdy tag `[DO SPRAWDZENIA]` blokuje zatwierdzenie** do czasu weryfikacji przepisu
  w aktualnym brzmieniu. Karta z niedomkniętym tagiem nie nadaje się do kalendarza.
- **Wpis do kalendarza wykonuje człowiek.** Skill nie tworzy zdarzeń kalendarzowych,
  nie ustawia przypomnień, nie wysyła niczego - to akty na zewnątrz (granica
  governance MateMatic: tool przygotowuje draft, nie wykonuje).
- **Rozbieżność = eskalacja.** Jeśli rachunek pełnomocnika i karta dają różne daty,
  nie uśredniaj i nie wybieraj - rozstrzyga człowiek po powrocie do brzmienia przepisu.
- **Zasada ostrożności przy wariantach:** gdy dwie obronne interpretacje dają różne
  daty, do pracy operacyjnej proponuj WCZEŚNIEJSZĄ, a późniejszą pokazuj jako wariant.
- Wynik skilla nie jest poradą prawną i nie przenosi odpowiedzialności - ale to nie
  nota chroni przed błędem, tylko rachunek + tagi + ta bramka (warstwy 1-5 fundamentu
  weryfikacyjnego MateMatic).

## Companion skills

- **sejm-eli-mcp (konektor)** - obowiązkowa weryfikacja aktualnego brzmienia przepisu
  (krok 3 workflow); bez niego wszystko zostaje na tagach `[DO SPRAWDZENIA]`.
- **hierarchia-zrodel-pl** - gdy reguły terminu zderzają się między aktami (ustawa
  szczególna vs KPC/KC): która norma wygrywa.
- **intake-sufficiency-pl** - gdy wejście jest dziurawe (brak daty doręczenia, brak
  trybu doręczenia): jakie pytania zadać zanim zaczniesz liczyć.
- **legal-request-router-pl** - triage na wejściu; wyliczenie terminu klasyfikuj
  zawsze jako high-stakes.

## Weryfikacja źródeł

- Przepisy przywołane w tym skillu opisują STAN METODYKI, nie zwalniają z weryfikacji:
  przy każdym użyciu brzmienie przepisu sprawdzane jest przez `sejm-eli-mcp` na dzień
  wyliczenia. Prawo o doręczeniach i e-doręczeniach zmienia się szybciej niż ten plik.
- Tagi pewności wg fundamentu weryfikacyjnego: **zweryfikowane** (przepis sprawdzony
  w sesji, z datą weryfikacji) / **[DO SPRAWDZENIA]** (prawdopodobne, niezweryfikowane -
  blokuje zatwierdzenie karty) / **nie używać** (numeru niepewnego nie wolno w ogóle
  wpisać na kartę - zamiast numeru wpisz opis przepisu z tagiem [DO SPRAWDZENIA]).
- Kalendarz świąt: stałe święta z ustawy o dniach wolnych od pracy, ruchome liczone
  dla konkretnego roku - zawsze potwierdzone przed zatwierdzeniem karty.
- Skill działa lokalnie na danych sprawy (RODO-safe); jedyny ruch na zewnątrz to
  odpytanie publicznych źródeł prawa (ISAP/ELI) o treść przepisów.
