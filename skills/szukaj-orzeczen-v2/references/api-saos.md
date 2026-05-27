# SAOS API Reference

## Search API

```
GET https://www.saos.org.pl/api/search/judgments
```

| Parametr | Opis |
|----------|------|
| `all` | Fraza pełnotekstowa |
| `keywords` | Hasła tematyczne (powtarzalny, AND). Tylko sądy powszechne |
| `pageSize` | 10-100 |
| `pageNumber` | 0+ |
| `sortingField` | `JUDGMENT_DATE`, `DATABASE_ID` |
| `sortingDirection` | `ASC` / `DESC` |
| `judgmentDateFrom` | `yyyy-MM-dd` |
| `judgmentDateTo` | `yyyy-MM-dd` |

Tryb `keywords` - tylko sądy powszechne. Dla SN / TK / KIO użyj `all`.

## Browse API

```
GET https://www.saos.org.pl/api/judgments/{id}
```

Pełny tekst w `data.textContent`. Search API daje tylko snippet - zawsze pobieraj przez Browse API.

## Obsługa błędów

| Scenariusz | Zachowanie |
|------------|-----------|
| HTTP 429 | Exponential backoff: 5s, 10s, 15s |
| HTTP 5xx | Retry: 2s, 4s, 6s |
| Timeout | 30s, 3 próby |
| Brak textContent | Fallback „Brak treści" |
| `division=null` | Guard `or {}` (nie crashuje) |
| Pusta fraza | Walidacja, exit 1 |
| <30 orzeczeń dla raportu | Ostrzeżenie: raport mało informatywny |

## Ważne ograniczenia

- **Opóźnienie 0.5s** między requestami - nie zmniejszaj.
- **Anti-hallucination** - NIE generuj fikcyjnych sygnatur, dat, treści. Dane wyłącznie z API SAOS.
- **Domena** - w Claude.ai `saos.org.pl` musi być na liście allowed domains.
- **Duże zbiory** - >500 orzeczeń = 10+ MB DOCX. Rekomenduj `--max-results`.
- **Kodowanie** - UTF-8 wszędzie.

## Środowisko

### Claude.ai (czat webowy / mobilny / desktop)

| Narzędzie | Zastosowanie |
|-----------|-------------|
| `bash_tool` | Uruchamianie skryptów Python, instalacja zależności |
| `view` | Podgląd plików wyjściowych |
| `create_file` | Tworzenie pliku JSON ze strukturą raportu tematycznego |
| `present_files` | **KRYTYCZNE** - jedyny sposób dostarczenia plików |

Ścieżki: roboczy `/home/claude/` → wyjściowy `/mnt/user-data/outputs/`

### Claude Code (terminal)

Bezpośredni terminal, brak ograniczeń sieciowych. Pliki w katalogu roboczym.
