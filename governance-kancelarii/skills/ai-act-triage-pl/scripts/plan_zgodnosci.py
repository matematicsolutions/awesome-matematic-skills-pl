#!/usr/bin/env python3
"""plan_zgodnosci.py - routing oceny zgodnosci (art. 43) + checklista zalacznika IV.

Fork MIT z alirezarezvani/claude-skills@eu-ai-act-specialist (autor: Alireza Rezvani).
Logika zachowana 1:1; output i cytaty na polska terminologie. Tylko stdlib.

Dla systemu wysokiego ryzyka wybiera modul oceny zgodnosci (A kontrola wewnetrzna vs
H pelny SZJ + jednostka notyfikowana) wg art. 43 i tworzy checkliste dokumentacji
technicznej z zalacznika IV.

Regula decyzyjna (art. 43):
  - Biometria (zalacznik III pkt 1) -> modul H (wymagana jednostka notyfikowana) domyslnie
  - Pozostale kategorie zalacznika III -> modul A (kontrola wewnetrzna) dopuszczalny
    tam, gdzie stosuje sie normy zharmonizowane (art. 40)
  - Produkty z zalacznika I (elementy bezpieczenstwa) -> procedura wg prawa sektorowego

Schemat wejscia (JSON):
{
  "system_name": "System przesiewowy CV",
  "annex_iii_category": "zatrudnienie",
  "applies_harmonised_standards": true,
  "harmonised_standards_referenced": ["EN ISO/IEC 42001", "EN ISO/IEC 23894"],
  "annex_i_product": false,
  "annex_i_sectoral_law": null,
  "existing_iso_42001_certification": false,
  "existing_iso_27001_certification": true
}

Uzycie:
    python plan_zgodnosci.py                  # wbudowana probka
    python plan_zgodnosci.py sciezka/do/system.json
    python plan_zgodnosci.py system.json --output json
"""

import argparse
import json
import sys
from typing import Any, Dict, List


BANNER = (
    "INTERPRETACJA MateMatic - narzedzie pomocnicze, NIE porada prawna. Wybor modulu "
    "i zakres zalacznika IV nalezy potwierdzic z prawnikiem i - dla modulu H - z "
    "jednostka notyfikowana."
)


SAMPLE: Dict[str, Any] = {
    "system_name": "System przesiewowy CV do rekrutacji",
    "annex_iii_category": "zatrudnienie",
    "applies_harmonised_standards": True,
    "harmonised_standards_referenced": ["EN ISO/IEC 42001", "EN ISO/IEC 23894"],
    "annex_i_product": False,
    "annex_i_sectoral_law": None,
    "existing_iso_42001_certification": False,
    "existing_iso_27001_certification": True,
}


# Zalacznik IV - wymagania dokumentacji technicznej (wg art. 11 ust. 1)
ANNEX_IV_ITEMS = [
    {
        "id": "iv.1",
        "title": "Ogolny opis systemu AI",
        "subitems": [
            "przeznaczenie",
            "nazwa i wersja dostawcy",
            "przeglad architektury systemu",
            "instrukcja obslugi (art. 13)",
        ],
        "reusable_from": "deklaracja zakresu ISO 42001; dokumentacja systemu ISO 27001",
    },
    {
        "id": "iv.2",
        "title": "Szczegolowy opis elementow systemu",
        "subitems": [
            "zastosowane metody (ML, regulowe itd.)",
            "zbiory treningowe/walidacyjne/testowe (pochodzenie + jakosc + ograniczanie stronniczosci wg art. 10)",
            "srodki nadzoru ze strony czlowieka (art. 14)",
            "kluczowe decyzje projektowe wraz z zalozeniami",
            "wykorzystane zasoby obliczeniowe",
        ],
        "reusable_from": "ISO 42001 A.6 dokumentacja cyklu zycia; ISO 42001 A.7 dowody dot. danych; karty modeli",
    },
    {
        "id": "iv.3",
        "title": "Informacje o monitorowaniu, funkcjonowaniu i kontroli",
        "subitems": [
            "metryki wydajnosci i oczekiwana dokladnosc",
            "zdolnosci rejestrowania zdarzen (art. 12)",
            "specyfikacja danych wejsciowych",
            "czlowiek w petli i nadzor (art. 14)",
        ],
        "reusable_from": "ISO 42001 A.9.3 monitorowanie; ISO 42001 A.9.4 rejestrowanie",
    },
    {
        "id": "iv.4",
        "title": "Opis systemu zarzadzania ryzykiem",
        "subitems": [
            "proces zarzadzania ryzykiem z art. 9",
            "zidentyfikowane ryzyka + srodki lagodzace",
            "akceptacja ryzyka rezydualnego",
            "metodyka testowania",
        ],
        "reusable_from": "ISO 42001 pkt 6.1 + zal. A.5 + zal. A.6.2.4; proces ISO 23894",
    },
    {
        "id": "iv.5",
        "title": "Opis zmian w systemie po wprowadzeniu do obrotu",
        "subitems": [
            "procedura zarzadzania zmiana",
            "kontrola wersji modelu + danych",
            "wyzwalacze ponownej oceny (dryft koncepcji, fine-tuning)",
        ],
        "reusable_from": "ISO 27001 A.8.32 zarzadzanie zmiana; ISO 42001 A.6.2.5 wdrozenie",
    },
    {
        "id": "iv.6",
        "title": "Wykaz zastosowanych norm zharmonizowanych",
        "subitems": [
            "domniemanie zgodnosci wg art. 40",
            "udokumentowane rozwiazania alternatywne tam, gdzie norm nie zastosowano",
        ],
        "reusable_from": "rejestr norm",
    },
    {
        "id": "iv.7",
        "title": "Deklaracja zgodnosci UE",
        "subitems": [
            "art. 47 - dostawca deklaruje zgodnosc, podpis osoby upowaznionej",
            "przechowywana 10 lat po wprowadzeniu do obrotu (art. 18)",
        ],
        "reusable_from": "tylko szablon - podpisywana na koncu procesu",
    },
    {
        "id": "iv.8",
        "title": "System monitorowania po wprowadzeniu do obrotu",
        "subitems": [
            "art. 72 - aktywne zbieranie danych o wydajnosci + incydentach",
            "procedura zglaszania poważnych incydentow (art. 73)",
            "petla zwrotna do zarzadzania ryzykiem (art. 9)",
        ],
        "reusable_from": "ISO 42001 A.9.3 monitorowanie + wzorzec nadzoru po wprowadzeniu do obrotu ISO 13485",
    },
]


def select_module(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Wybor modulu oceny zgodnosci wg art. 43."""
    annex_iii = payload.get("annex_iii_category")
    applies_standards = payload.get("applies_harmonised_standards", False)
    annex_i = payload.get("annex_i_product", False)
    sectoral_law = payload.get("annex_i_sectoral_law")

    if annex_i and sectoral_law:
        return {
            "module": "sektorowy",
            "citation": "art. 43 ust. 3 - produkt z zalacznika I podlega istniejacej procedurze sektorowej oceny zgodnosci",
            "notified_body_required": "zalezy_od_prawa_sektorowego",
            "rationale": f"Stosuj istniejaca procedure {sectoral_law}; AI Act nalozony na wierzch.",
        }

    if annex_iii == "biometria":
        return {
            "module": "H",
            "citation": "art. 43 ust. 1 + zalacznik VII - pelny SZJ + jednostka notyfikowana dla biometrii",
            "notified_body_required": "tak",
            "rationale": "Biometria wg zalacznika III pkt 1 wymaga domyslnie zaangazowania jednostki notyfikowanej.",
        }

    if annex_iii and applies_standards:
        return {
            "module": "A",
            "citation": "art. 43 ust. 2 + zalacznik VI - kontrola wewnetrzna z domniemaniem zgodnosci",
            "notified_body_required": "nie",
            "rationale": "System z zalacznika III stosujacy normy zharmonizowane (art. 40) moze uzyc kontroli wewnetrznej.",
        }

    if annex_iii and not applies_standards:
        return {
            "module": "A_z_zastrzezeniami",
            "citation": "art. 43 ust. 2 + zalacznik VI - kontrola wewnetrzna bez norm zharmonizowanych",
            "notified_body_required": "opcjonalna_ale_zalecana",
            "rationale": "Kontrola wewnetrzna nadal dopuszczalna, ale bez domniemania zgodnosci; udokumentuj w pelni alternatywne dowody zgodnosci.",
        }

    return {
        "module": "nie_dotyczy",
        "citation": "System nie sklasyfikowany jako wysokiego ryzyka; ocena zgodnosci nie jest wymagana",
        "notified_body_required": "nie",
        "rationale": "Uruchom ponownie klasyfikator_ryzyka_ai.py, aby potwierdzic poziom.",
    }


def reuse_summary(payload: Dict[str, Any]) -> List[str]:
    """Jakie dowody mozna ponownie wykorzystac z istniejacych certyfikacji."""
    notes = []
    if payload.get("existing_iso_42001_certification"):
        notes.append("Certyfikat ISO 42001: wykorzystaj dowody ryzyka z pkt 6.1 SZAI (zalacznik IV poz. 4)")
        notes.append("Certyfikat ISO 42001: wykorzystaj dowody cyklu zycia z zal. A.6 (zalacznik IV poz. 1-3)")
        notes.append("Certyfikat ISO 42001: wykorzystaj dowody monitorowania z zal. A.9 (zalacznik IV poz. 8)")
    if payload.get("existing_iso_27001_certification"):
        notes.append("Certyfikat ISO 27001: wykorzystaj dowody cyberbezpieczenstwa dla wymogu z art. 15")
        notes.append("Certyfikat ISO 27001: wykorzystaj A.5.19 zarzadzanie dostawcami dla odpowiedzialnosci w lancuchu wartosci (art. 25)")
        notes.append("Certyfikat ISO 27001: wykorzystaj A.8.15 rejestrowanie dla zalacznika IV poz. 3")
    if not notes:
        notes.append("Nie zadeklarowano wczesniejszych certyfikacji; zbuduj cala dokumentacje zalacznika IV od zera")
    return notes


def plan(payload: Dict[str, Any]) -> Dict[str, Any]:
    module = select_module(payload)
    return {
        "system_name": payload.get("system_name"),
        "annex_iii_category": payload.get("annex_iii_category"),
        "conformity_assessment": module,
        "annex_iv_checklist": ANNEX_IV_ITEMS,
        "reuse_from_existing_certifications": reuse_summary(payload),
        "next_steps": _next_steps(module["module"]),
    }


def _next_steps(module: str) -> List[str]:
    base = [
        "Skompletuj pakiet zalacznika IV wg checklisty (art. 11 + zalacznik IV).",
        "Przeprowadz cykl zarzadzania ryzykiem z art. 9 (wejscie do zalacznika IV poz. 4).",
        "Wdroz rejestrowanie zdarzen z art. 12 (wejscie do zalacznika IV poz. 3).",
        "Wdroz srodki nadzoru czlowieka z art. 14 (wejscie do zalacznika IV poz. 2-3).",
        "Uruchom monitorowanie po wprowadzeniu do obrotu z art. 72 (wejscie do zalacznika IV poz. 8).",
    ]
    if module == "H":
        base.append("Zaangazuj jednostke notyfikowana do oceny w module H (zalacznik VII).")
        base.append("Prowadz pelny SZJ wg art. 17 - sparuj z SZAI ISO 42001 dla wzajemnego wykorzystania dowodow.")
    elif module == "A":
        base.append("Zweryfikuj, ze kazda przywolana norma zharmonizowana jest na liscie z art. 40 na dzien decyzji.")
        base.append("Podpisz deklaracje zgodnosci UE (art. 47) PO skompletowaniu pakietu zalacznika IV.")
        base.append("Umiesc oznakowanie CE (art. 48).")
        base.append("Zarejestruj w bazie UE (art. 71) przed wprowadzeniem do obrotu.")
    elif module == "A_z_zastrzezeniami":
        base.append("Udokumentuj rownowazny dowod alternatywny dla kazdego wymogu bez normy zharmonizowanej.")
        base.append("Rozwaz dobrowolne zaangazowanie jednostki notyfikowanej dla zmniejszenia ryzyka regulacyjnego.")
    return base


def render_text(p: Dict[str, Any], source: str) -> str:
    lines = []
    lines.append("=" * 72)
    lines.append("AI ACT - PLAN OCENY ZGODNOSCI")
    lines.append(f"Zrodlo: {source}")
    lines.append("=" * 72)
    lines.append("")
    lines.append(f"System: {p['system_name']}")
    lines.append(f"Kategoria zalacznika III: {p['annex_iii_category']}")
    lines.append("")
    c = p["conformity_assessment"]
    lines.append(f"Modul zgodnosci: {c['module']}")
    lines.append(f"Podstawa: {c['citation']}")
    lines.append(f"Jednostka notyfikowana wymagana: {c['notified_body_required']}")
    lines.append(f"Uzasadnienie: {c['rationale']}")
    lines.append("")
    lines.append("-" * 72)
    lines.append("CHECKLISTA DOKUMENTACJI TECHNICZNEJ - ZALACZNIK IV (8 pozycji):")
    lines.append("")

    for item in p["annex_iv_checklist"]:
        lines.append(f"  [{item['id']}] {item['title']}")
        for sub in item["subitems"]:
            lines.append(f"        - {sub}")
        lines.append(f"        Do wykorzystania: {item['reusable_from']}")
        lines.append("")

    lines.append("-" * 72)
    lines.append("DO WYKORZYSTANIA Z ISTNIEJACYCH CERTYFIKACJI:")
    for note in p["reuse_from_existing_certifications"]:
        lines.append(f"  - {note}")
    lines.append("")

    lines.append("-" * 72)
    lines.append("NASTEPNE KROKI:")
    for step in p["next_steps"]:
        lines.append(f"  - {step}")
    lines.append("")
    lines.append("-" * 72)
    lines.append(BANNER)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Routing oceny zgodnosci AI Act (art. 43) + checklista dokumentacji technicznej zalacznika IV.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("path", nargs="?", help="Sciezka do JSON systemu (uzywa wbudowanej probki gdy pominieta)")
    parser.add_argument("--output", choices=("text", "json"), default="text", help="Format wyjscia")
    args = parser.parse_args()

    if args.path:
        try:
            with open(args.path, "r", encoding="utf-8") as f:
                payload = json.load(f)
            source = args.path
        except (IOError, OSError) as e:
            print(f"blad: nie mozna odczytac {args.path}: {e}", file=sys.stderr)
            return 1
        except json.JSONDecodeError as e:
            print(f"blad: niepoprawny JSON w {args.path}: {e}", file=sys.stderr)
            return 1
    else:
        payload = SAMPLE
        source = "<wbudowana probka: system przesiewowy CV, stosowane normy zharmonizowane>"

    result = plan(payload)
    if args.output == "json":
        print(json.dumps({"source": source, "disclaimer": BANNER, **result}, indent=2, ensure_ascii=False))
    else:
        print(render_text(result, source))
    return 0


if __name__ == "__main__":
    sys.exit(main())
