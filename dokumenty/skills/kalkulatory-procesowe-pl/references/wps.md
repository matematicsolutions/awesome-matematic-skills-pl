# Kalkulator 4: WPS - wartość przedmiotu sporu (art. 19-26 KPC)

Kodeks postępowania cywilnego (Dz.U. 1964 nr 43 poz. 296, tekst jednolity),
art. 19-26. WPS to rachunek pierwotny - od niego zależą właściwość rzeczowa
sądu, tryb postępowania, opłata sądowa ([oplata-sadowa.md](oplata-sadowa.md))
i stawki kosztów zastępstwa.

## Aktualne parametry - POBIERZ przed obliczeniem

| Parametr | Skąd żywa wartość | Fallback (zweryfikowano 2026-07-13) |
|---|---|---|
| tekst art. 19-26 KPC + art. 17 pkt 4 | konektor `sejm-eli-mcp` albo `https://api.sejm.gov.pl/eli/acts/DU/1964/296` | reguły niżej |
| próg właściwości sądu okręgowego | art. 17 pkt 4 KPC (pobierz brzmienie) | ponad 100 000 zł (od 1.07.2023; wcześniej 75 000 zł) |
| próg postępowania uproszczonego | art. 505[1] § 1 KPC | 20 000 zł |

Nie możesz pobrać = licz na fallbacku i oznacz wynik:
`[PARAMETRY Z DNIA 2026-07-13 - zweryfikuj przed użyciem]`.

## Reguły obliczania (art. 19-26 KPC)

- **Roszczenie pieniężne (art. 19 § 1):** WPS = podana kwota. W innych
  sprawach majątkowych powód sam oznacza WPS w pozwie (art. 19 § 2).
- **Czego NIE wlicza się (art. 20):** odsetek, pożytków i kosztów żądanych
  OBOK roszczenia głównego. Odsetki skapitalizowane i dochodzone JAKO
  roszczenie główne wchodzą do WPS - różnica leży w konstrukcji żądania.
- **Kumulacja roszczeń (art. 21):** kilka roszczeń w jednym pozwie =
  zlicza się ich wartość. Roszczenia ewentualne i alternatywne
  [DO SPRAWDZENIA na dzień użycia - praktyka: liczy się roszczenie
  o najwyższej wartości, nie suma].
- **Świadczenia powtarzające się (art. 22):** WPS = suma świadczeń za
  JEDEN ROK, a jeżeli trwają krócej - za cały czas trwania (klasyka:
  alimenty, renta).
- **Najem / dzierżawa (art. 23):** spór o istnienie, unieważnienie albo
  rozwiązanie umowy, o wydanie lub odebranie przedmiotu: czas oznaczony -
  suma czynszu za sporny okres, nie więcej niż za rok; czas NIEoznaczony -
  suma czynszu za TRZY miesiące.
- **Roszczenia pracownicze (art. 23[1]):** przy umowach na czas określony -
  suma wynagrodzenia za sporny okres, nie więcej niż za rok; na czas
  nieokreślony - za jeden rok [DO SPRAWDZENIA brzmienie na dzień użycia].
- **Zabezpieczenie, zastaw, hipoteka (art. 24):** wysokość wierzytelności;
  gdy przedmiot zabezpieczenia ma mniejszą wartość - decyduje ona
  [DO SPRAWDZENIA brzmienie na dzień użycia].
- **Zaokrąglenie (art. 126[1] § 3):** WPS podaje się w złotych,
  zaokrąglając W GÓRĘ do pełnego złotego.
- **Kontrola sądu (art. 25):** sąd może sprawdzić WPS przed doręczeniem
  pozwu; PO doręczeniu - tylko na zarzut pozwanego zgłoszony przed wdaniem
  się w spór co do istoty (art. 25 § 2). Po ustaleniu WPS nie podlega
  ponownemu badaniu w dalszym toku (art. 26).

## Co z WPS wynika (skutki rachunku)

| Skutek | Reguła | Podstawa |
|---|---|---|
| właściwość rzeczowa | ponad 100 000 zł -> sąd okręgowy | art. 17 pkt 4 KPC |
| tryb uproszczony | świadczenie do 20 000 zł | art. 505[1] § 1 KPC |
| opłata sądowa | widełki do 20 000 zł / 5% powyżej | art. 13 UKSC ([oplata-sadowa.md](oplata-sadowa.md)) |
| koszty zastępstwa | stawki wg przedziałów WPS | rozporządzenia MS [DO SPRAWDZENIA na dzień użycia] |

Właściwość ma własne wyjątki przedmiotowe (art. 17 pkt 1-3 i 4[1]-4[3]:
m.in. prawa niemajątkowe, prasowe, własność intelektualna niezależnie
od WPS) - przy sprawie z tych kategorii nie rozstrzygaj właściwości samym
WPS, pobierz katalog z art. 17.

## Workflow

1. Zbierz wejście: konstrukcja żądania (kwota główna, odsetki obok czy
   skapitalizowane w żądaniu głównym, liczba roszczeń), typ sprawy
   (świadczenie jednorazowe / powtarzające się / najem / pracownicza).
2. Dobierz regułę z art. 19-24 (przepis szczególny przed art. 19).
3. Zastosuj wyłączenia art. 20 - to najczęstszy błąd rachunku.
4. Zsumuj przy kumulacji (art. 21), zaokrąglij w górę (art. 126[1] § 3).
5. Wyprowadź skutki: właściwość, tryb, przełóż WPS na opłatę
   ([oplata-sadowa.md](oplata-sadowa.md)).
6. Wystaw kartę obliczenia (szablon w SKILL.md) - status DO ZATWIERDZENIA.

## Przykład rachunku

Pozew o alimenty 1500 zł miesięcznie, świadczenie na czas nieokreślony,
parametry pobrane w dniu obliczenia:

```
krok 1: świadczenie powtarzające się -> suma za jeden rok (art. 22 KPC) [zweryfikowane]
krok 2: 1500 zł x 12 = 18 000 zł [zweryfikowane]
krok 3: zaokrąglenie zbędne - pełne złote (art. 126[1] § 3 KPC) [zweryfikowane]
krok 4: skutki: do 100 000 zł -> sąd rejonowy (art. 17 pkt 4 KPC);
        powód w sprawie o alimenty zwolniony od kosztów
        (art. 96 ust. 1 pkt 2 UKSC) [zweryfikowane]
WYNIK (DRAFT): WPS = 18 000 zł
```

## Typowe błędy (checklist przed wystawieniem karty)

- [ ] odsetki żądane obok roszczenia głównego wliczone do WPS (art. 20 KPC),
- [ ] odsetki skapitalizowane w żądaniu głównym POMINIĘTE w WPS
      (lustrzany błąd poprzedniego),
- [ ] świadczenie powtarzające się policzone inaczej niż suma za rok
      (art. 22 KPC),
- [ ] najem na czas nieoznaczony policzony za 6 lub 12 miesięcy zamiast
      za trzy (art. 23 KPC),
- [ ] stary próg właściwości 75 000 zł zamiast 100 000 zł (zmiana od
      1.07.2023),
- [ ] roszczenia ewentualne zsumowane z głównym,
- [ ] zaokrąglenie w dół albo brak zaokrąglenia (art. 126[1] § 3 KPC),
- [ ] właściwość rozstrzygnięta samym WPS w sprawie z wyjątków
      przedmiotowych art. 17 KPC.
