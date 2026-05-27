#!/usr/bin/env python3
"""
fetch_eurlex.py - pobiera akt prawny EU z EUR-Lex po CELEX.

Komplementarny do eu-sparql-search (skill SPARQL nad Cellar/EUR-Lex):
- eu-sparql-search = zapytania semantyczne nad metadanymi (znajdz akty po
  temacie, autorze, dacie, relacjach)
- fetch_eurlex.py = bezposrednie pobranie pelnej tresci konkretnego aktu
  po znanym CELEX (do citation-grounding / fidelity / audit-bundle)

EUR-Lex jest za CloudFront WAF (x-amzn-waf-action: challenge), wiec curl
nie wystarczy - potrzebny prawdziwy browser (Playwright Chromium).

Output: outputs/eurlex/<celex>/akt.md + meta.json + screenshot.png

Uzycie:
  python fetch_eurlex.py --celex 32024R1689              # AI Act, jezyk PL (domyslnie)
  python fetch_eurlex.py --celex 32016R0679 --lang EN    # RODO, jezyk EN
  python fetch_eurlex.py --celex 32024R1689 --out outputs/custom

Kontrakt meta.json (zgodny z citation-grounding-pl + legal-ai-audit-bundle):
  {
    "celex": "32024R1689",
    "typ": "rozporzadzenie|dyrektywa|decyzja|...",
    "numer": "2024/1689",
    "data_publikacji": "2024-07-12",
    "jezyk": "PL",
    "tytul": "Rozporzadzenie Parlamentu Europejskiego ...",
    "url": "https://eur-lex.europa.eu/legal-content/PL/TXT/?uri=CELEX:32024R1689",
    "pdf_url": "https://eur-lex.europa.eu/...",
    "eli": "http://data.europa.eu/eli/reg/2024/1689/oj",
    "pobrano_at": "2026-05-27T10:00:00Z",
    "zrodlo": "eur-lex.europa.eu"
  }

Exit codes:
  0 = sukces
  1 = nie znaleziono aktu / nieprawidlowy CELEX
  2 = blad polaczenia / timeout / WAF challenge nieudany
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

BASE_URL = "https://eur-lex.europa.eu/legal-content/{lang}/TXT/?uri=CELEX:{celex}"
SOURCE = "eur-lex.europa.eu"
VIEWPORT = {"width": 1280, "height": 1800}
TIMEOUT_MS = 45_000
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_date_pl(s: str) -> str | None:
    """`12.7.2024` / `12.07.2024` / `12/07/2024` -> `2024-07-12`."""
    m = re.search(r"\b(\d{1,2})[./](\d{1,2})[./](\d{4})\b", s)
    if not m:
        return None
    d, mo, y = m.groups()
    return f"{int(y):04d}-{int(mo):02d}-{int(d):02d}"


def detect_typ(content: str) -> str:
    """Wyciagnij typ aktu z naglowka (ROZPORZADZENIE / DYREKTYWA / DECYZJA)."""
    for kandidat, label in [
        (r"ROZPORZ\S*DZENIE", "rozporzadzenie"),
        (r"DYREKTYWA", "dyrektywa"),
        (r"DECYZJA", "decyzja"),
        (r"ZALECENIE", "zalecenie"),
        (r"OPINIA", "opinia"),
    ]:
        if re.search(kandidat, content):
            return label
    return "nieznane"


def fetch(celex: str, lang: str, out_dir: Path) -> int:
    celex = celex.upper().strip()
    if not re.match(r"^\d{5,}[A-Z]\d{4}$", celex):
        sys.stderr.write(
            f"[fetch_eurlex] Nieprawidlowy CELEX (oczekiwano np. '32024R1689'): {celex}\n"
        )
        return 1

    work_dir = out_dir / celex
    work_dir.mkdir(parents=True, exist_ok=True)

    url = BASE_URL.format(lang=lang.upper(), celex=celex)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport=VIEWPORT, user_agent=UA)
            page.goto(url, wait_until="networkidle", timeout=TIMEOUT_MS)

            page.screenshot(path=str(work_dir / "screenshot.png"))

            body_text = page.inner_text("body")

            # Sanity: czy to nie strona "Document not found" / "no results"
            if re.search(r"document\s+not\s+available|no\s+document\s+with\s+celex", body_text, re.I):
                sys.stderr.write(f"[fetch_eurlex] CELEX {celex} nie znaleziony w EUR-Lex.\n")
                return 1

            # Typ aktu (rozporzadzenie/dyrektywa/decyzja)
            typ = detect_typ(body_text)

            # Tytul aktu - opisowy w mixed case ("Rozporzadzenie Parlamentu Europejskiego i Rady ...
            # w sprawie ..."). Bierze pierwsze zdanie pasujace, zwykle najlepszy opis.
            tytul = ""
            tytul_match = re.search(
                r"(Rozporz\S*dzenie|Dyrektywa|Decyzja|Zalecenie|Opinia)\s+[A-Z][^\n]{40,500}",
                body_text,
            )
            if tytul_match:
                tytul = re.sub(r"\s+", " ", tytul_match.group(0)).strip()
            else:
                # fallback - upper-case header
                tytul_match = re.search(
                    r"(ROZPORZ\S*DZENIE|DYREKTYWA|DECYZJA|ZALECENIE|OPINIA)\s+[^\n]{20,400}",
                    body_text,
                )
                if tytul_match:
                    tytul = tytul_match.group(0).strip()

            # Data publikacji w Dz.U. - EUR-Lex pokazuje DD/MM/YYYY w header strony,
            # zwykle obok numeru "2024/1689". Bierzemy pierwsza date w body w formacie
            # DD/MM/YYYY (publikacja); data uchwalenia ("z dnia 13 czerwca 2024 r.")
            # jest osobno w tytule.
            data_iso = None
            data_match = re.search(r"\b(\d{1,2}/\d{1,2}/\d{4})\b", body_text)
            if data_match:
                data_iso = parse_date_pl(data_match.group(1))
            else:
                # fallback - format DD.M.YYYY (czesto w sekcji "Seria L ... 12.7.2024")
                data_match = re.search(
                    r"(Seria\s+[LC]|OJ\s+[LC])\s*[^\n]*?(\d{1,2}\.\d{1,2}\.\d{4})",
                    body_text,
                )
                if data_match:
                    data_iso = parse_date_pl(data_match.group(2))

            # Numer (np. 2024/1689)
            numer = None
            numer_match = re.search(r"\b(\d{4}/\d{1,5})\b", body_text)
            if numer_match:
                numer = numer_match.group(1)

            # ELI URI
            eli = None
            eli_match = re.search(r"(http://data\.europa\.eu/eli/[^\s,)]+)", body_text)
            if eli_match:
                eli = eli_match.group(1)

            # PDF link w naszym jezyku - EUR-Lex renderuje 20+ linkow PDF
            # (po jednym na jezyk UE), wiec musimy wybrac konkretny /{lang}/TXT/PDF/
            pdf_url = None
            pdf_el = page.query_selector(f'a[href*="/{lang.upper()}/TXT/PDF/"]')
            if pdf_el:
                href = pdf_el.get_attribute("href")
                if href:
                    if href.startswith("./"):
                        href = "/legal-content" + href.split("/legal-content")[-1]
                    if href.startswith("/"):
                        pdf_url = "https://eur-lex.europa.eu" + href
                    else:
                        pdf_url = href

            meta = {
                "celex": celex,
                "typ": typ,
                "numer": numer,
                "data_publikacji": data_iso,
                "jezyk": lang.upper(),
                "tytul": tytul[:300] if tytul else None,
                "url": url,
                "pdf_url": pdf_url,
                "eli": eli,
                "pobrano_at": now_iso(),
                "zrodlo": SOURCE,
            }

            (work_dir / "meta.json").write_text(
                json.dumps(meta, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            md = f"""# {celex} - {typ}

**Typ:** {typ}
**Numer:** {numer or '?'}
**Data publikacji:** {data_iso or '?'}
**Jezyk pobranego:** {lang.upper()}
**ELI:** {eli or 'brak'}
**URL HTML:** {url}
**URL PDF:** {pdf_url or 'brak'}
**Pobrano:** {meta['pobrano_at']}

---

**Tytul:**
{tytul or '(nie udalo sie sparsowac)'}

---

**Tresc (full body):**

{body_text}
"""
            (work_dir / "akt.md").write_text(md, encoding="utf-8")

            print(json.dumps(meta, ensure_ascii=False, indent=2))
            print(f"\n[OK] Zapisano: {work_dir}/")
            return 0

        except PWTimeoutError as e:
            sys.stderr.write(f"[fetch_eurlex] Timeout: {e}\n")
            return 2
        finally:
            browser.close()


def main():
    parser = argparse.ArgumentParser(
        description="Pobierz akt prawny EU z EUR-Lex po CELEX (komplementarny do eu-sparql-search)."
    )
    parser.add_argument(
        "--celex",
        required=True,
        help='np. "32024R1689" (AI Act) lub "32016R0679" (RODO)',
    )
    parser.add_argument(
        "--lang",
        default="PL",
        help="Kod jezyka 2-literowy (PL, EN, DE, FR, ...), domyslnie PL",
    )
    parser.add_argument(
        "--out",
        default="outputs/eurlex",
        help="Katalog docelowy (domyslnie outputs/eurlex/)",
    )
    args = parser.parse_args()

    out_dir = Path(args.out)
    sys.exit(fetch(args.celex, args.lang, out_dir))


if __name__ == "__main__":
    main()
