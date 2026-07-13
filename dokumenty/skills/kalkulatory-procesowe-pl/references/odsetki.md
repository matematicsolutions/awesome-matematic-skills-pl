# Kalkulator 3: odsetki (KC + transakcje handlowe)

Trzy reżimy o różnych stopach i zakresach: odsetki kapitałowe (art. 359 KC),
odsetki za opóźnienie (art. 481 KC) i odsetki za opóźnienie w transakcjach
handlowych (ustawa z 8 marca 2013 r. o przeciwdziałaniu nadmiernym
opóźnieniom w transakcjach handlowych, Dz.U. 2013 poz. 403, tekst
jednolity; do 2019 r. "o terminach zapłaty w transakcjach handlowych").
Wszystkie trzy wiszą na stopie referencyjnej NBP - to parametr najbardziej
zmienny w całym skillu.

## Aktualne parametry - POBIERZ przed obliczeniem

| Parametr | Skąd żywa wartość | Fallback (zweryfikowano 2026-07-13) |
|---|---|---|
| stopa referencyjna NBP | `https://nbp.pl/polityka-pieniezna/decyzje-rpp/podstawowe-stopy-procentowe-nbp/` (strona bywa za bramką antybotową - wtedy komunikat RPP po ostatnim posiedzeniu albo serwisy stóp) | 3,75% (od marca 2026) |
| odsetki ustawowe kapitałowe = stopa ref. + 3,5 p.p. | obwieszczenie Ministra Sprawiedliwości w M.P. (art. 359 § 4 KC) | 7,25% |
| odsetki maksymalne kapitałowe = 2 x ustawowe | pochodna | 14,50% |
| odsetki ustawowe za opóźnienie = stopa ref. + 5,5 p.p. | obwieszczenie MS w M.P. (art. 481 § 2[4] KC) | 9,25% |
| odsetki maksymalne za opóźnienie = 2 x ustawowe za opóźnienie | pochodna | 18,50% |
| odsetki w transakcjach handlowych = stopa ref. z 1.01 / 1.07 + 10 p.p. (dłużnik publiczny leczniczy: + 8 p.p.) | obwieszczenie ministra właściwego ds. gospodarki w M.P. | II półrocze 2026: 13,75% / 11,75% [pochodna stopy 3,75% z 1.07.2026 - potwierdź obwieszczeniem] |
| kurs EUR do rekompensaty | tabela A NBP, `https://api.nbp.pl/api/exchangerates/rates/a/eur/{RRRR-MM-DD}/` | brak fallbacku - kurs zawsze pobierz |
| HISTORIA stóp dla okresów wstecznych | archiwum decyzji RPP / obwieszczeń w M.P. | brak - okres wsteczny wymaga pobrania historii |

Nie możesz pobrać = licz na fallbacku i oznacz wynik:
`[PARAMETRY Z DNIA 2026-07-13 - zweryfikuj przed użyciem]`. Rachunek za
okres, w którym stopa się zmieniała, bez pobranej historii stóp jest
niewykonalny - wtedy STOP, nie szacunek.

## Który reżim? (kolejność badania)

1. **Transakcja handlowa** (B2B lub z podmiotem publicznym, dostawa towaru
   albo świadczenie usługi za wynagrodzeniem) -> ustawa z 2013 r. jako
   lex specialis; art. 481 KC do wynagrodzenia z takiej transakcji nie
   stosuje się.
2. **Opóźnienie w zapłacie poza transakcją handlową** (konsument, delikt,
   kara umowna, zwrot świadczenia) -> art. 481 KC.
3. **Odsetki kapitałowe** (wynagrodzenie za korzystanie z kapitału: pożyczka,
   kredyt kupiecki, odroczenie) -> art. 359 KC; umowne nie mogą przekroczyć
   maksymalnych (art. 359 § 2[1]-2[2] KC: nadwyżka spada do maksymalnych).
4. **Strony umówiły stopę** - stosuj umowną w granicach maksymalnych
   (art. 359 § 2[2], art. 481 § 2[1]-2[2] KC).

## Mechanika rachunku

Wzór podstawowy (praktyka orzecznicza: rok = 365 dni):

```
odsetki = kwota x stopa roczna x liczba dni / 365
```

- **Podokresy:** stopa zmienia się w trakcie biegu = licz każdy podokres
  osobno według stopy z tego podokresu i sumuj. Nigdy jedna stopa na cały
  wieloletni okres.
- **Początek biegu (art. 481 § 1, art. 455 KC):** termin zapłaty z umowy ->
  od dnia następnego po terminie; zobowiązanie bezterminowe -> po wezwaniu
  do zapłaty (niezwłocznie); data sporna = flaga + wariant ostrożny.
- **Koniec:** dzień zapłaty (w żądaniu pozwu: "z odsetkami ... od dnia ...
  do dnia zapłaty").
- **Anatocyzm (art. 482 KC):** odsetek od zaległych odsetek nie wolno
  liczyć, poza wyjątkami (m.in. od chwili wytoczenia powództwa o nie).

## Rekompensata za koszty odzyskiwania (art. 10 ustawy z 2013 r.)

Tylko transakcje handlowe; należna obok odsetek, bez wezwania i bez dowodu
szkody:

| Kwota świadczenia pieniężnego | Rekompensata |
|---|---|
| do 5000 zł | 40 EUR |
| 5000 - 50 000 zł | 70 EUR |
| 50 000 zł i więcej | 100 EUR |

Przeliczenie: średni kurs EUR NBP z OSTATNIEGO DNIA ROBOCZEGO miesiąca
poprzedzającego miesiąc, w którym świadczenie stało się wymagalne.

## Workflow

1. Zbierz wejście: kwota główna, podstawa (umowa / faktura / wyrok), strony
   (B2B / B2C / podmiot publiczny), termin zapłaty albo data wezwania,
   data końcowa rachunku.
2. Rozstrzygnij reżim (kolejność badania wyżej) - wątpliwość co do
   kwalifikacji "transakcji handlowej" = flaga.
3. Pobierz stopy dla CAŁEGO okresu (protokół parametrów; okres wsteczny =
   historia zmian stóp).
4. Podziel na podokresy według zmian stopy i policz każdy wzorem.
5. Transakcja handlowa: dolicz rekompensatę 40/70/100 EUR po kursie
   z właściwego dnia.
6. Wystaw kartę obliczenia (szablon w SKILL.md) - status DO ZATWIERDZENIA.

## Przykład rachunku

Faktura B2C 10 000 zł, opóźnienie od 1 kwietnia do 30 czerwca 2026 r.
(91 dni, stopa bez zmian w tym okresie), parametry pobrane w dniu
obliczenia:

```
krok 1: poza transakcją handlową (konsument) -> art. 481 § 2 KC [zweryfikowane]
krok 2: stopa 9,25% (ref. 3,75% + 5,5 p.p.), bez zmian 1.04-30.06.2026 [zweryfikowane]
krok 3: 10 000 zł x 9,25% x 91 / 365 = 230,62 zł [zweryfikowane]
WYNIK (DRAFT): 230,62 zł odsetek ustawowych za opóźnienie
```

## Typowe błędy (checklist przed wystawieniem karty)

- [ ] art. 481 KC zastosowany do wynagrodzenia z transakcji handlowej
      (należało: ustawa z 2013 r., wyższa stopa),
- [ ] stopa transakcji handlowych policzona jako "+ 8 p.p." dla zwykłego
      dłużnika (od 2020 r. + 10 p.p.; + 8 tylko dłużnik publiczny
      leczniczy),
- [ ] jedna stopa na okres obejmujący zmianę stóp (brak podokresów),
- [ ] pominięta rekompensata 40/70/100 EUR albo kurs z niewłaściwego dnia,
- [ ] odsetki kapitałowe pomylone z odsetkami za opóźnienie (różne stopy:
      +3,5 vs +5,5 p.p.),
- [ ] przekroczenie odsetek maksymalnych przy stopie umownej,
- [ ] bieg liczony od daty faktury zamiast od dnia po terminie zapłaty
      (albo bez wezwania przy zobowiązaniu bezterminowym),
- [ ] odsetki od odsetek poza wyjątkami z art. 482 KC.
