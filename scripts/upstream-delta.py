#!/usr/bin/env python3
"""Fork-layer meter: how much of what we ship is ours, and how much is upstream.

Why this exists
---------------
Our kardynalna doktryna is "skladamy puzzle (MIT/Apache), nie wynajdujemy kola".
So we take somebody's repo, lay a MateMatic layer on top, upstream moves, and a
month later nobody can say which lines are ours. THIRD_PARTY_INSPIRATIONS.md
records the adoption in prose - snapshot date, licence, and a claimed RELATION
("PATTERN ONLY", "FORK z adaptacja", "ZALEZNOSC CLI"). Prose is a claim. This
script is the measurement, and the two are allowed to disagree exactly once:
here, in the report.

The claim that most needs a meter is "PATTERN ONLY". It is a legal statement -
for lawve-ai/awesome-legal-skills (CC BY-NC-ND curation, per-skill AGPL) it is
the whole reason we may ship at all. Nothing checked it until now.

Pattern ported from criptogus/HermesOffice tools/upstream-diff.sh (Apache-2.0):
soft-fork with no GitHub fork, manual upstream sync, and the fork's whole delta
classified by one script. That script classifies an in-repo git diff against
`upstream/main` because HermesOffice is one soft-forked app; our artifacts are
markdown skills gathered from several unrelated upstreams into two marketplaces,
so the walk is a manifest and pinned snapshots instead of a git remote. Kept from
the original: the classification-by-bucket shape, and the separation of cosmetic
rebranding into its own script (scripts/rebrand.py) so a rename never masquerades
as substantive work.

What the numbers mean - and what they cannot see
------------------------------------------------
text   - line-level similarity (difflib). Sees copied text. Near zero for a
         translation, so a Polish 1:1 copy of an English skill scores ~0.03.
struct - similarity of the heading skeleton (levels only, never the words).
         A translated fork keeps its shape, so this is the signal `text` cannot
         give. It is a HINT, never a blocker: it asks for human eyes.
Neither measures ideas. A taxonomy lifted wholesale and reworded scores clean
on both. This gate lowers the odds of a false attribution claim; it does not
certify one. Read `relation` mismatches as questions, not verdicts.

Measured on 2026-08-05 while building this: cloning lawvable/awesome-legal-skills
on Windows EXITS 0 with the directory tree in place and 2711 of its files never
written (MAX_PATH; git's own `status` reports the index, not the gap). A snapshot
that looks fine and is not is the failure mode this repo already calls kardynalna,
so `sync` verifies the checkout tree against the filesystem before it records a
pin, and unverified snapshots are reported UNMEASURED rather than compared.

Run from either repo root:
    python scripts/upstream-delta.py                 # measure (offline)
    python scripts/upstream-delta.py --id humanizer  # one upstream
    python scripts/upstream-delta.py --gate          # pre-release mode, exit 1 on blockers
    python scripts/upstream-delta.py --json          # machine-readable
    python scripts/upstream-delta.py sync            # NETWORK: refresh snapshots + pin
Exit 0 = releasable. Exit 1 = blocking findings on stdout.
Stdlib only, ASCII-safe output (PS 5.1 stdout is cp852). Network only in `sync`.
"""
import argparse
import difflib
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, ".matematic", "upstreams.json")

# Vocabulary is NOT this script's to invent. It is the canon WM set on 2026-08-05
# for the `attribution.relationship` field in SKILL.md, and scripts/attribution-gate.py
# already enforces it there. A third private vocabulary living in the manifest is
# how the humanizer defect became possible in the first place: two conventions for
# one fact, and nothing able to compare them.
#   vendored     - carried verbatim (or verbatim after a rebrand)
#   adaptation   - carried and reworked, translation included
#   pattern-only - the idea was taken, the text was not
#   clean-room   - written from zero, knowing the upstream exists
#   dependency   - invoked as a separate process; nothing carried
#   original     - no third-party source at all
# `dependency` and `original` carry nothing, so there is nothing to diff. Mapping an
# `original` skill anyway is legitimate and strict: it polices a no-source claim
# against the nearest upstream somebody might think it came from.
MEASURABLE = {"vendored", "adaptation", "pattern-only", "clean-room", "original"}
RELATIONS = MEASURABLE | {"dependency"}
# Anything carrying text. Below this line the claim is "we took no text", and the
# text number is what tests it.
CARRIES_TEXT = {"vendored", "adaptation"}
# Pre-canon manifests kept working rather than failing shut - but they say so.
LEGACY_RELATIONS = {"fork": "adaptation", "pattern": "pattern-only",
                    "cli": "dependency", "data": "dependency"}

# Defaults chosen from the only two adoptions we could measure on 2026-08-05.
# text 0.55: a rewrite-from-zero of a legal skill lands far below this even when
# both skills cover the same statute; a copy with edits lands far above.
# struct 0.90: heading skeletons drift fast under real editing, so a near-perfect
# match on shape with near-zero text is the translated-copy signature.
DEFAULT_THRESHOLDS = {"text": 0.55, "struct": 0.90}

# Never diffed: licence and notice files are SUPPOSED to be upstream verbatim.
# Flagging them as "not ours" would bury the real findings under noise.
VERBATIM_BY_DESIGN = {"LICENSE", "LICENSE.txt", "LICENSE.md", "NOTICE", "NOTICE.txt"}

_FOLD = {
    "ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n",
    "ó": "o", "ś": "s", "ź": "z", "ż": "z",
    "Ą": "A", "Ć": "C", "Ę": "E", "Ł": "L", "Ń": "N",
    "Ó": "O", "Ś": "S", "Ź": "Z", "Ż": "Z",
    "—": "-", "–": "-", "‘": "'", "’": "'",
    "“": '"', "”": '"',
}

HEADING_RE = re.compile(r"^(#{1,6})\s+\S")


def ascii_fold(s):
    """PS 5.1 stdout is cp852; fold to ASCII so findings stay readable."""
    return "".join(_FOLD.get(ch, ch if ord(ch) < 128 else "?") for ch in str(s))


def read_text(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    txt = raw.decode("utf-8", errors="replace")
    if txt.startswith("﻿"):
        txt = txt[1:]
    return txt.replace("\r\n", "\n").replace("\r", "\n")


def norm_lines(txt):
    """Trailing whitespace and trailing blank lines are not a fork delta."""
    lines = [ln.rstrip() for ln in txt.split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return lines


def heading_shape(lines):
    """Heading LEVELS only - never the words. Language-independent by design."""
    return [len(m.group(1)) for m in (HEADING_RE.match(ln) for ln in lines) if m]


def apply_rebrand(txt, pairs):
    for src, dst in pairs:
        txt = txt.replace(src, dst)
    return txt


def ratio(a, b):
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b, autojunk=False).ratio()


def line_delta(up_lines, our_lines):
    """(added, removed) counted the way a reviewer would read the diff."""
    sm = difflib.SequenceMatcher(None, up_lines, our_lines, autojunk=False)
    added = removed = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("replace", "insert"):
            added += j2 - j1
        if tag in ("replace", "delete"):
            removed += i2 - i1
    return added, removed


def git(args, cwd=None, check=True):
    r = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True,
                       errors="replace")
    if check and r.returncode != 0:
        raise RuntimeError((r.stderr or r.stdout or "git failed").strip())
    return r


# ---------------------------------------------------------------- manifest ---

def load_manifest(path=MANIFEST):
    if not os.path.isfile(path):
        return None
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save_manifest(cfg, path=MANIFEST):
    """Rewritten only by `sync`, and only to record a verified pin."""
    body = json.dumps(cfg, indent=2, ensure_ascii=False) + "\n"
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)


def snapshot_root(cfg):
    env = os.environ.get("MATEMATIC_UPSTREAM_SNAPSHOTS")
    raw = env or cfg.get("snapshot_root") or "~/Projects/_ref/upstream-snapshots"
    return os.path.abspath(os.path.expanduser(raw))


def snapshot_dir(cfg, up):
    return os.path.join(snapshot_root(cfg), up["id"])


# ------------------------------------------------------------------- sync ----

def tree_gap(sdir):
    """Files git believes it checked out that are not on disk.

    This is the check that catches the Windows MAX_PATH truncation, and it is
    deliberately NOT `git status`: after a failed checkout git reports its index,
    which said "deleted" for 2718 paths that were, by then, present. Compare the
    committed tree against the filesystem and the answer stops being clever.
    """
    listing = git(["ls-tree", "-r", "HEAD", "--name-only", "-z"], cwd=sdir).stdout
    tracked = [p for p in listing.split("\0") if p]
    missing = [p for p in tracked if not os.path.exists(os.path.join(sdir, p))]
    return tracked, missing


def sync_one(cfg, up, verbose=True):
    """Clone or refresh one snapshot, verify it, then pin it. Touches network."""
    sdir = snapshot_dir(cfg, up)
    ref = up.get("ref") or "main"
    os.makedirs(os.path.dirname(sdir), exist_ok=True)
    # core.longpaths: without it Windows silently drops every path over MAX_PATH
    # and the clone still exits 0.
    common = ["-c", "core.longpaths=true"]
    try:
        if os.path.isdir(os.path.join(sdir, ".git")):
            git(common + ["fetch", "--depth", "1", "origin", ref], cwd=sdir)
            git(common + ["checkout", "--force", "FETCH_HEAD"], cwd=sdir)
        else:
            git(common + ["clone", "--depth", "1", "--branch", ref,
                          up["repo"], sdir])
    except RuntimeError as e:
        return {"id": up["id"], "ok": False, "error": ascii_fold(e)}

    tracked, missing = tree_gap(sdir)
    commit = git(["rev-parse", "HEAD"], cwd=sdir).stdout.strip()
    rec = {"id": up["id"], "ok": not missing, "commit": commit,
           "files": len(tracked), "missing": len(missing)}
    if missing:
        # No pin. A pinned-but-partial snapshot is a measurement that lies.
        rec["sample"] = [ascii_fold(p) for p in missing[:3]]
        return rec
    up["pin"] = {"commit": commit, "ref": ref, "files": len(tracked),
                 "synced": cfg.get("_today") or up.get("pin", {}).get("synced")}
    if verbose:
        print("  synced %-24s %s  (%d files)" % (up["id"], commit[:12], len(tracked)))
    return rec


# ---------------------------------------------------------------- measure ----

def snapshot_state(cfg, up):
    """(state, detail) - never guess. UNMEASURED is a first-class answer."""
    sdir = snapshot_dir(cfg, up)
    if not os.path.isdir(os.path.join(sdir, ".git")):
        return "absent", "no snapshot at %s" % ascii_fold(sdir)
    try:
        tracked, missing = tree_gap(sdir)
    except RuntimeError as e:
        return "broken", ascii_fold(e)
    if missing:
        return "partial", "%d of %d files missing on disk" % (len(missing), len(tracked))
    head = git(["rev-parse", "HEAD"], cwd=sdir).stdout.strip()
    pinned = (up.get("pin") or {}).get("commit")
    if pinned and pinned != head:
        return "drifted", "snapshot %s != pin %s" % (head[:12], pinned[:12])
    return "ok", head[:12]


def expand_pairs(up, sdir):
    """Manifest entries -> concrete (upstream_path, our_path, relation) triples.

    A map entry is either file->file or dir->dir. Directory form is what makes
    "what did we add" and "what did we drop" answerable; file form keeps the
    common single-SKILL.md adoption from needing ceremony.

    The `explicit` flag separates the two, and it changes severity: a file the
    directory walk found missing on our side is a DROP (a choice), while a
    hand-written mapping pointing at a path we do not have is rot (a mistake).
    """
    default_rel = up.get("relation", "fork")
    out = []
    for entry in up.get("map", []):
        rel = entry.get("relation", default_rel)
        up_rel, our_rel = entry["upstream"], entry["ours"]
        up_abs, our_abs = os.path.join(sdir, up_rel), os.path.join(ROOT, our_rel)
        if os.path.isdir(up_abs) or os.path.isdir(our_abs):
            seen = set()
            for base, _d, files in os.walk(up_abs):
                for f in sorted(files):
                    r = os.path.relpath(os.path.join(base, f), up_abs).replace("\\", "/")
                    seen.add(r)
                    out.append((up_rel + "/" + r, our_rel + "/" + r, rel, False))
            for base, _d, files in os.walk(our_abs):
                for f in sorted(files):
                    r = os.path.relpath(os.path.join(base, f), our_abs).replace("\\", "/")
                    if r not in seen:
                        out.append((up_rel + "/" + r, our_rel + "/" + r, rel, False))
        else:
            out.append((up_rel, our_rel, rel, True))
    return out


def classify(up_abs, our_abs, rebrand):
    """One file pair -> bucket + the two numbers behind it."""
    has_up, has_our = os.path.isfile(up_abs), os.path.isfile(our_abs)
    if has_up and not has_our:
        return {"bucket": "DROPPED", "text": None, "struct": None,
                "added": 0, "removed": len(norm_lines(read_text(up_abs))), "delta": 0}
    if has_our and not has_up:
        n = len(norm_lines(read_text(our_abs)))
        return {"bucket": "OURS", "text": None, "struct": None,
                "added": n, "removed": 0, "delta": n}
    if not has_up and not has_our:
        return {"bucket": "MISSING", "text": None, "struct": None,
                "added": 0, "removed": 0, "delta": 0}

    up_txt, our_txt = read_text(up_abs), read_text(our_abs)
    up_lines, our_lines = norm_lines(up_txt), norm_lines(our_txt)

    if up_lines == our_lines:
        bucket = "IDENTICAL"
    elif norm_lines(apply_rebrand(up_txt, rebrand)) == our_lines:
        # Cosmetic-only. The whole point of keeping rebranding in its own script
        # is that this bucket stays distinguishable from real work.
        bucket = "REBRAND"
    else:
        bucket = "MODIFIED"

    added, removed = line_delta(norm_lines(apply_rebrand(up_txt, rebrand)), our_lines)
    up_shape, our_shape = heading_shape(up_lines), heading_shape(our_lines)
    return {
        "bucket": bucket,
        "text": round(ratio(norm_lines(apply_rebrand(up_txt, rebrand)), our_lines), 3),
        "struct": round(ratio(up_shape, our_shape), 3) if (up_shape and our_shape) else None,
        "added": added, "removed": removed,
        "delta": added if bucket != "IDENTICAL" else 0,
        "total": len(our_lines),
    }


def owning_skill_text(our_rel):
    """Nearest SKILL.md at or above a mapped path - where credit must live."""
    p = os.path.join(ROOT, our_rel)
    d = p if os.path.isdir(p) else os.path.dirname(p)
    while d and os.path.commonpath([os.path.abspath(d), ROOT]) == ROOT:
        cand = os.path.join(d, "SKILL.md")
        if os.path.isfile(cand):
            return read_text(cand)
        if os.path.abspath(d) == ROOT:
            break
        d = os.path.dirname(d)
    return None


def rebrand_module():
    """scripts/rebrand.py owns rebrand semantics; borrow its leak scan.

    Imported rather than reimplemented: two copies of the substring-masking rule
    would drift, and the drifted copy would be the one that stops finding leaks.
    """
    import importlib.util
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rebrand.py")
    if not os.path.isfile(p):
        return None
    spec = importlib.util.spec_from_file_location("matematic_rebrand", p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SK_REL_RE = re.compile(r"^\s*-?\s*relationship:\s*(.+?)\s*$", re.M)
SK_SRC_RE = re.compile(r"^\s*-?\s*source:\s*(.+?)\s*$", re.M)


def declared(text):
    """What the SKILL.md itself says: (relationships, sources).

    Read from the same `attribution:` block attribution-gate enforces, so the two
    gates argue about one fact instead of each inventing its own.
    """
    if not text:
        return set(), set()
    fm = text.split("---", 2)[1] if text.startswith("---") and text.count("---") >= 2 else text
    rels = {m.strip().lower() for m in SK_REL_RE.findall(fm)}
    srcs = {m.strip().strip('"\'').lower() for m in SK_SRC_RE.findall(fm)}
    return rels, srcs


def credits(text, up):
    if not text:
        return False
    tokens = up.get("credit_tokens") or [up.get("slug") or up["id"]]
    low = text.lower()
    return any(t.lower() in low for t in tokens)


# ----------------------------------------------------------------- report ----

def measure(cfg, only=None):
    results = []
    for up in cfg.get("upstreams", []):
        if only and up["id"] != only:
            continue
        raw = (up.get("relation") or "adaptation").strip().lower()
        norm = LEGACY_RELATIONS.get(raw, raw)
        rec = {"id": up["id"], "slug": up.get("slug"), "license": up.get("license"),
               "relation": norm, "pairs": [], "problems": [], "warnings": []}
        if raw in LEGACY_RELATIONS:
            rec["warnings"].append(
                "%s: manifest uses pre-canon relation '%s' - the canon is '%s' "
                "(same vocabulary as attribution.relationship in SKILL.md)"
                % (up["id"], raw, norm))
        elif norm not in RELATIONS:
            rec["warnings"].append("%s: unknown relation '%s'" % (up["id"], raw))
        if norm == "dependency":
            rec["state"] = "n/a"
            rec["detail"] = "relation 'dependency' - we call it, we do not carry it"
            results.append(rec)
            continue

        if not up.get("map"):
            # A measurable relation with nothing to compare is a GAP, not a pass.
            # Counting it as measured is how coverage becomes a comfortable lie.
            rec["state"] = "no-surface"
            rec["detail"] = up.get("note") or "no file pairs declared in 'map'"
            rec["warnings"].append(
                "%s: relation '%s' declared but no file pairs to compare - "
                "claim is not machine-checkable" % (up["id"], rec["relation"]))
            results.append(rec)
            continue

        state, detail = snapshot_state(cfg, up)
        rec["state"], rec["detail"] = state, detail
        if state != "ok":
            # Loud, and never mistaken for a pass. `partial` is the Windows
            # MAX_PATH case: comparing against it would report our own files as
            # additions and quietly overstate the delta.
            rec["warnings"].append(
                "%s: UNMEASURED (%s) - %s" % (up["id"], state, detail))
            results.append(rec)
            continue

        sdir = snapshot_dir(cfg, up)
        rebrand = [tuple(p) for p in up.get("rebrand", [])]
        thresholds = dict(DEFAULT_THRESHOLDS, **(up.get("thresholds") or {}))
        declared_dropped = set(up.get("dropped", []))

        for up_rel, our_rel, rel, explicit in expand_pairs(up, sdir):
            rel_raw = (rel or "").strip().lower()
            rel = LEGACY_RELATIONS.get(rel_raw, rel_raw)
            if rel_raw in LEGACY_RELATIONS:
                # Silent normalisation here would let the old vocabulary live on
                # in map entries - the drift this whole file exists to stop.
                rec["warnings"].append(
                    "%s: map entry for %s uses pre-canon relation '%s' - the canon "
                    "is '%s'" % (up["id"], ascii_fold(our_rel), rel_raw, rel))
            if os.path.basename(our_rel) in VERBATIM_BY_DESIGN:
                continue
            c = classify(os.path.join(sdir, up_rel), os.path.join(ROOT, our_rel), rebrand)
            c.update({"upstream": up_rel, "ours": our_rel, "relation": rel})
            rec["pairs"].append(c)

            if c["bucket"] == "MISSING":
                rec["problems"].append(
                    "%s: mapping points at nothing on either side (%s -> %s) "
                    "- manifest rot" % (up["id"], ascii_fold(up_rel), ascii_fold(our_rel)))
                continue

            if c["bucket"] == "DROPPED" and explicit:
                rec["problems"].append(
                    "%s: mapping declares %s -> %s but we carry no such file "
                    "- manifest rot (a drop belongs in 'dropped', not in 'map')"
                    % (up["id"], ascii_fold(up_rel), ascii_fold(our_rel)))
                continue

            if c["bucket"] == "DROPPED" and up_rel not in declared_dropped:
                rec["warnings"].append(
                    "%s: upstream file not carried and not declared in 'dropped': %s"
                    % (up["id"], ascii_fold(up_rel)))

            if rel not in CARRIES_TEXT and c["text"] is not None:
                if c["text"] >= thresholds["text"]:
                    rec["problems"].append(
                        "%s: declared '%s' (no text taken) but %s matches upstream "
                        "text at %.2f (threshold %.2f) - the claim is false as written"
                        % (up["id"], rel, ascii_fold(our_rel), c["text"], thresholds["text"]))
                elif c["struct"] is not None and c["struct"] >= thresholds["struct"]:
                    rec["warnings"].append(
                        "%s: declared '%s', text is clean (%.2f) but the heading "
                        "skeleton matches at %.2f - possible translated copy, "
                        "human eyes: %s"
                        % (up["id"], rel, c["text"], c["struct"], ascii_fold(our_rel)))

            if rel in CARRIES_TEXT and c["bucket"] in ("IDENTICAL", "REBRAND"):
                if not credits(owning_skill_text(our_rel), up):
                    rec["problems"].append(
                        "%s: %s is carried verbatim%s and the owning SKILL.md "
                        "credits no upstream - redistribution without notice"
                        % (up["id"], ascii_fold(our_rel),
                           " (rebrand only)" if c["bucket"] == "REBRAND" else ""))

            if (rel in CARRIES_TEXT and c["bucket"] == "MODIFIED"
                    and c["text"] is not None and c["text"] < 0.05
                    and (c["struct"] is None or c["struct"] < 0.50)):
                rec["warnings"].append(
                    "%s: declared '%s' but %s shares almost nothing with upstream "
                    "(text %.2f) - either it was written from zero (then it is "
                    "'clean-room') or the mapping is stale"
                    % (up["id"], rel, ascii_fold(our_rel), c["text"]))

            # Two of our own declarations about one fact: the manifest entry and
            # the skill's own attribution block. When they disagree, the direction
            # decides severity - a skill claiming LESS provenance than the manifest
            # records is the understatement that costs a licence notice.
            sk_txt = owning_skill_text(our_rel)
            sk_rels, sk_srcs = declared(sk_txt)
            if sk_rels and rel not in sk_rels:
                understated = rel in CARRIES_TEXT and not (sk_rels & CARRIES_TEXT)
                msg = ("%s: manifest says '%s' for %s, SKILL.md declares '%s'"
                       % (up["id"], rel, ascii_fold(our_rel), "/".join(sorted(sk_rels))))
                if understated:
                    rec["problems"].append(
                        msg + " - the skill claims less provenance than we carry")
                else:
                    rec["warnings"].append(msg + " - reconcile, one of them is stale")
            slug = (up.get("slug") or "").lower()
            if (rel in CARRIES_TEXT and slug and sk_srcs
                    and not any(slug in s2 for s2 in sk_srcs)):
                where = "%s: SKILL.md for %s names %s but not the upstream we carry (%s)" % (
                    up["id"], ascii_fold(our_rel),
                    ascii_fold("/".join(sorted(sk_srcs))), ascii_fold(slug))
                if c["text"] is not None and c["text"] >= 0.30:
                    rec["problems"].append(where + " - notice must name the source it came from")
                else:
                    rec["warnings"].append(where)

        # Cosmetics stay a warning: a leaked upstream name is untidy, not a
        # licence risk. It is checked HERE anyway, because a rule that lives
        # only in a separate script nobody remembers to run is not a rule.
        if rebrand:
            rb = rebrand_module()
            if rb is None:
                rec["warnings"].append(
                    "%s: scripts/rebrand.py missing - rebrand leaks not checked" % up["id"])
            else:
                keep = (list(up.get("credit_tokens") or [])
                        + [up.get("repo") or "", up.get("slug") or ""])
                for c in rec["pairs"]:
                    our_abs = os.path.join(ROOT, c["ours"])
                    if not os.path.isfile(our_abs):
                        continue
                    for tok in rb.leaks(read_text(our_abs), rebrand, keep=keep):
                        rec["warnings"].append(
                            "%s: upstream name '%s' still present in %s "
                            "(run: python scripts/rebrand.py --id %s --check)"
                            % (up["id"], ascii_fold(tok), ascii_fold(c["ours"]), up["id"]))

        results.append(rec)
    return results


def print_report(results, verbose=True):
    measured = [r for r in results if r.get("state") == "ok"]
    unmeasured = [r for r in results if r.get("state") not in ("ok", "n/a")]
    na = [r for r in results if r.get("state") == "n/a"]

    for rec in results:
        head = "[%-7s] %-22s %s" % (rec["relation"].upper(), rec["id"],
                                    rec.get("slug") or "")
        print(ascii_fold(head).rstrip())
        if rec.get("state") != "ok":
            print("    %s: %s" % (rec.get("state", "?"), ascii_fold(rec.get("detail", ""))))
            continue
        print("    snapshot %s   licence %s" % (rec["detail"], rec.get("license") or "?"))
        if verbose:
            for c in rec["pairs"]:
                t = "  -  " if c["text"] is None else "%5.2f" % c["text"]
                s = "  -  " if c["struct"] is None else "%5.2f" % c["struct"]
                print("      %-9s text %s  struct %s  +%-4d -%-4d  %s"
                      % (c["bucket"], t, s, c["added"], c["removed"],
                         ascii_fold(c["ours"])))
    print()

    pairs = [c for r in measured for c in r["pairs"]]
    buckets = {}
    for c in pairs:
        buckets[c["bucket"]] = buckets.get(c["bucket"], 0) + 1
    ours = sum(c["delta"] for c in pairs)
    total = sum(c.get("total", 0) or 0 for c in pairs)

    print("MEASURED:  %d of %d upstreams (%d unmeasured, %d not measurable by design)"
          % (len(measured), len(results), len(unmeasured), len(na)))
    if measured:
        print("SURFACE:   " + ", ".join("%d %s" % (v, k.lower())
                                        for k, v in sorted(buckets.items())) or "empty")
        print("OUR DELTA: %d of %d lines on the mapped surface are ours%s"
              % (ours, total, " (%d%%)" % round(100.0 * ours / total) if total else ""))
    if not measured and results:
        # The gate ran and proved nothing. Say it in the loudest place, because a
        # clean exit code on an empty measurement is how a gate stops working
        # without anyone noticing.
        print("NOTE:      nothing was measured - this run proves nothing. "
              "Refresh snapshots:  python scripts/upstream-delta.py sync")
    return measured, unmeasured


def main():
    ap = argparse.ArgumentParser(description="Measure the MateMatic layer on top of an upstream.")
    ap.add_argument("command", nargs="?", default="status", choices=["status", "sync"],
                    help="status = measure offline (default); sync = refresh snapshots (network)")
    ap.add_argument("--id", help="limit to one upstream id")
    ap.add_argument("--gate", action="store_true", help="pre-release mode: compact, exit 1 on blockers")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--today", help="date recorded in the pin on sync (YYYY-MM-DD)")
    # --root/--manifest exist so the gate itself can be exercised against a
    # throwaway tree. A blocker nobody has ever seen fire is a blocker nobody
    # knows still works.
    ap.add_argument("--root", help="repo root to measure (default: parent of this script)")
    ap.add_argument("--manifest", help="manifest path (default: <root>/.matematic/upstreams.json)")
    args = ap.parse_args()

    global ROOT, MANIFEST
    if args.root:
        ROOT = os.path.abspath(args.root)
        MANIFEST = os.path.join(ROOT, ".matematic", "upstreams.json")
    if args.manifest:
        MANIFEST = os.path.abspath(args.manifest)

    cfg = load_manifest(MANIFEST)
    if cfg is None:
        print("no .matematic/upstreams.json - no upstream adoption declared in this repo")
        sys.exit(0)

    if args.command == "sync":
        cfg["_today"] = args.today
        print("snapshots: %s" % ascii_fold(snapshot_root(cfg)))
        bad = []
        for up in cfg.get("upstreams", []):
            if args.id and up["id"] != args.id:
                continue
            if up.get("relation") in ("cli", "data"):
                continue
            r = sync_one(cfg, up)
            if not r["ok"]:
                bad.append(r)
                print("  FAILED %-24s %s" % (
                    r["id"], r.get("error") or "%d of %d files missing after checkout %s"
                    % (r["missing"], r["files"], r.get("sample", ""))))
        cfg.pop("_today", None)
        save_manifest(cfg, MANIFEST)
        print()
        print("RESULT:", "PASS" if not bad else "FAIL (unverified snapshots were not pinned)")
        sys.exit(0 if not bad else 1)

    results = measure(cfg, only=args.id)
    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=True))
        problems = [p for r in results for p in r["problems"]]
        sys.exit(0 if not problems else 1)

    measured, unmeasured = print_report(results, verbose=not args.gate)
    problems = [p for r in results for p in r["problems"]]
    warnings = [w for r in results for w in r["warnings"]]
    print()
    print("BLOCKING: %d" % len(problems))
    for x in problems:
        print("  X " + x)
    print("WARNINGS: %d" % len(warnings))
    for x in warnings:
        print("  ! " + x)
    print("RESULT:", "PASS" if not problems else "FAIL")
    sys.exit(0 if not problems else 1)


if __name__ == "__main__":
    main()
