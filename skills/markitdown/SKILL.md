---
name: markitdown
description: Konwersja dowolnego dokumentu (PDF, Word, Excel, PowerPoint, HTML, EPUB, audio, obrazy, YouTube) na Markdown dla LLM. Użyj gdy użytkownik mówi "konwertuj PDF", "przerób Word na markdown", "zamień PPT na MD", "markdown z Excela", "wyciągnij tekst z PDF", albo daje plik Office/PDF do analizy. Microsoft MarkItDown (pip) + MCP server.
---

# MarkItDown - konwerter dokumentów do Markdown (PL)

Lightweight utility Microsoftu - zachowuje strukturę (nagłówki, listy, tabele, linki), nie wygląd. Pod LLM, nie pod human.

## Instalacja (zrobione 2026-04-21)

```bash
python -m pip install --user markitdown markitdown-mcp
```

Wymaga Python 3.10+ (testowane na 3.14). CLI: `python -m markitdown`.

## Wspierane formaty

- **PDF** (preferuj dla krótkich, standardowych PDF; dla złożonych/tabel - OpenDataLoader PDF)
- **Office**: Word (.docx), Excel (.xlsx), PowerPoint (.pptx)
- **HTML, EPUB, CSV, JSON, XML**
- **Obrazy** (EXIF + OCR jeśli zainstalowane `[all]`)
- **Audio** (EXIF + transkrypcja jeśli włączone)
- **ZIP** (iteruje zawartość)
- **YouTube URL** (napisy)

## Użycie

### CLI (single file)
```bash
python -m markitdown input.pdf > output.md
python -m markitdown input.pptx -o output.md
```

### Batch (Obsidian Vault)
```bash
for f in "/c/Users/hp/Documents/Obsidian Vault/Konwerter"/*.pdf; do
  python -m markitdown "$f" > "${f%.pdf}.md"
done
```

### Python API
```python
from markitdown import MarkItDown
md = MarkItDown()
result = md.convert("plik.docx")
print(result.text_content)
```

### MCP server
Opcjonalnie - jeśli chcesz udostępnić Claude Code jako MCP tool:
```bash
markitdown-mcp
```

## Kiedy użyć MarkItDown vs OpenDataLoader PDF

| Sytuacja | Narzędzie |
|---|---|
| Word/Excel/PPT | **MarkItDown** |
| Prosty PDF, tekst liniowy | **MarkItDown** (szybsze) |
| Złożony PDF z tabelami, reading order, papers naukowe | **OpenDataLoader PDF** (jakość) |
| Audio/transkrypcja | Whisper (mamy `whisper-asr-pipeline`) |
| Web page | Defuddle (mamy `defuddle` od Kepano) |

## Integracja z vault

Output docelowo → `Konwerter/` (folder w vault dla source-pdf → MD). Frontmatter: `type: source-pdf, tags: [pdf, zrodlo]`. Zobacz `vault-rules.json` → `clippings.classification_rules.pdf_source`.

## Gotcha

- `markitdown[all]` na Python 3.14/3.15 failuje (onnxruntime, youtube-transcript-api konflikt) - użyj zainstalowanego `markitdown` bez extras
- Dla OCR obrazów / pełnego YouTube - Docker albo starszy Python (3.11/3.12)
- Nie używaj dla high-fidelity conversion dla human reading - tylko pod LLM
