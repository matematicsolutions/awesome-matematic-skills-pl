"""Rdzen kontraktu Document Intelligence.

Zero zaleznosci zewnetrznych (Python 3.11+ stdlib). RODO-safe, offline.
Article I (zero-cloud), Article IV (determinizm/audyt) konstytucji projektu.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

CONTRACT_VERSION = "1.2.0"  # 1.2.0: gating dwuosiowy (pewnosc x ugruntowanie)
#                            + werdykt trojstanowy zgodny z routing_gate
#                            1.1.0: +engine vlm-html (prompt-kontrakt VLM)

BLOCK_TYPES = {
    "title", "paragraph", "table", "list", "equation",
    "signature", "stamp", "figure", "header", "footer", "unknown",
}

_SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "contract", "contract.schema.json",
)


@dataclass
class Block:
    id: str
    page: int
    bbox: list | None          # [x0,y0,x1,y1] znormalizowane 0-1, albo None
    block_type: str
    text: str
    confidence: float | None    # 0-1 albo None (silnik nie dostarcza)
    flags: list = field(default_factory=list)

    def __post_init__(self):
        if self.block_type not in BLOCK_TYPES:
            self.block_type = "unknown"


def compute_doc_id(raw: bytes) -> str:
    """Deterministyczny identyfikator wejscia (Article IV)."""
    return hashlib.sha256(raw).hexdigest()


def _gating(blocks: list[Block], threshold: float) -> dict:
    """Gating DWUOSIOWY (Article III human-in-the-loop).

    Do 1.1.0 istniala jedna os - `confidence` silnika. To mieszalo dwa rozne
    twierdzenia, ktore moga sie rozjechac:

      os PEWNOSCI    - czy silnik jest pewny ODCZYTANYCH ZNAKOW
      os UGRUNTOWANIA - czy blok da sie w ogole WSKAZAC w dokumencie (bbox)

    Blok z confidence 0.99 i `bbox: None` jest pewny i jednoczesnie
    niecytowalny: nie da sie go podswietlic ani przypiac do strony. Stare
    gating zaliczalo go do `auto_approved` i nikt sie nie dowiadywal.

    Werdykt trojstanowy jest zgodny slownictwem i kodami wyjscia z
    `routing_gate.py` (ok / degraded / failed, 0 / 10 / 20).

    PUSTA LISTA BLOKOW = `failed`, nigdy `ok`. Bramka, ktora przy zerowym
    wejsciu mowi "nic do przegladu", przepuszcza dokument, ktorego nikt
    nie przeczytal.
    """
    review, auto, ungroundable = [], [], []
    for b in blocks:
        if b.confidence is None or b.confidence < threshold:
            review.append(b.id)
        else:
            auto.append(b.id)
        if b.bbox is None:
            ungroundable.append(b.id)

    total = len(blocks)
    if total == 0:
        verdict, note = "failed", "zero blokow - nie ma czego przegladac ani cytowac"
    elif len(ungroundable) == total:
        verdict, note = "degraded", "zaden blok nie ma bbox - cytat bez regionu dokumentu"
    elif review or ungroundable:
        verdict, note = "degraded", "czesc blokow wymaga czlowieka albo nie da sie ich wskazac"
    else:
        verdict, note = "ok", "wszystkie bloki pewne i ugruntowane"

    return {
        "threshold": threshold,
        "review_required": review,
        "auto_approved": auto,
        "ungroundable": ungroundable,
        "verdict": verdict,
        "note": note,
        # pelny mianownik: udzial, nie sama liczba
        "counts": {
            "total": total,
            "review_required": len(review),
            "auto_approved": len(auto),
            "ungroundable": len(ungroundable),
        },
    }


GATING_EXIT = {"ok": 0, "degraded": 10, "failed": 20}


def build_contract(
    blocks: list[Block],
    *,
    engine: str,
    raw: bytes,
    path: str | None = None,
    pages: int | None = None,
    threshold: float = 0.85,
    redaction_candidates: list[str] | None = None,
    engine_variant: str | None = None,
) -> dict:
    contract = {
        "doc_id": compute_doc_id(raw),
        "contract_version": CONTRACT_VERSION,
        "source": {"path": path, "engine": engine, "engine_variant": engine_variant, "pages": pages},
        "blocks": [asdict(b) for b in blocks],
        "gating": _gating(blocks, threshold),
        "redaction_candidates": list(redaction_candidates or []),
        "meta": {"created_at": datetime.now(timezone.utc).isoformat()},
    }
    return contract


# ---------------------------------------------------------------------------
# Minimalny walidator JSON Schema (podzbior draft-07: type/required/properties/
# items/enum). Zero zaleznosci - Article I. Wystarcza dla naszego schematu.
# ---------------------------------------------------------------------------

_TYPE_MAP = {
    "object": dict, "array": list, "string": str,
    "number": (int, float), "integer": int, "boolean": bool, "null": type(None),
}


def _check_type(value, type_spec, pointer: str, errors: list):
    types = type_spec if isinstance(type_spec, list) else [type_spec]
    # bool jest podtypem int w Pythonie - odfiltruj przy integer/number
    for t in types:
        py = _TYPE_MAP[t]
        if t in ("integer", "number") and isinstance(value, bool):
            continue
        if isinstance(value, py):
            return True
    errors.append(f"{pointer}: oczekiwano {types}, jest {type(value).__name__}")
    return False


def _validate(value, schema: dict, pointer: str, errors: list):
    if "type" in schema:
        if not _check_type(value, schema["type"], pointer, errors):
            return
    if "enum" in schema and value not in schema["enum"]:
        errors.append(f"{pointer}: '{value}' spoza enum {schema['enum']}")
    if isinstance(value, dict):
        for req in schema.get("required", []):
            if req not in value:
                errors.append(f"{pointer}: brak wymaganego pola '{req}'")
        for key, subschema in schema.get("properties", {}).items():
            if key in value:
                _validate(value[key], subschema, f"{pointer}.{key}", errors)
    if isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            _validate(item, schema["items"], f"{pointer}[{i}]", errors)


def load_schema() -> dict:
    with open(_SCHEMA_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def validate(contract: dict) -> list[str]:
    """Zwraca liste bledow ([] = kontrakt poprawny)."""
    errors: list[str] = []
    _validate(contract, load_schema(), "$", errors)
    return errors
