# vendor/docx-engine - status i pomiary

Silnik `.docx` wyodrebniony z `genspark-ai/genoffice` (Apache-2.0). Parsuje dokument
do drzewa blokow kotwiczonych indeksami elementow `<w:body>`, a przy zapisie
przepisuje **wylacznie** akapity zmienione - reszta archiwum `.docx` przechodzi
bajt w bajt.

**Status: zweryfikowany w spike'u, NIE wpiety w workflow skilla.**
`redline-docx-pl` dziala nadal na `adeu` (MIT, Python/uvx). Ten katalog jest
materialem do decyzji, nie zamiana silnika. Patrz "Co dalej".

Proweniencja, licencja i wykaz zmian: [NOTICE](NOTICE). Licencja: [LICENSE](LICENSE).

## Po co to kancelarii

Kancelaria nie przyjmie narzedzia, ktore przy edycji jednego zdania przebuduje
cale pismo - gina style, numeracja i formatowanie. Ten silnik zmienia tylko te
`<w:t>`, ktore przecinaja zmieniony zakres tekstu; `<w:pPr>` (styl + numeracja)
i `<w:rPr>` (formatowanie runow) zostaja nietkniete.

## Wynik pomiaru (2026-08-05)

Srodowisko: Windows 11, Node 24.15.0, katalog poza monorepo, wlasny `package.json`.

**Wyodrebnialnosc**

| Sprawdzenie | Wynik |
|---|---|
| Zaleznosci produkcyjne | `fast-xml-parser`, `jszip` - i nic wiecej |
| Import `electron` / API renderera | 0 wystapien w `src/` |
| Import innego pakietu monorepo (`@genoffice/*`) | 0 wystapien |
| Import `node:*` | 0 wystapien (silnik jest agnostyczny wobec runtime'u) |
| `tsc --noEmit` poza monorepo | exit 0 |
| Zestaw testow upstreamu poza monorepo | 52 pliki, **428 testow przeszlo, 0 padlo**, 1 pominiety |

**Wiernosc round-tripu - 56 prawdziwych plikow `.docx` z maszyny WM**

Scenariusz: parse -> chirurgiczna podmiana tekstu JEDNEGO akapitu (preferowany
numerowany) -> zapis -> porownanie skrotow SHA-256 kazdego wpisu ZIP.

| Sprawdzenie | Wynik |
|---|---|
| Zapis bez zmian = wejscie bajt w bajt | 56/56 |
| Wszystkie pozostale akapity bajt-identyczne | 55/55 * |
| `<w:pPr>` edytowanego akapitu (styl + numeracja) nietkniety | 55/55 * |
| `<w:rPr>` (formatowanie runow) nietkniete | 55/55 * |
| Plik po zapisie parsuje sie, styl i numeracja zachowane | 55/55 * |
| Bledy / wyjatki | 0/56 |

\* 1 z 56 plikow pominiety: harness wybral jako cel **tabele**, a
`patchParagraphTexts` obsluguje tekst akapitu, nie tabele - zwraca `null` i
oddaje sterowanie sciezce przebudowy. Zachowanie zgodne z dokumentacja funkcji,
nie blad. Edycja komorek tabeli ma osobne API (`patchTableCellTexts`) - zmierzone
osobno, patrz "Wynik pomiaru 2 / B" nizej.

**Czego dotyka zapis**

Jedyna zmieniana czesc **tresciowa** to `word/document.xml`. Nietkniete zostaja
`styles.xml`, `numbering.xml`, `footnotes.xml`, `theme1.xml`, `settings.xml`,
`header*.xml`, `footer*.xml`, `media/*`.

Osobno rusza sie `docProps/core.xml`, i tylko w polach metadanych:

- `dcterms:modified` - ustawiany na czas zapisu. **Kontrolowalny**: podanie
  `saveDocx(..., { savedAt: <oryginalna wartosc> })` daje `core.xml` identyczny.
- `cp:revision` - licznik wersji, inkrementowany bezwarunkowo gdy pole istnieje.
  Nie da sie tego wylaczyc opcja. Dla pisma wychodzacego na zewnatrz to i tak
  domyka krok `adeu sanitize` z workflow skilla (czysci metadane przed wysylka).

W 2 z 56 plikow `core.xml` nie zmienil sie wcale - ich `core.xml` zawiera sam
element glowny, bez `dcterms:modified` i `cp:revision`.

**Luka materialowa: przypisy**

Na 56 przeskanowanych plikow `.docx` na maszynie ani jeden polski dokument nie
mial przypisow dolnych (jedyny plik z przypisem to angielski formularz). Luke
domknieto **fixture'em syntetycznym** (`verify/core-and-notes.ts`, sekcja M2):
polskie pismo z naglowkami H1/H2, dwoma poziomami numeracji i dwoma przypisami
dolnymi, w tym akapit numerowany niosacy jednoczesnie odwolanie do przypisu i
pogrubiony run. Wynik: zmieniony wylacznie `word/document.xml`; `footnotes.xml`,
`numbering.xml` i `styles.xml` bajt-identyczne; odwolanie `<w:footnoteReference>`
i `<w:b/>` zachowane; po ponownym parsowaniu 2/2 przypisy i ta sama numeracja.

To pomiar na fixture, nie na piśmie z obrotu - przy pierwszym prawdziwym polskim
dokumencie z przypisami powtorz `verify/roundtrip-real.ts` na nim.

## Wynik pomiaru 2 (2026-08-05, wieczor) - sledzone zmiany i tabele

Domkniete dwie luki wskazane wyzej. Korpus: 71 prawdziwych plikow `.docx`
z maszyny WM (poprzedni pomiar szedl na 56 - roznica to szerszy zakres skanu,
nie inny material). Worda na tej maszynie NIE MA (`REGDB_E_CLASSNOTREG`),
wiec werdykt opiera sie na trzech niezaleznych czytnikach zamiast na jednym.

### A. Sledzone zmiany - dwie sciezki silnika wobec `adeu apply`

Silnik ma dwie rozne drogi do sledzonej zmiany. Nazwy jak w harnessie:

- **V1** - `SaveBlock.revision`: opakowuje CALY blok, `<w:ins><w:p>...</w:p></w:ins>`
- **V2** - `Run.ins` / `Run.del` w regenerowanym akapicie: `<w:ins><w:r><w:t>`,
  `<w:del><w:r><w:delText>`
- **ADEU** - `uvx adeu apply` (adeu 1.30.0), dzisiejsza produkcja skilla

| Sprawdzenie | V1 blok | V2 run | ADEU |
|---|---|---|---|
| zapis / apply bez bledu | 71/71 | 71/71 | 67/71 |
| `w:ins`/`w:del` w ogole powstaly | 71/71 | 71/71 | 67/71 |
| gdzie leza | `w:body`, owijaja `w:p` | w `w:p` | w `w:p` |
| autor + data + id na kazdym | 71/71 | 71/71 | 67/71 |
| tekst usuniety w `w:delText`, nie `w:t` | **0/71** | 71/71 | 11/11 * |
| `adeu extract` widzi wstawienie | **0/71** ** | 70/71 | 67/71 |
| `adeu extract` widzi usuniecie | **0/71** ** | 70/71 | 11/71 * |
| LibreOffice widzi region zmiany (3 pliki) | 2/3, zawsze `del=0` | 3/3 | 3/3 |
| inne bloki bajt-identyczne | 71/71 | 71/71 | **22/71** |
| `w:pPr` celu bajt-identyczny | 71/71 | 70/71 | 25/71 |

\* Edycja testowa byla dopisaniem tekstu, wiec adeu w 60 plikach slusznie nie
tworzy `w:del` w ogole. Tam, gdzie usuniecie powstalo, `w:delText` jest 11/11.

\** Liczby 2/71 w surowym wyjsciu harnessu dla V1 pochodza z dwoch plikow,
ktore MIALY sledzone zmiany JUZ WCZESNIEJ - czytnik widzi tam cudze rewizje,
nie nasze. Wlasnej zmiany V1 nie zobaczyl w zadnym pliku.

**Werdykt A.** Sciezka `SaveBlock.revision` nie produkuje Word Track Changes.
Trzy fakty skladaja sie na to samo:

1. Konstrukcja `<w:ins>` bezposrednio w `w:body`, owijajaca `w:p`, nie wystepuje
   w zadnym z 71 plikow wyprodukowanych przez Worda - tam wszystkie 4 znalezione
   elementy `w:ins`/`w:del` leza w `w:p` (`SCAN=1`).
2. Tekst usuniety zostaje w `w:t`. W plikach z Worda tekst usuniety jest
   w `w:delText` 2/2, `w:t` wewnatrz `w:del` - zero wystapien.
3. LibreOffice interpretuje polowe konstrukcji: widzi wstawienie, ale usuniecia
   NIE (`del=0` we wszystkich biegach). W praktyce oznacza to redline, w ktorym
   stary akapit zostaje w pismie jako zwykla tresc, obok nowego.

Sciezka V2 (`Run.ins` / `Run.del`) jest natomiast poprawna: `w:ins`/`w:del`
w `w:p`, `w:delText`, autor i data, rozpoznana przez oba niezalezne czytniki.
Jej koszt: akapit celu jest REGENEROWANY z modelu (runy np. 12 -> 5), przy
zachowaniu `w:pPr` co do bajtu (`rawPPr`) i wszystkich innych blokow 71/71.
Silnik nie ma API, ktore dalo by sledzona zmiane bez regeneracji akapitu -
sciezka chirurgiczna (`patchParagraphTexts`) i sciezka sledzonych zmian to
dwa rozne tryby tej samej funkcji zapisu.

Regeneracja w V2 nie jest gorsza od dzisiejszej produkcji. Osobny bieg na 20
plikach zliczyl, w ilu plikach KAZDY rozny `w:rPr` z oryginalnego akapitu
wystepuje nadal co do bajtu w wyniku (9 akapitow nie mialo `w:rPr` w ogole,
wiec liczy sie 11): V1 - 0/11 plikow, V2 - 6/11, adeu - 6/11, przy czym V2
i adeu wypadaja identycznie plik po pliku.
Te 5 rozjazdow to re-serializacja `w:rPr` przy dzieleniu runu na `w:ins`/`w:del`,
nie defekt silnika. Spadek liczby runow (12 -> 5) to konsolidacja identycznie
sformatowanych runow.

Jeden plik (ten sam, ktory wywrocil pomiar B nizej) zachowuje sie inaczej:
V2 nie zostal na nim rozpoznany, a `adeu apply` go odmowil. Adeu odmowilo
apply w 4/71 plikach - to jego bramka walidacji, nie awaria.

### B. Tabele - `patchTableCellTexts`

24 z 71 plikow ma tabele; 743 komorki lacznie. Scenariusz jak w
`roundtrip-real.ts`, tylko celem jest komorka tabeli.

| Sprawdzenie | Wynik |
|---|---|
| zmienil sie tylko `word/document.xml` (+ `docProps/core.xml`) | 24/24 |
| wszystkie inne bloki bajt-identyczne | 24/24 |
| wszystkie inne komorki tabeli bajt-identyczne | 24/24 |
| `w:tblPr`, `w:tblGrid`, `w:trPr` nietkniete | 24/24 |
| `w:tcPr` edytowanej komorki nietkniety | 24/24 |
| `w:pPr` pierwszego akapitu komorki nietkniety | 24/24 |
| liczba runow komorki bez zmian | **19/24** |
| `w:rPr` komorki nietkniete | **21/24** |
| `w:pPr` KAZDEGO akapitu komorki zachowany | **22/24** |
| bez utraty konstruktow (`w:br`, `w:hyperlink`, pola...) | **22/24** |
| tekst komorki po zapisie taki, jak zamierzony | **23/24** |
| bledy / wyjatki | 0/71 |

**Werdykt B.** Otoczenie tabeli jest bezpieczne, ale sama komorka NIE jest
patchowana chirurgicznie. `patchCellXml` odbudowuje ja z trzech elementow:
`w:tcPr`, `w:pPr` PIERWSZEGO akapitu i `w:rPr` PIERWSZEGO runu. Skutki
zmierzone na korpusie:

- runy komorki splaszczaja sie do jednego na akapit (6->1, 3->1, 2->1);
  formatowanie mieszane wewnatrz komorki gina. Ekspozycja: 19/743 komorek
  korpusu (3%) ma dzis mieszane formatowanie, wiec bylyby uszkodzone przy edycji.
- w 2 plikach komorka o 5 akapitach zostala odbudowana jako 1 akapit, razem
  z utrata `w:br`. Tekst przetrwal, uklad pionowy nie.
- w 1 pliku tekst komorki po zapisie ROZNI SIE od zamierzonego (140 znakow
  zamierzone, 183 po zapisie). Przyczyna: `TableCell.paras` powstaje przez
  `textOf()` na calym poddrzewie akapitu, wiec zbiera takze biale znaki
  formatowania XML - dla tej komorki 113 znakow przy 5 znakach realnego `w:t`.
  `patchTableCellTexts` przyjmuje wlasnie `paras` i wpisuje je z powrotem jako
  TRESC. Rozjazd `paras` wobec `richParas` widac w 8/743 komorek (1%),
  w 3 z 24 plikow z tabela.

To odwrotnosc `patchParagraphTexts`, ktory jest chirurgiczny i przeszedl 55/55.
Nazwy sa podobne, gwarancje nie.

## Jak powtorzyc pomiar

```bash
cd dokumenty/skills/redline-docx-pl/vendor/docx-engine
npm install
npx tsc --noEmit          # typecheck
npx vitest run            # zestaw testow upstreamu
```

Komendy wykonane doslownie w tej lokalizacji 2026-08-05: `tsc` exit 0,
`vitest` 428/428.

**Znany flake.** Pierwszy bieg `vitest run` bezposrednio po `npm install` dal
raz `1 failed | 427 passed`; cztery kolejne biegi 428/428. Upstream ustawia
`testTimeout: 20000` (vitest.config.ts), a pierwszy bieg idzie z zimnym cache
transformacji i konkuruje o dysk z npm. Jezeli zobaczysz pojedyncza porazke
zaraz po instalacji - powtorz bieg przed diagnozowaniem. Porazka powtarzalna to
juz sygnal, nie szum.

Harness MateMatic (katalog `verify/`, nie pochodzi z upstreamu). Skrypty
raportuja **wylacznie metryki strukturalne** - nazwy wpisow ZIP, liczniki,
werdykty. Zadnego znaku tresci dokumentu nie wypisuja, zeby mozna je bylo puscic
na aktach objetych tajemnica adwokacka:

```bash
node verify/probe.mjs sciezka/do/*.docx                    # co dokument zawiera (naglowki, numeracja, przypisy)
npx tsx verify/roundtrip-real.ts sciezka/do/*.docx         # wiernosc round-tripu akapitu, masowo
npx tsx verify/core-and-notes.ts sciezka/do/plik.docx      # delta docProps + fixture z przypisami
npx tsx verify/table-roundtrip.ts sciezka/do/*.docx        # POMIAR B: edycja komorki tabeli
npx tsx verify/revision-vs-adeu.ts sciezka/do/*.docx       # POMIAR A: sledzone zmiany wobec adeu
LO=1 npx tsx verify/revision-vs-adeu.ts sciezka/do/plik.docx   # + orakul LibreOffice (wolny)
SCAN=1 npx tsx verify/revision-vs-adeu.ts sciezka/do/*.docx    # tylko odczyt: gdzie Word klade w:ins/w:del
```

Dwa nowsze skrypty (`table-roundtrip.ts`, `revision-vs-adeu.ts`) nie wypisuja
takze NAZW plikow - nazwa pisma niesie nazwiska stron. Kazdy plik dostaje id
`fNN`. Starsze skrypty wypisuja `basename`; przy pracy na aktach klienta
uruchamiaj je swiadomie.

Pomiar A wymaga `uvx` (adeu) na PATH; sciezki mozna nadpisac zmiennymi
`UVX_BIN` i `SOFFICE_BIN`. Pliki posrednie powstaja w katalogu tymczasowym
systemu i sa kasowane po biegu.

## Ryzyka

- **Wiek upstreamu.** Repozytorium powstalo 2026-07-31. W dniu wendorowania
  liczylo 5 dni. Gwiazdki (1489) nie sa dojrzaloscia. Nie stawiamy na tym
  produkcji bez wlasnego zestawu testow na polskich pismach.
- **Drugi runtime.** Skill stoi na Pythonie (`uvx adeu`). Wpiecie tego silnika
  dokladalo by Node do wymagan skilla. To decyzja architektoniczna, nie
  konsekwencja tego spike'u.
- **`SaveBlock.revision` nie daje Word Track Changes** (zmierzone, patrz
  "Wynik pomiaru 2 / A"). Sledzona zmiane daje tylko sciezka `Run.ins`/`Run.del`,
  i to kosztem regeneracji akapitu.
- **`patchTableCellTexts` nie jest chirurgiczny** (zmierzone, "Wynik pomiaru 2 / B").
  Odbudowuje komorke; formatowanie mieszane i uklad akapitow w komorce gina.
- **Brak Worda na maszynie pomiarowej.** Werdykt o Track Changes opiera sie na
  trzech czytnikach zastepczych (struktura OOXML, `adeu extract`, LibreOffice)
  i na tym, co robi Word w 71 plikach z obrotu. Przy pierwszej maszynie
  z Wordem powtorz pomiar A i sprawdz `Document.Revisions.Count`.

## Co dalej - do decyzji WM

Oba pomiary z listy "co dalej" sa zrobione (2026-08-05 wieczor). Otwarte
zostaje jedno pytanie i jest to pytanie architektoniczne, nie pomiarowe:

1. Czy warto placic Node w wymaganiach skilla za jedyna przewage, ktora silnik
   ma udowodniona: bajtowa wiernosc reszty dokumentu (71/71 wobec 22/71 przy
   adeu). Rekomendacja i warianty czesciowe: `../../THIRD_PARTY_INSPIRATIONS.md`,
   sekcja o genoffice.
2. Sciezki zapisu do tabel nie wpinac bez wlasnej warstwy ochronnej - `paras`
   z modelu nie nadaja sie do zapisu wprost.
