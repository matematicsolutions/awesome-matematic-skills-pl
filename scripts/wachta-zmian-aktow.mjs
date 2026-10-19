#!/usr/bin/env node
// Wachta zmian aktow zrodlowych: dla kazdego aktu z seuranta/akty-zrodlowe.json pyta,
// czy pojawil sie NOWY akt zmieniajacy - akty UE w Cellar (SPARQL Urzedu Publikacji,
// cdm:resource_legal_amends_resource_legal), ustawy PL w ISAP (api.sejm.gov.pl/eli,
// "Akty zmieniajace" po dacie baseline). Nowa zmiana = BLAD (exit 1) z lista skilli,
// ktore cytuja akt - wymagaja przegladu tresci (terminy, progi, artykuly).
//
// Geneza (2026-10-19): rozporzadzenie (UE) 2026/1744 z 8.07.2026 przesunelo terminy
// AI Act, a nasze skille AI Act przez trzy miesiace mowily, ze wysokie ryzyko z zal. III
// juz obowiazuje. wachta-legislacyjna.mjs tego nie widziala: pilnuje tylko, czy ustawa PL
// obowiazuje i nie zmienila nazwy; aktow UE i nowelizacji nie zna.
//
// Skille wiazemy z aktem po wzorcach nazw (skille rzadko podaja numer aktu - pisza
// "GDPR", "AI Act"). Wpis bez zadnego skilla = OSTRZEZENIE (wzorce albo wpis do poprawy).
// Niedostepnosc Cellar/ISAP = OSTRZEZENIE (nie wywalaj CI na chwilowym 5xx).
// Pusty rejestr = BLAD: wachta bez mianownika przechodzi zawsze.
//
// Po przegladzie skilli: dopisz akt zmieniajacy do "znane_zmiany" (UE) albo podnies
// "baseline" (PL) - dopiero wtedy wachta znow jest zielona.
// Uruchamiane w CI co miesiac + recznie: node scripts/wachta-zmian-aktow.mjs [--rejestr PLIK]
import { readFileSync, readdirSync, existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const iArg = process.argv.indexOf("--rejestr");
const plikRej = iArg > 0 ? process.argv[iArg + 1] : join(root, "seuranta/akty-zrodlowe.json");
const reg = JSON.parse(readFileSync(plikRej, "utf8"));
const akty = reg.akty ?? [];
const dzis = new Date().toISOString().slice(0, 10);
const norm = (s) => (s ?? "").toLowerCase().normalize("NFC");
const pauza = () => new Promise((r) => setTimeout(r, 300));

if (!akty.length) {
  console.log(`BLAD: rejestr ${plikRej} nie ma zadnego aktu - wachta bez mianownika nic nie mierzy`);
  process.exit(1);
}

// Teksty skilli: SKILL.md + references/*.md, raz na przebieg.
const skille = [];
for (const plugin of readdirSync(root, { withFileTypes: true })) {
  if (!plugin.isDirectory() || plugin.name.startsWith(".")) continue;
  const dirSk = join(root, plugin.name, "skills");
  if (!existsSync(dirSk)) continue;
  for (const sk of readdirSync(dirSk, { withFileTypes: true })) {
    if (!sk.isDirectory()) continue;
    const plik = join(dirSk, sk.name, "SKILL.md");
    if (!existsSync(plik)) continue;
    let tekst = readFileSync(plik, "utf8");
    const ref = join(dirSk, sk.name, "references");
    if (existsSync(ref)) {
      for (const f of readdirSync(ref)) if (f.endsWith(".md")) tekst += "\n" + readFileSync(join(ref, f), "utf8");
    }
    skille.push({ nazwa: `${plugin.name}/${sk.name}`, tekst: norm(tekst) });
  }
}
const cytujace = (a) => skille.filter((s) => (a.wzorce ?? []).some((w) => s.tekst.includes(norm(w)))).map((s) => s.nazwa);

async function zmianyUE(celex) {
  const q = `PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT DISTINCT ?c WHERE { ?n cdm:resource_legal_id_celex "${celex}"^^xsd:string .
  ?w cdm:resource_legal_amends_resource_legal ?n ; cdm:resource_legal_id_celex ?c }`;
  const url = "https://publications.europa.eu/webapi/rdf/sparql?" +
    new URLSearchParams({ query: q, format: "application/sparql-results+json", timeout: "60000" });
  try {
    const r = await fetch(url, { signal: AbortSignal.timeout(90000), headers: { "user-agent": "MateMatic wachta-zmian-aktow" } });
    if (!r.ok) return null;
    const d = await r.json();
    return d.results.bindings.map((b) => b.c.value);
  } catch {
    return null;
  }
}

async function aktPL(eli) {
  try {
    const r = await fetch(`https://api.sejm.gov.pl/eli/acts/${eli}`, {
      redirect: "follow", signal: AbortSignal.timeout(20000), headers: { accept: "application/json" },
    });
    if (!r.ok) return null;
    return await r.json();
  } catch {
    return null;
  }
}
// ISAP zwraca zmiany pod kluczem "Akty zmieniajace" (z polskim znakiem) - po prefiksie.
function aktyZmieniajace(akt) {
  const refs = akt.references ?? {};
  for (const key of Object.keys(refs)) if (norm(key).startsWith("akty zmieniaj")) return refs[key] ?? [];
  return [];
}

let bledy = 0, ostrzezenia = 0, ok = 0;
console.log(`wachta zmian aktow - ${akty.length} aktow, ${skille.length} skilli w hubie\n`);
for (const a of akty) {
  const id = a.celex ? `celex:${a.celex}` : `eli:${a.eli}`;
  const sk = cytujace(a);
  if (!sk.length) {
    ostrzezenia++;
    console.log(`  [!]  ${a.nazwa} (${id}) - zaden skill nie pasuje do wzorcow; popraw wzorce albo usun wpis`);
  }
  const problemy = [];
  if (a.celex) {
    const zm = await zmianyUE(a.celex);
    if (zm === null) {
      ostrzezenia++;
      console.log(`  [!]  ${a.nazwa} (${id}) - Cellar nie odpowiada, sprawdz recznie`);
      await pauza();
      continue;
    }
    const znane = new Set(a.znane_zmiany ?? []);
    const nowe = zm.filter((c) => !znane.has(c)).sort();
    if (nowe.length) problemy.push(`nowe akty zmieniajace w Cellar: ${nowe.join(", ")}`);
  } else if (a.eli) {
    const akt = await aktPL(a.eli);
    if (!akt || !akt.title) {
      ostrzezenia++;
      console.log(`  [!]  ${a.nazwa} (${id}) - ISAP nie odpowiada, sprawdz recznie`);
      await pauza();
      continue;
    }
    if (akt.inForce !== "IN_FORCE") problemy.push(`inForce=${akt.inForce}`);
    // Zmiana przejrzana z wyprzedzeniem (np. opublikowana z pozniejsza data wejscia w zycie) nie alarmuje drugi raz.
    const znanePL = new Set(a.znane_zmiany ?? []);
    const zmiany = aktyZmieniajace(akt).filter((z) => z?.date && z.date > a.baseline && !znanePL.has(z.id));
    const weszly = zmiany.filter((z) => z.date <= dzis);
    const nadchodza = zmiany.filter((z) => z.date > dzis);
    if (weszly.length) problemy.push(`zmiany po baseline ${a.baseline}: ${weszly.map((z) => `${z.id} (od ${z.date})`).join(", ")}`);
    if (nadchodza.length) {
      ostrzezenia++;
      console.log(`  [!]  ${a.nazwa} - nadchodzace zmiany: ${nadchodza.map((z) => `${z.id} (od ${z.date})`).join(", ")}`);
    }
  } else {
    problemy.push("wpis bez celex i bez eli");
  }
  if (problemy.length) {
    bledy++;
    console.log(`  [X]  ${a.nazwa} (${id}) - ${problemy.join("; ")}`);
    console.log(`       -> przejrzyj skille: ${sk.join(", ") || "(brak dopasowania - sprawdz wzorce)"}`);
  } else {
    ok++;
  }
  await pauza();
}

console.log(`\n${ok} bez nowych zmian - ${ostrzezenia} ostrzezen - ${bledy} wymaga przegladu`);
if (bledy > 0) {
  console.log("\nAkt zrodlowy zmieniony: przejrzyj tresc wskazanych skilli wobec aktu zmieniajacego");
  console.log("(terminy, progi, numery artykulow), potem dopisz go do znane_zmiany / podnies baseline.");
  process.exit(1);
}
