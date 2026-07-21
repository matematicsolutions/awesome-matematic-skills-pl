# Wzorce specyfikacji konceptow dla typowych dokumentow prawnych

Gotowe do skopiowania specyfikacje `--concepts` dla `ekstrakcja_llm.py`. Dostosuj `description`
do konkretnego dokumentu - im precyzyjniejszy opis, tym lepsza ekstrakcja (zwlaszcza na
slabszych modelach lokalnych).

## Umowa (B2B / uslugi)

```json
{
  "concepts": [
    {"name": "Strony umowy", "description": "Nazwy i formy prawne stron umowy", "type": "string", "reference_depth": "sentences"},
    {"name": "Przedmiot umowy", "description": "Co jest przedmiotem swiadczenia", "type": "string", "reference_depth": "sentences"},
    {"name": "Wynagrodzenie", "description": "Kwota i sposob obliczenia wynagrodzenia", "type": "string", "reference_depth": "sentences"},
    {"name": "Termin platnosci (dni)", "description": "Liczba dni na platnosc od doreczenia faktury", "type": "numeric", "numeric_type": "int", "reference_depth": "sentences"},
    {"name": "Kara umowna", "description": "Postanowienie o karze umownej za niewykonanie/opoznienie i jej stawka", "type": "string", "reference_depth": "sentences", "justifications": true},
    {"name": "Okres wypowiedzenia", "description": "Termin i tryb wypowiedzenia umowy", "type": "string", "reference_depth": "sentences"},
    {"name": "Klauzula poufnosci obecna", "description": "Czy umowa zawiera postanowienia o poufnosci/NDA", "type": "boolean"},
    {"name": "Sad wlasciwy", "description": "Wskazany sad wlasciwy lub zapis na sad polubowny", "type": "string", "reference_depth": "sentences"},
    {"name": "Prawo wlasciwe", "description": "Wskazane prawo wlasciwe dla umowy", "type": "string", "reference_depth": "sentences"}
  ]
}
```

## Wyrok / orzeczenie

```json
{
  "concepts": [
    {"name": "Sygnatura", "description": "Sygnatura akt sprawy", "type": "string", "reference_depth": "sentences"},
    {"name": "Sad orzekajacy", "description": "Nazwa sadu wydajacego orzeczenie", "type": "string", "reference_depth": "sentences"},
    {"name": "Rozstrzygniecie", "description": "Sentencja - jak sad rozstrzygnal sprawe", "type": "string", "reference_depth": "sentences", "justifications": true},
    {"name": "Podstawa prawna", "description": "Przepisy powolane jako podstawa rozstrzygniecia", "type": "string", "reference_depth": "sentences"},
    {"name": "Teza", "description": "Glowna teza/holding orzeczenia", "type": "string", "reference_depth": "sentences", "justifications": true}
  ]
}
```

## Pismo procesowe

```json
{
  "concepts": [
    {"name": "Rodzaj pisma", "description": "Typ pisma procesowego (pozew, apelacja, zazalenie itd.)", "type": "string", "reference_depth": "paragraphs"},
    {"name": "Zadanie", "description": "Czego domaga sie strona (petitum)", "type": "string", "reference_depth": "sentences", "justifications": true},
    {"name": "Zarzuty", "description": "Podniesione zarzuty", "type": "string", "reference_depth": "sentences"},
    {"name": "Wartosc przedmiotu sporu", "description": "WPS jesli podana", "type": "string", "reference_depth": "sentences"},
    {"name": "Termin obecny", "description": "Czy pismo powoluje sie na termin/prekluzje", "type": "boolean"}
  ]
}
```

## Wskazowki

- **Grounding depth:** `sentences` dla precyzyjnych pol (kara, termin), `paragraphs` dla szerokich (rodzaj pisma).
- **justifications:** wlacz dla pol spornych/interpretacyjnych (teza, rozstrzygniecie), pomin dla oczywistych (sygnatura) - oszczedza tokeny i czas.
- **Slaby model lokalny:** trzymaj sie prostych typow (string/numeric), krotkie opisy, mniej konceptow na raz. Rozbij duzy zestaw na kilka biegow.
- **Zawsze** przepusc `refs` przez `citation-grounding-pl` przed uzyciem w pismie - LLM potrafi zakotwiczyc do zlego zdania.
