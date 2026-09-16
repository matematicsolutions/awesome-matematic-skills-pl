# Drabinka źródeł PL - co robić, gdy bezpośredni fetch zawiedzie

Adaptacja „fallback ladder" z biblioteki Jeanne Sulzer (CC BY 4.0). U Sulzer drabinka prowadzi
przez publiczne archiwa międzynarodowe (icc-cpi.int → legal-tools.org → snippet → press release).
Tutaj prowadzi przez polskie/unijne źródła. **Awaria bezpośredniego pobrania to stan normalny,
nie porażka** - pracuj drabinkę, zatrzymaj się na pierwszym szczeblu, który daje to, czego
wymaga poziom twierdzenia.

## Drabinka dla orzecznictwa PL

1. **SAOS przez `saos-orzecznictwo` / `szukaj-orzeczen-v2`.** Pełna treść + metadane (data, organ,
   skład, hasła). To zarazem **resolver kotwicy** (ISTNIENIE) i źródło tekstu (TREŚĆ/FRAGMENT).
   Z metadanych zbuduj `anchor_resolved`.
2. **Portal Orzeczeń Sądów Powszechnych / strona danego sądu** - gdy orzeczenia nie ma w SAOS
   (część SO/SR publikuje u siebie). Treść + sygnatura potwierdzają ISTNIENIE i często TREŚĆ.
3. **Baza SN / NSA / TK (orzeczenia.nsa.gov.pl, ipo.trybunal.gov.pl, sn.pl).** Dla najwyższych
   instancji często pełniejsze niż SAOS, z oficjalnym tekstem uzasadnienia.
4. **Snippet z wyszukiwarki z domeny Tier-1** - gdy treść niedostępna, a potrzebujesz potwierdzić
   samo ISTNIENIE. Wynik wyszukiwania cytujący sygnaturę + datę z domeny sądowej = poziom ISTNIENIE
   (dokument istnieje), zwykle NIE poziom FRAGMENT (snippety są krótkie, nie pokrywają się z akapitami).
5. **Zapytaj użytkownika o dokument** - kancelaria często ma dostęp do LEX/Legalis/zbioru własnego,
   którego skill nie ma. Poproś o wklejenie pełnego tekstu lub PDF (→ markitdown/opendataloader-pdf).

**Nigdy** nie wymyślaj numeru akapitu ani sygnatury, by zapełnić lukę. Jeśli weryfikacja staje na
szczeblu 4 (samo ISTNIENIE), output zatrzymuje się na twierdzeniach poziomu ISTNIENIE - przez
status `KALIBRACJA`.

## Drabinka dla aktów i orzecznictwa UE

1. **`eu-sparql-search`** - CELEX → metadane (resolver kotwicy) + treść w wybranym języku.
2. **EUR-Lex bezpośrednio** (eur-lex.europa.eu) po numerze CELEX.
3. **Snippet z curia.europa.eu / eur-lex** - potwierdzenie ISTNIENIA, gdy treść niedostępna.
4. **Zapytaj użytkownika.**

Uwaga: dla aktów/wyroków UE **wersja językowa ma znaczenie** - jeśli output cytuje po polsku,
weryfikuj wobec polskiej wersji (tłumaczenia bywają jedynym tekstem, ale różnice terminologiczne
są realne). Flaguj zależność od tłumaczenia, zamiast ją maskować.

## Drabinka dla ustaw PL / umów / pism

1. **ISAP (isap.sejm.gov.pl)** dla ustaw i rozporządzeń - tekst ujednolicony + metryka.
2. **Dokument dostarczony przez użytkownika** (umowa, pismo, akta) - jedyne źródło dla materiałów
   niepublicznych. Bez niego status = `BRAK ŹRÓDŁA`, nie „prawdopodobnie ok".
3. Dla materiałów objętych tajemnicą zawodową: pseudonimizuj przez `let-it-be` PRZED weryfikacją.

## Dopasowanie szczebla do poziomu (skrót)

| Szczebel drabinki daje… | …a to wystarcza na poziom |
|---|---|
| metadane (data, organ, sygnatura) z Tier-1 | **ISTNIENIE** |
| pełny tekst uzasadnienia | **TREŚĆ** i **FRAGMENT** |
| sam snippet z wyszukiwarki | **ISTNIENIE** (nie FRAGMENT) |
| brak czegokolwiek | `BRAK ŹRÓDŁA` - zatrzymaj twierdzenie |

Reguła nadrzędna: **output nie twierdzi mocniej, niż sięga najwyższy osiągnięty szczebel.**
