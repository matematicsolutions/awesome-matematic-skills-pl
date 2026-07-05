---
name: hierarchia-zrodel-pl
description: >-
  Routing autorytetu źródła PRZED udzieleniem odpowiedzi prawnej - mapuje pytanie
  na warstwy źródeł prawa polskiego i unijnego (Konstytucja, ratyfikowane umowy
  międzynarodowe, prawo UE z zasadą pierwszeństwa, ustawy, rozporządzenia,
  akty prawa miejscowego, orzecznictwo TK/SN/NSA/TSUE/ETPC, soft law),
  ustala kolejność weryfikacji, sprawdza reguły kolizyjne i wskazuje konektor
  MCP do każdej warstwy. Używaj gdy: "gdzie to sprawdzić", "jaka hierarchia
  źródeł", "które źródło ma pierwszeństwo", "od czego zacząć research",
  "mapa źródeł do pytania", przed każdym researchem prawnym bez oczywistego
  źródła.
license: Apache-2.0
allowed-tools: [Read]
data-residency: local
requires-human-approval: false
pii-egress: none
metadata:
  author: "Wiesław Mazur / MateMatic"
  version: "1.0.0"
  inspiration: "swiss-legal-source-authority-triage (Enrique G. Zbinden, MIT) - wzorzec 'route authority before answer'; treść PL/UE napisana od zera"
  companion_skills: "citation-grounding-pl, legal-request-router-pl, saos-orzecznictwo, eu-sparql-search, legal-data-hunter-pl"
---

# Hierarchia źródeł PL - routing autorytetu przed odpowiedzią

## Filozofia

Zanim powstanie odpowiedź prawna, trzeba wiedzieć, które źródło ją kontroluje.
Model, który zaczyna od wniosku i dopiero potem dobiera przepis, robi to w złej
kolejności - najpierw mapa warstw, potem research, na końcu teza.

Ten skill jest warstwą PRZED groundingiem. Rozgraniczenie trzech skilli:

- **hierarchia-zrodel-pl** (ten skill) mówi GDZIE i W JAKIEJ KOLEJNOŚCI szukać,
- **citation-grounding-pl** weryfikuje, CZY cytat i sygnatura są prawdziwe,
- **legal-request-router-pl** decyduje, JAKĄ kontrolę dać gotowemu wynikowi.

Skill nie udziela porady prawnej. Produkuje mapę źródeł i kolejność weryfikacji.
Wynik jest projektem do przejścia przez bramkę człowieka.

## Kiedy używać

- Pytanie prawne bez oczywistego, jednego źródła ("czy pracodawca może...",
  "czy klauzula jest ważna...", "jakie sankcje za...").
- Użytkownik pyta wprost: gdzie to sprawdzić, od czego zacząć, co ma
  pierwszeństwo, jaka jest hierarchia.
- Przed odpaleniem konektorów - żeby nie strzelać do baz na ślepo, tylko wg
  ustalonej kolejności warstw.
- Gdy w grze może być prawo UE, umowa międzynarodowa albo kolizja przepisów.

## Czego NIE robi

- Nie weryfikuje treści cytatu ani istnienia sygnatury - to citation-grounding-pl.
- Nie ocenia stawki sprawy i nie wybiera ścieżki kontroli - to legal-request-router-pl.
- Nie odpowiada na pytanie prawne merytorycznie - dostarcza mapę, nie wniosek.
- Nie zastępuje wyszukiwania w bazach - wskazuje konektor, samo nie pobiera.
- Nie rozstrzyga sporu Konstytucja vs prawo UE - taką kolizję flaguje człowiekowi.

## Mapa warstw

### Warstwa 1 - źródła powszechnie obowiązujące (Konstytucja art. 87-94)

Katalog jest ZAMKNIĘTY - jeśli akt nie mieści się w art. 87 Konstytucji,
nie wiąże obywatela.

| # | Źródło | Podstawa | Uwagi kolizyjne |
|---|---|---|---|
| 1 | Konstytucja RP | art. 8 ust. 1 | najwyższe prawo RP |
| 2 | Ratyfikowane umowy międzynarodowe | art. 91 | za zgodą ustawową: pierwszeństwo przed ustawą (art. 91 ust. 2) |
| 3 | Prawo UE | art. 91 ust. 3 + traktaty | pierwszeństwo przed ustawą; patrz niżej |
| 4 | Ustawy | art. 87 ust. 1 | rdzeń researchu krajowego |
| 5 | Rozporządzenia wykonawcze | art. 92 | tylko na podstawie szczegółowego upoważnienia ustawowego i w jego granicach |
| 6 | Akty prawa miejscowego | art. 87 ust. 2, art. 94 | wiążą na obszarze działania organu |
| - | Akty wewnętrzne (uchwały RM, zarządzenia) | art. 93 | NIE wiążą obywatela - tylko jednostki podległe; nie mogą być podstawą decyzji wobec obywatela |

Prawo UE w tej mapie:

- **Rozporządzenia UE** - stosowane bezpośrednio, bez transpozycji.
- **Dyrektywy** - wiążą co do rezultatu; sprawdź akt transpozycji do prawa PL;
  po upływie terminu transpozycji możliwy skutek bezpośredni wertykalny
  (jednostka vs państwo), jeśli przepis jest jasny, bezwarunkowy i precyzyjny.
- **Zasada pierwszeństwa** - kolizja ustawa PL vs prawo UE: stosuje się prawo UE
  (Costa v ENEL, 6/64); skutek bezpośredni od Van Gend en Loos (26/62).
- Kolizja prawo UE vs Konstytucja RP - nie rozstrzygaj, flaguj do człowieka.

### Warstwa 2 - orzecznictwo (autorytet bez formalnego precedensu)

Polska nie zna precedensu w sensie common law, ale warstwa orzecznicza faktycznie
steruje wykładnią. Status każdego sądu jest inny:

| Sąd | Status autorytetu |
|---|---|
| TK | orzeczenia mają moc powszechnie obowiązującą i są ostateczne (art. 190 ust. 1 Konstytucji) |
| SN | uchwały; uchwały składu 7 sędziów mogą uzyskać moc zasady prawnej - wiążą składy SN [DO SPRAWDZENIA - art. 87-88 ustawy o SN z 2017 r.] |
| NSA | uchwały 7 sędziów / całej izby - wiążą składy sądów administracyjnych w danej sprawie i pośrednio linię orzeczniczą |
| TSUE | wykładnia prawa UE wiąże sądy krajowe; pytania prejudycjalne (art. 267 TFUE) |
| ETPC | wyroki wiążą państwo-stronę w sprawie; linia strasburska jako autorytet wykładni EKPC |

### Warstwa 3 - soft law (chroni adresata, nie jest źródłem prawa)

| Instrument | Organ | Charakter |
|---|---|---|
| Interpretacje ogólne | MF | ochrona każdego, kto się zastosuje |
| Interpretacje indywidualne | KIS | ochrona wnioskodawcy |
| Objaśnienia podatkowe | MF | ochrona jak przy interpretacji ogólnej |
| Wytyczne i decyzje | UODO / EROD | praktyka organu, nie przepis |
| Wytyczne, decyzje, wyjaśnienia | UOKiK | praktyka organu |
| Stanowiska i komunikaty | KNF | oczekiwania nadzorcze |

Soft law nigdy nie wygrywa kolizji z ustawą. Cytuj jako praktykę organu,
wyraźnie oddzieloną od normy.

## Workflow

1. **Klasyfikuj pytanie do warstw.** Które warstwy mogą kontrolować odpowiedź?
   Zwykle 2-3 (np. RODO: rozporządzenie UE + ustawa krajowa + wytyczne EROD/UODO
   + orzecznictwo TSUE).
2. **Ustal kolejność weryfikacji.** Od najwyższej warstwy w dół: norma
   nadrzędna wyznacza ramy, zanim spojrzysz na przepis wykonawczy czy praktykę
   organu. Soft law czyta się NA KOŃCU, na tle normy.
3. **Sprawdź kolizje.** Reguły: lex superior derogat legi inferiori,
   lex specialis derogat legi generali, lex posterior derogat legi priori
   (ale lex posterior generalis non derogat legi priori speciali). Plus
   pierwszeństwo prawa UE przed ustawą. Kolizję nierozstrzygalną regułami
   flaguj człowiekowi.
4. **Wskaż konektor do każdej warstwy:**

   | Warstwa | Konektor |
   |---|---|
   | Ustawy, rozporządzenia, teksty jednolite (ISAP) | sejm-eli-mcp |
   | Orzecznictwo SN / TK / sądy powszechne / KIO | saos-orzecznictwo + szukaj-orzeczen-v2 |
   | Prawo UE, orzecznictwo TSUE (EUR-Lex) | eu-sparql-search |
   | Decyzje i wytyczne UODO | uodo-grounding-pl |
   | Orzecznictwo KIO (zamówienia publiczne) | kio-grounding-pl |
   | Stan rejestrowy podmiotu (KRS) | krs-grounding-pl |

5. **Flaguj wersję czasową.** Zawsze trzy pytania:
   - stan prawny na DZIEŃ ZDARZENIA czy na dziś? (research pod spór = wersja
     z daty zdarzenia; compliance = wersja obowiązująca dziś),
   - vacatio legis - czy akt już wszedł w życie, czy dopiero wejdzie,
   - przepisy przejściowe i dostosowujące - czy stara norma nie żyje dalej
     dla spraw w toku.

## Format wyniku

Zwracaj dokładnie ten szablon:

```markdown
# Mapa źródeł: [pytanie w jednym zdaniu]

Stan prawny na dzień: [data zdarzenia / dziś - wybór uzasadnij]

| Warstwa | Akt / źródło | Konektor | Status weryfikacji | Flagi |
|---|---|---|---|---|
| Prawo UE | [rozporządzenie / dyrektywa + art.] | eu-sparql-search | zweryfikowane / do sprawdzenia | [transpozycja? skutek bezpośredni?] |
| Ustawa | [ustawa + art.] | sejm-eli-mcp | zweryfikowane / do sprawdzenia | [wersja czasowa, vacatio legis] |
| Rozporządzenie | [akt wykonawczy] | sejm-eli-mcp | zweryfikowane / do sprawdzenia | [upoważnienie ustawowe aktualne?] |
| Orzecznictwo | [TK / SN / NSA / TSUE / ETPC] | saos-orzecznictwo / eu-sparql-search | do sprawdzenia | [uchwała? zasada prawna? linia zmienna?] |
| Soft law | [interpretacja / wytyczne / stanowisko] | uodo-grounding-pl (poza UODO: brak konektora - weryfikacja ręczna) | do sprawdzenia | [nie jest źródłem prawa] |

## Kolejność weryfikacji
1. [źródło] - bo [reguła hierarchii]
2. ...

## Kolizje
[lex superior / specialis / posterior / pierwszeństwo UE - albo "nie wykryto";
kolizja nierozstrzygalna -> bramka człowieka]

## Flagi czasowe
[wersja przepisu, vacatio legis, przepisy przejściowe - albo "brak"]

## Do bramki człowieka
[co wymaga decyzji prawnika zanim powstanie odpowiedź]
```

Artykuł, którego nie potwierdzono w bazie w tej sesji, oznaczaj
[DO SPRAWDZENIA] - nigdy nie podawaj numeru z pamięci jako pewnika.

## Bramka człowieka

Mapa źródeł to projekt researchu, nie odpowiedź prawna. Uprawniony człowiek:

- zatwierdza wybór stanu prawnego (data zdarzenia vs dziś),
- rozstrzyga kolizje, których nie zamykają reguły (zwłaszcza Konstytucja vs UE),
- ocenia aktualność linii orzeczniczej,
- bierze odpowiedzialność za odpowiedź zbudowaną na tej mapie.

Nic nie wychodzi do klienta na podstawie samej mapy.

## Companion skills

- **citation-grounding-pl** - następny krok: weryfikacja, czy pobrane cytaty
  i sygnatury są prawdziwe.
- **legal-request-router-pl** - warstwa nad wynikiem: jaka ścieżka kontroli
  (zwykła odpowiedź / grounding / debata / paczka audytowa).
- **saos-orzecznictwo**, **eu-sparql-search** - konektory wykonawcze mapy.
- **legal-data-hunter-pl** - gdy warstwa nie ma konektora i trzeba znaleźć
  źródło danych.
