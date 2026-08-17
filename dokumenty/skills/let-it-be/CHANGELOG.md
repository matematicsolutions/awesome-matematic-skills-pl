# Changelog

Format wg [Keep a Changelog](https://keepachangelog.com/pl/1.1.0/), wersjonowanie [SemVer](https://semver.org/lang/pl/).

## [0.2.0] - 2026-07-13

Warstwa odwracalnej redakcji PACZKI dokumentow. Do tej pory `pseudonimizuj` + `odwroc` dzialaly na pojedynczym dokumencie, a kazdy plik dostawal wlasna numeracje ([OSOBA_1] w pozwie i [OSOBA_1] w zeznaniu mogly byc dwiema roznymi osobami).

### Dodane

- `src/paczka.mjs` - `SlownikOdwracania`: stabilny placeholder per (kategoria, wartosc znormalizowana) w obrebie calej paczki; jednolita numeracja miedzy plikami; eksport/import JSON przezywa restart procesu (wczytany slownik kontynuuje numeracje, znane wartosci trzymaja stare placeholdery). Liczniki odtwarzane takze z sufiksow placeholderow, gdy pole `liczniki` w sidecarze jest niepelne.
- `pseudonimizujPaczke(pliki, opts)` - pseudonimizacja wielu dokumentow na wspolnym slowniku; per plik zwraca tekst, liczniki i `source_hash`.
- `przywroc(text, slownik)` - przywraca oryginaly (np. w odpowiedzi LLM) i raportuje placeholdery bez wpisu w slowniku (inna paczka albo zmyslone przez model).
- CLI: `paczka <plik...> --slownik s.mapa-pii.json [--out-dir]` oraz `przywroc <plik|-> --slownik s.mapa-pii.json`. Konwencja nazwy sidecara `*.mapa-pii.json` (ostrzezenie w nazwie pliku); CLI ostrzega, gdy nazwa od niej odbiega.
- Bramka "no PII leaves" dla paczki: kazdy wynik sprawdzany przeciw WSZYSTKIM oryginalom slownika (takze z innych plikow i poprzednich sesji); przy porazce nic nie jest zapisywane.
- Zdarzenie audit logu `paczka-applied` (per plik) i `pseudonim-reversed` dla `przywroc`.
- 11 nowych testow (roundtrip paczki, determinizm, jednolita numeracja, import/eksport, kontynuacja numeracji po restarcie procesu przez CLI, halucynowane placeholdery). Razem 32.

### Wzorce (pattern, nie kod - THIRD_PARTY_INSPIRATIONS.md)

- Rizzo-AI-Academy/rizzo-pii (MIT): stabilny placeholder per (label, wartosc znormalizowana) + slownik odwracania z eksportem/importem.
- moyupeng0422/legal-doc-redactor (MIT): jednolita numeracja w batchu + mapping w sidecarze.

### Roadmap v2 (nie w tym wydaniu)

- Tryb docx z zachowaniem tracked changes (podmiana na poziomie runs) - silnik jest dzis tekstowy.
- Publikacja pakietu (npm/PyPI wrapper) - poza tym wydaniem.

## [0.1.0-alpha] - 2026-05-22

Pierwsze wydanie. Samodzielny silnik "Let It Be".

### Dodane

- Detekcja polskich PII: PESEL/NIP/REGON/KRS (checksuma urzędowa), IBAN/NRB (checksuma mod-97), dowód osobisty (checksuma), e-mail, telefon (z/bez +48), imię i nazwisko (gazetteer ~120 imion + heurystyka), firma z formą prawną, adres (ulica + numer, kod pocztowy). Sygnatury SN/NSA/WSA/KIO/TK + CELEX/ELI (domyślnie nie podmieniane - to nie PII).
- Flaga `--min-confidence <n>` (CLI) i opcja `minConfidence` (biblioteka) - próg czułości detekcji.
- CI na GitHub Actions (`node --test` na Node 20/22/24).
- Dwa tryby RODO: `anonimizuj` (nieodwracalny, bez mapy) i `pseudonimizuj` + `odwroc` (odwracalny przez mapę).
- Rozwiązywanie nakładających się spanów (wyższe confidence wygrywa).
- Bramka "no PII leaves" (`ResidualPIIError`) - przerywa operację, gdy oryginał przetrwał podmianę. Komunikat nie ujawnia wartości.
- Wzorce operacyjne (cherry-pick z PII-Shield): `MappingStore` z TTL i cleanup, `sourceHash` (sha256), `AuditLog` plain-text dla Inspektora, archiwum AES-256-GCM (klucz scrypt).
- CLI (`bin/cli.mjs`): `wykryj`, `pseudonimizuj`, `anonimizuj`, `odwroc`. Wejście z pliku lub stdin.
- 18 testów (`node --test`), zero zależności zewnętrznych.

### Znane ograniczenia

- Fleksja imion/nazwisk poza pierwszym wystąpieniem nie zawsze łapana (bramka residual zatrzyma).
- Adres bez prefiksu ulicy (ul./al./pl./os.) może umknąć.
- Brak detekcji dat urodzenia, paszportu, prawa jazdy, PWZ.
