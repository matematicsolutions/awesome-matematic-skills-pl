#!/usr/bin/env node
/**
 * ocen_bramki.mjs - mierzy SCIEZKE KONSUMENTA, nie sam detektor.
 *
 * README silnika obiecuje bramke "no PII leaves": po podmianie sprawdza, czy jakis
 * oryginal przetrwal, i przerywa z kodem 2. Detektor moze przeciekac, a mimo to
 * produkt moze byc bezpieczny - jesli bramka lapie reszte. To sie mierzy osobno.
 *
 * Trzy wyniki na fragment:
 *   CZYSTO   - anonimizacja przeszla (kod 0) i zadna zlota wartosc PII nie przetrwala w wyjsciu
 *   BLOKADA  - anonimizacja przerwana (kod != 0): bramka zadzialala, PII nie wychodzi
 *   PRZECIEK - anonimizacja przeszla (kod 0), ale zlota wartosc PII JEST w wyjsciu
 *
 * PRZECIEK to jedyny wynik, ktory oznacza realny wyciek do modelu.
 * BLOKADA to koszt uzytecznosci, nie incydent bezpieczenstwa.
 */
import { existsSync, readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import path from 'node:path';

const ETYKIETA = /\{\{([A-Z_]+)\|([^{}]*)\}\}/g;

function rozbierz(linia) {
  let tekst = '';
  const zlote = [];
  let kursor = 0;
  for (const m of linia.matchAll(ETYKIETA)) {
    tekst += linia.slice(kursor, m.index);
    tekst += m[2];
    zlote.push({ typ: m[1], wartosc: m[2] });
    kursor = m.index + m[0].length;
  }
  tekst += linia.slice(kursor);
  return { tekst, zlote };
}

const plik = process.argv[2];
const silnik = process.argv[process.argv.indexOf('--silnik') + 1];
const szczegoly = process.argv.includes('--szczegoly');
const surowy = readFileSync(plik, 'utf8');
// Hash z znormalizowanych koncow linii - patrz komentarz w ocen.mjs.
const hash = createHash('sha256').update(surowy.replace(/\r\n/g, '\n')).digest('hex').slice(0, 16);
const linie = surowy.split(/\r?\n/).filter((l) => l.trim() && !l.startsWith('#'));
const cli = path.join(silnik, 'bin', 'cli.mjs');
if (!existsSync(cli)) {
  console.error(`BLOKADA: brak silnika ${cli}`);
  process.exit(2);
}
// Bramka "no PII leaves" konczy CLI kodem 2. Kazdy inny niezerowy kod to
// wywrotka silnika - wczesniej liczona jako BLOKADA, czyli jako sukces ochrony.
const KOD_BRAMKI = 2;
let bledySilnika = 0;

let czysto = 0, blokada = 0, przeciek = 0;
const przecieki = [];
const blokady = [];
const kody = {};

for (const linia of linie) {
  const { tekst, zlote } = rozbierz(linia);
  const pii = zlote.filter((z) => z.typ !== 'NIE');
  let out = '', kod = 0;
  try {
    out = execFileSync(process.execPath, [cli, 'anonimizuj', '-'], {
      input: tekst, encoding: 'utf8', maxBuffer: 16 * 1024 * 1024, stdio: ['pipe', 'pipe', 'pipe'],
    });
  } catch (e) {
    kod = e.status ?? -1;
    out = (e.stdout || '').toString();
  }
  kody[kod] = (kody[kod] || 0) + 1;

  if (kod !== 0 && kod !== KOD_BRAMKI) {
    bledySilnika++;
    continue;
  }
  if (kod !== 0) {
    blokada++;
    blokady.push({ tekst: tekst.slice(0, 70), kod });
    continue;
  }
  const ocalale = pii.filter((z) => out.includes(z.wartosc));
  if (ocalale.length) {
    przeciek++;
    przecieki.push({ fragment: tekst.slice(0, 60), ocalale: ocalale.map((o) => `${o.typ}:"${o.wartosc}"`) });
  } else {
    czysto++;
  }
}

const n = linie.length;
const pct = (a) => ((a / n) * 100).toFixed(1) + '%';
console.log('='.repeat(72));
console.log(`SCIEZKA KONSUMENTA: anonimizuj + bramka "no PII leaves"  |  ${new Date().toISOString().slice(0, 10)}`);
console.log(`zestaw: ${path.basename(plik)}  sha256:${hash}  fragmentow: ${n}`);
console.log('='.repeat(72));
console.log(`CZYSTO    ${String(czysto).padStart(3)}  ${pct(czysto).padStart(6)}  anonimizacja przeszla, zero PII w wyjsciu`);
console.log(`BLOKADA   ${String(blokada).padStart(3)}  ${pct(blokada).padStart(6)}  bramka przerwala - PII nie wychodzi (koszt uzytecznosci)`);
console.log(`PRZECIEK  ${String(przeciek).padStart(3)}  ${pct(przeciek).padStart(6)}  <<< REALNY WYCIEK DO MODELU`);
console.log(`BLAD SILNIKA ${String(bledySilnika).padStart(3)}  ${pct(bledySilnika).padStart(6)}  fragment nieoceniony (kod inny niz 0 i ${KOD_BRAMKI})`);
console.log(`\nkody wyjscia: ${JSON.stringify(kody)}`);
if (bledySilnika) process.exitCode = bledySilnika === n ? 2 : 1;

if (szczegoly) {
  console.log('\n--- PRZECIEKI (kod 0, a PII w wyjsciu) ---');
  if (!przecieki.length) console.log('  (brak)');
  for (const p of przecieki) console.log(`  "${p.fragment}..."\n      ocalalo: ${p.ocalale.join(', ')}`);
  console.log(`\n--- BLOKADY (pierwsze 15 z ${blokady.length}) ---`);
  for (const b of blokady.slice(0, 15)) console.log(`  [kod ${b.kod}] "${b.tekst}..."`);
}
