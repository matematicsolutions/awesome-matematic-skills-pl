"""CLI: znormalizuj wyjscie silnika OCR/PDF do kontraktu Document Intelligence.

Uzycie:
  python normalize.py --engine opendataloader plik.json
  python normalize.py --engine pdftotext plik.txt --threshold 0.9
  cat plik.json | python normalize.py --engine opendataloader -

Exit: 0 = kontrakt poprawny (schema-valid), 2 = blad wejscia/kontrakt niepoprawny.
Zero sieci (Article I). Zero LLM (Article IV).
"""
from __future__ import annotations

import argparse
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from contract import build_contract, validate  # noqa: E402
from adapters import opendataloader as odl  # noqa: E402
from adapters import pdftotext as ptt  # noqa: E402
from adapters import chandra as chd  # noqa: E402
from adapters import gaius as gai  # noqa: E402
from adapters import vlm_html as vlm  # noqa: E402
import degeneracja  # noqa: E402
import pii_flags  # noqa: E402
import signature  # noqa: E402


def _read(path: str) -> bytes:
    if path == "-":
        return sys.stdin.buffer.read()
    with open(path, "rb") as fh:
        return fh.read()


def main(argv=None) -> int:
    try:  # JSON zawsze UTF-8, niezaleznie od locale Windows (cp1250)
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser(description="Document Intelligence Output Contract")
    ap.add_argument("input", help="plik wejsciowy lub '-' dla stdin")
    ap.add_argument("--engine", required=True,
                    choices=["opendataloader", "pdftotext", "chandra", "gaius", "vlm-html"],
                    help="silnik zrodlowy (gaius = OCR PATRONa /ocr/poll; "
                         "vlm-html = dowolny VLM z prompt-kontraktem "
                         "references/prompt_vlm_ocr_pl.md)")
    ap.add_argument("--threshold", type=float, default=0.85,
                    help="prog confidence-gating (domyslnie 0.85)")
    ap.add_argument("--pretty", action="store_true", help="wyjscie z wcieciami")
    ap.add_argument("--no-pii", action="store_true",
                    help="wylacz detekcje PII/redaction_candidates (domyslnie wlaczona)")
    ap.add_argument("--no-signatures", action="store_true",
                    help="wylacz heurystyke podpisu/pieczatki (domyslnie wlaczona)")
    args = ap.parse_args(argv)

    try:
        raw = _read(args.input)
    except OSError as exc:
        print(f"BLAD wejscia: {exc}", file=sys.stderr)
        return 2

    path = None if args.input == "-" else args.input

    engine_variant = None
    try:
        if args.engine == "opendataloader":
            data = json.loads(raw.decode("utf-8"))
            blocks = odl.to_blocks(data)
            pages = odl.page_count(data)
        elif args.engine == "chandra":
            data = json.loads(raw.decode("utf-8"))
            blocks = chd.to_blocks(data)
            pages = chd.page_count(data)
        elif args.engine == "gaius":
            result = json.loads(raw.decode("utf-8"))
            blocks = gai.to_blocks(result)
            pages = gai.page_count(result)
            engine_variant = gai.variant(result)
        elif args.engine == "vlm-html":
            text = raw.decode("utf-8", errors="replace")
            blocks = vlm.to_blocks(text)
            pages = vlm.page_count(text)
            if degeneracja.wykryj_zapetlenie(text):
                # petla generacji konczy sie exit 0 z ucietym ogonem -
                # zamieniamy cicha niekompletnosc na glosna flage
                blocks[-1].flags = sorted(set(blocks[-1].flags) | {"degenerate_tail"})
                print("OSTRZEZENIE: wykryto zapetlenie generacji (powtarzajacy "
                      "sie ogon) - wynik prawdopodobnie niekompletny",
                      file=sys.stderr)
        else:  # pdftotext
            text = raw.decode("utf-8", errors="replace")
            blocks = ptt.to_blocks(text)
            pages = ptt.page_count(text)
    except (ValueError, KeyError) as exc:
        print(f"BLAD parsowania ({args.engine}): {exc}", file=sys.stderr)
        return 2

    redaction = [] if args.no_pii else list(pii_flags.annotate(blocks))
    if not args.no_signatures:
        for cid in signature.apply(blocks):
            if cid not in redaction:
                redaction.append(cid)
    if args.no_pii and not redaction and args.no_signatures:
        redaction = None

    contract = build_contract(
        blocks, engine=args.engine, raw=raw, path=path,
        pages=pages, threshold=args.threshold,
        redaction_candidates=redaction, engine_variant=engine_variant,
    )

    errors = validate(contract)
    if errors:
        print("BLAD: kontrakt niezgodny ze schematem:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 2

    indent = 2 if args.pretty else None
    print(json.dumps(contract, ensure_ascii=False, indent=indent))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
