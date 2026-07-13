# Kalkulator 2: przedawnienie roszczeń (art. 117-125 KC)

Kodeks cywilny (Dz.U. 1964 nr 16 poz. 93, tekst jednolity), tytuł VI
księgi pierwszej. Reguły ogólne zmieniła gruntownie nowela z 13 kwietnia
2018 r. (Dz.U. 2018 poz. 1104, wejście w życie 9.07.2018), a mechanikę
przerwania - nowela z 2 grudnia 2021 r. (Dz.U. 2021 poz. 2459, wejście
w życie 30.06.2022): mediacja i zawezwanie do próby ugodowej ZAWIESZAJĄ,
już nie przerywają.

## Aktualne parametry - POBIERZ przed obliczeniem

| Parametr | Skąd żywa wartość | Fallback (zweryfikowano 2026-07-13) |
|---|---|---|
| tekst art. 117-125 KC | konektor `sejm-eli-mcp` albo `https://api.sejm.gov.pl/eli/acts/DU/1964/93` | reguły niżej |
| termin szczególny dla danego typu roszczenia | przepis szczególny KC / ustawy odrębnej (pobierz tekst) | tabela orientacyjna niżej |

Nie możesz pobrać = licz na fallbacku i oznacz wynik:
`[PARAMETRY Z DNIA 2026-07-13 - zweryfikuj przed użyciem]`.

## Terminy ogólne (art. 118 KC)

| Roszczenie | Termin |
|---|---|
| ogólny (brak przepisu szczególnego) | 6 lat |
| o świadczenia okresowe (czynsz, odsetki, renta) | 3 lata |
| związane z prowadzeniem działalności gospodarczej | 3 lata |
| stwierdzone prawomocnym orzeczeniem lub ugodą (art. 125 § 1) | 6 lat; objęte orzeczeniem świadczenia okresowe należne w przyszłości - 3 lata |

**Reguła końca roku (art. 118 zd. 2):** koniec terminu przedawnienia
przypada na OSTATNI DZIEŃ ROKU KALENDARZOWEGO, chyba że termin jest
krótszy niż dwa lata. Terminy roczne i krótsze kończą się w dacie
wyliczonej normalnie, bez przedłużenia.

## Terminy szczególne (orientacyjnie - zawsze potwierdź przepis)

| Roszczenie | Termin | Podstawa |
|---|---|---|
| delikt | 3 lata od dowiedzenia się o szkodzie i osobie zobowiązanej, nie dłużej niż 10 lat od zdarzenia | art. 442[1] § 1 KC |
| szkoda ze zbrodni lub występku | 20 lat od dnia popełnienia | art. 442[1] § 2 KC |
| szkoda na osobie | 3 lata od dowiedzenia się, bez górnej granicy 10 lat | art. 442[1] § 3 KC |
| sprzedaż w zakresie działalności przedsiębiorstwa | 2 lata | art. 554 KC |
| umowa o dzieło | 2 lata od oddania dzieła | art. 646 KC |
| zlecenie (wybrane roszczenia) | 2 lata | art. 751 KC |
| umowa przewozu / spedycji | 1 rok | art. 778 / 803 KC |
| umowa ubezpieczenia | 3 lata | art. 819 KC |
| roszczenia pracownicze | 3 lata od wymagalności | art. 291 KP |

Tabela to mapa, nie wyrocznia - przed werdyktem pobierz przepis szczególny
i potwierdź brzmienie. Roszczenia nieprzedawnialne (m.in. windykacyjne
z nieruchomości - art. 223 KC, zniesienie współwłasności - art. 220 KC)
w ogóle nie wchodzą do rachunku.

## Mechanika rachunku

1. **Początek biegu (art. 120 § 1):** dzień wymagalności roszczenia;
   gdy wymagalność zależy od czynności wierzyciela - dzień, w którym
   roszczenie stałoby się wymagalne, gdyby wierzyciel podjął czynność
   w najwcześniejszym możliwym terminie.
2. **Długość terminu:** przepis szczególny przed ogólnym (tabele wyżej).
3. **Zawieszenie (art. 121 KC):** bieg nie rozpoczyna się / ulega
   zawieszeniu m.in. na czas siły wyższej (pkt 4), MEDIACJI (pkt 5)
   i postępowania pojednawczego (pkt 6) - dwa ostatnie od 30.06.2022.
   Po ustaniu przeszkody bieg toczy się dalej, nie od nowa.
4. **Przerwanie (art. 123 § 1):** czynność przed sądem lub innym organem
   przedsięwzięta bezpośrednio w celu dochodzenia, ustalenia, zaspokojenia
   lub zabezpieczenia roszczenia (pkt 1) oraz uznanie roszczenia przez
   dłużnika (pkt 2), także niewłaściwe (częściowa zapłata, prośba
   o rozłożenie na raty). Po przerwaniu biegnie OD NOWA (art. 124),
   przy czym w toku postępowania nie biegnie do jego zakończenia.
5. **Koniec:** zastosuj regułę końca roku (art. 118 zd. 2) dla terminów
   dwuletnich i dłuższych.
6. **Skutek (art. 117 § 2):** dłużnik może uchylić się od zaspokojenia -
   przedawnienie działa na ZARZUT. Wyjątek: przeciwko KONSUMENTOWI po
   upływie terminu nie można domagać się zaspokojenia z mocy prawa
   (art. 117 § 2[1]), a sąd bada to z urzędu; w wyjątkowych wypadkach może
   jednak zarzut pominąć po rozważeniu interesów stron (art. 117[1]).

## Workflow

1. Zbierz wejście: typ roszczenia, kto przeciw komu (B2B / B2C / C2C),
   data wymagalności (sporna = flaga + wariant ostrożny), zdarzenia
   przerywające i zawieszające z datami.
2. Dobierz termin (przepis szczególny > ogólny) - pobierz i potwierdź
   brzmienie przepisu.
3. Policz krok po kroku: start -> zawieszenia -> przerwania (bieg od nowa)
   -> koniec nominalny -> reguła końca roku.
4. Sprawdź reżim intertemporalny, jeśli roszczenie powstało przed
   9.07.2018 (art. 5 noweli z 2018 r. - stare 10 lat kontra nowe 6 lat)
   [DO SPRAWDZENIA na dzień użycia przy starych roszczeniach].
5. Wystaw kartę obliczenia z werdyktem trzystopniowym:
   **NIEPRZEDAWNIONE** (termin biegnie) / **PRZEDAWNIONE** (termin upłynął;
   pamiętaj o trybie zarzutu vs z urzędu) / **GRANICZNE** (upływ w ciągu
   6 miesięcy albo sporna data startu - flaga eskalacji).

## Przykład rachunku

Faktura B2B wymagalna 10 maja 2019 r., bez przerwań i zawieszeń,
parametry pobrane w dniu obliczenia:

```
krok 1: start biegu 10.05.2019 (art. 120 § 1 KC) [zweryfikowane]
krok 2: roszczenie z działalności gospodarczej -> 3 lata (art. 118 KC) [zweryfikowane]
krok 3: koniec nominalny 10.05.2022 [zweryfikowane]
krok 4: reguła końca roku (art. 118 zd. 2) -> 31.12.2022 [zweryfikowane]
WYNIK (DRAFT): PRZEDAWNIONE z końcem 31.12.2022; B2B = działa na zarzut
               dłużnika (art. 117 § 2 KC), nie z urzędu
```

## Typowe błędy (checklist przed wystawieniem karty)

- [ ] stare 10 lat zamiast 6 po 9.07.2018 (albo pominięty reżim
      intertemporalny dla roszczeń sprzed noweli),
- [ ] pominięta reguła końca roku - albo zastosowana do terminu krótszego
      niż 2 lata,
- [ ] mediacja / zawezwanie do próby ugodowej policzone jako PRZERWANIE
      (od 30.06.2022 to zawieszenie - art. 121 pkt 5-6 KC),
- [ ] wezwanie do zapłaty potraktowane jako przerwanie biegu (nie przerywa;
      przerywa uznanie przez dłużnika albo czynność przed organem),
- [ ] pomylenie osi "związane z działalnością" (liczy się działalność
      WIERZYCIELA dochodzącego roszczenia, nie status dłużnika),
- [ ] pominięcie badania z urzędu przeciwko konsumentowi
      (art. 117 § 2[1] KC),
- [ ] termin szczególny przykryty ogólnym (np. dzieło 2 lata, przewóz rok),
- [ ] pomylenie zawieszenia (bieg dalej) z przerwaniem (bieg od nowa).
