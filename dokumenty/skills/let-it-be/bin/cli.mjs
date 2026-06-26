#!/usr/bin/env node
// CLI "Let It Be" - anonimizacja/pseudonimizacja polskich danych osobowych.
//
// Uzycie:
//   anonimizuj-pl wykryj        <plik|->                       # raport wykrytych PII (JSON)
//   anonimizuj-pl pseudonimizuj <plik|-> --map mapa.json [--out wynik.txt] [--audit log.txt]
//   anonimizuj-pl anonimizuj    <plik|-> [--out wynik.txt] [--audit log.txt]
//   anonimizuj-pl odwroc        <plik|-> --map mapa.json [--out wynik.txt]
//
// Opcje:
//   --out <plik>            zapisz wynik do pliku (domyslnie stdout)
//   --map <plik>            plik mapy (pseudonimizuj zapisuje, odwroc czyta)
//   --audit <plik>          dopisz zdarzenie do plain-text audit logu
//   --include-sygnatury     traktuj sygnatury orzeczen/aktow jako podmieniane
//   --help                  ta pomoc
//
// Wejscie "-" lub brak = stdin. Brak zaleznosci, dziala offline.

import { parseArgs } from "node:util";
import { readFile, writeFile } from "node:fs/promises";
import {
    pseudonimizuj, anonimizuj, odwroc, detect,
    AuditLog, detectResidualPII, sourceHash,
} from "../src/index.mjs";

const HELP = `Let It Be - anonimizacja/pseudonimizacja polskich danych osobowych (RODO-safe, offline).

KOMENDY:
  wykryj        <plik|->                  raport wykrytych PII (JSON)
  pseudonimizuj <plik|-> --map mapa.json   ODWRACALNA podmiana (mapa do odwroc)
  anonimizuj    <plik|->                   NIEODWRACALNA podmiana (bez mapy)
  odwroc        <plik|-> --map mapa.json   przywraca oryginaly z mapy

OPCJE:
  --out <plik>          zapisz wynik do pliku (domyslnie stdout)
  --map <plik>          plik mapy token<->oryginal
  --audit <plik>        dopisz zdarzenie do audit logu (dla Inspektora RODO)
  --include-sygnatury   traktuj sygnatury orzeczen/aktow jako podmieniane
  --min-confidence <n>  odrzuc dopasowania ponizej progu (np. 0.8)
  --help                ta pomoc

Wejscie "-" lub brak = stdin.`;

async function readInput(path) {
    if (!path || path === "-") {
        const chunks = [];
        for await (const c of process.stdin) chunks.push(c);
        return Buffer.concat(chunks).toString("utf8");
    }
    return readFile(path, "utf8");
}

async function writeOutput(text, out) {
    if (out) await writeFile(out, text, "utf8");
    else process.stdout.write(text.endsWith("\n") ? text : text + "\n");
}

function originalsOf(text, opts) {
    return detect(text, opts).entities.filter((e) => e.isPii).map((e) => e.raw);
}

/** Bramka "no PII leaves" - rzuca jezeli oryginal przetrwal w wyniku. */
function assertNoResidual(out, originals) {
    const residual = detectResidualPII(out, originals);
    if (residual.count > 0) {
        process.stderr.write(
            `BLAD: ${residual.count} PII przetrwalo podmiane (np. fleksja nazwiska). ` +
            `Operacja przerwana - sprawdz dokument recznie.\n`,
        );
        process.exit(2);
    }
}

async function main() {
    const { values, positionals } = parseArgs({
        allowPositionals: true,
        options: {
            out: { type: "string" },
            map: { type: "string" },
            audit: { type: "string" },
            "include-sygnatury": { type: "boolean", default: false },
            "min-confidence": { type: "string" },
            help: { type: "boolean", default: false },
        },
    });

    const cmd = positionals[0];
    if (values.help || !cmd) {
        process.stdout.write(HELP + "\n");
        process.exit(values.help ? 0 : 1);
    }

    const detectOpts = {
        includeSignatures: values["include-sygnatury"],
        minConfidence: values["min-confidence"] ? Number(values["min-confidence"]) : 0,
    };
    const text = await readInput(positionals[1]);

    if (cmd === "wykryj") {
        const { entities } = detect(text, detectOpts);
        const pii = entities.filter((e) => e.isPii);
        const report = {
            source_hash: sourceHash(text),
            counts: pii.reduce((a, e) => ((a[e.type] = (a[e.type] || 0) + 1), a), {}),
            entities: pii.map((e) => ({ type: e.type, value: e.normalized, start: e.start, end: e.end, confidence: e.confidence })),
        };
        await writeOutput(JSON.stringify(report, null, 2), values.out);
        return;
    }

    if (cmd === "pseudonimizuj") {
        const res = pseudonimizuj(text, detectOpts);
        assertNoResidual(res.text, Object.values(res.map));
        await writeOutput(res.text, values.out);
        if (values.map) {
            await writeFile(values.map, JSON.stringify({
                source_hash: res.sourceHash, counts: res.counts,
                created_at: new Date().toISOString(), map: res.map,
            }, null, 2), "utf8");
        } else {
            process.stderr.write("UWAGA: brak --map - mapy nie zapisano, podmiana NIEODWRACALNA.\n");
        }
        if (values.audit) {
            await new AuditLog(values.audit).append({
                event: "pseudonim-applied", mode: "pseudonimizacja",
                source_hash: res.sourceHash, entities: res.counts,
                bytes_in: Buffer.byteLength(text, "utf8"),
                bytes_out: Buffer.byteLength(res.text, "utf8"),
            });
        }
        return;
    }

    if (cmd === "anonimizuj") {
        const originals = originalsOf(text, detectOpts);
        const res = anonimizuj(text, detectOpts);
        assertNoResidual(res.text, originals);
        await writeOutput(res.text, values.out);
        if (values.audit) {
            await new AuditLog(values.audit).append({
                event: "anonimizacja-applied", mode: "anonimizacja",
                source_hash: res.sourceHash, entities: res.counts,
                bytes_in: Buffer.byteLength(text, "utf8"),
                bytes_out: Buffer.byteLength(res.text, "utf8"),
            });
        }
        return;
    }

    if (cmd === "odwroc") {
        if (!values.map) {
            process.stderr.write("BLAD: odwroc wymaga --map <plik>.\n");
            process.exit(1);
        }
        const { map } = JSON.parse(await readFile(values.map, "utf8"));
        await writeOutput(odwroc(text, map), values.out);
        return;
    }

    process.stderr.write(`Nieznana komenda: ${cmd}\n\n${HELP}\n`);
    process.exit(1);
}

main().catch((err) => {
    process.stderr.write(`BLAD: ${err.message}\n`);
    process.exit(1);
});
