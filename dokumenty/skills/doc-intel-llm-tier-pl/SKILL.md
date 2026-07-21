---
name: doc-intel-llm-tier-pl
description: >-
  Warstwa LLM-tier ekstrakcji groundowanej dla polskich dokumentow prawnych - WRAP na
  contextgem (Apache-2.0). Wyciaga z umowy/pisma/wyroku INFEROWANE koncepty (kara umowna,
  termin, sad wlasciwy, strony, ryzyka), ktorych nie da sie zlapac regexem, i zakotwicza
  KAZDY do zdania/akapitu zrodlowego (grounding) plus uzasadnienie. Zwraca rekordy zgodne
  z kontraktem doc-intel-contract-pl {concept, block_type, text, confidence, refs,
  justification} - most do citation-grounding-pl. Governance wbudowany w tool: domyslnie
  backend LOKALNY (Ollama), model chmurowy wymaga jawnej flagi + ostrzega o RODO/EOG. Uzywaj
  gdy: "wyciagnij koncepty z umowy", "ekstrakcja z dokumentu prawnego", "co mowi ta umowa o
  X", "grounded extraction", "wyciagnij postanowienia + zrodla", ekstrakcja pol z pisma z
  zakotwiczeniem cytatu. Dopelnia (nie zastepuje) stdlib doc-intel-contract-pl. NIE porada prawna.
license: MIT
data-residency: local
requires-human-approval: true
metadata:
  version: 1.0.0
  author: MateMatic (Wieslaw Mazur)
  upstream: shcherbak-ai/contextgem (Apache-2.0)
  domain: document-intelligence-pl
  updated: 2026-07-21
  requires: contextgem>=0.25.1 (NIE stdlib - swiadomy wyjatek dla ekstrakcji LLM)
  positioning: local-first-configurable, RODO-safe (backend lokalny/EOG dla danych klienta)
---

# doc-intel-llm-tier-pl - grounded extraction (warstwa LLM)

WRAP MateMatic na `contextgem`. Wyciaga z polskiego dokumentu prawnego **inferowane koncepty**
zakotwiczone do zrodla + uzasadnienie, i mapuje na nasz kontrakt dokumentowy.

## Miejsce w ukladance (nie duplikuj)

| Warstwa | Skill | Technika | Co robi |
|---|---|---|---|
| Struktura + PII | `doc-intel-contract-pl` | **stdlib, zero-LLM** | block_type, bbox, confidence, redaction_candidates |
| **Koncepty prawne** | **ten skill** | **LLM + grounding** | inferowane pola (kara, termin, ryzyko) + refs zdaniowe + justification |
| Weryfikacja cytatu | `citation-grounding-pl` | string-match | czy cytat/ref istnieje w zrodle (anti-halucynacja) |

Przeplyw: stdlib doc-intel (struktura/PII) -> **ten skill (koncepty + grounding)** -> citation-grounding (weryfikacja refs). Nie ruszamy czystosci stdlib core - to osobna, opcjonalna warstwa.

## Granica governance (WBUDOWANA W TOOL)

- **Domyslny backend = LOKALNY (Ollama).** Dla danych KLIENTA (tajemnica adwokacka + RODO) - TYLKO taki.
- **Model chmurowy** (OpenRouter/OpenAI/DeepSeek...) wymaga jawnej flagi `--allow-cloud`; tool
  **odmawia** (exit 2) bez niej i **ostrzega**, ze cloud = wylacznie dane SYNTETYCZNE / nie-klienckie
  (transfer poza EOG). To nie dokumentacja - to zachowanie kodu.
- Tool przygotowuje ekstrakcje; decyzja co z nia (pismo, redakcja) zostaje u czlowieka.

## Zaleznosc (swiadomy wyjatek od stdlib)

```bash
pip install contextgem>=0.25.1
```

Grounded-extraction LLM nie da sie zrobic w samym stdlib - dlatego ten skill (w odroznieniu od
wiekszosci skilli MateMatic) ma jedna zaleznosc. Rdzen deterministyczny zostaje w stdlib doc-intel.

## Quick start

```bash
# LOKALNIE (RODO-safe, domyslnie) - wymaga dzialajacego Ollama z modelem 7-14B:
python scripts/ekstrakcja_llm.py --text umowa.txt --concepts koncepty.json \
    --model ollama_chat/llama3.1:8b --api-base http://localhost:11434

# z .docx (przez DocxConverter contextgem):
python scripts/ekstrakcja_llm.py --docx pismo.docx --concepts koncepty.json --output text

# CHMURA - TYLKO dane syntetyczne / nie-klienckie (transfer poza EOG):
python scripts/ekstrakcja_llm.py --sample --model openrouter/deepseek/deepseek-chat --allow-cloud
```

## Specyfikacja konceptow (JSON)

```json
{
  "concepts": [
    {"name": "Kara umowna", "description": "Postanowienie o karze umownej", "type": "string",
     "reference_depth": "sentences", "justifications": true},
    {"name": "Termin platnosci (dni)", "description": "Dni na platnosc od faktury", "type": "numeric",
     "numeric_type": "int", "reference_depth": "sentences"},
    {"name": "Klauzula poufnosci obecna", "description": "Czy umowa zawiera NDA", "type": "boolean"}
  ]
}
```

Typy: `string`, `numeric` (+`numeric_type`: int/float), `boolean`, `date`. `reference_depth`:
`sentences` lub `paragraphs`. `justifications: true` dolacza uzasadnienie modelu.

## Wyjscie - kontrakt doc-intel

```json
{
  "concept": "Kara umowna",
  "block_type": "concept",
  "text": "kara umowna 0,5% wynagrodzenia za kazdy dzien zwloki",
  "confidence": "grounded",           // "grounded" gdy jest ref, "ungrounded" gdy model nie zakotwiczyl
  "refs": ["W razie opoznienia Wykonawca zaplaci kare umowna w wysokosci 0,5%..."],
  "justification": "Zdanie wprost okresla kare za opoznienie i jej stawke."
}
```

`refs` -> podaj do `citation-grounding-pl`, aby zweryfikowac, ze cytat realnie istnieje w
dokumencie (podwojne zabezpieczenie anti-halucynacja: contextgem kotwiczy, my weryfikujemy).

**Uwaga o confidence:** contextgem nie daje liczbowej pewnosci per-item. Uzywamy kategorialnego
proxy `grounded`/`ungrounded`. `ungrounded` = model cos wyinferowal, ale nie wskazal zrodla ->
traktuj jak flage do recznej kontroli, nie jak fakt.

## Backend produkcyjny (governance)

- **Dane klienta** -> Ollama 7-14B na appliance PATRON, albo model hostowany w EOG. Maszyna
  deweloperska bywa za slaba (model 3B daje zly JSON) - dlatego model zyje na appliance.
- **Dane syntetyczne / testy / tresci nie-klienckie** -> dozwolony cloud za `--allow-cloud`.

## Skille sasiednie

- `doc-intel-contract-pl` - stdlib core (struktura, bbox, PII); ten skill to warstwa LLM ponad nim
- `citation-grounding-pl` - weryfikacja refs (obowiazkowa przed uzyciem konceptu w pismie)
- `klauzule-kontraktowe-pl`, `redline-docx-pl` - dalsze przetwarzanie wyciagnietych klauzul

## Referencje

- [wzorce_konceptow_prawnych.md](references/wzorce_konceptow_prawnych.md) - gotowe specyfikacje konceptow dla typowych dokumentow (umowa, wyrok, pismo procesowe)

---

**Wersja:** 1.0.0
**Pochodzenie:** WRAP na `shcherbak-ai/contextgem` (Apache-2.0). My dodajemy: kontrakt doc-intel,
most do citation-grounding-pl, banner governance i BRAMKE backendu (odmowa cloud bez flagi).
Bramka 1 (dziala live) zweryfikowana 2026-07-21 realna ekstrakcja PL. Atrybucja w `LICENSE`.
