---
name: citation-grounding-pl
description: >
  Mechaniczny weryfikator cytatu dla tekstów prawnych po polsku z GRADIENTEM
  weryfikacji (ISTNIENIE / TREŚĆ / FRAGMENT) - sprawdza string-matchem, czy każdy
  cytat z orzeczenia, ustawy, umowy lub pisma faktycznie istnieje w dokumencie
  źródłowym, czy sygnatura jest realna i czy parafraza oddaje stanowisko sądu,
  zamiast wierzyć modelowi "na oko". Przeciwdziała halucynacjom modelu (w tym
  problemowi "prawdziwy-cytat-fałszywa-teza"), RODO-safe (działa lokalnie), spina
  się z saos-orzecznictwo, szukaj-orzeczen-v2 i eu-sparql-search. Używaj gdy:
  weryfikacja cytatów w opinii prawnej / memo / piśmie procesowym, sprawdzenie czy
  AI nie zmyśliło fragmentu wyroku, przepisu lub sygnatury, czy parafraza nie
  przekręca holdingu, kontrola cytatu przed wysłaniem deliverable do klienta,
  audyt grounding outputu LLM, "sprawdź czy ten cytat jest prawdziwy", "zweryfikuj
  cytaty", "czy ten fragment wyroku istnieje", "grounding", "anti-halucynacja",
  "citation check", "czy AI to zmyśliło", "czy SN to naprawdę orzekł".
metadata:
  author: Wiesław Mazur / MateMatic
  version: 2.1.0
  inspiration: >
    v1 pattern (mechanical grounding verifier) - AnttiHero/lavern (Apache 2.0), ADR-011.
    v2 gradient weryfikacji (ISTNIENIE/TREŚĆ/FRAGMENT) - adaptacja Existence/Content/Paragraph
    z jeannesulzer/international-criminal-tribunals-skills (CC BY 4.0). v2.1 guard STRONY
    (Jaccard name-mismatch) - wzorzec z john-walkoe/courtlistener_citations_mcp (MIT).
    Kod, stop-listy i prompty od zera.
  companion_skills: saos-orzecznictwo, szukaj-orzeczen-v2, eu-sparql-search, legal-ai-audit-bundle, adversarial-legal-review-pl, deliverable-fidelity-pl, legal-request-router-pl
---

# Citation Grounding PL - mechaniczny weryfikator cytatu (gradient)

## Filozofia

**Cytat niezweryfikowany mechanicznie = cytat zmyślony, dopóki nie udowodnisz inaczej.**

Model językowy potrafi wygenerować fragment wyroku, który brzmi idealnie - sygnatura,
ton, słownictwo sądu - a którego w orzeczeniu nigdy nie było. Dla opinii prawnej cytującej
nieistniejący fragment SN to katastrofa zawodowa i ryzyko odpowiedzialności (art. 6 Prawa
o adwokaturze, należyta staranność).

**Zasada:** weryfikacja jest **mechaniczna**, nie semantyczna. Nie pytamy modelu „czy ten
cytat pasuje". Robimy string-match znormalizowanego cytatu wobec znormalizowanego źródła.
Match albo go nie ma. Odwrotny ciężar dowodu - to cytat musi się znaleźć w źródle.

## Co nowego w v2 - gradient weryfikacji

v1 sprawdzał tylko jedną rzecz: czy **dosłowny cytat** istnieje w źródle. To zostawiało dwie
ślepe plamy, które v2 zamyka:

1. **Zmyślona sygnatura.** v1 mówił „BRAK ŹRÓDŁA" = luka do uzupełnienia. v2 traktuje
   nierozwiązaną lub rozbieżną kotwicę jako **sygnał możliwego fałszerstwa**. **v2.1 dokłada guard
   STRONY:** sygnatura może być realna, ale doczepiona do INNEJ sprawy - gdy nazwy stron zadeklarowane
   rozjeżdżają się ze stronami rozwiązanego źródła (Jaccard tokenów nośnych < 0.30), to 🔴 blokada
   („prawdziwy cytat, fałszywa teza" już na poziomie kotwicy, nie dopiero w treści).
2. **Prawdziwy cytat, fałszywa teza** (problem Stanford „false-under-true"). Cytat może być
   dosłownie obecny (FRAGMENT zielony), a otaczające twierdzenie - „SN uznał, że…" - przekręca
   to, co sąd faktycznie orzekł. v1 **wprost zwalniał parafrazy** z weryfikacji. To była
   największa luka. v2 wciąga parafrazy w zakres na poziomie TREŚĆ.

**Trzy poziomy** (adaptacja Existence/Content/Paragraph z biblioteki Jeanne Sulzer, CC BY 4.0):

| Poziom | Co potwierdza | Stosuj do |
|---|---|---|
| **ISTNIENIE** | Kotwica - sygnatura/CELEX, data, organ - jest realna i zgadza się z deklaracją | „wyrok z 12.03.2019, II CSK…", „por. II CSK 123/19" |
| **TREŚĆ** | Źródło CO DO ISTOTY zawiera to, co twierdzi output | „SN przyjął, że…", parafraza holdingu |
| **FRAGMENT** | Cytowany akapit/zdanie istnieje dosłownie w źródle | każdy cytat w cudzysłowie, każdy pinpoint akapitu |

**Reguła kalibracji (rdzeń v2):** dopasuj siłę twierdzenia do **osiągniętego** poziomu. Jeśli
output twierdzi na poziomie FRAGMENT (dosłowny cytat), a weryfikacja dochodzi tylko do TREŚĆ
(źródło dotyczy tematu, ale cytatu dosłownie nie ma) → status **KALIBRACJA**: złagodź do
parafrazy ALBO oznacz pinpoint jako prowizoryczny. Pełna doktryna i macierz typów twierdzeń:
`references/gradient-weryfikacji.md`.

## Kiedy odpalać

**Zawsze przed wysłaniem do klienta / sądu:**
- Opinia prawna lub memo cytujące orzecznictwo, ustawy, umowę
- Pismo procesowe powołujące fragmenty wyroków
- Każdy output LLM zawierający cytaty, parafrazy holdingów lub powołania sygnatur

**Co teraz JEST w zakresie (zmiana wobec v1):** parafrazy i powołania samej sygnatury -
oznacz je `claim_type` i poddaj weryfikacji na właściwym poziomie. Bez cudzysłowu ≠ bez kontroli.

## Workflow

1. **Zbierz źródła i rozwiąż kotwice** - tekst dokumentu źródłowego dostępny lokalnie:
   - Orzeczenia: `saos-orzecznictwo` / `szukaj-orzeczen-v2` (zwracają też datę i organ → kotwica)
   - Akty EU: `eu-sparql-search` (CELEX → kotwica)
   - Ustawy PL / umowy / pisma: dostarcza użytkownik (.txt/.md/.docx → markitdown)
   - Gdy bezpośredni fetch zawiedzie, pracuj **drabinkę źródeł**: `references/drabinka-zrodel-pl.md`
   - **Bez źródła nie ma weryfikacji TREŚĆ/FRAGMENT** - status `BRAK ŹRÓDŁA`, nie „prawdopodobnie ok".

2. **Sklasyfikuj każde twierdzenie** - dla każdego powołania ustal `claim_type` (patrz macierz
   w `references/gradient-weryfikacji.md`). To ustawia WYMAGANY poziom weryfikacji:
   - `cytat_doslowny`, `teza_pinpoint` → FRAGMENT
   - `stanowisko_sadu`, `parafraza` → TREŚĆ
   - `fakt_proceduralny`, `powolanie` → ISTNIENIE

3. **Zbuduj zadanie** - jeden rekord na twierdzenie (format niżej): `quote` dla FRAGMENT,
   `claim_text` dla TREŚĆ, `anchor` + `anchor_resolved` dla ISTNIENIA.

4. **Weryfikacja mechaniczna** - uruchom skrypt:
   ```bash
   node scripts/ground-citations.mjs <plik-zadania.json>
   ```
   Skrypt liczy osiągnięty poziom, porównuje z wymaganym, kalibruje. Exit 1 = twarda blokada.

5. **Klasyfikuj wynik** (skrypt robi to automatycznie):
   - 🟢 `ZWERYFIKOWANY` - osiągnięty poziom ≥ wymagany (podaje offset dla FRAGMENT)
   - 🟡 `ZMODYFIKOWANY` - cytat znaleziony z drobną różnicą (interpunkcja, diakrytyki) - diff
   - 🟡 `WYMAGA_OSADU` - poziom TREŚĆ: terminy nośne obecne, substancję potwierdza człowiek / paraphrase-judge
   - 🟠 `KALIBRACJA` - osiągnięto niżej niż twierdzono (cytat dosłowny nieobecny, temat pokryty) - złagodź tezę
   - 🔴 `NIEZWERYFIKOWANY` - brak trafienia / rozbieżna kotwica = potencjalna halucynacja, BLOKUJ
   - ⛔ `BRAK ŹRÓDŁA` - nie dostarczono dokumentu / nierozwiązana sygnatura tam, gdzie wymagana

6. **Raport** - zwróć tabelę (niżej). 🔴 i ⛔ = **twarda blokada** (exit 1). 🟠 i 🟡 = **decyzja
   człowieka** przed publikacją (miękka). Nigdy nie przepuszczaj 🔴 milcząco.

## Format zadania (input skryptu)

```json
{
  "items": [
    {
      "id": "C1",
      "source_id": "II CSK 123/19",
      "claim_type": "cytat_doslowny",
      "quote": "sąd związany jest granicami zaskarżenia",
      "source_text": "<pełny znormalizowany tekst orzeczenia>"
    },
    {
      "id": "C2",
      "source_id": "I CSK 50/18",
      "claim_type": "stanowisko_sadu",
      "claim_text": "SN przyjął, że klauzula waloryzacyjna w umowie kredytu jest dopuszczalna",
      "source_text": "<pełny tekst orzeczenia>"
    },
    {
      "id": "C3",
      "source_id": "II CSK 123/19",
      "claim_type": "fakt_proceduralny",
      "anchor":          { "sygnatura": "II CSK 123/19", "data": "12.03.2019", "organ": "SN Izba Cywilna", "strony": "Kowalski przeciwko Bank Millennium S.A." },
      "anchor_resolved": { "sygnatura": "II CSK 123/19", "data": "2019-03-12", "organ": "Sąd Najwyższy Izba Cywilna", "strony": "Nowak przeciwko Skarb Państwa" }
    }
  ]
}
```

`anchor` = co twierdzi output. `anchor_resolved` = co zwrócił resolver (SAOS/EUR-Lex). Skrypt
porównuje mechanicznie (rozwija skróty: `SN`→`sąd najwyższy`, `NSA`, `TK`, `TSUE`…, normalizuje
daty `DD.MM.YYYY`↔`YYYY-MM-DD`). Brak `claim_type` → domyślnie `cytat_doslowny` (zachowanie v1).

**Pole `strony`** (opcjonalne, string „X przeciwko Y" albo tablica nazw) uruchamia **guard STRONY**:
gdy sygnatura się zgadza, ale nazwy stron zadeklarowane vs rozwiązane rozjeżdżają się (Jaccard tokenów
nośnych `< 0.30` przy ≥2 tokenach) → 🔴 blokada („prawdziwy cytat, fałszywa teza" na poziomie kotwicy).
Częściowa zgodność (`0.30–0.50`) → 🟡 miękka uwaga. Stop-lista odsiewa formy prawne (`sp. z o.o.`,
`S.A.`, `przeciwko`, `v.`, `i inni`), więc `Bank Millennium S.A.` ≡ `Bank Millennium Spółka Akcyjna`.
`anchor_resolved.strony` dostarcza resolver (SAOS zwraca strony postępowania).

## Reguły normalizacji (co robi skrypt)

Aby uniknąć fałszywych 🔴 z powodu kosmetyki, przed porównaniem skrypt:
- sprowadza do lowercase, zwija białe znaki, ujednolica cudzysłowy (`„` `"` `»` → `"`) i myślniki (`—` `–` → `-`)
- usuwa myślniki przenoszenia (`praw-\nnik` → `prawnik`)
- traktuje `[...]` / `...` w cytacie jako dozwoloną lukę
- przy kotwicy: rozwija skróty organów, normalizuje formaty dat, porównuje sygnatury bez kropek
- przy TREŚCI: wyciąga terminy nośne (≥4 znaki, bez stopwords), liczy pokrycie w źródle (próg 0.7)

Normalizacja NIE zmienia treści merytorycznej - jeśli słowo nośne jest inne, to nadal 🔴.

## Raport (dla użytkownika)

```
## Raport grounding (gradient) - <nazwa deliverable>

| ID | Źródło        | Typ              | Wym.→Osiąg.        | Status            | Uwaga                                   |
|----|---------------|------------------|--------------------|-------------------|-----------------------------------------|
| C1 | II CSK 123/19 | cytat_doslowny   | FRAGMENT→FRAGMENT  | 🟢 ZWERYFIKOWANY  | znak 4821                               |
| C2 | I CSK 50/18   | stanowisko_sadu  | TREŚĆ→TREŚĆ        | 🟡 WYMAGA_OSADU   | terminy 86% - potwierdź substancję      |
| C3 | III CZP 5/21  | cytat_doslowny   | FRAGMENT→ISTNIENIE | 🔴 NIEZWERYFIKOWANY| brak w źródle - BLOKADA                 |
| C4 | I CSK 50/18   | cytat_doslowny   | FRAGMENT→TREŚĆ     | 🟠 KALIBRACJA     | złagodź do parafrazy lub oznacz prowizor.|
| C5 | II CSK 999/19 | fakt_proceduralny| ISTNIENIE→BRAK     | 🔴 NIEZWERYFIKOWANY| rozbieżna sygnatura - możliwe falszerstwo|

Wynik: 1/5 zweryfikowane. 2 blokady (C3, C5), 1 kalibracja (C4), 1 do osądu (C2).
NIE publikuj dopóki C3 i C5 nie zostaną poprawione lub usunięte. C4 wymaga złagodzenia tezy.
```

## Ochrona danych (RODO)

- Skill działa **w całości lokalnie** - normalizacja i string-match w Node, bez wywołań sieciowych.
  (Rozwiązywanie kotwic przez SAOS/EUR-Lex robi agent osobnym krokiem - skrypt dostaje gotowy `anchor_resolved`.)
- Dla materiałów objętych tajemnicą zawodową: pseudonimizuj wcześniej przez `let-it-be`.
- Skrypt nie zapisuje logów poza katalogiem zadania.

## Integracja z AI Act

Mechaniczny grounding to dowód należytej staranności i element dokumentacji z art. 12 (rejestrowanie
zdarzeń) oraz nadzoru człowieka z art. 14. Gradient dodaje wymiar **kalibracji ryzyka**: poziom
weryfikacji per twierdzenie to ślad, jak mocno każda teza jest osadzona. Raport grounding wkładaj
do `legal-ai-audit-bundle` obok deliverable.

## Integracja z innymi skillami

- **`legal-request-router-pl`** routuje TU, gdy zapytanie zawiera powołania. Wysoka stawka →
  rozwiąż wszystkie kotwice (ISTNIENIE) + paraphrase-judge na 🟡.
- **`saos-orzecznictwo` / `eu-sparql-search`** = resolver kotwic (dają `anchor_resolved`) i źródło tekstu.
- **`deliverable-fidelity-pl`** pyta „czy nic nie wypadło z podsumowania"; ten skill pyta „czy to,
  co zostało, jest prawdziwe". Komplementarne - oba przed wysłaniem high-stakes.
- 🟡 `WYMAGA_OSADU` to dokładnie wejście dla warstwy paraphrase-judge (kaskada PATRON) -
  mechanika robi tani pre-filtr, osąd substancji robi człowiek lub model.

## Atrybucja

- Pattern mechanicznego groundingu (v1) zainspirowany AnttiHero/lavern (Apache 2.0, ADR-011).
- Guard STRONY (v2.1): wzorzec porównania nazw stron (Jaccard name-mismatch) zainspirowany funkcją
  `_is_name_mismatch` z `john-walkoe/courtlistener_citations_mcp` (MIT, 2026). Zaadaptowano **ideę**
  (parse → porównaj nazwy stron zadeklarowane vs rozwiązane → flaguj rozbieżność); kod, stop-lista
  form prawnych PL/EU i progi napisane od zera. Logika walidacji reporterów US z tamtego repo NIE jest
  przenoszona - żyje po stronie serwera CourtListener (wywołanie sieciowe + token), co łamie kontrakt
  zero-cloud; z repo bierzemy tylko lokalną, jurysdykcyjnie-neutralną heurystykę nazw stron.
- Gradient weryfikacji (v2): ISTNIENIE/TREŚĆ/FRAGMENT to adaptacja Existence/Content/Paragraph
  z `jeannesulzer/international-criminal-tribunals-skills` (CC BY 4.0, Jeanne Sulzer / Impact
  Litigation Lab, 2026). Zaadaptowano **ideę gradientu i regułę kalibracji**, nie kod ani treść -
  ich biblioteka to dyscyplina promptowa pod web_fetch publicznych archiwów; tutaj to mechaniczny
  silnik string-match pod lokalne źródła PL (RODO, zero-egress). Kod, prompty i reguły normalizacji
  napisane od zera pod polskie realia (cudzysłowy „…", sygnatury SN/NSA/TSUE, CELEX).
