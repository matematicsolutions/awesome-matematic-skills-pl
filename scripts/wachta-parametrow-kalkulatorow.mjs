#!/usr/bin/env node
// Wachta parametrow kalkulatorow procesowych: dla kazdego aktu bazowego
// z dokumenty/skills/kalkulatory-procesowe-pl/parametry-baseline.json pyta
// ISAP (api.sejm.gov.pl/eli) o status ORAZ o liste aktow zmieniajacych.
// Akt uchylony / NOT_IN_FORCE / przemianowany = BLAD. Zmiana, ktora weszla
// w zycie PO dacie baseline = BLAD (fallbacki w references/*.md moga byc
// nieaktualne - przejrzyj wskazany plik i podnies baseline po weryfikacji).
// Zmiana opublikowana z przyszla data wejscia w zycie = OSTRZEZENIE.
// Niedostepnosc API = OSTRZEZENIE (nie wywalaj CI na chwilowym 5xx).
// Uruchamiane w CI razem z wachta-legislacyjna + recznie:
// node scripts/wachta-parametrow-kalkulatorow.mjs
//
// Uzupelnia wachta-legislacyjna.mjs: tamta pilnuje ISTNIENIA ustaw calego
// huba, ta pilnuje AKTUALNOSCI parametrow liczbowych czterech kalkulatorow
// (widelki oplat, marze odsetkowe, progi WPS) wrazliwych na kazda nowele.

import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const reg = JSON.parse(readFileSync(
  join(root, "dokumenty/skills/kalkulatory-procesowe-pl/parametry-baseline.json"),
  "utf8",
));

const baseline = reg.baseline;
const dzis = new Date().toISOString().slice(0, 10);
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

// ISAP zwraca zmiany pod kluczem "Akty zmieniające" (z polskim znakiem) -
// dopasowujemy po prefiksie, zeby nie zalezec od dokladnej pisowni klucza.
function aktyZmieniajace(akt) {
  const refs = akt.references ?? {};
  for (const key of Object.keys(refs)) {
    if (norm(key).startsWith("akty zmieniaj")) return refs[key] ?? [];
  }
  return [];
}

let bledy = 0, ostrzezenia = 0, ok = 0;
console.log(`wachta parametrow kalkulatorow - baseline ${baseline}, ${reg.akty.length} aktow (ISAP ELI)\n`);

for (const u of reg.akty) {
  const akt = await fetchAct(u.eli);
  if (!akt || !akt.title) {
    ostrzezenia++;
    console.log(`  [!]  ${u.skrot} (${u.eli}) - ISAP nie odpowiada, sprawdz recznie`);
    await new Promise((r) => setTimeout(r, 300));
    continue;
  }

  const problemy = [];
  if (akt.inForce !== "IN_FORCE") {
    problemy.push(`inForce=${akt.inForce}`);
  }
  if (norm(akt.status).includes("uchylony")) {
    problemy.push(`status="${akt.status}"`);
  }
  if (!norm(akt.title).includes(norm(u.nazwa))) {
    problemy.push(`tytul w ISAP: "${akt.title}" nie zawiera oczekiwanego "${u.nazwa}"`);
  }

  const zmiany = aktyZmieniajace(akt).filter((z) => z?.date && z.date > baseline);
  const weszly = zmiany.filter((z) => z.date <= dzis);
  const nadchodza = zmiany.filter((z) => z.date > dzis);

  if (weszly.length) {
    problemy.push(
      `zmiany po baseline: ${weszly.map((z) => `${z.id} (od ${z.date})`).join(", ")}`,
    );
  }
  if (nadchodza.length) {
    ostrzezenia++;
    console.log(
      `  [!]  ${u.skrot} - nadchodzace zmiany: ${nadchodza.map((z) => `${z.id} (od ${z.date})`).join(", ")}`,
    );
  }

  if (problemy.length) {
    bledy++;
    console.log(`  [X]  ${u.skrot} (${u.eli}) - ${problemy.join("; ")}`);
    console.log(`       -> parametry: ${u.parametry}`);
    console.log(`       -> przejrzyj: ${u.plik}, potem podnies baseline w parametry-baseline.json`);
  } else {
    ok++;
  }
  await new Promise((r) => setTimeout(r, 300));
}

console.log(`\n${ok} aktualne - ${ostrzezenia} ostrzezen - ${bledy} wymaga przegladu`);
if (bledy > 0) {
  console.log("\nAkt bazowy kalkulatora uchylony albo zmieniony po dacie baseline:");
  console.log("zweryfikuj fallbacki we wskazanych references/*.md (daty weryfikacji,");
  console.log("kwoty, marze), zaktualizuj tabele i dopiero wtedy podnies baseline.");
  process.exit(1);
}
