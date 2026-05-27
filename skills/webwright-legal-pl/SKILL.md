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

Produkuje **reużywalny CLI script** `fetch_orzeczenie.py`:
```bash
python fetch_orzeczenie.py --sygnatura "I ACa 123/25" --sad "Warszawa"
# -> outputs/orzeczenia/i-aca-123-25/orzeczenie.md + meta.json
```

### 2. Szukaj orzeczeń po słowie kluczowym (`/webwright-legal-pl:szukaj`)

Produkuje listę JSON z matchującymi orzeczeniami:
```bash
python szukaj_orzeczen.py --fraza "AI Act odpowiedzialnosc" --sad "Sąd Apelacyjny" --limit 10
# -> outputs/szukaj/<slug>/wyniki.json
```

### 3. Pobierz akt prawny z EUR-Lex (`/webwright-legal-pl:eurlex`)

```bash
python fetch_eurlex.py --celex "32024R1689"   # AI Act = 32024R1689
# -> outputs/eurlex/32024R1689/akt.md + meta.json
```

## Format wyjściowy (kontrakt z PATRON)

Każdy pobrany dokument trafia do `outputs/<typ>/<slug>/`:

```
meta.json          → {sygnatura, sad, data, typ, url, pobrano_at, zrodlo}
orzeczenie.md      → # <sygnatura>\n\n**Sąd:** ...\n\n<treść>
screenshot_*.png   → dowód wizualny dla self-verify
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
