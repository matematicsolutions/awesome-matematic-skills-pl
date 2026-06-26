# Standard cytatu i tagów pewności

Wspólny standard dla wszystkich skilli w tym repo. Każdy plugin odwołuje się do niego w swoim `CLAUDE.md`. Cel: pewność źródła widać na pierwszy rzut oka, a model nie zmyśla sygnatur.

## Trzy klasy pewności

Każda teza nosząca ciężar prawny (przepis, sygnatura, cytat z wyroku, postanowienie umowne) należy do jednej z trzech klas. Klasa ma być widoczna od razu, przy linii, której dotyczy - nie zbiorczo na końcu akapitu.

- **Zweryfikowane** - źródło sprawdzone w tej sesji. Zapis z pełną sygnaturą i źródłem: `(kodeks cywilny art. 415, ISAP)` albo `(wyrok SN II CSK 33/19, SAOS)`.
- **Do sprawdzenia** - informacja prawdopodobna, ale niezweryfikowana. Zapis inline przy zdaniu: `[sprawdź w SAOS]`, `[zweryfikuj sygnaturę]`.
- **Nie używać** - zmyślona sygnatura, nieistniejący przepis, cytat bez źródła. Pomiń. Nigdy nie wymyślaj numeru sprawy ani jednostki redakcyjnej, żeby zapełnić lukę.

Samo istnienie sygnatury nie wystarcza. Trzeba sprawdzić treść - czy ten przepis mówi to, co mu przypisujesz, i czy ten wyrok rozstrzyga to, co cytujesz.

## Format zapisu

- **Orzeczenie:** sąd + sygnatura + rok: `wyrok NSA II FSK 1234/20`, `postanowienie SN III CZP 45/21`. Sygnatura w oryginalnej pisowni.
- **Ustawa / akt:** nazwa (małą literą) + jednostka redakcyjna: `kodeks cywilny art. 415`, `RODO art. 6 ust. 1 lit. f`. Zakres jednostek przez łącznik: `art. 2-4`.
- **Dziennik / publikator:** gdy podajesz numer aktu - `Dz.U. 2018 poz. 1000`.
- **Źródło bazy:** dopisz, skąd potwierdzenie - `SAOS`, `EUR-Lex`, `ISAP`, `KRS`.

## Hierarchia źródeł

1. Pierwotne: ISAP / Dziennik Ustaw, SAOS, EUR-Lex (Cellar), KRS, rejestry urzędowe.
2. Wtórne: literatura, komentarze - tylko gdy dostarczył je użytkownik lub licencja pozwala.
3. Nigdy: sama pamięć modelu jako jedyna podstawa.

## Czego ten standard NIE robi

- Nie zastępuje weryfikacji merytorycznej przez prawnika.
- Nie ocenia, czy cytowane orzecznictwo jest aktualne (linia orzecznicza bywa zmienna) - to ocena człowieka.
- Nie rozstrzyga sporów interpretacyjnych - oznacza tylko, czy źródło zostało potwierdzone.
