#!/usr/bin/env python3
"""ekstrakcja_llm.py - warstwa LLM-tier ekstrakcji groundowanej dla polskich dokumentow prawnych.

WRAP MateMatic na `contextgem` (Apache-2.0, shcherbak-ai). Bierze dokument (tekst lub .docx) +
specyfikacje konceptow do wyciagniecia i zwraca rekordy zgodne z kontraktem doc-intel-contract-pl:
    {concept, block_type, text, confidence, refs, justification}
gdzie `refs` to zdania/akapity zrodlowe (grounding) - most do citation-grounding-pl.

Rozni sie od stdlib doc-intel-contract-pl: TAMTEN jest deterministyczny/zero-LLM (bbox, block_type,
redaction). TEN dodaje inferencje LLM (koncepty, ktorych nie da sie wyciagnac regexem) + grounding
zdaniowy. Uzywaj razem: stdlib doc-intel do struktury/PII, ten do konceptow prawnych.

GRANICA GOVERNANCE (wbudowana w tool):
  - Domyslny backend = LOKALNY (Ollama). Dla danych KLIENTA (tajemnica adwokacka + RODO) TYLKO taki.
  - Model chmurowy (OpenRouter/OpenAI/DeepSeek itd.) wymaga JAWNEJ flagi --allow-cloud i drukuje
    ostrzezenie: cloud = wylacznie dane SYNTETYCZNE / nie-klienckie (transfer poza EOG).
  - Tool przygotowuje ekstrakcje; decyzja co z nia zrobic (pismo, redakcja) zostaje u czlowieka.

Zaleznosc (NIE stdlib - swiadomy wyjatek, bo grounded-extraction LLM nie da sie zrobic stdlib):
    pip install contextgem>=0.25.1

Schemat specyfikacji konceptow (JSON):
{
  "concepts": [
    {"name": "Kara umowna", "description": "Postanowienie o karze umownej", "type": "string",
     "reference_depth": "sentences", "justifications": true},
    {"name": "Termin platnosci (dni)", "description": "Dni na platnosc", "type": "numeric",
     "numeric_type": "int", "reference_depth": "sentences"}
  ]
}

Uzycie:
    # lokalnie (RODO-safe, domyslnie):
    python ekstrakcja_llm.py --text umowa.txt --concepts koncepty.json
    python ekstrakcja_llm.py --docx umowa.docx --concepts koncepty.json --model ollama_chat/llama3.1:8b

    # chmura - TYLKO dane syntetyczne/nie-klienckie:
    python ekstrakcja_llm.py --text probka.txt --concepts koncepty.json \
        --model openrouter/deepseek/deepseek-chat --allow-cloud

    # wbudowana probka (dane syntetyczne):
    python ekstrakcja_llm.py --sample --model openrouter/deepseek/deepseek-chat --allow-cloud
"""

import argparse
import json
import os
import sys


BANNER = (
    "INTERPRETACJA MateMatic - narzedzie pomocnicze, NIE porada prawna. Ekstrakcja LLM moze "
    "sie mylic - kazdy koncept zweryfikuj przez citation-grounding-pl przed uzyciem w pismie."
)

SAMPLE_TEXT = (
    "Umowa zawarta w dniu 15 stycznia 2026 r. w Warszawie pomiedzy Acme sp. z o.o. a Beta S.A.\n\n"
    "Wykonawca zobowiazuje sie wykonac przedmiot umowy w terminie 30 dni od dnia jej zawarcia. "
    "Wynagrodzenie wynosi 50 000 zl netto platne w terminie 14 dni od dnia doreczenia faktury.\n\n"
    "W razie opoznienia Wykonawca zaplaci kare umowna w wysokosci 0,5% wynagrodzenia za kazdy "
    "dzien zwloki. Sadem wlasciwym jest sad w Warszawie."
)

SAMPLE_CONCEPTS = {
    "concepts": [
        {"name": "Kara umowna", "description": "Postanowienie o karze umownej za opoznienie i jej stawka",
         "type": "string", "reference_depth": "sentences", "justifications": True},
        {"name": "Termin platnosci (dni)", "description": "Liczba dni na platnosc od doreczenia faktury",
         "type": "numeric", "numeric_type": "int", "reference_depth": "sentences"},
        {"name": "Sad wlasciwy", "description": "Wskazany sad wlasciwy dla sporow",
         "type": "string", "reference_depth": "sentences"},
    ]
}


def _is_local_backend(model: str) -> bool:
    m = (model or "").lower()
    return m.startswith("ollama") or m.startswith("lm_studio") or m.startswith("local")


def _build_concept(spec):
    """Buduje obiekt konceptu contextgem ze specyfikacji (import leniwy)."""
    from contextgem import StringConcept, NumericalConcept, BooleanConcept, DateConcept

    ctype = spec.get("type", "string").lower()
    common = dict(
        name=spec["name"],
        description=spec.get("description", spec["name"]),
        add_references=True,
        reference_depth=spec.get("reference_depth", "sentences"),
    )
    if spec.get("justifications"):
        common["add_justifications"] = True
        common["justification_depth"] = spec.get("justification_depth", "brief")

    if ctype == "numeric":
        return NumericalConcept(numeric_type=spec.get("numeric_type", "int"), **common)
    if ctype == "boolean":
        return BooleanConcept(**common)
    if ctype == "date":
        return DateConcept(**common)
    return StringConcept(**common)


def to_contract(doc):
    """Mapuje wyekstrahowane pozycje contextgem na rekordy kontraktu MateMatic."""
    records = []
    for c in doc.concepts:
        for it in c.extracted_items:
            refs = getattr(it, "reference_sentences", None) or getattr(it, "reference_paragraphs", None) or []
            ref_texts = [getattr(r, "raw_text", str(r)) for r in refs]
            records.append({
                "concept": c.name,
                "block_type": "concept",
                "text": str(it.value),
                # contextgem nie daje liczbowej pewnosci per-item; kategorialne proxy:
                "confidence": "grounded" if ref_texts else "ungrounded",
                "refs": ref_texts,
                "justification": getattr(it, "justification", None),
            })
    return records


def extract(raw_text, concepts_spec, model, api_base=None):
    """Uruchamia ekstrakcje contextgem i zwraca rekordy kontraktu (import leniwy)."""
    from contextgem import Document, DocumentLLM

    doc = Document(raw_text=raw_text)
    doc.concepts = [_build_concept(s) for s in concepts_spec.get("concepts", [])]

    kwargs = {"model": model}
    if api_base:
        kwargs["api_base"] = api_base
    if not _is_local_backend(model):
        # cloud - LiteLLM czyta klucz z env (OPENROUTER_API_KEY / OPENAI_API_KEY itd.)
        key = os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY")
        if key:
            kwargs["api_key"] = key
    llm = DocumentLLM(**kwargs)
    doc = llm.extract_all(doc)
    return to_contract(doc)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="LLM-tier grounded extraction dla polskich dokumentow prawnych (WRAP na contextgem).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    src = parser.add_mutually_exclusive_group()
    src.add_argument("--text", help="Sciezka do pliku .txt")
    src.add_argument("--docx", help="Sciezka do pliku .docx (przez DocxConverter)")
    src.add_argument("--sample", action="store_true", help="Uzyj wbudowanej probki (dane syntetyczne)")
    parser.add_argument("--concepts", help="Sciezka do JSON specyfikacji konceptow (dla --sample opcjonalne)")
    parser.add_argument("--model", default="ollama_chat/llama3.1:8b",
                        help="Model LiteLLM (domyslnie lokalny Ollama). Prefiks 'ollama'/'lm_studio' = lokalny.")
    parser.add_argument("--api-base", default=None, help="URL backendu (np. http://localhost:11434 dla Ollama)")
    parser.add_argument("--allow-cloud", action="store_true",
                        help="Zezwol na model chmurowy. WYMAGANE dla nie-lokalnych. TYLKO dane syntetyczne/nie-klienckie.")
    parser.add_argument("--output", choices=("json", "text"), default="json", help="Format wyjscia")
    args = parser.parse_args()

    # --- BRAMKA GOVERNANCE ---
    if not _is_local_backend(args.model) and not args.allow_cloud:
        print(
            "ODMOWA: model chmurowy '{}' bez flagi --allow-cloud.\n"
            "  Dla danych KLIENTA (tajemnica adwokacka + RODO) uzyj backendu LOKALNEGO/EOG\n"
            "  (np. --model ollama_chat/llama3.1:8b --api-base http://localhost:11434).\n"
            "  Cloud dozwolony TYLKO dla danych syntetycznych/nie-klienckich: dodaj --allow-cloud.".format(args.model),
            file=sys.stderr,
        )
        return 2
    if not _is_local_backend(args.model) and args.allow_cloud:
        print(
            "! OSTRZEZENIE: backend CHMUROWY ({}) - transfer poza EOG. Uzywaj WYLACZNIE na danych\n"
            "  SYNTETYCZNYCH / nie-klienckich. NIGDY na dokumentach klienta.".format(args.model),
            file=sys.stderr,
        )

    # --- WEJSCIE ---
    if args.sample:
        raw_text = SAMPLE_TEXT
        concepts_spec = SAMPLE_CONCEPTS
        if args.concepts:
            with open(args.concepts, "r", encoding="utf-8") as f:
                concepts_spec = json.load(f)
    else:
        if not args.concepts:
            print("blad: --concepts jest wymagane (albo uzyj --sample)", file=sys.stderr)
            return 1
        with open(args.concepts, "r", encoding="utf-8") as f:
            concepts_spec = json.load(f)
        if args.docx:
            try:
                from contextgem import DocxConverter
            except ImportError:
                print("blad: brak contextgem. Zainstaluj: pip install contextgem>=0.25.1", file=sys.stderr)
                return 1
            doc = DocxConverter().convert(args.docx)
            raw_text = doc.raw_text
        elif args.text:
            with open(args.text, "r", encoding="utf-8") as f:
                raw_text = f.read()
        else:
            print("blad: podaj --text, --docx albo --sample", file=sys.stderr)
            return 1

    # --- EKSTRAKCJA ---
    try:
        records = extract(raw_text, concepts_spec, args.model, args.api_base)
    except ImportError:
        print("blad: brak contextgem. Zainstaluj: pip install contextgem>=0.25.1", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"blad ekstrakcji: {e}", file=sys.stderr)
        return 1

    if args.output == "json":
        print(json.dumps({"disclaimer": BANNER, "backend": args.model,
                          "records": records}, ensure_ascii=False, indent=2))
    else:
        print("=" * 72)
        print(f"EKSTRAKCJA LLM-TIER (backend: {args.model})")
        print("=" * 72)
        for r in records:
            print(f"\n  [{r['concept']}] ({r['confidence']})")
            print(f"      wartosc: {r['text']}")
            for ref in r["refs"]:
                print(f"      zrodlo: {ref}")
            if r["justification"]:
                print(f"      uzasadnienie: {r['justification']}")
        print("\n" + "-" * 72)
        print(BANNER)
    return 0


if __name__ == "__main__":
    sys.exit(main())
