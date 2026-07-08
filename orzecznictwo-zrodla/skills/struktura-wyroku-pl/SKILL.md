---
name: struktura-wyroku-pl
description: >
  Rozkłada polskie orzeczenie na role retoryczne i robi streszczenie EKSTRAKTYWNE
  (cytuje zdania źródłowe, nie parafrazuje) - segmentuje wyrok/postanowienie na
  komparycję, stan faktyczny, przebieg postępowania, zarzuty/wnioski, podstawę prawną,
  rozważania sądu, sentencję i tezę (ratio decidendi), wskazuje rozstrzygnięcie i
  powołane przepisy. Mechaniczna segmentacja + ekstrakcja kluczowych zdań, bez
  zmyślania. Pairuje z saos-orzecznictwo (znajdź), ekstraktor-cytatow-pl (cytaty) i
  citation-grounding-pl (weryfikacja). Uzywaj gdy: "streść ten wyrok", "co sąd
  orzekł i dlaczego", "wyciągnij tezę z orzeczenia", "struktura uzasadnienia",
  "ratio decidendi", "rozłóż wyrok na części", "podsumuj orzeczenie", przy czytaniu
  długiego uzasadnienia / analizie linii orzeczniczej / przygotowaniu glosy.
license: Apache-2.0
allowed-tools: [Read]
data-residency: local
requires-human-approval: false
pii-egress: none
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.0.0
  inspiration: >
    Metoda (judgment structuring przez role retoryczne zdań + extractive summarization)
    oparta na OpenNyAI / Opennyai (Legal-NLP-EkStep), licencja MIT
    (https://github.com/OpenNyAI/Opennyai). Indyjskie role i modele porzucone; role
    retoryczne polskiego orzeczenia i reguly ekstrakcji napisane od zera.
  companion_skills: saos-orzecznictwo, ekstraktor-cytatow-pl, citation-grounding-pl, szukaj-orzeczen-v2
---

# Struktura wyroku PL - rozłóż orzeczenie i streść ekstraktywnie

## Filozofia

**Streszczenie wyroku, które parafrazuje, zmyśla.** Model „podsumowując" uzasadnienie często
przesuwa akcenty albo dopisuje tezę, której sąd nie postawił. Ten skill robi inaczej: segmentuje
orzeczenie na role retoryczne i streszcza **ekstraktywnie** - wybiera i cytuje zdania źródłowe,
nie przepisuje ich własnymi słowami. To, co czytasz w streszczeniu, jest słowami sądu.

Mechaniczna segmentacja + ekstrakcja kluczowych zdań. Parafraza i ocena zostają prawnikowi.

## Role retoryczne polskiego orzeczenia

Segmentuj tekst na poniższe role (nie każde orzeczenie ma wszystkie):

1. **Komparycja** - sygnatura, sąd, skład, data, strony, przedmiot sprawy.
2. **Sentencja (rozstrzygnięcie)** - co sąd orzekł (oddala, zasądza, uchyla, zmienia). Sedno wyniku.
3. **Stan faktyczny** - ustalenia faktyczne przyjęte za podstawę.
4. **Przebieg postępowania** - co działo się w instancjach niżej / wcześniej.
5. **Zarzuty i wnioski stron** - podstawy zaskarżenia, żądania, stanowiska.
6. **Podstawa prawna** - powołane przepisy (przekaż do ekstraktor-cytatow-pl).
7. **Rozważania sądu** - rozumowanie prawne, wykładnia, subsumcja.
8. **Teza / ratio decidendi** - reguła rozstrzygająca, dla której wyrok jest cytowany.
9. **Zdanie odrębne** - jeśli jest (votum separatum), oznacz osobno - to nie jest stanowisko sądu.

## Workflow

1. **Wczytaj orzeczenie** (np. z saos-orzecznictwo / szukaj-orzeczen-v2 albo wklejony tekst).
2. **Segmentuj** na role powyżej - przypisz fragmenty, oznacz role nieobecne.
3. **Streść ekstraktywnie** - dla każdej istotnej roli wybierz 1-3 zdania KLUCZOWE i zacytuj je
   dosłownie (z offsetem/stroną), nie parafrazuj.
4. **Wskaż ratio** - jedno-dwa zdania, dla których to orzeczenie się powołuje (zacytuj, nie streszczaj).
5. **Wypisz powołane przepisy i orzeczenia** - przekaż do ekstraktor-cytatow-pl, a dalej do
   citation-grounding-pl do weryfikacji.

## Format wyjścia

```
ORZECZENIE: <sąd>, <sygnatura>, <data>
ROZSTRZYGNIĘCIE (sentencja): "<cytat sentencji>"

STRESZCZENIE EKSTRAKTYWNE (cytaty źródłowe):
- Stan faktyczny: "<zdanie kluczowe>" (s.X)
- Zarzuty: "<...>" (s.X)
- Rozważania sądu: "<zdanie nośne rozumowania>" (s.X)

TEZA / RATIO: "<cytat zdania rozstrzygającego>" (s.X)

POWOŁANE: art. ... ; orzeczenia ...  -> do weryfikacji (ekstraktor-cytatow-pl -> citation-grounding-pl)
ROLE NIEOBECNE: <lista, jeśli brak np. zdania odrębnego>
```

## Granice

- Streszczenie jest ekstraktywne - wierne słowom sądu, ale to nadal wybór zdań; pełną wykładnię
  i ocenę linii orzeczniczej robi prawnik.
- Skill nie ocenia trafności orzeczenia ani nie buduje glosy - dostarcza uporządkowany,
  cytowalny szkielet do dalszej pracy.
- Role retoryczne to model polskiego uzasadnienia; nietypowa struktura (np. orzeczenia TSUE,
  postanowienia wpadkowe) może wymagać ręcznej korekty segmentacji.

## Atrybucja

Metoda (segmentacja orzeczenia przez role retoryczne zdań + streszczenie ekstraktywne) oparta na
**OpenNyAI / Opennyai** (Legal-NLP-EkStep), licencja **MIT**. Indyjskie role i modele NLP porzucone;
role retoryczne polskiego orzeczenia, reguły ekstrakcji i format wyjścia to oryginalne opracowanie
MateMatic. Interpretacja MateMatic, nie stanowisko NRA ani KRRP.
