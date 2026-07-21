---
name: ai-act-triage-pl
description: >-
  Szybki triage systemu pod AI Act (rozporządzenie (UE) 2024/1689) - 20-40 minut
  w łańcuchu ośmiu pytań: czy to w ogóle "system AI" (art. 3 pkt 1), czy praktyka
  nie jest zakazana (art. 5), czy to wysokie ryzyko (art. 6 + załączniki I i III),
  czy w grę wchodzi GPAI (rozdział V), jakie obowiązki przejrzystości (art. 50),
  jaka rola podmiotu (dostawca / podmiot stosujący / importer / dystrybutor plus
  rekwalifikacja z art. 25), jaka mapa obowiązków i terminów. Na końcu karta
  triage: klasyfikacja + rola + zastosowalne rozdziały + luki + następne kroki +
  tagi pewności. Wynik zasila matematic-konstytucja-ai i rejestr systemów AI
  organizacji. To triage, nie pełna ocena zgodności. Używaj gdy: "czy to podpada
  pod AI Act", "klasyfikacja systemu AI", "wysokie ryzyko załącznik III", "jaka
  jest nasza rola pod AI Act", "triage AI Act", "czy nasz chatbot ma obowiązki".
license: Apache-2.0
allowed-tools: [Read, Bash]
data-residency: local
requires-human-approval: true
pii-egress: none
metadata:
  author: Wiesław Mazur / MateMatic
  version: 1.1.0
  inspiration: dekompozycja triage -> rola -> obowiązki -> raport to utrwalony wzorzec w ekosystemie compliance; treść napisana od zera na tekście rozporządzenia (UE) 2024/1689
  companion_skills: matematic-konstytucja-ai, legal-ai-audit-bundle, rodo-dpia-pl, konektor mcp-eu-compliance
---

# AI Act Triage PL - szybka klasyfikacja systemu pod rozporządzenie (UE) 2024/1689

## Filozofia

**Zanim organizacja zamówi pełny audyt zgodności, powinna wiedzieć, czy w ogóle ma problem - i jak duży.**

Większość pytań "czy AI Act nas dotyczy" nie wymaga stu stron analizy. Wymaga
uporządkowanego łańcucha rozstrzygnięć, w którym każde pytanie zamyka albo otwiera
kolejne: definicja -> zakazy -> wysokie ryzyko -> GPAI -> przejrzystość -> rola ->
mapa obowiązków -> raport. Po 20-40 minutach organizacja ma kartę triage: wie, w
którym koszyku siedzi system, kim jest w łańcuchu wartości i co z tego wynika.

Karta nie jest opinią prawną. Jest ustrukturyzowanym punktem wyjścia: wejściem do
Konstytucji AI (`matematic-konstytucja-ai`), wpisem do rejestru systemów AI
organizacji i decyzją, czy sprawa idzie do człowieka i pełnej analizy.

## Kiedy używać

- Organizacja wdraża lub kupuje narzędzie z komponentem AI i pyta "czy to podpada pod AI Act".
- Inwentaryzacja: trzeba przejść listę systemów i każdy wstępnie zaklasyfikować.
- Dostawca softu pyta, czy jego produkt to system wysokiego ryzyka albo GPAI.
- Kancelaria buduje rejestr systemów AI klienta albo własny.
- Przed warsztatem Konstytucji AI - karta triage per system to materiał wejściowy.

## Czego NIE robi

- **Nie zastępuje pełnej oceny zgodności ani conformity assessment.** Karta mówi
  "to wygląda na wysokie ryzyko z zał. III pkt X", nie "spełniacie art. 8-15".
- **Nie wydaje opinii prawnej.** Wynik to projekt klasyfikacji do zatwierdzenia
  przez uprawnionego człowieka.
- **Przy wyniku wysokie ryzyko, GPAI albo podejrzeniu praktyki zakazanej kieruje
  do człowieka i pełnej analizy.** Triage się wtedy kończy, nie pogłębia.
- Nie ocenia zgodności z RODO - styk sygnalizuje i odsyła do `rodo-dpia-pl`.
- Nie wykonuje FRIA - tylko sygnalizuje, że jest wymagana (krok 7).

## Workflow 8 kroków (plus bramka wejściowa)

### Krok 0 - weryfikacja przepisu (obowiązkowy, przed każdym cytowaniem)

Żaden numer artykułu ani treść przepisu nie wchodzi do karty z pamięci modelu.
Przed wpisaniem podstawy prawnej pobierz aktualny tekst rozporządzenia (UE)
2024/1689 z EUR-Lex (CELEX 32024R1689) albo przez konektor `mcp-eu-compliance`
i porównaj brzmienie. Zanotuj w karcie datę pobrania i źródło. Przepis, którego
nie dało się zweryfikować w sesji, dostaje tag `[sprawdź w EUR-Lex]` i nie może
być podstawą rozstrzygnięcia "NIE dotyczy".

### Krok 1 - czy to "system AI" (art. 3 pkt 1)

Sprawdź elementy definicji, każdy osobno:
- system maszynowy,
- zaprojektowany do działania z różnym poziomem autonomii,
- może wykazywać zdolność adaptacji po wdrożeniu,
- z otrzymanych danych wejściowych wnioskuje, jak generować wyniki (predykcje,
  treści, zalecenia, decyzje),
- wyniki mogą wpływać na środowisko fizyczne lub wirtualne.

Pomocniczo: wytyczne Komisji Europejskiej w sprawie definicji systemu AI
(numer dokumentu [DO SPRAWDZENIA] - zweryfikuj w EUR-Lex przed cytowaniem).
Kontrprzykłady poza definicją: klasyczny software czysto regułowy bez warstwy
wnioskowania, prosta automatyzacja, arkusz z formułami.

Wynik: TAK / NIE / GRANICZNE. Przy NIE - koniec triage, ale uzasadnienie i wpis
do rejestru zostają (za rok ktoś zapyta, czemu uznaliście, że to nie system AI).

### Krok 2 - praktyki zakazane (art. 5) - checklist

Odhacz każdą literę, nie "ogólne wrażenie":
- [ ] techniki podprogowe lub celowo manipulacyjne prowadzące do poważnej szkody
- [ ] wykorzystywanie słabości osób (wiek, niepełnosprawność, sytuacja społeczna
      lub ekonomiczna)
- [ ] scoring społeczny prowadzący do nieuzasadnionego niekorzystnego traktowania
- [ ] ocena ryzyka popełnienia przestępstwa wyłącznie na podstawie profilowania
      lub cech osobowości
- [ ] nieukierunkowane scrapowanie wizerunków twarzy z internetu lub monitoringu
      do budowy baz rozpoznawania twarzy
- [ ] rozpoznawanie emocji w miejscu pracy i w edukacji (poza wyjątkami
      medycznymi i bezpieczeństwa)
- [ ] kategoryzacja biometryczna wnioskująca cechy wrażliwe (rasa, poglądy,
      przynależność związkowa, religia, życie seksualne, orientacja)
- [ ] zdalna identyfikacja biometryczna w czasie rzeczywistym w przestrzeni
      publicznej do celów ścigania (wąskie wyjątki)

Pomocniczo: wytyczne KE w sprawie praktyk zakazanych (numer dokumentu
[DO SPRAWDZENIA]). Zakazy obowiązują od 2.2.2025 - to stan prawny, nie prognoza.
PODEJRZENIE choćby jednej litery = STOP, natychmiast bramka człowieka.

### Krok 3 - wysokie ryzyko (art. 6 + załącznik I + załącznik III)

Dwie ścieżki kwalifikacji:
- **Ścieżka A (art. 6 ust. 1, zał. I):** system jest produktem albo związanym z
  bezpieczeństwem elementem produktu objętego unijnym prawodawstwem
  harmonizacyjnym z zał. I i podlega ocenie zgodności strony trzeciej
  (maszyny, wyroby medyczne, zabawki, dźwigi, lotnictwo, pojazdy itd.).
- **Ścieżka B (art. 6 ust. 2, zał. III):** use-case z obszarów: biometria;
  infrastruktura krytyczna; edukacja i szkolenie zawodowe; zatrudnienie i
  zarządzanie pracownikami; dostęp do usług zasadniczych (m.in. scoring
  kredytowy, wycena ubezpieczeń na życie i zdrowotnych, dysponowanie służbami
  ratunkowymi, świadczenia publiczne); egzekwowanie prawa; migracja, azyl i
  granice; wymiar sprawiedliwości i procesy demokratyczne.

**Filtr art. 6 ust. 3:** system z zał. III nie jest wysokiego ryzyka, gdy nie
stwarza znaczącego ryzyka szkody, bo wykonuje wyłącznie: wąskie zadanie
proceduralne / poprawia wynik zakończonej czynności człowieka / wykrywa wzorce
lub odchylenia bez zastępowania oceny człowieka / zadanie przygotowawcze.
Wyjątek od wyjątku: profilowanie osób fizycznych = zawsze wysokie ryzyko.
Skorzystanie z filtra wymaga udokumentowania oceny i rejestracji systemu
(art. 6 ust. 4 i art. 49 ust. 2 [DO SPRAWDZENIA] - zweryfikuj oba numery).

### Krok 4 - GPAI (rozdział V)

- Czy podmiot dostarcza model AI ogólnego przeznaczenia (definicja w art. 3,
  pkt [DO SPRAWDZENIA]) albo integruje cudzy model we własnym systemie?
- Obowiązki dostawców modeli GPAI: dokumentacja techniczna, informacje dla
  dostawców niższego szczebla, polityka prawnoautorska, streszczenie danych
  treningowych (art. 53). Częściowe wyłączenie dla modeli open-source - nie
  obejmuje modeli z ryzykiem systemowym.
- **Próg ryzyka systemowego (art. 51):** domniemanie, gdy łączna moc obliczeniowa
  treningu przekracza 10^25 FLOP; wtedy dodatkowe obowiązki z art. 55 (ewaluacje
  modelu, testy kontradyktoryjne, raportowanie incydentów, cyberbezpieczeństwo).
- Kodeks postępowania GPAI (art. 56) - status i wersję zweryfikuj w źródle
  [DO SPRAWDZENIA].

Typowy wynik dla kancelarii i MŚP: podmiot stosujący system zbudowany na GPAI,
nie dostawca modelu. Ale patrz krok 6 - rekwalifikacja.

### Krok 5 - obowiązki przejrzystości (art. 50)

- Interakcja z człowiekiem (chatbot): poinformuj, że rozmawia z AI, chyba że to
  oczywiste z kontekstu.
- Treść syntetyczna (audio, obraz, wideo, tekst): oznaczanie w formacie nadającym
  się do odczytu maszynowego po stronie dostawcy.
- Rozpoznawanie emocji / kategoryzacja biometryczna: poinformuj osoby, których
  to dotyczy.
- Deepfake: ujawnij, że treść została sztucznie wygenerowana lub zmanipulowana.
- Tekst publikowany w celu informowania o sprawach interesu publicznego: ujawnij
  udział AI, chyba że treść przeszła kontrolę redakcyjną człowieka.

Te obowiązki wchodzą ze stosowaniem zasadniczego korpusu (termin z art. 113 -
krok 7). Numery ustępów art. 50 przypisz do wierszy karty po weryfikacji w kroku 0.

### Krok 6 - rola podmiotu (+ rekwalifikacja z art. 25)

Ustal rolę: **dostawca** (provider) / **podmiot stosujący** (deployer) /
**importer** / **dystrybutor** / upoważniony przedstawiciel. Definicje w art. 3.

Test rekwalifikacji (art. 25) - stajesz się dostawcą systemu wysokiego ryzyka, gdy:
1. firmujesz system własną nazwą lub znakiem towarowym,
2. dokonujesz istotnej zmiany systemu wysokiego ryzyka,
3. zmieniasz przeznaczenie systemu tak, że staje się systemem wysokiego ryzyka.

Typowa pułapka: "nasz chatbot" na cudzym modelu, z logo organizacji na froncie.
Rola determinuje większość mapy obowiązków, więc ten krok rozstrzygnij zanim
powiesz cokolwiek o obowiązkach.

### Krok 7 - mapa obowiązków, harmonogram, sygnalizacja FRIA

Stan prawny względem daty triage (terminy z art. 113 - zweryfikuj w kroku 0):
- od 2.2.2025: zakazy (art. 5) i kompetencje w zakresie AI (art. 4) - OBOWIĄZUJĄ,
- od 2.8.2025: GPAI, governance, kary - OBOWIĄZUJĄ,
- od 2.8.2026: zasadniczy korpus, w tym wysokie ryzyko z zał. III i art. 50 -
  termin wynikający z rozporządzenia,
- do 2.8.2027: systemy wysokiego ryzyka ścieżki A (produkty z zał. I) - dłuższy
  okres z rozporządzenia.

Zbuduj mapę: rola x klasyfikacja -> zastosowalne rozdziały i artykuły -> od kiedy.

**Sygnalizacja FRIA (art. 27):** ocena skutków dla praw podstawowych przed
wdrożeniem jest wymagana od podmiotów stosujących będących podmiotami prawa
publicznego lub prywatnymi świadczącymi usługi publiczne oraz od stosujących
systemy scoringu kredytowego i wyceny ubezpieczeń na życie i zdrowotnych
(zał. III pkt 5, litery [DO SPRAWDZENIA]). Skill sygnalizuje wymóg i odsyła do
`rodo-dpia-pl` w części pokrywającej się z DPIA - nie wykonuje FRIA.

### Krok 8 - raport: karta triage

Wypełnij szablon poniżej. Karta jest wejściem do `matematic-konstytucja-ai`
(sekcje boundaries i governance) i wpisem do rejestru systemów AI organizacji.

## Format wyniku - karta triage

```
## Karta triage AI Act - <nazwa systemu>

Data: [rrrr-mm-dd] | Prowadzący: [osoba/agent] | Czas triage: [min]
Weryfikacja przepisów: EUR-Lex CELEX 32024R1689 / mcp-eu-compliance, pobrano <data>

### Klasyfikacja
| Pytanie                              | Wynik                     | Podstawa (zweryfikowana) | Tag pewności |
|--------------------------------------|---------------------------|--------------------------|--------------|
| System AI (art. 3 pkt 1)?            | TAK / NIE / GRANICZNE     | <element definicji>      | Zweryfikowane / [sprawdź w EUR-Lex] |
| Praktyka zakazana (art. 5)?          | NIE / PODEJRZENIE lit. <x>| <litera + stan faktyczny>| ... |
| Wysokie ryzyko (art. 6, zał. I/III)? | TAK zał. <I/III pkt> / NIE / wyłączony filtrem art. 6 ust. 3 | ... | ... |
| GPAI (rozdział V)?                   | NIE / model GPAI / ryzyko systemowe | ...            | ... |
| Przejrzystość (art. 50)?             | <obowiązki> / brak        | ...                      | ... |

### Rola podmiotu
Rola: dostawca / podmiot stosujący / importer / dystrybutor
Ryzyko rekwalifikacji (art. 25): TAK / NIE - <która przesłanka i dlaczego>

### Zastosowalne rozdziały i terminy (stan prawny na datę triage)
- <artykuł/rozdział> - stosuje się od <data z art. 113> - status: OBOWIĄZUJE / termin przyszły z rozporządzenia

### FRIA (art. 27)
Wymagana: TAK / NIE / DO ANALIZY - <przesłanka podmiotowa lub przedmiotowa>

### Luki (czego nie wiemy / czego brakło w stanie faktycznym)
1. ...

### Następne kroki
1. ...
[ ] Wpis do rejestru systemów AI organizacji
[ ] Przekazanie karty do matematic-konstytucja-ai (boundaries / governance)
[ ] Przy wysokim ryzyku / GPAI / podejrzeniu art. 5: eskalacja do człowieka i pełnej analizy

### Tagi pewności - podsumowanie
Zweryfikowane: <n> | Do sprawdzenia: <n> | Nie używać: 0 (wymóg twardy)
```

## Bramka człowieka

Karta triage to projekt klasyfikacji, nie decyzja. Uprawniony człowiek (prawnik,
compliance officer, wyznaczona rola z Konstytucji AI) sprawdza i zatwierdza kartę,
zanim trafi do rejestru jako obowiązująca. Trzy wyniki eskalują obowiązkowo i
natychmiast: podejrzenie praktyki zakazanej (art. 5), wysokie ryzyko, GPAI.
W tych przypadkach triage kończy się skierowaniem do człowieka i pełnej analizy -
skill nie próbuje jej zastąpić.

## Narzędzia deterministyczne (opcjonalne)

Łańcuch ośmiu pytań prowadzi człowiek. Trzy skrypty w `scripts/` dają deterministyczne
wsparcie tam, gdzie klasyfikacja i mapa obowiązków dają się policzyć maszynowo. Tylko
biblioteka standardowa Pythona, praca lokalna, nic nie wychodzi na zewnątrz. Nie zastępują
Kroku 0: cytaty w skryptach idą za strukturą rozporządzenia, ale przy wpisie do karty i tak
weryfikuj artykuł w EUR-Lex. Każdy skrypt kończy banner "INTERPRETACJA MateMatic".

- `klasyfikator_ryzyka_ai.py` - poziom ryzyka wg art. 5 / 6 / 50 + załącznik III (drzewo
  decyzyjne z filtrem art. 6 ust. 3 i wyjątkiem profilowania). Odpowiada krokom 2-5.
- `plan_zgodnosci.py` - dla wysokiego ryzyka: wybór modułu oceny zgodności (A kontrola
  wewnętrzna vs H jednostka notyfikowana, art. 43) i 8-punktowa checklista dokumentacji
  technicznej (załącznik IV). To warstwa, której triage celowo nie robi - następny krok
  po klasyfikacji, gdy sprawa i tak idzie do pełnej analizy.
- `tracker_obowiazkow.py` - macierz obowiązków per rola (dostawca / podmiot stosujący /
  importer / dystrybutor) posortowana wg terminów fazowania (art. 113). Odpowiada krokom 6-7.

Uruchomienie: `python scripts/<nazwa>.py` (wbudowana próbka) albo z własnym plikiem JSON;
`--output json` do dalszego przetwarzania. Referencje `references/` rozwijają załącznik III,
artykuł po artykule oraz styk z RODO.

## Companion skills

- `matematic-konstytucja-ai` - karta triage to materiał wejściowy do sekcji
  boundaries i governance Konstytucji AI; wpisz to w następnych krokach karty.
- `legal-ai-audit-bundle` - archiwizacja karty jako artefakt record-keepingu.
- `rodo-dpia-pl` - styk FRIA/DPIA i cała warstwa RODO, której ten skill nie ocenia.
- Konektor `mcp-eu-compliance` - pobranie i weryfikacja tekstu przepisu w kroku 0.

## Weryfikacja źródeł

Przepis pochodzi z bazy, nie z pamięci. Zasady twarde:
1. Każdy numer artykułu, ustępu, litery i punktu załącznika cytowany w karcie
   musi być zweryfikowany w sesji w EUR-Lex (CELEX 32024R1689) albo przez
   `mcp-eu-compliance` - inaczej dostaje tag `[sprawdź w EUR-Lex]`.
2. Tag `[DO SPRAWDZENIA]` w tym skillu oznacza miejsce, gdzie numer lub status
   dokumentu wymaga weryfikacji przed użyciem - nigdy nie cytuj go bez sprawdzenia.
3. Rozstrzygnięcie "AI Act nas nie dotyczy" nie może opierać się na
   niezweryfikowanym przepisie.
4. Wersja skonsolidowana ma pierwszeństwo przed pamięcią o brzmieniu pierwotnym -
   rozporządzenia bywają korygowane sprostowaniami.
