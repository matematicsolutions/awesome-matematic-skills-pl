#!/usr/bin/env node
// Wachta legislacyjna: dla kazdej ustawy z seuranta/ustawy.json pyta ISAP
// (api.sejm.gov.pl/eli) o status i tytul. Ustawa uchylona / NOT_IN_FORCE
// albo zmieniona nazwa = BLAD (exit 1) - skille cytujace ja wymagaja
// przegladu. Niedostepnosc API = OSTRZEZENIE (nie wywalaj CI na chwilowym
// 5xx). Uruchamiane w CI co miesiac + recznie: node scripts/wachta-legislacyjna.mjs
//
// Adaptacja saadosvahti z akunikkola/claude-for-legal-finland (MIT);
// zamiast skrobania <title> z Finlexu mamy strukturalne JSON ELI z ISAP.

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const reg = JSON.parse(readFileSync(join(root, "seuranta/ustawy.json"), "utf8"));

const norm = (s) => (s ?? "").toLowerCase().normalize("NFC");

async function fetchAct(eli) {
  try {
    const r = await fetch(`https://api.sejm.gov.pl/eli/acts/${eli}`, {
      redirect: "follow",
      signal: AbortSignal.timeout(20000),
      headers: { accept: "application/json" },
    });
    if (!r.ok) return null;
    return await r.json();
  } catch {
    return null;
  }
}

let bledy = 0, ostrzezenia = 0, ok = 0;
console.log(`wachta legislacyjna - ${reg.ustawy.length} ustaw (ISAP ELI)\n`);

for (const u of reg.ustawy) {
  const akt = await fetchAct(u.eli);
  if (!akt || !akt.title) {
    ostrzezenia++;
    console.log(`  [!]  ${u.skrot} (${u.eli}) - ISAP nie odpowiada, sprawdz recznie`);
    await new Promise((r) => setTimeout(r, 300));
    continue;
  }
  const problemy = [];
  if (akt.inForce !== "IN_FORCE") {
    problemy.push(`inForce=${akt.inForce}${akt.repealDate ? `, uchylona ${akt.repealDate}` : ""}`);
  }
  if (norm(akt.status).includes("uchylony")) {
    problemy.push(`status="${akt.status}"`);
  }
  if (!norm(akt.title).includes(norm(u.nazwa))) {
    problemy.push(`tytul w ISAP: "${akt.title}" nie zawiera oczekiwanego "${u.nazwa}" - nazwa mogla sie zmienic`);
  }
  if (problemy.length) {
    bledy++;
    console.log(`  [X]  ${u.skrot} (${u.eli}) - ${problemy.join("; ")}`);
    console.log(`       -> przejrzyj skille: ${u.uzycie}`);
  } else {
    ok++;
  }
  await new Promise((r) => setTimeout(r, 300));
}

console.log(`\n${ok} obowiazuje - ${ostrzezenia} nie sprawdzono - ${bledy} wymaga przegladu`);
if (bledy > 0) {
  console.log("\nUstawa uchylona lub przemianowana: zaktualizuj skille z kolumny 'uzycie',");
  console.log("potem popraw wpis w seuranta/ustawy.json (nowy ELI/nazwa).");
  process.exit(1);
}
