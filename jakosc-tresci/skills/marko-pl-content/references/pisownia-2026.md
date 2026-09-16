# Pisownia od 1 stycznia 2026 r. - ściąga dla recenzenta

Od 1 stycznia 2026 r. jedynym ważnym źródłem zasad pisowni jest dokument Rady Języka Polskiego „Zasady pisowni i interpunkcji polskiej”. Zmiany ogłosił komunikat RJP z 10 maja 2024 r., zmieniony 7 listopada 2025 r. Ta ściąga streszcza je własnymi słowami. W razie wątpliwości rozstrzyga źródło, nie ściąga.

Źródła:

- Komunikat RJP z pełnym wykazem zmian (serwis PWN): https://sjp.pwn.pl/zasady/komunikat-rady-jezyka-polskiego-w-sprawie-zmian-w-ortografii-od-stycznia-2026-r;3866473.html
- Strona Rady Języka Polskiego: https://rjp.pan.pl/

## Dlaczego recenzent tego pilnuje

To nie są literówki. Model językowy uczył się na tekstach sprzed reformy i pisze po staremu, a korektor pisowni oparty na starym słowniku uznaje starą formę za poprawną. Błąd przechodzi więc przez obie kontrole, także w tekstach pisanych już po wejściu reformy.

## Zmiany, które skaner sprawdza

| Punkt | Co się zmieniło | Stara forma (błąd) | Nowa forma |
|---|---|---|---|
| 4 | „nie” z imiesłowem odmiennym zawsze łącznie, bez względu na znaczenie | nie sprawdzony w bazie | niesprawdzony w bazie |
| 11 | „nie” z przymiotnikiem i przysłówkiem odprzymiotnikowym łącznie, także w stopniu wyższym i najwyższym | nie najlepsza pora | nienajlepsza pora |
| 3 | cząstka „by” ze spójnikiem rozdzielnie | czyby | czy by |
| 1 | mieszkańcy miast, dzielnic i wsi wielką literą | warszawianka | Warszawianka |
| 6 | „pół” łącznie w połączeniach typu żart i serio | pół żartem | półżartem |
| 9a | przedrostek łącznie z wyrazem pisanym małą literą, łącznik tylko przed wielką | post-walidacja | postwalidacja |
| 10 | „niby” i „quasi” łącznie z wyrazem pisanym małą literą | quasi nauka | quasinauka |
| 8c | wyraz „aleja”, „plac”, „most”, „pomnik” itp. na początku nazwy wielką literą (ulica zostaje małą) | plac Zbawiciela | Plac Zbawiciela |
| 8e | wszystkie człony nazw nagród i orderów wielką literą | nagroda Nobla | Nagroda Nobla |

Punkt 8b (nazwy geograficzne) Rada wycofała 7 listopada 2025 r. - obowiązuje dawna zasada.

## Czego skaner nie sprawdza

- **pkt 2** - egzemplarz wyrobu marki wielką literą. Rozstrzyga znaczenie zdania.
- **pkt 5** - przymiotniki od nazw osobowych małą literą. Potrzebny słownik.
- **pkt 7** - pary wyrazów równorzędnych mają trzy dopuszczone zapisy, więc nie ma błędu do wykrycia.
- **pkt 8a i 8d** - nazwy komet i lokali usługowych.
- **pkt 9b** - dopuszczenie zapisu rozdzielnego przy „super”, „mini”, „eko” itp. To swoboda, nie błąd.

Brak zarzutu w tych punktach nie znaczy, że tekst jest poprawny. Znaczy tylko, że nikt tego nie zmierzył.

## Trzy pułapki - kiedy „nie” rozdzielnie jest poprawne

Skaner zwraca kandydatów. Większość z nich okazuje się poprawna. Każdego oceń w kontekście.

1. **Przeciwstawienie.** „Nie” pisze się rozdzielnie, gdy jednocześnie zaprzecza i przeciwstawia jedną cechę drugiej. Wyjątek zostaje w zasadach z 2026 r. Przykłady: „tanie, nie darmowe”, „to decyzja organizacyjna, nie techniczna”, „szkic, a nie zatwierdzony dokument”.
   - Uwaga: samo „ale” w zdaniu nie robi przeciwstawienia. „Wybór szybki, ale nieprzypadkowy” łączy dwie cechy, nie zamienia jednej na drugą - więc łącznie.
   - Wyliczenie cech też nie jest przeciwstawieniem: „bezterminowa, zbywalna, nieograniczona terytorialnie”.
2. **„To nie…”** - gdy „nie” zaprzecza całemu orzeczeniu, a nie przymiotnikowi: „przesunięty termin to nie przesunięta odpowiedzialność”.
3. **Zaimek, nie partykuła.** „Odpowiadam na nie szybciej niż zwykle” - tu „nie” znaczy „na te pytania”. Skaner pomija „nie” po przyimku, ale sprawdź w wątpliwych zdaniach.


## Znane ograniczenia skanera

- Rozpoznaje przymiotniki i imiesłowy po końcówce, nie po słowniku. Czasowniki i rzeczowniki o podobnej końcówce („pyta”, „zna”, „maszyny”) odsiewa lista wyjątków - na tekstach o innym słownictwie może przepuścić szum.
- Polskie złożenia z łącznikiem rozpoznaje po znaku diakrytycznym albo typowej końcówce. Przeoczy wyraz bez obu („mega-dokument”).
- Angielski tekst w pliku `.md` lub `.txt` bez oznaczenia języka jest skanowany. Plik HTML z `lang` innym niż polski jest pomijany i liczony w mianowniku.
