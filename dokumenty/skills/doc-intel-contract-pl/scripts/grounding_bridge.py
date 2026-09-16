# -*- coding: utf-8 -*-
"""Most kontrakt Document Intelligence -> zadanie citation-grounding-pl.

Kontrakt to STRONA ZRODLOWA (bloki dokumentu z text+bbox). Ten most lokalizuje
kazdy cytat w blokach i doklada dwie rzeczy:

  `anchor_resolved` = {block_id, page, bbox, span}  - gdzie to jest
  `evidence`        = {kind, resolution, match_count, ...} - JAK MOCNY to dowod

Wynik pasuje do wejscia ground-citations.mjs:
  { "items": [ { id, source_id, claim_type, quote, source_text, anchor,
                 anchor_resolved, evidence } ] }

Zero zaleznosci, zero sieci (Article I). Cala mechanika lokalizacji zyje w
`evidence.py` - jeden dom dla reguly normalizacji i bramek dystynktywnosci.

## Co zmienilo sie w 2.0 (2026-08-30) i dlaczego

Wersja 1.x miala trzy zmierzone defekty, kazdy klasy "konczy sie sukcesem":

1. `_locate` zwracal PIERWSZE trafienie jako jedyna, pewna kotwice. Na fixture
   `pismo_pl_typografia` termin "Sadu Okregowego" wystepuje w 5 blokach,
   a most podawal `b0003` z bbox i zadnego sygnalu, ze sa inne. Fail-wrong.
2. Stary `normalize()` nie znal dywizu nielamliwego U+2011 ani miekkiego dywizu
   U+00AD - a to sa znaki, ktore polski PDF wstawia w sygnaturach i w
   justowanych akapitach. Cytaty "II-CSK 118/24" i "prawa materialnego" byly
   po prostu GUBIONE i ladowaly w fallbacku "caly dokument".
   (U+2011 to ta sama pulapka, ktora zmierzylismy wczesniej na EUR-Lex.)
3. Zwijanie bialych znakow bez mapy offsetow uniemozliwialo zwrot zakresu
   znakowego, wiec rozdzielczosc konczyla sie na bboxie CALEGO bloku.

Lek: `evidence.normalize_with_map` (mapa offsetow -> `span` w oryginale),
bramki dystynktywnosci fail-empty z jawnym `match_count`, oraz zasada
**wieloznacznosc idzie do raportu, nigdy do auto-wyboru**: przy wiecej niz
jednym trafieniu `anchor_resolved` jest `None`, a wszystkie kandydatury leza
w `evidence.anchors`. Naiwny konsument widzi wtedy uczciwe "brak jednej
kotwicy" zamiast falszywej pewnosci.
"""
from __future__ import annotations

import evidence as EV
from evidence import (  # re-eksport: jeden dom reguly normalizacji
    KIND_STRENGTH,
    RESOLUTION_STRENGTH,
    normalize,
    normalize_with_map,
)

BRIDGE_VERSION = "2.0.0"

# domyslny typ roszczenia gdy cytat w cudzyslowie -> wymaga poziomu FRAGMENT
DEFAULT_CLAIM_TYPE = "cytat_doslowny"

__all__ = [
    "BRIDGE_VERSION",
    "DEFAULT_CLAIM_TYPE",
    "build_task",
    "build_parser",
    "gate",
    "normalize",
    "normalize_with_map",
    "KIND_STRENGTH",
    "RESOLUTION_STRENGTH",
]


def gate(
    ev: dict,
    *,
    min_kind: str = "normalized",
    min_resolution: str = "span",
    require_unambiguous: bool = True,
) -> bool:
    """Bramka TRZYWARUNKOWA: rodzaj dowodu, rozdzielczosc, jednoznacznosc.

    Obie osie musza byc spelnione jednoczesnie. Jedna liczba `confidence`
    tego nie potrafila: "silnik OCR jest pewny znakow" i "wiem, gdzie
    dokladnie to jest" to dwa rozne twierdzenia i moga sie rozjechac.

    Trzeci warunek dopisany po przebiegu bojowym 2026-08-30: cytat
    "Sadu Okregowego" mial kind=verbatim i resolution=span, wiec przechodzil
    bramke - majac PIEC kandydatow i `anchor_resolved = None`. Mocny dowod na
    piec roznych miejsc nie jest mocnym dowodem na jedno. Bez tego warunku
    bramka odtwarzala pietro wyzej dokladnie ten fail-wrong, ktory warstwa
    dowodowa mial usunac.

    Bramka jest domyslnie ostra (normalized/span/jednoznaczny), bo do pisma
    procesowego idzie zakres znakowy, nie "gdzies w dokumencie".
    """
    k = KIND_STRENGTH.get(ev.get("kind"), 0) >= KIND_STRENGTH.get(min_kind, 0)
    r = RESOLUTION_STRENGTH.get(ev.get("resolution"), 0) >= RESOLUTION_STRENGTH.get(min_resolution, 0)
    if require_unambiguous and len(ev.get("anchors") or []) > 1:
        return False
    return k and r


def build_task(contract: dict, quotes) -> dict:
    """Zbuduj zadanie citation-grounding-pl z kontraktu + listy cytatow.

    quotes: lista str albo dict {text, claim_type?, source_id?}.

    Kontrakt wyjscia:
    - dokladnie jedno trafienie -> `anchor`/`anchor_resolved` wypelnione,
      `source_text` = tekst tego bloku, `anchor_resolved.span` = zakres
      znakowy w ORYGINALNYM tekscie bloku (nie w znormalizowanym).
    - wiecej niz jedno trafienie -> `anchor_resolved = None` i flaga
      `wieloznaczny`; wszystkie kandydatury w `evidence.anchors`.
      Nie zgadujemy, ktora jest ta wlasciwa.
    - brak trafienia -> `source_text` = caly dokument, `evidence.kind`
      mowi, czy cytat przeszedl przez granice blokow (`observed`) czy
      nie ma go wcale (`derived`).
    """
    doc_id = contract.get("doc_id", "")
    blocks = contract.get("blocks", [])
    full_text = "\n\n".join((b.get("text", "") or "") for b in blocks)
    by_id = {b.get("id"): b for b in blocks}

    items = []
    for i, q in enumerate(quotes, start=1):
        if isinstance(q, str):
            text, claim_type, source_id = q, DEFAULT_CLAIM_TYPE, doc_id
        else:
            text = q.get("text", "")
            claim_type = q.get("claim_type", DEFAULT_CLAIM_TYPE)
            source_id = q.get("source_id", doc_id)

        ev = EV.locate(text, blocks)
        flags = []
        anchor_id = None
        anchor_resolved = None
        source_text = full_text

        if len(ev.anchors) == 1:
            a = ev.anchors[0]
            anchor_id = a.block_id
            anchor_resolved = {
                "block_id": a.block_id,
                "page": a.page,
                "bbox": a.bbox,
                "span": list(a.span) if a.span else None,
            }
            source_text = (by_id.get(a.block_id, {}) or {}).get("text", "") or full_text
        elif len(ev.anchors) > 1:
            flags.append("wieloznaczny")
        if ev.kind == "normalized":
            # glify zrodla roznia sie od cytatu - przy przepisywaniu do pisma
            # trzeba wziac tekst ZRODLA, nie cytat
            flags.append("glify_zrodla_inne")
        if ev.skipped_reason:
            flags.append(ev.skipped_reason)

        items.append(
            {
                "id": "c%03d" % i,
                "source_id": source_id,
                "claim_type": claim_type,
                "quote": text,
                "source_text": source_text,
                "anchor": anchor_id,
                "anchor_resolved": anchor_resolved,
                "evidence": ev.as_dict(),
                "flags": flags,
            }
        )

    located = sum(1 for it in items if it["anchor_resolved"])
    ambiguous = sum(1 for it in items if "wieloznaczny" in it["flags"])
    return {
        "items": items,
        "summary": {
            "bridge_version": BRIDGE_VERSION,
            "total": len(items),
            "located_single": located,
            "ambiguous": ambiguous,
            "unlocated": len(items) - located - ambiguous,
            "gate_passed": sum(1 for it in items if gate(it["evidence"])),
        },
    }


# --- CLI -------------------------------------------------------------------
def build_parser():
    """Parser wystawiony osobno, zeby dalo sie go sprawdzic MECHANICZNIE.

    `tests/test_dokumentacja_zakotwiczona.py` wyciaga flagi z blokow bash w
    SKILL.md i przepuszcza je przez ten parser. Flaga opisana w dokumentacji,
    ktorej program nie zna, przestaje byc mozliwa do przeoczenia.
    """
    import argparse

    ap = argparse.ArgumentParser(description="Most kontrakt -> citation-grounding-pl")
    ap.add_argument("contract", help="plik kontraktu JSON (wyjscie normalize.py) lub '-'")
    ap.add_argument("--quotes", required=True,
                    help="plik z cytatami (jeden na linie) lub '-' dla stdin")
    ap.add_argument("--claim-type", default=DEFAULT_CLAIM_TYPE,
                    help="typ roszczenia dla wszystkich cytatow (domyslnie %s)" % DEFAULT_CLAIM_TYPE)
    ap.add_argument("--min-kind", default="normalized", choices=list(KIND_STRENGTH),
                    help="minimalny RODZAJ dowodu dla bramki (domyslnie normalized)")
    ap.add_argument("--min-resolution", default="span", choices=list(RESOLUTION_STRENGTH),
                    help="minimalna ROZDZIELCZOSC dla bramki (domyslnie span)")
    ap.add_argument("--pretty", action="store_true")
    return ap


def _main(argv=None) -> int:
    import json
    import sys

    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    args = build_parser().parse_args(argv)

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
        print("BLAD wejscia: %s" % exc, file=sys.stderr)
        return 2

    task = build_task(contract, quotes)
    for it in task["items"]:
        it["gate_passed"] = gate(it["evidence"], min_kind=args.min_kind,
                                 min_resolution=args.min_resolution)
    task["summary"]["gate_passed"] = sum(1 for it in task["items"] if it["gate_passed"])
    task["summary"]["gate"] = {"min_kind": args.min_kind, "min_resolution": args.min_resolution}

    print(json.dumps(task, ensure_ascii=False, indent=2 if args.pretty else None))
    # exit 10 gdy cokolwiek nie przeszlo bramki - trojstan, nie cisza
    return 10 if task["summary"]["gate_passed"] < task["summary"]["total"] else 0


if __name__ == "__main__":
    raise SystemExit(_main())
