# -*- coding: utf-8 -*-
"""Wspolne reguly wtyczki - jeden tekst w <plugin>/SHARED-RULES.md, ta sama kopia na koncu
kazdego <plugin>/skills/*/SKILL.md (miedzy znacznikami).

Geneza (06.10.2026): CLAUDE.md w katalogu wtyczki NIE laduje sie po instalacji (walidator
katalogu Claude i `claude plugin validate`: "CLAUDE.md at the plugin root is not loaded").
"Siatka bezpieczenstwa" wtyczki nie docierala wiec do nikogo - ani przy instalacji calej
wtyczki, ani w pojedynczym zipie z Boutique. Kopia w kazdym skillu dociera zawsze.

Trojstan:
  OK       - kazdy skill wtyczki z SHARED-RULES.md ma blok identyczny ze zrodlem
  UWAGI    - wtyczka nadal ma CLAUDE.md w korzeniu (reguly nie docieraja) - do migracji
  BLOKADA  - brak bloku, blok rozjechany ze zrodlem, wtyczka z SHARED-RULES.md bez skilli,
             zero wtyczek do zmierzenia (pusta lista = BLOKADA)

Uzycie:
  python scripts/shared-rules-sync.py           # bramka
  python scripts/shared-rules-sync.py --write   # wklej/odswiez blok we wszystkich skillach
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
BEGIN = "<!-- shared-rules:begin (wygenerowane z ../../SHARED-RULES.md przez scripts/shared-rules-sync.py - nie edytuj tutaj) -->"
END = "<!-- shared-rules:end -->"
BLOK = re.compile(r"\n*" + re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n*", re.S)


def norm(t):
    return t.replace("\r\n", "\n")


def main():
    write = "--write" in sys.argv[1:]
    ok, uwagi, blokady = [], [], []
    wtyczki = sorted(p for p in ROOT.iterdir() if (p / ".claude-plugin" / "plugin.json").exists())
    if not wtyczki:
        print("BLOKADA: zero wtyczek - nie ma czego mierzyc")
        return 1
    for w in wtyczki:
        src = w / "SHARED-RULES.md"
        if not src.exists():
            if (w / "CLAUDE.md").exists():
                uwagi.append(f"{w.name}: CLAUDE.md w korzeniu wtyczki nie laduje sie - reguly nie docieraja (do migracji)")
            continue
        tresc = norm(src.read_text(encoding="utf-8")).strip()
        blok = f"{BEGIN}\n{tresc}\n{END}"
        skille = sorted(w.glob("skills/*/SKILL.md"))
        if not skille:
            blokady.append(f"{w.name}: SHARED-RULES.md jest, ale zero skilli")
            continue
        for s in skille:
            raw = s.read_bytes().decode("utf-8")
            crlf = "\r\n" in raw
            t = norm(raw)
            znalezione = BLOK.findall(t)
            if write:
                t2 = BLOK.sub("\n", t).rstrip("\n") + "\n\n" + blok + "\n"
                if t2 != t:
                    s.write_bytes((t2.replace("\n", "\r\n") if crlf else t2).encode("utf-8"))
                    t = t2
                    znalezione = BLOK.findall(t)
            nazwa = f"{w.name}/{s.parent.name}"
            if len(znalezione) != 1:
                blokady.append(f"{nazwa}: blokow regul {len(znalezione)} (oczekiwany 1)")
            elif znalezione[0].strip() != blok:
                blokady.append(f"{nazwa}: blok rozjechany ze zrodlem (napraw: --write)")
            else:
                ok.append(nazwa)
    for l in uwagi:
        print("  UWAGI   " + l)
    for l in blokady:
        print("  BLOKADA " + l)
    stan = "BLOKADA" if blokady else ("UWAGI" if uwagi else "OK")
    print(f"shared-rules: {stan} - skille OK {len(ok)}, UWAGI {len(uwagi)}, BLOKADA {len(blokady)}")
    return 1 if blokady else 0


if __name__ == "__main__":
    sys.exit(main())
