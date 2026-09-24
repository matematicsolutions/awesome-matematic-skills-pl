---
name: doc-intel-contract-pl
description: >
  Normalizuje wyjscie darmowego RODO-safe stacku OCR/PDF (opendataloader-pdf,
  pdftotext, Chandra OCR, LiteParse - OCR skanow na CPU, OCR PATRONa/Gaius-Lex)
  do jednego audytowalnego kontraktu
  {block_type, bbox, text, confidence} inspirowanego architektura Mistral OCR 4
  (idea, nie wagi - model zamkniety=SKIP). Daje trzy rzeczy naraz: confidence-gating
  (region niskiej pewnosci -> kolejka human-in-the-loop, reszta auto-approve),
  typed blocks + flagi PII pod redakcje RODO (signature/stamp/PESEL/NIP/IBAN),
  oraz bbox+block domykajace grounding cytatow (cytat -> region dokumentu).
  Zero-cloud, zero LLM w sciezce normalizacji, deterministyczne (doc_id SHA256),
  Python stdlib. Uzywaj gdy: "znormalizuj OCR", "kontrakt dokumentu", "ktore
  bloki do przegladu", "confidence gating", "przygotuj redakcje PII", "bbox do
  cytatu", "wyjscie opendataloader do JSON", "human-in-the-loop dla skanu".
  Dzieli teczke akt na pisma lokalnie (split_packet.py, bez LLM). "podziel teczke",
  "rozbij akta na pisma", "OCR skanu bez GPU". Komplementarny do citation-grounding-pl
  (konsument kontraktu) i drabinki PDF.
attribution:
  - source: Mistral OCR 4 (Mistral AI)
    url: https://mistral.ai/news/mistral-ocr
    license: proprietary
    relationship: pattern-only
    note: >
      Idea kontraktu wyjscia Document Intelligence: typed blocks + bbox + confidence
      jako jedno audytowalne wyjscie. Model jest zamkniety, wiec bierzemy sam ksztalt
      kontraktu; schemat, gating, flagi PII i caly kod napisane od zera.
  - source: datalab-to/chandra
    url: https://github.com/datalab-to/chandra
    license: Apache-2.0
    relationship: adaptation
    note: >
      Z KODU (Apache-2.0), nie z wag (wagi sa na Modified OpenRAIL-M i nie sa tu
      uzywane). Wzorzec prompt-kontraktu constrained-HTML z data-label/data-bbox
      w skali 0-1000 (silnik vlm-html), algorytm detekcji zapetlenia generacji
      detect_repeat_token (degeneracja.py) oraz przepis renderu strony
      flatten AcroForm + dynamiczne DPI. Taksonomia etykiet, obsluga podpisu
      i pieczatki, adapter i testy napisane od zera.
  - source: firecrawl/pdf-inspector
    url: https://github.com/firecrawl/pdf-inspector
    license: MIT
    relationship: dependency
    note: >
      Zaleznosc opcjonalna (PyPI `pdf-inspector`, MIT) uzywana WYLACZNIE przez
      `scripts/routing_gate.py` do mechanicznej klasyfikacji skan-vs-tekst
      (classify_pdf: pdf_type, pages_needing_ocr, confidence 0-1). Sciezka
      normalizacji pozostaje zero-dep stdlib. Zmierzone 2026-08-08 na realnych aktach:
      pelny skan wykryty w milisekundach (pewnosc 0.95), wielostronicowy PDF
      tekstowy w kilkudziesieciu ms. Zamyka dziure szczebla 4 drabinki, gdzie decyzja
      "czy to skan" byla dotad ocena oka ludzkiego.
  - source: run-llama/liteparse
    url: https://github.com/run-llama/liteparse
    license: Apache-2.0
    relationship: dependency
    note: >
      Zaleznosc opcjonalna (PyPI `liteparse`, przypieta 2.14.6) uzywana WYLACZNIE
      przez `scripts/liteparse_extract.py` - szczebel OCR skanow na CPU (Tesseract
      w srodku, bez chmury). Zmierzone 2026-09-21: CER 0,5% na skanie 300 dpi
      publicznego wyroku SN, 3,5% na zdegradowanym, ogonki 431/431, ~2 s/str. na
      CPU. Piec pulapek wpisanych w ekstraktor jako
      bezpieczniki (limit 1000 stron obcinajacy po cichu, markdown wycinajacy
      sygnature, DPI, pobieranie modelu w locie, `§` czytany jako `$`). Modele
      jezyka (tessdata_best, Apache-2.0) przypinane `--tessdata`.
  - source: jerryjliu/docjev
    url: https://github.com/jerryjliu/docjev
    license: Apache-2.0
    relationship: pattern-only
    note: >
      NIE jest zaleznoscia. Wzorzec dla `scripts/split_packet.py`: podzial teczki
      jako decyzja dla kazdej strony osobno (kategoria + "czy strona N zaczyna nowe pismo"), a nie
      prosba o liste segmentow; niezmiennik "kazda strona dokladnie raz"; pusty
      odczyt to nie pusta strona; reguly kategorii jako id + opis celu pisma.
      DocJev pyta Jeva (hostowany model decyzyjny TypeSafe) - u nas silnik jest
      lokalny i deterministyczny,
      bo tekst akt nie moze opuscic maszyny kancelarii. Kod napisany od zera.
  - source: firecrawl/anydoc
    url: https://github.com/firecrawl/anydoc
    license: MIT
    relationship: pattern-only
    note: >
      NIE jest zaleznoscia - jest POWODEM istnienia bramki. Audyt zrodla
      2026-08-08 wykazal, ze zdarzenia pominiecia tresci (42 miejsca, m.in.
      "skipping slide", "skipping chapter", "duplicate note id dropped") ida do
      fasady `log`, a repo nigdzie nie rejestruje loggera. Dowod bojowy:
      .docx z jednym uszkodzonym chart1.xml -> exit 0, stderr 0 bajtow,
      a z wyjscia znika cala tabela danych. `check_ooxml` nazywa uszkodzona
      czesc ZANIM ktokolwiek zaufa wyjsciu. Kod bramki napisany od zera.
  - source: sandbox-quantum/flintai-cli
    url: https://github.com/sandbox-quantum/flintai-cli
    license: Apache-2.0 WITH Commons-Clause
    relationship: pattern-only
    note: >
      `mask_for_model.py` - maska dlugosciowa dla KOPII tekstu wysylanej do modelu
      (rung-5): kazdy znak sekretu -> `*`, dlugosc i pozycje reszty identyczne, wiec
      offsety i bbox dalej pasuja do oryginalu. Idea z ich `secret_anonymizer.py`
      (maskowanie kluczy w kodzie); tu regexy PII PL z pii_flags i wlasne. Zero kodu.
  - source: docling-project/docling-graph
    url: https://github.com/docling-project/docling-graph
    license: MIT
    relationship: pattern-only
    note: >
      Warstwa dowodowa `evidence.py` (zasada "fail-empty, never fail-wrong",
      proweniencja cytatu) oraz kotwica dokumentacji testem
      (`tests/test_dokumentacja_zakotwiczona.py`, wzorzec ich
      `tests/test_architecture_doc.py`). Wziete idee, nie zaleznosc; kod od zera.
metadata:
  author: Wieslaw Mazur / MateMatic
  version: 0.5.0
  scope: warstwa normalizujaca stack OCR/PDF -> kontrakt wyjscia (zero-cloud)
  cost: zero LLM (deterministyczna normalizacja)
  license: MIT
  companion_skills: citation-grounding-pl, opendataloader-pdf, markitdown
---

# doc-intel-contract-pl - kontrakt wyjscia Document Intelligence

## Po co
Kazdy szczebel naszej drabinki PDF (pdftotext -> anydoc -> markitdown ->
opendataloader -> liteparse -> Chandra -> vision) zwraca wynik w innym
formacie. Ten skill sprowadza te formaty do JEDNEGO kontraktu, ktory od razu
odpowiada na trzy pytania:

1. **Ktory fragment ma zobaczyc czlowiek?** - confidence-gating (Article III / AI Act art. 14).
2. **Co zredagowac?** - typed blocks + flagi PII (signature/stamp/PESEL/NIP/IBAN).
3. **Gdzie w dokumencie jest ten cytat?** - bbox + block_id -> most do `citation-grounding-pl`.

Zamkniety jest MODEL Mistral OCR 4, nie idea. Odtwarzamy kontrakt na wlasnym,
lokalnym, RODO-safe stacku - skladamy puzzle, nie wynajdujemy kola.

## Kontrakt (v1.2.0)

Wersja zyje w stalej `contract.CONTRACT_VERSION`; ten naglowek i przyklad ponizej
sa zakotwiczone testem `tests/test_dokumentacja_zakotwiczona.py` (D1).
```json
{
  "doc_id": "<sha256 wejscia>",
  "contract_version": "1.2.0",
  "source": {"path": "...", "engine": "opendataloader|pdftotext|chandra|gaius|vlm-html|pdf-inspector|liteparse", "engine_variant": "default|google_doc_ai|null", "pages": N},
  "blocks": [
    {"id": "b0001", "page": 1, "bbox": [x0,y0,x1,y1]|null,
     "block_type": "title|paragraph|table|list|equation|signature|stamp|figure|header|footer|unknown",
     "text": "...", "confidence": 0.0-1.0|null, "flags": ["partial","pii_suspected","pii:pesel","sensitive_block","signature_suspected",...]}
  ],
  "gating": {
    "threshold": 0.85,
    "review_required": ["b0003"], "auto_approved": ["b0001"],
    "ungroundable": ["b0007"],
    "verdict": "ok|degraded|failed",
    "note": "...",
    "counts": {"total": 11, "review_required": 1, "auto_approved": 10, "ungroundable": 0}
  },
  "redaction_candidates": ["b0004"],
  "meta": {"created_at": "ISO-8601"}
}
```
- `bbox` znormalizowany 0-1 (przenosny miedzy DPI). Silnik bez bbox -> `null` + flaga `partial`.
- `confidence == null` (partial) -> **zawsze** do `review_required` (konserwatywnie; nie wiemy = czlowiek patrzy).

### Gating jest DWUOSIOWY (od 1.2.0)

Do 1.1.0 istniala jedna os - `confidence` silnika. To mieszalo dwa twierdzenia,
ktore moga sie rozjechac:

| os | pyta o | pole |
|---|---|---|
| PEWNOSC | czy silnik jest pewny odczytanych znakow | `review_required` / `auto_approved` |
| UGRUNTOWANIE | czy blok da sie WSKAZAC w dokumencie (ma bbox) | `ungroundable` |

Blok z `confidence: 0.99` i `bbox: null` jest pewny i **jednoczesnie niecytowalny**:
nie da sie go podswietlic ani przypiac do strony. Wersja 1.1.0 wpisywala go do
`auto_approved` i nikt sie nie dowiadywal.

`verdict` jest trojstanowy, slownictwem i kodami wyjscia zgodny z `routing_gate.py`
(`ok`/`degraded`/`failed` = `0`/`10`/`20`; stala `contract.GATING_EXIT`).
**Zero blokow = `failed`, nigdy `ok`** - bramka, ktora przy pustym wejsciu mowi
"nic do przegladu", przepuszcza dokument, ktorego nikt nie przeczytal.

## Warstwa dowodowa cytatu (`scripts/evidence.py`, od 2026-08-30)

Most do groundingu nie mowi juz "znalazlem / nie znalazlem". Kazdy cytat dostaje
dowod o **dwoch ortogonalnych osiach** plus pelny mianownik trafien.

| `kind` (rodzaj dowodu) | sila | znaczenie |
|---|---|---|
| `verbatim` | 4 | wystepuje w bloku bajt w bajt |
| `normalized` | 3 | wystepuje po normalizacji typograficznej; lokalizacja doslowna, ale **glify zrodla roznia sie od cytatu** |
| `observed` | 2 | jest w dokumencie, lecz nie w jednym bloku (granica blokow albo zbyt wiele trafien) |
| `derived` | 0 | brak lokalizacji doslownej; przypisanie do calosci |

| `resolution` (rozdzielczosc) | sila |
|---|---|
| `span` (zakres znakowy w bloku) | 4 |
| `block` | 3 |
| `page` | 2 |
| `document` | 1 |
| `none` | 0 |

Bramka `grounding_bridge.gate()` ma **trzy warunki naraz**: rodzaj, rozdzielczosc
oraz **jednoznacznosc**. Mocny dowod na piec roznych miejsc nie jest mocnym
dowodem na jedno - dlatego przy wiecej niz jednym trafieniu `anchor_resolved`
jest `null`, a wszystkie kandydatury leza w `evidence.anchors`. Wieloznacznosc
idzie do raportu, nigdy do auto-wyboru.

```bash
python scripts/grounding_bridge.py kontrakt.json --quotes cytaty.txt --pretty
python scripts/grounding_bridge.py kontrakt.json --quotes cytaty.txt --min-kind verbatim --min-resolution span
```
Exit `10` gdy cokolwiek nie przeszlo bramki (trojstan, nie cisza).

### Czego nauczyl nas polski PDF (zmierzone 2026-08-30)

Wersja 1.x mostu gubila cytaty po cichu, bo jej normalizacja nie znala znakow,
ktore polski PDF wstawia naprawde:

| znak | gdzie wystepuje | skutek w 1.x |
|---|---|---|
| `U+2011` dywiz nielamliwy | sygnatury akt (`II‑CSK 118/24`) | cytat NIE znaleziony |
| `U+00AD` miekki dywiz | wnetrze slow w justowanym akapicie | cytat NIE znaleziony |
| `U+2212` minus, `U+200B` zerowa szerokosc | tabele, wklejki | cytat NIE znaleziony |
| przeniesienie wyrazu (`apela-
cje`) | lamanie linii | znaleziony, ale bez zakresu |

Do tego `ł`/`Ł` **nie maja dekompozycji NFD**, a reszta polskich liter ma - klasyczne
"dziala dla osmiu z dziewieciu".
`evidence.normalize_with_map()` sklada NFC **grupami** (znak bazowy + laczace) i
zwraca mape offsetow, dzieki czemu zakres wraca na ORYGINALNE glify zrodla.
Fixture wierny zjawisku: `tests/fixtures/pismo_pl_typografia.sample.json`.

## Uzycie (CLI)
```bash
cd doc-intel-contract-pl   # katalog tego skilla
python scripts/normalize.py --engine opendataloader wyjscie.json --pretty
python scripts/normalize.py --engine pdftotext dokument.txt --threshold 0.9
cat wyjscie.json | python scripts/normalize.py --engine opendataloader -
```
Exit: `0` = kontrakt schema-valid, `2` = blad wejscia / kontrakt niepoprawny (pasuje pod CI / pre-commit).

## Bramka routingu (PRZED silnikiem) - `routing_gate.py`
Odpowiada na pytanie, ktore dotad rozstrzygalo oko: **czy ten dokument w ogole da
sie przeczytac tekstowo i ktorym szczeblem**. Werdykt trojstanowy z pelnym
mianownikiem, kod wyjscia `0/10/20` (ok/degraded/failed).
```bash
python scripts/routing_gate.py AKTA.pdf --pretty
python scripts/routing_gate.py *.pdf *.docx --quiet   # tylko to, co nie jest ok
```
Lapie trzy rzeczy, ktorych zaden konwerter nie zglasza:
- **PDF mieszany** (czesc stron to skany) - kazde wyjscie tekstowe bedzie NIEPELNE,
  a wyglada na kompletne. Status `degraded` + numery stron do OCR.
- **Pelny skan** - z zainstalowanym `liteparse`: `degraded` + szczebel
  `4/liteparse-ocr-cpu` (tekst z OCR czytac tak, cytowac po weryfikacji). Bez niego:
  `failed`, eskalacja (Chandra wymaga GPU). `DOC_INTEL_NO_CPU_OCR=1` wylacza szczebel.
- **Uszkodzona czesc OOXML** - konwerter pominie ja bez slowa (zmierzone na anydoc:
  uszkodzony `chart1.xml` = exit 0, stderr pusty, znika cala tabela). Bramka nazywa
  czesc PRZED konwersja.

PDF wymaga `pip install pdf-inspector` (MIT). Jego brak = `failed`, nigdy ciche `ok`.

## Skany na CPU - `liteparse_extract.py` + `--engine liteparse`
```bash
python scripts/liteparse_extract.py SKAN.pdf --tessdata KATALOG_TESSDATA > skan.json   # exit 20 = niekompletny
python scripts/normalize.py --engine liteparse skan.json --pretty
```
Ekstraktor porownuje `total_pages` z liczba zwroconych stron (biblioteka domyslnie
obcina do 1000 stron bez bledu - na dluzszym PDF jedynym sladem jest `total_pages`). Adapter:
brakujaca strona = blok `missing_page`, raster bez tekstu = `unreadable`, `$` przed
liczba w OCR = `§` z flaga `repaired_paragraf`, pewnosc bloku = 10. percentyl
pewnosci slow (+ `weak_word`), tekst natywny = pewnosc `null` + `native_text`.
Bloki ukladu biblioteki uzywane tylko wtedy, gdy nie gubia zadnej litery ani cyfry
strony (`residual_alnum`); inaczej wlasne grupowanie + `layout_blocks_lossy`.

## Podzial teczki na pisma - `split_packet.py`
```bash
python scripts/split_packet.py TECZKA.pdf --pretty                 # exit 0/10/20
python scripts/split_packet.py strony.json --reguly contract/kategorie_pism.json
python scripts/split_packet.py TECZKA.pdf --eksport wynik/         # PDF per pismo, hash zrodla sprawdzany
```
Lokalnie, bez LLM. Decyzja per strona z jawnymi sygnalami (naglowek typu pisma,
formula "W imieniu RP", sygnatura w pierwszej linii, zmiana sygnatury, numer
strony, kontynuacja zdania, blok podpisow) - dowod w `page_decisions` jest
prawdziwy, bo silnik jest deterministyczny. Niezmienniki: kazda strona dokladnie
raz, pusta strona nie otwiera pisma, strona nieczytelna = `failed`, dwa sasiednie
pisma tej samej kategorii = dwa segmenty. Decyzje blisko progu i naglowki bez
sygnatury ida do przegladu (`degraded`).

Pomiar 2026-09-21 na teczkach zlozonych z publicznych orzeczen (granice znane z
konstrukcji; strojenie na dev, raport na odlozonym test): patrz "Status / roadmap".
Granica dowodu: teczki sa syntetyczne (tekst orzeczen dzielony na strony), bez
szumu OCR i bez pism stron (pozwy, pelnomocnictwa) - to nie jest pomiar na
prawdziwej teczce. **Na zeskanowanych aktach silnik mocno zaniza liczbe pism**
(przebieg 2026-09-21): protokoly, notatki i pisma organow nie maja struktury
orzeczenia, wiec sygnaly z tej listy na nich nie odpalaja. Wynik na aktach to
szkic granic do przejrzenia, nie podzial.

Pokrycie liczy sie od mianownika ZRODLA: sciezka PDF bierze `total_pages` z
`liteparse_extract.py`, a `split(pages, rules, total_pages=N)` daje `failed`,
gdy parser zwrocil mniej stron, niz ma plik.

## Miejsce w drabince PDF
Ten skill jest warstwa PO silniku OCR, PRZED groundingiem/redakcja:
`routing_gate -> (pdftotext|anydoc|opendataloader|liteparse|Chandra) -> [split_packet] -> doc-intel-contract-pl -> {gating do czlowieka | redaction_candidates | citation-grounding-pl}`

## Granica governance (Article III)
Skill PRZYGOTOWUJE: kolejke `review_required`, liste `redaction_candidates`,
wspolrzedne cytatu. NIE wykonuje redakcji ani akceptacji - to robi czlowiek.
Confidence-gating to kolejka, nie werdykt prawny.

**Wyjatek pozorny - `mask_for_model.py`.** Gdy fragment ma wyjsc do modelu (rung-5
vision, LLM-sedzia), kopia dostaje maske dlugosciowa: PESEL/NIP/REGON z suma kontrolna,
IBAN, e-mail, dowod, klucze API, `Bearer` -> `*` znak w znak. Oryginal, kontrakt i bloki
sa nietkniete, wiec to NIE jest redakcja dokumentu (Article III), tylko bezpiecznik na
kanale wyjscia (Article I). Dlugosc identyczna = offsety i bbox z `grounding_bridge`
pasuja do oryginalu bez przeliczania.

```bash
python scripts/mask_for_model.py < fragment.txt > fragment.dla_modelu.txt
# stderr: {"zamaskowane": 3, "kategorie": ["email", "iban", "pesel"]}
```

## Status / roadmap (spec 001)
- **US1 (MVP, DONE 2026-07-01):** adaptery opendataloader+pdftotext, kontrakt, confidence-gating, walidacja schematu.
- **US2 (DONE):** flagi PESEL/NIP/REGON (checksum)/IBAN/email/dowod + redaction_candidates; signature/stamp=sensitive_block. Flaga dowodu z wykluczeniami (pilot anonimizacji 2026-08-31): serie LEX/PLH/PLB oraz trafienie po liczebniku rzymskim (sygnatura repertorium, np. "III CRN 100001") NIE flaguja; to samo odsianie obowiazuje w `mask_for_model.py`.
- **US3 T030 (DONE):** most `grounding_bridge.py` -> zadanie citation-grounding-pl; lokalizuje cytat w blokach i doklada `anchor_resolved {page,bbox,block_id}` (cytat -> region).
- **US3 T031 (DONE):** adapter Chandra (layout DOM, bbox 0-1, block conf = MIN linii).
- **US3 T032 (DONE):** `signature.py` - heurystyka podpisu/pieczatki (dol strony + krotki + low-conf); detektor vision wstrzykiwalny (opt-in). Potwierdzenie wizualne = krok operatora w runtime.
- **EXTRA T033 (DONE):** adapter `gaius` - OCR PATRONa (Gaius-Lex `/ocr/poll`), engine_variant default/google_doc_ai.
- **T034 (DONE 2026-08-05):** adapter `chandra` dopasowany do REALNEGO formatu Chandry 2 (plaska lista `{bbox,label,content-HTML}`, 19 etykiet, BEZ confidence -> wszystko do review) + guard cichej niekompletnosci (niepuste wejscie, 0 blokow = ValueError, nie exit 0).
- **T035 (DONE 2026-08-05, kontrakt 1.1.0):** silnik `vlm-html`. Szablon promptu
  `references/prompt_vlm_ocr_pl.md` zmusza dowolny VLM do emisji constrained HTML
  z atrybutami data-label i data-bbox - wzorzec Chandry - a adapter parsuje to
  do kontraktu. VLM etykietuje `signature` i `stamp` wprost, wiec podpis i
  pieczatka same laduja w redaction_candidates. Do tego `degeneracja.py`:
  detektor zapetlenia generacji, w normalize daje flage `degenerate_tail`
  i ostrzezenie na stderr.
- **T036 (DONE 2026-08-30, kontrakt 1.2.0, most 2.0.0):** warstwa dowodowa
  `evidence.py` - rodzaj dowodu x rozdzielczosc zamiast jednej liczby, mapa
  offsetow (zakres znakowy wracajacy na ORYGINALNE glify zrodla), bramki
  dystynktywnosci fail-empty z jawnym `match_count`, gating dwuosiowy z
  werdyktem trojstanowym. Do tego JEDEN DOM reguly normalizacji
  (`contract/normalizacja.cases.json`) czytany przez oba runtime'y - Python
  i `citation-grounding-pl` (Node), gdzie ta sama regula miala wlasna
  implementacje i **szesc z osmiu** tych samych luk. Inspiracja: warstwa
  proweniencji docling-graph (MIT/IBM) - wziete idee, nie zaleznosc.
- **229 testow zielonych** (contract+pii+grounding+chandra+chandra2+gaius+signature+vlm-html+degeneracja+evidence+konformancja+kotwica dokumentacji+liteparse+split_packet). Sciezka normalizacji zero-dep Python stdlib; `liteparse` tylko w ekstraktorze.
- **Pomiar OCR 2026-09-21 (liteparse, publiczny wyrok SN).** Odsetek blednych znakow:
  0,5% (skan 300 dpi), 1,3% (bez jawnego DPI), 3,5% (skan pogorszony). Znak `§`
  odzyskany 28/28, zero falszywych trafien.
- **Pomiar podzialu teczek 2026-09-21.** Teczki zlozone z publicznych orzeczen,
  30 na wariant, zbior test odlozony od strojenia. Dokladnie podzielone 80/90
  (skrzynka mieszana 28/30, sasiednie pisma tej samej kategorii 25/30, wyrok +
  uzasadnienie tej samej sprawy 27/30). Precyzja granic 0,95-1,0, czulosc 0,94-1,0.
- **Porownanie z Jevem 2026-09-21** (hostowany model, ktorego uzywa DocJev), te same
  90 teczek, nasze kategorie i polskie orzeczenia - nie reguly i dane autora DocJev.
  Samo pytanie "czy strona zaczyna nowe pismo": 63/90 dokladnie, precyzja 0,99,
  czulosc 0,91 (2 falszywe granice na 1720 kontynuacji). Z regula DocJev "segment on
  a category change or source-document boundary": 0/90 - kategoria strony myli sie
  (strony wyrokow oznaczone jako uzasadnienie), a kazda pomylka tnie teczke. Wniosek
  dla tego skilla: granice z pytania o granice, kategoria raz na pismo. Koszt 0,15 USD.
- **Czego pomiar nie dowodzi.** Zbior test uzyto dwa razy (druga wersja po jednej
  poprawce z testu jednostkowego; obie daly 80/90). Z blednych podzialow 3/10 wyszly
  ze statusem `ok`, wiec trojstan nie lapie jeszcze wszystkich wlasnych pomylek.
- **Bramka kotwicy dokumentacji** (`tests/test_dokumentacja_zakotwiczona.py`):
  SKILL.md jest CZYTANY i konfrontowany z kodem - wersja kontraktu, enum
  silnikow, obie tabele sil, kody wyjscia werdyktu, flagi CLI, sciezki plikow
  i liczba testow. Dziewiec mutacji sprawdzonych na czerwono, zero luk.
  Dokumentacja nie moze juz zdryfowac po cichu.

**Granica dowodu (stan 2026-08-05).** Testy dowodza, ze parser czyta format
zgodnie ze specyfikacja - nie dowodza, ze zywy model ta specyfikacje stosuje.
Fixture `vlm_html.sample.html` napisalismy sami, wiec sprawdza adapter, nie
posluszenstwo VLM. Fixture `chandra2.sample.json` odwzorowuje format odczytany
z upstreamu `chandra/output.py`, ale bez przebiegu na realnej Chandrze.
Zanim silnik `vlm-html` pojdzie na akta, potrzebny jest przebieg bojowy:
prawdziwy skan, prawdziwy model, porownanie ze zrodlem - zgodnosc formatu
mierzy sie cudzym czytnikiem.

Render skanu do obrazow przed silnikiem VLM (flatten AcroForm + dynamiczne DPI,
pypdfium2 opcjonalnie): przepis w `references/render_skanu_pl.md`. UWAGA:
walidacja podpisu kwalifikowanego (skill `waliduj-podpis-pdf-pl`) PRZED flatten.

Most do groundingu:
```bash
python scripts/normalize.py --engine opendataloader wyjscie.json > kontrakt.json
python scripts/grounding_bridge.py kontrakt.json --quotes cytaty.txt --pretty
# -> {items:[{quote, source_text, anchor_resolved:{page,bbox,block_id,span},
#             evidence, flags}], summary:{total, located_single, ambiguous,
#             unlocated, gate_passed}}   -> ground-citations.mjs
```

Governance: `.matematic/konstytucja.md` + `.matematic/spec/001-output-contract-mvp/`.

## Czego NIE robi
- NIE jest silnikiem OCR (nie zastepuje Chandry).
- NIE wykonuje redakcji/akceptacji (przygotowuje, czlowiek decyduje).
- NIE wola cloud OCR (Mistral/Azure/Google) - zlamaloby Article I.
- NIE ocenia merytorycznie tresci prawnej.

## Testy
```bash
python -m unittest discover -s tests -v
```
Zero zaleznosci npm/pip (czysty Python 3.11+ stdlib).
