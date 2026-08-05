"""US3 / T030: most kontrakt Document Intelligence -> zadanie citation-grounding-pl.

Kontrakt to STRONA ZRODLOWA (bloki dokumentu z text+bbox). Ten most lokalizuje
kazdy cytat w blokach i doklada `anchor_resolved = {page, bbox, block_id}` -
to jest wartosc "cytat -> region dokumentu", ktorej sam grounding nie mial.

Wynik pasuje 1:1 do wejscia ground-citations.mjs:
  { "items": [ { id, source_id, claim_type, quote, source_text, anchor, anchor_resolved } ] }

Zero zaleznosci, zero sieci (Article I). Normalizacja spojna z ground-citations.mjs
(lowercase, ujednolicenie cudzyslowow/myslnikow, zwiniecie bialych znakow).
"""
from __future__ import annotations

import re

_QUOTE_CHARS = re.compile(r"[„“”»«’‘'`]")
_DASHES = re.compile(r"[—–]")
_HYPHEN_WRAP = re.compile(r"-\s*\n\s*")
_WS = re.compile(r"\s+")

# domyslny typ roszczenia gdy cytat w cudzyslowie -> wymaga poziomu FRAGMENT
DEFAULT_CLAIM_TYPE = "cytat_doslowny"


def normalize(s: str) -> str:
    if s is None:
        return ""
    s = _HYPHEN_WRAP.sub("", str(s))
    s = _QUOTE_CHARS.sub('"', s)
    s = _DASHES.sub("-", s)
    s = s.lower()
    s = _WS.sub(" ", s)
    return s.strip()


def _locate(quote: str, blocks: list[dict]) -> dict | None:
    """Znajdz pierwszy blok zawierajacy znormalizowany cytat. Zwroc anchor lub None."""
    # obetnij cudzyslowy brzegowe (cytat bywa owiniety w „...") - wewnetrzne zostaja
    nq = normalize(quote).strip('" ')
    if not nq:
        return None
    for b in blocks:
        if nq in normalize(b.get("text", "")):
            return {
                "block_id": b["id"],
                "page": b["page"],
                "bbox": b.get("bbox"),
                "source_text": b.get("text", ""),
            }
    return None


def build_task(contract: dict, quotes) -> dict:
    """Zbuduj zadanie citation-grounding-pl z kontraktu + listy cytatow.

    quotes: lista str albo dict {text, claim_type?, source_id?}.
    Cytat znaleziony -> source_text = tekst bloku + anchor_resolved z bbox.
    Cytat nieznaleziony -> source_text = caly dokument, anchor_resolved = null
    (grounding wtedy uczciwie obnizy poziom - to poprawne zachowanie).
    """
    doc_id = contract.get("doc_id", "")
    blocks = contract.get("blocks", [])
    full_text = "\n\n".join(b.get("text", "") for b in blocks)

    items = []
    for i, q in enumerate(quotes, start=1):
        if isinstance(q, str):
            text, claim_type, source_id = q, DEFAULT_CLAIM_TYPE, doc_id
        else:
            text = q.get("text", "")
            claim_type = q.get("claim_type", DEFAULT_CLAIM_TYPE)
            source_id = q.get("source_id", doc_id)

        hit = _locate(text, blocks)
        if hit:
            item = {
                "id": f"c{i:03d}",
                "source_id": source_id,
                "claim_type": claim_type,
                "quote": text,
                "source_text": hit["source_text"],
                "anchor": hit["block_id"],
                "anchor_resolved": {
                    "block_id": hit["block_id"],
                    "page": hit["page"],
                    "bbox": hit["bbox"],
                },
            }
        else:
            item = {
                "id": f"c{i:03d}",
                "source_id": source_id,
                "claim_type": claim_type,
                "quote": text,
                "source_text": full_text,
                "anchor": None,
                "anchor_resolved": None,
            }
        items.append(item)

    return {"items": items}


# --- CLI -------------------------------------------------------------------
def _main(argv=None) -> int:
    import argparse
    import json
    import sys

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser(description="Most kontrakt -> citation-grounding-pl")
    ap.add_argument("contract", help="plik kontraktu JSON (wyjscie normalize.py) lub '-'")
    ap.add_argument("--quotes", required=True,
                    help="plik z cytatami (jeden na linie) lub '-' dla stdin")
    ap.add_argument("--claim-type", default=DEFAULT_CLAIM_TYPE,
                    help=f"typ roszczenia dla wszystkich cytatow (domyslnie {DEFAULT_CLAIM_TYPE})")
    ap.add_argument("--pretty", action="store_true")
    args = ap.parse_args(argv)

    def _read(p):
        if p == "-":
            return sys.stdin.read()
        with open(p, encoding="utf-8") as fh:
            return fh.read()

    try:
        contract = json.loads(_read(args.contract))
        quotes = [
            {"text": ln.strip(), "claim_type": args.claim_type}
            for ln in _read(args.quotes).splitlines() if ln.strip()
        ]
    except (OSError, ValueError) as exc:
        print(f"BLAD wejscia: {exc}", file=sys.stderr)
        return 2

    task = build_task(contract, quotes)
    print(json.dumps(task, ensure_ascii=False, indent=2 if args.pretty else None))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
