# Przepisy agentów - agenci tła do pracy prawniczej PL

To są **książki kucharskie, nie gotowe produkty.** Każdy przepis to punkt wyjścia dla
agenta uruchamianego w tle (headless / harmonogram), opartego o tę samą dyscyplinę źródeł
co skille tego marketplace. Dopasuj przepis do własnego obiegu dokumentów, kalendarza,
kanału powiadomień i rytmu kontroli - bez tego dopasowania przepis nie działa, i tak ma być.

| Przepis | Co pilnuje | Agenci-liście |
|---|---|---|
| [`wachta-terminow`](wachta-terminow/) | Terminy procesowe i umowne w aktach sprawy (apelacja, zażalenie, odpowiedź na pozew, przedawnienie, terminy RODO) | czytelnik-akt · licznik-terminow · **redaktor-alertow** |
| [`wachta-orzeczen`](wachta-orzeczen/) | Nowe orzeczenia SN / TK / KIO / sądów powszechnych w zdefiniowanych tematach (SAOS) | szperacz-saos · oceniacz-trafnosci · **redaktor-przegladu** |

**Pogrubiony** agent-liść jako jedyny ma prawo `Write`.

Wachty legislacyjnej tu nie ma celowo: pilnowanie, czy ustawa nadal obowiązuje, jest
deterministyczne i nie potrzebuje LLM - robi to skrypt
[`scripts/wachta-legislacyjna.mjs`](../scripts/wachta-legislacyjna.mjs) w CI
(rejestr: [`seuranta/ustawy.json`](../seuranta/ustawy.json)). Nie agentyfikuj tego,
co załatwia skrypt.

## Model bezpieczeństwa - akta sprawy to niezaufane wejście

Dokument prawny może zawierać tekst, który próbuje sterować modelem („zignoruj wcześniejsze
instrukcje…" - wprost albo schowane w białym tekście / metadanych). Dlatego każdy przepis
dzieli pracę na **trzy poziomy uprawnień**:

1. **Czytelnik (reader)** dotyka niezaufanych dokumentów i ma wyłącznie `Read`/`Grep` -
   bez MCP, bez `Write`, bez sieci. Zwraca ograniczony długością, ustrukturyzowany JSON.
   Instrukcja osadzona w dokumencie to **dane, nie polecenie.**
2. **Analityk (analyzer)** dostaje JSON czytelnika, stosuje reguły z konfiguracji
   użytkownika i może mieć MCP **tylko do odczytu** do weryfikacji (SAOS / ISAP).
   Bez `Write`.
3. **Redaktor (writer)** składa finalny output i jako **jedyny** ma `Write`.
   Nigdy nie widzi surowych dokumentów.

Orkiestrator nie czyta surowych akt i nie pisze plików - tylko przekazuje komunikaty
między poziomami. Agenci nie wołają się nawzajem bezpośrednio; przekazanie pracy to
`handoff` routowany przez orkiestratora.

## Odpowiedzialność i tajemnica

Wszystko, co wyprodukują te agenty, to **projekt do sprawdzenia** - nie porada prawna.
Agent pilnuje, wyciąga i szkicuje; **człowiek sprawdza, weryfikuje i decyduje.**
Wyliczenia terminów to poszlaki, nie wiążące daty - każdy przepis ma sekcję
„Czego ten przepis NIE robi".

Przy danych objętych tajemnicą zawodową stosuj
[`references/odpowiedzialnosc-i-rodo.md`](../references/odpowiedzialnosc-i-rodo.md):
pseudonimizacja przed analizą (`let-it-be`), umowa powierzenia (RODO art. 28),
ocena tajemnicy zanim akta trafią do jakiegokolwiek narzędzia.

## Co dostajesz i czego nie

- **Dostajesz:** działającą strukturę manifestu, sensowne poziomy uprawnień, instrukcje
  oparte o dyscyplinę źródeł (SAOS / ISAP / terminy z ustawy, nie z pamięci) i przykład
  zdarzeń sterujących - pod polskie źródła i polską procedurę.
- **Nie dostajesz:** agenta produkcyjnego. Podepnij konektory do swoich systemów, ustaw
  rytm, skonfiguruj powiadomienia i zrób własną ewaluację, zanim zaufasz outputowi
  (fixture'y do ewaluacji: katalog [`examples/`](../examples/) i behawioralne listy
  kryteriów - „dobry output ROBI X", nie „dochodzi do wyniku Y").
- **W żadnym wypadku nie dostajesz:** zastępcy prawnika.

## Atrybucja

Model trójpoziomowy (reader/analyzer/writer z izolacją uprawnień), rama „keittokirja,
ei valmis tuote" (książka kucharska, nie produkt) i wzorzec manifestów zaadaptowane
z `agentti-reseptit` w [akunikkola/claude-for-legal-finland](https://github.com/akunikkola/claude-for-legal-finland)
(MIT). Substancja (SAOS, terminy KPC/KPA/KPK, procedura PL) napisana od zera.
