# Legal Data Hunter - pokrycie polskiego prawa

Migawka 2026-05-19. Zrodlo: `worldwidelaw/legal-sources`, katalog `sources/PL/`.
Odswiezanie: `cd ~/legal-data-hunter && git pull && python runner.py status`.

16 zrodel polskich. Status czytany z obecnosci `bootstrap.py` + `sample/` +
`status.yaml` (historia uruchomien) oraz z README poszczegolnych zrodel.

## Pelna tabela

| Zrodlo | Typ danych | Instytucja / portal | Status | Ostatni run |
|---|---|---|---|---|
| `ConstitutionalCourt` | case_law | Trybunal Konstytucyjny | dziala | 2026-02-13 |
| `SupremeCourt` | case_law | Sad Najwyzszy | dziala | 2026-02-21 |
| `NSA` | case_law | Naczelny Sad Administracyjny | dziala | 2026-02-24 |
| `NSA-Tax` | case_law | NSA - sprawy podatkowe | dziala | 2026-03-22 |
| `KIO` | case_law | Krajowa Izba Odwolawcza (zamowienia publ.) | dziala | 2026-04-18 |
| `SAOS` | case_law | SAOS - hurtowe archiwum wszystkich sadow | dziala | 2026-04-29 |
| `DziennikUrzedowy` | legislation | Dzienniki urzedowe | dziala | 2026-02-10 |
| `Sejm` | legislation / proceedings | Sejm ELI API (96K+ aktow od 1918) | untested | brak |
| `KIS-EUREKA` | tax interpretations | KIS - interpretacje podatkowe | dziala | 2026-03-30 |
| `KNF` | regulator | Komisja Nadzoru Finansowego | dziala* | brak status.yaml |
| `UODO` | regulator / doctrine | Urzad Ochrony Danych Osobowych | dziala* | brak status.yaml |
| `UOKIK` | regulator | Urzad Ochrony Konkurencji i Konsumentow | dziala* | brak status.yaml |
| `UKE` | regulator | Urzad Komunikacji Elektronicznej | dziala* | brak status.yaml |
| `URE` | regulator | Urzad Regulacji Energetyki | dziala* | brak status.yaml |
| `SN` | case_law | Sad Najwyzszy przez sn.pl | **ZABLOKOWANE** | - |
| `MF` | tax interpretations | Min. Finansow, sip.mf.gov.pl / EUREKA | **ZABLOKOWANE** | - |

`dziala*` = ma `bootstrap.py` + `config.yaml` + `sample/` z rekordami, ale brak
`status.yaml` w repo (zrodlo dodane pozniej, nie wpisano historii uruchomien).
Przed produkcyjnym uzyciem przepusc `runner.py sample`.

## Zablokowane - szczegoly

- **`SN`** - status `Blocked`. "sn.pl search temporarily blocked (maintenance).
  SAOS API hangs on all endpoints. Both access methods unavailable 2026-03-22."
  Orzecznictwo SN pokrywa osobne, dzialajace zrodlo `SupremeCourt`.
- **`MF`** - status `Blocked`. "EUREKA API (eureka.mf.gov.pl/api/public/v1/)
  times out consistently - likely geo-blocked or WAF-protected." Interpretacje
  podatkowe czesciowo pokrywa dzialajace `KIS-EUREKA`.

## Typy danych a strategia aktualizacji

- **legislation** (mutowalne) - akty sie zmieniaja; ten sam ID, nowa tresc;
  strategia: upsert z wersjonowaniem.
- **case_law** (niezmienne) - orzeczenia po publikacji sie nie zmieniaja;
  strategia: append-only z dedupem.

## Schemat wyjsciowy (wspolny)

Kazdy kolektor normalizuje do wspolnego schematu - klucze m.in.: `_id`
(primary key), `_source`, `_type`, `title`, `text` (tresc), `date`, `url`,
plus pola specyficzne (np. SAOS: `case_number`, `court_type`, `judgment_type`,
`judges`). Dokladny `schema.key_fields` jest w `config.yaml` zrodla.

## Uwaga o SAOS

Kolektor `sources/PL/SAOS` deklaruje w `config.yaml` pokrycie ADMINISTRATIVE i
"~500K+ judgments" - to optymistyczne. Realnie (test 2026-05-19, patrz skill
`saos-orzecznictwo`): `courtType=ADMINISTRATIVE` zwraca pustke, a baza konczy sie
~2016-2018. Kolektor LDH zrobil dotad tylko run probny (12 rekordow,
`total_records: 0`). SAOS traktuj jako archiwum historyczne, nie biezace zrodlo.

## Co z tego wynika dla MateMatic

- Legislacja PL: pokryta (Sejm ELI + Dziennik Urzedowy). Sejm wymaga walidacji
  (`untested`). To zastepuje osobny konektor ISAP - ELI API to nastepca ISAP.
- Orzecznictwo wyzszych instancji (TK, SN, NSA, KIO): pokryte.
- Orzecznictwo sadow powszechnych biezace: LUKA - tylko archiwum przez SAOS.
- Regulatorzy (KNF, UODO, UOKiK, UKE, URE): pokryci.
- Podatki: KIS-EUREKA + NSA-Tax dzialaja; MF zablokowany.
- KRS: brak w LDH - osobna sciezka (`gaius-lex`).
