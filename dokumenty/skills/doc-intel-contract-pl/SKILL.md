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
  - source: firecrawl/pdf-inspector
    url: https://github.com/firecrawl/pdf-inspector
    license: MIT
    relationship: dependency
    note: >
      Zaleznosc opcjonalna (PyPI `pdf-inspector`, MIT) uzywana WYLACZNIE przez
      `scripts/routing_gate.py` do mechanicznej klasyfikacji skan-vs-tekst
      (classify_pdf: pdf_type, pages_needing_ocr, confidence 0-1). Sciezka
      normalizacji pozostaje zero-dep stdlib. Zmierzone 2026-08-08 na aktach WM:
      pelny skan 14/14 stron wykryty w 8 ms (pewnosc 0.95), 102-stronicowy PDF
      tekstowy w 22 ms. Zamyka dziure szczebla 4 drabinki, gdzie decyzja
      "czy to skan" byla dotad ocena oka ludzkiego.
  - source: firecrawl/anydoc
    url: https://github.com/firecrawl/anydoc
    license: MIT
    relationship: pattern-only
    note: >
      NIE jest zaleznoscia - jest POWODEM istnienia bramki. Audyt zrodla
      2026-08-08 wykazal, ze zdarzenia pominiecia tresci (42 miejsca, m.in.
      "skipping slide", "skipping chapter", "duplicate note id dropped") ida do
      fasady `log`, a repo nigdzie nie rejestruje loggera. Dowod bojowy:
      .docx z jednym uszkodzonym chart1.xml -> exit 0, stderr 0 bajtow,
      a z wyjscia znika cala tabela danych. `check_ooxml` nazywa uszkodzona
      czesc ZANIM ktokolwiek zaufa wyjsciu. Kod bramki napisany od zera.
  - source: sandbox-quantum/flintai-cli
    url: https://github.com/sandbox-quantum/flintai-cli
    license: Apache-2.0 WITH Commons-Clause
    relationship: pattern-only
    note: >
      `mask_for_model.py` - maska dlugosciowa dla KOPII tekstu wysylanej do modelu
      (rung-5): kazdy znak sekretu -> `*`, dlugosc i pozycje reszty identyczne, wiec
      offsety i bbox dalej pasuja do oryginalu. Idea z ich `secret_anonymizer.py`
      (maskowanie kluczy w kodzie); tu regexy PII PL z pii_flags i wlasne. Zero kodu.
metadata:
  author: Wieslaw Mazur / MateMatic
  version: 0.3.0
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

## Bramka routingu (PRZED silnikiem) - `routing_gate.py`
Odpowiada na pytanie, ktore dotad rozstrzygalo oko: **czy ten dokument w ogole da
sie przeczytac tekstowo i ktorym szczeblem**. Werdykt trojstanowy z pelnym
mianownikiem, kod wyjscia `0/10/20` (ok/degraded/failed).
```bash
python scripts/routing_gate.py AKTA.pdf --pretty
python scripts/routing_gate.py *.pdf *.docx --quiet   # tylko to, co nie jest ok
```
Lapie trzy rzeczy, ktorych zaden konwerter nie zglasza:
- **PDF mieszany** (czesc stron to skany) - kazde wyjscie tekstowe bedzie NIEPELNE,
  a wyglada na kompletne. Status `degraded` + numery stron do OCR.
- **Pelny skan** - `failed`, eskalacja (Chandra wymaga GPU, ktorego tu nie ma).
- **Uszkodzona czesc OOXML** - konwerter pominie ja bez slowa (zmierzone na anydoc:
  uszkodzony `chart1.xml` = exit 0, stderr pusty, znika cala tabela). Bramka nazywa
  czesc PRZED konwersja.

PDF wymaga `pip install pdf-inspector` (MIT). Jego brak = `failed`, nigdy ciche `ok`.

## Miejsce w drabince PDF
Ten skill jest warstwa PO silniku OCR, PRZED groundingiem/redakcja:
`routing_gate -> (pdftotext|anydoc|opendataloader|Chandra) -> doc-intel-contract-pl -> {gating do czlowieka | redaction_candidates | citation-grounding-pl}`

## Granica governance (Article III)
Skill PRZYGOTOWUJE: kolejke `review_required`, liste `redaction_candidates`,
wspolrzedne cytatu. NIE wykonuje redakcji ani akceptacji - to robi czlowiek.
Confidence-gating to kolejka, nie werdykt prawny.

**Wyjatek pozorny - `mask_for_model.py`.** Gdy fragment ma wyjsc do modelu (rung-5
vision, LLM-sedzia), kopia dostaje maske dlugosciowa: PESEL/NIP/REGON z suma kontrolna,
IBAN, e-mail, dowod, klucze API, `Bearer` -> `*` znak w znak. Oryginal, kontrakt i bloki
sa nietkniete, wiec to NIE jest redakcja dokumentu (Article III), tylko bezpiecznik na
kanale wyjscia (Article I). Dlugosc identyczna = offsety i bbox z `grounding_bridge`
pasuja do oryginalu bez przeliczania.

```bash
python scripts/mask_for_model.py < fragment.txt > fragment.dla_modelu.txt
# stderr: {"zamaskowane": 3, "kategorie": ["email", "iban", "pesel"]}
```

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
