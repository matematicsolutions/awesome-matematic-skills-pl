---
description: Szukaj orzeczeń po frazie/słowie kluczowym w orzeczenia.ms.gov.pl lub sn.pl. Produkuje listę wyników JSON.
argument-hint: <fraza> [sąd] [limit] - np. "dobro dziecka Sąd Apelacyjny 10"
---

You are the Webwright agent in **CLI tool mode**. Your task: produce a
parameterized Python script `szukaj_orzeczen.py` that searches Polish court
portals by keyword phrase and returns a structured JSON results list.

Task arguments: $ARGUMENTS

Read `../SKILL.md` for the full output contract and RODO notes before starting.

## Routing

Domyślnie szukaj na `orzeczenia.ms.gov.pl` (sądy powszechne).
Jeśli w argumencie pojawi się "SN", "Sąd Najwyższy" lub "CSK" → szukaj też na `www.sn.pl`.

## Script contract

```bash
python szukaj_orzeczen.py \
  --fraza "dobro dziecka" \
  --sad "Sąd Apelacyjny" \
  --limit 10 \
  --output-dir outputs/szukaj/
```

Writes `outputs/szukaj/<slug>/wyniki.json`:
```json
{
  "fraza": "...",
  "sad": "...",
  "limit": 10,
  "pobrano_at": "ISO8601",
  "zrodlo": "orzeczenia.ms.gov.pl",
  "wyniki": [
    {"sygnatura": "...", "sad": "...", "data": "...", "url": "...", "fragment": "..."}
  ]
}
```

Log kończy się `FINAL_RESPONSE: <liczba wyników> orzeczeń`.

## Playwright notes

- Firefox, headless, viewport 1280×1800
- orzeczenia.ms.gov.pl: pole "Treść orzeczenia" lub "Słowa kluczowe" → wpisz frazę → "Szukaj"
  Zbierz z listy wyników: sygnatura, sąd, data, URL wyniku, fragment tekstu
- sn.pl: zakładka "Orzecznictwo" → wyszukiwarka pełnotekstowa → fraza
- Retry 3s jeśli 503
- Limit: pobierz maksymalnie `--limit` wyników (domyślnie 10), nie wchódź w treść każdego
