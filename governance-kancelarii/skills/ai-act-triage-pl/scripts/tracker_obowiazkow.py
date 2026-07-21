#!/usr/bin/env python3
"""tracker_obowiazkow.py - macierz obowiazkow AI Act wg roli.

Fork MIT z alirezarezvani/claude-skills@eu-ai-act-specialist (autor: Alireza Rezvani).
Logika zachowana 1:1; output, obowiazki i cytaty na polska terminologie. Tylko stdlib.

Dla roli/rol organizacji wg art. 25 (dostawca, podmiot stosujacy, importer,
dystrybutor, upowazniony przedstawiciel) oraz poziomu/-ow systemu produkuje
macierz obowiazkow posortowana wg terminow, powiazana z fazowym stosowaniem aktu:
  - 2 lut 2025: zakazy z art. 5 + kompetencje AI z art. 4
  - 2 sie 2025: GPAI art. 51-55 + zarzadzanie + kary
  - 2 sie 2026: obowiazki wysokiego ryzyka z tytulu III
  - 2 sie 2027: obowiazki wysokiego ryzyka wg zalacznika I (sektorowe)

Deterministyczna logika odwolujaca sie do art. 16, 22, 23, 24, 25, 26, 27, 50,
51-55, 72, 73 + fazowanie wg art. 113.

Schemat wejscia (JSON):
{
  "organization": "Acme AI sp. z o.o.",
  "establishment": "poza_ue",          # ue | poza_ue
  "roles": [
    {"role": "dostawca", "systems_tier": "wysokie_ryzyko"},
    {"role": "podmiot_stosujacy", "systems_tier": "wysokie_ryzyko", "public_sector": false},
    {"role": "podmiot_stosujacy", "systems_tier": "ograniczone_ryzyko"}
  ],
  "deploys_gpai": true,
  "gpai_systemic_risk": false
}

Uzycie:
    python tracker_obowiazkow.py
    python tracker_obowiazkow.py sciezka/do/roles.json
    python tracker_obowiazkow.py roles.json --output json
"""

import argparse
import json
import sys
from typing import Any, Dict, List


BANNER = (
    "INTERPRETACJA MateMatic - narzedzie pomocnicze, NIE porada prawna. Terminy i "
    "obowiazki zaleza od statusu wejscia w zycie i ewentualnej polskiej ustawy "
    "wdrozeniowej - zweryfikuj aktualny stan przed dzialaniem."
)


SAMPLE: Dict[str, Any] = {
    "organization": "Acme AI sp. z o.o.",
    "establishment": "poza_ue",
    "roles": [
        {"role": "dostawca", "systems_tier": "wysokie_ryzyko"},
        {"role": "podmiot_stosujacy", "systems_tier": "wysokie_ryzyko", "public_sector": False},
        {"role": "podmiot_stosujacy", "systems_tier": "ograniczone_ryzyko"},
    ],
    "deploys_gpai": True,
    "gpai_systemic_risk": False,
}


# Fazowanie (wg art. 113)
PHASE_DATES = {
    "zakazy_art_5": "2025-02-02",
    "kompetencje_ai_art_4": "2025-02-02",
    "gpai_art_51_55": "2025-08-02",
    "zarzadzanie_kary": "2025-08-02",
    "tytul_iii_wysokie_ryzyko_ogolne": "2026-08-02",
    "tytul_iii_zalacznik_i_sektorowe": "2027-08-02",
}


# Obowiazki wg roli + poziomu
PROVIDER_HIGH_RISK = [
    ("art. 9 - ustanowienie systemu zarzadzania ryzykiem w calym cyklu zycia AI", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 10 - zarzadzanie danymi: jakosc danych treningowych/walidacyjnych/testowych + ograniczanie stronniczosci", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 11 - prowadzenie dokumentacji technicznej wg zalacznika IV", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 12 - wdrozenie automatycznego rejestrowania zdarzen", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 13 - dostarczenie instrukcji obslugi podmiotom stosujacym", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 14 - projekt umozliwiajacy nadzor ze strony czlowieka", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 15 - dokladnosc, solidnosc, cyberbezpieczenstwo", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 16 - ogolne obowiazki dostawcy + wyznaczona osoba kontaktowa", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 17 - ustanowienie systemu zarzadzania jakoscia (SZJ)", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 43 - przeprowadzenie oceny zgodnosci przed wprowadzeniem do obrotu", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 47 - podpisanie deklaracji zgodnosci UE (przechowywanie 10 lat wg art. 18)", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 48 - umieszczenie oznakowania CE", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 49 - rejestracja w bazie UE (art. 71) dla systemow z zalacznika III", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 72 - ustanowienie systemu monitorowania po wprowadzeniu do obrotu", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 73 - zglaszanie powaznych incydentow organowi nadzoru rynku w ciagu 15 dni (lub 2 dni przy incydentach infrastruktury krytycznej)", "tytul_iii_wysokie_ryzyko_ogolne"),
]

DEPLOYER_HIGH_RISK = [
    ("art. 26 ust. 1 - stosowanie systemu AI zgodnie z instrukcja obslugi dostawcy", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 26 ust. 2 - powierzenie nadzoru osobom fizycznym o odpowiednich kompetencjach + uprawnieniach + wsparciu", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 26 ust. 3 - zapewnienie, ze dane wejsciowe sa istotne + wystarczajaco reprezentatywne", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 26 ust. 4 - monitorowanie dzialania; wstrzymanie stosowania gdy wystepuje ryzyko wg art. 79", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 26 ust. 5 - przechowywanie automatycznie generowanych rejestrow (art. 12) przez >= 6 miesiecy", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 26 ust. 7 - poinformowanie pracownikow + ich przedstawicieli przed wdrozeniem systemu w miejscu pracy", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 26 ust. 8 - wspolpraca z wlasciwymi organami krajowymi + Urzedem ds. AI", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 50 - poinformowanie osob fizycznych podlegajacych decyzjom AI (transparentnosc)", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 86 - prawo do wyjasnienia indywidualnej decyzji", "tytul_iii_wysokie_ryzyko_ogolne"),
]

DEPLOYER_PUBLIC_SECTOR = [
    ("art. 27 - przeprowadzenie oceny wplywu na prawa podstawowe (OWPP/FRIA) przed wdrozeniem", "tytul_iii_wysokie_ryzyko_ogolne"),
]

DEPLOYER_LIMITED_RISK = [
    ("art. 50 ust. 1 - poinformowanie osob fizycznych, ze wchodza w interakcje z systemem AI", "zarzadzanie_kary"),
    ("art. 50 ust. 4 - oznaczenie deepfake (obraz, audio, wideo) jako wygenerowanych przez AI; oznaczenie maszynowo-odczytywalne", "zarzadzanie_kary"),
]

IMPORTER = [
    ("art. 23 - weryfikacja, ze dostawca przeprowadzil ocene zgodnosci + posiada dokumentacje techniczna", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 23 ust. 3 - wskazanie nazwy, kontaktu, adresu na systemie AI lub dokumentacji towarzyszacej", "tytul_iii_wysokie_ryzyko_ogolne"),
]

DISTRIBUTOR = [
    ("art. 24 - weryfikacja oznakowania CE + dokumentacji przed udostepnieniem systemu", "tytul_iii_wysokie_ryzyko_ogolne"),
]

AUTH_REP_NON_EU_PROVIDER = [
    ("art. 22 - dostawcy spoza UE MUSZA wyznaczyc upowaznionego przedstawiciela z siedziba w UE", "tytul_iii_wysokie_ryzyko_ogolne"),
    ("art. 22 ust. 3 - przedstawiciel przechowuje dokumentacje techniczna + odpowiada za obowiazki dostawcy", "tytul_iii_wysokie_ryzyko_ogolne"),
]

GPAI_ALL = [
    ("art. 53 - prowadzenie aktualnej dokumentacji technicznej modelu GPAI", "gpai_art_51_55"),
    ("art. 53 - dostarczanie informacji dostawcom nizszego szczebla integrujacym model", "gpai_art_51_55"),
    ("art. 53 ust. 1 lit. c) - ustanowienie polityki zgodnosci z prawem autorskim UE", "gpai_art_51_55"),
    ("art. 53 ust. 1 lit. d) - publikacja szczegolowego streszczenia dot. danych treningowych", "gpai_art_51_55"),
]

GPAI_SYSTEMIC_RISK = [
    ("art. 55 - przeprowadzanie ocen modelu, w tym testow kontradyktoryjnych", "gpai_art_51_55"),
    ("art. 55 - ocena + lagodzenie ryzyk systemowych", "gpai_art_51_55"),
    ("art. 55 - sledzenie + zglaszanie powaznych incydentow Urzedowi ds. AI", "gpai_art_51_55"),
    ("art. 55 - zapewnienie ochrony cyberbezpieczenstwa modelu + infrastruktury fizycznej", "gpai_art_51_55"),
]

UNIVERSAL = [
    ("art. 4 - zapewnienie kompetencji w zakresie AI personelowi majacemu do czynienia z systemami AI", "kompetencje_ai_art_4"),
    ("art. 5 - brak zakazanych praktyk AI", "zakazy_art_5"),
]


def _make_obs(items: List[tuple], role_label: str) -> List[Dict[str, Any]]:
    return [{"role": role_label, "obligation": ob, "deadline_phase": phase,
             "deadline_date": PHASE_DATES[phase]} for ob, phase in items]


def _role_obligations(role: Dict[str, Any]) -> List[Dict[str, Any]]:
    r_type = role.get("role")
    tier = role.get("systems_tier")
    if r_type == "dostawca" and tier == "wysokie_ryzyko":
        return _make_obs(PROVIDER_HIGH_RISK, "dostawca/wysokie-ryzyko")
    if r_type == "podmiot_stosujacy" and tier == "wysokie_ryzyko":
        out = _make_obs(DEPLOYER_HIGH_RISK, "podmiot-stosujacy/wysokie-ryzyko")
        if role.get("public_sector"):
            out += _make_obs(DEPLOYER_PUBLIC_SECTOR, "podmiot-stosujacy/sektor-publiczny")
        return out
    if r_type == "podmiot_stosujacy" and tier == "ograniczone_ryzyko":
        return _make_obs(DEPLOYER_LIMITED_RISK, "podmiot-stosujacy/ograniczone-ryzyko")
    if r_type == "importer":
        return _make_obs(IMPORTER, "importer")
    if r_type == "dystrybutor":
        return _make_obs(DISTRIBUTOR, "dystrybutor")
    return []


def gather_obligations(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    obligations: List[Dict[str, Any]] = []
    obligations += _make_obs(UNIVERSAL, "kazdy")

    roles = payload.get("roles", [])
    for role in roles:
        obligations += _role_obligations(role)

    if payload.get("establishment") == "poza_ue":
        provider_role = any(r.get("role") == "dostawca" for r in roles)
        if provider_role:
            obligations += _make_obs(AUTH_REP_NON_EU_PROVIDER, "dostawca-spoza-UE")

    if payload.get("deploys_gpai"):
        obligations += _make_obs(GPAI_ALL, "dostawca-GPAI")
        if payload.get("gpai_systemic_risk"):
            obligations += _make_obs(GPAI_SYSTEMIC_RISK, "GPAI-ryzyko-systemowe")

    obligations.sort(key=lambda x: (x["deadline_date"], x["role"]))
    return obligations


def analyze(payload: Dict[str, Any]) -> Dict[str, Any]:
    obs = gather_obligations(payload)
    by_phase: Dict[str, int] = {}
    by_role: Dict[str, int] = {}
    for o in obs:
        by_phase[o["deadline_phase"]] = by_phase.get(o["deadline_phase"], 0) + 1
        by_role[o["role"]] = by_role.get(o["role"], 0) + 1
    return {
        "organization": payload.get("organization"),
        "establishment": payload.get("establishment"),
        "total_obligations": len(obs),
        "by_phase": by_phase,
        "by_role": by_role,
        "obligations": obs,
    }


def render_text(r: Dict[str, Any], source: str) -> str:
    lines = []
    lines.append("=" * 72)
    lines.append("AI ACT - MACIERZ OBOWIAZKOW (sortowana wg terminow)")
    lines.append(f"Zrodlo: {source}")
    lines.append("=" * 72)
    lines.append("")
    lines.append(f"Organizacja: {r['organization']}")
    lines.append(f"Siedziba: {r['establishment']}")
    lines.append(f"Obowiazkow lacznie: {r['total_obligations']}")
    lines.append("")
    lines.append("Wg fazy terminu:")
    for phase, n in sorted(r["by_phase"].items(), key=lambda x: PHASE_DATES.get(x[0], "")):
        lines.append(f"  {PHASE_DATES.get(phase, '?')}  {phase:38s}  {n} obowiazkow")
    lines.append("")
    lines.append("Wg roli:")
    for role, n in sorted(r["by_role"].items()):
        lines.append(f"  {role:34s}  {n} obowiazkow")
    lines.append("")
    lines.append("-" * 72)
    lines.append("PELNA LISTA (kolejnosc wg terminow):")
    lines.append("")
    current_date = None
    for o in r["obligations"]:
        if o["deadline_date"] != current_date:
            current_date = o["deadline_date"]
            lines.append(f"  >> Termin {current_date} - {o['deadline_phase']}")
        lines.append(f"     [{o['role']:30s}] {o['obligation']}")
    lines.append("")
    lines.append("-" * 72)
    lines.append("FAZOWANIE (art. 113):")
    lines.append("  2025-02-02: zakazy z art. 5 + kompetencje AI z art. 4")
    lines.append("  2025-08-02: GPAI (art. 51-55) + zarzadzanie + kary")
    lines.append("  2026-08-02: tytul III wysokie ryzyko (ogolne)")
    lines.append("  2027-08-02: zalacznik I sektorowe wysokie ryzyko")
    lines.append("")
    lines.append("-" * 72)
    lines.append(BANNER)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Macierz obowiazkow AI Act wg roli z terminami fazowania.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("path", nargs="?", help="Sciezka do JSON rol (uzywa wbudowanej probki gdy pominieta)")
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
        source = "<wbudowana probka: dostawca spoza UE + podmiot stosujacy wysokie ryzyko + GPAI>"

    result = analyze(payload)
    if args.output == "json":
        print(json.dumps({"source": source, "disclaimer": BANNER, **result}, indent=2, ensure_ascii=False))
    else:
        print(render_text(result, source))
    return 0


if __name__ == "__main__":
    sys.exit(main())
