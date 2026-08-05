---
name: klauzule-kontraktowe-pl
description: >
  Lista kontrolna klauzul umownych dla polskiej kancelarii - przechodzi umowę po 41 kategoriach
  klauzul (taksonomia CUAD zlokalizowana do PL/UE) i oznacza, które są obecne, których brakuje
  i które są ryzykowne, z kotwicą do polskiego przepisu (KC, prawo autorskie, KP). Inny niz
  contract-review-pl (bulk audit portfela do tabeli) - ten skupia sie na JEDNEJ umowie i pyta
  "czego tu nie ma i co tu gryzie". Uzywaj gdy: "sprawdz klauzule w tej umowie", "czego brakuje
  w umowie", "spotting klauzul", "lista kontrolna kontraktu", "review pojedynczej umowy",
  "jakie klauzule ryzykowne", "audyt jednej umowy", przed podpisem / w negocjacji / przy DD
  pojedynczego kontraktu.
license: Apache-2.0
allowed-tools: [Read]
data-residency: local
requires-human-approval: false
pii-egress: none
attribution:
  source: CUAD (Contract Understanding Atticus Dataset), The Atticus Project
  url: https://www.atticusprojectai.org/cuad
  license: CC-BY-4.0
  relationship: adaptation
  note: >
    Taksonomia 41 kategorii klauzul pochodzi z CUAD. Opisy kategorii, kotwice do prawa
    polskiego i logika red-flag napisane od zera dla realiów PL/UE.
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.0.0
  companion_skills: contract-review-pl, citation-grounding-pl, redline-docx-pl, let-it-be
---

# Klauzule kontraktowe PL - lista kontrolna pojedynczej umowy

## Filozofia

**Najdroższe klauzule to te, których w umowie nie ma.** Audyt umowy to nie tylko czytanie tego,
co napisano - to sprawdzenie, czy nie brakuje zabezpieczenia, które w tej transakcji powinno być.
Ten skill przechodzi umowę po stałej liście 41 kategorii klauzul i dla każdej mówi: jest / nie ma /
jest, ale ryzykowna - z kotwicą do polskiego przepisu, żeby prawnik wiedział, gdzie spojrzeć.

Skill **nie zastępuje oceny prawnika.** Wskazuje obecność, brak i ryzyko; rozstrzygnięcie i
rekomendacja zostają po stronie mecenasa. To checklista, nie opinia.

## Różnica wobec contract-review-pl

- `contract-review-pl` - bulk audit PORTFELA umów (folder PDF/DOCX) do jednej tabeli .docx.
- `klauzule-kontraktowe-pl` - głęboki spotting JEDNEJ umowy po 41 kategoriach z kotwicą prawną.

Naturalna kolejność: bulk audit przesiewa portfel, ta checklista wchodzi głębiej w umowę, która
wymaga uwagi.

## Workflow

1. **Wczytaj umowę** (tekst lub przez `contract-review-pl` / `redline-docx-pl` jako ekstraktor).
2. **Pseudonimizuj** dane osobowe stron, jeśli umowa idzie do modelu w chmurze (`let-it-be`).
3. **Przejdź 41 kategorii** poniżej. Dla każdej: status `JEST` / `BRAK` / `RYZYKO` + krótkie uzasadnienie
   + cytat fragmentu (jeśli `JEST`).
4. **Zweryfikuj cytaty** mechanicznie (`citation-grounding-pl`) - żaden fragment nie może być zmyślony.
5. **Zbierz red-flagi** na górze raportu: brakujące zabezpieczenia + klauzule jednostronnie niekorzystne.

## Taksonomia 41 kategorii (PL/UE)

Grupy zachowane za CUAD (1-6) plus kategorie bezgrupowe. Kotwica = miejsce w prawie polskim, do
którego sięga mecenas; nie jest poradą, tylko wskazaniem.

### Metadane umowy
- **Nazwa dokumentu** - jak nazwano umowę (typ nazwany czy nienazwany, art. 353(1) KC).
- **Strony** - kto zawiera umowę (firma, NIP/KRS, reprezentacja - sprawdź umocowanie).
- **Prawo właściwe** - któremu prawu podlega umowa. W UE dla zobowiązań umownych: rozporządzenie Rzym I; brak wyboru = reguły kolizyjne.

### Grupa 1 - czas trwania i terminy
- **Data zawarcia** - data podpisania.
- **Data wejścia w życie** - od kiedy umowa skutkuje (może różnić się od daty zawarcia).
- **Data wygaśnięcia** - koniec okresu pierwotnego / czas nieoznaczony.
- **Przedłużenie (renewal)** - automatyczne przedłużenie lub jednostronna opcja przedłużenia.
- **Termin wypowiedzenia przedłużenia** - ile dni/miesięcy przed, by nie doszło do automatycznego przedłużenia.

### Grupa 2 - ograniczenia konkurencji
- **Zakaz konkurencji** - ograniczenie działalności konkurencyjnej strony (B2B: swoboda umów art. 353(1) KC; pracownik: art. 101(1)-101(4) KP, zakaz po ustaniu = odszkodowanie).
- **Wyłączność** - zobowiązanie do wyłącznego współdziałania / zakaz oferowania osobom trzecim.
- **Zakaz pozyskiwania klientów (no-solicit)** - zakaz przejmowania klientów/partnerów drugiej strony w trakcie i po umowie.
- **Wyjątki od ograniczeń konkurencji** - carve-outy do zakazu konkurencji, wyłączności i no-solicit.

### Grupa 3 - kontrola i cesja
- **Zmiana kontroli (change of control)** - prawo wypowiedzenia / wymóg zgody, gdy strona przechodzi przejęcie, sprzedaż udziałów lub zbycie przedsiębiorstwa.
- **Zakaz cesji (anti-assignment)** - zgoda/zawiadomienie wymagane przy przeniesieniu umowy na osobę trzecią (pactum de non cedendo, art. 509 §1 KC).

### Grupa 4 - licencje i prawa
- **Udzielenie licencji** - czy umowa zawiera licencję jednej strony na rzecz drugiej (pola eksploatacji, art. 41 i 50 pr. aut.).
- **Licencja nieprzenoszalna** - ograniczenie przeniesienia licencji na osobę trzecią.
- **Licencja afiliantów licencjodawcy** - licencja obejmuje też IP spółek powiązanych licencjodawcy.
- **Licencja dla afiliantów licencjobiorcy** - licencja rozciąga się na spółki powiązane licencjobiorcy/sublicencjobiorcy.
- **Licencja nieograniczona (all-you-can-eat)** - licencja „enterprise" / bez limitu użycia.
- **Licencja nieodwołalna lub wieczysta** - licencja, której nie można wypowiedzieć / bezterminowa.

### Grupa 5 - po zakończeniu i audyt
- **Świadczenia po zakończeniu** - obowiązki po wygaśnięciu/rozwiązaniu (transition, last-buy, przeniesienie IP, wind-down).
- **Prawo audytu** - prawo kontroli ksiąg/rejestrów/lokalizacji drugiej strony dla weryfikacji zgodności.

### Grupa 6 - odpowiedzialność
- **Odpowiedzialność nieograniczona (uncapped)** - brak limitu odpowiedzialności przy naruszeniu (uwaga: za winę umyślną odpowiedzialności wyłączyć nie można, art. 473 §2 KC).
- **Limit odpowiedzialności (cap)** - górna granica odpowiedzialności / termin na dochodzenie roszczeń (art. 473 §1 KC dopuszcza modyfikację umowną).

### Kategorie bezgrupowe
- **Klauzula najwyższego uprzywilejowania (MFN)** - prawo do nie gorszych warunków, jeśli druga strona da je osobie trzeciej.
- **Zakaz pozyskiwania pracowników** - zakaz przejmowania/zatrudniania pracowników/współpracowników drugiej strony.
- **Zakaz oczerniania (non-disparagement)** - zobowiązanie do niewypowiadania się negatywnie o drugiej stronie.
- **Wypowiedzenie bez przyczyny (for convenience)** - prawo rozwiązania bez podania powodu (samo zawiadomienie + okres).
- **Prawo pierwszeństwa (ROFR/ROFO/ROFN)** - prawo pierwokupu / pierwszej oferty / pierwszej negocjacji co do udziałów, technologii, aktywów.
- **Podział przychodu/zysku** - obowiązek dzielenia się przychodem lub zyskiem z drugą stroną.
- **Ograniczenia cenowe** - zakaz podnoszenia/obniżania cen towarów/usług.
- **Minimalne zobowiązanie** - minimalny wolumen/kwota, którą jedna strona musi kupić.
- **Ograniczenie wolumenu** - dopłata/zgoda, jeśli użycie przekroczy próg.
- **Przeniesienie własności IP** - IP stworzone przez jedną stronę staje się własnością drugiej (skuteczne przeniesienie wymaga pól eksploatacji, art. 41 i 50 pr. aut.; forma pisemna art. 53 pr. aut.).
- **Wspólna własność IP** - współwłasność praw między stronami.
- **Escrow kodu źródłowego** - depozyt kodu u osoby trzeciej, uwalniany przy zdarzeniach (upadłość, niewypłacalność).
- **Zobowiązanie do niepozywania (covenant not to sue)** - zakaz kwestionowania ważności IP drugiej strony / wnoszenia roszczeń niezwiązanych z umową.
- **Kara umowna / odszkodowanie umowne** - zryczałtowane odszkodowanie za naruszenie lub opłata za rozwiązanie (kara umowna tylko za zobowiązanie niepieniężne, art. 483-484 KC; sąd może miarkować).
- **Czas trwania rękojmi/gwarancji** - okres odpowiedzialności za wady (rękojmia art. 556 i nn. KC; gwarancja art. 577 i nn. KC).
- **Ubezpieczenie** - obowiązek utrzymania ubezpieczenia na rzecz drugiej strony.
- **Beneficjent będący osobą trzecią** - osoba spoza umowy uprawniona do żądania świadczenia (umowa o świadczenie na rzecz osoby trzeciej, art. 393 KC).

## Format wyjścia

```
RED-FLAGI (na górze):
- BRAK: <kategoria> - <dlaczego to ryzyko w tej transakcji>
- RYZYKO: <kategoria> - <na czym polega jednostronność>

TABELA 41 KATEGORII:
| Kategoria | Status | Uzasadnienie | Cytat (jeśli JEST) | Kotwica |
| Prawo właściwe | JEST | prawo polskie, sąd w Warszawie | "..." | Rzym I |
| Kara umowna | BRAK | brak zabezpieczenia terminów | - | art. 483 KC |
...
```

## Granice

- To checklista obecności i ryzyka, nie interpretacja treści klauzuli. Ocenę skuteczności i
  rekomendację wydaje prawnik.
- Kotwice do przepisów to wskazania „gdzie patrzeć", nie porada prawna ani twierdzenie o stanie prawnym.
- Taksonomia jest anglosaska u źródła (CUAD) - część kategorii (np. ROFR/ROFO/ROFN, MFN) rzadziej
  występuje w polskich umowach krajowych; w obrocie międzynarodowym i M&A są standardem.

## Atrybucja

Taksonomia 41 kategorii klauzul oparta na **CUAD (Contract Understanding Atticus Dataset)**,
The Atticus Project, na licencji **CC BY 4.0**. Źródło: https://www.atticusprojectai.org/cuad.
Opisy kategorii po polsku, kotwice do prawa polskiego (KC, prawo autorskie, KP) oraz logika
red-flag są oryginalnym opracowaniem MateMatic - interpretacja MateMatic, nie stanowisko NRA ani KRRP.
