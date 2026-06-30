---
name: rodo-dsar-pl
description: >
  Obsługa żądań osób, których dane dotyczą (DSAR) po polsku, w oparciu o art. 12 oraz 15-22 RODO.
  Identyfikuje typ żądania (dostęp 15, sprostowanie 16, usunięcie 17, ograniczenie 18, przenoszenie
  20, sprzeciw 21, decyzje zautomatyzowane 22), pilnuje TERMINU (1 miesiąc od otrzymania, art. 12
  ust. 3; przedłużenie o maks. 2 miesiące przy złożoności), bramkuje wyjątki i podstawy odmowy (np.
  art. 17 ust. 3, żądania ewidentnie bezzasadne lub nadmierne - art. 12 ust. 5), składa draft
  odpowiedzi i rejestr. Weryfikacja tożsamości wnioskodawcy (art. 12 ust. 6) jako pierwszy krok.
  Wysyłkę odpowiedzi oraz usunięcie lub eksport danych zostawia człowiekowi. RODO-safe (lokalnie). Używaj gdy: "wniosek o dostęp do danych",
  "żądanie usunięcia", "prawo do bycia zapomnianym", "sprzeciw RODO", "termin na odpowiedź DSAR".
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.0.0
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
  informacji; to **zawiesza** bieg do potwierdzenia, ale nie służy do obstrukcji.
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
| 22 | Decyzje zautomatyzowane | prawo do interwencji ludzkiej |

## Krok 2 - Bramki i podstawy odmowy

Sprawdź wyjątki specyficzne dla prawa (zwłaszcza art. 17 ust. 3 i ograniczenia krajowe). Każdą odmowę
**uzasadnij prawnie** + pouczenie o skardze do UODO i drodze sądowej (art. 12 ust. 4). Powołania na
decyzje UODO => [[uodo-grounding-pl]].

## Krok 3 - Draft odpowiedzi + rejestr

Skill składa odpowiedź (język prosty, art. 12 ust. 1), listę danych/źródeł (z RoPA - [[rodo-ropa-dpa-pl]]),
i wpis do rejestru żądań (data wpływu, typ, termin, rozstrzygnięcie).

## Granica governance

Skill: klasyfikuje, liczy terminy, składa draft, prowadzi rejestr. Człowiek: weryfikuje tożsamość,
decyduje o realizacji/odmowie, **wykonuje usunięcie/eksport**, wysyła odpowiedź. Akty nieodwracalne i
na zewnątrz nigdy nie są automatyczne.

## Companion

Rejestr czynności (skąd dane): [[rodo-ropa-dpa-pl]]. Anonimizacja przy kopii: `gaius-api-anonymization`.
Parytet: `gdpr-dsar-en`.
