"""Podzial teczki na pisma - lokalnie, bez LLM, bez chmury.

Wzorzec: jerryjliu/docjev (Apache-2.0) - podzial jako DECYZJA PER STRONA
("czy strona N zaczyna nowy dokument, czy kontynuuje N-1?"), a nie prosba do
modelu o liste segmentow. Z DocJev bierzemy niezmienniki, silnik jest nasz:
DocJev pyta hostowanego Jeva, a tekst akt nie moze opuscic maszyny kancelarii.

Niezmienniki (kazdy sprawdzany, zlamanie = `failed`, nigdy cichy sukces):
  * kazda strona nalezy do DOKLADNIE jednego segmentu (pelny mianownik);
  * pusta strona zostaje w segmencie i nigdy nie otwiera nowego;
  * strona, na ktorej JEST obraz, a nie ma tekstu, to strona NIECZYTELNA - blad,
    nie kategoria "inne" (za DocJev: pusty OCR nie jest dowodem pustej strony);
  * dwa sasiednie pisma tej samej kategorii to DWA segmenty (zmiana kategorii nie
    jest jedynym sygnalem granicy);
  * decyzja niesie DOWOD: liste sygnalow, ktore zadzialaly. Silnik jest
    deterministyczny, wiec dowod jest prawdziwy - nie dopisujemy uzasadnien.

Uzycie:
    python scripts/split_packet.py TECZKA.pdf --pretty
    python scripts/split_packet.py strony.json --reguly contract/kategorie_pism.json
    python scripts/split_packet.py TECZKA.pdf --eksport wynik/   # PDF per pismo

`strony.json` = {"pages": [{"number": 1, "text": "...", "image": false}, ...]}
(`image` = na stronie jest raster; potrzebne do odroznienia pustej od nieczytelnej).

Kod wyjscia jak w routing_gate.py: 0 = ok, 10 = degraded (sa decyzje do przejrzenia
albo puste strony), 20 = failed (strona nieczytelna, brak wejscia, zlamany niezmiennik).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_RULES = os.path.join(os.path.dirname(HERE), "contract", "kategorie_pism.json")

STATUS_OK, STATUS_DEGRADED, STATUS_FAILED = "ok", "degraded", "failed"
EXIT = {STATUS_OK: 0, STATUS_DEGRADED: 10, STATUS_FAILED: 20}

HEAD_LINES = 12          # ile niepustych linii od gory strony to "naglowek"
HEADING_LINES = 3        # naglowek TYPU pisma musi byc w pierwszych liniach: pismo zaczyna sie na gorze strony
                         # (dev 09-21: "UZASADNIENIE" w 3.-5. linii pod punktami sentencji = srodek wyroku)
TAIL_LINES = 6           # ile linii od dolu to "blok podpisow"
THRESHOLD = 2.5          # suma wag >= prog -> strona otwiera nowe pismo
REVIEW_MARGIN = 1.0      # |suma - prog| < margines -> decyzja do przejrzenia

# --- Sygnaly (wagi nazwane w jednym miejscu, zeby dalo sie o nich rozmawiac) ---
W_HEADING = 3.0          # naglowek typu pisma (WYROK, POSTANOWIENIE, ...)
W_FORMULA = 2.0          # "W imieniu Rzeczypospolitej Polskiej"
W_SYGN_TOP = 1.5         # "Sygn. akt" w pierwszych liniach
W_SYGN_FIRST = 2.0       # "Sygn. akt" jako PIERWSZA linia strony
W_REPEATED = -3.0        # ten sam naglowek i ta sama sygnatura co biezace pismo = stopka strony (formularz UK)
W_SYGN_CHANGE = 2.0      # inna sygnatura niz w biezacym pismie
W_COURT_TOP = 0.5        # "Sad Rejonowy w ..." na gorze strony
W_DATE_TOP = 0.5         # "Dnia 12 marca 2024 r." na gorze strony
W_PAGE_ONE = 1.5         # "Strona 1 z N" / "- 1 -"
W_PAGE_NEXT = -3.0       # "Strona 3 z N" / "- 3 -" -> kontynuacja
W_LOWER_START = -2.0     # strona zaczyna sie mala litera -> kontynuacja zdania
W_PREV_MIDSENT = -1.5    # poprzednia strona konczy sie w pol zdania
W_PREV_HYPHEN = -2.0     # poprzednia strona konczy sie przeniesieniem wyrazu
W_PREV_SIGNED = 1.0      # poprzednia strona konczy sie blokiem podpisow

SYGN_RE = re.compile(
    r"(?:sygn\.?\s*(?:akt)?\s*:?\s*)?\b([IVXL]{1,5}\s*[A-Z][A-Za-z]{0,5}\.?(?:\s+[A-Z][a-z]{0,3}\.?)?\s+\d{1,6}/\d{2,4})\b")
SYGN_TOP_RE = re.compile(r"\bsygn(?:atura)?\.?\s*(?:akt)?\b", re.I)
# "Wyrok z dnia 19 wrzesnia 1996 r." - naglowek starych orzeczen SN, pisany mala litera
DATED_HEADING_RE = re.compile(r"^(wyrok|postanowienie|uchwa[lł]a|zarz[aą]dzenie)\s+(?:z\s+dnia|s[aą]du)\b", re.I)
ENUM_LINE_RE = re.compile(r"^(?:[IVXL]{1,6}|\d{1,3})[.)]\s*$")
FORMULA_RE = re.compile(r"w\s+imieniu\s+rzeczypospolitej\s+polskiej", re.I)
COURT_RE = re.compile(r"^(?:##+\s*)?s[aą]d\s+(?:rejonowy|okr[eę]gowy|apelacyjny|najwy[zż]szy)", re.I)
DATE_RE = re.compile(r"\bdnia\s+\d{1,2}\s+\w+\s+\d{4}\s*(?:r\.?|roku)?", re.I)
PAGE_MARK_RE = re.compile(r"(?:\bstrona\s+(\d{1,4})\s*(?:z|/)\s*\d{1,4}\b|^\s*-\s*(\d{1,4})\s*-\s*$)", re.I | re.M)
SIGN_RE = re.compile(
    r"\b(?:przewodnicz[aą]c|ssn|ssr|sso|ssa|s[eę]dzi(?:a|owie)|za\s+zgodno[sś][cć]|"
    r"podpis|prokurator|kierownik\s+sekretariatu|protokolant|adwokat|radca\s+prawny|obro[nń]ca)",
    re.I)
TERMINAL = set('.!?:;)"”»')
# Sygnaly naglowkowe licza sie TYLKO na krotkiej linii (struktura, nie proza).
# Zmierzone na dev 09-21: uzasadnienia cytuja cudze sygnatury i daty w zdaniach
# ("Postanowieniem z dnia 25 lipca 2001 r., sygn. akt VI GCo 134/01, Sad ..."),
# co dawalo 43 z ~100 falszywych granic jako `data_na_gorze + zmiana_sygnatury`.
SHORT = 60
SIGN_SHORT = 70


def _short(line: str, limit: int = SHORT) -> bool:
    return len(line) <= limit


def _norm_line(line: str) -> str:
    line = unicodedata.normalize("NFC", line)
    return re.sub(r"\s+", " ", line.lstrip("#").strip())


def _lines(text: str) -> list[str]:
    return [ln for ln in (_norm_line(x) for x in text.replace("\r", "").split("\n")) if ln]


def load_rules(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        rules = json.load(fh)
    cats = rules.get("categories") or []
    if not cats:
        raise ValueError(f"{path}: pusta lista kategorii - bramka bez regul to BLOKADA, nie sukces")
    for c in cats:
        c["_re"] = [re.compile(p, re.I) for p in c.get("heading_patterns", [])]
    if not any(c["id"] == "other" for c in cats):
        cats.append({"id": "other", "description": "Nie pasuje do zadnej kategorii.", "_re": []})
    return rules


def heading_category(head: list[str], rules: dict) -> tuple[str | None, str | None]:
    """Kategoria z naglowka: pierwsza linia naglowka pasujaca do wzorca kategorii.

    Naglowek typu pisma w aktach jest krotki i zwykle wersalikami; dlugiej linii
    prozy ("... postanowienie sadu z dnia ...") nie traktujemy jak naglowka.
    """
    for line in head:
        # Naglowek stoi PRZED trescia. Pierwsza linia tresci (proza, mala litera,
        # punkt sentencji "IV.") konczy strefe naglowka - "UZASADNIENIE" pod
        # punktami sentencji to srodek wyroku, nie nowe pismo (test 09-21).
        if len(line) > 90 or line[:1].islower() or ENUM_LINE_RE.match(line):
            break
        # "Sygn. akt III KK 306/22 POSTANOWIENIE" - sygnatura i typ w jednej linii
        probe = SYGN_RE.sub(" ", line)
        probe = SYGN_TOP_RE.sub(" ", probe).strip(" .:")
        letters = [ch for ch in probe if ch.isalpha()]
        if not letters:
            continue
        upper_ratio = sum(ch.isupper() for ch in letters) / len(letters)
        for cat in rules["categories"]:
            for rx in cat["_re"]:
                if rx.match(probe) and (upper_ratio > 0.6 or cat.get("mixed_case_ok")
                                        or (DATED_HEADING_RE.match(probe) and _short(probe))):
                    return cat["id"], line
    return None, None


def _sygn_line(line: str) -> bool:
    """Linia sygnatury: zaczyna sie od 'Sygn' albo jest krotka i sklada sie glownie z sygnatury."""
    if SYGN_TOP_RE.match(line):
        return _short(line, 90)
    m = SYGN_RE.search(line)
    return bool(m) and len(line) <= len(m.group(0)) + 25


def page_sygnatura(head: list[str]) -> str | None:
    for line in head[:6]:
        if not _sygn_line(line):
            continue
        m = SYGN_RE.search(line)
        if m:
            return re.sub(r"[\s.]+", " ", m.group(1)).strip().upper()
    return None


def decide(pages: list[dict], rules: dict) -> dict:
    decisions = []
    cur_sygn = None
    seen_pairs: set = set()   # (kategoria, sygnatura) widziane w biezacym pismie
    prev_lines: list[str] = []
    for idx, page in enumerate(pages):
        number = page["number"]
        text = page.get("text") or ""
        lines = _lines(text)
        blank = not lines
        dec = {"page": number, "blank": blank, "signals": [], "score": 0.0}
        if blank:
            if page.get("image"):
                dec["unreadable"] = True   # raster jest, tekstu nie ma -> NIE "pusta"
            dec["starts_document"] = idx == 0
            decisions.append(dec)
            continue          # pusta strona nie zmienia kontekstu poprzedniej
        head = lines[:HEAD_LINES]
        cat, heading = heading_category(head[:HEADING_LINES], rules)
        sygn = page_sygnatura(head)
        sig = dec["signals"]
        if cat and cat != "other":
            needs_sygn = next(c for c in rules["categories"] if c["id"] == cat).get("start_requires_sygnatura")
            has_sygn = any(_sygn_line(x) for x in head[:4])
            if needs_sygn and not has_sygn and heading != head[0]:
                sig.append(("naglowek_bez_sygnatury:" + cat, 0.0))
                dec["review"] = True
            elif needs_sygn and not has_sygn:
                # dev 09-21: naglowek w 1. linii bez sygnatury = poczatek pisma w 11 z 12
                sig.append(("naglowek_pierwsza_linia_bez_sygnatury:" + cat, W_HEADING))
                dec["review"] = True
            else:
                sig.append(("naglowek:" + cat, W_HEADING))
        if any(FORMULA_RE.search(x) for x in head):
            sig.append(("formula_rp", W_FORMULA))
        if _sygn_line(head[0]):
            sig.append(("sygnatura_pierwsza_linia", W_SYGN_FIRST))
        elif any(SYGN_TOP_RE.match(x) and _short(x, 90) for x in head[:4]):
            sig.append(("sygnatura_na_gorze", W_SYGN_TOP))
        if cat and cat != "other" and sygn and (cat, sygn) in seen_pairs:
            sig.append(("powtorzony_naglowek", W_REPEATED))
        if sygn and cur_sygn and sygn != cur_sygn:
            sig.append(("zmiana_sygnatury", W_SYGN_CHANGE))
        if any(COURT_RE.search(x) and _short(x, 100) for x in head[:6]):
            sig.append(("sad_na_gorze", W_COURT_TOP))
        if any(DATE_RE.search(x) and _short(x) for x in head[:8]):
            sig.append(("data_na_gorze", W_DATE_TOP))
        marks = [int(a or b) for a, b in PAGE_MARK_RE.findall(text)]
        if marks:
            sig.append(("numer_strony_1", W_PAGE_ONE) if min(marks) == 1 else ("numer_strony_" + str(min(marks)), W_PAGE_NEXT))
        first = lines[0]
        if first[:1].islower() or first[:1] in ",;)":
            sig.append(("start_mala_litera", W_LOWER_START))
        if prev_lines:
            last = prev_lines[-1]
            if last.endswith("-") and not last.endswith(" -"):
                sig.append(("poprzednia_przeniesienie", W_PREV_HYPHEN))
            elif last[-1:] not in TERMINAL and not (SIGN_RE.search(last) and _short(last, SIGN_SHORT)):
                sig.append(("poprzednia_w_pol_zdania", W_PREV_MIDSENT))
            if any(SIGN_RE.search(x) and _short(x, SIGN_SHORT) for x in prev_lines[-TAIL_LINES:]):
                sig.append(("poprzednia_podpisana", W_PREV_SIGNED))
        score = round(sum(w for _, w in sig), 2)
        dec["score"] = score
        dec["starts_document"] = idx == 0 or score >= THRESHOLD
        if idx > 0 and abs(score - THRESHOLD) < REVIEW_MARGIN:
            dec["review"] = True
        if idx > 0 and not dec["starts_document"] and cat and cat != "other" and not dec.get("review"):
            # naglowek typu pisma na gorze strony, a mimo to kontynuacja - zawsze do oka
            if any(c.startswith("naglowek:") for c, _ in sig):
                dec["review"] = True
        dec["category_hint"] = cat
        dec["heading"] = heading
        dec["sygnatura"] = sygn
        if dec["starts_document"]:
            cur_sygn = sygn      # nowe pismo = nowy kontekst sygnatury (moze byc None)
            seen_pairs = set()   # reset PRZED dodaniem pary strony otwierajacej pismo
        elif sygn and not cur_sygn:
            cur_sygn = sygn
        if cat and sygn:
            seen_pairs.add((cat, sygn))
        dec["signals"] = [{"code": c, "weight": w} for c, w in sig]
        decisions.append(dec)
        prev_lines = lines
    return {"decisions": decisions}


def build_segments(decisions: list[dict]) -> list[dict]:
    segs: list[dict] = []
    for d in decisions:
        if d.get("starts_document") or not segs:
            segs.append({"pages": [], "category": None, "heading": None, "sygnatura": None})
        s = segs[-1]
        s["pages"].append(d["page"])
        if s["category"] is None and d.get("category_hint"):
            s["category"], s["heading"] = d["category_hint"], d.get("heading")
        if s["sygnatura"] is None and d.get("sygnatura"):
            s["sygnatura"] = d["sygnatura"]
    for i, s in enumerate(segs, 1):
        s["id"] = f"pismo-{i:03d}"
        s["category"] = s["category"] or "other"
    return [{"id": s["id"], "category": s["category"], "pages": s["pages"],
             "heading": s["heading"], "sygnatura": s["sygnatura"]} for s in segs]


def split(pages: list[dict], rules: dict, total_pages: int | None = None) -> dict:
    """`total_pages` = mianownik ZRODLA (np. z parsera). Bez niego pokrycie mozna
    sprawdzic tylko wzgledem zwroconych stron - i obciecie przechodzi jako komplet."""
    if not pages:
        return {"status": STATUS_FAILED, "reasons": [{"code": "empty_input", "detail": "brak stron"}],
                "segments": [], "coverage": {"unit": "pages", "total": 0, "assigned": 0}}
    out = decide(pages, rules)
    decisions = out["decisions"]
    segments = build_segments(decisions)
    reasons = []

    # Niezmiennik pokrycia: kazda strona dokladnie raz, w kolejnosci.
    assigned = [p for s in segments for p in s["pages"]]
    expected = [p["number"] for p in pages]
    if assigned != expected:
        reasons.append({"code": "coverage_violation",
                        "detail": f"przypisane {len(assigned)} vs stron {len(expected)} - niezmiennik zlamany"})
    if total_pages is not None and total_pages != len(expected):
        reasons.append({"code": "coverage_violation",
                        "detail": f"zrodlo ma {total_pages} stron, parser zwrocil {len(expected)} - wynik NIEPELNY"})
        expected_total = total_pages
    else:
        expected_total = len(expected)

    unreadable = [d["page"] for d in decisions if d.get("unreadable")]
    blank = [d["page"] for d in decisions if d["blank"] and not d.get("unreadable")]
    review = [d["page"] for d in decisions if d.get("review")]
    if unreadable:
        reasons.append({"code": "pages_unreadable",
                        "detail": f"{len(unreadable)} stron z obrazem i bez tekstu: {unreadable[:12]} - "
                                  "najpierw OCR (routing_gate.py), podzial bez tych stron bylby zgadywaniem"})
    if blank:
        reasons.append({"code": "pages_blank", "detail": f"puste strony (zostaja w segmentach): {blank[:12]}"})
    if review:
        reasons.append({"code": "boundary_review",
                        "detail": f"granice blisko progu {THRESHOLD} (+/-{REVIEW_MARGIN}) na stronach {review[:12]} - do przejrzenia"})

    if any(r["code"] in ("coverage_violation", "pages_unreadable") for r in reasons):
        status = STATUS_FAILED
    elif reasons:
        status = STATUS_DEGRADED
    else:
        status = STATUS_OK
    return {"status": status, "reasons": reasons, "segments": segments,
            "coverage": {"unit": "pages", "total": expected_total, "assigned": len(assigned)},
            "engine": {"name": "sygnaly-lokalne", "threshold": THRESHOLD, "review_margin": REVIEW_MARGIN,
                       "wzorzec": "jerryjliu/docjev (Apache-2.0), decyzja per strona"},
            "page_decisions": decisions}


# --- Wejscie ------------------------------------------------------------------

def pages_from_pdf(path: str) -> tuple[list[dict], dict]:
    """LiteParse (lokalny OCR) gdy jest; inaczej pdftotext strona po stronie.

    Bez LiteParse strona-skan wyjdzie jako `image: None` + pusty tekst, wiec
    trafi do `pages_unreadable` tylko wtedy, gdy mamy dowod rastra. Bez dowodu
    oznaczamy ja jako NIEPEWNA (image=None) i status nie bedzie `ok`.
    """
    try:
        import liteparse  # noqa: PLC0415
    except ImportError:
        liteparse = None
    if liteparse is not None:
        # TEN SAM ekstraktor co sciezka kontraktu - z jawnym max_pages. Pierwsza wersja
        # wolala biblioteke bezposrednio i na aktach >1000 stron wziela 1000, a niezmiennik
        # pokrycia liczony od zwroconych stron zglosil komplet (przebieg 09-21).
        # Straznik w jednym pliku nie oslania drugiej sciezki wywolania.
        import liteparse_extract  # noqa: PLC0415
        data = liteparse_extract.extract(path, tessdata=os.environ.get("DOC_INTEL_TESSDATA") or None)
        pages = [{"number": p["number"], "text": p["text"], "image": p["image"]} for p in data["pages"]]
        return pages, {"parser": "liteparse", "total_pages": data["total_pages"],
                       "page_errors": len(data["page_errors"])}
    import subprocess  # noqa: PLC0415
    raw = subprocess.run(["pdftotext", "-enc", "UTF-8", path, "-"], capture_output=True, check=True).stdout
    chunks = raw.decode("utf-8").replace("\r\n", "\n").split("\f")
    if chunks and not chunks[-1].strip():
        chunks = chunks[:-1]
    pages = [{"number": i, "text": t, "image": None if not t.strip() else False}
             for i, t in enumerate(chunks, 1)]
    return pages, {"parser": "pdftotext", "total_pages": len(pages)}


def export_segments(pdf_path: str, segments: list[dict], out_dir: str) -> list[dict]:
    """Kopiuje DOKLADNE strony zrodla do PDF per pismo; sprawdza hash zrodla przed i po."""
    try:
        import pymupdf  # noqa: PLC0415
    except ImportError:
        return [{"code": "export_unavailable", "detail": "brak pymupdf - eksport pominiety JAWNIE"}]
    before = hashlib.sha256(open(pdf_path, "rb").read()).hexdigest()
    os.makedirs(out_dir, exist_ok=True)
    src = pymupdf.open(pdf_path)
    written = []
    for s in segments:
        dst = pymupdf.open()
        for p in s["pages"]:
            dst.insert_pdf(src, from_page=p - 1, to_page=p - 1)
        name = os.path.join(out_dir, f"{s['id']}-{s['category']}.pdf")
        if os.path.exists(name):
            return [{"code": "export_exists", "detail": f"{name} istnieje - nie nadpisuje"}]
        dst.save(name)
        if dst.page_count != len(s["pages"]):
            return [{"code": "export_page_mismatch", "detail": name}]
        written.append(name)
    after = hashlib.sha256(open(pdf_path, "rb").read()).hexdigest()
    if before != after:
        return [{"code": "source_changed", "detail": "zrodlo zmienilo sie w trakcie eksportu"}]
    return [{"code": "exported", "detail": f"{len(written)} plikow w {out_dir}", "source_sha256": before}]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("wejscie", help="PDF albo strony.json")
    ap.add_argument("--reguly", default=DEFAULT_RULES)
    ap.add_argument("--eksport", help="katalog na PDF per pismo (tylko wejscie PDF)")
    ap.add_argument("--pretty", action="store_true")
    ap.add_argument("--bez-decyzji", action="store_true", help="nie wypisuj page_decisions")
    a = ap.parse_args(argv)
    rules = load_rules(a.reguly)
    meta = {}
    if a.wejscie.lower().endswith(".json"):
        with open(a.wejscie, encoding="utf-8") as fh:
            pages = json.load(fh)["pages"]
    else:
        pages, meta = pages_from_pdf(a.wejscie)
    res = split(pages, rules, total_pages=meta.get("total_pages"))
    if meta.get("page_errors"):
        res["status"] = STATUS_FAILED
        res["reasons"].append({"code": "parser_page_errors", "detail": f"{meta['page_errors']} bledow stron parsera"})
    res["input"] = {"path": os.path.abspath(a.wejscie), **meta}
    if a.eksport:
        if a.wejscie.lower().endswith(".json"):
            res["reasons"].append({"code": "export_unavailable", "detail": "eksport wymaga PDF"})
        elif res["status"] == STATUS_FAILED:
            res["reasons"].append({"code": "export_refused", "detail": "status failed - nie tne teczki"})
        else:
            res["reasons"].extend(export_segments(a.wejscie, res["segments"], a.eksport))
    if a.bez_decyzji:
        res.pop("page_decisions", None)
    json.dump(res, sys.stdout, ensure_ascii=False, indent=2 if a.pretty else None)
    sys.stdout.write("\n")
    return EXIT[res["status"]]


if __name__ == "__main__":
    sys.exit(main())
