---
name: subsumpcja-pl
description: >
  Buduje jawny sylogizm prawniczy (subsumcję) dla zagadnienia - rozkłada rozumowanie na
  przesłankę większą (norma + wykładnia), przesłankę mniejszą (istotne fakty), podciągnięcie
  faktów pod normę i wniosek, a potem wskazuje słabe ogniwa: ukryte założenia, sporne fakty,
  wątpliwą wykładnię. Wymusza, by każdy krok był wypowiedziany i sprawdzalny, zamiast skoku
  od stanu faktycznego do tezy. Pairuje z adversarial-legal-review-pl (atak na sylogizm),
  citation-grounding-pl (weryfikacja powołanej normy) i struktura-wyroku-pl. Uzywaj gdy:
  "zbuduj subsumpcję", "sylogizm prawniczy", "podciągnij fakty pod normę", "rozpisz
  rozumowanie", "gdzie jest luka w argumentacji", "przesłanka większa i mniejsza",
  "uzasadnij krok po kroku", przy pisaniu opinii / uzasadnienia / pisma procesowego.
license: Apache-2.0
allowed-tools: [Read]
data-residency: local
requires-human-approval: false
pii-egress: none
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.0.0
  inspiration: >
    Subsumcja (sylogizm prawniczy) to klasyczna metoda polskiej dogmatyki prawa. Pomysł
    jawnego scaffoldu sylogizmu dla AI zainspirowany m.in. projektem Fuzi.Mingcha
    (irlab-sdu, podejście major/minor/conclusion); implementacja, reguły i kotwice PL
    napisane od zera, bez użycia ich kodu ani modeli.
  companion_skills: adversarial-legal-review-pl, citation-grounding-pl, struktura-wyroku-pl, legal-request-router-pl
---

# Subsumpcja PL - jawny sylogizm prawniczy

## Filozofia

**Błąd w opinii rzadko siedzi we wniosku - siedzi w przemilczanej przesłance.** Rozumowanie prawnicze
to sylogizm: norma (przesłanka większa), fakty (przesłanka mniejsza), podciągnięcie i wniosek. Gdy
któryś krok zostaje niewypowiedziany - „bo przecież oczywiste" - tam właśnie chowa się luka, którą
znajdzie druga strona albo sąd. Ten skill zmusza, by każdy krok wypowiedzieć i oznaczyć, co jest
pewne, a co sporne.

Skill **strukturyzuje** rozumowanie, nie rozstrzyga sprawy. Ocena i decyzja zostają prawnikowi.

## Workflow

1. **Przesłanka większa (norma + wykładnia)** - zidentyfikuj normę prawną (przepis), a potem jej
   wykładnię: jak rozumiane są przesłanki normy (językowo, systemowo, celowościowo). Powołaną normę
   przekaż do citation-grounding-pl do weryfikacji.
2. **Przesłanka mniejsza (fakty istotne)** - wypisz fakty, które mają znaczenie dla przesłanek normy.
   Oddziel fakty bezsporne od spornych i od ocen.
3. **Subsumcja (podciągnięcie)** - dla każdej przesłanki normy pokaż, który fakt ją spełnia (lub nie).
   To jest właściwa praca: dopasowanie faktu do znamienia normy.
4. **Wniosek** - skutek prawny wynikający z subsumcji.
5. **Test słabych ogniw** - oznacz: które przesłanki normy są sporne w wykładni, które fakty sporne
   dowodowo, jakie założenia przyjęto milcząco. To mapa dla adversarial-legal-review-pl.

## Format wyjścia

```
ZAGADNIENIE: <pytanie prawne>

PRZESŁANKA WIĘKSZA (norma): <przepis> - "<treść/znamiona>"
  Wykładnia: <jak rozumiane są znamiona; rozbieżności w doktrynie/orzecznictwie>

PRZESŁANKA MNIEJSZA (fakty istotne):
  - bezsporne: <...>
  - sporne (dowodowo): <...>

SUBSUMCJA (znamię -> fakt):
  - <znamię 1> : spełnione przez <fakt> | NIE spełnione | sporne
  - <znamię 2> : ...

WNIOSEK: <skutek prawny>

SŁABE OGNIWA (do adversarial-legal-review-pl):
  - wykładnia: <które znamię sporne i dlaczego>
  - fakty: <co wymaga dowodu>
  - założenia milczące: <...>
```

## Granice

- Sylogizm porządkuje rozumowanie - nie zastępuje wykładni ani ustaleń dowodowych. Trafność normy,
  wykładni i oceny faktów rozstrzyga prawnik.
- Skill nie waży argumentów za i przeciw (od tego jest adversarial-legal-review-pl) - układa je tak,
  by atak i weryfikacja miały na czym pracować.
- Subsumcja zakłada normę o znamionach. Dla klauzul generalnych i ważenia zasad sam sylogizm bywa
  niewystarczający - oznacz to jako rozumowanie ważące, nie subsumpcyjne.

## Atrybucja

Subsumcja (sylogizm prawniczy) to klasyczna metoda polskiej dogmatyki prawa. Pomysł jawnego
scaffoldu sylogizmu dla AI zainspirowany m.in. projektem **Fuzi.Mingcha** (irlab-sdu) - bez użycia
jego kodu ani modeli. Reguły, format i kotwice PL to oryginalne opracowanie MateMatic.
Interpretacja MateMatic, nie stanowisko NRA ani KRRP.
