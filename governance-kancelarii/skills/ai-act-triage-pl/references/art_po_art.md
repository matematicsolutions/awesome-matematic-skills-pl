# AI Act - kluczowe artykuly z rozbiciem na role

Referencja do decyzji 2 i 3. Cytuj artykul + ustep; nie parafrazuj bez cytatu.

## Poziomy i klasyfikacja

- **art. 5** - praktyki zakazane (8 liter a-h). Binarne, bez wyjatkow. Kara do 35 mln EUR / 7% obrotu (art. 99).
- **art. 6** - regula klasyfikacji wysokiego ryzyka. Ust. 1 = element bezpieczenstwa produktu z zalacznika I. Ust. 2 = kategorie zalacznika III. Ust. 3 = wyjatki (znoszone przez profilowanie).
- **art. 50** - obowiazki transparentnosci (ograniczone ryzyko): chatboty (ust. 1), tresci generowane/manipulowane i deepfake (ust. 4), rozpoznawanie emocji / kategoryzacja biometryczna (ust. 3).
- **art. 51-55** - GPAI (model AI ogolnego przeznaczenia). Art. 51 = prog ryzyka systemowego (>= 10^25 FLOP). Art. 53 = obowiazki dla wszystkich GPAI. Art. 55 = dodatkowe dla GPAI z ryzykiem systemowym.

## Wymogi dla wysokiego ryzyka (dostawca, art. 8-17)

- **art. 9** - system zarzadzania ryzykiem w calym cyklu zycia.
- **art. 10** - zarzadzanie danymi: jakosc danych treningowych/walidacyjnych/testowych + ograniczanie stronniczosci. (Styk z RODO - patrz `rodo_ai_act_styk.md`.)
- **art. 11 + zalacznik IV** - dokumentacja techniczna (8 pozycji, patrz `plan_zgodnosci.py`).
- **art. 12** - automatyczne rejestrowanie zdarzen (logi). To fundament art. 12 record-keeping w PATRONie.
- **art. 13** - instrukcja obslugi dla podmiotow stosujacych.
- **art. 14** - projekt umozliwiajacy nadzor ze strony czlowieka (human oversight).
- **art. 15** - dokladnosc, solidnosc, cyberbezpieczenstwo. (Reuse z ISO 27001.)
- **art. 16** - ogolne obowiazki dostawcy + osoba kontaktowa.
- **art. 17** - system zarzadzania jakoscia (SZJ). (Reuse z ISO 42001.)

## Ocena zgodnosci

- **art. 40** - normy zharmonizowane -> domniemanie zgodnosci.
- **art. 43** - procedury oceny zgodnosci. Ust. 2 + zalacznik VI = modul A (kontrola wewnetrzna). Ust. 1 + zalacznik VII = modul H (jednostka notyfikowana; wymagany dla biometrii).
- **art. 47** - deklaracja zgodnosci UE (przechowywanie 10 lat, art. 18).
- **art. 48** - oznakowanie CE.
- **art. 49 + art. 71** - rejestracja w bazie danych UE dla systemow z zalacznika III.

## Role (art. 3 + obowiazki nizszego szczebla)

- **art. 3 pkt 3** - dostawca (provider). **art. 3 pkt 4** - podmiot stosujacy (deployer). **art. 3 pkt 6** - importer. **art. 3 pkt 7** - dystrybutor.
- **art. 22** - upowazniony przedstawiciel (dostawcy spoza UE MUSZA go wyznaczyc).
- **art. 23** - obowiazki importera. **art. 24** - obowiazki dystrybutora.
- **art. 25** - odpowiedzialnosc w lancuchu wartosci. **Kluczowe:** podmiot stosujacy, ktory istotnie modyfikuje system wysokiego ryzyka lub wprowadza go pod wlasna nazwa, STAJE SIE dostawca.
- **art. 26** - obowiazki podmiotu stosujacego (uzycie wg instrukcji, nadzor, jakosc danych wejsciowych, przechowywanie logow >= 6 mc, informowanie pracownikow ust. 7).
- **art. 27** - ocena wplywu na prawa podstawowe (OWPP/FRIA) - podmioty sektora publicznego + niektore uslugi podstawowe.
- **art. 86** - prawo do wyjasnienia indywidualnej decyzji.

## Monitorowanie i incydenty

- **art. 72** - monitorowanie po wprowadzeniu do obrotu.
- **art. 73** - zglaszanie powaznych incydentow (15 dni; 2 dni dla infrastruktury krytycznej).
- **art. 79** - systemy stwarzajace ryzyko - procedura na poziomie krajowym.

## Fazowanie (art. 113)

| Data | Co wchodzi w zycie |
|---|---|
| 2025-02-02 | zakazy z art. 5 + kompetencje AI z art. 4 |
| 2025-08-02 | GPAI (art. 51-55) + zarzadzanie + kary |
| 2026-08-02 | tytul III - wysokie ryzyko (ogolne, zalacznik III) |
| 2027-08-02 | zalacznik I - sektorowe wysokie ryzyko |

## Kompetencje AI (przekrojowe)

- **art. 4** - kompetencje w zakresie AI (AI literacy) personelu majacego do czynienia z systemami AI. Obowiazuje od 2025-02-02, dotyczy KAZDEJ roli.
