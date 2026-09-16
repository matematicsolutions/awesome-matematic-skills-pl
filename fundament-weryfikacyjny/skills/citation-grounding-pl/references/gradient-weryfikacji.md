# Gradient weryfikacji - doktryna

Adaptacja modelu Existence / Content / Paragraph z biblioteki Jeanne Sulzer
(`jeannesulzer/international-criminal-tribunals-skills`, CC BY 4.0) na polskie realia prawnicze.

## Po co gradient

Weryfikacja binarna („zweryfikowane / nie") jest fałszywie prosta. W praktyce:

- Retrieval bywa zawodny (SAOS chwilowo niedostępny, dokument tylko w PDF skanie, fragment za paywallem).
- Twierdzenia mają **różną siłę**: „SN skazał 12.03.2019" wymaga mniej niż dosłowny cytat akapitu.
- Najgroźniejsza halucynacja nie jest zmyślonym cytatem w cudzysłowie - jest **parafrazą, która
  przekręca holding** przy prawdziwej sygnaturze. Binarna kontrola cytatów jej nie łapie.

Gradient rozwiązuje to przez dwie zasady:

1. **Trzy poziomy** weryfikacji, stosowane **per twierdzenie**, nie per dokument.
2. **Kalibracja**: siła tezy w deliverable nie może przekraczać osiągniętego poziomu weryfikacji.

## Trzy poziomy

| Poziom | Co potwierdza | Jak weryfikuje skrypt |
|---|---|---|
| **ISTNIENIE** | Kotwica (sygnatura/CELEX, data, organ) jest realna i zgodna z deklaracją | porównanie `anchor` (deklarowane) z `anchor_resolved` (z SAOS/EUR-Lex), z rozwinięciem skrótów i normalizacją dat |
| **TREŚĆ** | Źródło co do istoty zawiera to, co twierdzi output | pokrycie terminów nośnych twierdzenia w tekście źródła (≥70%) - **warunek konieczny, nie wystarczający** |
| **FRAGMENT** | Cytowany akapit/zdanie istnieje dosłownie | string-match znormalizowanego cytatu z dozwolonymi lukami `[...]` |

**Uczciwość mechaniczna:** poziom TREŚĆ NIGDY nie zwraca „zielonego" automatycznie. Obecność
terminów to dowód, że źródło *dotyczy tematu* - nie że *potwierdza tezę*. Status to `WYMAGA_OSADU`:
substancję rozstrzyga człowiek lub paraphrase-judge (kaskada PATRON). Skrypt robi tani pre-filtr i
łapie jaskrawą halucynację (terminy nieobecne → 🔴), ale nie udaje, że zrozumiał znaczenie.

## Macierz: typ twierdzenia → wymagany poziom

Każde powołanie w deliverable sklasyfikuj jednym z typów. To ustawia poprzeczkę.

| `claim_type` | Wymagany poziom | Przykład w tekście | Dlaczego |
|---|---|---|---|
| `cytat_doslowny` | FRAGMENT | „sąd związany jest granicami zaskarżenia" (w cudzysłowie) | cudzysłów obiecuje dosłowność |
| `teza_pinpoint` | FRAGMENT | „jak w pkt 15 uzasadnienia SN wskazał…" | pinpoint akapitu = obietnica lokalizacji |
| `stanowisko_sadu` | TREŚĆ | „SN przyjął, że klauzula jest dopuszczalna" | parafraza holdingu - musi oddać istotę |
| `parafraza` | TREŚĆ | „Trybunał uznał takie ograniczenie za proporcjonalne" | jak wyżej |
| `fakt_proceduralny` | ISTNIENIE | „wyrokiem z 12.03.2019 SN oddalił skargę" | data/skład/rozstrzygnięcie - kotwica wystarcza |
| `powolanie` | ISTNIENIE | „por. II CSK 123/19" | sama sygnatura jako autorytet |

Gdy wątpisz między `stanowisko_sadu` a `cytat_doslowny`: jeśli w tekście są cudzysłowy → FRAGMENT.
Jeśli to relacja własnymi słowami → TREŚĆ. Nie ma „parafrazy zwolnionej z weryfikacji" (to była
luka v1).

## Reguła kalibracji

Po weryfikacji skrypt zna `wymagany_poziom` i `osiagniety_poziom`. Decyzja:

- **osiągnięty ≥ wymagany** → 🟢 `ZWERYFIKOWANY` (lub 🟡 `WYMAGA_OSADU` na poziomie TREŚĆ - osąd substancji).
- **osiągnięty < wymagany, ale temat pokryty** → 🟠 `KALIBRACJA`. Dwie drogi naprawy:
  - **(a) złagodź twierdzenie** do osiągniętego poziomu: zamień dosłowny cytat na parafrazę
    („SN wypowiadał się w przedmiocie dopuszczalności klauzuli waloryzacyjnej…"), usuń cudzysłów.
  - **(b) oznacz pinpoint jako prowizoryczny**: „(cytat do potwierdzenia wobec pełnego tekstu)".
- **brak pokrycia / rozbieżna kotwica** → 🔴 `NIEZWERYFIKOWANY`, twarda blokada.

Zasada nadrzędna (za Sulzer): *„Never invent a paragraph number to fill a gap. If verification
stops at level 4, the output stops at level-4 claims."* Po polsku: **output nie może twierdzić
mocniej, niż sięga weryfikacja.**

## Pułapka „prawdziwy cytat, fałszywa teza"

Cytat dosłowny może być 🟢 na poziomie FRAGMENT, a otaczające zdanie nadal kłamać o tym, co sąd
orzekł (np. cytat z części opisowej podany jako rozstrzygnięcie; zdanie odrębne podane jako
stanowisko składu). Dlatego przy `cytat_doslowny`, który **podpiera tezę o stanowisku sądu**,
dodaj drugi rekord `stanowisko_sadu` z `claim_text` = twierdzeniem otaczającym. FRAGMENT potwierdza
że słowa są; TREŚĆ + osąd potwierdza że znaczą to, co im przypisano. To polski odpowiednik
dyscypliny „majority Judgment vs separate opinions" z biblioteki trybunałów.
