---
name: saos-orzecznictwo
description: >
  Search and retrieve Polish court judgments via the SAOS REST API (System Analizy
  Orzeczen Sadowych, Fundacja ePanstwo). Use this skill whenever the user wants to
  find Polish case law - orzeczenia, wyroki, postanowienia - from sady powszechne,
  Sad Najwyzszy, Trybunal Konstytucyjny or Krajowa Izba Odwolawcza; search by case
  number (sygnatura), date range, court, judge, keyword, legal basis or referenced
  regulation; fetch full judgment text; or bulk-download the judgment corpus. Also
  trigger on "orzecznictwo PL", "SAOS", "szukaj wyroku", "sygnatura akt", "baza
  orzeczen". Companion to eu-sparql-search (which covers EU law / CJEU).
---

# SAOS - Polish Case Law Search

Polski konektor orzecznictwa dla projektu legal AI MateMatic. Domyka pare z
`eu-sparql-search` (CJEU / prawo UE): SAOS pokrywa sady krajowe RP.

## Endpoint

```
https://www.saos.org.pl/api
```

Publiczne, otwarte REST API. **Bez klucza, bez autoryzacji.** Zwraca JSON.
Instancja testowa: `https://saos-test.icm.edu.pl/api` (nie uzywac do produkcji).

API ma trzy czesci:

| Czesc | Sciezka | Do czego |
|---|---|---|
| **Search API** | `/api/search/judgments` | przeszukiwanie wg kryteriow, zwraca skroty + `textContent` |
| **Browse API** | `/api/judgments/{id}` | pelny obiekt pojedynczego orzeczenia |
| **Dump API** | `/api/dump/judgments` | hurtowe pobranie calej bazy + synchronizacja |

## Zakres bazy (co SAOS faktycznie indeksuje)

| courtType | Sad | Status |
|---|---|---|
| `COMMON` | sady powszechne (rejonowe, okregowe, apelacyjne) | pelny |
| `SUPREME` | Sad Najwyzszy | pelny |
| `CONSTITUTIONAL_TRIBUNAL` | Trybunal Konstytucyjny | pelny |
| `NATIONAL_APPEAL_CHAMBER` | Krajowa Izba Odwolawcza (zamowienia publiczne) | pelny |
| `ADMINISTRATIVE` | sady administracyjne (WSA/NSA) | **PUSTY** - SAOS nie indeksuje; uzyj orzeczenia.nsa.gov.pl |

> ⚠️ **Zakres SAOS - fakty (zweryfikowane na zywym API 2026-05-19).** SAOS
> zawiera orzecznictwo biezace, nie tylko archiwalne: ~17 tys. orzeczen z 2024
> i ~14 tys. z 2025+. Pokrycie jest jednak **nierowne wg typu sadu** i zalezy od
> tego, ktore sady przekazuja orzeczenia. Realne ograniczenia: (1) `ADMINISTRATIVE`
> PUSTY - brak WSA/NSA, wiec SAOS nie ma merytorycznego orzecznictwa RODO
> (domena sadow administracyjnych) - odsylaj do `orzeczenia.nsa.gov.pl`;
> (2) **artefakty OCR** zaburzaja daty (np. "3013-12-04"), psujac sortowanie DESC -
> filtruj `judgmentDateTo` data biezaca i weryfikuj date/sygnature w zrodle.
> SAOS jest mocny do badania linii orzeczniczej, precedensow i wyszukiwania
> pelnotekstowego po orzecznictwie SN, sadow powszechnych, TK i KIO.

## Search API - parametry

`GET /api/search/judgments?<param>=<value>&...`

| Parametr | Opis | Przyklad |
|---|---|---|
| `all` | wyszukiwanie pelnotekstowe (po tresci orzeczenia) | `all=RODO` |
| `legalBase` | podstawa prawna | `legalBase=art. 415 kc` |
| `referencedRegulation` | przywolany akt prawny | `referencedRegulation=ustawa o ochronie danych` |
| `judgeName` | nazwisko sedziego | `judgeName=Kowalski` |
| `caseNumber` | sygnatura akt | `caseNumber=I ACa 772/13` |
| `courtType` | typ sadu (tabela wyzej) | `courtType=SUPREME` |
| `judgmentTypes` | typ orzeczenia (mozna wiele) | `judgmentTypes=SENTENCE` |
| `keywords` | slowa kluczowe (tagi tematyczne SAOS) | `keywords=zadoscuczynienie` |
| `judgmentDateFrom` / `judgmentDateTo` | zakres dat orzeczenia `YYYY-MM-DD` | `judgmentDateFrom=2020-01-01` |
| `ccCourtId` / `ccDivisionId` | id sadu powszechnego / wydzialu | `ccCourtId=154` |
| `scChamberId` / `scDivisionId` | id izby / wydzialu SN | |
| `pageSize` | wynikow na strone, **min 10, max 100** | `pageSize=20` |
| `pageNumber` | numer strony, od 0 | `pageNumber=0` |
| `sortingField` | `JUDGMENT_DATE` \| `DATABASE_ID` \| `JUDGMENT_TYPE` | `sortingField=JUDGMENT_DATE` |
| `sortingDirection` | `ASC` \| `DESC` | `sortingDirection=DESC` |

`judgmentTypes`: `DECISION`, `RESOLUTION`, `SENTENCE`, `REGULATION`, `REASONS`.

Wartosci tekstowe parametrow **musza byc URL-encoded** (spacje -> `%20`).

### Struktura odpowiedzi Search

```json
{
  "links": [{"rel":"self","href":"..."}, {"rel":"next","href":"..."}],
  "items": [ { "id":31345, "href":"...", "courtType":"COMMON",
               "courtCases":[{"caseNumber":"I ACa 772/13"}],
               "judgmentType":"SENTENCE", "judges":[...],
               "textContent":"...", "keywords":[...], "judgmentDate":"2013-12-04",
               "division":{...} } ],
  "info": { "totalResults": 3545 }
}
```

`info.totalResults` = laczna liczba trafien (do paginacji). `links[rel=next]` =
gotowy URL nastepnej strony.

## Browse API - pelne orzeczenie

`GET /api/judgments/{id}` -> `{"links":[...], "data":{...}}`

Pola w `data`: `id`, `courtType`, `courtCases`, `judgmentType`, `judgmentDate`,
`judges`, `source` (link do oryginalu w portalu sadu), `courtReporters`,
`decision`, `summary`, `textContent` (pelna tresc), `legalBases`,
`referencedRegulations`, `keywords`, `referencedCourtCases`, `receiptDate`,
`meansOfAppeal`, `judgmentResult`, `lowerCourtJudgments`, `division`.

Powiazane obiekty (osadzane w `division`): `/api/commonCourts/{id}`,
`/api/ccDivisions/{id}`, `/api/scChambers/{id}`. Pobiera sie je pojedynczo po id;
**listowanie zbiorcze `/api/commonCourts` zwraca 404** - id sadu bierz z pola
`division` w wyniku orzeczenia.

## Dump API - hurtowe pobranie

`GET /api/dump/judgments?pageSize=100&pageNumber=0` - cala baza, strona po stronie.
Parametry synchronizacji: `judgmentStartDate`, `judgmentEndDate`,
`sinceModificationDate` (przyrostowa aktualizacja lokalnej kopii). `pageSize` min 10.
Uzywaj do budowy lokalnego, RODO-safe indeksu (zgodnie z `matematic-stack-zero-cloud`).

## Jak wykonywac zapytania

### Metoda preferowana: helper Python

Skrypt `scripts/saos.py` w tym skillu owija API. Z bash_tool:

```bash
python ~/.claude/skills/saos-orzecznictwo/scripts/saos.py search \
  --all "RODO" --court SUPREME --from 2023-01-01 --size 10
python ~/.claude/skills/saos-orzecznictwo/scripts/saos.py get 352475
python ~/.claude/skills/saos-orzecznictwo/scripts/saos.py case "I ACa 772/13"
```

### Metoda inline (gdy trzeba wlasnej logiki)

```python
import urllib.parse, urllib.request, json

def saos_search(**params):
    qs = urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    url = f"https://www.saos.org.pl/api/search/judgments?{qs}"
    with urllib.request.urlopen(url, timeout=35) as r:
        return json.loads(r.read())

def saos_get(jid):
    url = f"https://www.saos.org.pl/api/judgments/{jid}"
    with urllib.request.urlopen(url, timeout=35) as r:
        return json.loads(r.read())["data"]

res = saos_search(all="RODO", courtType="SUPREME", pageSize=10,
                   sortingField="JUDGMENT_DATE", sortingDirection="DESC")
print(res["info"]["totalResults"])
```

> Uzywaj `curl` / Python `urllib` w bash_tool, nie `web_fetch` - URL-e SAOS z
> zapytan programowych zostana odrzucone przez ograniczenia `web_fetch`.

## Workflow

1. **Ustal intencje** - czego szuka uzytkownik: sygnatura, temat, sad, sedzia, data?
2. **Zmapuj na parametry** Search API (tabela wyzej). Sygnatura -> `caseNumber`;
   temat -> `all` (pelnotekstowe) lub `keywords` (tagi); akt -> `referencedRegulation`.
3. **Wykonaj** przez `scripts/saos.py` lub inline Python. Zacznij `pageSize=10`.
4. **Pokaz wyniki** jako czytelna tabela: sygnatura, sad, data, typ, fragment.
5. **Pobierz pelna tresc** przez Browse API, gdy uzytkownik chce konkretne orzeczenie.
6. **ZAWSZE cytuj zrodlo** - klikalny link do orzeczenia (sekcja nizej).
7. **Zaproponuj dalej** - kolejna strona, szerszy zakres dat, inny sad, dump lokalny.

## Cytowania - zawsze weryfikowalny link

Kazda odpowiedz oparta na tresci orzeczenia MUSI konczyc sie zrodlem. Bez tego
uzytkownik nie odroznia realnego cytatu od halucynacji.

**Strona orzeczenia w SAOS** (kanoniczny, stabilny link dla czlowieka):
```
https://www.saos.org.pl/judgments/{id}
```

**Surowy obiekt API** (do weryfikacji programowej):
```
https://www.saos.org.pl/api/judgments/{id}
```

**Oryginal w portalu sadu** - pole `source.judgmentUrl` w obiekcie Browse API
(prowadzi do oryginalnego orzeczenia na stronie sadu).

Format bloku zrodla na koncu odpowiedzi:

```
**Zrodlo:** Sad Apelacyjny w Lodzi, wyrok z 4.12.2013, sygn. I ACa 772/13
- SAOS: https://www.saos.org.pl/judgments/31345
- Oryginal sadu: http://api.orzeczenia.wroclaw.sa.gov.pl/...
```

## Reguly i pulapki

- API jest **publiczne, bez auth**. Nie wymyslaj kluczy.
- `pageSize` ma **twardy dolny limit 10** (mniej -> `400 WRONG REQUEST PARAMETER`),
  gorny 100. Nie da sie pobrac 1 wyniku - bierz 10 i tnij.
- `courtType=ADMINISTRATIVE` zwraca **pustke** - SAOS nie indeksuje sadow
  administracyjnych. Dla WSA/NSA odeslij do `orzeczenia.nsa.gov.pl`.
- **Dane zawieraja artefakty OCR** - w `textContent` i czasem w `judgmentDate`
  trafiaja sie literowki i bledne daty (widziano `judgmentDate":"3013-12-04"` i
  `"2101-04-14"` zamiast 2013/2016). Przy datach z pojedynczego rekordu sprawdzaj
  zdrowy rozsadek; sygnatura akt jest pewniejsza niz `judgmentDate`.
- **Zaburzone daty psuja sortowanie** - `sortingField=JUDGMENT_DATE&DESC` wypycha
  na gore rekordy z bledna data w przyszlosci (`3013`, `2101`). Pierwszy wynik nie
  musi byc najnowszym realnym orzeczeniem. Do "najnowszych" filtruj jawnie
  `judgmentDateTo` i odsiewaj absurdy.
- **Baza jest historyczna** (patrz ramka w "Zakres bazy") - nie obiecuj
  uzytkownikowi orzeczen z biezacego roku.
- **`textContent` zawiera znaczniki HTML** (`<p>`, `<div>`, `<h2>`) oraz - w
  wynikach Search dla `all` - tagi `<em>` wokol trafien. Do czystego tekstu
  zdejmij znaczniki (`html.parser` / regex) przed cytowaniem.
- API **nie ma operatorow boolowskich** w `all` - to proste wyszukiwanie
  pelnotekstowe. Zlozone zapytania rozbijaj na kilka wywolan i lacz po stronie klienta.
- **Brak listowania sadow** (`/api/commonCourts` -> 404). Id sadu/wydzialu czytaj
  z pola `division` w wynikach orzeczen.
- Zawsze dawaj `LIMIT` przez `pageSize` i paginuj `pageNumber` - nie probuj
  zaciagnac calej bazy jednym zapytaniem (od tego jest Dump API).
- Wartosci tekstowe parametrow URL-encoduj (`urllib.parse.urlencode` robi to sam).
- SAOS to **metadane + tresc orzeczen sadow**, nie akty prawne. Legislacje PL
  pokrywa skill `legal-data-hunter-pl` (Sejm ELI + Dziennik Urzedowy); prawo UE -
  `eu-sparql-search`.

## Miejsce w architekturze

Ten skill to warstwa **live query** dla SAOS - interaktywne wyszukiwanie orzeczen
przez Search/Browse API. Komplementarny do:

- **`legal-data-hunter-pl`** - warstwa harvestu/katalogu. Ma wlasny kolektor SAOS,
  ale uzywa tylko Dump API (hurtowe archiwum do lokalnego korpusu). Tam tez mapa
  16 zrodel polskiego prawa (legislacja, regulatorzy, podatki) i lista luk.
- **`eu-sparql-search`** - prawo UE / orzecznictwo CJEU.

Realna luka: merytoryczne orzecznictwo sadow administracyjnych (WSA/NSA) - SAOS
go nie indeksuje. Dla orzecznictwa administracyjnego (w tym RODO/decyzje UODO)
potrzebny osobny konektor do `orzeczenia.nsa.gov.pl`.

## Szczegoly

Pelna lista pol obiektow, enumeracji i przykladow zapytan: `references/api.md`.

## Dziennik szlifu

- **2026-05-19 (wieczor)** - korekta bledu. Stare ustalenie "SAOS to archiwum
  historyczne, ingestja zatrzymana ~2016-2018" bylo BLEDNE. Weryfikacja na zywym
  API: ~17 tys. orzeczen z 2024, ~14 tys. z 2025+. Poprawiono blok zakresu w
  SKILL.md i "Znane ograniczenia" w api.md - realne ograniczenia to brak WSA/NSA
  i artefakty OCR w datach, nie "brak danych biezacych". Ten sam blad poprawiony
  rownolegle w serwerze MCP `mcp-saos` (6 disclaimerow + filtr judgmentDateTo).
