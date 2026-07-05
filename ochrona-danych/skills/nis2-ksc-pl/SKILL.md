---
name: nis2-ksc-pl
description: >-
  Triage zakresu i obowiązków pod NIS2 (dyrektywa (UE) 2022/2555) po polsku - nawigator zakresu:
  czy podmiot w ogóle podlega (sektory załącznika I i II, reguła size-cap - próg wielkości przedsiębiorstwa, wyjątki niezależne od
  rozmiaru), podmiot kluczowy czy ważny, mapa 10 środków zarządzania ryzykiem z art. 21 ust. 2,
  zegar raportowania incydentu z art. 23 (24h -> 72h -> 1 miesiąc), obowiązki organu
  zarządzającego z art. 20, pułapy kar. Transpozycja PL = nowelizacja ustawy o krajowym systemie
  cyberbezpieczeństwa (KSC); skill NAJPIERW ustala aktualny stan transpozycji w ISAP (konektor
  sejm-eli-mcp), dopiero potem doradza - nie zakłada, że nowelizacja weszła w życie. Wynik: karta
  NIS2 do decyzji człowieka. Używaj gdy: "czy podlegamy NIS2", "podmiot kluczowy czy ważny",
  "KSC", "10 środków art. 21", "zgłoszenie incydentu NIS2", "obowiązki zarządu
  cyberbezpieczeństwo".
license: Apache-2.0
allowed-tools: [Read]
data-residency: local
requires-human-approval: true
pii-egress: none
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.0.0
  inspiration: "wzorzec 'scope navigator' z ekosystemu compliance; treść od zera na tekście dyrektywy (UE) 2022/2555"
  companion_skills: rodo-naruszenie-72h-pl, matematic-konstytucja-ai, sejm-eli-mcp, mcp-eu-compliance
  parity: nis2-compliance-triage-en
---

# NIS2 / KSC PL - triage zakresu i obowiązków (dyrektywa (UE) 2022/2555)

## Filozofia

NIS2 to najpierw pytanie o zakres, dopiero potem o środki. Większość błędów doradczych bierze się
z pominięcia triage'u: firma "czuje", że podlega (albo że nie podlega), i od razu kupuje audyt.
Skill prowadzi nawigator w stałej kolejności: **czy w zakresie -> jaka kategoria -> jakie środki ->
jakie raportowanie -> co mówi transpozycja krajowa**. Każda teza ma tag pewności; numer przepisu,
którego nie da się potwierdzić w sesji, dostaje [DO SPRAWDZENIA], nie zgadywany numer.

Druga zasada: **dyrektywa nie działa wprost na przedsiębiorcę**. Obowiązki w Polsce nakłada ustawa
o KSC po nowelizacji wdrażającej NIS2. Dopóki skill nie ustali stanu transpozycji na dzień użycia,
wszystko poniżej jest mapą dyrektywy, nie listą obowiązków wykonalnych "od jutra".

## Kiedy używać / Czego NIE robi

**Używać:** wstępny triage "czy podlegamy NIS2", spór "kluczowy czy ważny", inwentaryzacja 10
środków z art. 21 ust. 2 przed audytem, ułożenie zegara raportowania na wypadek incydentu,
briefing zarządu o odpowiedzialności z art. 20, przygotowanie luk do planu wdrożenia.

**NIE robi:**
- nie zastępuje audytu bezpieczeństwa ani testów penetracyjnych - mapa środków opiera się na
  deklaracjach użytkownika, skill niczego technicznie nie weryfikuje,
- nie ocenia jakości wdrożenia środka (czy backup faktycznie działa) - tylko czy istnieje i czy
  jest udokumentowany według wiedzy użytkownika,
- nie prowadzi obsługi żywego incydentu - przy trwającym incydencie odsyła do wewnętrznej
  procedury reagowania i do człowieka odpowiedzialnego (CISO / pełnomocnik / zarząd),
- nie wysyła żadnego zgłoszenia do CSIRT ani organu właściwego - składa draft i zegar,
- nie rozstrzyga ostatecznie klasyfikacji podmiotu - to decyzja prawna na tekście ustawy KSC po
  nowelizacji, z bramką człowieka.

**Rozgraniczenie reżimów:** jeśli incydent obejmuje dane osobowe, biegną RÓWNOLEGLE dwa zegary -
NIS2 (24h wczesne ostrzeżenie / 72h zgłoszenie do CSIRT) i RODO (72h zgłoszenie do UODO, art. 33).
Zegar RODO prowadzi `rodo-naruszenie-72h-pl`. Jedno zgłoszenie nie zastępuje drugiego.

## Workflow

### Krok 0 - stan transpozycji PL (OBOWIĄZKOWY, przed jakąkolwiek poradą)

Termin transpozycji NIS2 minął 17 października 2024 r. (art. 41 dyrektywy). Transpozycją polską
jest **nowelizacja ustawy z 5 lipca 2018 r. o krajowym systemie cyberbezpieczeństwa (KSC)** -
status: **[DO SPRAWDZENIA w ISAP przez konektor sejm-eli-mcp na dzień użycia]**.

1. Sprawdź w ISAP (sejm-eli-mcp) aktualny tekst ustawy o KSC i status nowelizacji wdrażającej
   NIS2: uchwalona? opublikowana w Dzienniku Ustaw? jaka vacatio legis?
2. Zapisz wynik w karcie (pole "Stan transpozycji") z datą sprawdzenia.
3. Dobierz reżim analizy: (a) nowelizacja obowiązuje -> analizuj na tekście ustawy; (b) nie
   obowiązuje -> analizuj na dyrektywie jako mapie NADCHODZĄCYCH obowiązków, a równolegle oznacz,
   że do czasu wejścia w życie nowelizacji stosuje się KSC w brzmieniu dotychczasowym (reżim NIS1:
   operatorzy usług kluczowych / dostawcy usług cyfrowych).
4. **Nigdy nie twierdź, że nowelizacja weszła w życie, bez potwierdzenia w ISAP w tej sesji.**

### Krok 1 - triage sektora (załącznik I i II)

**Załącznik I - sektory wysoce krytyczne:** energetyka (energia elektryczna, ciepłownictwo i
chłodnictwo, ropa naftowa, gaz, wodór), transport (lotniczy, kolejowy, wodny, drogowy),
bankowość, infrastruktura rynków finansowych, opieka zdrowotna, woda pitna, ścieki,
infrastruktura cyfrowa (m.in. IXP, dostawcy usług DNS, rejestry nazw TLD, dostawcy chmury,
centra danych, CDN, dostawcy usług zaufania, publiczne sieci i usługi łączności elektronicznej),
zarządzanie usługami ICT B2B (dostawcy usług zarządzanych i zarządzanych usług bezpieczeństwa),
administracja publiczna, przestrzeń kosmiczna.

**Załącznik II - inne sektory krytyczne:** usługi pocztowe i kurierskie, gospodarowanie odpadami,
chemikalia (produkcja, wytwarzanie, dystrybucja), żywność (produkcja, przetwarzanie,
dystrybucja), produkcja (m.in. wyroby medyczne, komputery i elektronika, urządzenia elektryczne,
maszyny, pojazdy samochodowe i inny sprzęt transportowy), dostawcy usług cyfrowych (internetowe
platformy handlowe, wyszukiwarki internetowe, platformy usług sieci społecznościowych),
organizacje badawcze.

Podmiot spoza obu załączników -> co do zasady poza zakresem; sprawdź jeszcze, czy transpozycja
krajowa nie rozszerza katalogu (pole [DO SPRAWDZENIA] w karcie).

### Krok 2 - size-cap i wyjątki niezależne od rozmiaru (art. 2)

**Reguła size-cap (art. 2 ust. 1):** dyrektywa obejmuje podmioty z załącznika I lub II, które są
co najmniej **średnimi przedsiębiorstwami** według zalecenia 2003/361/WE (orientacyjnie: od 50
pracowników lub powyżej 10 mln EUR obrotu rocznego / sumy bilansowej; duże: od 250 pracowników
lub powyżej 50 mln EUR obrotu / 43 mln EUR sumy bilansowej). Mikro i małe firmy - co do zasady
poza zakresem.

**Wyjątki niezależne od rozmiaru (art. 2 ust. 2-4)** - podmiot podlega bez względu na wielkość,
m.in. gdy:
- jest dostawcą publicznych sieci łączności elektronicznej lub publicznie dostępnych usług
  łączności elektronicznej,
- jest dostawcą usług zaufania, rejestrem nazw TLD lub dostawcą usług DNS,
- jest jedynym w państwie dostawcą usługi kluczowej dla utrzymania krytycznej działalności
  społecznej lub gospodarczej,
- zakłócenie jego usługi mogłoby mieć istotny wpływ na bezpieczeństwo publiczne, ochronę ludności
  lub zdrowie publiczne, albo wywołać istotne ryzyko systemowe,
- ma krytyczne znaczenie na szczeblu krajowym lub regionalnym,
- jest podmiotem administracji publicznej (rządowej centralnej; regionalnej - według decyzji
  państwa członkowskiego),
- został uznany za podmiot krytyczny na podstawie dyrektywy CER (2022/2557).

### Krok 3 - podmiot kluczowy czy ważny (art. 3)

**Kluczowe** (orientacyjnie): duże podmioty z sektorów załącznika I; niezależnie od rozmiaru -
kwalifikowani dostawcy usług zaufania, rejestry TLD i dostawcy usług DNS; dostawcy publicznych
sieci łączności co najmniej średni; podmioty krytyczne według CER; podmioty wskazane przez
państwo członkowskie jako kluczowe. **Ważne**: pozostałe podmioty w zakresie (średnie z
załącznika I oraz średnie i duże z załącznika II). Ostateczny podział w Polsce określa ustawa KSC
po nowelizacji - klasyfikację krajową oznacz [DO SPRAWDZENIA] do czasu potwierdzenia w Kroku 0.
Konsekwencja podziału: inny nadzór (ex ante vs ex post) i inne pułapy kar (Krok 7).

### Krok 4 - mapa 10 środków zarządzania ryzykiem (art. 21 ust. 2)

Wszystkie podmioty w zakresie (kluczowe i ważne) wdrażają środki proporcjonalne do ryzyka,
obejmujące CO NAJMNIEJ:

1. polityki analizy ryzyka i bezpieczeństwa systemów informatycznych,
2. obsługę incydentów,
3. ciągłość działania (kopie zapasowe, przywracanie po katastrofie) i zarządzanie kryzysowe,
4. bezpieczeństwo łańcucha dostaw, w tym relacje z bezpośrednimi dostawcami i usługodawcami,
5. bezpieczeństwo w nabywaniu, rozwoju i utrzymaniu sieci i systemów informatycznych, w tym
   obsługę i ujawnianie podatności,
6. polityki i procedury oceny skuteczności środków zarządzania ryzykiem cyberbezpieczeństwa,
7. podstawowe praktyki cyberhigieny i szkolenia z cyberbezpieczeństwa,
8. polityki i procedury stosowania kryptografii, w stosownych przypadkach szyfrowania,
9. bezpieczeństwo zasobów ludzkich, politykę kontroli dostępu i zarządzanie aktywami,
10. uwierzytelnianie wieloskładnikowe lub ciągłe, zabezpieczoną komunikację głosową, wideo i
    tekstową oraz zabezpieczone systemy łączności awaryjnej - w stosownych przypadkach.

Dla każdego środka zapytaj użytkownika o status (wdrożony / częściowo / brak / nie wiem) i wpisz
do mapy. "Nie wiem" to luka, nie zero - nie zgaduj za użytkownika.

### Krok 5 - raportowanie incydentu istotnego (art. 23)

**Incydent istotny** (art. 23 ust. 3): spowodował lub może spowodować dotkliwe zakłócenia
operacyjne usług lub straty finansowe podmiotu, ALBO wpłynął lub może wpłynąć na inne osoby
(fizyczne lub prawne), powodując znaczne szkody majątkowe lub niemajątkowe.

Zegar (biegnie od powzięcia wiedzy o incydencie istotnym):
- **24h** - wczesne ostrzeżenie do CSIRT lub organu właściwego (w tym: czy podejrzewa się
  działanie bezprawne lub w złym zamiarze, czy możliwy skutek transgraniczny),
- **72h** - zgłoszenie incydentu (aktualizacja wczesnego ostrzeżenia, wstępna ocena powagi,
  skutków, wskaźniki naruszenia integralności - IoC),
- na żądanie CSIRT/organu - **raport pośredni** o postępach,
- **1 miesiąc** od zgłoszenia - **raport końcowy** (szczegółowy opis, rodzaj zagrożenia,
  przyczyna źródłowa, zastosowane środki, skutek transgraniczny); jeśli incydent nadal trwa -
  raport z postępów, a raport końcowy w miesiąc od zakończenia obsługi incydentu.
- W stosownych przypadkach - powiadomienie odbiorców usług, których incydent może dotyczyć.

Adresata zgłoszeń w Polsce (właściwy CSIRT / organ) określa ustawa KSC po nowelizacji -
[DO SPRAWDZENIA w Kroku 0]. Przy incydencie ŻYWYM: skill układa zegar i draft, ale odsyła do
procedury reagowania i człowieka. Dane osobowe w incydencie -> równolegle `rodo-naruszenie-72h-pl`.

### Krok 6 - organ zarządzający (art. 20)

Zarząd (organ zarządzający) podmiotu kluczowego i ważnego: **zatwierdza** środki zarządzania
ryzykiem z art. 21, **nadzoruje** ich wdrażanie i **może ponosić odpowiedzialność** za naruszenia
tego artykułu przez podmiot. Członkowie organu mają obowiązek **odbywać szkolenia** z
cyberbezpieczeństwa i powinni oferować analogiczne szkolenia pracownikom. Zakres odpowiedzialności
osobistej w Polsce (kara pieniężna dla kierownika, inne sankcje) - [DO SPRAWDZENIA w ustawie KSC
po nowelizacji].

### Krok 7 - kary (art. 34)

Pułapy z dyrektywy (maksima, które państwo musi co najmniej przewidzieć):
- podmioty **kluczowe**: co najmniej do **10 000 000 EUR lub 2%** łącznego rocznego światowego
  obrotu przedsiębiorstwa - kwota wyższa,
- podmioty **ważne**: co najmniej do **7 000 000 EUR lub 1,4%** obrotu - kwota wyższa.

Konkretne widełki złotówkowe, kary dla kierowników i środki nadzorcze (w tym możliwość
tymczasowego zakazu pełnienia funkcji zarządczych w podmiocie kluczowym - [DO SPRAWDZENIA numer
artykułu i kształt w transpozycji]) określa ustawa KSC po nowelizacji - [DO SPRAWDZENIA].

## Format wyniku - karta NIS2 (szablon dosłowny)

```
KARTA NIS2 - [podmiot] - [data analizy]

STAN TRANSPOZYCJI PL (Krok 0): [wynik z ISAP/sejm-eli-mcp + data sprawdzenia / DO SPRAWDZENIA]
Reżim analizy: [ustawa KSC po nowelizacji / dyrektywa 2022/2555 jako mapa + KSC 2018 przejściowo]

W ZAKRESIE: [TAK / NIE / DO SPRAWDZENIA]
Kategoria podmiotu: [kluczowy / ważny / poza zakresem / DO SPRAWDZENIA]
Sektor: [załącznik I lub II - sektor - podsektor]
Podstawa objęcia: [size-cap: średni/duży / wyjątek niezależny od rozmiaru: który]

MAPA 10 ŚRODKÓW (art. 21 ust. 2) - status wg deklaracji użytkownika:
| # | Środek                                        | Status                  | Luka |
| 1 | polityki analizy ryzyka i bezpieczeństwa      | [wdrożony/częściowo/brak/nie wiem] | ... |
| 2 | obsługa incydentów                            | ...                     | ...  |
| ... (wszystkie 10)                                                                  |

ZEGAR RAPORTOWANIA (art. 23) - [tryb: symulacja / incydent żywy]:
- powzięcie wiedzy: [data+godzina lub "n/d"]
- wczesne ostrzeżenie (24h):  [deadline]
- zgłoszenie incydentu (72h): [deadline]
- raport końcowy (1 miesiąc): [deadline]
- adresat: [CSIRT/organ wg transpozycji - DO SPRAWDZENIA jeśli nieustalone]
- dane osobowe w incydencie: [TAK -> równolegle rodo-naruszenie-72h-pl / NIE]

ZARZĄD (art. 20): [zatwierdzenie środków: status | nadzór: status | szkolenia: status]

EKSPOZYCJA NA KARY: [pułap wg kategorii: 10 mln EUR / 2% albo 7 mln EUR / 1,4%]

LUKI: [ponumerowana lista - w tym każde "nie wiem" z mapy środków]
NASTĘPNE KROKI: [1-5 pozycji, od najpilniejszej]
TAGI PEWNOŚCI: [co zweryfikowane w sesji, co DO SPRAWDZENIA]
```

## Bramka człowieka

Karta NIS2 to projekt do decyzji, nie rozstrzygnięcie. Klasyfikację podmiotu, decyzję o
zgłoszeniu incydentu i wysyłkę czegokolwiek do CSIRT lub organu właściwego zatwierdza i wykonuje
uprawniony człowiek (zarząd / CISO / pełnomocnik / prawnik). Przy incydencie żywym skill nie
przejmuje reagowania - układa zegar i drafty, resztę prowadzi procedura i człowiek. Wysyłka nigdy
nie jest automatyczna.

## Companion skills

- `rodo-naruszenie-72h-pl` - równoległy zegar RODO, gdy incydent obejmuje dane osobowe,
- `matematic-konstytucja-ai` - reguły governance przy wdrażaniu AI w organizacji objętej NIS2,
- konektor **sejm-eli-mcp** - stan ustawy o KSC i nowelizacji w ISAP (Krok 0),
- konektor **mcp-eu-compliance** - tekst dyrektywy (UE) 2022/2555 z EUR-Lex do weryfikacji
  przepisów.

## Weryfikacja źródeł

Numery artykułów w tym skillu pochodzą z tekstu dyrektywy (UE) 2022/2555; przed wpisaniem do
deliverable zweryfikuj każde powołanie w EUR-Lex (CELEX 32022L2555, przez mcp-eu-compliance), a
stan prawa polskiego w ISAP (sejm-eli-mcp). Obowiązują tagi pewności fundamentu weryfikacyjnego:
zweryfikowane / [DO SPRAWDZENIA] / nie używać. Sygnatury i numery, których nie potwierdzisz w
sesji, zostają z tagiem [DO SPRAWDZENIA] - nigdy nie wymyślaj numeru przepisu ani progu kary.
