# doc-intel-contract-pl

Warstwa, która ujednolica wyjście naszego darmowego, lokalnego stacku OCR/PDF do
jednego kontraktu `{block_type, bbox, text, confidence}`. Pomysł podpatrzony w
architekturze Mistral OCR 4 (model zamknięty, więc bierzemy ideę, nie wagi) i
złożony na własnych klockach.

## Po co to jest

Nasza drabinka PDF daje pięć różnych kształtów wyjścia. Ten skill sprowadza je do
jednego i od razu odpowiada na trzy pytania audytu LegalTech:

1. **Który fragment ma sprawdzić człowiek?** confidence-gating (AI Act art. 14).
2. **Co zredagować?** kandydaci PII (PESEL/NIP/REGON z sumą kontrolną, IBAN, e-mail,
   dowód) plus podpis i pieczątka.
3. **Gdzie w dokumencie jest ten cytat?** bbox + block_id, czyli most do
   `citation-grounding-pl` (cytat wskazuje region, nie sam string).

## Silniki wejściowe

| Engine | Źródło | Bogactwo |
|---|---|---|
| `opendataloader` | opendataloader-pdf (JSON) | bbox + typy bloków + confidence |
| `chandra` | Chandra OCR 2 (`parse_chunks`) | bbox + 19 etykiet layoutu, bez confidence |
| `vlm-html` | dowolny VLM z promptem `references/prompt_vlm_ocr_pl.md` | bbox + nasze etykiety (w tym podpis i pieczątka), bez confidence |
| `gaius` | OCR PATRONa, Gaius-Lex `/api/v1/ocr/poll` | tekst + wariant silnika (default / google_doc_ai) |
| `pdftotext` | pdftotext (plain) | tekst (partial, bez bbox) |

Silnik, który nie dostarcza bbox lub confidence, degraduje się łagodnie: pole
`null` plus flaga `partial`, a blok trafia do kolejki człowieka. Silniki
generatywne (`chandra`, `vlm-html`) nie podają pewności wcale, więc cały
dokument idzie do przeglądu.

Silnik `vlm-html` odwraca zależność: to nie my dopasowujemy się do kolejnego
formatu OCR, tylko prompt narzuca modelowi nasz kontrakt. Ten sam szablon
obsłuży Claude vision, lokalny Qwen-VL i OCR PATRONa. Wzorzec podpatrzony
w Chandrze (Apache-2.0), etykiety własne - Chandra nie zna kategorii podpisu
ani pieczątki, a bez nich nie ma redakcji RODO.

## Użycie

```bash
cd ~/.claude/skills/doc-intel-contract-pl

# normalizacja do kontraktu
python scripts/normalize.py --engine opendataloader wyjscie.json --pretty
python scripts/normalize.py --engine gaius poll_result.json          # OCR PATRONa
python scripts/normalize.py --engine chandra chandra.json --threshold 0.9
python scripts/normalize.py --engine vlm-html strona.html            # dowolny VLM

# most do groundingu (cytat -> region)
python scripts/normalize.py --engine opendataloader wyjscie.json > kontrakt.json
python scripts/grounding_bridge.py kontrakt.json --quotes cytaty.txt --pretty
```

Exit `0` = kontrakt zgodny ze schematem, `2` = błąd wejścia lub kontrakt niepoprawny.
Pasuje pod CI i pre-commit.

## Granica governance

Skill przygotowuje kolejkę do przeglądu, listę kandydatów do redakcji i współrzędne
cytatu. Redakcji ani akceptacji nie wykonuje. To zostaje człowiekowi (Article III
konstytucji projektu).

## Testy

```bash
python -m unittest discover -s tests -v
```

57 testów, zero zależności (Python 3.11+ stdlib). Zero sieci, zero LLM w ścieżce
normalizacji.

## Governance i spec

- `.matematic/konstytucja.md` - zasady projektu (SEMVER).
- `.matematic/spec/001-output-contract-mvp/` - spec, plan, zadania.

Licencja: MIT (własny kod, zero wag vendora).
