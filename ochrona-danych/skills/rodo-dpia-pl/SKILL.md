---
name: rodo-dpia-pl
description: >
  Ocena skutków dla ochrony danych (DPIA / OSOD) po polsku, krok po kroku w oparciu o art. 35-36
  RODO, wytyczne Grupy Roboczej Art. 29 (WP248 rev.01) i wykaz Prezesa UODO. Prowadzi przez: test czy
  DPIA jest WYMAGANE (9 kryteriów WP248, reguła co najmniej dwóch kryteriów, wykaz UODO), strukturę
  OSOD wg art. 35 ust. 7 (opis, niezbędność i proporcjonalność, ocena ryzyka, środki) oraz decyzję
  o uprzednich konsultacjach z UODO wg art. 36. Składa draft OSOD i rejestr decyzji; decyzję
  administratora i wniosek do UODO zostawia człowiekowi. Nie dodaje konektorów i sam niczego nie wysyła; wklejony opis systemu trafia do modelu, który masz skonfigurowany.
  Używaj gdy: "czy potrzebuję DPIA", "ocena skutków RODO", "OSOD dla profilowania/monitoringu/AI",
  "art. 35 RODO", "uprzednie konsultacje UODO", "DPIA dla nowego systemu".
license: Apache-2.0
allowed-tools: [Read]
data-residency: local
requires-human-approval: true
pii-egress: none
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.2.0
  companion_skills: uodo-grounding-pl, rodo-ropa-dpa-pl, klauzule-kontraktowe-pl, legal-ai-audit-bundle
  parity: gdpr-dpia-en
---

# RODO DPIA PL - ocena skutków dla ochrony danych (art. 35-36 RODO)

## Filozofia

DPIA to nie formularz do odhaczenia, lecz proces zarządzania ryzykiem dla praw i wolności osób.
Skill prowadzi proces i składa **draft** - rozstrzygnięcie (czy ryzyko jest akceptowalne, czy
wdrożyć system) należy do administratora. Każde powołanie na decyzję/karę UODO przepuść przez
[[uodo-grounding-pl]] przed wpisaniem do dokumentu.

## Krok 1 - Czy DPIA jest WYMAGANE (próg art. 35 ust. 1)

DPIA jest obowiązkowe, **przed rozpoczęciem przetwarzania**, gdy przetwarzanie **może powodować
wysokie ryzyko**. Trzy ścieżki:

1. **Wykaz Prezesa UODO** (art. 35 ust. 4; komunikat z 17 czerwca 2019 r., M.P. poz. 666) - lista
   kryteriów z przykładami, oparta na WP248: co do zasady przetwarzanie spełniające **co najmniej dwa**
   kryteria wymaga DPIA, w niektórych przypadkach wystarczy jedno. Kryteria obejmują m.in. ocenę i
   profilowanie, zautomatyzowane decyzje, systematyczny monitoring miejsc dostępnych publicznie z
   rozpoznawaniem cech (bez zwykłego monitoringu wizyjnego nagrywanego na potrzeby incydentów), dane
   szczególnych kategorii, dane biometryczne i genetyczne. Przykłady w wykazie są ilustracyjne.
2. **9 kryteriów WP248** (Grupa Robocza Art. 29, WP248 rev.01) - reguła kciuka: **>=2 kryteria
   spełnione => DPIA w większości przypadków**, czasem wystarczy jedno. Kryteria: ocena/scoring,
   zautomatyzowane decyzje o skutkach prawnych lub podobnie istotnych (art. 22), systematyczny
   monitoring, dane szczególne/wysoce osobiste, dane na dużą skalę, łączenie/zestawianie zbiorów,
   osoby wymagające szczególnej opieki (dzieci, pracownicy), innowacyjne zastosowanie rozwiązań
   technologicznych lub organizacyjnych (przykłady z WP248: łączenie odcisków palców z rozpoznawaniem
   twarzy, Internet rzeczy), przetwarzanie uniemożliwiające realizację prawa lub korzystanie z
   usługi albo umowy.
3. **Art. 35 ust. 3** - obligatoryjne przypadki: a) systematyczna, kompleksowa ocena czynników
   osobowych oparta na zautomatyzowanym przetwarzaniu, w tym profilowaniu, **która jest podstawą
   decyzji wywołujących skutki prawne lub w podobny sposób znacząco wpływających na osobę**;
   b) dane szczególnych kategorii (art. 9 ust. 1) lub dotyczące wyroków skazujących (art. 10) na
   dużą skalę; c) systematyczny monitoring miejsc dostępnych publicznie na dużą skalę.

Wynik: `DPIA_wymagane: tak/nie/zalecane` + uzasadnienie per kryterium.

## Krok 2 - Struktura OSOD (minimum z art. 35 ust. 7)

Draft musi zawierać cztery filary:
- **a) Systematyczny opis** operacji i celów (+ prawnie uzasadniony interes, jeśli dotyczy).
- **b) Ocena niezbędności i proporcjonalności** względem celów (minimalizacja, podstawa prawna,
  ograniczenie celu, retencja, prawa osób, transfery).
- **c) Ocena ryzyka** dla praw i wolności osób (źródła ryzyka, scenariusze: poufność/integralność/
  dostępność; prawdopodobieństwo x waga).
- **d) Środki** zaradcze i zabezpieczenia (techniczne i organizacyjne) redukujące ryzyko + ryzyko
  szczątkowe.

Opinia IOD (jeżeli został wyznaczony) i, w stosownych przypadkach, opinie osób, których dane
dotyczą, lub ich przedstawicieli - udokumentuj wg art. 35 ust. 2 i ust. 9.

## Krok 3 - Uprzednie konsultacje (art. 36)

Jeśli **ryzyko szczątkowe pozostaje WYSOKIE mimo środków** => administrator MA OBOWIĄZEK
skonsultować się z Prezesem UODO PRZED rozpoczęciem przetwarzania (art. 36 ust. 1 w odczytaniu
WP248: konsultacja jest wymagana zawsze, gdy administrator nie znajduje środków wystarczających do
ograniczenia ryzyka do akceptowalnego poziomu). Skill przygotowuje draft
wystąpienia (zakres z art. 36 ust. 3), ale **wniosek składa człowiek** (granica governance).

## Narzędzie - przesiew progu (deterministyczny, offline)

Czy DPIA jest wymagane przesiej skryptem zamiast oceniać "na oko" (zero zależności, offline):

```bash
python scripts/dpia_screening.py --criteria evaluation,sensitive,largescale
python scripts/dpia_screening.py --mandatory public_monitoring
```

Zwraca `verdict` (required / recommended / not_required) wg reguły WP248 >=2 oraz przypadków art. 35 ust. 3. To przesiew, nie zwolnienie - decyzję dokumentuje administrator.

## Granica governance

Skill: składa draft OSOD, klasyfikuje kryteria, przygotowuje wystąpienie do UODO. Człowiek:
zatwierdza ocenę ryzyka, decyduje o wdrożeniu, podpisuje i składa wniosek o konsultacje. Akt na
zewnątrz (złożenie do UODO) nigdy nie jest automatyczny.

## Companion

Rejestr czynności i powierzenie: [[rodo-ropa-dpa-pl]]. Weryfikacja powołań UODO: [[uodo-grounding-pl]].
Parytet angielski: `gdpr-dpia-en`.

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
