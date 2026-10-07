---
name: chronologia-stanowiska-pl
description: >
  Dla prawnika prowadzącego spór. Z tekstu akt (wynik akta-przeszukiwalne-pl) buduje
  chronologię zdarzeń albo zestawienie stanowisk stron (element roszczenia x twierdzenie x
  stanowisko przeciwnika x dowody x luka), a mechaniczna bramka sprawdza, czy każdy wpis
  wskazuje istniejący plik i stronę akt i czy cytat naprawdę na niej stoi. Wpis bez kotwicy
  w aktach nie przechodzi. Z perspektywy powoda albo pozwanego (także oskarżyciela i obrony).
  Nie ocenia, kto ma rację, nie rozstrzyga sprzeczności i nie liczy terminów. Używaj gdy:
  "zrób chronologię z akt", "oś czasu sprawy", "co się działo kiedy", "zestawienie
  stanowisk stron", "co przyznał pozwany", "czego nam brakuje do udowodnienia",
  "stan faktyczny do pisma", "chronologia dla świadka".
attribution:
  - source: anthropics/claude-for-legal
    url: https://github.com/anthropics/claude-for-legal
    license: Apache-2.0
    relationship: adaptation
    note: skille litigation-legal chronology i claim-chart, commit d541734
  - source: b1rdmania/chronology
    url: https://github.com/b1rdmania/chronology
    license: Apache-2.0
    relationship: adaptation
    note: Andrew Bird, commit 628e807
  - source: legalquants/lq-skills
    url: https://github.com/legalquants/lq-skills
    license: Apache-2.0
    relationship: adaptation
    note: skill building-chronologies, commit 70ebcea
  - source: rohasnagpal/legal-ai-skills
    url: https://github.com/rohasnagpal/legal-ai-skills
    license: MIT
    relationship: adaptation
    note: skille chronology-builder i pleadings-analyst, commit 20fbad1
metadata:
  author: Wieslaw Mazur / MateMatic
  version: 0.1.0
  license: Apache-2.0
  cost: bramka bez LLM i bez sieci (stdlib); budowa wpisów - model w sesji
  companion_skills: akta-przeszukiwalne-pl, citation-grounding-pl, adversarial-legal-review-pl
---

# Chronologia akt i zestawienie stanowisk

Fakty idą w kolejności, a każde pismo w sprawie na tej kolejności wisi. Ten skill wyciąga
z akt daty i stanowiska stron, ale ma jedną twardą regułę: **wpis bez kotwicy w aktach nie przechodzi jako pewny** -
fakt spoza akt wolno zapisać tylko z tagiem pochodzenia i trafia do sprawdzenia.
Pilnuje tego skrypt, nie dobra wola modelu.

Wynik jest szkicem: `[SZKIC AI - wymaga analizy i nadzoru uprawnionego prawnika]`.

## Krok 0 - tekst akt

Skill czyta katalog `akta-tekst` z `akta-przeszukiwalne-pl` (pliki `.txt` z nagłówkami
`===== strona N =====`). Nie ma go? Najpierw uruchom skill `akta-przeszukiwalne-pl`
(z jego katalogu):

```bash
python scripts/akta.py "<folder akt>"
```

Przeczytaj `RAPORT.md`: strony nieczytelne i pliki o identycznej treści to pierwsze luki
chronologii, zanim powstanie choć jeden wpis.

## Krok 1 - bramka użycia materiału (zawsze, przed ekstrakcją)

Zapytaj i zapisz odpowiedź w nagłówku wyniku:

- Czy materiał pochodzi z **akt innego postępowania** albo z **postępowania
  przygotowawczego**? Wykorzystanie go poza tym postępowaniem bywa ograniczone
  `[DO WERYFIKACJI: tajemnica postępowania przygotowawczego, dostęp do akt innej sprawy - przepis wskazuje prawnik]`.
- Czy chronologia zostanie **w tej samej sprawie**? Inne użycie = stop do decyzji prawnika.

Nie potwierdzono? W nagłówku: `UWAGA: ograniczenie użycia materiału niepotwierdzone`.

## Krok 2 - postawa tajemnicy (bramka, nie ostrzeżenie)

Korespondencja z klientem, notatki pełnomocnika i projekty pism są objęte tajemnicą
zawodową. Wyciągnięcie ich do chronologii, która potem wyjdzie poza krąg, może ją naruszyć.
Przed ekstrakcją użytkownik wybiera:

- **A** - wszystkie źródła sprawdzone, nic objętego tajemnicą. Bez flag.
- **B** - źródła mieszane albo niesprawdzone (domyślne przy wątpliwości). Każdy wpis
  dostaje `tajemnica: ok | flaga | do_przegladu`. Wątpliwe idzie do `flaga`, nie do `ok`:
  nadmiar flag prawnik zdejmie, ujawnienia nie cofnie.
- **C** - stop, najpierw przegląd. Bramka zablokuje każdy wynik z postawą C.

Postawa trafia do nagłówka wyniku jako ślad pochodzenia.

## Tryb 1 - chronologia

1. **Perspektywa.** Powód / pozwany (oskarżyciel / obrona). Oś czasu jest neutralna;
   perspektywa zmienia tylko wagę wpisu. Zapisz ją w nagłówku.
2. **Ekstrakcja.** Z każdego dokumentu zdarzenia z datą: kto, co, wobec kogo. Rozdzielaj
   rodzaje dat - w polskich aktach to się rozjeżdża najczęściej: data **zdarzenia**,
   **dokumentu**, **nadania** (stempel), **doręczenia**, **wpływu** (prezentata sądu),
   **posiedzenia**. Nie zamieniaj szacunku, przedziału ani „na początku kwietnia” w pewną
   datę: `pewnosc_daty` to `dokladna | miesiac | rok | przedzial | przyblizona | sporna`.
3. **Status wpisu.** `dowod_bezposredni` (dokument z epoki), `relacja` (świadek, notatka),
   `twierdzenie_strony` (pismo procesowe), `ustalenie_sadu`, `zdarzenie_procesowe`,
   `wniosek` (wywnioskowane - tylko z wyraźnym uzasadnieniem w uwagach). Twierdzenie
   strony to nie dowód: nie podnoś go do rangi faktu.
4. **Kotwica.** Każde źródło: `plik`, `strona` i `cytat` - dosłowny fragment, min. 3 słowa,
   przepisany z tekstu akt, nie streszczony. Jedno zdarzenie z trzech dokumentów = jeden
   wpis z trzema źródłami.
5. **Pochodzenie spoza akt.** Fakt podany przez użytkownika w rozmowie: `pochodzenie:
   uzytkownik`. Z wiedzy modelu albo internetu - tylko za zgodą użytkownika, z tagiem
   `wiedza_modelu` / `internet`. Bramka przepuści je jako UWAGI, nigdy jako OK.
6. **Waga** (według perspektywy): `kluczowe` - zdarzenie, które przesuwa ocenę sądu;
   `istotne` - kontekst i wzorzec; `tlo`. W wątpliwości wyżej nie wchodzisz: niższa waga
   i `[DO WERYFIKACJI: waga]`. Gdy ponad połowa wpisów jest kluczowa, nic nie jest.
7. **Sprzeczności zostają.** Dwa dokumenty, dwie daty - dwa wpisy, `pewnosc_daty: sporna`,
   obie kotwice. Rozstrzyga prawnik.

## Tryb 2 - zestawienie stanowisk stron

1. **Roszczenie i elementy.** Elementy podstawy roszczenia (albo zarzutu) podaje prawnik
   lub wynikają z pozwu. Skill może zaproponować listę, ale każdy element nosi
   `[DO WERYFIKACJI: przesłanka - potwierdza prawnik]`. Nie zaszywamy prawa w skillu.
2. **Twierdzenia.** Dla każdego elementu: które akapity pisma go zgłaszają (kotwice).
3. **Stanowisko przeciwnika** dla każdego twierdzenia: `przyznanie`,
   `przyznanie_z_zastrzezeniem`, `zaprzeczenie`, `brak_stanowiska`, `nie_dotyczy` -
   zawsze ze wskazaniem pisma (`zrodla_stanowiska`). Skutek braku stanowiska to kwestia
   prawna `[DO WERYFIKACJI: skutek niewypowiedzenia się co do twierdzeń - wskazuje prawnik]`.
   Milczenie to nie przyznanie, dopóki prawnik tak nie oceni.
4. **Dowody za i przeciw** - z kotwicami. Dowód powołany w piśmie, którego nie ma w
   aktach, to nie dowód, tylko luka („wskazany, niezałączony”).
5. **Stan elementu:** `wykazane` (są dowody za, bramka wymaga co najmniej jednego),
   `czesciowo`, `sporne`, `luka`, `do_uzupelnienia` (co trzeba dosłać / o co wnieść).
6. **Lista luk jest głównym wynikiem.** Dla każdego elementu w stanie `luka` /
   `do_uzupelnienia`: czego brakuje i skąd to można wziąć. Terminy na twierdzenia i
   dowody `[DO WERYFIKACJI: aktualne przepisy i zarządzenia w sprawie]` - skill ich nie liczy.

## Krok 3 - zapis i bramka (obowiązkowo, za każdym razem)

Zapisz wynik maszynowy obok tekstu akt, np. `akta-tekst/../chronologia.json`:

```json
{"rodzaj": "chronologia", "sprawa": "...", "perspektywa": "powod", "postawa_tajemnicy": "B",
 "wpisy": [{"id": "Z1", "data": "2024-01-15", "pewnosc_daty": "dokladna",
   "rodzaj_daty": "zdarzenia", "kto": "...", "zdarzenie": "...", "waga": "istotne",
   "status": "dowod_bezposredni", "tajemnica": "ok", "pochodzenie": "akta",
   "zrodla": [{"plik": "umowa.pdf", "strona": 1, "cytat": "dosłowny fragment z akt"}]}]}
```

Zestawienie: `"rodzaj": "zestawienie"`, lista `elementy` z polami `id, element,
twierdzenia, stanowisko_przeciwnika, zrodla_stanowiska, dowody_za, dowody_przeciw, stan`.
Wzory: `tests/fixtures/chronologia.json`, `tests/fixtures/zestawienie.json`.

Uruchom bramkę OSOBNO (nie przez `&&` ani `|`, bo potok gubi kod wyjścia):

```bash
python scripts/bramka_lokatorow.py chronologia.json akta-tekst --csv chronologia.csv
```

| Kod | Stan | Co robisz |
|---|---|---|
| 0 | OK | każdy wpis zakotwiczony; wolno pokazać wynik |
| 10 | UWAGI | strona nieczytelna, cytat zgodny tylko bez polskich znaków, fakt spoza akt - pokaż, ale z listą wpisów do sprawdzenia w oryginale |
| 20 | BLOKADA | cytatu nie ma na wskazanej stronie, brak pliku, zła data, pusta lista - **popraw wpisy i uruchom ponownie**; nie pokazuj wyniku jako gotowego |

Przy kodzie ZR08 raport podaje stronę, na której cytat naprawdę stoi - popraw lokator,
nie cytat. Przy ZR09 cytat bywa zgodny z papierem, ale nie z OCR (np. „Sp. z o.o.”
odczytane jako „Sp. Z 0.o.”): przepisz fragment dokładnie z pliku `.txt` albo wybierz
sąsiedni, czysto odczytany fragment. Nigdy nie poprawiaj cytatu „na oko” pod tezę.

Na ekran bramka wypisuje wyłącznie liczby i identyfikatory; szczegóły są w
`*.bramka.md` obok pliku JSON. CSV ma komórki zneutralizowane przed formułami (`'=`),
bo cytat z pisma przeciwnika nie może stać się formułą w arkuszu.

## Wynik dla prawnika (Markdown, z JSON po bramce)

```
[SZKIC AI - wymaga analizy i nadzoru uprawnionego prawnika]
Bramka lokatorów: STAN OK | Mianownik: N = a OK + b UWAGI + 0 BLOKADA
Sprawa · perspektywa · postawa tajemnicy · ograniczenie użycia materiału · data budowy · źródła (N plików)

## Oś czasu            | Data | Pewność | Zdarzenie | Waga | Status | Tajemnica | Źródło (plik s. N) |
## Kluczowe zdarzenia  (co, dlaczego ważne dla tezy sprawy, źródła)
## Sprzeczności        (wpisy sporne obok siebie)
## Luki                okresy bez zdarzeń · dokumenty powołane, a nieobecne w aktach ·
                       strony nieczytelne · pliki o identycznej treści (RAPORT.md)
```

Zestawienie: tabela `| # | Element | Twierdzenie (pismo s.) | Stanowisko przeciwnika (pismo s.) | Dowody za | Dowody przeciw | Stan |`, pod nią **Lista luk**, a na końcu
zdanie: *Skill nie rozstrzyga. Elementy wykazane: [...], sporne: [...], luki: [...].*

**Warianty na prośbę** (zawsze z tego samego JSON, master się nie zmienia):
- **stan faktyczny do pisma** - tylko `kluczowe` i wybrane `istotne`, proza z lokatorami;
  wpisy `tajemnica: flaga | do_przegladu` i `pewnosc_daty: sporna` wyłączone, chyba że
  prawnik wprost każe je włączyć (zapisz to w nagłówku);
- **dla świadka** - zdarzenia, w których osoba jest nadawcą, adresatem, uczestnikiem lub
  przedmiotem: co wiedziała i od kiedy.

Wersjonowanie: kolejna budowa czyta poprzedni JSON, podaje różnicę (nowe, zmienione,
usunięte z powodem) i podnosi numer wersji.

## Czego ten skill nie robi

- nie rozstrzyga sprzeczności między źródłami - pokazuje je obok siebie;
- nie dopisuje zdarzeń spoza akt bez zgody i bez tagu pochodzenia;
- nie liczy terminów (przedawnienie, prekluzja, terminy procesowe);
- nie ocenia szans ani zasadności - zestawienie to mapa, nie wyrok;
- nie decyduje o tajemnicy - flaguje, decyduje prawnik;
- nie poprawia OCR - strona nieczytelna to luka do sprawdzenia w oryginale.

## Testy

```bash
python -m pytest tests -q
```

Akta w `tests/fixtures` są fikcyjne. Nigdy nie wkładaj tu fragmentów prawdziwej sprawy.

## Pochodzenie

Adaptacja do polskiej procedury czterech otwartych skilli (szczegóły w `NOTICE`):
struktura chronologii, postawa tajemnicy i wariant stanu faktycznego - claude-for-legal;
kotwica każdego wpisu w dokumencie i bramka użycia materiału - Andrew Bird; pasmo
pewności i rozdzielenie dat - lq-skills i Rohas Nagpal; mapa twierdzenie / stanowisko /
dowód - claim-chart i pleadings-analyst. Własne: bramka lokatorów (deterministyczna
kontrola cytatu na stronie akt) i spięcie z lokalnym OCR akt.

<!-- shared-rules:begin (wygenerowane z ../../SHARED-RULES.md przez scripts/shared-rules-sync.py - nie edytuj tutaj) -->
## Wspólne reguły wtyczki dokumenty (Dokumenty)

Te reguły obowiązują w każdym skillu tej wtyczki, także gdy sam skill milczy. Są skopiowane do każdego skilla, więc działają zarówno po instalacji całej wtyczki, jak i pojedynczego skilla.

Plugin obsługuje dokumenty: konwersję do Markdown, redlining .docx i anonimizację danych osobowych. Część operacji dotyka danych wrażliwych, więc reguła ochrony danych jest tu pierwsza.

### Ochrona danych

- **Anonimizacja przed wysyłką** - gdy dokument zawiera dane osobowe, oczyść je lokalnie (skill `let-it-be`), zanim treść trafi do modelu. Dane osobowe nie powinny wychodzić do API. To zasada minimalizacji (RODO).
- **Metadane przy wysyłce** - redlining .docx czyści też metadane autora; sprawdź je przed przekazaniem pliku na zewnątrz.
- **Próg poufności** - materiał objęty tajemnicą lub szczególnie wrażliwy oceniaj osobno, czy w ogóle wnosić do narzędzia. Przy wątpliwości nie przekazuj.

### Operacje nieodwracalne

Niektóre operacje są nieodwracalne (anonimizacja w trybie nieodwracalnym, zaakceptowanie wszystkich zmian w .docx). Skille oznaczają je jawnie - wykonuj je dopiero po potwierdzeniu przez człowieka.

### Bramka człowieka

Wynik to projekt. Nic nie zostaje wysłane ani złożone, zanim sprawdzi to uprawniony człowiek. Plugin przygotowuje plik, nie wykonuje aktu wysyłki.

### Zakres pluginu

Plugin daje narzędzia na dokumentach (konwersja, redline, anonimizacja). Nie ocenia treści prawnej ani nie weryfikuje cytatu - tę warstwę daje plugin "fundament weryfikacyjny".
<!-- shared-rules:end -->
