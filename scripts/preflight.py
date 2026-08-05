#!/usr/bin/env python3
"""Pre-release gate for a MateMatic skills marketplace repo.

Mirrors the checks the Claude plugin directory review pipeline runs on every
submission, plus two defects that shipped from this repo before this gate
existed (2026-08-02): a bundle without .claude-plugin/plugin.json, and
plugin.json versions lagging behind marketplace.json - which silently stops
installed users from ever receiving updates.

Run from the repo root:  python scripts/preflight.py
Exit 0 = releasable. Exit 1 = blocking defects listed on stdout.
Stdlib only, ASCII-safe output, no network.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORBIDDEN_IN_CLAUDE_PLUGIN = {"skills", "commands", "agents", "hooks"}
EM_DASH = "—"

problems = []
warnings = []


def check(cond, msg, soft=False):
    if not cond:
        (warnings if soft else problems).append(msg)


mp_path = os.path.join(ROOT, ".claude-plugin", "marketplace.json")
try:
    mp = json.load(open(mp_path, encoding="utf-8"))
except Exception as e:
    print(f"FATAL: marketplace.json does not parse: {e}")
    sys.exit(1)

print(f"marketplace: {mp.get('name')}  v{mp.get('version')}  bundles: {len(mp.get('plugins', []))}")

for p in mp.get("plugins", []):
    name = p.get("name", "?")
    src = p.get("source")
    if isinstance(src, str):
        pdir = os.path.join(ROOT, src.lstrip("./"))
    elif isinstance(src, dict) and src.get("path"):
        pdir = os.path.join(ROOT, src["path"].lstrip("./"))
    else:
        pdir = os.path.join(ROOT, name)

    if not os.path.isdir(pdir):
        problems.append(f"{name}: bundle directory missing -> {pdir}")
        continue

    # 1. plugin.json exists, parses, matches name; version in sync with marketplace
    man_p = os.path.join(pdir, ".claude-plugin", "plugin.json")
    if not os.path.isfile(man_p):
        problems.append(f"{name}: missing .claude-plugin/plugin.json (fails directory review)")
    else:
        try:
            man = json.load(open(man_p, encoding="utf-8"))
            check(man.get("name") == name,
                  f"{name}: plugin.json name '{man.get('name')}' != marketplace name")
            check(bool(man.get("description")), f"{name}: plugin.json has no description")
            mv, pv = p.get("version"), man.get("version")
            check(not (mv and pv and mv != pv),
                  f"{name}: VERSION DRIFT marketplace {mv} vs plugin.json {pv} "
                  f"- installed users only update on a plugin.json bump")
            desc = man.get("description", "")
            check(EM_DASH not in desc, f"{name}: em dash in plugin.json description (house style)")
        except Exception as e:
            problems.append(f"{name}: plugin.json does not parse ({e})")

    # 2. the documented "common mistake": component dirs inside .claude-plugin/
    cp = os.path.join(pdir, ".claude-plugin")
    if os.path.isdir(cp):
        bad = [d for d in os.listdir(cp)
               if d in FORBIDDEN_IN_CLAUDE_PLUGIN and os.path.isdir(os.path.join(cp, d))]
        check(not bad, f"{name}: {bad} inside .claude-plugin/ (must sit at bundle root)")

    # 3. every skill dir has SKILL.md with parseable frontmatter and a description
    sdir = os.path.join(pdir, "skills")
    nskills = 0
    if os.path.isdir(sdir):
        for d in sorted(os.listdir(sdir)):
            sk = os.path.join(sdir, d)
            if not os.path.isdir(sk):
                continue
            sm = os.path.join(sk, "SKILL.md")
            if not os.path.isfile(sm):
                problems.append(f"{name}/{d}: skill directory without SKILL.md")
                continue
            nskills += 1
            txt = open(sm, encoding="utf-8", errors="replace").read()
            if not txt.startswith("---") or txt.count("---") < 2:
                problems.append(f"{name}/{d}: SKILL.md has no frontmatter")
                continue
            fm = txt.split("---", 2)[1]
            m = re.search(r"^description:\s*(.+?)(?=^[\w-]+:\s|\Z)", fm, re.M | re.S)
            if not m:
                problems.append(f"{name}/{d}: SKILL.md frontmatter has no description")
                continue
            d_txt = " ".join(m.group(1).split())
            check(EM_DASH not in d_txt, f"{name}/{d}: em dash in description (house style)")
            # future-dated years in public copy (zero-future-dates rule)
            check(not re.search(r"\b20(2[7-9]|[3-9]\d)\b", d_txt),
                  f"{name}/{d}: future year in description", soft=True)
            # 4. links escaping the bundle break the "own directory" review criterion
            for link in re.findall(r"\]\(([^)]+)\)", txt):
                if link.startswith("../.."):
                    warnings.append(f"{name}/{d}: link escapes the bundle: {link}")
                    break
    print(f"  [{name}] skills: {nskills}")

# 5. repo-level README explains installation (review criterion)
rd = os.path.join(ROOT, "README.md")
if not os.path.isfile(rd):
    problems.append("repo: README.md missing")
elif "instal" not in open(rd, encoding="utf-8", errors="replace").read().lower():
    warnings.append("README.md does not mention installation")

# 6. attribution + licence gate. Kept as its own script so it can run alone
# against either marketplace, but folded in here so the pre-release gate stays
# the single thing you have to remember to run.
gate = os.path.join(ROOT, "scripts", "attribution-gate.py")
if os.path.isfile(gate):
    import subprocess
    r = subprocess.run([sys.executable, gate], capture_output=True, text=True)
    print()
    print((r.stdout or "").rstrip())
    if r.returncode != 0:
        problems.append("attribution-gate: blocking attribution/licence findings (listed above)")
else:
    warnings.append("scripts/attribution-gate.py missing - attribution not checked")

# 7. fork-layer meter. attribution-gate reads what a skill CLAIMS about its
# upstream; this measures the bytes and reports where claim and reality part
# company. Folded in for the same reason as step 6: one command to remember.
# Offline - it compares against pinned local snapshots and never fetches.
delta = os.path.join(ROOT, "scripts", "upstream-delta.py")
if os.path.isfile(delta):
    import subprocess
    r = subprocess.run([sys.executable, delta, "--gate"], capture_output=True, text=True)
    print()
    print((r.stdout or "").rstrip())
    if r.returncode != 0:
        problems.append("upstream-delta: blocking fork-layer findings (listed above)")
    # Roll the sub-gate's warnings into this summary. A final "WARNINGS: 0"
    # printed under a report that just listed three of them is the kind of
    # tidy-looking output people stop reading.
    n_soft = sum(1 for ln in (r.stdout or "").splitlines() if ln.startswith("  ! "))
    if n_soft:
        warnings.append("upstream-delta: %d fork-layer warning(s) listed above" % n_soft)
elif os.path.isfile(os.path.join(ROOT, ".matematic", "upstreams.json")):
    warnings.append("scripts/upstream-delta.py missing - fork layer not measured")

print()
print(f"BLOCKING: {len(problems)}")
for x in problems:
    print("  X " + x)
print(f"WARNINGS: {len(warnings)}")
for x in warnings:
    print("  ! " + x)
print("RESULT:", "PASS" if not problems else "FAIL")
sys.exit(0 if not problems else 1)
