---
name: opendataloader-pdf
description: Wysokiej jakości konwerter PDF→JSON/Markdown dla AI — zachowuje reading order, strukturę tabel, headings. Użyj gdy użytkownik mówi "wysoka jakość PDF", "papers naukowe PDF", "tabele z PDF", "opendataloader", "PDF z skomplikowaną strukturą", albo gdy MarkItDown daje słaby output. Główny konwerter PDF→MD w pipeline Konwerter/ w Obsidian Vault.
---

# OpenDataLoader PDF — PDF→JSON/MD (PL)

Java-based (Python wrapper) parser PDF najwyższej jakości dla AI. Benchmarki: NID (reading order), TEDS (tabele), MHS (headings). Używany w pipeline `Konwerter/` w vault.

## Instalacja (zrobione 2026-04-21)

```bash
python -m pip install --user opendataloader-pdf
```

Python 3.14, `opendataloader-pdf 2.2.1`. Wymaga **Java 17+** (mamy Eclipse Adoptium JDK 17). CLI: `python -m opendataloader_pdf` albo `opendataloader-pdf.exe` ze Scripts/.

## Wspierane outputy

- **JSON** (pełna struktura — reading order, bounding boxes, tabele jako 2D arrays) — default
- **Markdown** (flattened output, gotowy pod LLM)
- **HTML** (opcjonalnie)

## Użycie

### CLI — pojedynczy PDF
```bash
python -m opendataloader_pdf --input plik.pdf --output output/ --format md
```

### Batch (Obsidian Vault, pipeline Konwerter)
```bash
python -m opendataloader_pdf \
  --input "C:/Users/hp/Documents/Obsidian Vault/wszystko co wpada szybko/" \
  --output "C:/Users/hp/Documents/Obsidian Vault/Konwerter/" \
  --format md \
  --recursive
```

### Zaawansowane flagi
- `--enrich-formula` — wyciąga formuły LaTeX
- `--enrich-picture-description` — opis obrazów (wymaga `--hybrid-mode full`)
- `--filter-hidden-text` — wykrywa ukryty tekst (off by default, per-page rendering)

### Python API
```python
import opendataloader_pdf
result = opendataloader_pdf.load("plik.pdf", output_format="markdown")
print(result.markdown)
```

## Kiedy użyć vs MarkItDown

| PDF | Narzędzie |
|---|---|
| Prosty, tekst liniowy (blog, artykuł prasowy) | MarkItDown (szybsze) |
| Papers naukowe, raporty z tabelami | **OpenDataLoader** (jakość) |
| Dokumenty z 2-kolumnowym layoutem | **OpenDataLoader** (reading order) |
| Multi-page tabele | **OpenDataLoader** (TEDS) |
| Batch Konwerter/ (domyślnie) | **OpenDataLoader** |

## Integracja z vault

Pipeline Konwerter (istnieje Python script w `_vault-management/scripts/`):
1. PDF wrzucone do `wszystko co wpada szybko/` lub dropowane bezpośrednio
2. `opendataloader-pdf --input <path> --format md --output Konwerter/`
3. Frontmatter: `type: source-pdf, tags: [pdf, zrodlo]` — zgodnie z `vault-rules.json` → `clippings.classification_rules.pdf_source`
4. Powiązane oryginały PDF w folderze `Konwerter/` lub Attachments

## Gotcha

- **Java 17 wymagana** — Adoptium JDK zainstalowana (`/c/Program Files/Eclipse Adoptium/jdk-17.0.10.7-hotspot/`)
- **Wolniejsze** niż MarkItDown — nie używaj dla prostych PDFów
- **ForkJoinPool parallelism** — per-page przetwarzanie równoległe, `--filter-hidden-text` wyłącza parallel
- Przy zmianach CLI opcji w Java: `npm run sync` (dla kontrybutorów — nas nie dotyczy)

## Zasady

- Zawsze output do `Konwerter/`, nie nadpisuj oryginalnych PDF
- Batch > 10 PDF → zapytaj Wiesława przed startem
- Idempotencja: jeśli `.md` już istnieje w output i checksumma PDF nie zmieniona → skip
