#!/usr/bin/env node
// Test-harness silnika citation-grounding-pl (zero-dep). Uruchom: node test-grounding.mjs
// Rubryka PASS/FAIL per przypadek; exit 1 gdy ktorykolwiek FAIL (bramka CI).
// Pokrywa nowy guard STRONY ("prawdziwy cytat, falszywa teza") + regresje rdzenia v2.

import { existsSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { verify, stronyOverlap, partyTokens, zbieznoscFragmentu, normalize, normalizeWithMap } from "./ground-citations.mjs";

let pass = 0, fail = 0;
function check(name, got, want) {
  const ok = got === want;
  console.log(`${ok ? "PASS" : "FAIL"}  ${name}  (got=${got}${ok ? "" : ` want=${want}`})`);
  ok ? pass++ : fail++;
}

// --- GUARD STRONY -------------------------------------------------------------
// 1. Sygnatura sie zgadza, ale STRONY calkiem inne -> twardy czerwony (falszywa teza).
check("strony rozbiezne przy zgodnej sygnaturze -> NIEZWERYFIKOWANY",
  verify({
    id: "S1", source_id: "II CSK 123/19", claim_type: "fakt_proceduralny",
    anchor:          { sygnatura: "II CSK 123/19", data: "12.03.2019", strony: "Kowalski przeciwko Bank Millennium S.A." },
    anchor_resolved: { sygnatura: "II CSK 123/19", data: "2019-03-12", strony: "Nowak przeciwko Skarb Panstwa" },
  }).status, "NIEZWERYFIKOWANY");

// 2. Ta sama sprawa, INNA FORMA nazwy strony (S.A. vs Spolka Akcyjna) -> brak fałszywego czerwonego.
check("rozna forma nazwy tej samej strony -> ZWERYFIKOWANY",
  verify({
    id: "S2", source_id: "II CSK 123/19", claim_type: "fakt_proceduralny",
    anchor:          { sygnatura: "II CSK 123/19", data: "12.03.2019", strony: "Bank Millennium S.A." },
    anchor_resolved: { sygnatura: "II CSK 123/19", data: "2019-03-12", strony: "Bank Millennium Spolka Akcyjna" },
  }).status, "ZWERYFIKOWANY");

// 3. Czesciowa zgodnosc stron (jedna wspolna, jedna inna) -> miekka uwaga -> WYMAGA_OSADU.
check("czesciowa zgodnosc stron -> WYMAGA_OSADU",
  verify({
    id: "S3", source_id: "II CSK 123/19", claim_type: "fakt_proceduralny",
    anchor:          { sygnatura: "II CSK 123/19", data: "12.03.2019", strony: "Kowalski przeciwko Bank Millennium S.A." },
    anchor_resolved: { sygnatura: "II CSK 123/19", data: "2019-03-12", strony: "Bank Millennium S.A. przeciwko Skarb Panstwa" },
  }).status, "WYMAGA_OSADU");

// 4. Pojedynczy token po kazdej stronie i rozbieznosc -> NIE twardy czerwony (za malo sygnalu), miekko.
check("jednotokenowe strony rozne -> WYMAGA_OSADU (nie blokada)",
  verify({
    id: "S4", source_id: "II CSK 123/19", claim_type: "fakt_proceduralny",
    anchor:          { sygnatura: "II CSK 123/19", data: "12.03.2019", strony: "Kowalski" },
    anchor_resolved: { sygnatura: "II CSK 123/19", data: "2019-03-12", strony: "Nowak" },
  }).status, "WYMAGA_OSADU");

// 5. Brak stron w danych -> zachowanie jak dotad (bez wplywu guardu).
check("brak stron -> ZWERYFIKOWANY (backward-compat)",
  verify({
    id: "S5", source_id: "II CSK 123/19", claim_type: "fakt_proceduralny",
    anchor:          { sygnatura: "II CSK 123/19", data: "12.03.2019" },
    anchor_resolved: { sygnatura: "II CSK 123/19", data: "2019-03-12" },
  }).status, "ZWERYFIKOWANY");

// --- REGRESJE RDZENIA v2 ------------------------------------------------------
// 6. Rozbiezna sygnatura nadal twardy czerwony (istniejace zachowanie).
check("regresja: rozbiezna sygnatura -> NIEZWERYFIKOWANY",
  verify({
    id: "R1", source_id: "II CSK 123/19", claim_type: "powolanie",
    anchor:          { sygnatura: "II CSK 123/19" },
    anchor_resolved: { sygnatura: "III CZP 5/21" },
  }).status, "NIEZWERYFIKOWANY");

// 7. Doslowny cytat obecny w zrodle -> ZWERYFIKOWANY.
check("regresja: cytat doslowny obecny -> ZWERYFIKOWANY",
  verify({
    id: "R2", source_id: "II CSK 123/19", claim_type: "cytat_doslowny",
    quote: "sad zwiazany jest granicami zaskarzenia",
    source_text: "W ocenie Sadu Najwyzszego sad zwiazany jest granicami zaskarzenia oraz podstawami.",
  }).status, "ZWERYFIKOWANY");

// 8. Parafraza z pokryciem terminow -> WYMAGA_OSADU.
check("regresja: parafraza pokryta -> WYMAGA_OSADU",
  verify({
    id: "R3", source_id: "I CSK 50/18", claim_type: "stanowisko_sadu",
    claim_text: "klauzula waloryzacyjna w umowie kredytu jest dopuszczalna",
    source_text: "Sad uznal, ze klauzula waloryzacyjna w umowie kredytu jest dopuszczalna w swietle zasad wspolzycia.",
  }).status, "WYMAGA_OSADU");

// --- JEDNOSTKOWE: stronyOverlap / partyTokens --------------------------------
check("partyTokens odsiewa formy prawne i spojniki",
  JSON.stringify(partyTokens("Kowalski przeciwko Bank Millennium S.A.")),
  JSON.stringify(["kowalski", "bank", "millennium"]));

check("stronyOverlap identycznych rdzeni = 1",
  stronyOverlap("Bank Millennium S.A.", "Bank Millennium Spolka Akcyjna").overlap, 1);

check("stronyOverlap null gdy brak tokenow po jednej stronie",
  stronyOverlap("S.A.", "Nowak").overlap, null);

// --- v2.3: DYSKONTO SZABLONU + ZBIEZNOSC FRAGMENTU -----------------------------
// 12. Cytat doslowny nieznaleziony, pokrycie glownie frazami szablonowymi -> BLOKADA
//     (przed v2.3 wpadaloby w KALIBRACJA - boilerplate zawyzal pokrycie).
const zrodloSzablonowe =
  "Strony ustalily, ze zadna ze stron nie ponosi odpowiedzialnosci za niewykonanie zobowiazan " +
  "wskutek dzialania sily wyzszej, chyba ze umowa stanowi inaczej. Wszelkie zmiany wymagaja formy " +
  "pisemnej, z zastrzezeniem postanowien odmiennych. Dokument nie zawiera innych regul.";
check("v2.3: falszywy cytat na poduszce szablonu -> NIEZWERYFIKOWANY",
  verify({
    id: "B1", source_id: "umowa-x", claim_type: "cytat_doslowny",
    quote: "pozwana spolka nie ponosi odpowiedzialnosci, chyba ze umowa stanowi inaczej, z zastrzezeniem wyjatkow",
    source_text: zrodloSzablonowe,
  }).status, "NIEZWERYFIKOWANY");

// 13. Parafraza (TRESC) o tym samym pokryciu szablonowym -> miekko WYMAGA_OSADU (nie twarda blokada),
//     bo wszystkie terminy SA w zrodle - czlowiek osadza substancje.
const wynikB2 = verify({
  id: "B2", source_id: "umowa-x", claim_type: "parafraza",
  claim_text: "pozwana spolka nie ponosi odpowiedzialnosci, chyba ze umowa stanowi inaczej, z zastrzezeniem wyjatkow",
  source_text: zrodloSzablonowe,
});
check("v2.3: parafraza na szablonie -> WYMAGA_OSADU (miekko)", wynikB2.status, "WYMAGA_OSADU");
check("v2.3: nota parafrazy na szablonie wskazuje jezyk szablonowy",
  wynikB2.note.includes("szablonowym"), true);

// 14. Regresja: merytoryczna parafraza bez szablonu nadal WYMAGA_OSADU z pelnym pokryciem.
const wynikB3 = verify({
  id: "B3", source_id: "I CSK 50/18", claim_type: "stanowisko_sadu",
  claim_text: "klauzula waloryzacyjna w umowie kredytu jest dopuszczalna",
  source_text: "Sad uznal, ze klauzula waloryzacyjna w umowie kredytu jest dopuszczalna w swietle zasad wspolzycia.",
});
check("v2.3 regresja: parafraza merytoryczna -> WYMAGA_OSADU", wynikB3.status, "WYMAGA_OSADU");
check("v2.3 regresja: zwarty fragment -> brak uwagi o rozproszeniu",
  wynikB3.note.includes("rozproszone"), false);

// 15. Terminy obecne, ale ROZPROSZONE po dlugim dokumencie -> uwaga o niskiej zbieznosci fragmentu.
const wypelniacz = "Postepowanie toczylo sie przed sadem pierwszej instancji przez wiele miesiecy. ".repeat(6);
const zrodloRozproszone =
  "Powod zaciagnal kredyt hipoteczny w 2008 roku. " + wypelniacz +
  "Pozwany bank przedstawil harmonogram splat. " + wypelniacz +
  "Biegly odniosl sie do mechanizmu waloryzacji swiadczen pracowniczych. " + wypelniacz +
  "Sad oddalil wniosek o powolanie kolejnego bieglego, wskazujac na klauzule generalne. " + wypelniacz +
  "W odrebnym watku pojawila sie kwestia abuzywnego zachowania pelnomocnika. " + wypelniacz;
const wynikB4 = verify({
  id: "B4", source_id: "I ACa 1/20", claim_type: "stanowisko_sadu",
  claim_text: "bank stosowal abuzywne klauzule waloryzacji kredytu",
  source_text: zrodloRozproszone,
});
check("v2.3: terminy rozproszone -> WYMAGA_OSADU", wynikB4.status, "WYMAGA_OSADU");
check("v2.3: nota zawiera uwage o rozproszeniu terminow",
  wynikB4.note.includes("rozproszone"), true);

// 16. Jednostkowe: zbieznoscFragmentu wysoka dla zwartej parafrazy, niska dla rozproszenia.
check("zbieznoscFragmentu >= 0.5 dla zwartego fragmentu",
  zbieznoscFragmentu("klauzula waloryzacyjna w umowie kredytu jest dopuszczalna",
    "sad uznal, ze klauzula waloryzacyjna w umowie kredytu jest dopuszczalna w swietle zasad") >= 0.5, true);

// --- KONFORMANCJA NORMALIZACJI ------------------------------------------------
// Regula normalizacji ma JEDEN DOM: tablice prawdy w doc-intel-contract-pl.
// Ten sam plik czyta test Pythona (test_normalizacja_kontrakt.py). Do 2026-08-30
// kazda strona miala wlasna implementacje - tutejsza gubila SZESC z osmiu znakow,
// ktore polski PDF wstawia naprawde, przez co poziom FRAGMENT potrafil orzec
// "cytatu nie ma w zrodle" o cytacie, ktory tam byl.
// Sciezka wzgledem katalogu skilla, bez sciezek prywatnych. Kolejnosc kandydatow:
// 1) zmienna NORMALIZACJA_CASES (jawne wskazanie), 2) uklad plaski - skille jako
// rodzenstwo w jednym katalogu, 3) uklad huba awesome-matematic-skills-pl
// (<plugin>/skills/<skill>). Zaden nie istnieje = FAIL ponizej, nie pominiecie.
const SKILL_DIR = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const KANDYDACI = [
  process.env.NORMALIZACJA_CASES,
  join(SKILL_DIR, "..", "doc-intel-contract-pl", "contract", "normalizacja.cases.json"),
  join(SKILL_DIR, "..", "..", "..", "dokumenty", "skills", "doc-intel-contract-pl",
       "contract", "normalizacja.cases.json"),
].filter(Boolean);
const TABLICA = KANDYDACI.find((k) => existsSync(k)) || KANDYDACI[KANDYDACI.length - 1];
let tab = null;
try {
  tab = JSON.parse(readFileSync(TABLICA, "utf-8"));
} catch (e) {
  // Brak tablicy to FAIL, nie ciche pominiecie: bramka, ktora nie ma na czym
  // zadzialac, przechodzi zawsze.
  check(`tablica prawdy normalizacji czytelna (${TABLICA})`,
        `BLAD: ${e.code || e.message}`, "OK");
}
if (tab) {
  check("tablica prawdy niepusta (mianownik bramki)", tab.przypadki.length > 0, true);
  let zgodne = 0;
  const rozjazdy = [];
  for (const c of tab.przypadki) {
    const got = normalize(c.wejscie);
    if (got === c.oczekiwane) zgodne++;
    else rozjazdy.push(`${c.nazwa}: got=${JSON.stringify(got)} want=${JSON.stringify(c.oczekiwane)}`);
  }
  check(`normalizacja zgodna z tablica prawdy v${tab._wersja} (${zgodne}/${tab.przypadki.length})`,
        zgodne, tab.przypadki.length);
  for (const r of rozjazdy) console.log(`      ROZJAZD ${r}`);
}

// --- ZAKRES W ORYGINALE (v2.5) --------------------------------------------------
// Do v2.4 `offset` byl liczony w tekscie ZNORMALIZOWANYM: po wiodacych spacjach,
// podwojnych odstepach czy przeniesieniu wyrazu wskazywal INNE miejsce niz cytat.
// Kazdy test sprawdza wycinek ORYGINALU pod zwroconym zakresem, nie sam fakt zwrotu.
const ZRODLO_Z = "WYROK\n\n   Sąd  Najwyższy   zważył,  że  umowa jest nie-\nważna w całości.  Dalej: „klauzula waloryzacyjna” jest abuzywna.";
const rz = verify({ id: "Z1", source_id: "t", quote: "umowa jest nieważna w całości", source_text: ZRODLO_Z });
check("zakres: ZWERYFIKOWANY", rz.status, "ZWERYFIKOWANY");
check("zakres: wycinek oryginalu == cytat po normalizacji",
  normalize(ZRODLO_Z.slice(rz.zakres.start, rz.zakres.end)), normalize("umowa jest nieważna w całości"));
check("zakres: offset wskazuje poczatek cytatu w ORYGINALE (nie w tekscie znormalizowanym)",
  ZRODLO_Z.slice(rz.offset, rz.offset + 5), "umowa");
check("zakres: fragment_zrodla niesie przeniesienie wyrazu z oryginalu",
  rz.fragment_zrodla, "umowa jest nie-\nważna w całości");

// v3: luka wycinajaca ZWYKLE slowa ("w całości") - dwa segmenty, kazdy co najmniej 3 slowa.
const rg = verify({ id: "Z2", source_id: "t", quote: "umowa jest nieważna [...] Dalej: „klauzula waloryzacyjna” jest abuzywna", source_text: ZRODLO_Z });
check("zakres: cytat z luka [...] -> dwa segmenty", rg.segmenty && rg.segmenty.length, 2);
check("zakres: drugi segment trafia w oryginal",
  normalize(ZRODLO_Z.slice(rg.segmenty[1].start, rg.segmenty[1].end)), normalize("Dalej: „klauzula waloryzacyjna” jest abuzywna"));
// Do v2.6 ten cytat przechodzil jako ZWERYFIKOWANY, choc luka wycinala "umowa jest nieważna w całości".
const rgs = verify({ id: "Z2b", source_id: "t", quote: "Sąd Najwyższy zważył [...] jest abuzywna", source_text: ZRODLO_Z });
check("v3: luka z segmentem krotszym niz 3 slowa -> NIEZWERYFIKOWANY (nie da sie sprawdzic, co wycieto)", rgs.status, "NIEZWERYFIKOWANY");
check("v3: ... z kodem powodu opuszczenie_niesprawdzalne", rgs.powod_kod, "opuszczenie_niesprawdzalne");

const NFD = "Orzeczenie: Sąd uchylił wyrok.";
const rn = verify({ id: "Z3", source_id: "t", quote: "Sąd uchylił", source_text: NFD });
check("zakres: zrodlo w NFD - zakres obejmuje znak laczacy",
  NFD.slice(rn.zakres.start, rn.zakres.end), "Sąd uchylił");

// v3: inna forma slowa ("abuzywne" zamiast "abuzywna") to cytat NIEDOSLOWNY - twarda odmowa z nazwana para,
// nie "drobne roznice". Fragment zrodla nadal wskazuje wlasciwe miejsce.
const rp = verify({ id: "Z4", source_id: "t", quote: "klauzula waloryzacyjna jest abuzywne", source_text: ZRODLO_Z });
check("v3: inna forma slowa -> NIEZWERYFIKOWANY", rp.status, "NIEZWERYFIKOWANY");
check("v3: ... kod powodu zmieniona_tresc i nazwana para", [rp.powod_kod, rp.roznice[0].cytat, rp.roznice[0].zrodlo].join("|"), "zmieniona_tresc|abuzywne|abuzywna");
check("v3: ... fragment zrodla wskazuje wlasciwe miejsce", /klauzula\s+waloryzacyjna/.test(rp.fragment_zrodla || ""), true);
// Dopasowanie znakowe zostaje dla cytatow krotszych niz 3 slowa.
const rk = verify({ id: "Z4b", source_id: "t", quote: "klauzula waloryzacyjnaa", source_text: ZRODLO_Z });
check("zakres: cytat 2 slowa z literowka -> ZMODYFIKOWANY (dopasowanie znakowe)", [rk.status, rk.powod_kod].join("|"), "ZMODYFIKOWANY|znaki");
check("zakres: przyblizone - fragment wskazuje wlasciwe miejsce", /klauzula\s+waloryzacyjna/.test((rk.fragmenty_zrodla || [])[0] || ""), true);

const rb = verify({ id: "Z5", source_id: "t", quote: "zmyslony cytat o czyms", source_text: "Sad zwazyl, ze umowa jest wazna." });
check("blokada: segmenty w detail.segmenty (nie klucze '0','1')",
  Array.isArray(rb.detail.segmenty) && !("0" in rb.detail), true);

// Niezmiennik mapy na calej tablicy prawdy: pelny zakres mapy odtwarza caly tekst znormalizowany.
if (tab) {
  let zgodneMapy = 0;
  for (const c of tab.przypadki) {
    const m = normalizeWithMap(c.wejscie);
    const ok = m.start.length === m.norm.length && m.end.length === m.norm.length &&
      (m.norm.length === 0 || normalize(c.wejscie.slice(m.start[0], m.end[m.norm.length - 1])) === m.norm);
    if (ok) zgodneMapy++;
  }
  check(`mapa pozycji spojna na tablicy prawdy (${zgodneMapy}/${tab.przypadki.length})`,
        zgodneMapy, tab.przypadki.length);
}

// --- POROWNANIE NA SLOWACH (v3.0) ------------------------------------------------
// Do v2.6 zmiana "14 dni" -> "15 dni" i dopisane "nie" dawaly ZMODYFIKOWANY ("drobne roznice"), blokada=false,
// kod 0 - ten sam status co cudzyslow wokol cytatu. Teksty ponizej sa zmyslone (nie z realnych spraw ani ustaw).
{
  const { porownajSlowa, twardy, istotnyWOpuszczeniu } = await import("./porownanie-slow.mjs");
  const S = "Art. 1. Kto z winy swej wyrządził drugiemu szkodę, obowiązany jest do jej naprawienia w terminie 14 dni od dnia " +
    "wezwania. Sąd może, na wniosek strony lub z urzędu, zawiesić postępowanie, jeżeli rozstrzygnięcie zależy od wyniku " +
    "innego postępowania cywilnego albo karnego.4) Koszty takiego postępowania ponosi w całości Skarb Państwa. " +
    "Pracodawca nie może wypowiedzieć umowy o pracę w okresie ochrony pracownika przed zwolnieniem.";
  const v = (quote, source_text = S) => verify({ id: "W", source_id: "t", quote, source_text });
  const Q1 = "obowiązany jest do jej naprawienia w terminie 14 dni od dnia wezwania";

  check("v3: cytat doslowny -> ZWERYFIKOWANY", v(Q1).status, "ZWERYFIKOWANY");
  const liczba = v(Q1.replace("14 dni", "15 dni"));
  check("v3: zmieniona liczba -> NIEZWERYFIKOWANY", liczba.status, "NIEZWERYFIKOWANY");
  check("v3: ... para '15' zamiast '14', roznica twarda",
    JSON.stringify(liczba.roznice.map((r) => [r.cytat, r.zrodlo, r.twarda])), JSON.stringify([["15", "14", true]]));
  check("v3: ... nota nazywa roznice", /"15" zamiast "14"/.test(liczba.note), true);
  const nie = v("Sąd nie może, na wniosek strony lub z urzędu, zawiesić postępowanie");
  check("v3: dopisane 'nie' -> NIEZWERYFIKOWANY z para ('nie' / brak)",
    [nie.status, nie.roznice && nie.roznice[0].cytat, nie.roznice && nie.roznice[0].zrodlo].join("|"), "NIEZWERYFIKOWANY|nie|");
  check("v3: 'lub' -> 'i' -> NIEZWERYFIKOWANY", v("na wniosek strony i z urzędu, zawiesić postępowanie").status, "NIEZWERYFIKOWANY");
  check("v3: slowo zamienione na inne (nie twarde) -> NIEZWERYFIKOWANY",
    v("wyrządził innemu szkodę, obowiązany jest do jej naprawienia").powod_kod, "zmieniona_tresc");
  check("v3: kropka przesunieta o slowo ('...karnego koszty. takiego') -> NIEZWERYFIKOWANY",
    v("postępowania cywilnego albo karnego Koszty. Takiego postępowania ponosi w całości Skarb Państwa").status, "NIEZWERYFIKOWANY");

  // typografia i interpunkcja brzegowa nie sa trescia
  check("v3: cudzyslow wokol cytatu, twarda spacja, miekki dywiz, podwojne spacje -> ZWERYFIKOWANY",
    v("„obowiązany  jest do jej napra\u00adwienia w\u00a0terminie 14 dni od dnia wezwania”").status, "ZWERYFIKOWANY");
  check("v3: cytat bez przecinkow -> ZWERYFIKOWANY", v("Sąd może na wniosek strony lub z urzędu zawiesić postępowanie").status, "ZWERYFIKOWANY");
  check("v3: fragment urwany w srodku zdania z dopisana kropka -> ZWERYFIKOWANY", v("obowiązany jest do jej naprawienia.").status, "ZWERYFIKOWANY");
  const zak = v("  obowiązany jest do jej naprawienia w\u00a0terminie 14 dni");
  check("v3: zakres wskazuje cytat w ORYGINALE", S.slice(zak.zakres.start, zak.zakres.end), "obowiązany jest do jej naprawienia w terminie 14 dni");

  // opuszczenia
  const op = v("obowiązany jest do jej naprawienia (...) terminie 14 dni od dnia wezwania");
  check("v3: '(...)' wycinajace zwykle slowo... 'w' -> ZWERYFIKOWANY z wycietym tekstem", [op.status, JSON.stringify(op.opuszczone)].join("|"), 'ZWERYFIKOWANY|["w"]');
  check("v3: ... nota pokazuje, co wycieto", /pomija 1 slow/.test(op.note || ""), true);
  const opn = v("Pracodawca [...] wypowiedzieć umowy o pracę w okresie ochrony");
  check("v3: luka przy segmencie jednego slowa -> NIEZWERYFIKOWANY", opn.status, "NIEZWERYFIKOWANY");
  const opi = v("Koszty takiego postępowania ponosi w całości Skarb Państwa. Pracodawca (...) wypowiedzieć umowy o pracę w okresie ochrony");
  check("v3: luka wycinajaca 'nie może' -> NIEZWERYFIKOWANY, kod opuszczenie_istotne, slowo nazwane",
    [opi.status, opi.powod_kod, (opi.opuszczone_istotne || []).join(",")].join("|"), "NIEZWERYFIKOWANY|opuszczenie_istotne|może,nie");
  check("v3: ... wyciety tekst w wyniku", JSON.stringify(opi.opuszczone), '["nie może"]');
  const dlugi = "Strona wnosi odwołanie do sądu właściwego. " + Array.from({ length: 45 }, (_, i) => `wyraz${i}`).join(" ") + ". Organ rozpatruje je niezwłocznie po otrzymaniu.";
  check("v3: segmenty ponad 40 slow od siebie -> opuszczenie_za_szerokie",
    v("Strona wnosi odwołanie do sądu [...] Organ rozpatruje je niezwłocznie", dlugi).powod_kod, "opuszczenie_za_szerokie");
  const dwa = "Sąd wydaje postanowienie na posiedzeniu niejawnym bez udziału stron. " + Array.from({ length: 45 }, (_, i) => `wyraz${i}`).join(" ") +
    ". Sąd wydaje postanowienie na posiedzeniu jawnym po wysłuchaniu wszystkich stron.";
  check("v3: fraza powtorzona w zrodle - liczy sie wystapienie blizsze reszcie cytatu",
    JSON.stringify(v("Sąd wydaje postanowienie (...) jawnym po wysłuchaniu wszystkich stron", dwa).opuszczone), '["na posiedzeniu"]');

  // diakrytyki i odnosniki redakcyjne
  const dia = v("obowiazany jest do jej naprawienia w terminie 14 dni");
  check("v3: roznica wylacznie w znakach diakrytycznych -> ZMODYFIKOWANY/diakrytyki (miekko)", [dia.status, dia.powod_kod].join("|"), "ZMODYFIKOWANY|diakrytyki");
  check("v3: diakrytyki + zmieniona liczba -> NIEZWERYFIKOWANY", v("obowiazany jest do jej naprawienia w terminie 15 dni").status, "NIEZWERYFIKOWANY");
  const odn = v("innego postępowania cywilnego albo karnego. Koszty takiego postępowania ponosi w całości Skarb Państwa");
  check("v3: odnosnik redakcyjny tylko w zrodle ('karnego.4)') nie jest roznica", [odn.status, JSON.stringify(odn.odnosniki_pominiete)].join("|"), 'ZWERYFIKOWANY|["4"]');
  check("v3: cytat skopiowany RAZEM z odnosnikiem -> ZWERYFIKOWANY",
    v("postępowania cywilnego albo karnego.4) Koszty takiego postępowania ponosi w całości").status, "ZWERYFIKOWANY");
  check("v3: INNY numer odnosnika w cytacie -> NIEZWERYFIKOWANY",
    v("postępowania cywilnego albo karnego.5) Koszty takiego postępowania ponosi w całości").status, "NIEZWERYFIKOWANY");
  check("v3: punkt wyliczenia po spacji to tresc, nie odnosnik",
    v("gdy: 6) oskarżony zmarł przed wydaniem", "Postępowanie umarza się, gdy: 5) oskarżony zmarł przed wydaniem wyroku.").status, "NIEZWERYFIKOWANY");

  const przed = v("zależy od wyniku innego postępowania cywilnego albo karnego");
  check("v3: odnosnik stojacy ZA cytatem nie jest przypisywany cytatowi", [przed.status, przed.odnosniki_pominiete === undefined].join("|"), "ZWERYFIKOWANY|true");
  const przyklejony = v("ponosi w całości Skarb Państwa", "Koszty takiego postępowania ponosi w całości Skarb Państwa4) oraz właściwa gmina.");
  check("v3: odnosnik przyklejony do OSTATNIEGO slowa cytatu, ale stojacy za nim, nie jest przypisywany cytatowi",
    [przyklejony.status, przyklejony.odnosniki_pominiete === undefined, przyklejony.fragment_zrodla].join("|"), "ZWERYFIKOWANY|true|ponosi w całości Skarb Państwa");
  const daleki = v("Kto z premedytacją wyrządził komukolwiek krzywdę, zobowiązany będzie do jej wyrównania w terminie 14 dni");
  check("v3: cytat podobny tylko z grubsza (5 innych slow na 15) to NIE 'zmieniona tresc' z lista par, tylko brak cytatu",
    [daleki.status === "ZWERYFIKOWANY", daleki.powod_kod === "zmieniona_tresc"].join("|"), "false|false");

  // lamanie wiersza i sklejenia przy kopiowaniu z PDF
  check("v3: wyraz polamany w cytacie ('napra- wienia') albo sklejony ('jejnaprawienia') to nie zmiana tresci",
    [v("obowiązany jest do jej napra- wienia w terminie 14 dni").status, v("obowiązany jest do jejnaprawienia w terminie 14 dni").status].join("|"),
    "ZWERYFIKOWANY|ZWERYFIKOWANY");
  check("v3: ... ale polamany wyraz obok zmienionej liczby nadal blokuje",
    v("obowiązany jest do jej napra- wienia w terminie 15 dni").powod_kod, "zmieniona_tresc");
  // Trzy slowa z 9 inne o jeden znak: slowami to juz nie ten cytat (prog 2), a znakowo roznica ok. 5% - do v2.6
  // i przez furtke w pierwszej wersji v3 wychodzilo "drobne roznice" (ZMODYFIKOWANY, bez blokady).
  const rf = v("wyrządzył drugiemu szkode, obowiązani jest do jei naprawienia w termine");
  check("v3: cytat >= 3 slow, ktorego slowa nie pasuja, NIE wraca do dopasowania znakowego ('drobne roznice')",
    [rf.status === "ZMODYFIKOWANY", rf.status === "ZWERYFIKOWANY"].join("|"), "false|false");

  // odbior krytyka 2026-11-18: cztery furtki
  const L = "Sąd stosuje art. 56 ust. 2 ustawy i zasądza kwotę 10 000 zł tytułem zwrotu kosztów postępowania.";
  check("v3: podzial cyfr jest trescia - 'art. 5 6' przy 'art. 56' i '100 00 zł' przy '10 000 zł' blokuja",
    [v("Sąd stosuje art. 5 6 ust. 2 ustawy", L).status, v("zasądza kwotę 100 00 zł tytułem zwrotu kosztów", L).status].join("|"),
    "NIEZWERYFIKOWANY|NIEZWERYFIKOWANY");
  check("v3: ... a poprawny zapis tysiecy sklejony albo rozdzielony ('10000' / '10 000') nie jest roznica",
    [v("zasądza kwotę 10000 zł tytułem zwrotu kosztów", L).status, v("zasądza kwotę 10 000 zł tytułem zwrotu", L).status].join("|"),
    "ZWERYFIKOWANY|ZWERYFIKOWANY");
  const kr = v("art. 57", L);
  check("v3: cytat 2 slowa z INNA liczba ('art. 57' przy 'art. 56') nie jest 'drobna roznica'",
    [kr.status === "ZMODYFIKOWANY", kr.status === "ZWERYFIKOWANY", v("art. 56", L).status].join("|"), "false|false|ZWERYFIKOWANY");
  const bezpl = v("obowiazany jest do jej naprawienia w terminie 14 dni od dnia wezwania. Sad moze, na wniosek strony lub z urzedu, zawiesic postepowanie");
  check("v3: cytat przepisany bez polskich znakow (6 slow z 20) -> ZMODYFIKOWANY/diakrytyki, nie 'halucynacja'",
    [bezpl.status, bezpl.powod_kod, bezpl.roznice && bezpl.roznice.length >= 3 && bezpl.roznice.every((r) => r.tylko_diakrytyki)].join("|"), "ZMODYFIKOWANY|diakrytyki|true");
  check("v3: ... ale brak polskich znakow nie zaslania zmienionej liczby",
    v("obowiazany jest do jej naprawienia w terminie 15 dni od dnia wezwania. Sad moze, na wniosek strony").status, "NIEZWERYFIKOWANY");
  const wt = v("Sąd może, na wniosek strony [powoda] lub z urzędu, zawiesić postępowanie");
  check("v3: wtracenie cytujacego w nawiasie kwadratowym jest pomijane i nazwane",
    [wt.status, JSON.stringify(wt.wtracenia), /wtracenie/.test(wt.note || "")].join("|"), 'ZWERYFIKOWANY|["powoda"]|true');
  check("v3: ... ale wtracenie nie zaslania zmienionego slowa obok",
    v("Sąd nie może, na wniosek strony [powoda] lub z urzędu, zawiesić postępowanie").status, "NIEZWERYFIKOWANY");
  const I = "Odsetki nie mogą przekraczać stopy określonej w § 2[1] oraz w art. 359[2] ustawy. Dziennik Ustaw - 45 -\nPoz. 1342 dalszy tekst.";
  const wi = v("Sąd [nie] może, na wniosek strony lub z urzędu, zawiesić postępowanie");
  check("v3: wtracenie ze slowem zmieniajacym sens ('[nie]', '[bez]', '[lub pozwanego]') blokuje",
    [wi.status, wi.powod_kod, (wi.wtracenia_istotne || []).join(","),
     v("Sąd może, na wniosek strony [lub pozwanego] lub z urzędu, zawiesić postępowanie").powod_kod,
     v("ponosi [bez wyjątku] w całości Skarb Państwa. Pracodawca nie może wypowiedzieć").powod_kod].join("|"),
    "NIEZWERYFIKOWANY|wtracenie_istotne|nie|wtracenie_istotne|wtracenie_istotne");
  const kt = v("strony i", "Sąd może, na wniosek strony lub z urzędu, zawiesić postępowanie.");
  check("v3: cytat 2 slowa ze zmienionym spojnikiem ('strony i' przy 'strony lub') blokuje, a literowka w zwyklym slowie nie",
    [kt.status, kt.powod_kod, v("zawiesić postępowanei").status].join("|"), "NIEZWERYFIKOWANY|krotki_cytat_niezgodny|ZMODYFIKOWANY");
  check("v3: krotki cytat trafia tylko na granicach slow ('art. 5' nie pasuje do 'art. 56', 'art. 56' pasuje)",
    [v("art. 5", L).status === "ZWERYFIKOWANY", v("art. 56", L).status].join("|"), "false|ZWERYFIKOWANY");
  check("v3: '[1]' przy numerze jednostki to indeks, nie wtracenie - wierny cytat przechodzi, zmieniony indeks blokuje",
    [v("stopy określonej w § 2[1] oraz w art. 359[2] ustawy", I).status, v("stopy określonej w § 2[3] oraz w art. 359[2] ustawy", I).status,
     v("stopy określonej w § 2 oraz w art. 359[2] ustawy", I).status].join("|"), "ZWERYFIKOWANY|NIEZWERYFIKOWANY|NIEZWERYFIKOWANY");
  check("v3: liczba sklejona ze slowem przez lamanie wiersza ('45 poz' / '45poz') nie jest roznica, a inna liczba jest",
    [v("art. 359[2] ustawy. Dziennik Ustaw - 45 - Poz. 1342 dalszy tekst", I).status, v("art. 359[2] ustawy. Dziennik Ustaw - 46 - Poz. 1342 dalszy tekst", I).status].join("|"),
    "ZWERYFIKOWANY|NIEZWERYFIKOWANY");
  check("v3: '[...]' to nadal opuszczenie, nie wtracenie",
    v("obowiązany jest do jej naprawienia [...] terminie 14 dni od dnia wezwania").opuszczone !== undefined, true);

  // liczby, znaki, slowniki
  const P = "Opłata wynosi 2,5 % podstawy wymiaru, nie mniej jednak niż 50 % kwoty minimalnej, zgodnie z art. 5 § 1² ustawy.";
  check("v3: '2,5' to jedno slowo ('2 5' i '25' sa roznica)", [v("Opłata wynosi 2 5 % podstawy wymiaru", P).status, v("Opłata wynosi 25 % podstawy wymiaru", P).status].join("|"), "NIEZWERYFIKOWANY|NIEZWERYFIKOWANY");
  check("v3: zgubiony '%' -> NIEZWERYFIKOWANY", v("nie mniej jednak niż 50 kwoty minimalnej", P).status, "NIEZWERYFIKOWANY");
  check("v3: indeks gorny i '§' sa trescia", [v("zgodnie z art. 5 § 1 ustawy", P).status, v("zgodnie z art. 5 1² ustawy", P).status, v("zgodnie z art. 5 § 1² ustawy", P).status].join("|"),
    "NIEZWERYFIKOWANY|NIEZWERYFIKOWANY|ZWERYFIKOWANY");
  check("v3: antonim spoza slownika ('mniej' -> 'więcej') -> NIEZWERYFIKOWANY", v("nie więcej jednak niż 50 % kwoty minimalnej", P).status, "NIEZWERYFIKOWANY");
  check("v3: slowniki - 'pierwszeństwo' to nie liczebnik, 'niejawny' i 'bezskuteczna' sa istotne w wycieciu, 'niego' nie",
    [twardy("pierwszeństwo"), twardy("pierwszej"), istotnyWOpuszczeniu("niejawny"), istotnyWOpuszczeniu("bezskuteczna"), istotnyWOpuszczeniu("niego"), istotnyWOpuszczeniu("przed")].join(","),
    "false,true,true,true,false,true");
  check("v3: '%', promil i '§' sa twarde (roznica na nich to zmiana liczby albo jednostki)", [twardy("%"), twardy("‰"), twardy("§"), twardy("ustawy")].join(","), "true,true,true,false");
  const proc = v("nie mniej jednak niż 50 (...) kwoty minimalnej, zgodnie z art. 5", P);
  check("v3: wyciety '%' -> opuszczenie_istotne", [proc.powod_kod, (proc.opuszczone_istotne || []).join(",")].join("|"), "opuszczenie_istotne|%");

  // czas przy wielu opuszczeniach (bylo wykladniczo)
  const powt = Array.from({ length: 60 }, () => "Strona wnosi odwołanie do sądu właściwego miejscowo.").join(" ");
  const t0 = Date.now();
  const rt = porownajSlowa(normalize(Array.from({ length: 8 }, () => "strona wnosi odwołanie do sądu").join(" (...) ")), normalize(powt));
  check("v3: fraza x60 i 8 segmentow - wynik ponizej 5 s", Date.now() - t0 < 5000 && /OPUSZCZENIE|DOKLADNY/.test(rt.stan), true);

  // CLI: zmieniona tresc MUSI dac blokade i kod != 0 (do v2.6: blokada=false, kod 0)
  const { spawnSync } = await import("node:child_process");
  const { mkdtempSync, writeFileSync, rmSync } = await import("node:fs");
  const { tmpdir } = await import("node:os");
  const SKRYPT = join(dirname(fileURLToPath(import.meta.url)), "ground-citations.mjs");
  const tmp = mkdtempSync(join(tmpdir(), "grounding-slowa-"));
  const plik = join(tmp, "zadanie.json");
  writeFileSync(plik, JSON.stringify({ items: [{ id: "A", source_id: "t", quote: Q1.replace("14 dni", "15 dni"), source_text: S }] }));
  const r = spawnSync(process.execPath, [SKRYPT, plik], { encoding: "utf8" });
  let wynik = {};
  try { wynik = JSON.parse(r.stdout); } catch { /* zly JSON = FAIL ponizej */ }
  check("v3 CLI: zmieniona liczba -> blokada=true, kod != 0, licznik zmieniona_tresc",
    [wynik.blokada, r.status !== 0, wynik.summary && wynik.summary.zmieniona_tresc].join("|"), "true|true|1");
  writeFileSync(plik, JSON.stringify({ items: [{ id: "B", source_id: "t", quote: "„" + Q1 + "”", source_text: S }] }));
  const r2 = spawnSync(process.execPath, [SKRYPT, plik], { encoding: "utf8" });
  check("v3 CLI: wierny cytat w cudzyslowie -> blokada=false, kod 0", [JSON.parse(r2.stdout).blokada, r2.status].join("|"), "false|0");
  rmSync(tmp, { recursive: true, force: true });
}

// --- PUSTA LISTA = BLOKADA (v2.6) ----------------------------------------------
// Do v2.5 zadanie bez cytatow (items: [] albo brak pola) dawalo total=0, blokada=false
// i exit 0: bramka, ktora nie ma na czym zadzialac, przechodzila na zielono.
// Test woła CLI tak jak uzytkownik, bo werdykt i kod wyjscia liczy main(), nie verify().
{
  const { spawnSync } = await import("node:child_process");
  const { mkdtempSync, writeFileSync, rmSync } = await import("node:fs");
  const { tmpdir } = await import("node:os");
  const SKRYPT = join(dirname(fileURLToPath(import.meta.url)), "ground-citations.mjs");
  const tmp = mkdtempSync(join(tmpdir(), "grounding-pusta-"));
  for (const [nazwa, zadanie] of [["items: []", { items: [] }], ["brak pola items", {}]]) {
    const plik = join(tmp, "zadanie.json");
    writeFileSync(plik, JSON.stringify(zadanie));
    const r = spawnSync(process.execPath, [SKRYPT, plik], { encoding: "utf8" });
    let wynik = {};
    try { wynik = JSON.parse(r.stdout); } catch { /* zly JSON = FAIL ponizej */ }
    check(`pusta lista (${nazwa}) -> blokada=true`, wynik.blokada, true);
    check(`pusta lista (${nazwa}) -> exit != 0`, r.status !== 0, true);
  }
  rmSync(tmp, { recursive: true, force: true });
}

console.log(`\n${pass}/${pass + fail} PASS`);
process.exit(fail ? 1 : 0);
