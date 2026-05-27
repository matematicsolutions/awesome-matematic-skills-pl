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
]);

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
