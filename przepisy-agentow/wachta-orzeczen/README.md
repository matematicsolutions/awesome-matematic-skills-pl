# wachta-orzeczen - przegląd nowego orzecznictwa w pilnowanych tematach

Agent tła, który cyklicznie odpytuje SAOS (przez `mcp-saos` / skill
`szukaj-orzeczen-v2`) o nowe orzeczenia SN / TK / KIO / sądów powszechnych
w zdefiniowanych tematach i składa **przegląd do sprawdzenia** - z linkiem
źródłowym przy każdej sygnaturze.

## Jak to działa (3 poziomy, patrz ../README.md)

1. **szperacz-saos** (MCP read-only) odpytuje SAOS per temat, diff ze stanem poprzednim,
   sygnatury i daty dosłownie z wyniku narzędzia - nigdy z pamięci.
2. **oceniacz-trafnosci** (bez narzędzi) odsiewa trafienia uboczne (fraza w wątku
   proceduralnym ≠ orzeczenie w temacie); gdy fragment nie wystarcza - status
   „do przeczytania", nie zgadywanie tezy.
3. **redaktor-przegladu** (jedyny Write) składa tabelę przeglądu z nagłówkiem
   „projekt do sprawdzenia".

## Czego ten przepis NIE robi

- **NIE interpretuje tez orzeczeń** - do przeglądu trafia fragment + link; tezę czyta
  człowiek (albo osobna, jawnie uruchomiona analiza pełnego tekstu).
- **NIE pokrywa WSA/NSA.** SAOS nie indeksuje sądownictwa administracyjnego -
  orzecznictwo RODO/UODO wymaga CBOSA (orzeczenia.nsa.gov.pl) jako osobnego źródła.
- **NIE wprowadza sygnatur do pism.** Każda sygnatura z przeglądu przed użyciem
  w deliverable przechodzi `citation-grounding-pl`.

## Dopasowanie (minimum przed pierwszym uruchomieniem)

- lista tematów + notatka „dlaczego pilnujemy" per temat,
- stan poprzedni (plik JSON z ostatnio widzianymi sygnaturami) i rytm (np. poniedziałek 07:00),
- kanał wyjścia (plik przeglądu / mail wysyłany przez człowieka - wysyłka to akt
  na zewnątrz, zostaje po stronie człowieka),
- ewaluacja na fixture'ach (kryteria behawioralne: link przy każdej sygnaturze,
  odsiew trafień ubocznych, zero sygnatur spoza wyników narzędzia).
