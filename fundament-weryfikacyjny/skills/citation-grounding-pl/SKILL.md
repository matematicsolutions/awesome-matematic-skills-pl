---
name: citation-grounding-pl
description: >
  Mechaniczny weryfikator cytatu dla tekstów prawnych po polsku - sprawdza
  string-matchem, czy każdy cytat z orzeczenia, ustawy, umowy lub pisma
  faktycznie istnieje w dokumencie źródłowym, zamiast wierzyć modelowi "na oko".
  Przeciwdziała halucynacjom modelu, RODO-safe (działa lokalnie), spina się z saos-orzecznictwo,
  szukaj-orzeczen-v2 i eu-sparql-search. Używaj gdy: weryfikacja cytatów w opinii
  prawnej / memo / piśmie procesowym, sprawdzenie czy AI nie zmyśliło fragmentu
  wyroku lub przepisu, kontrola cytatu przed wysłaniem deliverable do klienta,
  audyt grounding outputu LLM, "sprawdź czy ten cytat jest prawdziwy", "zweryfikuj
  cytaty", "czy ten fragment wyroku istnieje", "grounding", "anti-halucynacja",
  "citation check", "czy AI to zmyśliło".
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.0.0
  inspiration: AnttiHero/lavern (Apache 2.0) - pattern ADR-011 mechanical grounding verifier, kod i prompty napisane od zera
  companion_skills: saos-orzecznictwo, szukaj-orzeczen-v2, eu-sparql-search, legal-ai-audit-bundle, adversarial-legal-review-pl
---

# Citation Grounding PL - mechaniczny weryfikator cytatu

## Filozofia

**Cytat niezweryfikowany mechanicznie = cytat zmyślony, dopóki nie udowodnisz inaczej.**

Model językowy potrafi wygenerować fragment wyroku, który brzmi idealnie - sygnatura,
ton, słownictwo sądu - a którego w orzeczeniu nigdy nie było. Dla kodu to drobny błąd.
Dla opinii prawnej cytującej nieistniejący fragment SN to katastrofa zawodowa i ryzyko
odpowiedzialności (art. 6 Prawa o adwokaturze, należyta staranność).

**Zasada:** weryfikacja jest **mechaniczna**, nie semantyczna. Nie pytamy modelu "czy ten
cytat pasuje". Robimy string-match znormalizowanego cytatu wobec znormalizowanego źródła.
Match albo go nie ma. Odwrotny ciężar dowodu - to cytat musi się znaleźć w źródle.

## Kiedy odpalać

**Zawsze przed wysłaniem do klienta / sądu:**
- Opinia prawna lub memo cytujące orzecznictwo, ustawy, umowę
- Pismo procesowe powołujące fragmenty wyroków
- Każdy output LLM, który zawiera cytaty w cudzysłowie z dokumentu źródłowego

**Nie wymaga weryfikacji:**
- Parafraza bez cudzysłowu (ale oznacz ją jako parafrazę, nie cytat)
- Tekst bez powołań na źródła zewnętrzne

## Workflow

1. **Zbierz źródła** - tekst dokumentu źródłowego musi być dostępny lokalnie:
   - Orzeczenia: pobierz przez `saos-orzecznictwo` / `szukaj-orzeczen-v2`
   - Akty EU: `eu-sparql-search`
   - Ustawy PL / umowy / pisma: dostarcza użytkownik (plik .txt/.md/.docx → markitdown)
   - **Bez źródła nie ma weryfikacji** - status cytatu = `BRAK ŹRÓDŁA` (czerwony), nie "prawdopodobnie ok".

2. **Wyodrębnij cytaty** - z weryfikowanego tekstu wyciągnij wszystkie fragmenty w cudzysłowie
   (`"..."`, `„..."`, `»...«`) przypisane do konkretnego źródła. Każdy cytat = jeden rekord
   z polem `source` (sygnatura / CELEX / nazwa pliku).

3. **Weryfikacja mechaniczna** - uruchom skrypt:
   ```bash
   node scripts/ground-citations.mjs <plik-zadania.json>
   ```
   Skrypt normalizuje cytat i źródło (patrz sekcja "Reguły normalizacji"), obsługuje wielokropki
   (`[...]` / `...` = dozwolona luka), i zwraca status + offset trafienia.

4. **Klasyfikuj wynik** (skrypt robi to automatycznie):
   - 🟢 `ZWERYFIKOWANY` - znormalizowany cytat znaleziony w źródle (podaj offset)
   - 🟡 `ZMODYFIKOWANY` - znaleziony fragment różni się drobnie (interpunkcja, ucięcie) - pokaż diff
   - 🔴 `NIEZWERYFIKOWANY` - brak trafienia w źródle = potencjalna halucynacja, BLOKUJ
   - ⛔ `BRAK ŹRÓDŁA` - nie dostarczono dokumentu do porównania

5. **Raport** - zwróć tabelę (patrz sekcja "Raport"). Każdy 🔴 i ⛔ wymaga decyzji człowieka przed
   publikacją. Nigdy nie przepuszczaj 🔴 milcząco.

## Reguły normalizacji (co robi skrypt)

Aby uniknąć fałszywych 🔴 z powodu kosmetyki, przed porównaniem skrypt:
- sprowadza do lowercase
- zwija wielokrotne białe znaki (spacje, taby, newline) do pojedynczej spacji
- ujednolica cudzysłowy (`„` `"` `»` `«` `'` → `"`) i myślniki (`—` `–` → `-`)
- usuwa myślniki przenoszenia na końcu wiersza (`praw-\nnik` → `prawnik`)
- traktuje `[...]` oraz `...` w cytacie jako "dozwolona luka" (dopasowanie częściowe po obu stronach luki)

Normalizacja NIE zmienia treści merytorycznej - jeśli słowo jest inne, to nadal 🔴.

## Format zadania (input skryptu)

```json
{
  "items": [
    {
      "id": "C1",
      "source_id": "II CSK 123/19",
      "source_text": "<pełny znormalizowany tekst orzeczenia>",
      "quote": "sąd związany jest granicami zaskarżenia"
    }
  ]
}
```

## Raport (dla użytkownika)

```
## Raport grounding - <nazwa deliverable>

| ID | Źródło       | Status            | Offset / uwaga                       |
|----|--------------|-------------------|--------------------------------------|
| C1 | II CSK 123/19| 🟢 ZWERYFIKOWANY  | znak 4821                            |
| C2 | art. 233 KPC | 🟡 ZMODYFIKOWANY  | brak słowa "swobodnej" - patrz diff  |
| C3 | III CZP 5/21 | 🔴 NIEZWERYFIKOWANY| brak w źródle - BLOKADA publikacji  |
| C4 | umowa NDA    | ⛔ BRAK ŹRÓDŁA    | nie dostarczono dokumentu            |

Wynik: 1/4 zweryfikowane. 1 blokada (C3), 1 do uzupełnienia źródła (C4).
NIE publikuj dopóki C3 nie zostanie poprawione lub usunięte.
```

## Ochrona danych (RODO)

- Skill działa **w całości lokalnie** - normalizacja i string-match w Node, bez wywołań sieciowych.
- Treść cytatów i źródeł nie opuszcza maszyny poza standardowym promptem do modelu (który i tak
  je widzi). Dla materiałów objętych tajemnicą zawodową: pseudonimizuj wcześniej przez `let-it-be`.
- Skrypt nie zapisuje logów poza katalogiem zadania.

## Integracja z AI Act

Mechaniczny grounding to dowód należytej staranności i element dokumentacji z art. 12 (rejestrowanie
zdarzeń) oraz nadzoru człowieka z art. 14. Raport grounding wkładaj do `legal-ai-audit-bundle`
obok deliverable.

## Atrybucja

Pattern (mechanical grounding verifier) zainspirowany przez AnttiHero/lavern (Apache 2.0, ADR-011
w blueprincie Patrona). Kod, prompty i reguły normalizacji napisane od zera pod polskie realia
(cudzysłowy „...", sygnatury, CELEX). Nie skopiowano kodu ani promptów Lavern.
