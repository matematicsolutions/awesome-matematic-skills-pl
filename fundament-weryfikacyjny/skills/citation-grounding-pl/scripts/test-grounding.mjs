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

const rg = verify({ id: "Z2", source_id: "t", quote: "Sąd Najwyższy zważył [...] jest abuzywna", source_text: ZRODLO_Z });
check("zakres: cytat z luka [...] -> dwa segmenty", rg.segmenty && rg.segmenty.length, 2);
check("zakres: drugi segment trafia w oryginal",
  ZRODLO_Z.slice(rg.segmenty[1].start, rg.segmenty[1].end), "jest abuzywna");

const NFD = "Orzeczenie: Sąd uchylił wyrok.";
const rn = verify({ id: "Z3", source_id: "t", quote: "Sąd uchylił", source_text: NFD });
check("zakres: zrodlo w NFD - zakres obejmuje znak laczacy",
  NFD.slice(rn.zakres.start, rn.zakres.end), "Sąd uchylił");

const rp = verify({ id: "Z4", source_id: "t", quote: "klauzula waloryzacyjna jest abuzywne", source_text: ZRODLO_Z });
check("zakres: przyblizone -> ZMODYFIKOWANY z fragmentem zrodla", rp.status, "ZMODYFIKOWANY");
check("zakres: przyblizone - fragment wskazuje wlasciwe miejsce",
  /klauzula waloryzacyjna/.test(rp.fragmenty_zrodla[0] || ""), true);

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

console.log(`\n${pass}/${pass + fail} PASS`);
process.exit(fail ? 1 : 0);
