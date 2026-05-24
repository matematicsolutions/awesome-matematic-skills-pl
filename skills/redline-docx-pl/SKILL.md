---
name: redline-docx-pl
description: Redlining polskich umow i pism w .docx z natywnymi Word Track Changes - bez niszczenia formatowania OOXML. Czyta .docx do Markdown (CriticMarkup) dla LLM, aplikuje zmiany jako sledzone (w:ins/w:del) + komentarze, i robi sanitize przed wyslaniem (strip metadanych autora, last-modified-by, rsid, timestampy - RODO przy wysylce pisma). Silnik = adeu (MIT). Use when the user wants to nanosic poprawki w umowie/pismie .docx, zrobic redline/tryb sledzenia zmian, czytac docx dla LLM bez utraty formatowania, przygotowac pismo do wyslania (usunac metadane autora z Worda), porownac dwie wersje .docx, lub mentions track changes / sledzenie zmian / redline / .docx / DOCX.
---

# Redline DOCX po polsku

Wrapper nad **adeu** (MIT, Dealfluence Oy) - dwukierunkowy translator `.docx <-> LLM`.
Robi to, czego `python-docx` NIE potrafi: wstrzykuje **natywne Word Track Changes**
(`w:ins`/`w:del`) i komentarze, zachowujac formatowanie, fonty i marginesy.

Cala praca lokalnie (uvx, brak chmury). Silnik testowany na polskim .docx 2026-05-22
(extract/apply/sanitize - patrz [THIRD_PARTY_INSPIRATIONS.md](THIRD_PARTY_INSPIRATIONS.md)).

## Wymagania

`uv` (jezeli brak: `pip install uv`). adeu pobiera sie samo przez `uvx adeu` przy pierwszym uzyciu (wersja sprawdzona: 1.7.5).

## Workflow (4 kroki)

### 1. Czytaj - .docx do Markdown dla LLM

```bash
uvx adeu extract umowa.docx -o umowa.md
```

Zwraca czysty Markdown (+ opcjonalny Semantic Appendix: defined terms, cross-references,
typos). LLM pracuje na semantyce, nie na surowym OOXML. Tani kontekstowo.

### 2. Przygotuj liste zmian - edits.json

Format to lista obiektow `modify` (search-and-replace na tekscie, NIE na pozycji):

```json
[
  {
    "type": "modify",
    "target_text": "sad wlasciwy dla siedziby Zleceniodawcy",
    "new_text": "Sad Arbitrazowy przy KIG w Warszawie",
    "comment": "Proponuje arbitraz zamiast sadu powszechnego."
  }
]
```

`target_text` musi byc jednoznaczny - adeu blokuje niejednoznaczne dopasowania
ZANIM dotkna pliku (bramka walidacji). Jezeli fragment wystepuje kilka razy,
doprecyzuj kontekst.

### 3. Aplikuj - natywne Track Changes

```bash
uvx adeu apply umowa.docx edits.json -o umowa_redline.docx --author "Kancelaria"
```

Daje `umowa_redline.docx` ze sledzonymi zmianami i komentarzami. Bez `--author`
adeu wpisuje nazwe konta systemowego biezacego uzytkownika - **zawsze podawaj
`--author` jawnie**, zeby nie wyciekla nazwa konta do dokumentu.

### 4. Sanitize PRZED wyslaniem - RODO

```bash
uvx adeu sanitize umowa_redline.docx -o umowa_clean.docx --keep-markup --author "Kancelaria" --report
```

Usuwa: `creator`, `last modified by`, template, `rsid`, custom XML parts;
normalizuje timestampy; podmienia autorow track-changes/komentarzy na jedna nazwe.
`--keep-markup` zachowuje sledzone zmiany (do negocjacji); bez tego (`--accept-all`)
akceptuje wszystko i zwraca czysty dokument. Konczy werdyktem `Result: CLEAN`.

> **Zawsze rob sanitize przed wyslaniem pisma na zewnatrz.** Word zostawia w metadanych
> nazwiska autorow, sciezki szablonow i historie edycji - to wyciek danych.

## Pozostale komendy

```bash
uvx adeu diff v1.docx v2.docx          # wizualny diff dwoch wersji
uvx adeu apply --live edits.json       # edycja zywego dokumentu w Word (Windows + MS Word)
```

## Integracja z anonimizacja PII

`sanitize` czysci **metadane** Worda, ale NIE tresc. Do anonimizacji tresci (PESEL,
NIP, nazwiska w fleksji) najpierw przepusc tekst przez silnik anonimizacji PII
(np. [matematic-anonimizacja-pl](https://github.com/matematicsolutions/matematic-anonimizacja-pl)),
potem redline:

1. anonimizator PII -> pseudonimizuj tresc pisma (PII -> tokeny)
2. praca/redline na zpseudonimizowanej wersji
3. `adeu sanitize` -> domkniecie metadanych przed wyslaniem

anonimizator PII = tresc (RODO art. 4 dane osobowe w tekscie); adeu sanitize = metadane pliku.
Dwie rozne warstwy wycieku, obie trzeba domknac.

## Ograniczenia

- Live MS Word tylko Windows + zainstalowany Word (backend Python).
- `target_text` na dopasowaniu tekstu - przy duplikatach trzeba kontekstu.
- adeu to narzedzie wspomagajace, NIE zastepuje weryfikacji przez prawnika.
- Silnik zewnetrzny (adeu, Dealfluence) - przy aktualizacji wersji zrob ponowny smoke test.

## Atrybucja

Silnik: [adeu](https://github.com/dealfluence/adeu) (c) 2026 Dealfluence Oy, licencja MIT.
Szczegoly i snapshot licencji: [THIRD_PARTY_INSPIRATIONS.md](THIRD_PARTY_INSPIRATIONS.md).
