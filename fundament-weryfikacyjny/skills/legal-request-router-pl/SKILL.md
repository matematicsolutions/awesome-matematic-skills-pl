---
name: legal-request-router-pl
description: >
  Klasyfikator zadania prawnego - patrzy na zapytanie (i opcjonalnie deliverable)
  i decyduje, ktora sciezka weryfikacji uruchomic: zwykla odpowiedz, weryfikacja
  cytatow (citation-grounding-pl), kontradyktoryjna debata (adversarial-legal-review-pl)
  czy paczka audytowa (legal-ai-audit-bundle). Ocenia zlozonosc i ryzyko, zwraca
  decyzje routingu z uzasadnieniem. To warstwa NAD warstwa weryfikacji - chroni przed
  paleniem tokenow na rutynie i przed przepuszczeniem spraw wysokiej stawki bez kontroli. Uzywaj
  gdy: "co z tym zrobic", "czy to wymaga debaty", "jaka sciezka", "rozdziel zadanie",
  "klasyfikuj zapytanie", "czy to high-stakes", "routing", "triage zadania prawnego",
  na poczatku obslugi nowego zapytania prawnego zanim wybierzesz narzedzia.
license: Apache-2.0
allowed-tools: [Read]
data-residency: local
requires-human-approval: false
pii-egress: none
attribution:
  source: AnttiHero/lavern
  license: Apache-2.0
  relationship: pattern-only
  note: >
    Wzorzec klasyfikacji żądania przed skierowaniem go do narzędzia. Schemat i reguły
    napisane od zera.
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.0.0
  companion_skills: citation-grounding-pl, adversarial-legal-review-pl, legal-ai-audit-bundle, let-it-be
---

# Legal Request Router PL - klasyfikator i triage zadania prawnego

## Filozofia

**Nie kazde zapytanie zasluguje na te sama sciezke.** Streszczenie wyroku nie potrzebuje
kontradyktoryjnej debaty; opinia do klienta nie powinna wyjsc bez weryfikacji cytatow.
Router to jedna decyzja podejmowana na wejsciu, ktora dobiera proporcjonalna sciezke -
oszczedza tokeny na rutynie i wymusza kontrole tam, gdzie stawka jest wysoka.

Ten skill **nie wykonuje** pracy prawnej ani weryfikacji. Tylko klasyfikuje i wskazuje,
ktore companion-skille uruchomic i w jakiej kolejnosci.

## Workflow

1. **Zbierz sygnaly** - typ zapytania, czy jest gotowy deliverable, czy sa cytaty ze zrodel,
   kto jest odbiorca (klient / sad / wewnetrzne), jaka konsekwencja bledu.
2. **Sklasyfikuj** wg schematu ponizej (LLM zwraca strukture, NIE proza).
3. **Zmapuj na sciezke** wg tabeli decyzyjnej.
4. **Zwroc decyzje** + uzasadnienie + liste skilli do odpalenia w kolejnosci.

## Schemat klasyfikacji (output)

```json
{
  "typ_zadania": "odpowiedz_bezposrednia | weryfikacja_cytatow | kontrola_adwersaryjna | pelna_sciezka",
  "zlozonosc": "niska | srednia | wysoka",
  "ryzyko": "niskie | srednie | wysokie",
  "ma_cytaty_zrodlowe": true,
  "odbiorca": "wewnetrzny | klient | sad | regulator",
  "wymaga_groundingu": true,
  "wymaga_debaty": false,
  "wymaga_paczki_audytowej": false,
  "wymaga_pseudonimizacji": true,
  "sciezka": ["let-it-be", "citation-grounding-pl"],
  "uzasadnienie": "krotko: dlaczego ta sciezka"
}
```

## Tabela decyzyjna

Najpierw `typ_zadania` (rosnaca intensywnosc kontroli), 1:1 ze sciezka:

| Sygnal wejsciowy | `typ_zadania` | Sciezka kontroli |
|---|---|---|
| Brak cytatow, odbiorca wewnetrzny, ryzyko niskie | `odpowiedz_bezposrednia` | zadna weryfikacja |
| Sa cytaty ze zrodel (orzeczenie / ustawa / umowa), ale odbiorca wewnetrzny | `weryfikacja_cytatow` | **citation-grounding-pl** |
| Odbiorca klient / sad / regulator, ryzyko srednie+ | `kontrola_adwersaryjna` | **citation-grounding-pl** -> **adversarial-legal-review-pl** |
| Deliverable wychodzi na zewnatrz, ryzyko wysokie | `pelna_sciezka` | grounding -> debata -> **legal-ai-audit-bundle** |

Potem dwie flagi dodatkowe, niezalezne od `typ_zadania`:

| Sygnal | Flaga | Skill |
|---|---|---|
| Wejscie zawiera dane objete tajemnica / PII | `wymaga_pseudonimizacji = true` | **let-it-be** PRZED czymkolwiek |
| Deliverable na zewnatrz lub ryzyko wysokie | `wymaga_paczki_audytowej = true` | **legal-ai-audit-bundle** na koncu |

(`weryfikacja_cytatow` ustawia `wymaga_groundingu`, `kontrola_adwersaryjna` dodatkowo `wymaga_debaty`,
`pelna_sciezka` wszystkie cztery.)

## Reguly twarde

- **Nie eskaluj rutyny.** Jesli ryzyko niskie i odbiorca wewnetrzny - nie odpalaj debaty
  ani paczki audytowej, chocby dalo sie. Bramka kosztu dziala w obie strony.
- **Nie przepuszczaj wysokiej stawki na skroty.** Odbiorca sad/klient + cytaty = grounding obowiazkowy,
  nawet jesli uzytkownik nie poprosil. Jezeli odmawiasz eskalacji - powiedz to wprost w `uzasadnienie`.
- **Grounding poprzedza debate.** Jesli sciezka ma i grounding, i debate - grounding idzie pierwszy
  (debata na niezweryfikowanych cytatach jest bezwartosciowa).
- **Pseudonimizacja zawsze pierwsza.** `let-it-be` przed jakimkolwiek wyslaniem do modelu.
- **Paczka audytowa zawsze ostatnia.** Pakuje slady z poprzednich krokow.

## Output (dla uzytkownika)

```
## Routing - <nazwa zapytania>

Typ: pelna_sciezka | Zlozonosc: wysoka | Ryzyko: wysokie | Odbiorca: klient
Sciezka (kolejnosc):
  1. let-it-be          (pseudonimizacja - sa dane klienta)
  2. <praca prawna>     (poza tym skillem)
  3. citation-grounding-pl   (3 cytaty z orzecznictwa do weryfikacji)
  4. adversarial-legal-review-pl  (high-stakes: opinia do klienta)
  5. legal-ai-audit-bundle   (deliverable wychodzi na zewnatrz)

Uzasadnienie: opinia cytujaca SN, idzie do klienta, ryzyko wysokie -> pelna sciezka.
```

## Ochrona danych (RODO)

Router operuje na metadanych zapytania (typ, ryzyko, odbiorca), nie musi widziec pelnej tresci
objetej tajemnica. Jezeli do klasyfikacji potrzebny jest fragment dokumentu z danymi - pseudonimizuj
przez `let-it-be` najpierw.

## Integracja z AI Act

Proporcjonalna sciezka to operacjonalizacja podejscia opartego na ryzyku (risk-based approach AI Act).
Jawne `ryzyko` + `uzasadnienie` w decyzji routingu to slad, ktory wklada sie do `legal-ai-audit-bundle`
jako uzasadnienie wyboru poziomu kontroli.

## Atrybucja

Pattern (router + klasyfikacja zadania na sciezki) zainspirowany przez AnttiHero/lavern
(Apache 2.0, RouterClassification). Schemat, tabela decyzyjna i reguly napisane od zera pod polski
kontekst i warstwe weryfikacji MateMatic. Nie skopiowano kodu Lavern.

<!-- shared-rules:begin (wygenerowane z ../../SHARED-RULES.md przez scripts/shared-rules-sync.py - nie edytuj tutaj) -->
## Wspólne reguły wtyczki fundament-weryfikacyjny (Fundament weryfikacyjny)

Te reguły obowiązują w każdym skillu tej wtyczki, także gdy sam skill milczy. Są skopiowane do każdego skilla, więc działają zarówno po instalacji całej wtyczki, jak i pojedynczego skilla. Pełniejszy standard: https://github.com/matematicsolutions/awesome-matematic-skills-pl/tree/main/references

### Pięć warstw ochrony (przed każdym disclaimerem)

1. **Weryfikacja źródła** - przepisy i orzecznictwo z baz, nie z pamięci modelu.
2. **Klasa pewności** - każda teza prawna oznaczona: zweryfikowane / do sprawdzenia / nie używać.
3. **Kontrola przesłanek** - fakty od użytkownika sprawdza się przed analizą.
4. **Jawny zakres ujemny** - każdy skill mówi, czego NIE robi.
5. **Bramka człowieka** - uprawniona osoba sprawdza i zatwierdza wynik.

Jeśli błąd przeszedłby bez zatrzymania przez warstwy 1-5, wina jest w skillu. Naprawiamy narzędzie, nie dopisujemy noty. Nota "to nie porada prawna" nie zatrzymuje błędu i nie przenosi odpowiedzialności.

### Tagi pewności

- **Zweryfikowane** - źródło sprawdzone w sesji, z pełną sygnaturą: `(kodeks cywilny art. 415)`, `(wyrok SN II CSK NN/RR, SAOS)`.
- **Do sprawdzenia** - prawdopodobne, niezweryfikowane: `[sprawdź w SAOS]`.
- **Nie używać** - zmyślona sygnatura lub przepis. Pomiń, nigdy nie wymyślaj numeru.

Tag stoi przy linii, której dotyczy. Samo istnienie sygnatury nie wystarcza - treść trzeba sprawdzić.

### Bramka człowieka

Nic nie zostaje wysłane, złożone, podpisane ani opublikowane, zanim sprawdzi i zatwierdzi to uprawniony człowiek. Wynik skilla to projekt, nie gotowy dokument.

### Zakres pluginu

Fundament weryfikacyjny jest neutralny jurysdykcyjnie - to rdzeń metody, nie substancja prawa. Nie łączy się z żadnym źródłem zewnętrznym (brak konektorów MCP) i nie wysyła danych na zewnątrz. Substancję dostarczają osobne pluginy (orzecznictwo, dokumenty).
<!-- shared-rules:end -->
