# Orzecznictwo i źródła - reguły wspólne

Ten plik to siatka bezpieczeństwa pluginu. Obowiązuje, nawet gdy konkretny skill milczy. Rdzeń jest tu wpisany wprost, żeby działał po instalacji samego pluginu. Pełniejszy standard: `references/` w repozytorium marketplace.

## Źródła, nie pamięć

Ten plugin pobiera przepisy i orzecznictwo z baz przez konektory MCP (read-only, publiczne API). Każda teza prawna należy do jednej z klas:

- **Zweryfikowane** - potwierdzone w bazie, z sygnaturą i źródłem: `(wyrok NSA II FSK NNNN/RR, SAOS)`.
- **Do sprawdzenia** - prawdopodobne, jeszcze niepotwierdzone: `[zweryfikuj w EUR-Lex]`.
- **Nie używać** - sygnatura lub przepis bez pokrycia w bazie. Pomiń, nie zmyślaj numeru.

Samo istnienie sygnatury nie wystarcza - sprawdź treść orzeczenia, czy rozstrzyga to, co mu przypisujesz. Linia orzecznicza bywa zmienna; aktualność ocenia człowiek.

## Konektory w tym pluginie

Plik `.mcp.json` deklaruje konektory polskich i unijnych źródeł (SAOS, KRS, EUR-Lex). Działają read-only na publicznych danych. Wymagają `node`/`npx` w środowisku. Dane sprawy objęte tajemnicą lub wrażliwe - oceń osobno, czy w ogóle wnosić je do narzędzia; przy wątpliwości nie przekazuj.

## Bramka człowieka

Wynik to projekt do weryfikacji. Nic nie zostaje wysłane ani złożone, zanim sprawdzi to uprawniony człowiek, który bierze odpowiedzialność zawodową.

## Pobieranie spoza MCP

Oprócz konektorów plugin zawiera skill `webwright-legal-pl` - pobiera orzeczenia z serwisów niedostępnych przez MCP (orzeczenia.ms.gov.pl, sn.pl, trybunal.gov.pl, EUR-Lex PL) przez przeglądarkę (Playwright). Te same reguły: dane wrażliwe oceniaj osobno, wynik to projekt do weryfikacji.

## Zakres pluginu

Plugin dostarcza wyszukiwanie i pobieranie źródeł prawa PL/UE. Nie zastępuje analizy prawnej ani weryfikacji cytatu - tę warstwę daje plugin "fundament weryfikacyjny" (zalecany razem).
