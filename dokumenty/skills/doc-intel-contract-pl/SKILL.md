---
name: doc-intel-contract-pl
description: >
  Normalizuje wyjscie darmowego RODO-safe stacku OCR/PDF (opendataloader-pdf,
  pdftotext, Chandra OCR, OCR PATRONa/Gaius-Lex) do jednego audytowalnego kontraktu
  {block_type, bbox, text, confidence} inspirowanego architektura Mistral OCR 4
  (idea, nie wagi - model zamkniety=SKIP). Daje trzy rzeczy naraz: confidence-gating
  (region niskiej pewnosci -> kolejka human-in-the-loop, reszta auto-approve),
  typed blocks + flagi PII pod redakcje RODO (signature/stamp/PESEL/NIP/IBAN),
  oraz bbox+block domykajace grounding cytatow (cytat -> region dokumentu).
  Zero-cloud, zero LLM w sciezce normalizacji, deterministyczne (doc_id SHA256),
  Python stdlib. Uzywaj gdy: "znormalizuj OCR", "kontrakt dokumentu", "ktore
  bloki do przegladu", "confidence gating", "przygotuj redakcje PII", "bbox do
  cytatu", "wyjscie opendataloader do JSON", "human-in-the-loop dla skanu".
  Komplementarny do citation-grounding-pl (konsument kontraktu) i drabinki PDF.
attribution:
  - source: Mistral OCR 4 (Mistral AI)
    url: https://mistral.ai/news/mistral-ocr
    license: proprietary
    relationship: pattern-only
    note: >
      Idea kontraktu wyjscia Document Intelligence: typed blocks + bbox + confidence
      jako jedno audytowalne wyjscie. Model jest zamkniety, wiec bierzemy sam ksztalt
      kontraktu; schemat, gating, flagi PII i caly kod napisane od zera.
  - source: datalab-to/chandra
    url: https://github.com/datalab-to/chandra
    license: Apache-2.0
    relationship: adaptation
    note: >
      Z KODU (Apache-2.0), nie z wag (wagi sa na Modified OpenRAIL-M i nie sa tu
      uzywane). Wzorzec prompt-kontraktu constrained-HTML z data-label/data-bbox
      w skali 0-1000 (silnik vlm-html), algorytm detekcji zapetlenia generacji
      detect_repeat_token (degeneracja.py) oraz przepis renderu strony
      flatten AcroForm + dynamiczne DPI. Taksonomia etykiet, obsluga podpisu
      i pieczatki, adapter i testy napisane od zera.
metadata:
  author: Wieslaw Mazur / MateMatic
  version: 0.2.0
  scope: warstwa normalizujaca stack OCR/PDF -> kontrakt wyjscia (zero-cloud)
  cost: zero LLM (deterministyczna normalizacja)
  license: MIT
  companion_skills: citation-grounding-pl, opendataloader-pdf, markitdown
---

# doc-intel-contract-pl - kontrakt wyjscia Document Intelligence

## Po co
Nasza drabinka PDF (pdftotext -> markitdown -> opendataloader -> Chandra ->
vision) daje 5 roznych ksztaltow wyjscia. Ten skill ujednolica je do JEDNEGO
kontraktu, ktory od razu odpowiada na trzy pytania:

1. **Ktory fragment ma zobaczyc czlowiek?** - confidence-gating (Article III / AI Act art. 14).
2. **Co zredagowac?** - typed blocks + flagi PII (signature/stamp/PESEL/NIP/IBAN).
3. **Gdzie w dokumencie jest ten cytat?** - bbox + block_id -> most do [[citation-grounding-pl]].

Zamkniety jest MODEL Mistral OCR 4, nie idea. Odtwarzamy kontrakt na wlasnym,
lokalnym, RODO-safe stacku. [[feedback_doktryna_skladanie_puzzli_nie_wynajdywanie_kola]]

## Kontrakt (v1.1.0)
```json
{
  "doc_id": "<sha256 wejscia>",
  "contract_version": "1.1.0",
  "source": {"path": "...", "engine": "opendataloader|pdftotext|chandra|gaius|vlm-html", "engine_variant": "default|google_doc_ai|null", "pages": N},
  "blocks": [
    {"id": "b0001", "page": 1, "bbox": [x0,y0,x1,y1]|null,
     "block_type": "title|paragraph|table|list|equation|signature|stamp|figure|header|footer|unknown",
     "text": "...", "confidence": 0.0-1.0|null, "flags": ["partial","pii_suspected","pii:pesel","sensitive_block","signature_suspected",...]}
  ],
  "gating": {"threshold": 0.85, "review_required": ["b0003"], "auto_approved": ["b0001"]},
  "redaction_candidates": ["b0004"],
  "meta": {"created_at": "ISO-8601"}
}
```
- `bbox` znormalizowany 0-1 (przenosny miedzy DPI). Silnik bez bbox -> `null` + flaga `partial`.
- `confidence == null` (partial) -> **zawsze** do `review_required` (konserwatywnie; nie wiemy = czlowiek patrzy).

## Uzycie (CLI)
```bash
cd ~/.claude/skills/doc-intel-contract-pl
python scripts/normalize.py --engine opendataloader wyjscie.json --pretty
python scripts/normalize.py --engine pdftotext dokument.txt --threshold 0.9
cat wyjscie.json | python scripts/normalize.py --engine opendataloader -
```
Exit: `0` = kontrakt schema-valid, `2` = blad wejscia / kontrakt niepoprawny (pasuje pod CI / pre-commit).

## Miejsce w drabince PDF
Ten skill jest warstwa PO silniku OCR, PRZED groundingiem/redakcja:
`(pdftotext|opendataloader|Chandra) -> doc-intel-contract-pl -> {gating do czlowieka | redaction_candidates | citation-grounding-pl}`

## Granica governance (Article III)
Skill PRZYGOTOWUJE: kolejke `review_required`, liste `redaction_candidates`,
wspolrzedne cytatu. NIE wykonuje redakcji ani akceptacji - to robi czlowiek.
Confidence-gating to kolejka, nie werdykt prawny.

## Status / roadmap (spec 001)
- **US1 (MVP, DONE 2026-07-01):** adaptery opendataloader+pdftotext, kontrakt, confidence-gating, walidacja schematu.
- **US2 (DONE):** flagi PESEL/NIP/REGON (checksum)/IBAN/email/dowod + redaction_candidates; signature/stamp=sensitive_block.
- **US3 T030 (DONE):** most `grounding_bridge.py` -> zadanie citation-grounding-pl; lokalizuje cytat w blokach i doklada `anchor_resolved {page,bbox,block_id}` (cytat -> region).
- **US3 T031 (DONE):** adapter Chandra (layout DOM, bbox 0-1, block conf = MIN linii).
- **US3 T032 (DONE):** `signature.py` - heurystyka podpisu/pieczatki (dol strony + krotki + low-conf); detektor vision wstrzykiwalny (opt-in). Potwierdzenie wizualne = krok operatora w runtime.
- **EXTRA T033 (DONE):** adapter `gaius` - OCR PATRONa (Gaius-Lex `/ocr/poll`), engine_variant default/google_doc_ai.
- **T034 (DONE 2026-08-05):** adapter `chandra` dopasowany do REALNEGO formatu Chandry 2 (plaska lista `{bbox,label,content-HTML}`, 19 etykiet, BEZ confidence -> wszystko do review) + guard cichej niekompletnosci (niepuste wejscie, 0 blokow = ValueError, nie exit 0).
- **T035 (DONE 2026-08-05, kontrakt 1.1.0):** silnik `vlm-html`. Szablon promptu
  `references/prompt_vlm_ocr_pl.md` zmusza dowolny VLM do emisji constrained HTML
  z atrybutami data-label i data-bbox - wzorzec Chandry - a adapter parsuje to
  do kontraktu. VLM etykietuje `signature` i `stamp` wprost, wiec podpis i
  pieczatka same laduja w redaction_candidates. Do tego `degeneracja.py`:
  detektor zapetlenia generacji, w normalize daje flage `degenerate_tail`
  i ostrzezenie na stderr.
- **83 testy zielone** (contract+pii+grounding+chandra+chandra2+gaius+signature+vlm-html+degeneracja). Zero-dep Python stdlib.

**Granica dowodu (stan 2026-08-05).** Testy dowodza, ze parser czyta format
zgodnie ze specyfikacja - nie dowodza, ze zywy model ta specyfikacje stosuje.
Fixture `vlm_html.sample.html` napisalismy sami, wiec sprawdza adapter, nie
posluszenstwo VLM. Fixture `chandra2.sample.json` odwzorowuje format odczytany
z upstreamu `chandra/output.py`, ale bez przebiegu na realnej Chandrze.
Zanim silnik `vlm-html` pojdzie na akta, potrzebny jest przebieg bojowy:
prawdziwy skan, prawdziwy model, porownanie ze zrodlem.
[[feedback_zgodnosc_formatu_mierz_cudzym_czytnikiem]]

Render skanu do obrazow przed silnikiem VLM (flatten AcroForm + dynamiczne DPI,
pypdfium2 opcjonalnie): przepis w `references/render_skanu_pl.md`. UWAGA:
walidacja podpisu kwalifikowanego ([[waliduj-podpis-pdf-pl]]) PRZED flatten.

Most do groundingu:
```bash
python scripts/normalize.py --engine opendataloader wyjscie.json > kontrakt.json
python scripts/grounding_bridge.py kontrakt.json --quotes cytaty.txt --pretty
# -> {items:[{quote, source_text, anchor_resolved:{page,bbox,block_id}}]} do ground-citations.mjs
```

Governance: `.matematic/konstytucja.md` + `.matematic/spec/001-output-contract-mvp/`.

## Czego NIE robi
- NIE jest silnikiem OCR (nie zastepuje Chandry).
- NIE wykonuje redakcji/akceptacji (przygotowuje, czlowiek decyduje).
- NIE wola cloud OCR (Mistral/Azure/Google) - zlamaloby Article I.
- NIE ocenia merytorycznie tresci prawnej.

## Testy
```bash
python -m unittest discover -s tests -v
```
Zero zaleznosci npm/pip (czysty Python 3.11+ stdlib).
