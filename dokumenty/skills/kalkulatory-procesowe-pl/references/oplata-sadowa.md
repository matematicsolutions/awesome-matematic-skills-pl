# Kalkulator 1: opłata sądowa (UKSC)

Ustawa z 28 lipca 2005 r. o kosztach sądowych w sprawach cywilnych
(Dz.U. 2005 nr 167 poz. 1398, tekst jednolity; dalej UKSC). Ustawa ma za
sobą ponad sto aktów zmieniających - to najczęściej nowelizowany akt z
czterech obsługiwanych przez ten skill. Bez pobrania aktualnego tekstu
nie licz.

## Aktualne parametry - POBIERZ przed obliczeniem

| Parametr | Skąd żywa wartość | Fallback (zweryfikowano 2026-07-13) |
|---|---|---|
| tekst UKSC (art. 13-19, opłaty stałe, zwolnienia) | konektor `sejm-eli-mcp` albo `https://api.sejm.gov.pl/eli/acts/DU/2005/1398` (metadane + tekst) | tabele niżej |
| widełki art. 13 ust. 1 | jw. | 30-1000 zł (tabela niżej) |
| opłata stosunkowa art. 13 ust. 2 | jw. | 5% WPS, nie więcej niż **100 000 zł** (od 23.09.2025; wcześniej 200 000 zł) |
| minimum opłaty | jw. | 30 zł (art. 20 ust. 1 UKSC) |

Nie możesz pobrać = licz na fallbacku i oznacz wynik:
`[PARAMETRY Z DNIA 2026-07-13 - zweryfikuj przed użyciem]`.

**Pułapka świeżej noweli:** ustawą z 25 lipca 2025 r. (Dz.U. 2025 poz. 1157,
wejście w życie 23.09.2025) obniżono górną granicę opłaty stosunkowej
z 200 000 zł do 100 000 zł. Do pism wniesionych PRZED 23.09.2025 stosuje
się limit stary (przepis przejściowy) - przy rachunku wstecznym data
wniesienia pisma decyduje o limicie i idzie do flag ryzyka.

## Trzy rodzaje opłat (art. 11-14 UKSC)

- **stała** - kwota z przepisu dla danego rodzaju sprawy (art. 12),
- **stosunkowa** - w sprawach o prawa majątkowe, liczona od WPS (art. 13),
- **podstawowa** - 30 zł, gdy przepis nie przewiduje innej (art. 14).

Przy prawach majątkowych najpierw ustal WPS ([wps.md](wps.md)), potem wróć tu.

## Opłata w sprawach o prawa majątkowe (art. 13)

WPS do 20 000 zł - opłata stała według widełek (art. 13 ust. 1):

| WPS | Opłata |
|---|---|
| do 500 zł | 30 zł |
| 500 - 1500 zł | 100 zł |
| 1500 - 4000 zł | 200 zł |
| 4000 - 7500 zł | 400 zł |
| 7500 - 10 000 zł | 500 zł |
| 10 000 - 15 000 zł | 750 zł |
| 15 000 - 20 000 zł | 1000 zł |

WPS ponad 20 000 zł - opłata stosunkowa 5% WPS, nie więcej niż 100 000 zł
(art. 13 ust. 2, limit od 23.09.2025).

Kategorie z własnymi regułami - zawsze sprawdź w pobranym tekście, zanim
zastosujesz art. 13: roszczenia z czynności bankowych konsumenta
(art. 13a), inne art. 13b-13e dodawane nowelami [DO SPRAWDZENIA na dzień
użycia - lista tych wyjątków rośnie].

Końcówkę opłaty zaokrągla się W GÓRĘ do pełnego złotego (art. 21 UKSC).

## Ułamki opłaty (art. 19 UKSC) - najczęstsze modyfikatory

| Pismo | Ułamek | Podstawa |
|---|---|---|
| pozew w elektronicznym postępowaniu upominawczym (EPU) | 1/4 opłaty [DO SPRAWDZENIA brzmienie art. 19 ust. 2 na dzień użycia] | art. 19 ust. 2 |
| zarzuty od nakazu zapłaty w postępowaniu nakazowym | 3/4 opłaty | art. 19 ust. 4 |
| zażalenie | 1/5 opłaty, chyba że przepis szczególny stanowi inaczej | art. 19 ust. 3 pkt 2 |
| apelacja | opłata jak od pozwu (liczona od wartości przedmiotu zaskarżenia) | art. 18 ust. 2 |
| wniosek o uzasadnienie | 100 zł, zaliczana na opłatę od środka zaskarżenia | art. 25b |

Sprzeciw od nakazu zapłaty w postępowaniu upominawczym nie podlega opłacie -
pozwany wnosi go bez kosztów (opłatę poniósł powód od pozwu); przy piśmie
pozwanego w trybie nakazowym wróć do wiersza "zarzuty" wyżej.

## Wybrane opłaty stałe (orientacyjnie - potwierdź w pobranym tekście)

| Sprawa | Opłata | Podstawa |
|---|---|---|
| rozwód, separacja | 600 zł | art. 26 ust. 1 |
| naruszenie posiadania | 200 zł | art. 27 |
| stwierdzenie nabycia spadku | 100 zł | art. 49 |
| dział spadku | 500 zł (300 zł przy zgodnym projekcie) | art. 51 |
| zniesienie współwłasności | 1000 zł (300 zł przy zgodnym projekcie) | art. 41 |
| wpis własności do księgi wieczystej | 200 zł (150 zł przy dziedziczeniu) | art. 42-44 |

Tabela celowo krótka - pełny katalog opłat stałych to kilkadziesiąt
artykułów UKSC i zmienia się nowelami. Sprawy spoza tabeli: pobierz tekst
i znajdź właściwy przepis, nie zgaduj z pamięci.

## Zwolnienia i zwroty - sprawdź zanim policzysz

- **Zwolnienia ustawowe (art. 94-96):** m.in. strona dochodząca alimentów,
  pracownik w sprawach z zakresu prawa pracy w granicach progu WPS
  (art. 35 - próg i mechanika [DO SPRAWDZENIA na dzień użycia]),
  konsument w niektórych kategoriach z art. 13a i nast.
- **Zwolnienie na wniosek (art. 102):** oświadczenie o stanie rodzinnym,
  majątku i dochodach; skill może przygotować draft wniosku, decyzja
  i podpis należą do człowieka.
- **Zwrot opłaty (art. 79-82):** m.in. całość przy cofnięciu pozwu przed
  wysłaniem odpisu pozwanemu, część przy ugodzie - wysokości ułamków
  [DO SPRAWDZENIA na dzień użycia].

## Workflow

1. Ustal rodzaj pisma i tryb postępowania (zwykłe / uproszczone / nakazowe /
   upominawcze / EPU / nieprocesowe).
2. Sprawdź zwolnienia ustawowe - zwolnienie kończy rachunek.
3. Prawa majątkowe: weź WPS z [wps.md](wps.md). Prawa niemajątkowe /
   katalog opłat stałych: znajdź przepis szczególny.
4. Zastosuj art. 13 (widełki albo 5% z limitem) lub opłatę stałą.
5. Nałóż ułamek z art. 19, jeśli dotyczy.
6. Zaokrąglij końcówkę w górę do pełnego złotego (art. 21); pilnuj minimum
   30 zł (art. 20 ust. 1).
7. Wystaw kartę obliczenia (szablon w SKILL.md) - status DO ZATWIERDZENIA.

## Przykład rachunku

Pozew o zapłatę 48 250 zł, tryb zwykły, wniesiony w 2026 r., parametry
pobrane w dniu obliczenia:

```
krok 1: WPS = 48 250 zł, ponad 20 000 zł -> opłata stosunkowa (art. 13 ust. 2) [zweryfikowane]
krok 2: 5% x 48 250 zł = 2412,50 zł [zweryfikowane]
krok 3: limit 100 000 zł niedotknięty [zweryfikowane]
krok 4: zaokrąglenie w górę (art. 21) -> 2413 zł [zweryfikowane]
WYNIK (DRAFT): 2413 zł
```

## Typowe błędy (checklist przed wystawieniem karty)

- [ ] stary limit 200 000 zł po 23.09.2025 (albo nowy limit do pisma
      sprzed tej daty - decyduje data wniesienia pisma),
- [ ] widełki sprzed reformy z 2019 r. (7 progów wyżej to stan po niej),
- [ ] policzenie 5% dla WPS poniżej 20 000 zł zamiast widełek,
- [ ] pominięcie kategorii szczególnych art. 13a i nast.,
- [ ] zaokrąglenie w dół zamiast w górę (art. 21),
- [ ] pominięcie ułamka z art. 19 (zażalenie 1/5, zarzuty 3/4),
- [ ] pominięcie 100 zł od wniosku o uzasadnienie i jej zaliczenia na
      opłatę od apelacji (art. 25b),
- [ ] liczenie opłaty od kwoty z odsetkami, kosztami i pożytkami żądanymi
      obok roszczenia głównego (do WPS ich nie wlicza się - art. 20 KPC).
