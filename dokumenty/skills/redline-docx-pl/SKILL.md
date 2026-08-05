---
name: redline-docx-pl
description: Redlining polskich umow i pism w .docx z natywnymi Word Track Changes - bez niszczenia formatowania OOXML. Czyta .docx do Markdown (CriticMarkup) dla LLM, aplikuje zmiany jako sledzone (w:ins/w:del) + komentarze, i robi sanitize przed wyslaniem (strip metadanych autora, last-modified-by, rsid, timestampy - RODO przy wysylce pisma). Silnik = adeu (MIT). Use when the user wants to nanosic poprawki w umowie/pismie .docx, zrobic redline/tryb sledzenia zmian, czytac docx dla LLM bez utraty formatowania, przygotowac pismo do wyslania (usunac metadane autora z Worda), porownac dwie wersje .docx, lub mentions track changes / sledzenie zmian / redline / .docx / DOCX.
license: MIT
attribution:
  - source: dealfluence/adeu
    url: https://github.com/dealfluence/adeu
    license: MIT
    relationship: dependency
    note: >
      Silnik konwersji i aplikacji zmian, wolany przez uvx. Skill go opakowuje,
      nie wywodzi sie z jego kodu.
  - source: evolsb/legal-redline-tools
    url: https://github.com/evolsb/legal-redline-tools
    license: MIT
    relationship: pattern-only
    note: >
      Wzorce memo negocjacyjnego (tier/rationale/walkaway/precedent) i skanera
      placeholderow. Oba skrypty napisane od zera pod realia polskie.
  - source: genspark-ai/genoffice
    url: https://github.com/genspark-ai/genoffice
    license: Apache-2.0
    relationship: vendored
    note: >
      packages/docx-engine wendorowany do vendor/docx-engine (commit 8f52328,
      Apache-2.0). Silnik round-trip po bajtach. Zmierzony 2026-08-05 (round-trip,
      sledzone zmiany, tabele), NIE wpiety w workflow skilla - sledzonych zmian
      nie robi poprawnie na sciezce blokowej. Szczegoly i wykaz zmian
      w vendor/docx-engine/NOTICE i README.md.
allowed-tools: [Bash, Read, Write, Edit]
data-residency: local
requires-human-approval: true
pii-egress: none
---

# Redline DOCX po polsku

Wrapper nad **adeu** (MIT, Dealfluence Oy) - dwukierunkowy konwerter miedzy `.docx`
a Markdown (CriticMarkup), z aplikacja zmian z powrotem do `.docx`. Robi to,
czego `python-docx` NIE potrafi: wstrzykuje **natywne Word Track Changes**
(`w:ins`/`w:del`) i komentarze, zachowujac formatowanie, fonty i marginesy.

Cala praca lokalnie (uvx, brak chmury). Silnik testowany na polskim .docx 2026-05-22
(extract/apply/sanitize - patrz [THIRD_PARTY_INSPIRATIONS.md](THIRD_PARTY_INSPIRATIONS.md)).

## Wymagania

`uv` (jezeli brak: `pip install uv`). adeu pobiera sie samo przez `uvx adeu` przy pierwszym uzyciu (wersja sprawdzona: 1.7.5).

## Safety Tiers (KRYTYCZNE)

Przed wykonaniem każdej operacji ustal tier i zastosuj regułę:

| Tier | Operacje | Reguła |
|------|----------|--------|
| **R - Read-only** | `extract` (czytanie .docx), `skan_placeholder.py`, `memo_negocjacyjne.py` (pisza tylko nowe pliki raportu/memo) | Bez potwierdzenia. Wykonaj od razu. |
| **M - Mutating** | `apply`, `diff`, `apply --live` | Pokaż użytkownikowi proponowane zmiany. Czekaj na potwierdzenie słowne. |
| **D - Destructive** | `sanitize --accept-all` (akceptuje wszystkie zmiany nieodwracalnie) | Użytkownik musi wpisać dosłownie: **"potwierdzam"** zanim wykonasz. |

---

## Workflow (4 kroki)

### 1. Czytaj - .docx do Markdown dla LLM

```bash
uvx adeu extract umowa.docx -o umowa.md
```

Zwraca czysty Markdown (+ opcjonalny Semantic Appendix: defined terms, cross-references,
typos). LLM pracuje na semantyce, nie na surowym OOXML - kilkukrotnie mniej tokenow
niz wrzucenie pliku w postaci binarnej.

### 2. Przygotuj liste zmian - edits.json

Format to lista obiektow `modify` (search-and-replace na tekscie, NIE na pozycji):

```json
[
  {
    "type": "modify",
    "target_text": "sad wlasciwy dla siedziby Zleceniodawcy",
    "new_text": "Sad Arbitrazowy przy KIG w Warszawie",
    "comment": "Proponuje arbitraz zamiast sadu powszechnego."
  }
]
```

`target_text` musi byc jednoznaczny - adeu blokuje niejednoznaczne dopasowania
ZANIM dotkna pliku (bramka walidacji). Jezeli fragment wystepuje kilka razy,
doprecyzuj kontekst.

#### Rozszerzenie schematu - pola negocjacyjne (opcjonalne)

Kazdy obiekt `modify` moze dostac cztery dodatkowe pola. Sluza one memo
negocjacyjnemu (krok 2a), NIE trafiaja do adeu ani do drugiej strony:

```json
[
  {
    "type": "modify",
    "target_text": "kara umowna w wysokosci 20% wartosci umowy",
    "new_text": "kara umowna w wysokosci 5% wartosci umowy, lacznie nie wiecej niz 10%",
    "comment": "Proponujemy ograniczenie kary umownej.",
    "tier": 1,
    "rationale": "20% bez limitu lacznego to ekspozycja nieproporcjonalna do wartosci kontraktu.",
    "walkaway": "Maksymalnie 10% z limitem lacznym 15%. Powyzej tego nie podpisujemy.",
    "precedent": "Umowa z kontrahentem X (2025): 5% z limitem 10% przeszlo bez sporu."
  }
]
```

| Pole | Znaczenie |
|------|-----------|
| `tier` | Priorytet 1-3 (framework nizej). |
| `rationale` | Uzasadnienie zmiany - argument do rozmowy, nie do dokumentu. |
| `walkaway` | Granica ustepstwa: co akceptujemy najdalej i kiedy odchodzimy od stolu. |
| `precedent` | Odwolanie do porownywalnej umowy lub wczesniejszej negocjacji. |

Rozdzial widocznosci jest twardy: `comment` widzi druga strona (komentarz w
track changes), `rationale`/`walkaway`/`precedent` zostaja w memo wewnetrznym.

#### Framework Tier 1-3 - kategorie ryzyka

| Tier | Kategoria | Regula negocjacyjna |
|------|-----------|---------------------|
| **1** | Warunki brzegowe (non-starter) | Bez tej zmiany umowy nie podpisujemy. Pozycja `walkaway` obowiazkowa - memo bez niej nie przejdzie walidacji. |
| **2** | Istotne | Realne ryzyko prawne lub finansowe. Negocjuj, ustepstwo tylko za cos. |
| **3** | Pozadane | Poprawia nasza pozycje, ale mozna odpuscic bez straty. Waluta wymienna za tier 2. |

Brak `tier` = pozycja nieskategoryzowana; memo wypisze ja osobno jako zaleglosc
do klasyfikacji przez prawnika.

### 2a. Memo negocjacyjne (opcjonalne, dokument WEWNETRZNY)

```bash
# sciezka scripts/ wzgledem katalogu tego skilla; z katalogu sprawy podaj pelna
python scripts/memo_negocjacyjne.py edits.json -o memo.md --tytul "Umowa serwisowa - kontrahent X"
python scripts/memo_negocjacyjne.py edits.json --adeu edits_adeu.json   # kopia bez pol memo, do kroku 3
```

Generuje memo w Markdown: zmiany pogrupowane wg tierow, naglowek poufnosci,
licznik zmian per tier, przy kazdej pozycji rationale / walkaway / precedent.
Skrypt zero-dep (Python stdlib). Walidacja: tier spoza 1-3 lub tier 1 bez
`walkaway` = exit 1.

**Granica governance**: memo to draft do rozmowy, nie automat. Negocjacje
prowadzi czlowiek - skrypt przygotowuje mu mape pozycji, niczego nie wysyla
i nie rozstrzyga. Memo NIGDY nie idzie do drugiej strony (naglowek poufnosci
jest w szablonie na stale). Do adeu `apply` podawaj kopie z `--adeu` - pola
negocjacyjne nie moga trafic do pliku wymienianego z kontrahentem.

### 3. Aplikuj - natywne Track Changes

```bash
uvx adeu apply umowa.docx edits.json -o umowa_redline.docx --author "Kancelaria"
```

Daje `umowa_redline.docx` ze sledzonymi zmianami i komentarzami. Bez `--author`
adeu wpisuje nazwe konta systemowego biezacego uzytkownika - **zawsze podawaj
`--author` jawnie**, zeby nie wyciekla nazwa konta do dokumentu.

### 3a. Skan placeholderow - bramka "czy draft nie wychodzi z dziurami"

```bash
# sciezka scripts/ wzgledem katalogu tego skilla, jak w kroku 2a
python scripts/skan_placeholder.py umowa_redline.docx        # tez .md / .txt, wiele plikow naraz
python scripts/skan_placeholder.py umowa_redline.docx --json # raport maszynowy
```

Wykrywa niedokonczone pola: `[...]`, `[   ]`, `[wstaw ...]`, `[insert ...]`,
`TBD`, `DO UZUPELNIENIA`, `$X` / `$___`, ciagi podkreslen `___`, placeholder
sygnatury `NN/RR`, puste pola dat (`dnia __`, `[data]`) i kwot (`[kwota]` oraz
kazde `0,00 zl` - czesty artefakt niewypelnionego pola; jezeli kwota zerowa
jest zamierzona, odnotuj to przy przekazaniu). Raport `plik:pozycja` (paragraf w .docx,
linia w tekscie) + fragment kontekstu.

Zero zaleznosci (Python stdlib, .docx czytany przez `zipfile`). Exit 0 = czysto,
exit 1 = znaleziska. **Kazde znalezisko blokuje wysylke** - najpierw uzupelnij
pole albo swiadomie zostaw (np. kwota do wpisania przez klienta) i odnotuj to
przy przekazaniu draftu czlowiekowi.

### 4. Sanitize PRZED wyslaniem - RODO

```bash
uvx adeu sanitize umowa_redline.docx -o umowa_clean.docx --keep-markup --author "Kancelaria" --report
```

Usuwa: `creator`, `last modified by`, template, `rsid`, custom XML parts;
normalizuje timestampy; podmienia autorow track-changes/komentarzy na jedna nazwe.
`--keep-markup` zachowuje sledzone zmiany (do negocjacji); bez tego (`--accept-all`)
akceptuje wszystko i zwraca czysty dokument. Konczy werdyktem `Result: CLEAN`.

> **Zawsze rob sanitize przed wyslaniem pisma na zewnatrz.** Word zostawia w metadanych
> nazwiska autorow, sciezki szablonow i historie edycji - to wyciek danych.

## Pozostale komendy

```bash
uvx adeu diff v1.docx v2.docx          # wizualny diff dwoch wersji
uvx adeu apply --live edits.json       # edycja zywego dokumentu w Word (Windows + MS Word)
```

## Integracja z let-it-be (PII PL)

`sanitize` czysci **metadane** Worda, ale NIE tresc. Do anonimizacji tresci (PESEL,
NIP, nazwiska w fleksji) najpierw przepusc tekst przez [`let-it-be`](../let-it-be), potem redline:

1. `let-it-be` -> pseudonimizuj tresc pisma (PII -> tokeny)
2. praca/redline na zpseudonimizowanej wersji
3. `adeu sanitize` -> domkniecie metadanych przed wyslaniem

let-it-be = tresc (RODO art. 4 dane osobowe w tekscie); adeu sanitize = metadane pliku.
Dwie rozne warstwy wycieku, obie trzeba domknac.

## Ograniczenia

- Live MS Word tylko Windows + zainstalowany Word (backend Python).
- `target_text` na dopasowaniu tekstu - przy duplikatach trzeba kontekstu.
- adeu to narzedzie wspomagajace, NIE zastepuje weryfikacji przez prawnika.
- Silnik zewnetrzny (adeu, Dealfluence) - przy aktualizacji wersji zrob ponowny smoke test.
- W `vendor/docx-engine/` lezy DRUGI silnik (GenOffice, Apache-2.0), zweryfikowany
  pomiarowo, ale **NIE wpiety w zaden krok workflow**. Workflow stoi w calosci na adeu.
  Nie wolaj go z tego skilla, dopoki nie zapadnie decyzja opisana nizej.

## Atrybucja

Silnik: [adeu](https://github.com/dealfluence/adeu) (c) 2026 Dealfluence Oy, licencja MIT.

Wzorce memo negocjacyjnego (pola tier/rationale/walkaway/precedent, grupowanie
wg tierow) i skanera placeholderow: [evolsb/legal-redline-tools](https://github.com/evolsb/legal-redline-tools)
(MIT). PATTERN, nie kod - oba skrypty napisane od zera pod polskie realia
(wzorce PL: `DO UZUPELNIENIA`, `NN/RR`, `dnia __`, kwoty w zl) i pod format
edits.json adeu zamiast ich wlasnego formatu redlines.

Silnik wendorowany (NIEAKTYWNY): [`vendor/docx-engine/`](vendor/docx-engine/) - `packages/docx-engine`
z [genspark-ai/genoffice](https://github.com/genspark-ai/genoffice) (Apache-2.0, commit `8f52328`),
redystrybuowany razem z LICENSE i NOTICE zgodnie z sekcjami 4(b) i 4(d) tej licencji.

Szczegoly i snapshoty licencji: [THIRD_PARTY_INSPIRATIONS.md](THIRD_PARTY_INSPIRATIONS.md).

## Drugi silnik - dlaczego lezy nieaktywny

W `vendor/docx-engine/` lezy silnik round-tripu po bajtach z GenOffice (Apache-2.0),
zmierzony 2026-08-05 na pismach z maszyny WM. **Nie zastepuje adeu** i nie wolno
go wolac z tego workflow.

Pomiar sledzonych zmian (2026-08-05 wieczor, 71 pism) rozstrzygnal, ze pole
`SaveBlock.revision` NIE produkuje Word Track Changes: `w:ins`/`w:del` laduja na
poziomie `w:body`, tekst usuniety zostaje w `w:t` zamiast `w:delText`, a niezalezny
czytnik (`adeu extract`) nie widzi zmiany w zadnym z 71 plikow. Druga sciezka silnika
(`Run.ins`/`Run.del`) jest poprawna, ale nie daje przewagi nad adeu. Osobno zmierzono
`patchTableCellTexts` - odbudowuje komorke zamiast ja patchowac, wiec do edycji tabel
takze sie nie nadaje bez wlasnej warstwy ochronnej.

Komplet liczb i rekomendacja: [THIRD_PARTY_INSPIRATIONS.md](THIRD_PARTY_INSPIRATIONS.md)
(sekcja o genoffice) oraz [vendor/docx-engine/README.md](vendor/docx-engine/README.md).
Decyzja o jakimkolwiek wpieciu nalezy do WM.
