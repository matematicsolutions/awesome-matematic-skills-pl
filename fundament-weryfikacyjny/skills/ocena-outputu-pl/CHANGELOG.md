# Changelog - ocena-outputu-pl

Format: [Keep a Changelog](https://keepachangelog.com/), wersjonowanie [SemVer](https://semver.org/).

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
