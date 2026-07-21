# Zalacznik III - 8 kategorii wysokiego ryzyka + test wyjatku z art. 6 ust. 3

Referencja do decyzji 1 (klasyfikacja). Trafienie w kategorie zalacznika III uruchamia
art. 6 ust. 2 (wysokie ryzyko), chyba ze zachodzi wyjatek z art. 6 ust. 3 - i nawet wtedy
**profilowanie osob fizycznych znosi wyjatek**.

## 8 kategorii (art. 6 ust. 2 + zalacznik III)

1. **Biometria** (pkt 1) - zdalna identyfikacja biometryczna, kategoryzacja biometryczna wg cech wrazliwych, rozpoznawanie emocji (poza kontekstem zakazanym z art. 5). **Uwaga:** biometria domyslnie wymaga modulu H (jednostka notyfikowana) w ocenie zgodnosci - art. 43 ust. 1.
2. **Infrastruktura krytyczna** (pkt 2) - elementy bezpieczenstwa w zarzadzaniu ruchem drogowym, zaopatrzeniu w wode, gaz, cieplo, energie elektryczna.
3. **Ksztalcenie i szkolenie zawodowe** (pkt 3) - dostep/przyjecie, ocena efektow uczenia, ocena wlasciwego poziomu ksztalcenia, monitorowanie zabronionych zachowan podczas egzaminow.
4. **Zatrudnienie, zarzadzanie pracownikami** (pkt 4) - rekrutacja (w tym ogloszenia, przesiew, ocena kandydatow), decyzje o awansie/rozwiazaniu, przydzial zadan, monitorowanie i ocena.
5. **Dostep do uslug podstawowych** (pkt 5) - swiadczenia publiczne, **scoring kredytowy / ocena zdolnosci kredytowej**, ocena ryzyka i wycena w ubezpieczeniach na zycie i zdrowotnych, klasyfikacja zgloszen alarmowych / dyspozytornia ratunkowa.
6. **Organy scigania** (pkt 6) - ocena ryzyka ofiary/sprawcy, poligraf, ocena wiarygodnosci dowodow, przewidywanie przestepczosci (poza zakazem z art. 5 ust. 1 lit. d), profilowanie.
7. **Migracja, azyl, kontrola graniczna** (pkt 7) - poligraf, ocena ryzyka bezpieczenstwa/migracji, rozpatrywanie wnioskow o azyl/wize, wykrywanie osob.
8. **Wymiar sprawiedliwosci i procesy demokratyczne** (pkt 8) - wspomaganie organu sadowego w badaniu i interpretacji faktow i prawa, wplyw na wynik wyborow/referendum lub zachowania wyborcze.

## Test wyjatku z art. 6 ust. 3 (decyzja: czy naprawde wysokie ryzyko?)

System z zalacznika III **NIE** jest wysokiego ryzyka, jesli **nie stwarza istotnego ryzyka**
dla zdrowia, bezpieczenstwa lub praw podstawowych, bo spelnia co najmniej jeden z warunkow:

- **(a)** wykonuje **waskie zadanie proceduralne** (np. przeksztalcenie nieustrukturyzowanych danych w ustrukturyzowane, klasyfikacja dokumentow do kategorii);
- **(b)** **usprawnia wynik** wczesniej zakonczonej czynnosci czlowieka (np. poprawa jezyka pisma);
- **(c)** **wykrywa wzorce decyzyjne** lub odchylenia od nich bez zastepowania/wplywania na wczesniejsza ocene czlowieka bez odpowiedniej weryfikacji;
- **(d)** wykonuje **zadanie przygotowawcze** do oceny istotnej z punktu widzenia kategorii zalacznika III.

**Zdanie ostatnie art. 6 ust. 3 (znosnik wyjatku):** system z zalacznika III ZAWSZE jest
wysokiego ryzyka, jesli **przeprowadza profilowanie osob fizycznych**. To bramka nadrzedna -
w kliencie skryptu odpowiada za nia flaga `performs_profiling: true`.

## Jak to widzi klasyfikator

Flagi wejsciowe (`klasyfikator_ryzyka_ai.py`):

- `annex_iii_category` - jedna z: `biometria`, `infrastruktura_krytyczna`, `edukacja`, `zatrudnienie`, `uslugi_podstawowe`, `organy_scigania`, `migracja_azyl`, `wymiar_sprawiedliwosci` (albo `null`).
- `article_6_3_carveout_applies: true` - wywolujacy ocenil, ze zachodzi jeden z warunkow (a)-(d).
- `performs_profiling: true` - znosi wyjatek, utrzymuje wysokie ryzyko.
- `article_6_1_safety_component: true` - element bezpieczenstwa produktu regulowanego wg zalacznika I (osobna sciezka, art. 6 ust. 1).

Sekwencja: zakazy art. 5 -> zalacznik I (art. 6 ust. 1) -> zalacznik III (art. 6 ust. 2)
-> wyjatek art. 6 ust. 3 (znoszony przez profilowanie) -> transparentnosc art. 50 -> minimalne.

## Zrodlo tekstu

Pelny tekst Rozporzadzenia (UE) 2024/1689 pobierz przez `eu-sparql-search` (CELEX
`32024R1689`) i zweryfikuj cytat przez `citation-grounding-pl` przed umieszczeniem w memo.
Konsolidowana wersja zalacznika III moze byc zmieniana aktami delegowanymi - sprawdzaj date.
