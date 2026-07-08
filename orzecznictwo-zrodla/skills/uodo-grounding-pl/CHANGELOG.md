# Changelog - uodo-grounding-pl

Format: [Keep a Changelog](https://keepachangelog.com/), [SemVer](https://semver.org/).

## [1.0.0] - 2026-06-04

### Added
- Drugi weryfikator domenowy z szablonu `citation-grounding-pl/references/szkielet-weryfikatora-domenowego`.
  **Dowód generalizacji szablonu poza SAOS**: decyzje Prezesa UODO są na uodo.gov.pl, nie w SAOS -
  resolver kotwicy to WebFetch/byob/PDF, nie companion-skill SAOS jak przy KIO.
- Backbone 7-plikowy: SKILL.md, CHANGELOG.md, references (zrodla-autorytatywne, format-cytatu,
  drabinka-zrodel, teksty-zrodlowe, traps), examples (weryfikacja, audyt).
- `references/traps.md` - pułapki domenowe RODO/UODO: GIODO (przed 25.05.2018) vs Prezes UODO (po),
  RODO (rozporządzenie UE 2016/679) vs krajowa ustawa o ochronie danych z 10.05.2018, sygnatury DKN/DS/DKE,
  decyzja administracyjna vs wyrok WSA/NSA, kara EUR/% vs PLN, serwis uodo.gov.pl wrogi botom.
- `references/drabinka-zrodel.md` - centralna dla tej domeny: uodo.gov.pl zwraca 500/JS, więc FRAGMENT
  wymaga PDF/realnego Chrome/użytkownika; bez tekstu cytat = ⛔ BRAK ŹRÓDŁA.
- Przykłady na **realnych** sygnaturach DKN.5131.29.2023 (kara 238 345 zł) i DKN.5131.13.2022 (30.11.2023).

### Wkład zwrotny do silnika współdzielonego (citation-grounding-pl)
- Budowa tego skilla ujawniła dwa braki w silniku `ground-citations.mjs`, naprawione tam (korzystają
  wszystkie weryfikatory):
  1. Skróty organów `UODO`/`PUODO`/`UOKiK` dodane do mapy (forma dopełniaczowa: „Prezes UODO" ↔
     „Prezes Urzędu Ochrony Danych Osobowych").
  2. **Organ stał się polem MIĘKKIM** - tożsamość kotwicy niesie sygnatura + data (twardy czerwony);
     niezgodność samego organu to uwaga, nie blokada (polska deklinacja urząd/urzędu nie daje już
     fałszywych czerwonych). Zero regresji na zestawach citation-grounding-pl i kio-grounding-pl.
