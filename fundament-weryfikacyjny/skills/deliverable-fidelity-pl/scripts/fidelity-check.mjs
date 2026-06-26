#!/usr/bin/env node
// deliverable-fidelity-pl - mechaniczny check wiernosci (zero-dep ESM).
// Usage: node fidelity-check.mjs <task.json>
// task.json: { findings: [ { id, severity, tekst, rozstrzygniecie? } ], deliverable }
// Sprawdza, czy kluczowe terminy kazdego ustalenia pojawiaja sie w deliverable. Pominiete RED -> exit 1.
// To CZESC MECHANICZNA. Bagatelizowanie tonu wykrywa dopiero spot-check LLM (patrz SKILL.md).

import { readFileSync } from "node:fs";

const STOP = new Set([
  "i","oraz","lub","albo","ale","wiec","czy","ze","iz","sie","nie","tak","jak","to","ta","te","ten","tej","tym","tych",
  "jest","sa","byc","byl","byla","bylo","beda","bedzie","ma","maja","mial","miala","do","od","na","w","we","z","ze","za",
  "po","przy","przez","dla","o","u","pod","nad","bez","wobec","wedlug","miedzy","oraz","jako","co","ktory","ktora","ktore",
  "ktorego","ktorej","ktorych","gdy","gdyz","poniewaz","jezeli","jesli","aby","zeby","tez","takze","juz","tylko","bardzo",
  "moze","mozna","powinien","powinna","art","par","ust","pkt","kc","kpc","ksh","rodo"
]);

function normalize(s) {
  if (s == null) return "";
  return String(s)
    .replace(/[„""»«’‘'`]/g, '"')
    .replace(/[—–]/g, "-")
    .toLowerCase()
    .replace(/\s+/g, " ")
    .trim();
}

// Kluczowe terminy: slowa >=4 znaki, nie-stop, plus zachowane liczby/sygnatury (np. "473", "385").
function keyTerms(text) {
  const norm = normalize(text);
  const raw = norm.split(/[^0-9a-ząćęłńóśźż]+/).filter(Boolean);
  const terms = [];
  const seen = new Set();
  for (const w of raw) {
    if (seen.has(w)) continue;
    const isNum = /^\d{2,}$/.test(w);
    if (isNum || (w.length >= 4 && !STOP.has(w))) {
      terms.push(w);
      seen.add(w);
    }
  }
  return terms;
}

// Konserwatywny stem dla polskiej fleksji: utnij 2 koncowe znaki przy slowach >=7
// (np. "klauzuli" -> "klauzu", "usuniecia" -> "usuniec"). Krotsze slowa bez zmian,
// zeby nie podniesc ryzyka falszywego trafienia (gorszy kierunek - cichy pass pominietego RED).
function stem(t) {
  return t.length >= 7 ? t.slice(0, t.length - 2) : t;
}

function coverage(terms, deliverableNorm) {
  if (terms.length === 0) return { present: 0, total: 0, ratio: 1, missing: [] };
  let present = 0;
  const missing = [];
  for (const t of terms) {
    if (deliverableNorm.includes(stem(t))) present += 1;
    else missing.push(t);
  }
  return { present, total: terms.length, ratio: present / terms.length, missing };
}

const THRESHOLD = 0.4; // co najmniej 40% kluczowych terminow ustalenia obecnych

function main() {
  const path = process.argv[2];
  if (!path) {
    console.error("Usage: node fidelity-check.mjs <task.json>");
    process.exit(2);
  }
  const task = JSON.parse(readFileSync(path, "utf8").replace(/^﻿/, ""));
  const findings = Array.isArray(task.findings) ? task.findings : [];
  const deliv = normalize(task.deliverable);
  if (deliv.length === 0) {
    console.error("Brak deliverable do sprawdzenia");
    process.exit(2);
  }

  const results = findings.map((f) => {
    const terms = keyTerms(f.tekst);
    const cov = coverage(terms, deliv);
    const reprezentowane = cov.ratio >= THRESHOLD;
    let rozstrz = null;
    if (f.rozstrzygniecie && String(f.rozstrzygniecie).trim()) {
      const rTerms = keyTerms(f.rozstrzygniecie);
      const rCov = coverage(rTerms, deliv);
      rozstrz = { reprezentowane: rCov.ratio >= THRESHOLD, ratio: Number(rCov.ratio.toFixed(2)) };
    }
    return {
      id: f.id,
      severity: f.severity,
      reprezentowane,
      pokrycie: `${cov.present}/${cov.total}`,
      ratio: Number(cov.ratio.toFixed(2)),
      brakujace_terminy: reprezentowane ? [] : cov.missing.slice(0, 8),
      rozstrzygniecie: rozstrz,
    };
  });

  const pominieteRed = results.filter((r) => r.severity === "RED" && !r.reprezentowane);
  const rozstrzRedBrak = results.filter(
    (r) => r.severity === "RED" && r.rozstrzygniecie && !r.rozstrzygniecie.reprezentowane
  );
  const blokada = pominieteRed.length > 0;

  const summary = {
    total: results.length,
    reprezentowane: results.filter((r) => r.reprezentowane).length,
    pominiete_red: pominieteRed.map((r) => r.id),
    rozstrzygniecia_red_brak: rozstrzRedBrak.map((r) => r.id),
    najciezsze_do_spotcheck_llm: results
      .filter((r) => r.severity === "RED")
      .slice(0, 3)
      .map((r) => r.id),
  };

  console.log(JSON.stringify({ summary, blokada, uwaga: "check mechaniczny - bagatelizowanie tonu wykrywa spot-check LLM", results }, null, 2));
  process.exit(blokada ? 1 : 0);
}

main();
