#!/usr/bin/env node
// Audyt cytowan ustaw: pelny sweep repo pod katem KAZDEGO wystapienia
// cytowania ustawy, nie tylko top-level rejestru. Odpowiednik
// viittausauditointi z akunikkola/claude-for-legal-finland (MIT) - ich
// pelny audyt 137 cytowan zlapal 4 realne bledy (m.in. uchylona ustawa
// podana jako obowiazujaca), ktorych ich watch po samej nazwie nie widzial.
//
// Dwie role, jeden problem u korzenia: wachta-legislacyjna.mjs chroni
// TYLKO to, co zarejestrowane w seuranta/ustawy.json:
//   1. Dla kazdej zarejestrowanej ustawy - konkretne lokalizacje (plik:linia)
//      cytowania, zamiast recznie pisanej notatki "uzycie" (ktora sie starzeje).
//   2. Wykrycie cytowan Dz.U. w tresci repo, ktore NIE sa zarejestrowane -
//      luka pokrycia rejestru samego w sobie, ktorej zadna wachta nie zobaczy,
//      bo nie wie o istnieniu tych ustaw.
//
// Nie zastepuje wachty - jest jej dopelnieniem na poziomie WYSTAPIEN.
// Uzycie: node scripts/audyt-cytowan-ustaw.mjs
// Exit 1 = znaleziono cytowania Dz.U. spoza rejestru (wymaga decyzji:
// dopisac do rejestru albo zweryfikowac recznie i swiadomie pominac).

import { readFileSync, readdirSync, statSync } from "node:fs";
import { dirname, join, relative } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const reg = JSON.parse(readFileSync(join(root, "seuranta/ustawy.json"), "utf8"));

const SKIP_DIRS = new Set(["node_modules", ".git", "dist", "build"]);
// Materialy cwiczebne w examples/ - Dz.U. tam moze byc przykladowe/nieprawdziwe,
// nie realne cytowanie do sledzenia.
const SKIP_PREFIXES = ["examples/"];

function walkMd(dir, out = []) {
  for (const name of readdirSync(dir)) {
    if (SKIP_DIRS.has(name)) continue;
    const p = join(dir, name);
    const st = statSync(p);
    if (st.isDirectory()) walkMd(p, out);
    else if (name.endsWith(".md")) out.push(p);
  }
  return out;
}

function eliToDzU(eli) {
  const [, rok, poz] = eli.split("/");
  return { rok, poz };
}

const files = walkMd(root).filter(
  (f) => !SKIP_PREFIXES.some((p) => relative(root, f).replace(/\\/g, "/").startsWith(p))
);
const fileLines = new Map();
for (const f of files) {
  fileLines.set(f, readFileSync(f, "utf8").split("\n"));
}

console.log(`audyt cytowan ustaw - ${reg.ustawy.length} zarejestrowanych, ${files.length} plikow .md (bez examples/)\n`);

const escapeRegex = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
// Granice slowa: \b (ASCII) nie lapie substring wewnatrz innego wyrazu
// (np. "KC" w "INSTRUKCJA") - bez tego krotkie skroty (KC, KK, KP) generuja
// falszywe trafienia. \b traktuje polskie znaki diakrytyczne jako NIE-word,
// wiec granica tuz przy nich zadziala tak samo jak przy spacji/przecinku.
const termRegex = (t) => new RegExp(`\\b${escapeRegex(t)}\\b`);

// --- Czesc 1: lokalizacje cytowan zarejestrowanych ustaw -------------------
for (const u of reg.ustawy) {
  const { rok, poz } = eliToDzU(u.eli);
  const terms = [u.skrot, u.nazwa, `Dz.U. ${rok} poz. ${poz}`, `Dz. U. ${rok} poz. ${poz}`]
    .filter(Boolean)
    .map(termRegex);
  const hits = [];
  for (const [f, lines] of fileLines) {
    lines.forEach((line, i) => {
      if (terms.some((re) => re.test(line))) hits.push(`${relative(root, f)}:${i + 1}`);
    });
  }
  console.log(`${u.skrot} (${u.eli}): ${hits.length} wystapien`);
  if (hits.length) {
    const shown = hits.slice(0, 12);
    console.log(`  ${shown.join(", ")}${hits.length > shown.length ? `, ... (+${hits.length - shown.length})` : ""}`);
  }
}

// --- Czesc 2: cytowania Dz.U. w repo NIEOBECNE w rejestrze -----------------
const DZU_RE = /Dz\.?\s?U\.?\s?(?:z\s+)?(\d{4})[^0-9]{0,15}poz\.?\s?(\d+)/g;
const known = new Set(
  reg.ustawy.map((u) => {
    const { rok, poz } = eliToDzU(u.eli);
    return `${rok}/${poz}`;
  })
);
// Swiadome pominiecia z rejestru (sekcja "pominiete"): noweli skonsumowane
// itp. - cytowane historycznie, ich tresc zyje w zarejestrowanym akcie
// bazowym. Kazdy wpis niesie "powod"; bez powodu w JSON nie dopisuj.
const pominiete = new Map((reg.pominiete ?? []).map((p) => [p.dzu, p.powod]));
const unregistered = new Map();

for (const [f, lines] of fileLines) {
  lines.forEach((line, i) => {
    for (const m of line.matchAll(DZU_RE)) {
      const key = `${m[1]}/${m[2]}`;
      if (!known.has(key) && !pominiete.has(key)) {
        if (!unregistered.has(key)) unregistered.set(key, []);
        unregistered.get(key).push(`${relative(root, f)}:${i + 1}`);
      }
    }
  });
}

if (pominiete.size) {
  console.log(`\n--- Swiadomie pominiete (${pominiete.size}, sekcja "pominiete" rejestru) ---`);
  for (const [key, powod] of pominiete) {
    console.log(`Dz.U. ${key.replace("/", " poz. ")}: ${powod}`);
  }
}

console.log(`\n--- Cytowania Dz.U. spoza rejestru (${unregistered.size}) ---`);
if (unregistered.size === 0) {
  console.log("Brak - kazde cytowane Dz.U. jest w seuranta/ustawy.json.");
} else {
  for (const [key, locs] of unregistered) {
    console.log(`Dz.U. ${key.replace("/", " poz. ")}: ${locs.join(", ")}`);
  }
  console.log(
    "\nDodaj powyzsze do seuranta/ustawy.json (jesli ustawa jest istotna dla skilli) albo swiadomie pomin -"
  );
  console.log("wachta-legislacyjna.mjs pilnuje WYLACZNIE tego, co zarejestrowane.");
}

console.log(
  "\nGranica: czesc 2 lapie WYLACZNIE doslowne cytowania \"Dz.U. RRRR poz. NNNN\" - nowy skrot"
);
console.log(
  "wprowadzony bez takiego odniesienia (np. samo \"XYZ\" w tekscie) nie zostanie wykryty automatycznie."
);

process.exit(unregistered.size > 0 ? 1 : 0);
