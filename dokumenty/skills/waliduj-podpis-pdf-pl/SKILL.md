---
name: waliduj-podpis-pdf-pl
description: Sprawdza podpis elektroniczny w PRZYCHODZĄCYM PDF - czy plik zmieniono po podpisaniu, kto go podpisał, kiedy, czy jest znacznik czasu i czy podpis obejmuje cały dokument. Działa lokalnie na pyHanko, bez sieci i bez wysyłania pliku gdziekolwiek (RODO-safe, tajemnica zawodowa). Wyłącznie odczyt - NIE podpisuje niczego. Używaj gdy - "sprawdź podpis", "zweryfikuj podpis elektroniczny", "czy ten PDF jest podpisany", "czy dokument zmieniono po podpisaniu", "kto podpisał ten PDF", "walidacja eIDAS", "PAdES", "czy podpis jest ważny", "dostałem podpisany PDF", "weryfikacja podpisu kwalifikowanego", "czy pismo z sądu ma podpis", sprawdzenie podpisu na umowie, wyroku, decyzji administracyjnej lub piśmie procesowym otrzymanym od drugiej strony.
license: MIT
attribution:
  - source: MatthiasValvekens/pyHanko
    url: https://github.com/MatthiasValvekens/pyHanko
    license: MIT
    relationship: dependency
    note: >
      Biblioteka walidacji PAdES wolana lokalnie. Skill ja opakowuje i tlumaczy
      wynik na werdykt laczony - nie wywodzi sie z jej kodu.
allowed-tools: [Bash, Read]
data-residency: local
requires-human-approval: false
pii-egress: none
metadata:
  author: Wiesław Mazur / MateMatic
  version: 0.1.0
  cost: zero LLM (walidacja kryptograficzna)
  companion_skills: doc-intel-contract-pl, opendataloader-pdf
---

# Walidacja podpisu elektronicznego w PDF

## Po co to jest

Kancelaria dostaje podpisane PDF-y - wyroki, decyzje, umowy, pisma od drugiej
strony - i zwykle ufa im na słowo albo na zielony pasek w czytniku. Ten skill
sprawdza plik mechanicznie, w całości na maszynie kancelarii: dokument nie jest
nigdzie wysyłany, narzędzie nie odpytuje żadnego serwera i działa bez internetu.
Ma to znaczenie, bo sprawdzany plik zwykle jest objęty tajemnicą zawodową.

Najczęstszy realny problem nie brzmi „czy podpis jest fałszywy", tylko **„czy
ktoś dopisał coś po podpisaniu"**. PDF pozwala dołączyć kolejną wersję na końcu
pliku - podpis pozostaje kryptograficznie nienaruszony, a dokument już nie jest
tym, co podpisano. Skill to wykrywa.

## Granica

**Ten skill nie podpisuje.** Złożenie podpisu to akt nieodwracalny i skuteczny
na zewnątrz - zostaje człowiekowi. Narzędzie jest wyłącznie odczytowe.

**Kolejność w pipeline OCR:** jeśli dokument idzie potem do skanowania lub OCR
(drabinka PDF, silnik `vlm-html` z [[doc-intel-contract-pl]]), walidację podpisu
rób NAJPIERW, na oryginale. Przygotowanie skanu spłaszcza PDF przed renderem,
żeby pola formularza nie zniknęły z obrazu - i przy okazji NISZCZY podpis
kryptograficznie. Po spłaszczeniu nie ma już czego walidować.

## Jak używać

Instalacja w izolowanym środowisku. Windows:

```bash
python -m venv .venv && .venv/Scripts/python.exe -m pip install pyHanko
```

Linux i macOS:

```bash
python3 -m venv .venv && .venv/bin/python -m pip install pyHanko
```

Uruchamiaj interpreterem z tego środowiska, nie systemowym - inaczej dostaniesz
`ModuleNotFoundError`. Windows:

```bash
.venv/Scripts/python.exe waliduj_podpis.py <plik.pdf>
```

Linux i macOS:

```bash
.venv/bin/python waliduj_podpis.py <plik.pdf>
```

Tryb maszynowy: dołóż `--json` (wynik zawiera `werdykt_ogolny`, `podpisy`,
`zakres_sprawdzenia`).

Kody wyjścia, identyczne w obu trybach: `0` podpis ważny w zakresie sprawdzonym,
`1` brak podpisu albo werdykt inny niż ważny (w tym dokument zmieniony po
podpisaniu), `2` błąd odczytu pliku. Kod wynika z werdyktu, nie z tego, czy
udało się cokolwiek odczytać - nadaje się więc do kontroli automatycznej.

## Co skill rozstrzyga

- czy dokument w ogóle zawiera podpis i ile ich jest,
- czy treść podpisana jest nienaruszona,
- czy podpis obejmuje cały plik, czy tylko jego fragment - to jest test na
  dopisanie treści po podpisaniu,
- kto widnieje w certyfikacie i kto go wystawił,
- deklarowany czas podpisania oraz obecność znacznika czasu.

Werdykt jest **jeden i łączony**. Osobno podane „integralność OK" i „pokrywa cały
plik: nie" czytają się jak dobra wiadomość, a razem znaczą `DOKUMENT ZMIENIONY PO
PODPISANIU`. Skill nigdy nie rozdziela tych dwóch ustaleń w podsumowaniu.

## Czego skill NIE rozstrzyga

**Czy podpis jest kwalifikowany w rozumieniu eIDAS.** Do tego potrzebne są
unijne listy zaufane (LOTL/TSL) z kotwicami zaufania państw członkowskich,
których to narzędzie nie wgrywa. Bez nich łańcuch zaufania jest raportowany jako
`NIEROZSTRZYGNIĘTY` - i tak trzeba to powiedzieć klientowi, zamiast wyprowadzać
z zielonego napisu wniosek, którego on nie niesie.

Skill nie ocenia też, czy treść dokumentu jest prawdziwa merytorycznie.

## Kiedy sięgnąć po coś innego

- **Potrzebny status kwalifikowany do sporu** - walidacja przez narzędzie oparte
  o listy zaufane UE, np. [esig/dss](https://github.com/esig/dss) Komisji
  Europejskiej; ten skill daje wtedy szybką pierwszą odpowiedź, nie dowód
  procesowy.
- **Dokument to skan bez warstwy podpisu** - to nie jest podpis elektroniczny,
  tylko obraz; patrz drabinka odczytu PDF w instrukcjach globalnych.
- **Trzeba złożyć podpis** - poza zakresem, człowiek.

## Co zostało sprawdzone (2026-08-05)

Skill przeszedł przebieg na wygenerowanych plikach kontrolnych. pyHanko 0.36.2,
Python 3.13, instalacja i wywołanie dokładnie wg instrukcji powyżej:

| Przypadek | Werdykt | Kod |
|---|---|---|
| PDF podpisany, nienaruszony | `PODPIS WAZNY w zakresie sprawdzonym`, łańcuch `NIEROZSTRZYGNIETY` | 0 |
| PDF podpisany, treść dopisana po podpisaniu (poprawny incremental update) | `DOKUMENT ZMIENIONY PO PODPISANIU` przy integralności OK | 1 |
| PDF bez podpisu | `Dokument NIE zawiera podpisu` | 1 |

Drugi wiersz to powód istnienia tego skilla: podpis pozostaje kryptograficznie
nienaruszony, a dokument nie jest już tym, co podpisano. Werdykt łączy oba
ustalenia zamiast pokazywać osobno „integralność OK".

**Granica:** pliki były kontrolne, z certyfikatem samopodpisanym. Skill nie
przeszedł jeszcze biegu na prawdziwym piśmie z sądu podpisanym podpisem
kwalifikowanym - to zostaje do zrobienia na materiale kancelarii. Sprawdzona
jest mechanika, nie zachowanie wobec konkretnego dostawcy podpisu.

## Uwagi wykonawcze

`pyhanko` loguje nieudaną budowę ścieżki certyfikatu jako błąd ze śladem stosu.
Przy braku wgranych kotwic zaufania jest to stan **oczekiwany**, nie awaria -
skrypt wycisza te logi i przenosi ustalenie do pola `lancuch_zaufania`. Nie
interpretuj tych śladów jako błędu narzędzia.
