---
name: ekstraktor-cytatow-pl
description: >
  Deterministyczny ekstraktor cytatów prawnych z polskiego pisma - znajduje WSZYSTKIE
  odwołania (sygnatury sądów, ECLI, identyfikatory Dz.U./M.P./ELI, powołane przepisy),
  normalizuje je, deduplikuje i rozwiązuje odwołania skrótowe (tamże, op. cit., wyżej
  powołany wyrok) do antecedentu. Front-end do citation-grounding-pl: najpierw znajdź
  każdy cytat, potem zweryfikuj. Mechaniczny, bez LLM przy ekstrakcji (regex + reguły),
  RODO-safe (lokalnie). Uzywaj gdy: "wypisz wszystkie cytaty z tego pisma", "jakie
  orzeczenia sa powolane", "lista sygnatur", "wyciagnij przepisy z opinii", "ekstrakcja
  cytatow", "co tu jest cytowane", przed groundingiem / przed wyslaniem pisma /
  przy audycie cudzego pisma.
license: Apache-2.0
allowed-tools: [Read]
data-residency: local
requires-human-approval: false
pii-egress: none
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.0.0
  inspiration: >
    Architektura ekstrakcja -> agregacja -> adnotacja oparta na eyecite (Free Law Project),
    licencja BSD-2-Clause (https://github.com/freelawproject/eyecite). Amerykanskie wzorce
    reporterow porzucone; wzorce sygnatur PL, ECLI, Dz.U./ELI i logika antecedentow napisane
    od zera dla realiow polskich.
  companion_skills: citation-grounding-pl, saos-orzecznictwo, eu-sparql-search, legal-ai-audit-bundle
---

# Ekstraktor cytatów PL - znajdź każdy cytat, zanim go zweryfikujesz

## Filozofia

**Zweryfikować można tylko to, co się najpierw znajdzie.** Grounding cytatu (citation-grounding-pl)
sprawdza, czy dany cytat istnieje w źródle - ale działa na liście cytatów, którą ktoś musi najpierw
zebrać. Ten skill jest tym front-endem: przechodzi pismo i wypisuje WSZYSTKIE odwołania, tak by żadne
nie wymknęło się weryfikacji. Pominięty cytat to cytat niesprawdzony.

Ekstrakcja jest **mechaniczna** (wzorce + reguły, nie LLM) - to celowe: model na etapie znajdowania
cytatów mógłby jeden przeoczyć albo dopowiedzieć. Lokalnie, RODO-safe.

## Trzy kroki (za eyecite, zlokalizowane do PL)

1. **Ekstrakcja** - rozpoznaj i wyłap każde odwołanie wg wzorców PL poniżej.
2. **Agregacja** - rozwiąż odwołania skrótowe (tamże / op. cit. / wyżej powołany wyrok) do
   pełnego antecedentu, żeby policzyć je jako jeden cytat, nie kilka.
3. **Przekazanie** - oddaj ustrukturyzowaną listę do citation-grounding-pl do weryfikacji string-match.

## Wzorce odwołań (PL)

### Sygnatury orzeczeń
- **SN / sądy powszechne**: izba rzymska + litera wydziału + numer/rok, np. `II CSK NN/RR`, `I KZP NN/RR`, `III CZP NN/RR` (NN = numer, RR = rok - placeholdery).
- **Sądy administracyjne**: NSA `II FSK NNNN/RR`; WSA z oznaczeniem siedziby przez ukośnik, np. `III SA/Wa NNN/RR`, `I SA/Gd NN/RR`.
- **Trybunał Konstytucyjny**: `K 1/20`, `P 7/19`, `SK 3/18`, `Ts 45/20`.
- **KIO** (zamówienia publiczne): `KIO NNN/RR`, sprawy łączone `KIO NNN/RR, KIO NNN/RR`.
- **TSUE**: `C-123/20`, odwoławcze `C-123/20 P`, sprawy połączone `C-123/20 i C-124/20`; Sąd UE `T-456/19`.

### ECLI
- Polski: `ECLI:PL:SN:2015:IICSK24515`, `ECLI:PL:NSA:2018:...`.
- Unijny: `ECLI:EU:C:2020:559`, `ECLI:EU:T:2019:...`.

### Akty prawne (Dz.U. / M.P. / ELI / UE)
- `Dz.U. 2020 poz. 1234`, `Dz.U. z 2020 r. poz. 1234`, starszy format `Dz.U. z 2020 r. Nr 5, poz. 100`.
- `M.P. 2019 poz. 50`; `Dz.Urz. UE L 119` (RODO), `Dz.Urz. UE C ...`.
- ELI URI Sejmu, np. `.../DU/2020/1234`.

### Powołane przepisy
- `art. 415 KC`, `art. 5 ust. 1 lit. a RODO`, `art. 233 § 1 KPC`, `§ 3 ust. 2` (akt wykonawczy).

## Agregacja - odwołania skrótowe (antecedenty PL)

Rozwiąż do pełnego cytatu powołanego wcześniej:
`tamże`, `ibidem`, `op. cit.`, `tak też`, `cyt. wyżej`, `wyżej powołany/przywołany wyrok`,
`powołane orzeczenie`, `j.w.`. Każde takie odwołanie wskazuje na ostatni zgodny antecedent
w tekście - policz je jako ten sam cytat, ale zachowaj miejsce wystąpienia.

## Format wyjścia

```
ZNALEZIONE CYTATY (n):
| # | Typ | Cytat (znormalizowany) | Wystąpienia (offset/strona) | Antecedent (jeśli skrót) |
| 1 | orzeczenie SN | II CSK NN/RR | s.3, s.7 (tamże) | - |
| 2 | przepis | art. 415 KC | s.4 | - |
| 3 | akt | Dz.U. 2020 poz. 1234 | s.2 | - |

DO WERYFIKACJI: przekaż kolumnę "Cytat" do citation-grounding-pl.
```

## Granice

- Ekstrakcja wyłapuje odwołania o znanym formacie. Cytat opisowy bez sygnatury („wyrok SN w sprawie
  rękojmi") nie ma czego dopasować - oznacz jako `bez sygnatury, do ręcznego sprawdzenia`.
- To nie jest weryfikacja istnienia - od tego jest citation-grounding-pl. Ten skill mówi „co jest
  cytowane", nie „czy cytat prawdziwy".
- Wzorce pokrywają najczęstsze formaty; nietypowy zapis sygnatury może umknąć - przy audycie
  wysokiej stawki przejrzyj też ręcznie.

## Atrybucja

Architektura (ekstrakcja -> agregacja -> adnotacja, logika antecedentów) zainspirowana **eyecite**
(Free Law Project), licencja **BSD-2-Clause**. Amerykańskie wzorce reporterów porzucone; wzorce
sygnatur PL, ECLI, Dz.U./ELI i reguły antecedentów to oryginalne opracowanie MateMatic.
Interpretacja MateMatic, nie stanowisko NRA ani KRRP.
