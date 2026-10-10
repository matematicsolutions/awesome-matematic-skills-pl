---
name: rodo-naruszenie-72h-pl
description: >
  Obsługa naruszenia ochrony danych w reżimie 72h po polsku, w oparciu o art. 33-34 RODO, wytyczne
  EROD 9/2022 (zgłaszanie naruszeń) i formularz zgłoszeniowy Prezesa UODO. Prowadzi drzewo
  decyzyjne: czy to naruszenie i jaki typ (poufność/integralność/dostępność), ocena ryzyka dla praw
  i wolności, czy zgłaszać do UODO bez zbędnej zwłoki, w miarę możliwości w 72h (art. 33), z
  licznikiem granicy 72h od stwierdzenia, czy
  zawiadomić osoby (art. 34, "wysokie ryzyko") i wyjątki, wpis do wewnętrznego rejestru naruszeń
  (art. 33 ust. 5). Składa draft zgłoszenia i zawiadomień; wysyłkę do UODO i osób zostawia
  człowiekowi. Nie dodaje konektorów i sam niczego nie wysyła; wklejony opis incydentu trafia do modelu, który masz skonfigurowany. Używaj gdy: "wyciek danych",
  "naruszenie RODO", "zgłoszenie do UODO 72h", "czy zawiadomić osoby", "art. 33", "data breach PL".
license: Apache-2.0
allowed-tools: [Read]
data-residency: local
requires-human-approval: true
pii-egress: none
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.2.0
  companion_skills: uodo-grounding-pl, rodo-dpia-pl, legal-ai-audit-bundle
  parity: gdpr-breach-72h-en
---

# RODO Naruszenie 72h PL - obsługa naruszenia ochrony danych (art. 33-34)

## Filozofia

Przy naruszeniu liczy się zegar i dowód rozumowania. Skill prowadzi **udokumentowane** drzewo
decyzyjne i składa drafty; **decyzję o zgłoszeniu i wysyłkę podejmuje administrator/IOD**. Zero
domyślania - jeśli brak danych do oceny ryzyka, skill to oznacza jako lukę, nie zgaduje.

## Krok 1 - Czy to naruszenie i jaki typ

Naruszenie = naruszenie bezpieczeństwa prowadzące do przypadkowego/niezgodnego z prawem
zniszczenia, utraty, modyfikacji, nieuprawnionego ujawnienia lub dostępu (art. 4 pkt 12). Sklasyfikuj:
**poufność** (ujawnienie/dostęp), **integralność** (modyfikacja), **dostępność** (utrata/zniszczenie).
Często łączone.

## Krok 2 - Ocena ryzyka dla praw i wolności

Czynniki (wytyczne EROD 9/2022, zaktualizowana wersja WP250 rev.01): typ naruszenia,
charakter/wrażliwość/wolumen danych, łatwość identyfikacji, waga skutków (kradzież tożsamości,
strata finansowa, dyskryminacja, szkoda reputacyjna), cechy szczególne osób (dzieci, pacjenci),
cechy szczególne administratora (np. placówka medyczna), liczba osób. Wynik: `ryzyko: brak / istnieje
/ wysokie`.

## Krok 3 - Zgłoszenie do UODO (art. 33) - LICZNIK 72h

- **Zegar startuje od STWIERDZENIA** naruszenia (nie od zdarzenia). Zgłoś **bez zbędnej zwłoki,
  w miarę możliwości nie później niż w terminie 72 godzin** (art. 33 ust. 1) - 72 godziny to granica,
  nie cel.
- Zgłaszaj, **chyba że** jest **mało prawdopodobne**, by naruszenie skutkowało ryzykiem dla praw i
  wolności (art. 33 ust. 1). Brak zgłoszenia => uzasadnij i udokumentuj.
- **Po 72 godzinach** => zgłoszenie + wyjaśnienie przyczyn opóźnienia (art. 33 ust. 1 zd. 2).
- Treść zgłoszenia, co najmniej (art. 33 ust. 3): charakter naruszenia (w miarę możliwości
  kategorie i przybliżona liczba osób oraz wpisów), imię i nazwisko oraz dane kontaktowe IOD lub
  oznaczenie innego punktu kontaktowego, możliwe konsekwencje, środki zastosowane lub proponowane
  (w stosownych przypadkach także minimalizujące skutki). Dopuszczalne **zgłoszenie etapowe**, gdy
  nie wszystko wiadomo od razu, sukcesywnie bez zbędnej zwłoki (art. 33 ust. 4).
- Skill podaje `deadline_72h` (data+godzina) i przygotowuje draft wg pól formularza UODO.

## Krok 4 - Zawiadomienie osób (art. 34)

Jeśli **wysokie ryzyko** => zawiadom osoby **bez zbędnej zwłoki**, językiem prostym i jasnym (art. 34
ust. 2: charakter naruszenia, IOD lub inny punkt kontaktowy, konsekwencje, środki). **Wyjątki**
(art. 34 ust. 3): środki ochrony zastosowane do danych, których dotyczy naruszenie (np. szyfrowanie
uniemożliwiające odczyt), środki następcze eliminujące prawdopodobieństwo wysokiego ryzyka lub
niewspółmiernie duży wysiłek => publiczny komunikat albo podobny, równie skuteczny środek.

## Krok 5 - Rejestr naruszeń (art. 33 ust. 5)

KAŻDE naruszenie (nawet niezgłoszone) wpisz do wewnętrznego rejestru: okoliczności, skutki, podjęte
działania. To dowód rozliczalności wobec UODO.

## Narzędzie - kalkulator terminu (deterministyczny, offline)

Licznika 72h nie licz w pamięci. Użyj skryptu (zero zależności, offline):

```bash
python scripts/gdpr_deadlines.py breach --from "2026-06-30T14:30"
```

Zwraca `deadline_72h` (ISO 8601): moment stwierdzenia plus 72 godziny. To granica, liczona z
zapasem (według art. 3 ust. 1 rozporządzenia (EWG, Euratom) nr 1182/71 godzina stwierdzenia nie
wliczałaby się do terminu), więc wynik nigdy nie wypada później niż termin prawny. Wklej go do
draftu i rejestru.

## Granica governance

Skill: drzewo decyzyjne, licznik 72h, draft zgłoszenia i zawiadomień, wpis do rejestru. Człowiek:
zatwierdza ocenę ryzyka, wysyła zgłoszenie do UODO i zawiadomienia do osób. Wysyłka nigdy nie jest
automatyczna.

## Companion

Weryfikacja powołań UODO: [[uodo-grounding-pl]]. Ocena skutków: [[rodo-dpia-pl]]. Parytet:
`gdpr-breach-72h-en`.

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
