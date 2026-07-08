# Drabinka źródeł UODO - gdy uodo.gov.pl zawiedzie (a zawiedzie często)

To centralna część tego skilla: serwis uodo.gov.pl jest wrogi botom - `/decyzje/` zwraca 500 dla
prostego fetcha, treść renderowana JS, TLS bywa niespójny. Awaria to stan NORMALNY. Wariant ogólny:
`../citation-grounding-pl/references/drabinka-zrodel-pl.md`.

## Dla istnienia decyzji (ISTNIENIE)

1. **Lista decyzji uodo.gov.pl** + strona-streszczenie (sekcja aktualności) - potwierdzają
   sygnaturę, datę, organ i kwotę kary. Zbuduj z tego `anchor_resolved`. Zwykle wystarcza, by
   potwierdzić ISTNIENIE i `powolanie`.
2. **WebSearch po sygnaturze** (`DKN.5131.x.RRRR site:uodo.gov.pl`) - gdy bezpośrednia strona pada,
   wynik z domeny uodo.gov.pl potwierdza ISTNIENIE.

## Dla treści i cytatu (TREŚĆ / FRAGMENT)

3. **PDF decyzji** - UODO często udostępnia pełną decyzję jako PDF (→ `markitdown` / `opendataloader-pdf`).
   To podstawowa droga do FRAGMENT, bo HTML jest renderowany JS.
4. **Realny Chrome (byob)** - gdy treść tylko w JS-SPA. Uwaga: byob działa wyłącznie z Chrome
   (Windows otwiera Edge → „No live byob bridge"); przy braku mostka zejdź do PDF lub użytkownika.
5. **Wyrok WSA/NSA ze skargi** - sąd cytuje decyzję UODO w uzasadnieniu; pośrednie potwierdzenie
   treści (oznacz, że cytujesz za wyrokiem sądu, nie za decyzją).
6. **Zapytaj użytkownika** - kancelaria często ma decyzję w aktach sprawy. Poproś o PDF/tekst.

**Bez tekstu decyzji cytat dosłowny = ⛔ BRAK ŹRÓDŁA, nigdy „prawdopodobnie ok".** To przy UODO
częste - patrz `examples/przyklad-weryfikacja.md` (rekord U3). Nigdy nie wymyślaj sygnatury DKN ani
fragmentu uzasadnienia, by zapełnić lukę.
