#!/usr/bin/env node
// Test-harness silnika citation-grounding-pl (zero-dep). Uruchom: node test-grounding.mjs
// Rubryka PASS/FAIL per przypadek; exit 1 gdy ktorykolwiek FAIL (bramka CI).
// Pokrywa nowy guard STRONY ("prawdziwy cytat, falszywa teza") + regresje rdzenia v2.

import { verify, stronyOverlap, partyTokens } from "./ground-citations.mjs";

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

console.log(`\n${pass}/${pass + fail} PASS`);
process.exit(fail ? 1 : 0);
