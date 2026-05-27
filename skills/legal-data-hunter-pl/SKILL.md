---
name: legal-data-hunter-pl
description: >
  Catalog and bulk-harvest layer for Polish legal data, built on the Legal Data
  Hunter project (worldwidelaw/legal-sources). Use this skill whenever the user
  wants to know which Polish legal sources are already available, bulk-download
  Polish legislation, case law or regulator decisions (UODO, UOKiK, KNF, UKE,
  URE, KIO, NSA, Trybunal Konstytucyjny, Sad Najwyzszy, Dziennik Urzedowy, Sejm
  ELI), build a local RODO-safe corpus of Polish law, or decide whether MateMatic
  needs to build its own connector for a gap. Trigger on "Legal Data Hunter",
  "pokrycie polskiego prawa", "zaciagnij ustawy", "harvest orzecznictwa",
  "ktore zrodla mamy", "luka w zrodlach". Companion to saos-orzecznictwo (live
  query) and eu-sparql-search (EU law).
---

# Legal Data Hunter - warstwa katalogu zrodel polskiego prawa

Warstwa "katalog + harvest" projektu legal AI MateMatic. Mapuje, co z polskiego
prawa jest juz dostepne gotowymi kolektorami, i wskazuje luki do uzupelnienia
wlasnymi konektorami.

## Czym to jest

`worldwidelaw/legal-sources` (Legal Data Hunter) - otwarte repo skryptow zbierania
otwartych danych prawnych z 110+ krajow (960+ kolektorow). Kazdy kolektor pobiera
i normalizuje dane z oficjalnego portalu/API rzadowego do wspolnego schematu.

- Repo: https://github.com/worldwidelaw/legal-sources
- Dashboard + hostowane Search API (16 mln dokumentow): https://legaldatahunter.com
- **Licencja repo: AGPL-3.0** (skrypty). Licencja DANYCH jest per-zrodlo - patrz
  blok `license:` w `config.yaml` danego zrodla (np. SAOS = public domain).

## Lokalna kopia

Sparse-clone polskiej czesci jest w `~/legal-data-hunter/`
(17 MB; `sources/PL/` + framework `common/` + `runner.py`). Aktualizacja:

```bash
cd ~/legal-data-hunter && git pull
```

Pelne repo to 388 MB - NIE klonuj calosci, sparse-checkout wystarcza:
```bash
git clone --filter=blob:none --no-checkout --depth 1 \
  https://github.com/worldwidelaw/legal-sources.git legal-data-hunter
cd legal-data-hunter
git config index.sparse true
git sparse-checkout init --cone --sparse-index
git sparse-checkout set sources/PL common docs
git checkout
```
> ⚠️ `--sparse-index` jest KONIECZNY na Windows - bez niego `git checkout` wywala
> sie na sciezkach z `:` w nazwie (US/Louisiana) mimo cone-mode.

## Pokrycie polskiego prawa (16 zrodel, stan 2026-05-19)

Pelna tabela ze statusem, API i licencja: `references/coverage-pl.md`.

**Dziala (13 zrodel)** - legislacja, orzecznictwo, regulatorzy, podatki:
- Legislacja: `DziennikUrzedowy`, `Sejm` (ELI API, 96K aktow - oznaczony untested)
- Orzecznictwo: `ConstitutionalCourt` (TK), `SupremeCourt` (SN), `NSA`, `KIO`,
  `SAOS` (hurtowe archiwum wszystkich sadow)
- Regulatorzy: `KNF`, `UODO`, `UOKIK`, `UKE`, `URE`
- Podatki: `KIS-EUREKA`, `NSA-Tax`

**Zablokowane / luki (3 zrodla)**:
- `SN` - sn.pl w konserwacji, alternatywa SAOS zawiesila sie (osobne zrodlo
  `SupremeCourt` dziala - ta pozycja to redundantny, zepsuty wariant)
- `MF` - interpretacje podatkowe sip.mf.gov.pl, API EUREKA geo-blokowane/WAF
  (czesciowo zastepuje je dzialajacy `KIS-EUREKA`)

To pokrywa wieksza czesc opublikowanego polskiego prawa - stad teza "~80%".

## Czego TU NIE MA - luki do uzupelnienia przez MateMatic

| Luka | Dlaczego | Plan MateMatic |
|---|---|---|
| Biezace orzeczenia sadow powszechnych | LDH ma je tylko przez SAOS, a SAOS to archiwum konczace sie ~2018 | wlasny konektor do portali orzeczen `orzeczenia.ms.gov.pl` |
| Interpretacje podatkowe MF | zrodlo `MF` zablokowane (WAF/geo) | wlasny konektor lub oprzec sie na `KIS-EUREKA` |
| KRS - rejestr przedsiebiorcow | brak w `sources/PL` w ogole | skille `gaius-lex` (KRS) juz w MateMatic; ew. wlasny konektor MCP |
| Monitor Polski | jawnie nieindeksowany | do rozwazenia |
| Wyszukiwanie interaktywne (live query) | kolektory LDH to HARVESTERY (hurt), nie API zapytan | wlasne konektory zapytan: skill `saos-orzecznictwo`, przyszle ISAP/KRS |

## Jak to sie laczy z reszta architektury

Trzy warstwy dostepu do polskiego prawa - **nie konkuruja, uzupelniaja sie**:

1. **Harvest / katalog (ta warstwa)** - Legal Data Hunter. Hurtowy zaciag ~13
   dzialajacych zrodel do lokalnego korpusu RODO-safe. Off-line, batch.
2. **Live query** - wlasne konektory MateMatic. Skill `saos-orzecznictwo`
   (interaktywne wyszukiwanie orzeczen), przyszle ISAP/KRS. To jest moat.
3. **Prawo UE** - skill `eu-sparql-search` (EUR-Lex/CJEU).

Kolektor SAOS w LDH (`sources/PL/SAOS`) uzywa tylko Dump API (hurtowe archiwum,
append-only). Skill `saos-orzecznictwo` uzywa Search/Browse API (zapytania na
zywo). To NIE jest dublowanie - jedno zasila lokalny indeks, drugie odpowiada na
pytanie tu i teraz.

> ⚠️ **Hostowane Search API legaldatahunter.com to zaleznosc chmurowa** - sprzeczna
> z teza zero-cloud MateMatic (RODO-safe self-hosted stack). Do produktu dla
> kancelarii uruchamiaj kolektory lokalnie i trzymaj korpus u siebie. Hostowane
> API jest OK tylko do szybkiego rozpoznania/dev.

## Uruchamianie kolektorow

Framework: Python. Zaleznosci w `requirements.txt` (core: `requests`, `pyyaml`,
`beautifulsoup4`, `lxml`; ciezsze opcjonalne: `playwright`, `psycopg2-binary`,
`opendataloader-pdf`). Core jest juz zainstalowany na tej maszynie.

```bash
cd ~/legal-data-hunter
python runner.py status              # przeglad stanu projektu
python runner.py sample PL/SAOS      # tryb probny - 10+ rekordow do walidacji
python runner.py test PL/UODO        # test kolektora
python runner.py fast PL/KIO         # bootstrap_fast
```

Struktura kazdego zrodla `sources/PL/<Nazwa>/`:
- `bootstrap.py` - kolektor: `fetch_all()`, `fetch_updates()`, `normalize()`
- `config.yaml` - metadane, API, rate-limit, schema, licencja danych
- `status.yaml` - historia uruchomien (jesli byl uruchamiany)
- `sample/` - 10+ rekordow do walidacji
- `retrieve.py` - resolver referencji ("art. 415 kc" -> dokument), o ile istnieje

> ⚠️ `common/pdf_extract.py` ma `preload_existing_ids()` odpytujace hostowana baze
> Neon Postgres (idempotencja pipeline'u LDH). Przy harveScie dla MateMatic
> uruchamiaj w trybie bez tego checku - nie wystawiaj danych kancelarii do Neon.

## Workflow

1. **Pytanie "czy mamy zrodlo X?"** - sprawdz `references/coverage-pl.md`. Jest
   -> uzyj kolektora. Nie ma / zablokowane -> luka, patrz tabela luk wyzej.
2. **Hurtowy zaciag** - `runner.py sample` na probe, potem pelny `fetch_all()`;
   zapis do lokalnego korpusu (SQLite + vector store, patrz
   wewnetrzne KGLF MateMatic).
3. **Synchronizacja** - kolektory legislacyjne robia upsert (akty sie zmieniaja),
   case-law append-only z dedup. Cyklicznie `fetch_updates()`.
4. **Zapytanie na zywo** - NIE przez LDH; uzyj `saos-orzecznictwo` lub innego
   konektora zapytan.
5. **Luka** - jesli zrodla brak albo jest zablokowane, to kandydat na wlasny
   konektor MateMatic. Najpierw skill (wzorem `saos-orzecznictwo`), potem MCP.

## Reguly

- Repo AGPL-3.0 - skrypty kolektorow sa copyleft. Dane wyjsciowe maja wlasne
  licencje (per `config.yaml`). Uruchamianie kolektorow jako osobnych procesow i
  uzywanie zebranych danych nie czyni powloki MCP MateMatic dzielem zaleznym -
  spojne z insightem licencyjnym o MCP w otwartym ekosystemie MateMatic.
- Do produktu dla kancelarii: kolektory lokalnie, korpus lokalnie. Bez Neon, bez
  hostowanego Search API.
- README polskiej sekcji w repo bywa nieaktualny (widziano date 2026-02-21 i
  spis 4 zrodel przy realnych 16) - ufaj drzewu `sources/PL/` i `status.yaml`,
  nie tekstowi README.
- Statusy w `references/coverage-pl.md` to migawka 2026-05-19 - przy waznych
  decyzjach odswiez (`git pull` + `runner.py status`).
