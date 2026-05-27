---
description: Pobierz akt prawny UE z EUR-Lex w wersji polskiej po numerze CELEX. Produkuje akt.md + meta.json.
argument-hint: <celex-id> - np. "32024R1689" (AI Act) albo "32016R0679" (RODO)
---

You are the Webwright agent in **CLI tool mode**. Your task: produce a
parameterized Python script `fetch_eurlex.py` that fetches a EU legal act
from EUR-Lex in Polish and saves it as Markdown + JSON.

Task arguments: $ARGUMENTS

Read `../SKILL.md` for the full output contract and RODO notes before starting.

## CELEX format reminder

| Akt | CELEX |
|-----|-------|
| AI Act (2024/1689) | 32024R1689 |
| RODO (2016/679) | 32016R0679 |
| DSA (2022/2065) | 32022R2065 |
| DMA (2022/1925) | 32022R1925 |
| NIS2 (2022/2555) | 32022L2555 |

## Script contract

```bash
python fetch_eurlex.py \
  --celex "32024R1689" \
  --jezyk "PL" \
  --output-dir outputs/eurlex/
```

Writes `outputs/eurlex/<celex>/`:
- `akt.md` - pełna treść rozporządzenia/dyrektywy w języku PL
- `meta.json` - `{celex, tytul, jezyk, data_wejscia, url, pobrano_at, zrodlo}`
- `screenshot_wynik.png`

Log kończy się `FINAL_RESPONSE: <url>`.

## Playwright notes

- Firefox, headless, viewport 1280×1800
- URL bezpośredni: `https://eur-lex.europa.eu/legal-content/PL/TXT/?uri=CELEX:<celex>`
- Alternatywnie: strona główna EUR-Lex → wyszukiwarka → wpisz CELEX → wybierz PL
- Treść: `div#document1`, `div.eli-main-title` + `div.consLegBody` lub główny `<article>`
- Sprawdź ARIA snapshot przed wyodrębnianiem treści
- Retry 3s jeśli 503 lub przekierowanie na stronę CAPTCHA
