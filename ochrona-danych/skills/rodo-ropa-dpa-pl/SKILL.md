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
  człowiekowi. RODO-safe (lokalnie). Używaj gdy: "rejestr czynności przetwarzania", "RCP art. 30", "umowa powierzenia",
  "DPA art. 28", "przegląd umowy z procesorem", "rejestr RODO".
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.1.0
  companion_skills: klauzule-kontraktowe-pl, redline-docx-pl, rodo-dpia-pl, uodo-grounding-pl
  parity: gdpr-ropa-dpa-en
---

# RODO RCP + DPA PL - rejestr czynności (art. 30) i powierzenie (art. 28)

## Filozofia

RCP to żywy dokument rozliczalności, a umowa powierzenia to lista obowiązkowych klauzul - jedno i
drugie da się zweryfikować mechanicznie wobec artykułu. Skill składa draft/redline; podpis i złożenie
to akt człowieka.

## Część 1 - Rejestr czynności przetwarzania (art. 30)

**Administrator (art. 30 ust. 1)** - pola obowiązkowe per czynność:
- nazwa i dane kontaktowe administratora / współadministratora / IOD,
- cele przetwarzania,
- kategorie osób i kategorie danych osobowych,
- kategorie odbiorców (w tym w państwach trzecich),
- transfery do państw trzecich + zabezpieczenia (rozdz. V),
- planowane terminy usunięcia kategorii danych,
- ogólny opis technicznych i organizacyjnych środków bezpieczeństwa (art. 32).

**Podmiot przetwarzający (art. 30 ust. 2)** - węższy zakres: kategorie przetwarzań w imieniu każdego
administratora, transfery + zabezpieczenia, opis środków.

Skill waliduje kompletność (brak pola = luka, nie zgadywanie) i wskazuje czynności wymagające DPIA
=> [[rodo-dpia-pl]]. Zwolnienie z obowiązku (art. 30 ust. 5, <250 osób) interpretuj wąsko - w praktyce
rzadko ma zastosowanie.

## Część 2 - Przegląd umowy powierzenia (art. 28 ust. 3)

Umowa MUSI zawierać, że podmiot przetwarzający:
- **a)** przetwarza wyłącznie na **udokumentowane polecenie** administratora (w tym transfery),
- **b)** zapewnia **poufność** osób upoważnionych,
- **c)** stosuje środki **bezpieczeństwa** (art. 32),
- **d)** przestrzega warunków **podpowierzenia** (zgoda + te same obowiązki na subprocesora),
- **e)** **pomaga** administratorowi realizować żądania osób (prawa z rozdz. III),
- **f)** **pomaga** w zgodności art. 32-36 (bezpieczeństwo, naruszenia, DPIA),
- **g)** po zakończeniu **usuwa lub zwraca** dane,
- **h)** udostępnia informacje i umożliwia **audyty/inspekcje**.

Plus: przedmiot, czas, charakter i cel, rodzaj danych, kategorie osób (art. 28 ust. 3 zd. 1) oraz
transfery rozdz. V (SCC/decyzja adekwatności). Skill produkuje **redline** brakujących/wadliwych
klauzul (silnik [[redline-docx-pl]], biblioteka [[klauzule-kontraktowe-pl]]).

## Narzędzie - kontrola klauzul art. 28 (deterministyczny, offline)

Braki w umowie powierzenia wskaż skryptem - podajesz obecne klauzule, zwraca brakujące (zero zależności, RODO-safe):

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
