#!/usr/bin/env python3
"""Attribution + license gate for MateMatic skills marketplace repos.

Why this exists
---------------
Our kardynalna doktryna is "skladamy puzzle (MIT/Apache), nie wynajdujemy kola".
We had the RULE but no MECHANICAL GATE, and on 2026-08-04 that cost us: the twin
skills humanizer-pl and humanizer-en drifted - PL credited "adaptacja
blader/humanizer (MIT)", EN credited only Wikipedia. MIT requires the notice to
travel with redistribution, and these repos ARE redistribution.

Measured on 2026-08-05 before this gate existed: 61 SKILL.md across both repos,
exactly 1 carried an `attribution:` frontmatter field.

Pattern ported from criptogus/HermesOffice tools/check-licenses.mjs (Apache-2.0):
allowlist + SPDX expression parsing + EXCEPTIONS dict + exit 1. That script walks
an npm package-lock; our artifacts are markdown skills, so the walk is different
while the gate shape is the same. The twin cross-check is ours - it is the defect
class that actually bit us, and it compares the SET of credited upstreams rather
than "is there any attribution at all", because the humanizer defect was exactly
a skill that credited *an* upstream while dropping *the* upstream.

Severity model
--------------
BLOCKING - a redistributed skill credits nobody, or twins credit different
           upstreams. That is the license-notice risk.
WARNING  - attribution exists in prose but not as a machine-readable
           `attribution:` field, or a third-party repo is linked without context.
           Hygiene, not risk.

Run from either repo root:  python scripts/attribution-gate.py
Optional:                   python scripts/attribution-gate.py --twin ../awesome-matematic-skills-en
Exit 0 = releasable. Exit 1 = blocking defects on stdout.
Stdlib only, ASCII-safe output (PS 5.1 stdout is cp852), no network.
"""
import argparse
import os
import re
import sys

# Permissive licenses we are allowed to build on. Anything outside this list is a
# strategy decision for WM, not something a script waves through.
ALLOWED_LICENSES = {
    "MIT", "MIT-0", "Apache-2.0", "Apache 2.0", "ISC", "BSD-2-Clause",
    "BSD-3-Clause", "0BSD", "BlueOak-1.0.0", "CC0-1.0", "CC-BY-4.0",
    "CC BY 4.0", "Zlib", "Unlicense", "Python-2.0", "Unicode-3.0", "OFL-1.1",
}

# Skills that legitimately have no upstream: written from zero at MateMatic.
# Adding a name here is an ASSERTION that you checked the history, not a mute button.
EXCEPTIONS = {
    # name: why it needs no attribution
}

# Twin pairs across the PL and EN marketplaces. Credited upstreams must not
# diverge between a skill and its translation - the 2026-08-04 defect class.
TWINS = {
    "humanizer-pl": "humanizer-en",
    "marko-pl-content": "reviewer-en",
    "adversarial-legal-review-pl": "adversarial-legal-review-en",
    "ocena-outputu-pl": "output-scoring-en",
    "ekstraktor-cytatow-pl": "citation-extraction-en",
    "atak-przeciwnika-pl": "opposing-counsel-attack-en",
    "pierwsze-wrazenie-sedziego-pl": "judicial-first-impression-en",
    "rodo-dsar-pl": "gdpr-dsar-en",
    "rodo-dpia-pl": "gdpr-dpia-en",
    "rodo-naruszenie-72h-pl": "gdpr-breach-72h-en",
    "rodo-ropa-dpa-pl": "gdpr-ropa-dpa-en",
    "ai-act-triage-pl": "eu-ai-act-triage-en",
    "nis2-ksc-pl": "nis2-compliance-triage-en",
    "tajemnica-preflight-pl": "privilege-preflight-en",
    "subsumpcja-pl": "legal-syllogism-en",
    "klauzule-kontraktowe-pl": "clause-checklist-en",
    "hierarchia-zrodel-pl": "authority-triage-en",
    "eu-sparql-search": "eu-sparql-search",
}

# Derivation markers. Deliberately EXCLUDES bare "na podstawie": it is ordinary
# Polish legal prose ("na podstawie art. 92") and matched 43/43 skills on the
# first measurement. A marker alone is not enough - see SOURCE_TOKEN_RE.
DERIVATION_RE = re.compile(
    r"(?i)\b("
    r"adaptacj\w*|adaptowan\w*|adapted\s+from|adaptation\s+of|"
    r"cherry-?pick\w*|"
    r"fork(?:ed)?\s+(?:of|from|z)\b|"
    r"based\s+on|bazuje\s+na|"
    r"wzorowan\w*\s+na|"
    r"\bport\s+(?:of|z)\b|"
    r"przeklad\s+skilla|przek\u0142ad\s+skilla"
    r")"
)

# A derivation claim only counts when the same line names a source. This is what
# separates "Cherry-pick z github/spec-kit (MIT)" from the AI Act's
# "zdolnosc adaptacji po wdrozeniu".
SOURCE_TOKEN_RE = re.compile(
    r"(?i)("
    r"https?://|github\.com|wikipedia|"
    r"\bautorstwa\b|"
    r"\((?:MIT|Apache[ -]?2\.?0?|BSD[^)]*|CC[ -]?BY[^)]*|ISC)\)|"
    r"\b(?:MIT|Apache)\b"
    r")"
)

# Our own orgs are not third-party sources.
OWN_ORGS = {"matematicsolutions", "mazurwieslaw2022-cmd", "matematic-co"}
GH_RE = re.compile(r"github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)")
WIKI_RE = re.compile(r"(?i)\b(?:en\.|pl\.)?wikipedia\.org|\bWikipedia\b")
AUTHOR_RE = re.compile(
    r"(?i)\bautorstwa\s+"
    r"([A-Z\u0104-\u017b][\w\u0104-\u017c-]+(?:\s+[A-Z\u0104-\u017b][\w\u0104-\u017c-]+){0,2})"
    r"(?=[\s.,;)]|$)")

# Bare `owner/repo` credit, only ever read off a line that already states a
# derivation. Filenames and in-repo paths are filtered out by the dot test and
# the stopword list, so `scripts/preflight.py` or `skills/humanizer-pl` do not
# masquerade as upstreams.
BARE_SLUG_RE = re.compile(r"(?<![\w/.-])([A-Za-z0-9][\w.-]{1,38})/([A-Za-z0-9][\w.-]{1,38})(?![\w/-])")
SLUG_STOPWORDS = {
    "skills", "scripts", "docs", "src", "packages", "tools", "apps", "assets",
    "examples", "references", "commands", "agents", "hooks", "tests", "lib",
    "main", "blob", "tree", "raw", "releases", "tag", "www", "http", "https",
    "claude", "plugin", "bundle", "and", "or", "the", "a", "i", "w", "z",
    # Polish prose that happens to parse as owner/repo when a licence token
    # sits nearby on the same line. Known limitation: this list is observed,
    # not exhaustive - a new false upstream shows up as a twin warning, never
    # as a blocker, because blocking needs one side at zero repos.
    "edycji", "przegladu", "tresci", "analizy", "oceny", "pisma", "wyroku",
}

# Canonical key: `attribution:`, top level (WM decision 2026-08-05). The name has
# to say the obligation, not the sentiment - MIT and Apache-2.0 require a notice,
# and "inspiration" makes a licence duty read like a courtesy. The two repos used
# to disagree (PL `attribution:`, EN `metadata.inspiration:`) and that divergence
# is exactly why nothing could cross-check the twins.
#
# Migrated 2026-08-05: 20 PL + 11 EN skills moved off `inspiration:`, 0 left.
# `inspiration` stays readable ONLY so a stale branch fails loudly here rather
# than silently losing its credit; new skills must use `attribution:`.
ATTRIB_KEY_RE = re.compile(r"^\s*(attribution)\s*:\s*(.*)$", re.I)
LEGACY_KEY_RE = re.compile(r"^\s*(inspiration|credits?|upstream|based_on)\s*:\s*(.*)$", re.I)

LICENSE_TOKEN_RE = re.compile(r"(?i)\b(MIT|Apache[ -]?2\.?0?|BSD-?\d?|CC[ -]?BY|ISC|github)\b")

# The canonical shape (WM decision 2026-08-05): one top-level `attribution:` key,
# with the nature of the relationship in the value, not in the key name.
#   attribution:
#     source: owner/repo
#     url: https://...
#     license: MIT
#     relationship: adaptation | clean-room | pattern-only | vendored | original
#     note: >
#       what was taken and what was written from scratch
# A list of such blocks is allowed when a skill draws on more than one upstream.
SOURCE_LINE_RE = re.compile(r"^\s*-?\s*source:\s*(.+)$", re.I)
# `dependency` was added after the gate blocked doc-intel-llm-tier-pl, which does
# not derive from contextgem at all - it imports it at runtime. Forcing that into
# "adaptation" would have been a false statement about provenance, so the
# vocabulary grew instead of the fact bending to fit it.
RELATIONSHIPS = {"adaptation", "clean-room", "pattern-only",
                 "vendored", "dependency", "original"}
RELATION_LINE_RE = re.compile(r"^\s*-?\s*relationship:\s*(.+?)\s*$", re.I)

SPDX_SPLIT = re.compile(r"\s+(?:OR|AND)\s+", re.I)

_FOLD = {
    "\u0105": "a", "\u0107": "c", "\u0119": "e", "\u0142": "l", "\u0144": "n",
    "\u00f3": "o", "\u015b": "s", "\u017a": "z", "\u017c": "z",
    "\u0104": "A", "\u0106": "C", "\u0118": "E", "\u0141": "L", "\u0143": "N",
    "\u00d3": "O", "\u015a": "S", "\u0179": "Z", "\u017b": "Z",
    "\u2014": "-", "\u2013": "-", "\u2018": "'", "\u2019": "'",
    "\u201c": '"', "\u201d": '"',
}


def ascii_fold(s):
    """PS 5.1 stdout is cp852; fold to ASCII so findings stay readable."""
    return "".join(_FOLD.get(ch, ch if ord(ch) < 128 else "?") for ch in s)


def spdx_ok(expr):
    """Accept an SPDX expression if it resolves to permissive licenses.

    OR -> any branch qualifying is enough. AND -> every branch must qualify.
    WITH -> fall back to the base license. Mirrors check-licenses.mjs semantics.
    """
    if not expr:
        return False
    expr = expr.strip().strip('"').strip("'").rstrip(".")
    expr = expr.split(" WITH ")[0].strip().strip("()")
    if re.search(r"\bOR\b", expr, re.I):
        return any(spdx_ok(p) for p in SPDX_SPLIT.split(expr))
    if re.search(r"\bAND\b", expr, re.I):
        return all(spdx_ok(p) for p in SPDX_SPLIT.split(expr))
    return expr in ALLOWED_LICENSES


def split_frontmatter(txt):
    """Return (frontmatter_text, body_text, body_line_offset).

    The offset matters: findings must cite real file:line, not body-relative
    lines. Getting this wrong once already sent me chasing a phantom defect.
    """
    if not txt.startswith("---"):
        return "", txt, 0
    parts = txt.split("---", 2)
    if len(parts) < 3:
        return "", txt, 0
    fm = parts[1]
    # line 1 is the opening '---'; fm contributes its own newlines; then '---'.
    offset = 1 + fm.count("\n")
    return fm, parts[2], offset


def fm_field(fm, key):
    """Read a single frontmatter field, tolerating folded multi-line values."""
    m = re.search(
        r"^%s:\s*(.*?)(?=^[A-Za-z_][\w-]*:\s|\Z)" % re.escape(key),
        fm, re.M | re.S,
    )
    if not m:
        return None
    return " ".join(m.group(1).split()) or None


def credited_upstreams(text, slug_lines=(), trusted_lines=()):
    """Normalized set of third parties this text credits.

    Credit is written three ways in our corpus and all three count:
    a full github.com URL, a bare `owner/repo` slug (AnttiHero/lavern,
    github/spec-kit), and a named human ("autorstwa X"). Counting only URLs
    reported four skills as crediting nobody when they plainly do - an
    overstatement of legal risk, which is worse than a miss here.
    """
    out = set()
    for owner, repo in GH_RE.findall(text):
        if owner.lower() not in OWN_ORGS:
            repo = repo.rstrip(")].,").lower()
            if repo.endswith(".git"):
                repo = repo[:-4]  # clone URL and page URL are the same upstream
            out.add("gh:%s/%s" % (owner.lower(), repo))
    # A bare slug only counts as credit when the same line names a licence or
    # github. Without that clamp, legal prose donates fake upstreams:
    # "IRAC/CREAC", "PL/UE" and "CELEX/OJ" all parse as owner/repo, and one of
    # them manufactured a blocking finding on its own.
    #
    # An attribution FIELD is a declaration, so the whole line is trusted. Prose
    # is not, so there the slug must also sit beside the licence token. Applying
    # the distance clamp to declaration lines emptied two skills that plainly do
    # credit their upstream, and the "both sides empty" twin branch then dropped
    # the pair without a word - a clean exit code hiding a lost finding.
    # Inside an attribution block, the upstream is named on its own `source:` line,
    # so the licence sits on a DIFFERENT line and the proximity rule cannot apply.
    # Read those lines directly. Restricting this to `source:` also keeps prose in
    # `note:` out - otherwise "IRAC/CREAC" in a note would donate a fake upstream.
    for line in trusted_lines:
        m = SOURCE_LINE_RE.match(line)
        if not m:
            continue
        for om in BARE_SLUG_RE.finditer(m.group(1)):
            owner, repo = om.group(1), om.group(2)
            if owner.lower() in OWN_ORGS or "." in repo or "." in owner:
                continue
            if owner.lower() in SLUG_STOPWORDS or repo.lower() in SLUG_STOPWORDS:
                continue
            out.add("gh:%s/%s" % (owner.lower(), repo.lower()))

    for line, trusted in ([(l, True) for l in trusted_lines]
                          + [(l, False) for l in slug_lines]):
        marks = [m.start() for m in LICENSE_TOKEN_RE.finditer(line)]
        if not marks:
            continue
        for m in BARE_SLUG_RE.finditer(line):
            owner, repo = m.group(1), m.group(2)
            if not trusted and min(abs(m.start() - p) for p in marks) > 60:
                continue
            # No extra clamp on trusted lines. Adding one here silently stopped
            # detecting legacy free-text `inspiration:` values, where the slug sits
            # at the start and the licence 80 characters later - two twin pairs went
            # from credited to "credits nobody" without a single file changing.
            # Acronym noise (IRAC/CREAC, PL/UE) is already handled by the
            # all-uppercase filter below.
            if owner.lower() in OWN_ORGS or "." in repo or "." in owner:
                continue
            if owner.lower() in SLUG_STOPWORDS or repo.lower() in SLUG_STOPWORDS:
                continue
            if owner.isupper() and repo.isupper():
                continue
            out.add("gh:%s/%s" % (owner.lower(), repo.lower()))
    if WIKI_RE.search(text):
        out.add("wikipedia")
    for author in AUTHOR_RE.findall(text):
        out.add("person:%s" % " ".join(author.split()).lower())
    return out


def validate_attribution_schema(fm):
    """Check the attribution block against the canonical shape.

    PyYAML is OPTIONAL on purpose: the gate must keep running on a bare Python,
    so a missing parser degrades to "not checked" rather than to a false pass.
    Returns a list of problem strings (empty when fine or when unchecked).
    """
    try:
        import yaml
    except ImportError:
        return []
    try:
        data = yaml.safe_load(fm)
    except Exception as e:
        return ["frontmatter is not valid YAML: %s" % str(e).split("\n")[0]]
    if not isinstance(data, dict):
        return []
    blocks = data.get("attribution")
    if blocks is None:
        return []
    if isinstance(blocks, str):
        return []  # legacy prose value, tolerated
    if isinstance(blocks, dict):
        blocks = [blocks]
    if not isinstance(blocks, list):
        return ["attribution must be a mapping, a list of mappings, or prose"]
    out = []
    for i, b in enumerate(blocks):
        where = "attribution[%d]" % i if len(blocks) > 1 else "attribution"
        if not isinstance(b, dict):
            out.append("%s is not a mapping" % where)
            continue
        rel = str(b.get("relationship", "")).strip()
        if not rel:
            out.append("%s has no `relationship`" % where)
        elif rel not in RELATIONSHIPS:
            out.append("%s relationship '%s' not in %s"
                       % (where, rel, "|".join(sorted(RELATIONSHIPS))))
        # `original` means there is nobody to credit, so it is the one shape
        # allowed to omit a source. Everything else must name one.
        if rel != "original" and not str(b.get("source", "")).strip():
            out.append("%s relationship '%s' requires a `source`" % (where, rel or "?"))
    return out


def scan_repo(root):
    """Collect one record per SKILL.md under root.

    Upstreams are extracted from the WHOLE file, frontmatter included. An
    earlier revision parsed only the body plus a top-level `attribution:` key
    and therefore reported three EN skills as crediting nobody - their credit
    sat in a `metadata.inspiration:` field it never read. Scanning everything
    removes that entire bug class.
    """
    out = {}
    for dirpath, _dirnames, filenames in os.walk(root):
        if "SKILL.md" not in filenames:
            continue
        path = os.path.join(dirpath, "SKILL.md")
        txt = open(path, encoding="utf-8", errors="replace").read()
        fm, _body, _offset = split_frontmatter(txt)
        name = fm_field(fm, "name") or os.path.basename(dirpath)

        lines = txt.splitlines()
        derived, attrib_lines, attrib_key = [], [], None
        legacy_keys = []
        in_attrib_block, attrib_indent = False, 0
        for i, line in enumerate(lines, 1):
            legacy = LEGACY_KEY_RE.match(line)
            if legacy:
                legacy_keys.append((i, legacy.group(1).lower()))
            key_here = ATTRIB_KEY_RE.match(line)
            if key_here:
                attrib_key = attrib_key or key_here.group(1).strip()
                in_attrib_block = True
                attrib_indent = len(line) - len(line.lstrip())
                attrib_lines.append(line)
                continue
            if in_attrib_block:
                # A YAML block continues while the line is indented deeper than its
                # key. The earlier rule also stopped at any `key:` line, which broke
                # the list form: `- source: a` was read, then the sibling `license:`
                # line ended the block and every later entry vanished. A skill
                # crediting two upstreams silently reported one.
                if not line.strip():
                    attrib_lines.append(line)
                    continue
                if len(line) - len(line.lstrip()) > attrib_indent:
                    attrib_lines.append(line)
                    continue
                in_attrib_block = False
            if DERIVATION_RE.search(line) and SOURCE_TOKEN_RE.search(line):
                derived.append((i, " ".join(line.split())[:150]))

        out[name] = {
            "path": os.path.relpath(path, os.path.dirname(root)),
            "attrib_key": attrib_key,
            "legacy_keys": legacy_keys,
            "schema": validate_attribution_schema(fm),
            "license": fm_field(fm, "license"),
            "upstreams": credited_upstreams(
                txt,
                slug_lines=[s for _, s in derived],
                trusted_lines=attrib_lines,
            ),
            "derived": derived,
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--twin", help="path to the sibling marketplace repo")
    ap.add_argument("--root", default=None, help="repo root (default: parent of this script)")
    ap.add_argument("--notice", action="store_true",
                    help="print the aggregated upstream block for NOTICE and exit 0")
    args = ap.parse_args()

    root = os.path.abspath(args.root or os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    twin_root = args.twin
    if not twin_root:
        base = os.path.basename(root)
        for suffix, other in (("-pl", "-en"), ("-en", "-pl")):
            if base.endswith(suffix):
                guess = os.path.join(os.path.dirname(root), base[: -len(suffix)] + other)
                if os.path.isdir(guess):
                    twin_root = guess
                break

    if args.notice:
        # NOTICE lists per-skill licences but never named the upstreams those
        # skills derive from - the one place a redistributor actually looks.
        # Regenerate that block from the same parse the gate uses, so the two
        # cannot drift apart.
        skills = scan_repo(root)
        by_upstream = {}
        for name, rec in skills.items():
            for up in rec["upstreams"]:
                if up.startswith("gh:"):
                    by_upstream.setdefault(up[3:], set()).add(name)
        print("Third-party upstreams")
        print("=====================")
        print()
        print("Skills in this repo adapt patterns from the projects below.")
        print("Generated by scripts/attribution-gate.py --notice; do not hand-edit.")
        print()
        for up in sorted(by_upstream):
            print("- https://github.com/%s" % up)
            for s in sorted(by_upstream[up]):
                print("    used by: %s" % s)
        print()
        print("(%d upstream projects across %d skills)" % (
            len(by_upstream), len({s for v in by_upstream.values() for s in v})))
        sys.exit(0)

    problems, warnings = [], []
    here = scan_repo(root)
    there = scan_repo(os.path.abspath(twin_root)) if twin_root else {}

    print("repo:  %s  (%d skills)" % (os.path.basename(root), len(here)))
    if twin_root:
        print("twin:  %s  (%d skills)" % (os.path.basename(os.path.abspath(twin_root)), len(there)))
    print()

    for name, rec in sorted(here.items()):
        if name in EXCEPTIONS:
            continue

        # 1. Derived work that credits nobody at all = license-notice risk.
        if rec["derived"] and not rec["upstreams"]:
            ln, snippet = rec["derived"][0]
            problems.append(
                "%s: states derivation but credits no source\n"
                "      %s:%d  %s" % (name, rec["path"], ln, ascii_fold(snippet))
            )
        # 2. Credited in prose only = hygiene, not risk.
        elif rec["derived"] and not rec["attrib_key"]:
            ln, _ = rec["derived"][0]
            warnings.append(
                "%s: derivation credited in prose only, no attribution field (%s:%d)"
                % (name, rec["path"], ln)
            )

        # 2a. Legacy key names. Blocking on purpose: a stale branch that still
        # says `inspiration:` must fail here rather than quietly ship a credit
        # the canonical parser no longer reads.
        for ln, key in rec["legacy_keys"]:
            problems.append(
                "%s: legacy key `%s:` at %s:%d - the canonical key is `attribution:` "
                "(top level)" % (name, key, rec["path"], ln)
            )

        # 2b. A malformed attribution block is worse than none: it looks like
        # compliance while carrying no usable fact.
        for msg in rec["schema"]:
            problems.append("%s: %s (%s)" % (name, msg, rec["path"]))

        # 3. Declared licenses must be permissive.
        lic = rec["license"]
        if lic and not spdx_ok(lic):
            problems.append(
                "%s: license '%s' is not on the permissive allowlist "
                "(doktryna: MIT/Apache, nigdy foundation)" % (name, ascii_fold(lic))
            )

    # 4. Twins must credit the SAME upstreams. Boolean "has some attribution"
    #    is not enough - that is precisely how the humanizer defect survived.
    if there:
        for pl_name, en_name in sorted(TWINS.items()):
            a, b = here.get(pl_name), there.get(en_name)
            if a is None and b is None:
                a, b = here.get(en_name), there.get(pl_name)
            if not a or not b:
                continue
            # One side crediting NOBODY while the other credits an upstream is
            # the humanizer defect: the notice stopped travelling with the
            # translation. That blocks. Two sides crediting DIFFERENT upstreams
            # is usually legitimate - output-scoring-en genuinely derives from
            # DISC-LawLLM while ocena-outputu-pl derives from lavern - so that
            # only asks for human eyes.
            # Compare code upstreams only. `person:` is detected from the Polish
            # "autorstwa X" and has no English equivalent, so keeping it in the
            # comparison reported a language asymmetry as a content difference on
            # every translated pair.
            a_repos = {u for u in a["upstreams"] if u.startswith("gh:")}
            b_repos = {u for u in b["upstreams"] if u.startswith("gh:")}
            a_cmp = {u for u in a["upstreams"] if not u.startswith("person:")}
            b_cmp = {u for u in b["upstreams"] if not u.startswith("person:")}
            if not a_repos and not b_repos:
                # Neither credits a repo. Silence here is what hid the pair
                # before, so a difference in any other credit still surfaces.
                if a_cmp != b_cmp:
                    warnings.append(
                        "TWIN %s <-> %s: no code upstream on either side, other "
                        "credits differ (%s vs %s)" % (
                            pl_name, en_name,
                            ", ".join(sorted(a_cmp)) or "-",
                            ", ".join(sorted(b_cmp)) or "-",
                        )
                    )
                continue
            if not a_repos or not b_repos:
                silent, loud = (b, a) if not b_repos else (a, b)
                problems.append(
                    "TWIN DRIFT %s <-> %s: one twin credits no code upstream at all\n"
                    "      credits:  %s\n"
                    "      silent:   %s" % (
                        pl_name, en_name,
                        ", ".join(sorted(loud["upstreams"])), silent["path"],
                    )
                )
            elif a_cmp != b_cmp:
                warnings.append(
                    "TWIN %s <-> %s credit different upstreams (%s vs %s) - "
                    "legitimate if they really derive from different sources" % (
                        pl_name, en_name,
                        ", ".join(sorted(a_cmp)), ", ".join(sorted(b_cmp)),
                    )
                )

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
