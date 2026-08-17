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
attribution:
  - source: AnttiHero/lavern
    license: Apache-2.0
    relationship: pattern-only
    note: >
      Wzorzec debaty z trójwarstwową weryfikacją oraz panel rozbieżności. Prompty i role
      napisane od zera.
  - source: gregmos/memoforge
    url: https://github.com/gregmos/memoforge
    license: MIT
    relationship: clean-room
    note: >
      Ograniczona samorewizja z cofnięciem po regresji, poziomy dostępu recenzentów
      i zasada „zawsze dostarcz". Koncepcje adaptowane clean-room, nie prompty ani kod.
      Ten sam upstream co bliźniak EN.
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.3.0
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

### Poziomy dostępu recenzentów (anty-bias)

Recenzenci dzielą się na dwa poziomy o RÓŻNYM dostępie do materiału. To jest celowe, nie
przypadkowe:

- **IZOLOWANY** (spójność wewnętrzna): recenzent logiki i struktury widzi **wyłącznie
  bieżący draft** - bez źródeł, bez orzecznictwa. Mandat: czy teza nie przeczy własnemu
  uzasadnieniu, czy wnioski wynikają z przesłanek, gdzie są luki logiczne. NIE ocenia, czy
  cytat jest prawdziwy. *Gdyby widział źródła, myliłby „brzmi jak źródło" z „jest spójne
  wewnętrznie".*
- **WZBOGACONY** (grounding): attacker (rola 2) i kontrola cytatów (punkt 1 verifiera)
  widzą źródła i intake, i sięgają po orzecznictwo przeciwne. Mandat: oparcie twierdzeń
  i autorytet przeciwny.

W trybie jednego modelu grającego wszystkie role izolacja jest **dyscypliną promptu**, nie
sandboxem - roli IZOLOWANEJ wprost zabroń sięgania po źródła. Twarda izolacja przez osobne
przebiegi to opcja premium (bramka kosztu, sekcja wyżej).

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

### 4a. Pętla rewizji - ograniczona, z gwarancją „nigdy gorsza wersja"

Gdy verifier znajdzie uchybienia, deliverable wraca do poprawy i przechodzi atak ponownie.
Pętla ma twarde limity i jedną gwarancję: **nigdy nie wysyłamy wersji gorszej od najlepszej
widzianej**.

- **Wersjonowanie:** `draft_v1` (po pierwszej syntezie), `draft_v2`... Każda iteracja to
  celowane poprawki z rekomendacji synthesizera, potem ponowny atak i weryfikacja.
- **`wynik_zbiorczy`** (0-100) = średnia z: verifier (X/10 → x10) + spójność (IZOLOWANY,
  0-100) + grounding (WZBOGACONY, 0-100). Składnik twardy: mechaniczna kontrola cytatów -
  każde niepowodzenie blokuje niezależnie od wyniku (chroni przed fałszywym cofnięciem na
  subiektywnej ocenie modelu).
- **`v_najlepsza`:** po każdej iteracji zapamiętaj draft z najwyższym `wynik_zbiorczy`.
- **Limit rund per stawka:** wysoka = maks. 3 rundy; tryb szybki = maks. 1.

**Decyzja o wyjściu należy do synthesizera.** Drzewo, w kolejności:

1. **Czysta akceptacja** - wszyscy recenzenci zaakceptowali, 0 blokerów →
   `zaakceptowano_na_vN`.
2. **COFNIĘCIE PO REGRESJI (N≥2)** - `wynik_zbiorczy(vN) < wynik_zbiorczy(v_najlepsza)` →
   odrzuć vN, przywróć `v_najlepsza`, wyjdź jako `wymuszone_wyjscie_na_v<najlepsza>_z_otwartymi`
   z banerem „runda N pogorszyła deliverable - przywrócono najlepszą wersję".
3. **Wczesne wyjście na plateau (N≥2)** - wynik ≥ próg (domyślnie 85), ale poprawa < 1,0
   pkt względem poprzedniej → `zaakceptowano_wczesnie_na_vN` (nie palić tokenów na
   marginalny zysk).
4. **Kontynuuj** - są blokery, limit nieosiągnięty, brak regresji i plateau → kolejna runda
   celowanych poprawek.
5. **Wymuszone wyjście na limicie** - limit osiągnięty, blokery zostały →
   `wymuszone_wyjscie_na_limicie` + baner z listą nierozstrzygniętych zarzutów.

Powód limitu: nieskończone polerowanie maskuje problem zamiast go rozstrzygać. Jeśli
trzy rundy nie domknęły zarzutu, redakcja go nie domknie - spór jest merytoryczny albo
brakuje dowodu, a to rozstrzyga prawnik, nie kolejny przebieg modelu. Licznik rund
i stan końcowy zapisuj w raporcie (patrz Output).

### Stany końcowe i zasada „zawsze dostarcz"

**Każde zakończenie MUSI wyprodukować artefakt dla człowieka** (pełny blok recenzji albo
markdown awaryjny). Nigdy ciche/puste wyjście. Stany końcowe:

`zaakceptowano_na_vN` | `zaakceptowano_wczesnie_na_vN` | `wymuszone_wyjscie_na_v<najlepsza>`
(regresja) | `wymuszone_wyjscie_na_limicie` | `porazka_z_fallbackiem` (np. brak danych
źródłowych - dostarcz, co masz, plus powód).

Baner zawsze pokazuje: stan końcowy, którą wersję draftu dostarczono, jakie blokery
zostały. **Governance:** skill produkuje rekomendację i wersje draftu; NIE wysyła
dokumentu. Decyzja „wysłać mimo `wymuszone_wyjscie_na_limicie` z blokerami" zostaje przy
człowieku. Transkrypt wszystkich wersji v1..vN idzie jako załącznik do paczki audytowej -
dowód ograniczonej rewizji i ewentualnego cofnięcia (AI Act art. 12/14).

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

### 4c. Panel rozbieżności (dissent) - moduł OPCJONALNY

Debata builder/attacker to spór wyreżyserowany: obie role gra ten sam model i
może zgodnie mylić się w tym samym miejscu. Panel rozbieżności łapie inny typ
błędu - interpretację, którą jeden przebieg uznaje za oczywistą, a która wcale
oczywista nie jest.

**Kiedy (bramka kosztu, jawna).** Tylko dla klauzul i tez NOŚNYCH: takich, od
których zależy wynik sprawy, przy stawce już zakwalifikowanej jako wysoka
(sekcja 0). Każda niezależna ocena to osobny pełny przebieg, więc domyślnie
panel dostaje 0 pytań; wskaż maksymalnie 1-2 filary, dla których rozbieżność
interpretacji realnie zmienia werdykt. Jeśli żaden filar nie spełnia tego
progu - nie uruchamiaj panelu i napisz to wprost w raporcie.

**Protokół.**

1. Sformułuj pytanie interpretacyjne jako multiple-choice (2-4 opcje), np.:
   „Czy kara umowna z par. 8 obejmuje także odstąpienie od umowy?
   A) tak, B) nie, C) tylko przy odstąpieniu z winy wykonawcy".
   Zamknięta lista opcji wymusza porównywalne werdykty - „to zależy" nie jest opcją.
2. Zbierz **co najmniej 2 NIEZALEŻNE oceny**: drugi model, drugi przebieg z
   innym promptem i bez dostępu do transkryptu debaty, albo człowiek. Każdy
   głosujący dostaje identyczne pytanie + sporny fragment i NIE widzi werdyktów
   pozostałych.
3. Zgoda panelu → odnotuj jedną linią w raporcie (pytanie, opcja, kto głosował).
4. **Split = FINDING pierwszej klasy.** Rozbieżność trafia do deliverable
   cytowana verbatim: kto głosował, jaka opcja, z jaką pewnością, jaki fragment
   klauzuli wskazał jako podstawę. NIE ukrywaj jej i NIE uśredniaj. Cichy wybór
   „lepszej" odpowiedzi to rozstrzygnięcie bez mandatu - dokładnie to, przed czym
   panel ma chronić.
5. **Pętla rozstrzygania: dociągnij autorytet.** Pobierz orzecznictwo lub
   przepis przez `saos-orzecznictwo` / ISAP (`legal-data-hunter-pl`) /
   `eu-sparql-search` (polskie i unijne źródła; oryginał lavern używa
   CourtListener - US) i powtórz głosowanie z dowodem na stole. Jedna runda
   re-vote, nie więcej.
6. **Split, który przetrwał dowody → human gate.** Filar dostaje werdykt
   NIEPEWNE (sekcja 3): DOKUMENT_NIEJEDNOZNACZNY, gdy panel czytał ten sam
   materiał i widzi różne rzeczy; NIEWYSTARCZAJĄCY_DOWÓD, gdy do rozstrzygnięcia
   brakuje materiału (np. pełnego uzasadnienia wyroku SN II CSK NN/RR).
   Rozstrzyga prawnik, nie trzeci przebieg modelu.

Format FINDING w deliverable:

```
FINDING - rozbieżność panelu (par. 8, kara umowna):
  Ocena A (model X): opcja B - "kara umowna zastrzeżona na wypadek niewykonania" (pewność: wysoka)
  Ocena B (przebieg niezależny): opcja C - "z winy wykonawcy" (pewność: średnia)
  Re-vote po dowodzie (uchwała SN III CZP NN/RR, SAOS): split utrzymany.
  Werdykt filaru: NIEPEWNE (DOKUMENT_NIEJEDNOZNACZNY) - decyzja prawnika.
```

**Spójność z resztą skilla (dissent wpina się, nie dubluje).** Werdykt z panelu
wchodzi do tabeli synthesizera jak każdy inny: split nierozstrzygnięty = NIEPEWNE
z wagą 0.25 w funkcji werdyktu (sekcja 4b), więc 2+ takie filary same z siebie
ściągają wynik do WYŚLIJ_WARUNKOWO. Re-vote panelu NIE liczy się jako runda
rewizji z sekcji 4a - limit rund per stawka dotyczy poprawek deliverable po
verifierze, a panel ma własny, jeszcze twardszy limit: jedno głosowanie + jedno
powtórzenie z dowodem. Eskalacja do człowieka to ten sam mechanizm, co
`wymuszone_wyjscie_na_limicie` w drzewie wyjścia.

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
Iteracje: v2 (najlepsza=v2) | Stan końcowy: zaakceptowano_wczesnie_na_v2 | wynik_zbiorczy: 78 → 86 (limit 3 rundy dla stawki wysokiej).
Funkcja werdyktu: Krok A (krytyczne) TAK - cytat 🔴 → FAIL. Krok B informacyjnie: (1.0+1.0+0.5+0.25+0.0)/5 = 0.55 (< 0.6).
Poziom pewności po debacie: ŚREDNI (1 filar NIEPEWNY, linia orzecznicza niejednolita w 1 filarze).

Werdykt: FAIL. NIE wysyłaj przed (a) poprawą cytatu 🔴, (b) dodaniem zastrzeżenia do filaru
obalonego, (c) uzupełnieniem dowodu dla filaru NIEPEWNEGO albo jawnym zastrzeżeniem w tekście.

[baner stanu końcowego - przykłady]
- wymuszone_wyjscie_na_v1: „Runda 2 obniżyła wynik_zbiorczy (84 → 79) - przywrócono v1. Blokery: 1 cytat 🔴."
- wymuszone_wyjscie_na_limicie: „3 rundy wyczerpane, blokery zostały: filar III bez odniesienia do orzecznictwa przeciwnego. Dostarczono v3 - decyzja o wysyłce należy do Ciebie."
```

Pełny zapis debaty (transcript builder/attacker/synthesizer, wszystkie wersje v1..vN)
zwróć jako załącznik do `legal-ai-audit-bundle` - to dowód kontradyktoryjnej weryfikacji
i ograniczonej rewizji.

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

## Komplementarność z matematic-prompt-defense-pl

Ten skill atakuje **deliverable** (czy teza wytrzyma kontrargument, PO napisaniu, PRZED
wysyłką). [[matematic-prompt-defense-pl]] atakuje **system prompt** (czy zawiera obronę
przed 12 znanymi wektorami OWASP LLM Top 10, PRZED wdrożeniem use case'u). Razem to
dwustopniowa brama: prompt zaprojektowany odpornie + deliverable przeczytany
kontradyktoryjnie. Warstwę agenta z narzędziami i pamięcią (OWASP ASI) pokrywa
[[agentic-risk-asi-pl]].

## Atrybucja

Pattern (debate + 3-layer verification) zainspirowany przez AnttiHero/lavern (Apache 2.0,
ADR-010 w blueprincie Patrona). Role, prompty i 10-punktowa kontrola napisane od zera pod
polską procedurę i semantykę. Nie skopiowano 67 promptów agentów Lavern (US common law).

Trzy wzorce dodane w v1.1.0, każdy z AnttiHero/lavern (Apache 2.0), adaptacja od zera:
NIEPEWNE jako werdykt pierwszej klasy (sekcja 3), pętla rewizji z twardym limitem 2 rund
i przymusową eskalacją (sekcja 4a), deterministyczna funkcja werdyktu z jawnymi wagami
(sekcja 4b). Wagi, progi i podkategorie polskie - opracowanie MateMatic.

Czwarty wzorzec dodany w v1.2.0: panel rozbieżności (sekcja 4c) z AnttiHero/lavern
(Apache 2.0, `src/mcp/tools/dissent.ts`) - pytanie multiple-choice do niezależnych ocen,
split jako FINDING pokazywany verbatim, pętla resolveDissent (autorytet → re-vote →
eskalacja). Adaptacja od zera: źródła autorytetu polskie i unijne (saos-orzecznictwo /
ISAP / eu-sparql-search zamiast CourtListener), wpięcie splitu w werdykt NIEPEWNE i wagę
0.25 zamiast osobnego rejestru panelistów, limit jednej rundy re-vote.

Piąty wzorzec dodany w v1.3.0: ograniczona samorewizja z cofnięciem po regresji (drzewo
wyjścia, `v_najlepsza`, plateau), poziomy dostępu recenzentów (izolowany/wzbogacony) i zasada
„zawsze dostarcz" ze stanami końcowymi - adaptacja clean-room z gregmos/memoforge (MIT),
koncepcje sterowania pętlą i ról, nie prompty ani kod. Ten sam upstream, który od początku
kredytuje bliźniak adversarial-legal-review-en; port domyka rozjazd bliźniaków. Limit 2 rund
z v1.1.0 zastąpiony: gwarancja „nigdy gorsza wersja" pokrywa też tamten przypadek, a limit
rund jest teraz jawnym parametrem per stawka.

Odsyłacz (nie derywacja): PromptDefense z Microsoft Agent Governance Toolkit (MIT) jako
wskazanie różnicy fazy/scope. Ten skill nie adaptuje stamtąd żadnego wzorca - robi to
`matematic-prompt-defense-pl`, gdzie siedzi właściwa atrybucja z linkiem do repozytorium.
