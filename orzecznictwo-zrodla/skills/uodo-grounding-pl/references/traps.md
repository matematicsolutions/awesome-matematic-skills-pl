# Pułapki domenowe UODO / RODO - guardrails

Błędy specyficzne dla ochrony danych, których generyczny grounding nie złapie. Czytaj PRZED
weryfikacją. Wzorzec za biblioteką Jeanne Sulzer („classic traps").

## 1. GIODO vs Prezes UODO - cezura 25 maja 2018 r. (NAJWAŻNIEJSZA)

- Przed 25.05.2018: organem był **Generalny Inspektor Ochrony Danych Osobowych (GIODO)**, podstawa -
  ustawa o ochronie danych osobowych z 29 sierpnia **1997 r.**
- Od 25.05.2018: **Prezes Urzędu Ochrony Danych Osobowych (Prezes UODO)**, podstawa - **RODO**
  (rozporządzenie UE 2016/679) + ustawa krajowa z 10 maja **2018 r.**

**Reguła:** decyzji GIODO nie przypisuj „Prezesowi UODO" ani odwrotnie. Model nagminnie myli oba
organy i obie ustawy. To domenowy odpowiednik pułapki stanu prawnego Pzp (2004 vs 2019) - kotwica
sygnatury może być poprawna, a przypisanie organu/podstawy błędne. Sprawdź datę decyzji.

## 2. RODO (UE) vs krajowa ustawa o ochronie danych osobowych

- **RODO** = rozporządzenie Parlamentu Europejskiego i Rady (UE) 2016/679. Cytujesz: `art. 5 ust. 1
  lit. f RODO`, `art. 6 ust. 1 RODO`, `art. 32 RODO`, `art. 33`, `art. 34`, `art. 83 RODO` (kary).
- **Ustawa o ochronie danych osobowych z 10 maja 2018 r.** - akt KRAJOWY uzupełniający RODO
  (procedura, Prezes UODO, sankcje dla podmiotów publicznych). Inny akt, inna numeracja.

Nie pisz „art. 83 ustawy o ochronie danych osobowych" (kary są w RODO, nie w ustawie krajowej).
Weryfikuj, czy powołany przepis pochodzi z właściwego aktu. CELEX RODO: `32016R0679` (resolver UE:
`eu-sparql-search`).

## 3. Sygnatura decyzji

- `DKN.5131.<nr>.<rok>` - Departament Kontroli i Naruszeń, postępowania kontrolne/sankcyjne.
- `DS.<...>` - postępowania skargowe; `DKE.<...>` - egzekucyjne; starsze: `ZSPU/ZSPR/ZSZZS`.
  Człon środkowy koduje typ - nie zgaduj.
- Decyzja UODO ≠ wyrok WSA/NSA ze skargi (pkt 4).

## 4. Decyzja administracyjna vs wyrok sądu administracyjnego

Decyzja Prezesa UODO jest zaskarżalna do **WSA w Warszawie**, a wyrok WSA - skargą kasacyjną do
**NSA**. To trzy różne dokumenty, trzy sygnatury, trzy organy. „UODO nałożyła karę X" (decyzja) to
nie to samo co „WSA utrzymał/uchylił" (wyrok). Sprawdź, czy decyzja nie została wzruszona przez sąd -
powołanie samej decyzji bez wzmianki o jej uchyleniu bywa mylące.

## 5. Kara: podstawa, waluta, adresat

- Maksima kar w RODO liczone w EUR / % rocznego obrotu (art. 83 ust. 4-6), ale kara nakładana jest
  **w PLN**. Weryfikuj kwotę i walutę - nie przepisuj „mln EUR" jako „mln PLN".
- Sprawdź adresata (administrator vs podmiot przetwarzający) i podstawę konkretnego naruszenia.

## 6. Strona uodo.gov.pl wroga botom (ograniczenie techniczne)

`/decyzje/<sygnatura>` zwraca 500 dla prostego fetcha, treść renderowana JS, TLS bywa niespójny.
**Skutek dla weryfikacji:** poziom FRAGMENT (cytat dosłowny) często NIE jest osiągalny bez pobrania
PDF decyzji / realnego Chrome (byob) / tekstu od użytkownika. Bez tekstu - status ⛔ BRAK ŹRÓDŁA,
nigdy „prawdopodobnie ok". Drabinka: `references/drabinka-zrodel.md`.

## 7. Wspólne (przypomnienie)

- Teza decyzji vs cytat z ustaleń strony / fragmentu opisowego - przypisuj Prezesowi UODO tylko to,
  co rozstrzygnął, nie twierdzenia uczestnika. Przy `cytat_doslowny` podpierającym tezę - dodaj
  rekord `stanowisko_sadu`.
