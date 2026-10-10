---
name: rodo-dsar-pl
description: >
  Obsługa żądań osób, których dane dotyczą (DSAR) po polsku, w oparciu o art. 12 oraz 15-22 RODO.
  Identyfikuje typ żądania (dostęp 15, sprostowanie 16, usunięcie 17, ograniczenie 18, przenoszenie
  20, sprzeciw 21, decyzje zautomatyzowane 22), pilnuje TERMINU (najpóźniej 1 miesiąc od otrzymania,
  art. 12 ust. 3; przedłużenie o maks. 2 miesiące z uwagi na skomplikowany charakter lub liczbę
  żądań), bramkuje wyjątki i podstawy odmowy (np. art. 17 ust. 3, żądania ewidentnie nieuzasadnione
  lub nadmierne - art. 12 ust. 5), składa draft
  odpowiedzi i rejestr. Weryfikacja tożsamości wnioskodawcy (art. 12 ust. 6) jako pierwszy krok.
  Wysyłkę odpowiedzi oraz usunięcie lub eksport danych zostawia człowiekowi. Nie dodaje konektorów i sam niczego nie wysyła; treść wniosku trafia do modelu, który masz skonfigurowany. Używaj gdy: "wniosek o dostęp do danych",
  "żądanie usunięcia", "prawo do bycia zapomnianym", "sprzeciw RODO", "termin na odpowiedź DSAR".
license: Apache-2.0
allowed-tools: [Read]
data-residency: local
requires-human-approval: true
pii-egress: none
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.3.0
  companion_skills: uodo-grounding-pl, rodo-ropa-dpa-pl, gaius-api-anonymization
  parity: gdpr-dsar-en
---

# RODO DSAR PL - obsługa żądań podmiotów danych (art. 12, 15-22)

## Filozofia

Żądanie podmiotu to zegar + ocena prawna, nie automat. Skill klasyfikuje, pilnuje terminu i składa
**draft** - decyzję o realizacji/odmowie i wysyłkę podejmuje administrator. Usunięcie/eksport danych
to akt nieodwracalny/na zewnątrz => zawsze człowiek (granica governance).

## Krok 0 - Tożsamość i termin

- **Weryfikacja tożsamości** (art. 12 ust. 6) - przy uzasadnionych wątpliwościach żądaj dodatkowych
  informacji. To NIE zawiesza biegu bezwarunkowo: wg Wytycznych EROD 01/2022 zawieszenie wchodzi w grę
  **tylko**, gdy informacja jest niezbędna do potwierdzenia tożsamości ORAZ administrator zażądał jej
  bez zbędnej zwłoki. Datę wpływu zachowaj w rejestrze zawsze - spóźnione lub nieproporcjonalne żądanie
  tożsamości nie przedłuża terminu, a weryfikacja nie służy do obstrukcji.
- **TERMIN: bez zbędnej zwłoki, a w każdym razie w ciągu miesiąca od otrzymania żądania**
  (art. 12 ust. 3) - miesiąc to granica. Przedłużenie o **kolejne 2 miesiące** w razie potrzeby, z
  uwagi na skomplikowany charakter żądania lub liczbę żądań - poinformuj osobę w ciągu pierwszego
  miesiąca, z podaniem przyczyn opóźnienia. Skill liczy `deadline_1_month` i
  `deadline_extended_3_months`.
- **Co do zasady bezpłatnie** (art. 12 ust. 5). Rozsądna opłata albo odmowa tylko gdy żądanie jest
  **ewidentnie nieuzasadnione lub nadmierne** (w szczególności ustawiczne) - obowiązek wykazania
  spoczywa na administratorze.

## Krok 1 - Klasyfikacja prawa

| Art. | Prawo | Klucz |
|---|---|---|
| 15 | Dostęp + kopia | zakres informacji, kopia danych, prawa osób trzecich |
| 16 | Sprostowanie | dane nieprawidłowe/niekompletne |
| 17 | Usunięcie ("zapomnienie") | przesłanki ust. 1 vs **wyjątki ust. 3**: wolność wypowiedzi i informacji, obowiązek prawny lub zadanie publiczne, zdrowie publiczne, cele archiwalne/badawcze/statystyczne, roszczenia |
| 18 | Ograniczenie | "zamrożenie" zamiast usunięcia |
| 20 | Przenoszenie | tylko zgoda/umowa + przetwarzanie zautomatyzowane; format ustrukturyzowany |
| 21 | Sprzeciw | uzasadniony interes / marketing (marketing = bezwzględny) |
| 22 | Decyzje zautomatyzowane | prawo pierwotne = **niepodleganie** decyzji opartej wyłącznie na zautomatyzowanym przetwarzaniu wywołującej skutki prawne/istotne; wyjątki ust. 2 (umowa, przepis, wyraźna zgoda) => zabezpieczenia ust. 3: interwencja ludzka, własne stanowisko, zakwestionowanie |

## Krok 2 - Bramki i podstawy odmowy

Sprawdź wyjątki specyficzne dla prawa (zwłaszcza art. 17 ust. 3 i ograniczenia krajowe). Gdy
administrator nie podejmuje działań, informuje osobę niezwłocznie, najpóźniej w ciągu miesiąca od
otrzymania żądania, o powodach oraz o możliwości skargi do UODO i drodze sądowej (art. 12 ust. 4). Powołania na
decyzje UODO => [[uodo-grounding-pl]].

## Krok 3 - Draft odpowiedzi + rejestr

Skill składa odpowiedź (język prosty, art. 12 ust. 1), dopasowaną do powołanego prawa. Przy art. 15
to **kopia danych osobowych pobrana z systemów operacyjnych**, które je faktycznie przechowują, plus
dostępne informacje o źródle danych (art. 15 ust. 1 lit. g) - RCP ([[rodo-ropa-dpa-pl]]) dostarcza
tylko ogólnych informacji o przetwarzaniu (cele, kategorie, odbiorcy), nie danych osoby. Do tego wpis
do rejestru żądań (data wpływu, typ, termin, rozstrzygnięcie).

## Narzędzie - kalkulator terminu (deterministyczny, offline)

Terminu miesięcznego nie licz w pamięci - arytmetyka miesiąca ma pułapki (wpływ 31 stycznia => koniec 28/29 lutego, wg rozporządzenia (EWG, Euratom) nr 1182/71). Użyj skryptu (zero zależności, offline):

```bash
python scripts/gdpr_deadlines.py dsar --from 2026-01-31 --extend
```

Zwraca `deadline_1_month` oraz (z `--extend`) `deadline_extended_3_months`. Skrypt nie przesuwa
daty, która wypada w sobotę, niedzielę lub święto (art. 3 ust. 4 rozporządzenia (EWG, Euratom) nr 1182/71), więc
jego wynik może wypaść wcześniej niż termin prawny, nigdy później. Wklej go do odpowiedzi i rejestru.

## Granica governance

Skill: klasyfikuje, liczy terminy, składa draft, prowadzi rejestr. Człowiek: weryfikuje tożsamość,
decyduje o realizacji/odmowie, **wykonuje usunięcie/eksport**, wysyła odpowiedź. Akty nieodwracalne i
na zewnątrz nigdy nie są automatyczne.

## Companion

Rejestr czynności (skąd dane): [[rodo-ropa-dpa-pl]]. Anonimizacja przy kopii: `gaius-api-anonymization`.
Parytet: `gdpr-dsar-en`.

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
