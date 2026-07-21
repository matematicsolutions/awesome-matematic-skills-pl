# doc-intel-llm-tier-pl

Warstwa **LLM-tier** ekstrakcji groundowanej dla polskich dokumentow prawnych. WRAP na
`contextgem` (Apache-2.0). Dopelnia stdlib `doc-intel-contract-pl` (nie zastepuje).

Wyciaga z umowy/pisma/wyroku **inferowane koncepty** (kara umowna, termin, ryzyko), ktorych
nie zlapie regex, i **zakotwicza kazdy do zdania zrodlowego** + uzasadnienie. Zwraca rekordy
zgodne z kontraktem doc-intel: `{concept, block_type, text, confidence, refs, justification}`.

## Zaleznosc

```bash
pip install contextgem>=0.25.1
```

Swiadomy wyjatek od reguly stdlib - grounded-extraction LLM nie da sie zrobic w samym stdlib.

## Uzycie

```bash
# LOKALNIE (RODO-safe, domyslnie) - Ollama z modelem 7-14B:
python scripts/ekstrakcja_llm.py --docx umowa.docx --concepts koncepty.json \
    --model ollama_chat/llama3.1:8b --api-base http://localhost:11434 --output text

# CHMURA - TYLKO dane syntetyczne/nie-klienckie:
python scripts/ekstrakcja_llm.py --sample --model openrouter/deepseek/deepseek-chat --allow-cloud
```

Wzorce `--concepts` dla umowy/wyroku/pisma: `references/wzorce_konceptow_prawnych.md`.

## Governance (wbudowany w tool)

- Domyslny backend **lokalny** (Ollama). Dla danych klienta - TYLKO taki.
- Model chmurowy: tool **odmawia** (exit 2) bez `--allow-cloud` i **ostrzega** o transferze poza EOG.
- Cloud dozwolony wylacznie na danych syntetycznych/nie-klienckich.

## Miejsce w ukladance

```
stdlib doc-intel-contract-pl   (struktura, bbox, PII - zero LLM)
        │
        ▼
doc-intel-llm-tier-pl          (koncepty + grounding zdaniowy - warstwa LLM)  ← TEN SKILL
        │
        ▼
citation-grounding-pl          (weryfikacja refs - anti-halucynacja)
```

## Backend produkcyjny

Dane klienta -> Ollama 7-14B na appliance PATRON albo model w EOG (maszyna dev bywa za slaba).
Patrz `Projects/contextgem-wrap-poc/DECISION.md`.

## Pochodzenie

WRAP na `shcherbak-ai/contextgem` (Apache-2.0, dependency nie vendored). Nasze: kontrakt
doc-intel, most do citation-grounding, banner + bramka governance, wzorce PL. Patrz `LICENSE`.
