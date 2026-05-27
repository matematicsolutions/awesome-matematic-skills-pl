#!/usr/bin/env python3
"""
fetch_orzeczenie.py - pobiera orzeczenie Sadu Najwyzszego (sn.pl) po sygnaturze.

Wypelnia luke wzgledem mcp-saos (SAOS indeksuje wyroki SN do ~2016 nierowno -
po 2016 trzeba scrapowac sn.pl bezposrednio).

Output: outputs/orzeczenia/<slug>/orzeczenie.md + meta.json + screenshot.png

Wymagania:
  pip install playwright
  python -m playwright install chromium

Uzycie:
  python fetch_orzeczenie.py --sygnatura "I CSK 100/22"
  python fetch_orzeczenie.py --sygnatura "II CSK 50/23" --out outputs/custom

Kontrakt meta.json (zgodny z PATRON / citation-grounding-pl / legal-ai-audit-bundle):
  {
    "sygnatura": "I CSK 100/22",
    "sad": "Sad Najwyzszy",
    "data": "2023-MM-DD" lub null jezeli nie udalo sie sparsowac,
    "typ": "wyrok|postanowienie|uchwala|...",
    "url": "https://www.sn.pl/...",
    "pobrano_at": "2026-05-27T14:32:00Z",
    "zrodlo": "sn.pl/wyszukiwanie/SitePages/orzeczenia.aspx"
  }

Exit codes:
  0 = sukces (pobrano orzeczenie)
  1 = nie znaleziono orzeczenia o tej sygnaturze
  2 = blad polaczenia / timeout / inny blad krytyczny
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

SEARCH_URL = "https://www.sn.pl/orzecznictwo/SitePages/Baza_orzeczen.aspx"
SOURCE = "sn.pl/wyszukiwanie/SitePages/orzeczenia.aspx"
VIEWPORT = {"width": 1280, "height": 1800}
TIMEOUT_MS = 30_000


def slugify(sygnatura: str) -> str:
    """`I CSK 100/22` -> `i-csk-100-22`."""
    s = sygnatura.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch(sygnatura: str, out_dir: Path) -> int:
    slug = slugify(sygnatura)
    work_dir = out_dir / slug
    work_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport=VIEWPORT)
            page.goto(SEARCH_URL, wait_until="networkidle", timeout=TIMEOUT_MS)

            sygnatura_input = page.locator(
                'input[id$="_TextBoxSygnatura"]'
            ).first
            sygnatura_input.fill(sygnatura)

            page.screenshot(path=str(work_dir / "screenshot-form.png"))

            page.get_by_role("button", name=re.compile("Szukaj", re.I)).click()
            page.wait_for_load_state("networkidle", timeout=TIMEOUT_MS)

            body_text = page.inner_text("body")

            # SN format wyniku: "Znaleziono orzeczen: N"
            count_match = re.search(r"Znaleziono\s+orzecze\S*:\s*(\d+)", body_text)
            count = int(count_match.group(1)) if count_match else 0

            if count == 0:
                sys.stderr.write(
                    f"[fetch_orzeczenie] Nie znaleziono orzeczenia: {sygnatura}\n"
                )
                page.screenshot(path=str(work_dir / "screenshot-no-results.png"))
                return 1

            # Header wyniku: "I CSK 100/22\npostanowienie SN z dnia 18 marca 2022 r."
            header_re = (
                re.escape(sygnatura).replace(r"\ ", r"\s+")
                + r"\s*(wyrok|postanowienie|uchwala|zarzadzenie)\s+SN\s+z\s+dnia\s+(\d{1,2})\s+(\w+)\s+(\d{4})"
            )
            typ = "nieznane"
            data_iso = None
            polish_months = {
                "stycznia": 1, "lutego": 2, "marca": 3, "kwietnia": 4,
                "maja": 5, "czerwca": 6, "lipca": 7, "sierpnia": 8,
                "wrzesnia": 9, "września": 9,
                "pazdziernika": 10, "października": 10,
                "listopada": 11, "grudnia": 12,
            }
            hm = re.search(header_re, body_text, re.I)
            if hm:
                typ = hm.group(1).lower()
                day, month_pl, year = hm.group(2), hm.group(3).lower(), hm.group(4)
                month = polish_months.get(month_pl, 0)
                if month:
                    data_iso = f"{int(year):04d}-{month:02d}-{int(day):02d}"

            # Link do PDF z pelna trescia (jezeli istnieje) - to kanoniczne zrodlo
            pdf_link = page.locator('a[href*="/sites/orzecznictwo/"]').first
            pdf_url = pdf_link.get_attribute("href") if pdf_link.count() > 0 else None
            if pdf_url and pdf_url.startswith("/"):
                pdf_url = "https://www.sn.pl" + pdf_url

            # Link do detalu HTML (ItemSID) - krotka informacja o orzeczeniu
            detail_link = page.locator('a[href*="ItemSID"]').first
            detail_url = detail_link.get_attribute("href") if detail_link.count() > 0 else page.url
            if detail_url.startswith("/"):
                detail_url = "https://www.sn.pl" + detail_url

            page.screenshot(path=str(work_dir / "screenshot-results.png"))

            # Otworz strone detalu i wyciagnij content
            content_text = ""
            if detail_link.count() > 0:
                detail_link.click()
                page.wait_for_load_state("networkidle", timeout=TIMEOUT_MS)
                page.screenshot(path=str(work_dir / "screenshot-detail.png"))
                content_selectors = [
                    'div[id*="ContentPlaceHolder"]',
                    "main",
                    "article",
                    "body",
                ]
                for sel in content_selectors:
                    el = page.locator(sel).first
                    if el.count() > 0:
                        content_text = el.inner_text()
                        if len(content_text) > 200:
                            break

            meta = {
                "sygnatura": sygnatura,
                "sad": "Sad Najwyzszy",
                "data": data_iso,
                "typ": typ,
                "url": detail_url,
                "pdf_url": pdf_url,
                "pobrano_at": now_iso(),
                "zrodlo": SOURCE,
            }

            (work_dir / "meta.json").write_text(
                json.dumps(meta, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            md = f"""# {sygnatura}

**Sad:** Sad Najwyzszy
**Typ:** {typ}
**Data:** {data_iso or 'nie udalo sie sparsowac'}
**URL detalu:** {detail_url}
**URL PDF (pelna tresc):** {pdf_url or 'brak'}
**Pobrano:** {meta['pobrano_at']}

---

{content_text}
"""
            (work_dir / "orzeczenie.md").write_text(md, encoding="utf-8")

            print(json.dumps(meta, ensure_ascii=False, indent=2))
            print(f"\n[OK] Zapisano: {work_dir}/")
            return 0

        except PWTimeoutError as e:
            sys.stderr.write(f"[fetch_orzeczenie] Timeout: {e}\n")
            return 2
        finally:
            browser.close()


def main():
    parser = argparse.ArgumentParser(
        description="Pobierz orzeczenie SN po sygnaturze (wypelnia luke mcp-saos)."
    )
    parser.add_argument("--sygnatura", required=True, help='np. "I CSK 100/22"')
    parser.add_argument(
        "--out",
        default="outputs/orzeczenia",
        help="Katalog docelowy (domyslnie outputs/orzeczenia/)",
    )
    args = parser.parse_args()

    out_dir = Path(args.out)
    sys.exit(fetch(args.sygnatura, out_dir))


if __name__ == "__main__":
    main()
