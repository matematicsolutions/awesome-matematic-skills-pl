# Zaufanie i granice

Co te skille gwarantują, czego nie kontrolują i gdzie kończą się nasze deklaracje. Najpierw luki.

## Czego nie kontrolujemy

Skill to zestaw instrukcji wykonywany przez agenta AI, w którym go uruchamiasz
(Claude Code, Cowork, dowolne środowisko zgodne z SKILL.md). Tekst, który
stawiasz przed agentem, trafia do modelu, który masz skonfigurowany. Jeśli to
model chmurowy, Twoja treść dociera do jego dostawcy na warunkach Twojej umowy
z nim - niezależnie od tego, co robi skill. Sam agent też jest poza naszą
kontrolą: jego telemetria i połączenia to sprawa między Tobą a jego dostawcą.

Żaden plik w tym repozytorium tego nie zmienia i żadnej naszej deklaracji nie
należy czytać inaczej. "RODO-safe" w tym hubie opisuje warstwę skilla, nigdy
Twój tor modelu.

## Co skill z tego huba gwarantuje

Każdą z poniższych deklaracji można sprawdzić, czytając pliki samego skilla.

- **Bundle czysto metodyczne nie dodają konektorów.** `fundament-weryfikacyjny`,
  `ochrona-danych`, `governance-kancelarii` i `jakosc-tresci` nie deklarują
  własnych serwerów MCP ani endpointów.
- **Bundle sięgające na zewnątrz mówią to wprost.** `orzecznictwo-zrodla`
  i `multi-jurysdykcja-ue` instalują konektory odpytujące publiczne API baz
  prawa (SAOS, Sejm ELI, EUR-Lex i krajowe odpowiedniki) - pytają o prawo,
  więc formułuj zapytania w kategoriach przepisu, nie swojej sprawy.
  W `dokumenty` skill `markitdown` używa serwera MCP do konwersji plików
  lokalnie, a `let-it-be` anonimizuje lokalnym narzędziem Node. `dev-mcp`
  to narzędzia deweloperskie do budowy konektorów - z natury dotykają
  sieci przy testach. Które narzędzie czego dotyka, opisuje SKILL.md
  danego skilla.
- **Kalkulatory terminów są offline.** Skrypty terminowe i kontrolne
  w `ochrona-danych` i `dokumenty` to biblioteka standardowa Pythona, bez
  połączeń; dostają daty albo listy klauzul, nie akta sprawy.
- **Draft, nie akt.** Zawiadomienie UODO, wysyłka odpowiedzi na wniosek,
  złożenie pisma, podpis: skill przygotowuje dokument, akt wykonuje
  człowiek. Ta granica jest zapisana per bundle w jego `CLAUDE.md`.

## Co znaczą pola frontmattera

Część skilli niesie `data-residency: local` i `pii-egress: none`. Zakres:
**zachowanie samego skilla**. `pii-egress: none` znaczy, że skill nie dodaje
żadnego kanału wyprowadzającego dane osobowe. Nie znaczy, że Twoja sesja nic
nie wysyła - o tym decyduje konfiguracja modelu i agenta, punkt wyżej.

## Jeśli potrzebujesz pełnej lokalności

Wskaż agentowi model lokalny (np. przez Ollama) - wtedy warstwa skilla
i warstwa modelu są na Twojej maszynie. Czy lokalny jest też sam agent,
zależy od jego dostawcy, nie od nas. Przy modelu chmurowym nie wklejaj
danych identyfikujących albo najpierw zanonimizuj - do tego jest skill
`let-it-be` w bundle `dokumenty`.

## Brama człowieka

Nic, co tu powstaje, nie jest poradą prawną. Każdy wynik traktuj jak draft,
który nie wychodzi z kancelarii bez przeglądu i zatwierdzenia przez osobę
uprawnioną. Jeśli błąd przeszedłby mimo kontroli, które skill uruchamia, to
wada skilla - zgłoś ją, zamiast liczyć, że disclaimer ją pochłonie.
