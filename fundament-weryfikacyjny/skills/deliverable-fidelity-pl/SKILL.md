---
name: deliverable-fidelity-pl
description: >
  Weryfikator wiernosci deliverable - sprawdza, czy finalny dokument (opinia, memo,
  pismo) wiernie oddaje ustalenia analizy: czy zadna flaga RED nie wypadla z podsumowania,
  czy rozstrzygniecia sa odzwierciedlone. Mechaniczny check (skrypt, za darmo) + osad LLM
  na 3 najciezszych ustaleniach. Inny niz grounding (czy cytat prawdziwy) i adversarial
  (czy teza wytrzymuje) - ten pyta "czy streszczenie nie zgubilo tego, co wazne". Pominiete
  RED = blokada. Uzywaj gdy: "czy deliverable oddaje analize", "czy nic nie wypadlo z
  podsumowania", "weryfikacja wiernosci", "fidelity", "czy executive summary jest pelne",
  "czy RED jest w finalnej wersji", "spojnosc analizy z deliverable", przed wyslaniem
  zlozonego dokumentu ktory streszcza dluzsza analize.
license: Apache-2.0
allowed-tools: [Bash, Read]
data-residency: local
requires-human-approval: false
pii-egress: none
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.1.0
  inspiration: AnttiHero/lavern (Apache 2.0) - pattern src/assembly/post-assembly-verifier.ts, kod i reguly napisane od zera
  companion_skills: adversarial-legal-review-pl, citation-grounding-pl, legal-ai-audit-bundle, legal-request-router-pl
---

# Deliverable Fidelity PL - weryfikator wiernosci dokumentu

## Filozofia

**Najgrozniejszy blad to nie zly cytat, tylko prawdziwe ustalenie, ktore wypadlo z podsumowania.**
Analiza znalazla klauzule RED, opinia ma 12 stron, ale w podsumowaniu dla zarzadu tej klauzuli
nie ma - bo model "streszczajac" ja pominal. Cytaty sie zgadzaja, teza wytrzymuje atak, a mimo to
deliverable klamie przez przemilczenie. Ten skill sprawdza wiernosc: czy to, co wyszlo, oddaje to,
co znaleziono.

To trzecia, odrebna os weryfikacji:
- `citation-grounding-pl` - czy cytaty istnieja w zrodle (prawdziwosc).
- `adversarial-legal-review-pl` - czy teza wytrzymuje atak (odpornosc).
- `deliverable-fidelity-pl` - czy deliverable oddaje analize (wiernosc).

## Kiedy odpalac

Gdy finalny dokument **streszcza dluzsza analize** - opinia z podsumowaniem dla zarzadu, memo DD z tabela
ryzyk, raport z sekcja wnioskow. Tam, gdzie skracanie moze zgubic ustalenie. Nie trzeba dla krotkiego
pisma bez warstwy "analiza -> streszczenie".

## Wejscie

1. **Ustalenia analizy** (findings) - lista z severity i opcjonalnym rozstrzygnieciem:
   ```json
   { "findings": [
       { "id": "F1", "severity": "RED", "tekst": "klauzula limitacji odpowiedzialnosci sprzeczna z art. 473 par. 2 KC", "rozstrzygniecie": "rekomendacja usuniecia" },
       { "id": "F2", "severity": "YELLOW", "tekst": "termin platnosci 60 dni - ryzyko zatorow", "rozstrzygniecie": "" }
     ],
     "deliverable": "<pelny tekst finalnego dokumentu>" }
   ```
2. **Deliverable** - finalny tekst do sprawdzenia.

## Workflow

1. **Check mechaniczny (skrypt, za darmo)** - uruchom:
   ```bash
   node scripts/fidelity-check.mjs <plik-zadania.json>
   ```
   Skrypt wyciaga kluczowe terminy z kazdego ustalenia, normalizuje (lowercase, biale znaki, cudzyslowy,
   myslniki) i stosuje konserwatywny stem (utniecie 2 koncowych znakow przy slowach >=7, by zlapac fleksje
   - "klauzuli" pasuje do "klauzula"), po czym sprawdza, czy wystarczajaco terminow pojawia sie w deliverable.
   Per ustalenie: `reprezentowane` lub `pominiete`. **Pominiete RED -> blokada (exit 1).** Rozstrzygniecia tez sprawdzane.
2. **Kontrola wyrywkowa LLM (osad)** - dla ustalen RED (skrypt podaje liste `najciezsze_do_spotcheck_llm`,
   maks. 3) sprawdz nie tylko obecnosc slow, ale czy **sens** jest oddany (RED moze byc wspomniany, ale
   zbagatelizowany - "drobna uwaga" zamiast "klauzula niewazna"). To robi model, nie skrypt - mechaniczny
   match nie wykryje przeklamania tonu. Gdy brak ustalen RED, ta kontrola odpada (skrypt nie eskaluje YELLOW).
3. **Werdykt** - liczony deterministycznie wg funkcji ponizej, nie "na oko".

## Funkcja werdyktu (deterministyczna, jawne wagi i progi)

Werdykt NIE jest ogolnym osadem modelu. Liczy sie go z wynikow kroku 1 (skrypt) i kroku 2
(kontrola wyrywkowa) wg jawnego wzoru - trzy kroki, zawsze w tej kolejnosci:

**Krok A - warunki krytyczne (dowolny spelniony -> FAIL, bez liczenia dalej):**
- pominiete RED (skrypt: `pominiete_red` niepuste, exit 1),
- RED obecny, ale zbagatelizowany (kontrola wyrywkowa LLM),
- rozstrzygniecie RED nieodzwierciedlone (skrypt: `rozstrzygniecia_red_brak` niepuste).

**Krok B - score wazony pokrycia.** Kazde ustalenie ma wage wg severity:

| Severity | Waga |
|---|---|
| RED | 5 |
| YELLOW | 2 |
| GREEN / INFO | 1 |

`score = suma wag ustalen reprezentowanych / suma wag wszystkich ustalen`.
**Score < 0.85 -> FAIL** (nawet gdy zaden RED nie wypadl - masowe gubienie YELLOW
tez jest przemilczeniem).

**Krok C - prog warunkowy.** 3 lub wiecej pominietych YELLOW -> najwyzej
**CONDITIONAL_PASS**: deliverable moze wyjsc dopiero po decyzji czlowieka, z lista
pominietych ustalen dolaczona do raportu. Inaczej **PASS**.

Wagi i progi sa wypisane wprost celowo: audytor odtwarza werdykt z samych liczb
w raporcie, bez pytania modelu o uzasadnienie. To wymog rejestrowania zdarzen
z art. 12 AI Act sprowadzony do arytmetyki - argument wprost pod PATRONa. Te same
trzy kroki (krytyczne -> score wazony -> prog warunkowy) stosuje
`adversarial-legal-review-pl` dla filarow tezy; roznia sie tylko wagi, bo inna materia.

## Output (dla uzytkownika)

```
## Wiernosc deliverable: FAILED

Mechaniczny: 4/5 ustalen reprezentowane
- POMINIETE (RED): F3 "kara umowna bez gornego limitu" - BLOKADA, brak w deliverable
Kontrola wyrywkowa LLM (RED, maks. 3):
- F1 (RED) - oddany wiernie
- F2 (RED) - OBECNY ALE ZBAGATELIZOWANY: analiza "niewazny zapis", deliverable "kwestia do rozwazenia"
- F4 (YELLOW) - oddany

Funkcja werdyktu:
- Krok A (krytyczne): pominiete RED F3 + zbagatelizowany RED F2 -> FAIL.
- Krok B (informacyjnie): reprezentowane F1(5)+F2(5)+F4(2)+F5(1) / wszystkie F1..F5 (5+5+5+2+1)
  = 13/18 = 0.72 < 0.85 (F5 = GREEN, reprezentowane).

Werdykt: FAIL - NIE wysylaj. Dodaj F3 do podsumowania, wzmocnij F2 do faktycznej wagi.
```

## Reguly twarde

- **Pominiete RED = bezwzgledna blokada.** Czerwone ustalenie nieobecne w deliverable to przemilczenie
  istotnego ryzyka - nigdy nie przepuszczaj.
- **Bagatelizowanie liczy sie jak pominiecie.** RED opisany jako "drobna uwaga" jest gorszy niz brak,
  bo usypia czujnosc. Kontrola wyrywkowa LLM ma to lapac.
- **Skrypt mowi co obecne, model mowi czy wiernie.** Nie ufaj samemu matchowi slow - i nie kaz modelowi
  liczyc obecnosci, od tego jest skrypt.

## Ochrona danych (RODO)

Skrypt dziala lokalnie (Node, zero sieci). Kontrola wyrywkowa LLM widzi ustalenia i deliverable - jezeli zawieraja
dane objete tajemnica, pseudonimizuj przez `let-it-be` wczesniej. Skrypt nie zapisuje logow poza katalogiem zadania.

## Integracja z AI Act

Weryfikacja wiernosci to dowod, ze nadzor czlowieka (art. 14) dostaje pelen obraz - deliverable nie ukrywa
przed decydentem ustalen, ktore analiza wykryla. Raport wiernosci wkladaj do `legal-ai-audit-bundle`.

## Atrybucja

Pattern (post-assembly fidelity: mechaniczny check reprezentacji ustalen + kontrola wyrywkowa LLM najciezszych)
zainspirowany przez AnttiHero/lavern (Apache 2.0, `src/assembly/post-assembly-verifier.ts`). Kod, reguly
i polska lista stop-slow napisane od zera. Nie skopiowano kodu Lavern.

Wzorzec dodany w v1.1.0: deterministyczna funkcja werdyktu z jawnymi wagami i progami
(krytyczne -> score wazony -> prog warunkowy) z AnttiHero/lavern (Apache 2.0), adaptacja
od zera - wagi severity, prog 0.85 i regula CONDITIONAL_PASS to opracowanie MateMatic.
