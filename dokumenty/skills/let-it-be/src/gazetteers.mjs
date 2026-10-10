// Gazetteery PL zaszyte w silniku (samodzielnosc - brak zewnetrznych JSON).
//
// 1. POLISH_FIRST_NAMES - lista trzonowa najpopularniejszych polskich imion.
//    Sluzy detekcji OSOBA ("Imie Nazwisko") - czego pl-entities NIE mial
//    (tam OSOBA byla LLM-fallback). To wartosc dodana tego skilla:
//    deterministyczna detekcja osob bez wysylania tekstu do modelu.
//    Lista nie jest wyczerpujaca - to ~120 najczestszych imion (GUS top).
//    Nazwiska po imieniu lapiemy heurystyka regex (slowo z wielkiej litery,
//    opcjonalny czlon dwuczlonowy z lacznikiem).
//
// 2. WSA_CITY_PREFIXES - rozszyfrowanie skrotow miast w sygnaturach WSA.
//
// 3. COURTS - trzonowa lista sadow najwyzszego szczebla (metadata enrichment).

export const POLISH_FIRST_NAMES = new Set([
    // meskie
    "Adam", "Adrian", "Aleksander", "Andrzej", "Antoni", "Arkadiusz", "Artur",
    "Bartlomiej", "Bartosz", "Bogdan", "Cezary", "Damian", "Daniel", "Dariusz",
    "Dawid", "Dominik", "Emil", "Eryk", "Filip", "Franciszek", "Grzegorz",
    "Gustaw", "Henryk", "Hubert", "Igor", "Ireneusz", "Jacek", "Jakub", "Jan",
    "Janusz", "Jaroslaw", "Jerzy", "Jozef", "Kacper", "Kamil", "Karol",
    "Kazimierz", "Konrad", "Krzysztof", "Lech", "Leszek", "Lukasz", "Maciej",
    "Marcin", "Marek", "Mariusz", "Mateusz", "Michal", "Mikolaj", "Miroslaw",
    "Norbert", "Oskar", "Pawel", "Piotr", "Przemyslaw", "Rafal", "Robert",
    "Roman", "Ryszard", "Sebastian", "Slawomir", "Stanislaw", "Stefan",
    "Szymon", "Tadeusz", "Tomasz", "Waldemar", "Wiktor", "Wlodzimierz",
    "Wojciech", "Zbigniew", "Zdzislaw", "Zygmunt",
    // zenskie
    "Agata", "Agnieszka", "Aleksandra", "Alicja", "Aneta", "Anna", "Barbara",
    "Beata", "Bozena", "Danuta", "Dorota", "Edyta", "Elzbieta", "Emilia",
    "Ewa", "Gabriela", "Grazyna", "Halina", "Hanna", "Helena", "Iga", "Ilona",
    "Irena", "Iwona", "Izabela", "Jadwiga", "Joanna", "Jolanta", "Julia",
    "Justyna", "Karolina", "Katarzyna", "Kinga", "Klaudia", "Krystyna",
    "Lena", "Lidia", "Magdalena", "Malgorzata", "Maria", "Marta", "Martyna",
    "Marzena", "Monika", "Natalia", "Oliwia", "Patrycja", "Paulina", "Renata",
    "Sandra", "Sylwia", "Teresa", "Urszula", "Weronika", "Wiktoria", "Wioletta",
    "Zofia", "Zuzanna",
    // uzupelnienie 2026-09-24 (czeste imiona spoza pierwotnej listy)
    "Albert", "Aleksy", "Alfred", "Boguslaw", "Boleslaw", "Borys", "Bronislaw",
    "Czeslaw", "Edmund", "Edward", "Ernest", "Eugeniusz", "Feliks", "Gerard",
    "Hieronim", "Ignacy", "Julian", "Kajetan", "Kornel", "Leon", "Leonard",
    "Lucjan", "Ludwik", "Maksymilian", "Marian", "Mieczyslaw", "Milosz",
    "Olaf", "Oliwer", "Patryk", "Radoslaw", "Remigiusz", "Sylwester", "Tymon",
    "Tymoteusz", "Waclaw", "Wieslaw", "Witold", "Wladyslaw", "Zenon",
    "Aldona", "Celina", "Czeslawa", "Dagmara", "Daria", "Diana", "Dominika",
    "Ewelina", "Honorata", "Jagoda", "Janina", "Kamila", "Karina", "Kornelia",
    "Laura", "Lucja", "Lucyna", "Maja", "Marianna", "Marlena", "Milena",
    "Nikola", "Olga", "Regina", "Roksana", "Sabina", "Stanislawa", "Stefania",
    "Tamara", "Wanda", "Zaneta", "Genowefa", "Wieslawa", "Bogumila",
]);

/** Mianowniki imion malymi literami - do kolejnosci "Nazwisko Imie" z tabel. */
export const FIRST_NAMES_NOM = new Set([...POLISH_FIRST_NAMES].map((n) => n.toLowerCase()));

/**
 * Wszystkie formy odmiany imion z POLISH_FIRST_NAMES, malymi literami i bez
 * ogonkow. W pismie osoba rzadko stoi w mianowniku: "powodki Anny Zielinskiej",
 * "pozwanemu Janowi Kowalskiemu", "z Pawlem Nowakiem". Lista mianownikow
 * gubila kazda taka osobe - a razem z nia wszystkie dalsze wystapienia nazwiska.
 */
export const FIRST_NAME_FORMS = (() => {
    const out = new Set();
    const dodaj = (rdzen, koncowki) => { for (const k of koncowki) out.add(rdzen + k); };
    for (const imie of POLISH_FIRST_NAMES) {
        const n = imie.toLowerCase();
        out.add(n);
        if (n.endsWith("a")) {
            dodaj(n.slice(0, -1), ["a", "y", "i", "ie", "e", "o"]);
        } else if (n.endsWith("y")) {
            dodaj(n.slice(0, -1), ["ego", "emu", "ym"]);
        } else if (n.endsWith("i")) {
            dodaj(n, ["ego", "emu", "m"]);
        } else {
            const meskie = ["a", "owi", "em", "ie", "u", "e"];
            dodaj(n, meskie);
            // e ruchome: Marek -> Marka, Pawel -> Pawla, Zbigniew bez zmian.
            const ruchome = n.match(/^(.*)e([klc])$/);
            if (ruchome) dodaj(ruchome[1] + ruchome[2], meskie);
        }
    }
    return out;
})();

/** Skroty miast w sygnaturach WSA (np. "II SA/Wa 1234/24" -> Warszawa). */
export const WSA_CITY_PREFIXES = {
    Wa: "Warszawa", Kr: "Krakow", Po: "Poznan", Gd: "Gdansk", Wr: "Wroclaw",
    Op: "Opole", Bd: "Bydgoszcz", Bk: "Bialystok", Gl: "Gliwice", Ke: "Kielce",
    Lu: "Lublin", Lo: "Lodz", Ol: "Olsztyn", Rz: "Rzeszow", Sz: "Szczecin",
    Go: "Gorzow Wielkopolski", Ki: "Kielce",
};

/** Trzonowa lista sadow/organow najwyzszego szczebla. */
export const COURTS = [
    { id: "sn", name: "Sad Najwyzszy", aliases: ["SN", "Sąd Najwyższy"] },
    { id: "nsa", name: "Naczelny Sad Administracyjny", aliases: ["NSA"] },
    { id: "tk", name: "Trybunal Konstytucyjny", aliases: ["TK", "Trybunał Konstytucyjny"] },
    { id: "kio", name: "Krajowa Izba Odwolawcza", aliases: ["KIO"] },
];
