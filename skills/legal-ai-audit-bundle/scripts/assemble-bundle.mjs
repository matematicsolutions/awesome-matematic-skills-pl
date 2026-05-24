#!/usr/bin/env node
// legal-ai-audit-bundle - składanie paczki audytowej AI Act art. 12 (zero-dep ESM).
// Usage: node assemble-bundle.mjs <descriptor.json> <katalog-docelowy>
// Kopiuje artefakty do ustrukturyzowanego folderu, liczy SHA256, generuje manifest.json + INDEX.md.

import { readFileSync, writeFileSync, mkdirSync, copyFileSync, existsSync, statSync } from "node:fs";
import { createHash } from "node:crypto";
import { join, basename } from "node:path";

const SLOTS = [
  { key: "deliverable",       dir: "01-deliverable",        wymagany: true },
  { key: "slad_rozumowania",  dir: "02-slad-rozumowania",   wymaganyHighStakes: true },
  { key: "raport_grounding",  dir: "03-grounding",          wymagany: false },
  { key: "log_kosztu",        dir: "04-koszt",              wymagany: true },
];

function sha256(path) {
  return createHash("sha256").update(readFileSync(path)).digest("hex");
}

function readJson(path) {
  return JSON.parse(readFileSync(path, "utf8").replace(/^﻿/, ""));
}

function main() {
  const [descPath, outRoot] = process.argv.slice(2);
  if (!descPath || !outRoot) {
    console.error("Usage: node assemble-bundle.mjs <descriptor.json> <katalog-docelowy>");
    process.exit(2);
  }
  const d = readJson(descPath);
  const highStakes = String(d.stawka || "").toUpperCase() === "WYSOKA";
  const bundleId = d.deliverable_id || "BUNDLE";
  const bundleDir = join(outRoot, bundleId);
  mkdirSync(bundleDir, { recursive: true });

  const entries = [];
  const missing = [];

  for (const slot of SLOTS) {
    const src = (d.artefakty || {})[slot.key];
    const wymagany = slot.wymagany || (slot.wymaganyHighStakes && highStakes);
    if (!src || !existsSync(src)) {
      const status = wymagany ? "MISSING" : "BRAK (opcjonalny)";
      entries.push({ slot: slot.key, dir: slot.dir, status, plik: src || null });
      if (wymagany) missing.push(slot.key);
      continue;
    }
    const targetDir = join(bundleDir, slot.dir);
    mkdirSync(targetDir, { recursive: true });
    const fname = basename(src);
    const dest = join(targetDir, fname);
    copyFileSync(src, dest);
    entries.push({
      slot: slot.key,
      dir: slot.dir,
      status: "OBECNY",
      plik: `${slot.dir}/${fname}`,
      bajty: statSync(dest).size,
      sha256: sha256(dest),
    });
  }

  const manifest = {
    deliverable_id: bundleId,
    tytul: d.tytul || null,
    data: d.data || new Date().toISOString().slice(0, 10),
    model: d.model || null,
    autor: d.autor || null,
    zatwierdzajacy: d.zatwierdzajacy || null,
    stawka: d.stawka || null,
    zrodla: d.zrodla || [],
    pseudonimizacja_uzyta: !!d.pseudonimizacja_uzyta,
    artefakty: entries,
    kompletnosc: { wymagane_obecne: missing.length === 0, missing },
    wygenerowano: new Date().toISOString(),
  };
  writeFileSync(join(bundleDir, "manifest.json"), JSON.stringify(manifest, null, 2), "utf8");

  const idx = [
    `# Paczka audytowa: ${bundleId}`,
    "",
    `**Tytuł:** ${manifest.tytul || "-"}`,
    `**Data:** ${manifest.data}  |  **Model AI:** ${manifest.model || "-"}`,
    `**Autor:** ${manifest.autor || "-"}  |  **Zatwierdził (nadzór człowieka, art. 14):** ${manifest.zatwierdzajacy || "BRAK ⚠️"}`,
    `**Stawka:** ${manifest.stawka || "-"}`,
    `**Źródła:** ${manifest.zrodla.length ? manifest.zrodla.join(", ") : "-"}`,
    "",
    "> Wynik powstał z udziałem systemu AI (AI Act art. 50 - obowiązek poinformowania).",
    manifest.pseudonimizacja_uzyta
      ? "> Użyto pseudonimizacji. Mapa re-identyfikacji NIE jest częścią tej paczki - trzymana osobno (RODO art. 4 pkt 5)."
      : "> Pseudonimizacji nie użyto.",
    "",
    "## Artefakty (integralność SHA256)",
    "",
    "| Slot | Plik | Status | SHA256 |",
    "|------|------|--------|--------|",
    ...entries.map((e) =>
      `| ${e.slot} | ${e.plik || "-"} | ${e.status} | ${e.sha256 ? e.sha256.slice(0, 16) + "…" : "-"} |`
    ),
    "",
    `## Kompletność`,
    manifest.kompletnosc.wymagane_obecne
      ? "Wszystkie wymagane artefakty obecne ✅"
      : `BRAKUJE wymaganych: ${missing.join(", ")} ⚠️ - uzupełnij lub świadomie odnotuj brak.`,
    "",
    "_Manifest maszynowy: manifest.json_",
  ].join("\n");
  writeFileSync(join(bundleDir, "INDEX.md"), idx, "utf8");

  console.log(JSON.stringify({
    bundleDir,
    artefakty_obecne: entries.filter((e) => e.status === "OBECNY").length,
    artefakty_total: SLOTS.length,
    missing,
    high_stakes: highStakes,
    zatwierdzajacy_brak: !manifest.zatwierdzajacy,
    pseudonimizacja_uzyta: manifest.pseudonimizacja_uzyta,
  }, null, 2));
  process.exit(missing.length > 0 ? 1 : 0);
}

main();
