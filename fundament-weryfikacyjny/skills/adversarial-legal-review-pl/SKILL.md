---
name: adversarial-legal-review-pl
description: >
  Czerwony zespół dla pisma prawnego - bierze gotowy deliverable wysokiej stawki
  (opinia, memo DD, M&A, pismo procesowe, rekomendacja do zarządu) i prowadzi
  kontradyktoryjną debatę: builder buduje najmocniejszą wersję tezy, attacker ją
  atakuje kontrargumentami i kontr-orzecznictwem, synthesizer godzi, verifier robi
  kontrolę końcową. Cel: wyłapać słabość ZANIM zrobi to przeciwnik, sąd albo klient.
  Z bramką kosztu - tylko dla spraw wysokiej stawki, nie dla każdego zapytania (drogie
  tokenowo). Używaj gdy: "przeatakuj tę opinię", "czerwony zespół", "adwokat diabła
  dla tego pisma", "znajdź słabości", "red team", "stress-test argumentacji",
  "co powie druga strona", "pre-mortem opinii", "obroń tę tezę", "kontradyktoryjna
  weryfikacja", "devil's advocate", weryfikacja high-stakes deliverable przed wysłaniem.
license: Apache-2.0
allowed-tools: [Read, Write]
data-residency: local
requires-human-approval: false
pii-egress: none
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.1.0
  inspiration: AnttiHero/lavern (Apache 2.0) - pattern ADR-010 debate + 3-layer verification, prompty i role napisane od zera
  companion_skills: citation-grounding-pl, legal-ai-audit-bundle, matematic-expert-panel, saos-orzecznictwo
---

# Adversarial Legal Review PL - czerwony zespół dla pisma prawnego

## Filozofia

**Lepiej, żeby słabość Twojej tezy znalazł Twój własny agent niż przeciwnik na rozprawie.**

Pojedynczy przebieg LLM produkuje argumentację, która brzmi pewnie - bo model jest
trenowany, by brzmieć pewnie. To złudzenie kompetencji. Prawdziwa wartość prawnika to
przewidzieć kontrargument, kontr-orzecznictwo i lukę w rozumowaniu, zanim zrobi to druga
strona. Ten skill instytucjonalizuje kontradyktoryjność: jeden agent broni, drugi atakuje,
trzeci godzi, czwarty weryfikuje.

To NIE jest pisanie deliverable od zera. To stress-test gotowego deliverable.

## Bramka kosztu (czytaj PRZED uruchomieniem)

Pełny cykl jest drogi tokenowo. Uruchamiaj **tylko dla wysokiej stawki**:

| Uruchom (high-stakes) | NIE uruchamiaj (zwykłe) |
|---|---|
| Opinia prawna do klienta | Notatka wewnętrzna |
| Due diligence / memo M&A | Streszczenie orzeczenia |
| Pismo procesowe przed terminem | Robocza analiza, draft |
| Rekomendacja do zarządu kancelarii | FAQ, content marketingowy |
| Stanowisko niosące istotne ryzyko finansowe lub reputacyjne | Zapytanie rutynowe |

Jeśli sprawa nie jest high-stakes - powiedz to wprost i zaproponuj zwykły jednoprzebiegowy
review zamiast pełnej debaty. Nie pal tokenów na rutynę.

## Workflow (4 role + weryfikacja)

Każda rola to osobny przebieg z czystym mandatem. Pseudonimizuj wejście przez `let-it-be`,
jeśli dokument zawiera dane objęte tajemnicą zawodową.

### 0. Bramka high-stakes
Oceń, czy sprawa kwalifikuje (tabela wyżej). Jeśli nie - stop, zaproponuj zwykły review.

### 1. Builder - najmocniejsza wersja tezy
Zbuduj najsilniejszą możliwą argumentację za tezą deliverable. Zbierz najlepsze przepisy,
orzecznictwo, doktrynę. Cel: dać attackerowi twardy cel, nie słomianego stracha.
Output: teza + 3-7 filarów (każdy z podstawą prawną).

### 2. Attacker - adwokat diabła
Zaatakuj każdy filar jak przeciwnik procesowy / sceptyczny sąd:
- kontr-orzecznictwo (pobierz realne przez `saos-orzecznictwo` / `eu-sparql-search`)
- kontrargument doktrynalny
- luka faktyczna / dowodowa
- nadinterpretacja przepisu, pominięty wyjątek, nieaktualna linia orzecznicza
- ryzyko proceduralne (terminy, legitymacja, właściwość)
Output: per filar - zarzut + jego siła (wysoka/średnia/niska) + źródło zarzutu.

### 3. Synthesizer - bilans
Dla każdego filaru rozstrzygnij: **przetrwał / osłabiony / obalony / NIEPEWNE**. Wskaż, co
zostaje z tezy po ataku, gdzie deliverable wymaga przeformułowania, gdzie trzeba zastrzeżenia
("ryzyko sporne, linia orzecznicza niejednolita").
Output: tabela filar → werdykt → rekomendowana zmiana.

**NIEPEWNE to werdykt pierwszej klasy, nie unik.** Synthesizer używa go, gdy debata nie
rozstrzygnęła sporu, i ZAWSZE dokłada dwie rzeczy: podkategorię oraz wskazanie, jakiego
dowodu brakuje do rozstrzygnięcia. Podkategorie:

- **NIEWYSTARCZAJĄCY_DOWÓD** - zarzut attackera ani nie potwierdzony, ani nie odparty,
  bo brakuje konkretnego materiału (np. pełny tekst uzasadnienia wyroku SN II CSK NN/RR,
  brzmienie aneksu do umowy, stan faktyczny od klienta).
- **DOKUMENT_NIEJEDNOZNACZNY** - materiał jest, ale nie daje się z niego wyczytać jednej
  odpowiedzi (klauzula dwuznaczna, rozbieżne wersje językowe, sprzeczne zapisy w umowie).

Zakaz przemilczania: filaru nierozstrzygniętego NIE wolno zapisać jako "przetrwał" ani
pominąć w tabeli. Ciche podciągnięcie niepewności pod pewność to najgorszy możliwy błąd
tego skilla - dokładnie ten, który ma łapać. To slogan "AI, która wie, czego nie wie"
jako schemat danych, nie deklaracja marketingowa.

### 4. Verifier - kontrola końcowa (10-punktowa)
Mechaniczna i merytoryczna kontrola zsyntetyzowanego deliverable:
1. Wszystkie cytaty przez `citation-grounding-pl` (BLOKADA na 🔴)
2. Każdy filar ma podstawę prawną
3. Żaden obalony filar nie został w finalnej tezie bez zastrzeżenia
4. Kontr-orzecznictwo attackera zaadresowane (nie zamiecione)
5. Brak twierdzeń kategorycznych tam, gdzie linia jest sporna
6. Aktualność przepisów (czy nie uchylony / znowelizowany)
7. Spójność wewnętrzna (teza nie przeczy uzasadnieniu)
8. Zakres zgodny z pytaniem klienta (nie więcej, nie mniej)
9. Ryzyka proceduralne wymienione
10. Poziom pewności wyrażony jawnie (nie fałszywa stanowczość)

### 4a. Pętla rewizji - twardy limit 2 rund

Gdy verifier znajdzie uchybienia, deliverable wraca do poprawy. Ta pętla ma twardy limit:

- **Runda 1**: verifier zgłasza uchybienia → poprawa → ponowna kontrola.
- **Runda 2**: to samo, ostatni raz.
- **Trzeci fail NIE jest kolejną iteracją.** Po drugiej nieudanej rewizji następuje
  obowiązkowa eskalacja do człowieka: raport z listą nierozstrzygniętych zarzutów
  (numer punktu kontroli, treść zarzutu, co próbowano w rundach 1-2, dlaczego nie
  przeszło). Żadnego "spróbuję jeszcze raz".

Powód: nieskończone polerowanie maskuje problem zamiast go rozstrzygać. Jeśli dwie
rewizje nie domknęły zarzutu, redakcja go nie domknie - spór jest merytoryczny albo
brakuje dowodu, a takie rzeczy rozstrzyga prawnik, nie kolejny przebieg modelu. Licznik
rund zapisuj w raporcie (patrz Output) - to część śladu audytowego.

### 4b. Funkcja werdyktu - deterministyczna, z jawnymi wagami

Werdykt końcowy NIE jest ogólnym osądem verifiera. Liczy się go z jawnego wzoru:

**Krok A - warunki krytyczne (dowolny spełniony → FAIL, bez liczenia dalej):**
- cytat 🔴 z citation-grounding-pl,
- filar obalony pozostawiony w tezie bez zastrzeżenia,
- zarzut attackera o sile wysokiej bez odpowiedzi w syntezie.

**Krok B - score ważony.** Każdy filar dostaje wagę wg werdyktu synthesizera:

| Werdykt filaru | Waga |
|---|---|
| przetrwał | 1.0 |
| osłabiony | 0.5 |
| NIEPEWNE (obie podkategorie) | 0.25 |
| obalony | 0.0 |

`score = suma wag / liczba filarów`. **Score < 0.6 → FAIL.**

**Krok C - próg warunkowy.** 2 lub więcej filarów osłabionych lub NIEPEWNYCH →
najwyżej **WYŚLIJ_WARUNKOWO** (odpowiednik CONDITIONAL_PASS w `deliverable-fidelity-pl`;
lista warunków: jakie zastrzeżenia dopisać, jaki dowód uzupełnić). Inaczej **PASS**.

Wagi i progi są wypisane w skillu celowo: audytor ma odtworzyć werdykt z samych liczb,
bez pytania modelu "dlaczego". To wymóg rejestrowania zdarzeń z art. 12 AI Act
zamieniony na arytmetykę - argument wprost pod PATRONa. Te same trzy kroki
(A krytyczne → B score ważony → C próg warunkowy) stosuje `deliverable-fidelity-pl`;
różnią się tylko wagi, bo inna jest materia (filary tezy vs ustalenia analizy).

## Output

```
## Adversarial review - <nazwa deliverable>

Stawka: WYSOKA (kwalifikuje)
Filary tezy: 5 | Przetrwały: 2 | Osłabione: 1 | Obalone: 1 | NIEPEWNE: 1

| Filar                        | Atak (siła)      | Werdykt    | Działanie                  |
|------------------------------|------------------|------------|----------------------------|
| Podstawa roszczenia art. X   | brak (niska)     | przetrwał  | bez zmian                  |
| Linia orzecznicza SN         | III CZP NN/RR (wysoka)| obalony| usuń lub dodaj zastrzeżenie|
| Skuteczność zastrzeżenia umownego | II CSK NN/RR (średnia) | NIEPEWNE (NIEWYSTARCZAJĄCY_DOWÓD) | brakuje: pełny tekst uzasadnienia - pobierz przez saos-orzecznictwo |
| ...                          | ...              | ...        | ...                        |

Kontrola verifiera: 9/10 OK. Punkt 1 (grounding): 1 cytat 🔴 - warunek krytyczny.
Rundy rewizji: 1/2 (limit twardy; trzeci fail = eskalacja do człowieka).
Funkcja werdyktu: Krok A (krytyczne) TAK - cytat 🔴 → FAIL. Krok B informacyjnie: (1.0+1.0+0.5+0.25+0.0)/5 = 0.55 (< 0.6).
Poziom pewności po debacie: ŚREDNI (1 filar NIEPEWNY, linia orzecznicza niejednolita w 1 filarze).

Werdykt: FAIL. NIE wysyłaj przed (a) poprawą cytatu 🔴, (b) dodaniem zastrzeżenia do filaru
obalonego, (c) uzupełnieniem dowodu dla filaru NIEPEWNEGO albo jawnym zastrzeżeniem w tekście.
```

Pełny zapis debaty (transcript builder/attacker/synthesizer) zwróć jako załącznik do
`legal-ai-audit-bundle` - to dowód kontradyktoryjnej weryfikacji.

## Ochrona danych (RODO)

- Każda rola działa w ramach standardowego API - dla materiałów objętych tajemnicą zawodową
  pseudonimizuj wejście przez `let-it-be` PRZED uruchomieniem.
- Pobieranie kontr-orzecznictwa przez companion-skille (saos / eu-sparql) - publiczne źródła.
- Skill nie zapisuje deliverable poza katalogiem sprawy.

## Integracja z AI Act

Kontradyktoryjna weryfikacja + jawny poziom pewności + transcript = operacjonalizacja nadzoru
człowieka (art. 14) i dokumentacji (art. 12). Człowiek dostaje nie "gotową odpowiedź", lecz
mapę tego, co przetrwało atak i z jaką pewnością - i na tej podstawie decyduje.

## Różnica od matematic-expert-panel

`matematic-expert-panel` = wieloperspektywiczna analiza decyzji biznesowej przez 5-7 person
(produkt warsztatowy dla zarządu). Ten skill = kontradyktoryjny stress-test JEDNEGO prawnego
deliverable (teza vs antyteza vs synteza vs weryfikacja). Panel patrzy wszerz, adversarial w głąb.

## Komplementarność z PromptDefense 12-vector (Microsoft AGT)

Ten skill atakuje **deliverable** (merytorycznie - czy teza wytrzyma kontrargument). Microsoft AGT
[`prompt_defense.py`](https://github.com/microsoft/agent-governance-toolkit/blob/main/agent-governance-python/agent-compliance/src/agent_compliance/prompt_defense.py)
(MIT, snapshot 2026-05-24) atakuje **system prompt** AI (pre-deployment - czy system prompt zawiera
obronę przed 12 znanymi atakami: role-escape, instruction-override, data-leakage, output-manipulation,
multilang-bypass, encoding-attacks, context-injection, tool-abuse, jailbreak, persona-hijacking,
memory-poisoning, output-extraction; mapping na OWASP LLM Top 10). 

Dwa różne narzędzia, dwie różne fazy:
- Adversarial-legal-review-pl: **PO** napisaniu deliverable, **PRZED** wysłaniem klientowi
- PromptDefense 12-vector: **PRZED** wdrożeniem nowego use case AI w kancelarii, walidacja
  czy system prompt zawiera obronę przed znanymi atakami

Razem stanowią dwustopniową bramę: prompt zaprojektowany odpornie (PromptDefense) + deliverable
przeczytany kontradyktoryjnie (adversarial-legal-review-pl). Cherry-pick wzorca PromptDefense
do dorobienia jako osobny walidator system promptów kancelarii pod kątem 12 wektorów ataku -
regex+zero LLM cost (backlog wewnętrzny).

## Atrybucja

Pattern (debate + 3-layer verification) zainspirowany przez AnttiHero/lavern (Apache 2.0,
ADR-010 w blueprincie Patrona). Role, prompty i 10-punktowa kontrola napisane od zera pod
polską procedurę i semantykę. Nie skopiowano 67 promptów agentów Lavern (US common law).

Trzy wzorce dodane w v1.1.0, każdy z AnttiHero/lavern (Apache 2.0), adaptacja od zera:
NIEPEWNE jako werdykt pierwszej klasy (sekcja 3), pętla rewizji z twardym limitem 2 rund
i przymusową eskalacją (sekcja 4a), deterministyczna funkcja werdyktu z jawnymi wagami
(sekcja 4b). Wagi, progi i podkategorie polskie - opracowanie MateMatic.

Referencja komplementarna do PromptDefense (12-vector) z [microsoft/agent-governance-toolkit](https://github.com/microsoft/agent-governance-toolkit)
(MIT, snapshot 2026-05-24, audyt RODO 🟢 ZIELONY) - tylko jako wskazanie różnicy fazy/scope,
nie cherry-pick kodu.
