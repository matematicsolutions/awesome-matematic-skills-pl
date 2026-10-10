#!/usr/bin/env node
/**
 * ocen.mjs - harness ewaluacyjny dla matematic-anonimizacja-pl.
 *
 * Mierzy detektor PII na zaslepionym zestawie ze zlotymi spanami.
 * Wzorzec metryki: arthur-mask/degerlendirme (proprietary, NIE kopiowany kod -
 * przepisany od zera na nasz format wyjscia i nasze etykiety).
 *
 *   node ocen.mjs <zestaw.txt> --silnik <sciezka-do-repo> [--szczegoly]
 *
 * Metryki:
 *   POKRYCIE  - odsetek zlotych spanow PII trafionych JAKIMKOLWIEK typem (nakladanie sie).
 *               To jest liczba, ktora interesuje kancelarie: ile PII w ogole zostalo zlapane.
 *   ZGODNOSC  - odsetek trafionych, ktore dostaly WLASCIWY typ.
 *   RECALL/PRECISION per typ.
 *   NADMIAR   - wykrycia poza zlotymi spanami PII, z osobnym licznikiem najgorszej klasy:
 *               trafien w KONTROLE NEGATYWNA (sygnatury, przepisy, sady, kwoty).
 *
 * Kazde uruchomienie wypisuje date i hash zestawu: wynik bez zestawu nie znaczy nic.
 */
import { existsSync, readFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import path from 'node:path';

const ETYKIETA = /\{\{([A-Z_]+)\|([^{}]*)\}\}/g;

/** Zamienia linie ze zlotymi spanami na czysty tekst + liste spanow z offsetami. */
function rozbierz(linia) {
  let tekst = '';
  const zlote = [];
  let kursor = 0;
  for (const m of linia.matchAll(ETYKIETA)) {
    tekst += linia.slice(kursor, m.index);
    const start = tekst.length;
    tekst += m[2];
    zlote.push({ typ: m[1], wartosc: m[2], start, end: tekst.length });
    kursor = m.index + m[0].length;
  }
  tekst += linia.slice(kursor);
  return { tekst, zlote };
}

const nakladaja = (a, b) => a.start < b.end && b.start < a.end;

/** Mapowanie etykiet zestawu na typy zwracane przez silnik. Jawne, nie domyslne. */
const ALIAS = {
  OSOBA: ['OSOBA', 'PERSON', 'IMIE', 'NAZWISKO'],
  FIRMA: ['FIRMA', 'ORG', 'ORGANIZACJA', 'SPOLKA'],
  PESEL: ['PESEL'],
  NIP: ['NIP'],
  REGON: ['REGON'],
  KRS: ['KRS'],
  PHONE: ['PHONE', 'TELEFON', 'TEL'],
  EMAIL: ['EMAIL', 'MAIL', 'E_MAIL'],
  IBAN: ['IBAN', 'RACHUNEK', 'NRB'],
  ADRES: ['ADRES', 'ADDRESS', 'LOCATION'],
  DATA_UR: ['DATA_UR', 'DATA_URODZENIA', 'BIRTHDATE', 'DATE'],
};
const zgodnyTyp = (zloty, wykryty) => (ALIAS[zloty] || [zloty]).includes(wykryty);

function main() {
  const args = process.argv.slice(2);
  const plik = args[0];
  const silnik = args[args.indexOf('--silnik') + 1];
  const szczegoly = args.includes('--szczegoly');
  if (!plik || !silnik) {
    console.error('uzycie: node ocen.mjs <zestaw.txt> --silnik <sciezka-repo> [--szczegoly]');
    process.exit(2);
  }

  const surowy = readFileSync(plik, 'utf8');
  // Hash z znormalizowanych koncow linii: inaczej ten sam zestaw dawalby inny
  // hash po checkoucie na Windows (CRLF) niz na Linux (LF), a liczba w README
  // przestalaby byc odtwarzalna u odbiorcy.
  const hash = createHash('sha256').update(surowy.replace(/\r\n/g, '\n')).digest('hex').slice(0, 16);
  const linie = surowy.split(/\r?\n/).filter((l) => l.trim() && !l.startsWith('#'));

  const cli = path.join(silnik, 'bin', 'cli.mjs');
  // Bez silnika kazdy fragment konczyl sie bledem, a raport pokazywal "0/0"
  // z kodem 0 - pomiar, ktorego nie bylo, wygladal jak wynik.
  if (!existsSync(cli)) {
    console.error(`BLOKADA: brak silnika ${cli}`);
    process.exit(2);
  }
  const stat = {
    zlotePII: 0, trafione: 0, trafioneDokladnie: 0, zgodnyTyp: 0,
    negatywne: 0, negatywneZjedzone: 0, nadmiar: 0, linii: 0, bledy: 0,
  };
  const perTyp = {};
  const luki = [];
  const zjedzone = [];
  const falszywe = [];

  for (const linia of linie) {
    const { tekst, zlote } = rozbierz(linia);
    stat.linii++;

    let wykryte = [];
    try {
      const out = execFileSync(process.execPath, [cli, 'wykryj', '-'], {
        input: tekst, encoding: 'utf8', maxBuffer: 16 * 1024 * 1024,
      });
      wykryte = (JSON.parse(out).entities || []).map((e) => ({
        typ: e.type, wartosc: e.value, start: e.start, end: e.end,
      }));
    } catch (e) {
      stat.bledy++;
      continue;
    }

    const uzyte = new Set();
    for (const z of zlote) {
      const negatywny = z.typ === 'NIE';
      if (negatywny) stat.negatywne++;
      else {
        stat.zlotePII++;
        perTyp[z.typ] ??= { zlote: 0, trafione: 0, zgodne: 0 };
        perTyp[z.typ].zlote++;
      }

      const dopasowane = wykryte.filter((w) => nakladaja(z, w));
      dopasowane.forEach((w) => uzyte.add(w));

      if (negatywny) {
        if (dopasowane.length) {
          stat.negatywneZjedzone++;
          zjedzone.push({ tekst: z.wartosc, jako: dopasowane.map((d) => `${d.typ}:"${d.wartosc}"`).join(', ') });
        }
        continue;
      }

      if (dopasowane.length) {
        stat.trafione++;
        perTyp[z.typ].trafione++;
        if (dopasowane.some((w) => w.start === z.start && w.end === z.end)) stat.trafioneDokladnie++;
        if (dopasowane.some((w) => zgodnyTyp(z.typ, w.typ))) {
          stat.zgodnyTyp++;
          perTyp[z.typ].zgodne++;
        }
      } else {
        luki.push({ typ: z.typ, tekst: z.wartosc });
      }
    }

    for (const w of wykryte) {
      if (!uzyte.has(w)) {
        stat.nadmiar++;
        falszywe.push({ typ: w.typ, tekst: w.wartosc });
      }
    }
  }

  const pct = (a, b) => (b ? (a / b) : 0).toFixed(3);
  console.log('='.repeat(72));
  console.log(`POMIAR DETEKTORA PII  |  ${new Date().toISOString().slice(0, 10)}`);
  console.log(`zestaw: ${path.basename(plik)}  sha256:${hash}  fragmentow: ${stat.linii}`);
  console.log(`silnik: ${silnik}`);
  console.log('='.repeat(72));
  if (stat.bledy) console.log(`UWAGA: ${stat.bledy} fragmentow nie dalo sie ocenic (blad silnika)\n`);
  console.log(`POKRYCIE PII        ${pct(stat.trafione, stat.zlotePII)}   (${stat.trafione}/${stat.zlotePII} zlotych spanow trafionych jakimkolwiek typem)`);
  console.log(`  w tym co do spanu ${pct(stat.trafioneDokladnie, stat.zlotePII)}   (${stat.trafioneDokladnie} dokladnych granic)`);
  console.log(`  w tym wlasciwy typ  ${pct(stat.zgodnyTyp, stat.zlotePII)}   (${stat.zgodnyTyp} z wlasciwa etykieta)`);
  console.log(`NIEWYKRYTE (WYCIEK) ${stat.zlotePII - stat.trafione} spanow PII przeszlo przez detektor\n`);
  console.log(`KONTROLA NEGATYWNA  ${stat.negatywneZjedzone}/${stat.negatywne} zjedzonych (sygnatury, przepisy, sady, kwoty - maskowac NIE WOLNO)`);
  console.log(`NADMIAR             ${stat.nadmiar} wykryc poza zlotymi spanami\n`);

  console.log('PER TYP:');
  console.log('  typ        zlote  trafione  recall   wlasciwy typ');
  for (const [t, v] of Object.entries(perTyp).sort((a, b) => b[1].zlote - a[1].zlote)) {
    console.log(`  ${t.padEnd(10)} ${String(v.zlote).padStart(5)}  ${String(v.trafione).padStart(8)}  ${pct(v.trafione, v.zlote).padStart(6)}   ${pct(v.zgodne, v.zlote)}`);
  }

  if (szczegoly) {
    console.log('\n--- NIEWYKRYTE (wyciek) ---');
    for (const l of luki) console.log(`  ${l.typ.padEnd(9)} "${l.tekst}"`);
    console.log('\n--- ZJEDZONA KONTROLA NEGATYWNA ---');
    for (const z of zjedzone) console.log(`  "${z.tekst}"  ->  ${z.jako}`);
    console.log('\n--- NADMIAR (pierwsze 40) ---');
    for (const f of falszywe.slice(0, 40)) console.log(`  ${f.typ.padEnd(9)} "${f.tekst}"`);
  }
  console.log('\nZestaw po tym pomiarze jest SPALONY do strojenia: kolejne strojenie mierz nowym zestawem.');
  // Czesciowy pomiar nie jest pomiarem: kazdy blad silnika = kod rozny od 0.
  if (stat.bledy === stat.linii) process.exitCode = 2;
  else if (stat.bledy) process.exitCode = 1;
}

main();
