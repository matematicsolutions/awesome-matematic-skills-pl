#!/usr/bin/env python3
"""Memo negocjacyjne z edits.json (redline-docx-pl).

Grupuje zmiany wg tierow 1-3, wypisuje rationale / walkaway / precedent.
Dokument WEWNETRZNY - draft do rozmowy dla prawnika, nie do drugiej strony.

Pattern (pola tier/rationale/walkaway/precedent, grupowanie wg tierow):
evolsb/legal-redline-tools (MIT). Kod napisany od zera, zero zaleznosci
(Python stdlib), format wejscia = edits.json adeu + pola negocjacyjne.

Uzycie:
    python memo_negocjacyjne.py edits.json -o memo.md --tytul "Umowa X"
    python memo_negocjacyjne.py edits.json --adeu edits_adeu.json

Exit: 0 = OK, 1 = blad walidacji (tier spoza 1-3, tier 1 bez walkaway,
zly format wejscia), 2 = blad IO.
"""

import argparse
import datetime
import json
import sys

NAGLOWEK_POUFNOSCI = "POUFNE - MATERIAL WEWNETRZNY - NIE PRZEKAZYWAC DRUGIEJ STRONIE"

TIERY = {
    1: "Tier 1 - warunki brzegowe (non-starter)",
    2: "Tier 2 - istotne",
    3: "Tier 3 - pozadane",
}

# Pola znane adeu; reszta to metadane memo i musi byc odcieta przed apply.
POLA_ADEU = ("type", "target_text", "new_text", "comment")


def wczytaj_edits(sciezka):
    with open(sciezka, "r", encoding="utf-8") as f:
        dane = json.load(f)
    if not isinstance(dane, list):
        raise ValueError("edits.json musi byc lista obiektow")
    return dane


def waliduj(edits):
    bledy = []
    for i, e in enumerate(edits):
        if not isinstance(e, dict):
            bledy.append("pozycja %d: nie jest obiektem" % i)
            continue
        tier = e.get("tier")
        if tier is not None and tier not in (1, 2, 3):
            bledy.append("pozycja %d: tier=%r poza zakresem 1-3" % (i, tier))
        if tier == 1 and not str(e.get("walkaway", "")).strip():
            bledy.append(
                "pozycja %d: tier 1 wymaga pola walkaway (granica ustepstwa)" % i
            )
    return bledy


def skrot(tekst, limit=90):
    tekst = " ".join(str(tekst).split())
    return tekst if len(tekst) <= limit else tekst[: limit - 3] + "..."


def pozycja_md(e, nr):
    linie = []
    tytul = e.get("title") or skrot(e.get("target_text", "(brak target_text)"))
    linie.append("### %d. %s" % (nr, tytul))
    linie.append("")
    if e.get("section"):
        linie.append("- **Miejsce w umowie:** %s" % e["section"])
    typ = e.get("type", "modify")
    linie.append("- **Typ zmiany:** %s" % typ)
    if e.get("target_text"):
        linie.append("- **Bylo:** %s" % skrot(e["target_text"], 200))
    if e.get("new_text"):
        linie.append("- **Ma byc:** %s" % skrot(e["new_text"], 200))
    if e.get("comment"):
        linie.append("- **Komentarz w track changes (WIDZI DRUGA STRONA):** %s" % e["comment"])
    if e.get("rationale"):
        linie.append("- **Uzasadnienie (wewnetrzne):** %s" % e["rationale"])
    if e.get("walkaway"):
        linie.append("- **Walkaway:** %s" % e["walkaway"])
    if e.get("precedent"):
        linie.append("- **Precedens:** %s" % e["precedent"])
    linie.append("")
    return linie


def buduj_memo(edits, tytul):
    dzis = datetime.date.today().isoformat()
    grupy = {1: [], 2: [], 3: [], None: []}
    for e in edits:
        grupy[e.get("tier") if e.get("tier") in (1, 2, 3) else None].append(e)

    out = []
    out.append("# Memo negocjacyjne - %s" % tytul)
    out.append("")
    out.append("> %s" % NAGLOWEK_POUFNOSCI)
    out.append("")
    out.append("Data: %s | Pozycji: %d (tier 1: %d, tier 2: %d, tier 3: %d, bez kategorii: %d)"
               % (dzis, len(edits), len(grupy[1]), len(grupy[2]), len(grupy[3]), len(grupy[None])))
    out.append("")

    nr = 0
    for tier in (1, 2, 3):
        if not grupy[tier]:
            continue
        out.append("## %s" % TIERY[tier])
        out.append("")
        for e in grupy[tier]:
            nr += 1
            out.extend(pozycja_md(e, nr))
    if grupy[None]:
        out.append("## Bez kategorii - do klasyfikacji przez prawnika")
        out.append("")
        for e in grupy[None]:
            nr += 1
            out.extend(pozycja_md(e, nr))

    out.append("---")
    out.append("")
    out.append("Memo wygenerowane skryptem `memo_negocjacyjne.py` (redline-docx-pl).")
    out.append("To draft do rozmowy - negocjacje prowadzi czlowiek. Pola rationale /")
    out.append("walkaway / precedent nie moga trafic do dokumentu wymienianego z")
    out.append("kontrahentem; do adeu apply uzyj kopii z opcji --adeu.")
    out.append("")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser(description="Memo negocjacyjne z edits.json")
    ap.add_argument("edits", help="sciezka do edits.json")
    ap.add_argument("-o", "--output", help="plik memo Markdown (domyslnie stdout)")
    ap.add_argument("--tytul", default="redline", help="tytul memo (nazwa umowy)")
    ap.add_argument("--adeu", help="zapisz kopie edits.json tylko z polami adeu")
    args = ap.parse_args()

    try:
        edits = wczytaj_edits(args.edits)
    except (OSError, json.JSONDecodeError) as exc:
        print("BLAD IO/JSON: %s" % exc, file=sys.stderr)
        return 2
    except ValueError as exc:
        print("BLAD: %s" % exc, file=sys.stderr)
        return 1

    bledy = waliduj(edits)
    if bledy:
        for b in bledy:
            print("BLAD WALIDACJI: %s" % b, file=sys.stderr)
        return 1

    if args.adeu:
        czyste = [{k: e[k] for k in POLA_ADEU if k in e} for e in edits]
        with open(args.adeu, "w", encoding="utf-8") as f:
            json.dump(czyste, f, ensure_ascii=False, indent=2)
        print("Zapisano kopie dla adeu (bez pol memo): %s" % args.adeu)

    memo = buduj_memo(edits, args.tytul)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(memo)
        print("Zapisano memo: %s" % args.output)
    else:
        print(memo)
    return 0


if __name__ == "__main__":
    sys.exit(main())
