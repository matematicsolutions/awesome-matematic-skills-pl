# Standard odpowiedzialności, etyki i ochrony danych

Wspólny standard dla wszystkich skilli w tym repo. Zasada nadrzędna: ochrona bierze się z mechanizmów, nie z noty na końcu. Nota "to nie porada prawna" nie zatrzymuje żadnego błędu i nie przenosi żadnej odpowiedzialności.

## Pięć warstw ochrony (przed disclaimerem)

1. **Weryfikacja źródła** - przepisy i orzecznictwo z baz (ISAP, SAOS, EUR-Lex), nie z pamięci modelu.
2. **Klasa pewności** - każda teza prawna oznaczona: zweryfikowane / do sprawdzenia / nie używać (patrz `styl-cytatu.md`).
3. **Kontrola przesłanek** - fakty podane przez użytkownika sprawdza się przed analizą, nie przyjmuje na słowo.
4. **Jawny zakres ujemny** - każdy skill mówi wprost, czego NIE robi i gdzie kończy się jego kompetencja.
5. **Bramka człowieka** - uprawniona osoba sprawdza i zatwierdza wynik, biorąc odpowiedzialność zawodową.

Jeśli błąd przeszedłby bez zatrzymania przez którąś z warstw 1-5, wina jest w skillu. Naprawiamy narzędzie, nie dopisujemy noty.

## Bramka człowieka

Nic nie zostaje wysłane, złożone w sądzie, podpisane ani opublikowane, zanim sprawdzi i zatwierdzi to uprawniony człowiek. Akty nieodwracalne i skierowane na zewnątrz zostają po stronie człowieka - narzędzie przygotowuje projekt, nie wykonuje.

## Każdy wynik to projekt

Wyniki skilli to projekty wygenerowane przez AI. Gdy przekazujesz je dalej, oznacz to jawnie. Obowiązek przejrzystości wynika z aktu o sztucznej inteligencji (art. 50) - odbiorca ma wiedzieć, że pracuje z wytworem AI.

## Ochrona danych osobowych

- **Anonimizacja lokalna** - dane osobowe zastępuj znacznikami lokalnie, zanim trafią do modelu. Nie powinny wychodzić do API. To zasada minimalizacji.
- **Umowa powierzenia** - jeśli dane osobowe przetwarzane są w narzędziu zewnętrznym lub chmurze, z dostawcą musi istnieć umowa powierzenia (RODO art. 28). Sprawdź retencję i czy dane są przekazywane poza EOG.
- **Dane wrażliwe i tajemnica zawodowa** - przed wniesieniem dokumentu oceń osobno, czy materiał objęty tajemnicą lub szczególnie wrażliwy w ogóle może trafić do narzędzia. Przy wątpliwości - nie przekazuj.

## Czego ten standard NIE robi

- Nie wykrywa konfliktu interesów między zleceniami - to odpowiedzialność prawnika.
- Nie nadaje uprawnień do reprezentacji - skill nie czyni osoby nieuprawnionej pełnomocnikiem.
- Nie zastępuje porady prawnej, zwłaszcza dla osób bez wykształcenia prawniczego.
- Nie rozstrzyga, czy dane poufne wolno wprowadzić do systemu - tę ocenę podejmuje człowiek.
