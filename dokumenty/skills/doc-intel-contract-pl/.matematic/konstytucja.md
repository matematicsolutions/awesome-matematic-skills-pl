# doc-intel-contract-pl - Konstytucja

## Mission (1 zdanie)
Znormalizowac wyjscie naszego darmowego RODO-safe stacku OCR/PDF do jednego,
audytowalnego kontraktu `{block_type, bbox, text, confidence}`, ktory zasila
confidence-gating (human-in-the-loop), redakcje RODO i grounding cytatow - bez
zaleznosci od zamknietego modelu vendora.

## Core Principles (Articles)

### Article I - Zero-cloud / RODO-safe (MUST)
Cala normalizacja dziala lokalnie. Zaden dokument ani jego fragment NIE opuszcza
maszyny. Zaleznosci: tylko lokalne silniki (Chandra OCR, opendataloader-pdf,
pdftotext) + Python stdlib. Wywolania sieciowe = zakazane w warstwie kontraktu.

### Article II - Idea, nie waga (MUST)
Odtwarzamy ARCHITEKTURE / kontrakt wyjscia zainspirowany Mistral OCR 4, NIE
forkujemy ani nie owijamy zamknietego modelu. Zaden bajt wag/kodu vendora.
Kardynalna doktryna: skladamy puzzel z wlasnych klockow. [[reference_ocr_output_contract_from_mistral4]]

### Article III - Granica governance (MUST NOT)
Warstwa PRZYGOTOWUJE decyzje (lista "do przegladu przez czlowieka", propozycja
redakcji), NIGDY nie wykonuje aktu nieodwracalnego. Redakcja/akceptacja/zlozenie =
czlowiek. Confidence-gating produkuje kolejke, nie autorytatywny werdykt prawny.

### Article IV - Determinizm i audytowalnosc (MUST)
Ten sam input = ten sam kontrakt (poza polami czasowymi). Kazdy kontrakt ma
`doc_id` (SHA256 wejscia) + `contract_version` + `created_at`. Zero LLM w sciezce
normalizacji (LLM tylko opcjonalnie w rung-5 vision dla podpisu/pieczatki, jawnie
oznaczony w metadanych). Zgodne z AI Act art. 12 (record-keeping).

### Article V - Degradacja lagodna (SHOULD)
Gdy silnik nie dostarcza bbox lub word-confidence, kontrakt wypelnia pole `null` +
flaga `partial`, nie wywala sie. Kontrakt jest nadzbiorem - kazdy silnik mapuje
tyle, ile ma.

## Boundaries

**Robi:**
- Mapuje wyjscie Chandra / opendataloader / pdftotext -> kontrakt JSON.
- Klasyfikuje bloki (typed blocks) na tyle, na ile silnik pozwala.
- Liczy confidence-gating (prog -> kolejka human-review + auto-approve).
- Flaguje bloki wrazliwe (signature/stamp/PII-suspected).
- Dostarcza most do [[citation-grounding-pl]] (cytat -> blok+bbox).

**Nie robi (anty-zakres):**
- NIE jest silnikiem OCR (nie zastepuje Chandry).
- NIE wykonuje redakcji ani akceptacji (przygotowuje, czlowiek decyduje).
- NIE wola cloud OCR (Mistral/Azure/Google) - to zlamie Article I.
- NIE ocenia merytorycznie tresci prawnej (to inne skille).

**Wspolpracuje z:**
- Drabinka PDF w CLAUDE.md (Chandra OCR rung 4, opendataloader rung 3, vision rung 5).
- [[citation-grounding-pl]] (konsument kontraktu).
- Granica governance PATRONa / approval cards (confidence-gating -> kolejka).

## Governance
- Owner: Wieslaw Mazur
- Reviewers: anthropic-skills:matematic-reviewer (kod), marko-pl (SKILL.md/tresc)
- Amendment: zmiana Article = MINOR+ bump + wpis w Amendments.

## Compliance Map
- **RODO** art. 5 (minimalizacja - audit trzyma doc_id/hash, nie raw), art. 25 (privacy by design - Article I).
- **AI Act** art. 12 (record-keeping - Article IV), art. 14 (human oversight - Article III confidence-gating).
- **Licencja projektu:** MIT (wlasny kod, zero wag vendora - Article II).

## Amendments
- 0.1.0 - pierwsza ratyfikacja.

**Version:** 0.1.0 | **Ratified:** 2026-07-01 | **Last Amended:** 2026-07-01
