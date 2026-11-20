# Changelog - ocena-outputu-pl

Format: [Keep a Changelog](https://keepachangelog.com/), wersjonowanie [SemVer](https://semver.org/).

## [1.3.0] - 2026-11-20

### Changed
- **Pełny mianownik w warstwie 1.** Każda pozycja niesie liczbę sprawdzonych
  (`cytaty 7/7`); 0/0 nigdy nie jest OK - to BRAK (teza prawna bez źródła tej
  kategorii) albo N/D z jednozdaniowym powodem. BRAK w cytatach lub przepisach
  jest kotwicą (decyzja co najwyżej Pełna weryfikacja). Wcześniej output bez
  żadnego cytatu dostawał „cytaty OK”.
- BRAK w sygnaturach lub kompletności -> decyzja co najwyżej Popraw; w razie
  wątpliwości BRAK, nie N/D; zapis kompletności liczy flagi RED.

### Attribution
- Wzorzec „zakaz w parze z pozytywnym sprawdzeniem obecności” z
  GoogleChrome/modern-web-guidance-src (Apache 2.0), wyłącznie idea.

## [1.1.0] - 2026-07-13

### Added
- **NIEPEWNE jako ocena pierwszej klasy w rubryce.** Sędzia zamiast wymuszonej
  liczby wystawia NIEPEWNE z podkategorią NIEWYSTARCZAJĄCY_DOWÓD /
  DOKUMENT_NIEJEDNOZNACZNY i wskazaniem, jakiego dowodu brakuje. NIEPEWNE nie
  wchodzi do średniej i nie wolno go zamienić na 3. NIEPEWNE w Poprawności
  prawnej lub Ugruntowaniu -> decyzja co najwyżej Pełna weryfikacja; w innych
  wymiarach -> co najwyżej Popraw.
- Sekcja Decyzja i Format wyjścia zaktualizowane o obsługę NIEPEWNYCH.

### Attribution
- Wzorzec kategorii niepewności z AnttiHero/lavern (Apache 2.0), adaptacja od
  zera - podkategorie i reguły decyzji to opracowanie MateMatic.

## [1.0.0] - 2026-06-25

### Added
- Pierwsze wydanie: dwie warstwy oceny (obiektywna mechaniczna + subiektywna
  rubryka 1-5 LLM-as-judge), decyzja Wyślij / Popraw / Pełna weryfikacja.
