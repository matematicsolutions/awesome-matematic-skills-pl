---
name: webwright-legal-pl
description: Pobierz orzeczenia i akty prawne z polskich serwisów sądowych niedostępnych przez MCP (orzeczenia.ms.gov.pl, sn.pl, trybunal.gov.pl) używając Playwright. Użyj gdy potrzebujesz wyroku po sygnaturze z MS, SN lub TK, albo gdy mcp-saos nie ma danego orzeczenia.
allowed-tools: Bash, Read, Write, Edit
---

# webwright-legal-pl

Skill do pobierania orzeczeń z polskich serwisów prawnych niedostępnych
przez istniejące MCP konektory. Wrapper nad Webwright
(Playwright Firefox, code-as-action) wyspecjalizowany pod polskie domeny.

## Kiedy używać

| Serwis | URL | Kiedy |
|--------|-----|-------|
| Portal Orzeczeń MS | orzeczenia.ms.gov.pl | orzeczenia sądów powszechnych (SA, SO, SR) niedostępne w mcp-saos |
| Sąd Najwyższy | www.sn.pl/orzecznictwo | wyroki SN, gdy mcp-saos / SAOS nie maja konkretnego orzeczenia (uzupelnienie zrodla, nie zastapienie) |
| Trybunał Konstytucyjny | trybunal.gov.pl | wyroki TK |
| EUR-Lex PL | eur-lex.europa.eu | rozporządzenia EU w wersji PL (RODO, AI Act) |

## Zależności (one-time setup)

Sklonuj Webwright do dowolnego katalogu i zainstaluj Playwright:

```bash
git clone https://github.com/microsoft/webwright --depth=1
pip install playwright
playwright install firefox
```

Ścieżkę do lokalnego klonu Webwright ustaw raz w zmiennej środowiskowej
`WEBWRIGHT_HOME` - skille i skrypty w tym pakiecie odczytują ją zamiast
hardcodowanych ścieżek.

## Tryby działania

### 1. Pobierz orzeczenie po sygnaturze (`/webwright-legal-pl:orzeczenie`)

Referencyjny skrypt: [`scripts/fetch_orzeczenie.py`](scripts/fetch_orzeczenie.py) (gotowy do uruchomienia, ~150 wierszy, Playwright Chromium, sn.pl).

```bash
python scripts/fetch_orzeczenie.py --sygnatura "III CZP 1/24" --out outputs/orzeczenia
# -> outputs/orzeczenia/iii-czp-1-24/orzeczenie.md + meta.json + 3 screenshoty
```

Walidacja na żywym sn.pl (2026-05-27):

| Sygnatura | Wynik | Sparsowano |
|---|---|---|
| `I CSK 100/22` | postanowienie SN z 18 marca 2022 r. | data 2022-03-18, link do PDF |
| `III CZP 1/24` | postanowienie SN z 4 lipca 2024 r. | data 2024-07-04, link do PDF |

Oba post-2016, czyli poza zasięgiem mcp-saos. Skrypt parsuje typ orzeczenia (wyrok/postanowienie/uchwala) z nagłówka wyników i datę z polskiej formy ("z dnia 18 marca 2022 r." -> ISO 2022-03-18). Robi 3 screenshoty (formularz / wyniki / detal) jako dowód wizualny dla self-verify.

Dla nowej domeny (orzeczenia.ms.gov.pl, trybunal.gov.pl) skopiuj `fetch_orzeczenie.py` i podmień selektory formularza po wykonaniu ARIA snapshot - patrz workflow niżej.

### 2. Szukaj orzeczeń po słowie kluczowym (`/webwright-legal-pl:szukaj`)

Produkuje listę JSON z matchującymi orzeczeniami:
```bash
python szukaj_orzeczen.py --fraza "AI Act odpowiedzialnosc" --sad "Sąd Apelacyjny" --limit 10
# -> outputs/szukaj/<slug>/wyniki.json
```

### 3. Pobierz akt prawny z EUR-Lex (`/webwright-legal-pl:eurlex`)

Referencyjny skrypt: [`scripts/fetch_eurlex.py`](scripts/fetch_eurlex.py) (Playwright Chromium, ~200 wierszy). Komplementarny do `eu-sparql-search`: SPARQL znajduje akty semantycznie, ten skrypt pobiera pełną treść konkretnego CELEX (do citation grounding i audit bundle).

```bash
python scripts/fetch_eurlex.py --celex 32024R1689 --out outputs/eurlex
# -> outputs/eurlex/32024R1689/akt.md + meta.json + screenshot.png

python scripts/fetch_eurlex.py --celex 32016R0679 --lang EN   # RODO po angielsku
```

EUR-Lex jest za CloudFront WAF (HTTP 202 + challenge), więc `curl` zwraca pustkę - skrypt używa headless Chromium, który challenge automatycznie przechodzi.

Walidacja na żywym EUR-Lex (2026-05-27):

| CELEX | Akt | Sparsowano |
|---|---|---|
| `32024R1689` | AI Act (rozporządzenie 2024/1689) | data 2024-07-12, ELI, PDF PL, pełny opisowy tytuł |
| `32016R0679` | RODO (rozporządzenie 2016/679) | data 2016-05-04, ELI, PDF PL, pełny opisowy tytuł |

Parser radzi sobie z dwoma formatami daty (`12/07/2024` w headerze + `12.7.2024` w treści Dz.U.) i filtruje link PDF wg parametru `--lang` (EUR-Lex renderuje 20+ linków PDF, po jednym na język UE).

## Format wyjściowy (kontrakt z PATRON)

Każdy pobrany dokument trafia do `outputs/<typ>/<slug>/`:

```
meta.json          -> {sygnatura, sad, data, typ, url, pobrano_at, zrodlo}
orzeczenie.md      -> # <sygnatura>\n\n**Sąd:** ...\n\n<treść>
screenshot_*.png   -> dowód wizualny dla self-verify
```

`meta.json` jest zgodny ze schematem oczekiwanym przez `citation-grounding-pl`
oraz `legal-ai-audit-bundle`: pola `url` i `pobrano_at` umożliwiają późniejszy
audit trail.

## Workflow (Webwright standard)

1. **Plan** - zapisz critical points do `plan.md`
2. **Explore** - scratch Playwright script, ARIA snapshot serwisu
3. **Author** `final_script.py` w `final_runs/run_<id>/`
4. **Execute** - uruchom, zapisz screenshots
5. **Self-verify** - sprawdź CP przez Read na PNG + log

Viewport zawsze `{"width": 1280, "height": 1800}`. Nigdy `full_page=True`.
Przeglądarka: Firefox (`playwright.firefox.launch(headless=True)`).

## Uwagi RODO

- Dane klientów NIGDY nie trafiają do URL ani formularzy zewnętrznych serwisów
- Pobieramy tylko publiczne orzeczenia (anonimizowane przez sądy)
- Screenshots lądują lokalnie w `outputs/` - nie wysyłaj ich dalej bez sanityzacji
- Pliki `outputs/` NIE idą do git

## Slash Commands

- `/webwright-legal-pl:orzeczenie <sygnatura> [sąd]`
- `/webwright-legal-pl:szukaj <fraza> [sąd] [limit]`
- `/webwright-legal-pl:eurlex <celex-id>`
