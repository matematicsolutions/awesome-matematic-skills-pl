---
name: rodo-dsar-pl
description: >
  Obsługa żądań osób, których dane dotyczą (DSAR) po polsku, w oparciu o art. 12 oraz 15-22 RODO.
  Identyfikuje typ żądania (dostęp 15, sprostowanie 16, usunięcie 17, ograniczenie 18, przenoszenie
  20, sprzeciw 21, decyzje zautomatyzowane 22), pilnuje TERMINU (1 miesiąc od otrzymania, art. 12
  ust. 3; przedłużenie o maks. 2 miesiące przy złożoności), bramkuje wyjątki i podstawy odmowy (np.
  art. 17 ust. 3, żądania ewidentnie bezzasadne lub nadmierne - art. 12 ust. 5), składa draft
  odpowiedzi i rejestr. Weryfikacja tożsamości wnioskodawcy (art. 12 ust. 6) jako pierwszy krok.
  Wysyłkę odpowiedzi oraz usunięcie lub eksport danych zostawia człowiekowi. Nie dodaje konektorów i sam niczego nie wysyła; treść wniosku trafia do modelu, który masz skonfigurowany. Używaj gdy: "wniosek o dostęp do danych",
  "żądanie usunięcia", "prawo do bycia zapomnianym", "sprzeciw RODO", "termin na odpowiedź DSAR".
license: Apache-2.0
allowed-tools: [Bash, Read]
data-residency: local
requires-human-approval: true
pii-egress: none
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.2.0
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
- **TERMIN: 1 miesiąc od otrzymania** (art. 12 ust. 3). Przedłużenie o **max 2 miesiące** przy
  skomplikowaniu/liczbie żądań - poinformuj w ciągu pierwszego miesiąca z przyczyną. Skill liczy
  `deadline` i `deadline_extended`.
- **Co do zasady bezpłatnie** (art. 12 ust. 5). Opłata/odmowa tylko gdy żądanie **ewidentnie
  bezzasadne lub nadmierne** - ciężar dowodu po administratorze.

## Krok 1 - Klasyfikacja prawa

| Art. | Prawo | Klucz |
|---|---|---|
| 15 | Dostęp + kopia | zakres informacji, kopia danych, prawa osób trzecich |
| 16 | Sprostowanie | dane nieprawidłowe/niekompletne |
| 17 | Usunięcie ("zapomnienie") | przesłanki ust. 1 vs **wyjątki ust. 3** (obowiązek prawny, roszczenia, wolność wypowiedzi) |
| 18 | Ograniczenie | "zamrożenie" zamiast usunięcia |
| 20 | Przenoszenie | tylko zgoda/umowa + przetwarzanie zautomatyzowane; format ustrukturyzowany |
| 21 | Sprzeciw | uzasadniony interes / marketing (marketing = bezwzględny) |
| 22 | Decyzje zautomatyzowane | prawo pierwotne = **niepodleganie** decyzji opartej wyłącznie na zautomatyzowanym przetwarzaniu wywołującej skutki prawne/istotne; wyjątki ust. 2 (umowa, przepis, wyraźna zgoda) => zabezpieczenia ust. 3: interwencja ludzka, własne stanowisko, zakwestionowanie |

## Krok 2 - Bramki i podstawy odmowy

Sprawdź wyjątki specyficzne dla prawa (zwłaszcza art. 17 ust. 3 i ograniczenia krajowe). Każdą odmowę
**uzasadnij prawnie** + pouczenie o skardze do UODO i drodze sądowej (art. 12 ust. 4). Powołania na
decyzje UODO => [[uodo-grounding-pl]].

## Krok 3 - Draft odpowiedzi + rejestr

Skill składa odpowiedź (język prosty, art. 12 ust. 1), dopasowaną do powołanego prawa. Przy art. 15
to **kopia danych osobowych pobrana z systemów operacyjnych**, które je faktycznie przechowują, plus
dostępne informacje o źródle danych (art. 15 ust. 1 lit. g) - RCP ([[rodo-ropa-dpa-pl]]) dostarcza
tylko ogólnych informacji o przetwarzaniu (cele, kategorie, odbiorcy), nie danych osoby. Do tego wpis
do rejestru żądań (data wpływu, typ, termin, rozstrzygnięcie).

## Narzędzie - kalkulator terminu (deterministyczny, offline)

Terminu miesięcznego nie licz w pamięci - arytmetyka miesiąca ma pułapki (wpływ 31 stycznia => koniec 28/29 lutego, wg rozporządzenia EWG 1182/71). Użyj skryptu (zero zależności, offline):

```bash
python scripts/gdpr_deadlines.py dsar --from 2026-01-31 --extend
```

Zwraca `deadline_1_month` oraz (z `--extend`) `deadline_extended_3_months`. Wynik wklej do odpowiedzi i rejestru.

## Granica governance

Skill: klasyfikuje, liczy terminy, składa draft, prowadzi rejestr. Człowiek: weryfikuje tożsamość,
decyduje o realizacji/odmowie, **wykonuje usunięcie/eksport**, wysyła odpowiedź. Akty nieodwracalne i
na zewnątrz nigdy nie są automatyczne.

## Companion

Rejestr czynności (skąd dane): [[rodo-ropa-dpa-pl]]. Anonimizacja przy kopii: `gaius-api-anonymization`.
Parytet: `gdpr-dsar-en`.
