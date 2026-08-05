#!/usr/bin/env python3
"""Cosmetic rebrand pass for freshly imported upstream files - and its inverse check.

Why this is a SEPARATE script
-----------------------------
Because if renaming rides along with editing, the fork layer stops being
measurable: every file looks "modified" and nobody can tell a rename from work.
Keeping the rename mechanical and separate is what lets scripts/upstream-delta.py
report a REBRAND bucket distinct from MODIFIED. Ported from
criptogus/HermesOffice tools/rebrand-hermesoffice.py (Apache-2.0), which hardcodes
one project's pairs; ours reads them from .matematic/upstreams.json so the
manifest stays the single source of truth for what each adoption renames.

Two directions, one pair list:
    --apply <dir>   rewrite a STAGED upstream import before it enters the repo
    --check         scan what we already ship for upstream names that leaked in

`--check` is the "rebrand sujo?" question from the original. It is a hygiene
signal, not a licence risk, so it is a WARNING inside the pre-release gate
(upstream-delta.py imports leaks() from here) and exit 1 only when run alone.

Substring safety: our pairs are things like humanizer -> humanizer-pl, where the
source token lives inside its own replacement. A naive search reports every
correctly-renamed file as a leak, so replacements are masked out before the
search runs. Getting this wrong makes the check useless by drowning it.

    python scripts/rebrand.py --id blader-humanizer --check
    python scripts/rebrand.py --id blader-humanizer --apply ../staged-import
    python scripts/rebrand.py --id blader-humanizer --apply ../staged-import --dry-run

Stdlib only, ASCII-safe output, no network.
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, ".matematic", "upstreams.json")

TEXT_EXT = {".md", ".txt", ".json", ".yaml", ".yml", ".py", ".js", ".mjs", ".ts",
            ".html", ".css", ".svg", ".toml", ".cff", ".sh", ".ps1"}

# Never rewritten: the attribution must keep naming the original project, which
# is the whole point of carrying it.
PROTECTED = {"LICENSE", "LICENSE.txt", "LICENSE.md", "NOTICE", "NOTICE.txt",
             "package-lock.json", "THIRD_PARTY_INSPIRATIONS.md"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "out"}

_SENTINEL = "\x00%d\x00"


def load_upstream(uid):
    with open(MANIFEST, encoding="utf-8") as fh:
        cfg = json.load(fh)
    for up in cfg.get("upstreams", []):
        if up["id"] == uid:
            return cfg, up
    raise SystemExit("unknown upstream id '%s' in %s" % (uid, MANIFEST))


def apply_pairs(txt, pairs):
    for src, dst in pairs:
        txt = txt.replace(src, dst)
    return txt


def leaks(txt, pairs, keep=()):
    """Upstream tokens still present after the rename, ignoring correct results.

    Two kinds of legitimate occurrence are masked before the search:

    1. The replacement itself, so `humanizer-pl` never registers as a stray
       `humanizer`. Longest destination first, or a shorter one eats a longer
       one's prefix and the mask leaks by itself.
    2. `keep` - the credit tokens. Measured on humanizer-pl 2026-08-05: all five
       hits were the required MIT notice ("Polska adaptacja blader/humanizer").
       A check that flags the attribution pushes whoever is clearing warnings to
       delete the notice, which is the exact defect the attribution gate exists
       to prevent. Cosmetics must never argue with licensing.

    What survives the masks must then be a STANDALONE token to count. Our own
    sibling names extend the upstream one (humanizer -> humanizer-pl and
    humanizer-en, which the PL skill cross-references), so a bare substring
    search reports the twin link as a leak. Known edge: a genuine leak that
    happens to sit inside a longer word goes unseen - the cheaper miss.
    """
    masked = txt
    for tok in sorted([k for k in keep if k], key=len, reverse=True):
        masked = masked.replace(tok, "\x00keep\x00")
    ordered = sorted(range(len(pairs)), key=lambda i: -len(pairs[i][1]))
    for i in ordered:
        masked = masked.replace(pairs[i][1], _SENTINEL % i)
    return sorted({src for src, _dst in pairs
                   if src and re.search(r"(?<![\w-])%s(?![\w-])" % re.escape(src), masked)})


def walk_files(root):
    for base, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in sorted(files):
            yield os.path.join(base, f)


def read(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    return raw.decode("utf-8", errors="replace").replace("\r\n", "\n")


def cmd_apply(up, target, dry):
    pairs = [tuple(p) for p in up.get("rebrand", [])]
    if not pairs:
        print("upstream '%s' declares no rebrand pairs - nothing to do" % up["id"])
        return 0
    target = os.path.abspath(target)
    if not os.path.isdir(target):
        raise SystemExit("not a directory: %s" % target)
    if os.path.commonpath([target, ROOT]) == ROOT:
        # Rewriting the repo in place would turn a cosmetic pass into an
        # unreviewable mass edit. Staged imports only.
        raise SystemExit("refusing to rewrite inside the repo: %s" % target)

    changed = renamed = 0
    for path in walk_files(target):
        name = os.path.basename(path)
        if name in PROTECTED or os.path.splitext(name)[1].lower() not in TEXT_EXT:
            continue
        txt = read(path)
        new = apply_pairs(txt, pairs)
        if new != txt:
            changed += 1
            print("  content  %s" % os.path.relpath(path, target).replace("\\", "/"))
            if not dry:
                with open(path, "w", encoding="utf-8", newline="\n") as fh:
                    fh.write(new)

    for path in sorted(walk_files(target), key=len, reverse=True):
        name = os.path.basename(path)
        if name in PROTECTED:
            continue
        new_name = apply_pairs(name, pairs)
        if new_name != name:
            renamed += 1
            print("  rename   %s -> %s" % (name, new_name))
            if not dry:
                os.rename(path, os.path.join(os.path.dirname(path), new_name))

    print()
    print("%s%d files rewritten, %d renamed" % ("DRY RUN: " if dry else "", changed, renamed))
    return 0


def cmd_check(up):
    pairs = [tuple(p) for p in up.get("rebrand", [])]
    if not pairs:
        print("upstream '%s' declares no rebrand pairs - nothing to check" % up["id"])
        return 0
    targets = []
    for entry in up.get("map", []):
        p = os.path.join(ROOT, entry["ours"])
        if os.path.isdir(p):
            targets.extend(walk_files(p))
        elif os.path.isfile(p):
            targets.append(p)
    keep = list(up.get("credit_tokens") or []) + [up.get("repo") or "", up.get("slug") or ""]
    found = []
    for path in targets:
        if os.path.basename(path) in PROTECTED:
            continue
        if os.path.splitext(path)[1].lower() not in TEXT_EXT:
            continue
        for tok in leaks(read(path), pairs, keep=keep):
            found.append((os.path.relpath(path, ROOT).replace("\\", "/"), tok))
    print("checked %d files mapped from %s" % (len(targets), up["id"]))
    for path, tok in found:
        print("  ! %s: upstream name '%s' still present" % (path, tok))
    print("RESULT:", "CLEAN" if not found else "LEAKS (%d)" % len(found))
    return 0 if not found else 1


def main():
    ap = argparse.ArgumentParser(description="Cosmetic rebrand pass, kept out of the substantive diff.")
    ap.add_argument("--id", required=True, help="upstream id from .matematic/upstreams.json")
    ap.add_argument("--apply", metavar="DIR", help="rewrite a staged import directory (outside the repo)")
    ap.add_argument("--check", action="store_true", help="scan shipped files for leaked upstream names")
    ap.add_argument("--dry-run", action="store_true", help="with --apply: show, do not write")
    args = ap.parse_args()

    _cfg, up = load_upstream(args.id)
    if args.apply:
        sys.exit(cmd_apply(up, args.apply, args.dry_run))
    sys.exit(cmd_check(up))


if __name__ == "__main__":
    main()
