---
name: rodo-ropa-dpa-pl
description: >
  Rejestr czynności przetwarzania (RCP / RoPA, art. 30 RODO) i przegląd umów powierzenia (DPA, art.
  28 RODO) po polsku. Część 1 - RCP: buduje i waliduje rejestr administratora (art. 30 ust. 1) oraz
  podmiotu przetwarzającego (art. 30 ust. 2), pilnuje wymaganych pól (cele, kategorie osób i danych,
  odbiorcy, transfery, terminy usunięcia, środki bezpieczeństwa). Część 2 - DPA: sprawdza umowę
  powierzenia pod kątem obowiązkowych klauzul art. 28 ust. 3 lit. a-h (polecenia administratora,
  poufność, bezpieczeństwo, podpowierzenie, pomoc w prawach osób, pomoc art. 32-36, usunięcie/zwrot,
  audyty) oraz transfery rozdz. V. Składa draft rejestru i redline umowy; podpis zostawia
  człowiekowi. Nie dodaje konektorów i sam niczego nie wysyła; wklejona treść umowy trafia do modelu, który masz skonfigurowany. Używaj gdy: "rejestr czynności przetwarzania", "RCP art. 30", "umowa powierzenia",
  "DPA art. 28", "przegląd umowy z procesorem", "rejestr RODO".
license: Apache-2.0
allowed-tools: [Read]
data-residency: local
requires-human-approval: true
pii-egress: none
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.3.0
  companion_skills: klauzule-kontraktowe-pl, redline-docx-pl, rodo-dpia-pl, uodo-grounding-pl
  parity: gdpr-ropa-dpa-en
---

# RODO RCP + DPA PL - rejestr czynności (art. 30) i powierzenie (art. 28)

## Filozofia

RCP to żywy dokument rozliczalności, a umowa powierzenia to lista obowiązkowych klauzul - jedno i
drugie da się zweryfikować mechanicznie wobec artykułu. Skill składa draft/redline; podpis i złożenie
to akt człowieka.

## Część 1 - Rejestr czynności przetwarzania (art. 30)

**Administrator (art. 30 ust. 1 lit. a-g)** - treść rejestru per czynność:
- imię i nazwisko lub nazwa oraz dane kontaktowe administratora i współadministratorów, a gdy ma to
  zastosowanie - przedstawiciela administratora oraz IOD,
- cele przetwarzania,
- kategorie osób i kategorie danych osobowych,
- kategorie odbiorców (w tym w państwach trzecich lub organizacjach międzynarodowych),
- gdy ma to zastosowanie, przekazania do państwa trzeciego lub organizacji międzynarodowej z ich
  nazwą, a przy przekazaniach z art. 49 ust. 1 akapit drugi - dokumentacja odpowiednich zabezpieczeń,
- jeżeli jest to możliwe, planowane terminy usunięcia poszczególnych kategorii danych,
- jeżeli jest to możliwe, ogólny opis technicznych i organizacyjnych środków bezpieczeństwa
  (art. 32 ust. 1).

**Podmiot przetwarzający (art. 30 ust. 2)** - pola obowiązkowe wg lit. a-d: nazwa i dane kontaktowe
procesora (procesorów) **i każdego administratora**, w imieniu którego działa (oraz, gdy dotyczy,
przedstawicieli i IOD), kategorie przetwarzań w imieniu każdego administratora, transfery +
zabezpieczenia, opis środków. Samo wymienienie administratorów i subprocesorów z nazwy to NIE jest
kompletny rejestr - dane kontaktowe, przedstawiciele i IOD są polami ustawowymi.

Skill waliduje kompletność (brak pola = luka, nie zgadywanie) i wskazuje czynności wymagające DPIA
=> [[rodo-dpia-pl]]. Zwolnienie z obowiązku (art. 30 ust. 5, <250 osób) interpretuj wąsko - i pamiętaj,
że niezależnie od zatrudnienia zwolnienie odpada, gdy przetwarzanie może powodować ryzyko dla praw lub
wolności, nie ma charakteru sporadycznego, obejmuje szczególne kategorie z art. 9 ust. 1 **albo dane
dotyczące wyroków skazujących i czynów zabronionych z art. 10** (każda przesłanka osobno). W praktyce
rzadko ma zastosowanie.

## Część 2 - Przegląd umowy powierzenia (art. 28 ust. 3)

Umowa MUSI zawierać, że podmiot przetwarzający:
- **a)** przetwarza wyłącznie na **udokumentowane polecenie** administratora (w tym transfery),
  chyba że obowiązek nakłada na niego prawo Unii lub państwa członkowskiego - wtedy przed
  przetwarzaniem informuje o tym administratora, o ile to prawo nie zabrania tego z uwagi na ważny
  interes publiczny,
- **b)** zapewnia **poufność** osób upoważnionych,
- **c)** stosuje środki **bezpieczeństwa** (art. 32),
- **d)** przestrzega warunków **podpowierzenia** (zgoda + te same obowiązki na subprocesora),
- **e)** **pomaga** administratorowi realizować żądania osób (prawa z rozdz. III),
- **f)** **pomaga** w zgodności art. 32-36 (bezpieczeństwo, naruszenia, DPIA),
- **g)** po zakończeniu usług, zależnie od decyzji administratora, **usuwa lub zwraca** wszelkie dane
  i usuwa ich istniejące kopie, chyba że prawo Unii lub państwa członkowskiego nakazuje
  przechowywanie,
- **h)** udostępnia wszelkie informacje niezbędne do wykazania zgodności i umożliwia **audyty/
  inspekcje** - oraz niezwłocznie informuje administratora, jeżeli jego zdaniem polecenie narusza
  przepisy o ochronie danych (art. 28 ust. 3 akapit drugi).

Plus: przedmiot i czas trwania, charakter i cel, rodzaj danych osobowych, kategorie osób oraz
obowiązki i prawa administratora (art. 28 ust. 3 zd. 1), a także transfery rozdz. V
(SCC/decyzja adekwatności). Skill produkuje **redline** brakujących/wadliwych
klauzul (silnik [[redline-docx-pl]], biblioteka [[klauzule-kontraktowe-pl]]).

## Narzędzie - kontrola klauzul art. 28 (deterministyczny, offline)

Braki w umowie powierzenia wskaż skryptem - podajesz obecne klauzule, zwraca brakujące (zero zależności, offline):

```bash
python scripts/dpa_clause_check.py --present a,b,c,g
```

Zwraca `missing` (np. d, e, f, h) = dokładny cel redline. `complete` gdy wszystkie 8 (lit. a-h) obecne.

## Granica governance

Skill: buduje/waliduje rejestr, robi redline umowy, mapuje braki na artykuły. Człowiek: zatwierdza
treść, negocjuje, **podpisuje** umowę i odpowiada za rejestr. Podpis nigdy nie jest automatyczny.

## Companion

Redline: [[redline-docx-pl]]. Klauzule: [[klauzule-kontraktowe-pl]]. DPIA: [[rodo-dpia-pl]]. Parytet:
`gdpr-ropa-dpa-en`.

<!-- shared-rules:begin (wygenerowane z ../../SHARED-RULES.md przez scripts/shared-rules-sync.py - nie edytuj tutaj) -->
## Wspólne reguły wtyczki ochrona-danych (Ochrona danych)

Te reguły obowiązują w każdym skillu tej wtyczki, także gdy sam skill milczy. Są skopiowane do każdego skilla, więc działają zarówno po instalacji całej wtyczki, jak i pojedynczego skilla.

Plugin prowadzi operacje RODO kancelarii i inspektora ochrony danych: ocenę skutków, obsługę naruszenia, żądania osób, rejestr czynności i przegląd umów powierzenia. To procesy zakończone projektem do decyzji, nie gotowe akty.

### Reguły

- **Wynik to projekt do decyzji.** Draft OSOD, zgłoszenia naruszenia, odpowiedzi na żądanie, rejestru czy redline umowy są punktem wyjścia dla administratora / IOD. Zatwierdza i wykonuje człowiek.
- **Granica governance - akt na zewnątrz zostaje człowiekowi.** Złożenie wniosku do UODO, wysyłka zgłoszenia naruszenia, wysyłka odpowiedzi na DSAR, usunięcie lub eksport danych, podpis umowy - plugin przygotowuje draft, nie wykonuje aktu.
- **Brak gwiazdkowania ryzyka.** Ocena ryzyka (DPIA, naruszenie) wymaga danych wejściowych; brak danych to luka do uzupełnienia, nie pole do zgadywania.
- **Bez porady prawnej.** Plugin porządkuje obowiązki RODO i mapuje je na artykuły; nie zastępuje analizy prawnej konkretnej sprawy.
- **Dane organizacji i osób.** Traktuj dane realnej kancelarii i osób, których dane dotyczą, jak poufne - nie wynoś poza uzgodniony obieg. Te skille nie dodają własnego kanału wychodzącego; co trafia do modelu, decyduje Twoja konfiguracja (patrz https://github.com/matematicsolutions/awesome-matematic-skills-pl/blob/main/TRUST.md).
- **Powołania na decyzje UODO** weryfikuj mechanicznie przez `uodo-grounding-pl` (bundel orzecznictwo-zrodla) przed wpisaniem do dokumentu.

### Zakres pluginu

Plugin daje operacyjne narzędzia RODO (DPIA, naruszenie 72h, DSAR, RoPA/DPA). Nie weryfikuje cytatu ani nie pobiera źródeł prawa - do tego są pluginy "fundament weryfikacyjny" i "orzecznictwo i źródła". Redline umowy powierzenia korzysta z `redline-docx-pl` i `klauzule-kontraktowe-pl` (bundel dokumenty).
<!-- shared-rules:end -->
