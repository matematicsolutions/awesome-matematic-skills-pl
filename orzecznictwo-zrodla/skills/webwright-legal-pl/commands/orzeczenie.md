---
description: Pobierz orzeczenie z orzeczenia.ms.gov.pl lub sn.pl po sygnaturze. Produkuje reużywalny CLI script + orzeczenie.md + meta.json.
argument-hint: <sygnatura> [sąd] - np. "I ACa 123/25 Sąd Apelacyjny w Warszawie"
---

You are the Webwright agent in **CLI tool mode**. Your task: produce a
parameterized Python script `fetch_orzeczenie.py` that fetches a Polish
court judgment and saves it as Markdown + JSON.

Task arguments: $ARGUMENTS

Read `../SKILL.md` for the full output contract and RODO notes before starting.

## Routing

- Sygnatura zawiera "SN", "CSK", "II CSK", "III CZP", "IV CSK" → użyj `www.sn.pl`
- Sygnatura zawiera "TK", "K ", "P ", "SK " → użyj `trybunal.gov.pl`
- Pozostałe → użyj `orzeczenia.ms.gov.pl`

## Script contract

```bash
python fetch_orzeczenie.py \
  --sygnatura "I ACa 123/25" \
  --sad "Sąd Apelacyjny w Warszawie" \
  --output-dir outputs/orzeczenia/
```

Writes `outputs/orzeczenia/<slug>/`:
- `orzeczenie.md`
- `meta.json` - `{sygnatura, sad, data, typ, url, pobrano_at, zrodlo}`
- `screenshot_wynik.png`

Log kończy się `FINAL_RESPONSE: <url>`.

## Playwright notes

- Firefox, headless, viewport 1280×1800
- orzeczenia.ms.gov.pl: pole "Sygnatura" → wpisz → "Szukaj" → kliknij wynik
- sn.pl: wyszukiwarka orzeczeń → sygnatura → Enter → kliknij wynik
- Treść: `div#tresc`, `div.orzeczenie-tresc`, lub główny `<article>` - sprawdź ARIA snapshot
- Retry 3s jeśli 503
