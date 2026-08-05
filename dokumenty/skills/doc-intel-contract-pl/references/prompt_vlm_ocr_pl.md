# Prompt-kontrakt VLM OCR (PL) - szablon

Wzorzec z datalab-to/chandra (Apache-2.0): layout nie jest osobna warstwa
detekcji - MODEL emituje HTML ograniczony allowlista, a atrybuty `data-*`
niosa layout. Ten szablon podajesz DOWOLNEMU VLM (Claude vision, lokalny
Qwen-VL, Gaius) razem z obrazem strony; wyjscie idzie prosto do:

```bash
python scripts/normalize.py --engine vlm-html strona.html
```

Roznice vs Chandra: etykiety = NASZA taksonomia kontraktu (w tym `signature`
i `stamp`, ktorych Chandra nie ma - potrzebne pod redakcje RODO), skala bbox
0-1000 bez zmian, po polsku, z twarda regula anty-halucynacyjna.

Obraz strony przygotuj wg `references/render_skanu_pl.md` (flatten + DPI).

## Szablon

Do modelu kopiujesz WYLACZNIE tekst miedzy znacznikami POCZATEK/KONIEC
(bez samych znacznikow), jeden obraz strony na wywolanie.

=== POCZATEK SZABLONU ===

Jestes silnikiem OCR z rozpoznawaniem ukladu strony. Przepisz DOKLADNIE
tresc strony z obrazu do HTML wedlug ponizszych regul. Zwroc WYLACZNIE HTML,
bez komentarzy i bez markdown.

STRUKTURA:
- Cala strona w jednym wrapperze: `<div data-page="{NUMER_STRONY}">...</div>`
- Kazdy blok layoutu jako osobny element:
  `<div data-label="ETYKIETA" data-bbox="x0 y0 x1 y1">tresc</div>`
- `data-bbox`: wspolrzedne lewego-gornego i prawego-dolnego rogu bloku
  w skali 0-1000 wzgledem szerokosci i wysokosci strony (int).
- Bloki w kolejnosci czytania (reading order), nie w kolejnosci wizualnej
  kolumn.

DOZWOLONE ETYKIETY (data-label) - dokladnie jedna na blok:
`title` (naglowek sekcji/tytul pisma), `paragraph` (akapit tekstu),
`table` (tabela/formularz), `list` (lista punktowana/numerowana),
`equation` (wzor), `signature` (podpis odreczny lub miejsce podpisu),
`stamp` (pieczatka/pieczec), `figure` (obraz/wykres/diagram),
`header` (naglowek strony), `footer` (stopka/numer strony),
`unknown` (nie pasuje do zadnej).

DOZWOLONE TAGI WEWNATRZ BLOKU:
`p, b, i, u, s, sub, sup, br, span, table, thead, tbody, tr, td, th, ul, ol, li`
- Tabele: struktura wiernie, scalenia komorek przez `colspan`/`rowspan`.
- Checkboxy w formularzach: `[x]` zaznaczony, `[ ]` pusty.
- Zadnych innych tagow ani atrybutow poza `data-page`, `data-label`,
  `data-bbox`, `colspan`, `rowspan`.

WIERNOSC (regula twarda):
- Przepisujesz TYLKO to, co widac na obrazie. Niczego nie uzupelniasz,
  nie poprawiasz i nie streszczasz.
- Zachowaj polskie znaki diakrytyczne, oryginalna pisownie, numeracje
  i sygnatury DOKLADNIE jak w dokumencie (takze bledy pisarskie).
- Fragment nieczytelny: wpisz doslownie `[nieczytelne]` - nie zgaduj.
- Pismo odreczne przepisz, a jesli to podpis - etykieta `signature`
  z trescia `[podpis odreczny]` plus odczytane imie/nazwisko, jesli czytelne.
- Pieczatki: etykieta `stamp`, tresc pieczatki przepisz.
- Pusta strona: `<div data-page="N"><div data-label="unknown"></div></div>`.

=== KONIEC SZABLONU ===

## Po stronie odbiorcy

- Kazdy blok dostaje `confidence=null` -> flaga `partial` -> CALY dokument
  trafia do `review_required` (Article III: generatywny OCR zawsze przez
  czlowieka).
- `normalize.py` dla `--engine vlm-html` odpala tez detektor zapetlenia
  generacji (`degeneracja.py`) - ogon powtorzen = flaga `degenerate_tail`
  na ostatnim bloku + ostrzezenie na stderr.
- Bloki `signature`/`stamp` leca do `redaction_candidates` przez
  `signature.py`/`pii_flags.py` jak z kazdego innego silnika.
