#!/usr/bin/env python3
"""klasyfikator_ryzyka_ai.py - klasyfikator poziomu ryzyka wg AI Act (Rozp. UE 2024/1689).

Fork MIT z alirezarezvani/claude-skills@eu-ai-act-specialist (autor: Alireza Rezvani).
Logika drzewa decyzyjnego zachowana 1:1; output, komentarze i cytaty przeniesione na
polska terminologie Rozporzadzenia. Tylko biblioteka standardowa (zero zaleznosci).

Klasyfikuje kazdy system AI do jednego z czterech poziomow:
  - zakazany           (art. 5)
  - wysokiego ryzyka   (art. 6 + zalacznik III, ALBO art. 6 ust. 1 + zalacznik I)
  - ograniczonego ryzyka / transparentnosc (art. 50)
  - minimalnego ryzyka (domyslnie)

Deterministyczne drzewo zgodne z architektura opartą na ryzyku (motyw 26 +
art. 5, 6, 50). Wyjatki z art. 6 ust. 3 zastosowane.

Schemat wejscia (JSON):
{
  "systems": [
    {
      "name": "System przesiewowy CV",
      "intended_purpose": "Filtrowanie i ranking kandydatow do rekrutacji",
      "users": "wewnetrzny_hr",
      "data_processes_natural_persons": true,
      "annex_iii_category": "zatrudnienie",
      "performs_profiling": true,
      "article_5_practice": null,
      "article_6_1_safety_component": false,
      "article_6_3_carveout_applies": false,
      "interacts_with_natural_persons_directly": false,
      "is_general_purpose_ai_model": false,
      "training_compute_flops": null
    }
  ]
}

Uwaga o `article_5_practice`: ta flaga to prawna preddecyzja wywolujacego, ze
wymieniona w art. 5 praktyka wystepuje W SWOIM ZAKAZANYM KONTEKSCIE - klasyfikator
jej ufa i nie wyprowadza jej ponownie z pozostalych pol. Kontekst ma znaczenie:
rozpoznawanie emocji jest zakazane wg art. 5 ust. 1 lit. f) TYLKO w miejscu pracy
i instytucjach edukacyjnych (poza waskimi wyjatkami bezpieczenstwa/medycznymi);
ten sam system np. w handlu detalicznym NIE jest zakazany - podlega transparentnosci
z art. 50 ust. 3 i moze byc wysokiego ryzyka wg zalacznika III pkt 1 (biometria).

Uzycie:
    python klasyfikator_ryzyka_ai.py                       # wbudowana probka 5 systemow
    python klasyfikator_ryzyka_ai.py sciezka/do/systems.json
    python klasyfikator_ryzyka_ai.py systems.json --output json
"""

import argparse
import json
import sys
from typing import Any, Dict, List, Optional


BANNER = (
    "INTERPRETACJA MateMatic - narzedzie pomocnicze, NIE porada prawna ani wiazaca "
    "opinia. Rozporzadzenie 2024/1689 jest aktem wiazacym; przy sprawach spornych "
    "(czy to model GPAI? czy stosuje sie wyjatek z art. 6 ust. 3? czy fine-tuning to "
    "istotna modyfikacja?) angazuj wykwalifikowanego prawnika."
)


SAMPLE: Dict[str, Any] = {
    "systems": [
        {
            # Art. 5 ust. 1 lit. f) zakazuje rozpoznawania emocji TYLKO w MIEJSCU PRACY
            # i EDUKACJI (poza waskimi wyjatkami bezpieczenstwa/medycznymi). Ten sam
            # system skierowany do klientow SKLEPU nie jest zakazany - podpada pod
            # transparentnosc z art. 50 ust. 3 (ograniczone ryzyko) i moze byc wysokiego
            # ryzyka wg zalacznika III pkt 1 (biometria). Probka uzywa realnego kontekstu
            # pracowniczego, wiec znacznik "zakazany" jest poprawny.
            "name": "Rozpoznawanie emocji pracownikow w CCTV w miejscu pracy",
            "intended_purpose": "Monitorowanie stanu emocjonalnego pracownikow dla oceny zaangazowania",
            "users": "menedzerowie_hr",
            "data_processes_natural_persons": True,
            "annex_iii_category": None,
            "performs_profiling": False,
            "article_5_practice": "rozpoznawanie_emocji_praca_lub_edukacja",
            "article_6_1_safety_component": False,
            "article_6_3_carveout_applies": False,
            "interacts_with_natural_persons_directly": False,
            "is_general_purpose_ai_model": False,
            "training_compute_flops": None,
        },
        {
            "name": "System przesiewowy CV do rekrutacji",
            "intended_purpose": "Filtrowanie i ranking kandydatow do krotkiej listy",
            "users": "wewnetrzny_hr",
            "data_processes_natural_persons": True,
            "annex_iii_category": "zatrudnienie",
            "performs_profiling": True,
            "article_5_practice": None,
            "article_6_1_safety_component": False,
            "article_6_3_carveout_applies": False,
            "interacts_with_natural_persons_directly": False,
            "is_general_purpose_ai_model": False,
            "training_compute_flops": None,
        },
        {
            "name": "Chatbot obslugi klienta",
            "intended_purpose": "Odpowiadanie na pytania wsparcia; przekazywanie do konsultanta",
            "users": "klienci",
            "data_processes_natural_persons": True,
            "annex_iii_category": None,
            "performs_profiling": False,
            "article_5_practice": None,
            "article_6_1_safety_component": False,
            "article_6_3_carveout_applies": False,
            "interacts_with_natural_persons_directly": True,
            "is_general_purpose_ai_model": False,
            "training_compute_flops": None,
        },
        {
            "name": "Filtr antyspamowy poczty",
            "intended_purpose": "Klasyfikacja poczty przychodzacej jako spam / nie-spam",
            "users": "wszyscy_pracownicy",
            "data_processes_natural_persons": False,
            "annex_iii_category": None,
            "performs_profiling": False,
            "article_5_practice": None,
            "article_6_1_safety_component": False,
            "article_6_3_carveout_applies": False,
            "interacts_with_natural_persons_directly": False,
            "is_general_purpose_ai_model": False,
            "training_compute_flops": None,
        },
        {
            "name": "Model fundamentowy udostepniany przez API",
            "intended_purpose": "Generowanie tekstu ogolnego przeznaczenia",
            "users": "deweloperzy",
            "data_processes_natural_persons": True,
            "annex_iii_category": None,
            "performs_profiling": False,
            "article_5_practice": None,
            "article_6_1_safety_component": False,
            "article_6_3_carveout_applies": False,
            "interacts_with_natural_persons_directly": False,
            "is_general_purpose_ai_model": True,
            "training_compute_flops": 5e25,
        },
    ]
}


# Zakazane praktyki z art. 5 (wg wiazacego tekstu Rozporzadzenia)
ARTICLE_5_PRACTICES = {
    "techniki_podprogowe": "art. 5 ust. 1 lit. a) - techniki podprogowe poza swiadomoscia wyrzadzajace szkode",
    "wykorzystanie_slabosci": "art. 5 ust. 1 lit. b) - wykorzystanie slabosci ze wzgledu na wiek/niepelnosprawnosc/sytuacje spoleczno-ekonomiczna",
    "scoring_spoleczny": "art. 5 ust. 1 lit. c) - scoring spoleczny prowadzacy do krzywdzacego traktowania",
    "predykcyjne_dzialania_policji": "art. 5 ust. 1 lit. d) - ocena ryzyka popelnienia przestepstwa wylacznie na podstawie profilowania",
    "nieukierunkowane_pobieranie_wizerunkow": "art. 5 ust. 1 lit. e) - nieukierunkowane pozyskiwanie wizerunkow twarzy do baz rozpoznawania",
    "rozpoznawanie_emocji_praca_lub_edukacja": "art. 5 ust. 1 lit. f) - rozpoznawanie emocji w miejscu pracy i instytucjach edukacyjnych",
    "kategoryzacja_biometryczna_wrazliwa": "art. 5 ust. 1 lit. g) - kategoryzacja biometryczna wg cech wrazliwych",
    "zdalna_identyfikacja_biometryczna_rzeczywista_organy": "art. 5 ust. 1 lit. h) - zdalna identyfikacja biometryczna w czasie rzeczywistym w przestrzeni publicznej przez organy scigania",
}

# Kategorie wysokiego ryzyka z zalacznika III (8 - art. 6 ust. 2)
ANNEX_III_CATEGORIES = {
    "biometria": "zalacznik III pkt 1 - biometria, w tym identyfikacja i kategoryzacja biometryczna",
    "infrastruktura_krytyczna": "zalacznik III pkt 2 - infrastruktura krytyczna (elementy bezpieczenstwa)",
    "edukacja": "zalacznik III pkt 3 - ksztalcenie i szkolenie zawodowe",
    "zatrudnienie": "zalacznik III pkt 4 - zatrudnienie, zarzadzanie pracownikami, dostep do samozatrudnienia",
    "uslugi_podstawowe": "zalacznik III pkt 5 - dostep do podstawowych uslug prywatnych/publicznych i swiadczen (w tym scoring kredytowy, dyspozytornia ratunkowa, wycena ubezpieczen)",
    "organy_scigania": "zalacznik III pkt 6 - organy scigania",
    "migracja_azyl": "zalacznik III pkt 7 - migracja, azyl, kontrola graniczna",
    "wymiar_sprawiedliwosci": "zalacznik III pkt 8 - sprawowanie wymiaru sprawiedliwosci i procesy demokratyczne",
}


def classify(system: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministyczna klasyfikacja wg art. 5, 6, 50 + zalacznik III."""
    name = system.get("name", "<bez nazwy>")
    article_5 = system.get("article_5_practice")
    annex_iii = system.get("annex_iii_category")
    safety_component = system.get("article_6_1_safety_component", False)
    carveout = system.get("article_6_3_carveout_applies", False)
    profiling = system.get("performs_profiling", False)
    interacts = system.get("interacts_with_natural_persons_directly", False)
    is_gpai = system.get("is_general_purpose_ai_model", False)
    flops = system.get("training_compute_flops")

    # Krok 1: zakazy z art. 5 (binarne, bez wyjatkow)
    if article_5 and article_5 in ARTICLE_5_PRACTICES:
        return {
            "name": name,
            "tier": "zakazany",
            "primary_citation": ARTICLE_5_PRACTICES[article_5],
            "rationale": "Wymieniona praktyka z art. 5. Nie moze byc wprowadzona do obrotu ani stosowana w UE (kara do 35 mln EUR / 7% obrotu).",
            "is_gpai": is_gpai,
            "gpai_systemic_risk": False,
        }

    # Krok 2: art. 6 ust. 1 - element bezpieczenstwa produktu regulowanego wg zalacznika I
    if safety_component:
        return {
            "name": name,
            "tier": "wysokie_ryzyko",
            "primary_citation": "art. 6 ust. 1 - element bezpieczenstwa produktu z zalacznika I",
            "rationale": "Element bezpieczenstwa podlegajacy ocenie zgodnosci przez strone trzecia wg prawa sektorowego (zalacznik I).",
            "is_gpai": is_gpai,
            "gpai_systemic_risk": False,
        }

    # Krok 3: art. 6 ust. 2 + zalacznik III - wysokie ryzyko wg kategorii
    if annex_iii and annex_iii in ANNEX_III_CATEGORIES:
        # Sprawdzenie wyjatku z art. 6 ust. 3
        if carveout and not profiling:
            # Wyjatek stosuje sie ORAZ brak profilowania - spada do ograniczonego lub minimalnego
            tier = "ograniczone_ryzyko" if interacts else "minimalne_ryzyko"
            return {
                "name": name,
                "tier": tier,
                "primary_citation": "art. 6 ust. 3 - wyjatek od zalacznika III: waskie zadanie proceduralne / przygotowawcze / usprawnienie wyniku pracy czlowieka",
                "rationale": "Kategoria zalacznika III wystapila, ale stosuje sie wyjatek z art. 6 ust. 3 i brak profilowania.",
                "is_gpai": is_gpai,
                "gpai_systemic_risk": False,
            }
        if carveout and profiling:
            # Profilowanie znosi wyjatek - art. 6 ust. 3 zdanie ostatnie
            return {
                "name": name,
                "tier": "wysokie_ryzyko",
                "primary_citation": f"art. 6 ust. 2 + {ANNEX_III_CATEGORIES[annex_iii]}",
                "rationale": "Podniesiono wyjatek, ale profilowanie osob fizycznych utrzymuje wysokie ryzyko wg art. 6 ust. 3 zdanie ostatnie.",
                "is_gpai": is_gpai,
                "gpai_systemic_risk": False,
            }
        return {
            "name": name,
            "tier": "wysokie_ryzyko",
            "primary_citation": f"art. 6 ust. 2 + {ANNEX_III_CATEGORIES[annex_iii]}",
            "rationale": "Miesci sie w kategorii wysokiego ryzyka z zalacznika III; nie zastosowano wyjatku z art. 6 ust. 3.",
            "is_gpai": is_gpai,
            "gpai_systemic_risk": False,
        }

    # Krok 4: transparentnosc z art. 50 (ograniczone ryzyko)
    if interacts:
        return {
            "name": name,
            "tier": "ograniczone_ryzyko",
            "primary_citation": "art. 50 ust. 1 - transparentnosc systemow AI wchodzacych w interakcje z osobami fizycznymi",
            "rationale": "Bezposrednia interakcja z osobami fizycznymi wymaga poinformowania, ze maja do czynienia z AI.",
            "is_gpai": is_gpai,
            "gpai_systemic_risk": _gpai_systemic_risk(is_gpai, flops),
        }

    # Krok 5: domyslnie - minimalne ryzyko
    return {
        "name": name,
        "tier": "minimalne_ryzyko",
        "primary_citation": "brak przeslanki z art. 5, zalacznika III lub art. 50",
        "rationale": "Domyslnie minimalne ryzyko. Brak obowiazkow wg Rozporzadzenia (jedynie dobrowolne kodeksy postepowania - art. 95).",
        "is_gpai": is_gpai,
        "gpai_systemic_risk": _gpai_systemic_risk(is_gpai, flops),
    }


def _gpai_systemic_risk(is_gpai: bool, flops: Optional[float]) -> bool:
    """art. 51 - prog ryzyka systemowego GPAI: moc obliczeniowa treningu >= 10^25 FLOP."""
    if not is_gpai or flops is None:
        return False
    return flops >= 1e25


def annotate_all(payload: Dict[str, Any]) -> Dict[str, Any]:
    classified = [classify(s) for s in payload.get("systems", [])]
    tier_counts: Dict[str, int] = {}
    for c in classified:
        tier_counts[c["tier"]] = tier_counts.get(c["tier"], 0) + 1
    gpai_systems = [c["name"] for c in classified if c["is_gpai"]]
    systemic_risk = [c["name"] for c in classified if c["gpai_systemic_risk"]]
    return {
        "total_systems": len(classified),
        "by_tier": tier_counts,
        "gpai_systems": gpai_systems,
        "gpai_systemic_risk_systems": systemic_risk,
        "systems": classified,
    }


def render_text(r: Dict[str, Any], source: str) -> str:
    lines = []
    lines.append("=" * 72)
    lines.append("AI ACT (Rozp. UE 2024/1689) - KLASYFIKACJA RYZYKA")
    lines.append(f"Zrodlo: {source}")
    lines.append("=" * 72)
    lines.append("")
    lines.append(f"Systemow lacznie: {r['total_systems']}")
    lines.append(f"Wg poziomu: {r['by_tier']}")
    if r["gpai_systems"]:
        lines.append(f"Systemy GPAI: {', '.join(r['gpai_systems'])}")
    if r["gpai_systemic_risk_systems"]:
        lines.append(f"GPAI z ryzykiem systemowym (art. 51): {', '.join(r['gpai_systemic_risk_systems'])}")
    lines.append("")
    lines.append("-" * 72)

    for s in r["systems"]:
        tier_label = s["tier"].replace("_", "-").upper()
        gpai_flag = "  [GPAI]" if s["is_gpai"] else ""
        sysrisk_flag = "  [RYZYKO SYSTEMOWE]" if s["gpai_systemic_risk"] else ""
        lines.append(f"  {s['name']}{gpai_flag}{sysrisk_flag}")
        lines.append(f"      Poziom: {tier_label}")
        lines.append(f"      Podstawa: {s['primary_citation']}")
        lines.append(f"      Uzasadnienie: {s['rationale']}")
        lines.append("")

    lines.append("-" * 72)
    lines.append("KOLEJNOSC DECYZJI: zakazy art. 5 -> art. 6 ust. 1 zal. I -> art. 6 ust. 2 zal. III")
    lines.append("                -> wyjatki art. 6 ust. 3 (znoszone przez profilowanie) -> transparentnosc art. 50 -> minimalne ryzyko domyslnie")
    lines.append("")
    lines.append("-" * 72)
    lines.append(BANNER)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Klasyfikator poziomu ryzyka AI Act wg art. 5/6/50 + zalacznik III.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("path", nargs="?", help="Sciezka do JSON z systemami (uzywa wbudowanej probki gdy pominieta)")
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
        source = "<wbudowana probka: 5 systemow we wszystkich 4 poziomach + 1 GPAI>"

    result = annotate_all(payload)
    if args.output == "json":
        print(json.dumps({"source": source, "disclaimer": BANNER, **result}, indent=2, ensure_ascii=False))
    else:
        print(render_text(result, source))
    return 0


if __name__ == "__main__":
    sys.exit(main())
