---
name: rodo-naruszenie-72h-pl
description: >
  Obsługa naruszenia ochrony danych w reżimie 72h po polsku, w oparciu o art. 33-34 RODO, wytyczne
  EROD 9/2022 (zgłaszanie naruszeń) i formularz zgłoszeniowy Prezesa UODO. Prowadzi drzewo
  decyzyjne: czy to naruszenie i jaki typ (poufność/integralność/dostępność), ocena ryzyka dla praw
  i wolności, czy zgłaszać do UODO w 72h (art. 33) z licznikiem terminu od stwierdzenia, czy
  zawiadomić osoby (art. 34, "wysokie ryzyko") i wyjątki, wpis do wewnętrznego rejestru naruszeń
  (art. 33 ust. 5). Składa draft zgłoszenia i zawiadomień; wysyłkę do UODO i osób zostawia
  człowiekowi. RODO-safe (lokalnie). Używaj gdy: "wyciek danych",
  "naruszenie RODO", "zgłoszenie do UODO 72h", "czy zawiadomić osoby", "art. 33", "data breach PL".
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.1.0
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

Czynniki (EROD 9/2022 / dawniej WP250): typ naruszenia, charakter/wrażliwość/wolumen danych,
łatwość identyfikacji, waga skutków (kradzież tożsamości, strata finansowa, dyskryminacja, szkoda
reputacyjna), cechy szczególne osób (dzieci, pacjenci), liczba osób. Wynik: `ryzyko: brak / istnieje
/ wysokie`.

## Krok 3 - Zgłoszenie do UODO (art. 33) - LICZNIK 72h

- **Zegar startuje od STWIERDZENIA** naruszenia (nie od zdarzenia). Termin: **72 godziny**.
- Zgłaszaj, **chyba że** jest **mało prawdopodobne**, by naruszenie skutkowało ryzykiem dla praw i
  wolności (art. 33 ust. 1). Brak zgłoszenia => uzasadnij i udokumentuj.
- **Po terminie** => zgłoszenie + wyjaśnienie opóźnienia (art. 33 ust. 1 zd. 2).
- Treść zgłoszenia (art. 33 ust. 3): charakter naruszenia (kategorie i przybliżona liczba osób oraz
  wpisów), dane kontaktowe IOD, możliwe konsekwencje, zastosowane/proponowane środki. Dopuszczalne
  **zgłoszenie etapowe** (art. 33 ust. 4).
- Skill podaje `deadline_72h` (data+godzina) i przygotowuje draft wg pól formularza UODO.

## Krok 4 - Zawiadomienie osób (art. 34)

Jeśli **wysokie ryzyko** => zawiadom osoby **bez zbędnej zwłoki**, językiem prostym i jasnym (art. 34
ust. 2: opis, IOD, konsekwencje, środki). **Wyjątki** (art. 34 ust. 3): odpowiednie zabezpieczenia
(np. szyfrowanie czyniące dane nieczytelnymi), środki następcze eliminujące wysokie ryzyko, lub
niewspółmierny wysiłek => komunikat publiczny.

## Krok 5 - Rejestr naruszeń (art. 33 ust. 5)

KAŻDE naruszenie (nawet niezgłoszone) wpisz do wewnętrznego rejestru: okoliczności, skutki, podjęte
działania. To dowód rozliczalności wobec UODO.

## Narzędzie - kalkulator terminu (deterministyczny, offline)

Licznika 72h nie licz w pamięci. Użyj skryptu (zero zależności, RODO-safe, lokalnie):

```bash
python scripts/gdpr_deadlines.py breach --from "2026-06-30T14:30"
```

Zwraca `deadline_72h` (ISO 8601) liczone od momentu stwierdzenia. Wynik wklej do draftu i rejestru.

## Granica governance

Skill: drzewo decyzyjne, licznik 72h, draft zgłoszenia i zawiadomień, wpis do rejestru. Człowiek:
zatwierdza ocenę ryzyka, wysyła zgłoszenie do UODO i zawiadomienia do osób. Wysyłka nigdy nie jest
automatyczna.

## Companion

Weryfikacja powołań UODO: [[uodo-grounding-pl]]. Ocena skutków: [[rodo-dpia-pl]]. Parytet:
`gdpr-breach-72h-en`.
