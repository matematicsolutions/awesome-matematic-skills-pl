---
name: akta-przeszukiwalne-pl
description: >
  Zamienia folder akt sprawy (PDF, takze skany bez warstwy tekstowej) w tekst z numerami
  stron, lokalna wyszukiwarke i raport: strony nieczytelne, duplikaty plikow oraz pliki
  o IDENTYCZNEJ tresci pod roznymi nazwami (bywa sladem brakujacego pisma). OCR dziala
  lokalnie na CPU - tekst akt nie opuszcza komputera, bez konta i bez chmury. Uzywaj gdy:
  "przeszukaj akta", "zrob z akt tekst", "gdzie w aktach jest", "OCR akt", "skany akt",
  "akta ze skanow", "czego brakuje w aktach", "zdigitalizuj akta sprawy".
attribution:
  - source: run-llama/liteparse
    url: https://github.com/run-llama/liteparse
    license: Apache-2.0
    relationship: dependency
    note: >
      Zaleznosc (PyPI `liteparse`, przypieta 2.14.6): parser PDF z OCR Tesseract na CPU.
      Ekstraktor `scripts/liteparse_extract.py` to kopia z doc-intel-contract-pl, gdzie
      zyje kanon wraz z pomiarem i piecioma bezpiecznikami na ciche pulapki biblioteki.
metadata:
  author: Wieslaw Mazur / MateMatic
  version: 0.1.0
  license: MIT
  cost: zero LLM, zero chmury (OCR lokalny)
  companion_skills: doc-intel-contract-pl, citation-grounding-pl
  twin: searchable-case-files-en
---

# Akta przeszukiwalne

Folder skanow akt zamienia sie w tekst, w ktorym da sie szukac. Wynik podaje plik i
strone, wiec kazde trafienie mozna od razu sprawdzic w oryginale.

## Szybki start

```bash
python -m pip install liteparse==2.14.6
python scripts/akta.py "C:/Sprawy/II K 123-24/akta"
cd "C:/Sprawy/II K 123-24/akta-tekst"
python szukaj.py "opinia bieglej"
```

Pierwsze uruchomienie pobiera polski model OCR (ok. 12 MB, tessdata_best, Apache-2.0).
Praca offline: pobierz model raz i podaj katalog `--tessdata`. Akta po angielsku:
`--jezyk eng` (wtedy bez naprawy `$`, bo w angielskich pismach to kwota). Wersja
angielska skilla: `searchable-case-files-en`.

## Co powstaje (obok folderu akt; oryginaly nietkniete)

- `<dokument>.txt` - tekst z naglowkami `===== strona N =====`;
- `RAPORT.md` - stan kazdego pliku, strony nieczytelne, duplikaty po bajtach i po tresci;
- `szukaj.py` + `indeks.sqlite` - wyszukiwarka: plik, strona, fragment.

Wyszukiwarka ignoruje wielkosc liter i polskie znaki ("lodz" znajdzie "Łódź") i z grubsza
obsluguje odmiane ("bieglej" znajdzie "biegla", "bieglego"), ucinajac koncowke - dlatego
lapie tez wyrazy pokrewne ("prokuratora" znajdzie i "prokurature"). `--dokladnie` szuka
tylko podanej formy.

## Jak czytac RAPORT.md

- **Ten sam tekst w roznych plikach** - dwa PDF-y o roznych nazwach maja identyczna tresc.
  Bywa to zwykla kopia, ale bywa tez plik o mylacej nazwie, a pisma z nazwy w aktach nie ma.
- **Strony nieczytelne** - strona ma obraz, ale OCR nic nie odczytal. W tekscie oznaczona
  `[STRONA NIECZYTELNA - sprawdz oryginal]`; trzeba ja przeczytac w PDF-ie.
- Stan `blokada` (kod wyjscia 20) - ktorys plik jest niekompletny albo sie nie otworzyl.
  Tekstu z takiego pliku nie traktuj jak pelnego.

## Zasady, ktorych skill pilnuje

- Tekst z OCR sluzy do WYSZUKIWANIA. Cytat do pisma zawsze porownaj z oryginalem.
- Znak `§` odczytany przez OCR jako `$` jest poprawiany (liczba napraw w raporcie).
- Liczba stron kazdego pliku jest porownywana z liczba odczytanych; rozjazd to blokada,
  nie cichy sukces.
- Na ekran trafiaja wylacznie liczby. Tresc akt zostaje w katalogu wyniku.
- Przerwany przebieg mozna wznowic tym samym poleceniem - gotowe dokumenty sa pomijane.

## Ograniczenia

- Skany slabej jakosci daja wiecej bledow OCR. Pomiar na publicznym wyroku SN zlozonym
  w skan: da sie znalezc 98,8% jego slow przy 300 dpi i 85,4% przy skanie celowo
  pogorszonym (obrot, rozmycie, szum); blednych znakow 0,5% i 3,5%. Przy gorszym skanie
  jeden zly ogonek psuje caly wyraz, dlatego slow ginie wiecej, niz sugeruja znaki.
- Czas: ok. 2 s na strone (pomiar na jednym laptopie z Windows 11); tysiac stron to ok.
  pol godziny. Na slabszym sprzecie dluzej.
- Windows ze Smart App Control moze zablokowac niepodpisane pliki biblioteki OCR
  (`pdfium.dll`, `_liteparse.pyd`). Blad "DLL load failed" skill zamienia na komunikat
  wskazujacy Smart App Control - sprawdzone na symulacji bledu, nie na maszynie z wlaczonym
  SAC. Decyzja o ustawieniach nalezy do wlasciciela komputera.
- Rozpoznaje tylko PDF. Pisma DOCX zapisz jako PDF.

## Testy

```bash
python -m pytest tests -q
```
