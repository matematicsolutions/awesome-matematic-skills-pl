#!/usr/bin/env python3
"""Legal-accuracy gate: statutory-unit coverage for changed skills.

Born 2026-08-07, the day an external reviewer (codex on a mike-workflows PR)
flagged 7 legal-accuracy defects that our form/style gate had passed - and all
7 lived in the source skills of this repo. Root class: a legal claim written
unconditionally when the law is conditional, or a statutory field list
silently truncated. The style gate never looked at claims per statutory unit.

What this gate does (mechanical, per the tier doctrine in preflight.py):
  1. Finds skills whose SKILL.md changed against a base (last tag, else
     merge-base with origin/main, else HEAD~1; override with --base).
  2. Extracts every statutory-reference unit from the CHANGED LINES of each
     file (art./Art./Article/ust./§/lit./Article-number patterns, EN + PL,
     plus named guidelines: EDPB/EROD/WP###).
  3. Requires reviews/legal-accuracy.md to hold a section for that skill
     covering EVERY extracted unit. Coverage is reported with the full
     denominator (n/m and the missing list) - never a bare "ok".

Goodhart line (why coverage blocks but truth cannot): "unit appears in the
ledger" is a structural fact a throwaway entry CAN satisfy - paste the list,
write "ok" everywhere. This gate cannot verify the verdicts; it exists to
make the OMISSION visible, because the 2026-08-07 defects were omissions
(no one had listed the units, so no one had checked them). The verdicts
themselves are the human/adversarial-review layer (adversarial-legal-review
skill); fabricating them is lying to a register, which no mechanical gate
fixes. Pairing rule satisfied: this gate measures the denominator; the
review skill supplies the judgement.

Run:  python scripts/legal-accuracy-gate.py [--base REF] [--gate]
Exit 0 = covered (or nothing legal changed). Exit 1 = uncovered units listed.
Stdlib only, ASCII-safe output, no network.
"""
import argparse
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "reviews", "legal-accuracy.md")

# Statutory-unit patterns, EN + PL. Conservative on purpose: a missed unit is
# a silent gap, an over-matched unit is one extra ledger line - err wide.
UNIT_RES = [
    # art. 30(2)(a) / Art. 30 ust. 2 lit. a / Article 15(1)(g) / art. 101[3]
    re.compile(r"\b[Aa]rt(?:icle|\.)\s*\d+[a-z]?"
               r"(?:\s*\[\d+\])?"
               r"(?:\(\d+[a-z]?\)|\s+ust\.\s*\d+[a-z]?)?"
               r"(?:\(\d*[a-z]\)|\s+lit\.\s*[a-z](?:-[a-z])?)?"),
    # bare paragraph signs: § 3 ust. 2, § 134
    re.compile(r"§\s*\d+[a-z]?(?:\s+ust\.\s*\d+)?"),
    # named guidance that carries legal weight
    re.compile(r"\b(?:EDPB|EROD)\s+(?:Guidelines|Wytyczn\w+)\s+\d+/\d{4}", re.I),
    re.compile(r"\bWytyczn\w+\s+(?:EROD|EDPB)\s+\d+/\d{4}", re.I),
    re.compile(r"\bWP\s?\d{3}\b"),
    # EU acts by number: Regulation (EU) 2016/679, Directive 2019/790
    re.compile(r"\b(?:Regulation|Directive|rozporządzenie|dyrektywa)\s+\((?:EU|EC|WE|EWG|EEC)\)\s*(?:No\s*)?\d+/\d+", re.I),
]


def norm(u):
    """Normalise for comparison: collapse whitespace, casefold - so
    'Art. 30(2)(a)' == 'art. 30(2)(a)' but the content must match exactly."""
    return " ".join(u.split()).casefold()


def sh(*args):
    return subprocess.run(["git", "-C", ROOT] + list(args),
                          capture_output=True, text=True)


def pick_base(explicit):
    """Default base = merge-base with origin/main: the gate checks what you
    are ABOUT TO SHIP (local commits + working tree), not repo history.
    History already on origin/main is grandfathered - retro-covering dozens
    of old skills would only breed pasted verdicts (the Goodhart line).
    Tags are the fallback for a repo without a remote."""
    if explicit:
        return explicit
    r = sh("merge-base", "HEAD", "origin/main")
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip()
    r = sh("describe", "--tags", "--abbrev=0")
    if r.returncode == 0 and r.stdout.strip():
        return r.stdout.strip()
    return "HEAD~1"


def changed_skill_files(base):
    r = sh("diff", "--name-only", base, "--", "*SKILL.md")
    if r.returncode != 0:
        print(f"  ! git diff against '{base}' failed: {r.stderr.strip()}")
        return []
    return [f for f in r.stdout.splitlines() if f.endswith("SKILL.md")]


def added_lines(base, path):
    r = sh("diff", base, "--", path)
    return [ln[1:] for ln in r.stdout.splitlines()
            if ln.startswith("+") and not ln.startswith("+++")]


def extract_units(lines):
    units = {}
    for ln in lines:
        for rx in UNIT_RES:
            for m in rx.finditer(ln):
                u = m.group(0).rstrip(".,;: ")
                units[norm(u)] = u
    return units  # norm -> display form


def ledger_sections():
    """Parse reviews/legal-accuracy.md into {skill-name: section-text}."""
    if not os.path.isfile(LEDGER):
        return None
    txt = open(LEDGER, encoding="utf-8", errors="replace").read()
    sections = {}
    cur = None
    for ln in txt.splitlines():
        m = re.match(r"##\s+([\w-]+)", ln)
        if m:
            cur = m.group(1)
            sections.setdefault(cur, [])
        elif cur:
            sections[cur].append(ln)
    return {k: "\n".join(v) for k, v in sections.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", help="git ref to diff against (default: last tag, else merge-base origin/main, else HEAD~1)")
    ap.add_argument("--gate", action="store_true", help="exit 1 on uncovered units (default behaviour; kept for symmetry with sibling gates)")
    args = ap.parse_args()

    base = pick_base(args.base)
    files = changed_skill_files(base)
    print(f"legal-accuracy-gate  base: {base}  changed SKILL.md: {len(files)}")

    if not files:
        print("RESULT: PASS (no skill content changed)")
        return 0

    sections = ledger_sections()
    problems = []
    total_units = 0

    for f in sorted(files):
        skill = os.path.basename(os.path.dirname(f))
        units = extract_units(added_lines(base, f))
        total_units += len(units)
        if not units:
            print(f"  [{skill}] 0 statutory units in changed lines - nothing to cover")
            continue
        if sections is None or sections.get(skill) is None:
            what = ("reviews/legal-accuracy.md does not exist" if sections is None
                    else f"no '## {skill}' section in the ledger")
            problems.append(f"{skill}: {len(units)} unit(s) changed but {what}")
            print(f"  [{skill}] units: {len(units)}  ledger section: MISSING")
            for u in sorted(units.values()):
                print(f"      to cover: {u}")
            continue
        sec = sections[skill]
        sec_norm = norm(sec)
        missing = [disp for key, disp in sorted(units.items()) if key not in sec_norm]
        covered = len(units) - len(missing)
        print(f"  [{skill}] coverage: {covered}/{len(units)}")
        for u in missing:
            print(f"      uncovered: {u}")
        if missing:
            problems.append(f"{skill}: {len(missing)}/{len(units)} unit(s) uncovered in the ledger")

    print()
    print(f"UNITS (denominator): {total_units}")
    print(f"BLOCKING: {len(problems)}")
    for p in problems:
        print("  X " + p)
    print("RESULT:", "PASS" if not problems else "FAIL")
    print("Note: coverage != correctness. The ledger verdicts are the "
          "adversarial-review layer; this gate only proves no unit was skipped.")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
