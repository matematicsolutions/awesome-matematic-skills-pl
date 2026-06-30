---
name: rodo-dpia-pl
description: >
  Ocena skutków dla ochrony danych (DPIA / OSOD) po polsku, krok po kroku w oparciu o art. 35-36
  RODO, wytyczne EROD (WP248 rev.01) i komunikaty Prezesa UODO. Prowadzi przez: test czy DPIA jest
  WYMAGANE (9 kryteriów EROD, reguła co najmniej dwóch kryteriów, wykaz operacji UODO), strukturę
  OSOD wg art. 35 ust. 7 (opis, niezbędność i proporcjonalność, ocena ryzyka, środki) oraz decyzję
  o uprzednich konsultacjach z UODO wg art. 36. Składa draft OSOD i rejestr decyzji; decyzję
  administratora i wniosek do UODO zostawia człowiekowi. RODO-safe (lokalnie).
  Używaj gdy: "czy potrzebuję DPIA", "ocena skutków RODO", "OSOD dla profilowania/monitoringu/AI",
  "art. 35 RODO", "uprzednie konsultacje UODO", "DPIA dla nowego systemu".
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.0.0
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

DPIA jest obowiązkowe, gdy przetwarzanie **może powodować wysokie ryzyko**. Trzy ścieżki:

1. **Wykaz Prezesa UODO** (art. 35 ust. 4) - komunikat z rodzajami operacji zawsze wymagających
   DPIA (m.in. monitoring na dużą skalę, profilowanie z istotnym skutkiem, dane biometryczne,
   przetwarzanie danych szczególnych kategorii na dużą skalę). Sprawdź aktualny wykaz na uodo.gov.pl.
2. **9 kryteriów EROD (WP248)** - reguła kciuka: **>=2 kryteria spełnione => DPIA**. Kryteria:
   ocena/scoring, automatyczne decyzje z istotnym skutkiem (art. 22), systematyczny monitoring,
   dane szczególne/wysoce osobiste, dane na dużą skalę, łączenie/zestawianie zbiorów, osoby
   wymagające szczególnej opieki (dzieci, pracownicy), nowe technologie (AI, IoT), uniemożliwienie
   realizacji prawa/usługi.
3. **Art. 35 ust. 3** - obligatoryjne przypadki: systematyczna i kompleksowa ocena (profilowanie),
   dane szczególne/karne na dużą skalę, systematyczny monitoring miejsc publicznych na dużą skalę.

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

Opinia IOD (jeśli powołany) i konsultacja z osobami, których dane dotyczą (gdy stosowne) -
udokumentuj wg art. 35 ust. 2 i ust. 9.

## Krok 3 - Uprzednie konsultacje (art. 36)

Jeśli **ryzyko szczątkowe pozostaje WYSOKIE mimo środków** => administrator MA OBOWIĄZEK
skonsultować się z Prezesem UODO PRZED rozpoczęciem przetwarzania. Skill przygotowuje draft
wystąpienia (zakres z art. 36 ust. 3), ale **wniosek składa człowiek** (granica governance).

## Granica governance

Skill: składa draft OSOD, klasyfikuje kryteria, przygotowuje wystąpienie do UODO. Człowiek:
zatwierdza ocenę ryzyka, decyduje o wdrożeniu, podpisuje i składa wniosek o konsultacje. Akt na
zewnątrz (złożenie do UODO) nigdy nie jest automatyczny.

## Companion

Rejestr czynności i powierzenie: [[rodo-ropa-dpa-pl]]. Weryfikacja powołań UODO: [[uodo-grounding-pl]].
Parytet angielski: `gdpr-dpia-en`.
