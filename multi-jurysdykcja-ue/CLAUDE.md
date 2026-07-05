# Multi-jurysdykcja UE - reguły wspólne

Ten plik to siatka bezpieczeństwa pluginu. Obowiązuje, nawet gdy konektor milczy.

Plugin instaluje jedną komendą dziewięć konektorów prawa krajowego UE (DE, AT, ES, FI, IE, NL, SE, FR, LU). Każdy działa read-only na urzędowym API open-data danego kraju i zwraca źródła ze stabilnym identyfikatorem (ELI / ECLI).

## Źródła, nie pamięć

Każda teza prawna należy do jednej z klas:

- **Zweryfikowane** - potwierdzone w źródle urzędowym, z identyfikatorem: `(BGB § 433, de-eli)`, `(wyrok C-311/18, TSUE)`.
- **Do sprawdzenia** - prawdopodobne, jeszcze niepotwierdzone: `[zweryfikuj w krajowym dzienniku]`.
- **Nie używać** - identyfikator bez pokrycia. Pomiń, nie zmyślaj.

Istnienie odwołania nie wystarcza - potwierdź, że mówi to, co mu przypisujesz. Każda jurysdykcja ma własną strukturę i język; trzymaj jurysdykcję widoczną w każdym cytacie, żeby nic nie trafiło po cichu do złego kraju.

## Wymagania

Konektory działają przez `uvx` (Python), więc środowisko potrzebuje `uv`. Francja (`fr-eli`, Legifrance/PISTE) wymaga darmowych poświadczeń OAuth PISTE; pozostałe osiem działa bez klucza. Instalacja wszystkich dziewięciu uruchamia dziewięć serwerów MCP - instaluj plugin, gdy realnie pracujesz transgranicznie, nie domyślnie.

## Bramka człowieka

Wynik to projekt do weryfikacji. Prawo kraju, w którym nie praktykujesz, jest punktem wyjścia dla miejscowego prawnika, nie poradą. Nic nie zostaje złożone ani podpisane, zanim sprawdzi to uprawniony człowiek.

## Zakres

Ustawodawstwo i orzecznictwo państw członkowskich UE, jeden konektor na kraj. Prawo szczebla UE (EUR-Lex / TSUE) jest w bundlu `orzecznictwo-zrodla` (eu-sparql). Metoda weryfikacji (grounding, czerwony zespół) jest w `fundament-weryfikacyjny`.
