# Third-party inspirations / dependencies

## adeu (silnik redline)

- **Repo:** https://github.com/dealfluence/adeu
- **PyPI:** `adeu` | **npm:** `@adeu/core`, `@adeu/mcp-server`
- **Licencja:** MIT (c) 2026 Dealfluence Oy
- **Wersja sprawdzona:** 1.7.5 (2026-05-22)
- **Relacja:** ZALEZNOSC, nie cherry-pick kodu. `redline-docx-pl` to cienki wrapper
  workflow PL nad CLI adeu (`uvx adeu ...`). Nie kopiujemy kodu adeu - wolamy go.

### Snapshot licencji (naglowek MIT)

```
MIT License
Copyright (c) 2026 Dealfluence Oy
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction... [pelny tekst: repo/LICENSE]
```

MIT pozwala na uzycie komercyjne, modyfikacje i redystrybucje przy zachowaniu
noty o prawach autorskich. Wrapper spelnia warunek przez atrybucje w 3 miejscach
(SKILL.md, ten plik, CHANGELOG).

### Co adeu robi (czego python-docx nie potrafi)

- `.docx -> Markdown/CriticMarkup` z Semantic Appendix (defined terms, cross-refs, typos)
- wstrzykiwanie **natywnych Word Track Changes** (`w:ins`/`w:del`) bez niszczenia OOXML
- bramka walidacji - blokuje niejednoznaczne dopasowania zanim dotkna pliku
- `sanitize` - strip metadanych autora / last-modified-by / rsid / template / custom XML
- live MS Word (Windows + Word, backend Python)

## Smoke test PL (2026-05-22)

Testowane lokalnie na `umowa.docx` (polski, z metadanymi autora "Jan Kowalski",
last-modified-by "Anna Nowak"):

| Krok | Wynik |
|------|-------|
| `extract` | Polski tekst poprawnie do Markdown (diakrytyki OK) |
| `apply` (edits.json modify + comment) | 1x `w:ins` + 1x `w:del` natywne, autor podmieniony na `--author` |
| `sanitize --keep-markup` | creator + lastModifiedBy wyczyszczone do pustych; autorzy track-changes -> jedna nazwa; rsid/timestampy/template/custom XML usuniete; werdykt `Result: CLEAN` |

Wniosek: silnik dziala na polskim materiale, sanitize realnie domyka wyciek metadanych
Worda (istotne RODO przy wysylce pisma).

## evolsb / legal-redline-tools (wzorce memo + skan)

- **Repo:** https://github.com/evolsb/legal-redline-tools
- **Licencja:** MIT
- **Snapshot:** 2026-07-13
- **Relacja:** PATTERN, nie kod. Dwa wzorce zaadaptowane w v0.2.0:
  1. **Memo negocjacyjne** - pola `tier`/`rationale`/`walkaway`/`precedent`
     w redline JSON + memo grupowane wg tierow (ich `memo.py` generuje PDF
     z naglowkiem "attorney work product"; nasz `memo_negocjacyjne.py`
     generuje Markdown z polskim naglowkiem poufnosci, format wejscia =
     edits.json adeu).
  2. **Skan placeholderow** - bramka przed wysylka (ich `scan.py` lapie
     `$X`/`TBD`/puste nawiasy; nasz `skan_placeholder.py` dodaje wzorce PL:
     `DO UZUPELNIENIA`, `NN/RR`, `dnia __`, kwoty w zl, i raportuje
     `plik:pozycja`).

Kod obu skryptow napisany od zera (Python stdlib, zero zaleznosci). MIT
pozwala takze na kopiowanie kodu z atrybucja - nie skorzystano, bo ich kod
jest zwiazany z ich formatem redlines i python-docx, a nasz z adeu.

## genspark-ai/genoffice - packages/docx-engine (WENDOROWANY, nieaktywny)

- **Repo:** https://github.com/genspark-ai/genoffice
- **Sciezka:** `packages/docx-engine` | **Commit:** `8f523289d6c34f940cd691472ee56b2013d148c8`
- **Licencja:** Apache-2.0 (c) 2026 Mainfunc, Inc.
- **Wendorowano:** 2026-08-05 do `vendor/docx-engine/`
- **Relacja:** WENDOROWANY - kod osob trzecich redystrybuowany razem ze skillem, w
  odroznieniu od adeu (zaleznosc CLI) i evolsb (sam wzorzec). Apache-2.0 wymaga przy
  redystrybucji zachowania LICENSE, noty upstreamu (sek. 4d) i wykazu zmian (sek. 4b) -
  wszystkie trzy leza w `vendor/docx-engine/`.
- **Status: NIE wpiety w workflow.** Skill dziala w calosci na adeu.

### Dlaczego lezy, a nie pracuje

**To jest jedyne miejsce z pelnym uzasadnieniem** - SKILL.md odsyla tutaj, zeby dwie
kopie tego samego wywodu nie rozjechaly sie przy nastepnej aktualizacji.

Silnik przepisuje przy zapisie wylacznie zmienione akapity; `styles.xml`, `numbering.xml`
i `footnotes.xml` przechodza bajt w bajt. Zmierzylismy to na 56 prawdziwych pismach
z maszyny WM. Zapis bez zmian dal 56/56 bajt w bajt. Po chirurgicznej edycji jednego
akapitu 55/55 pozostalych akapitow bylo bajt-identycznych, `w:pPr` i `w:rPr` nietkniete,
zero bledow. Zestaw testow upstreamu przeszedl 428/428 poza monorepo.

Rozbieznosc 56 wobec 55 nie jest bledem: w jednym pliku harness wybral jako cel tabele,
a `patchParagraphTexts` obsluguje tekst akapitu, nie komorki tabeli - zwraca wtedy `null`
i oddaje sterowanie sciezce przebudowy. Zachowanie zgodne z dokumentacja funkcji.

Blokowaly dwie rzeczy. **Obie zostaly zmierzone 2026-08-05 wieczorem** (sekcje nizej);
zostaje jedna, i jest architektoniczna, nie pomiarowa:

**Drugi runtime.** Skill wymaga dzis Pythona (`uvx adeu`), a silnik jest w Node.
Wpiecie doklada Node do wymagan u prawnika. To decyzja WM, nie wniosek z pomiaru.

## Pomiar 2 (2026-08-05, wieczor) - sledzone zmiany i tabele

Korpus: 71 prawdziwych `.docx` z maszyny WM (poprzedni pomiar szedl na 56; roznica
to szerszy zakres skanu, nie inny material). Harness: `vendor/docx-engine/verify/
revision-vs-adeu.ts` i `verify/table-roundtrip.ts` - raportuja wylacznie metryki
strukturalne, bez tresci i bez nazw plikow, wiec pomiar poszedl na aktach.

**Worda na maszynie nie ma** (`REGDB_E_CLASSNOTREG`). Zamiast jednego czytnika
sa trzy niezalezne: struktura OOXML, `uvx adeu extract` na wyniku silnika oraz
LibreOffice (`--convert-to fodt`, liczba `text:changed-region`).

### A. Sciezka `revision` wobec `adeu apply`

Silnik ma DWIE rozne drogi do sledzonej zmiany i to jest sedno wyniku:

- **V1** - `SaveBlock.revision`: opakowuje caly blok, `<w:ins><w:p>...</w:p></w:ins>`
- **V2** - `Run.ins` / `Run.del` w regenerowanym akapicie: `<w:ins><w:r><w:t>`,
  `<w:del><w:r><w:delText>`

| Sprawdzenie | V1 blok | V2 run | `adeu apply` |
|---|---|---|---|
| zapis / apply bez bledu | 71/71 | 71/71 | 67/71 |
| gdzie leza `w:ins`/`w:del` | `w:body`, owijaja `w:p` | w `w:p` | w `w:p` |
| autor + data + id | 71/71 | 71/71 | 67/71 |
| tekst usuniety w `w:delText` | **0/71** | 71/71 | 11/11 * |
| `adeu extract` widzi wstawienie | **0/71** | 70/71 | 67/71 |
| `adeu extract` widzi usuniecie | **0/71** | 70/71 | 11/71 * |
| LibreOffice widzi region zmiany (3 pliki) | 2/3, zawsze `del=0` | 3/3 | 3/3 |
| inne bloki bajt-identyczne | 71/71 | 71/71 | **22/71** |
| `w:pPr` celu bajt-identyczny | 71/71 | 70/71 | 25/71 |

\* Edycja testowa byla dopisaniem tekstu, wiec w 60 plikach adeu slusznie nie tworzy
`w:del`. Tam, gdzie usuniecie powstalo, `w:delText` jest 11/11.

**V1 nie produkuje Word Track Changes.** Trzy niezalezne fakty:

1. `<w:ins>` bezposrednio w `w:body`, owijajacy `w:p`, nie wystepuje w zadnym
   z 71 plikow z obrotu - tam wszystkie znalezione `w:ins`/`w:del` leza w `w:p`.
2. Tekst usuniety zostaje w `w:t`. W plikach z Worda usuniety tekst jest
   w `w:delText` 2/2, a `w:t` wewnatrz `w:del` nie wystapil ani razu.
3. LibreOffice interpretuje polowe konstrukcji: widzi wstawienie, usuniecia nie
   (`del=0` w kazdym biegu). Praktycznie: stary akapit zostaje w pismie jako
   zwykla tresc, obok nowego. Dla kancelarii to redline zepsuty, nie redline.

Wlasny parser silnika czyta te konstrukcje poprawnie (`blockRevision`), wiec test
upstreamu przechodzi. To round-trip przez samego siebie, nie zgodnosc z Wordem.

**V2 jest poprawna** - `w:ins`/`w:del` w `w:p`, `w:delText`, autor i data,
rozpoznana przez oba niezalezne czytniki. Kosztem jest regeneracja akapitu celu
z modelu (runy np. 12 -> 5) przy zachowanym `w:pPr` co do bajtu (`rawPPr`).
Silnik nie ma API laczacego chirurgie tekstu ze sledzona zmiana: `patchParagraphTexts`
i sledzone zmiany to dwa rozne tryby tej samej funkcji zapisu.

Regeneracja akapitu w V2 nie jest gorsza od dzisiejszej produkcji. Osobny bieg
na 20 plikach sprawdzil, w ilu plikach KAZDY rozny `w:rPr` z oryginalnego akapitu
wystepuje nadal co do bajtu w wyniku (9 akapitow nie mialo `w:rPr` w ogole, wiec
liczy sie 11): V1 - 0/11 plikow, V2 - 6/11, adeu - 6/11. V2 i adeu maja profil identyczny co do pliku, wiec te
5 rozjazdow to re-serializacja `w:rPr` przy dzieleniu runu na `w:ins`/`w:del`,
a nie utrata specyficzna dla silnika. Spadek liczby runow w V2 (12 -> 5) to
konsolidacja identycznie sformatowanych runow, nie splaszczenie formatowania.

Adeu odmowilo `apply` w 4/71 plikach - to jego bramka walidacji dopasowania,
nie awaria. Jeden plik zachowal sie inaczej we wszystkich pomiarach: V2 nie
zostal na nim rozpoznany, adeu go odmowilo, i to ten sam plik, ktory wywrocil
pomiar B.

### B. `patchTableCellTexts`

24 z 71 plikow ma tabele, 743 komorki lacznie.

| Sprawdzenie | Wynik |
|---|---|
| zmienil sie tylko `word/document.xml` (+ `docProps/core.xml`) | 24/24 |
| wszystkie inne bloki i wszystkie inne komorki bajt-identyczne | 24/24 |
| `w:tblPr`, `w:tblGrid`, `w:trPr`, `w:tcPr` celu nietkniete | 24/24 |
| `w:pPr` pierwszego akapitu komorki nietkniety | 24/24 |
| liczba runow komorki bez zmian | **19/24** |
| `w:rPr` komorki nietkniete | **21/24** |
| `w:pPr` KAZDEGO akapitu komorki zachowany | **22/24** |
| bez utraty konstruktow (`w:br` i pokrewne) | **22/24** |
| tekst komorki po zapisie taki, jak zamierzony | **23/24** |
| bledy / wyjatki | 0/71 |

Otoczenie tabeli jest bezpieczne, ale komorka NIE jest patchowana chirurgicznie.
`patchCellXml` odbudowuje ja z `w:tcPr`, `w:pPr` PIERWSZEGO akapitu i `w:rPr`
PIERWSZEGO runu. Zmierzone skutki:

- runy splaszczaja sie do jednego na akapit (6->1, 3->1, 2->1) - mieszane
  formatowanie wewnatrz komorki gina. Dzis takich komorek jest 19/743 (3%).
- w 2 plikach komorka o 5 akapitach wyszla jako 1 akapit, razem z utrata `w:br`.
- w 1 pliku tekst komorki po zapisie rozni sie od zamierzonego (140 znakow
  zamierzone, 183 po zapisie). Przyczyna: `TableCell.paras` powstaje przez
  `textOf()` na calym poddrzewie akapitu, wiec zbiera tez biale znaki formatowania
  XML - w tej komorce 113 znakow przy 5 znakach realnego `w:t`. `patchTableCellTexts`
  przyjmuje wlasnie `paras` i wpisuje je z powrotem jako TRESC. Rozjazd `paras`
  wobec `richParas` widac w 8/743 komorek (1%), w 3 z 24 plikow z tabela.

Nazwa myli: `patchParagraphTexts` jest chirurgiczny (55/55 w pierwszym pomiarze),
`patchTableCellTexts` nie jest. Gwarancje sa rozne mimo podobnej nazwy.

## Rekomendacja (2026-08-05) - decyduje WM

**Nie wpinac silnika do sciezki ZAPISU. Wpiac go opcjonalnie jako ODCZYT.**

Uzasadnienie po kolei:

1. **Track Changes zostaja przy adeu.** V1 jest wykluczone pomiarem. V2 dziala,
   ale nie daje przewagi nad adeu w tej warstwie - robi to samo, tylko po stronie
   Node i bez bramki walidacji dopasowania, ktora adeu ma (odmowilo 4/71 wtedy,
   gdy dopasowanie bylo watpliwe; silnik w tej samej sytuacji zapisuje bez pytania).
   Zamiana narzedzia zmierzonego w produkcji na drugie, rownie dobre, za cene
   drugiego runtime'u to zla wymiana.
2. **Tabel nie ruszac.** `patchTableCellTexts` traci formatowanie w 3/24 plikow
   i raz na 24 zapisal do komorki tekst inny niz zamierzony. Wpiecie wymagaloby
   wlasnej warstwy ochronnej (budowanie tekstu z `richParas`, nie z `paras`,
   plus bramka na komorki z mieszanym formatowaniem). To praca na osobna decyzje,
   nie efekt uboczny wpiecia.
3. **Jedyna udowodniona przewaga silnika to wiernosc bajtowa** reszty dokumentu:
   71/71 wobec 22/71 przy adeu. Ta przewaga daje sie zebrac BEZ ryzyka, jesli
   silnik uzyc tylko do ODCZYTU - jako bramke kontrolna po `adeu apply`:
   ktore wpisy ZIP sie ruszyly, czy `styles.xml` / `numbering.xml` / `footnotes.xml`
   przetrwaly, ile akapitow zachowalo oryginalne bajty. To jest dokladnie to,
   czego kancelaria sie boi ("narzedzie przebudowalo mi pismo"), a dzis nikt tego
   nie sprawdza.
4. **Node zostaje po stronie operatora, nie prawnika.** Bramka z pkt. 3 jest
   opcjonalna: kiedy Node jest, workflow dostaje raport; kiedy go nie ma, skill
   dziala jak dzis. Wymagania skilla sie nie zmieniaja.

Czego rekomendacja NIE obejmuje: zastapienia adeu, wpiecia zapisu, wpiecia tabel,
wystawienia silnika jako narzedzia dla prawnika. Do czasu decyzji WM katalog
`vendor/docx-engine/` zostaje materialem referencyjnym i nie jest wolany z zadnego
kroku workflow.

Jesli WM zdecyduje inaczej i wpiecie zapisu wchodzi w gre, minimum przed nim to
powtorzenie pomiaru A na maszynie z Wordem (`Document.Revisions.Count`) - tu Worda
nie bylo i werdykt stoi na trzech czytnikach zastepczych.

### Jedno odstepstwo od dokumentacji upstreamu

Upstream mowi „reszta archiwum nietknieta". Pomiar pokazal, ze `docProps/core.xml` rusza
sie zawsze: `dcterms:modified` (kontrolowalne przez `saveDocx(..., {savedAt})`) oraz
`cp:revision`, inkrementowany bezwarunkowo i niewylaczalny opcja. Dla pisma wychodzacego
na zewnatrz domyka to i tak `adeu sanitize`.

## Powiazania

- [`let-it-be`](../let-it-be) - anonimizacja TRESCI (PII PL); adeu sanitize czysci METADANE pliku.
  Dwie rozne warstwy, lancuch: let-it-be tresc -> redline -> adeu sanitize metadane.
