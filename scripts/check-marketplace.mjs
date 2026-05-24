#!/usr/bin/env node
/**
 * check-marketplace.mjs - walidator spojnosci `.claude-plugin/marketplace.json` vs `./skills/`
 *
 * Zero dependencies (Node >= 18). Uruchamiac z root repo: `node scripts/check-marketplace.mjs`
 *
 * Sprawdza:
 *  1. kazdy wpis w marketplace.json ma odpowiadajacy folder `./skills/<name>/`
 *  2. kazdy folder w `./skills/` (poza ukrytymi) ma odpowiadajacy wpis w marketplace.json
 *  3. nazwy w marketplace.json (`name`) zgodne z nazwa folderu
 *  4. kazdy SKILL.md istnieje i ma frontmatter z polami `name` i `description`
 *  5. licencje i wersje w marketplace.json maja niepuste wartosci
 *
 * Exit codes:
 *  0 = OK (wszystko spojne)
 *  1 = znaleziono niezgodnosci (lista wypisana na stderr)
 *  2 = blad uruchomienia (brak plikow konfiguracyjnych etc.)
 */

import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, '..');
const MARKETPLACE = join(ROOT, '.claude-plugin', 'marketplace.json');
const SKILLS_DIR = join(ROOT, 'skills');

function fail(msg, code = 2) {
  process.stderr.write(`[check-marketplace] ERROR: ${msg}\n`);
  process.exit(code);
}

if (!existsSync(MARKETPLACE)) fail(`brak ${MARKETPLACE}`);
if (!existsSync(SKILLS_DIR)) fail(`brak ${SKILLS_DIR}`);

let manifest;
try {
  manifest = JSON.parse(readFileSync(MARKETPLACE, 'utf-8'));
} catch (e) {
  fail(`marketplace.json nie jest poprawnym JSON: ${e.message}`);
}

if (!Array.isArray(manifest.plugins)) fail('marketplace.json brakuje pola "plugins" (array)');

const manifestNames = new Set(manifest.plugins.map((p) => p.name));

const skillFolders = readdirSync(SKILLS_DIR)
  .filter((entry) => !entry.startsWith('.'))
  .filter((entry) => statSync(join(SKILLS_DIR, entry)).isDirectory());
const folderNames = new Set(skillFolders);

const issues = [];

// 1. wpisy bez folderu
for (const plugin of manifest.plugins) {
  if (!folderNames.has(plugin.name)) {
    issues.push(`MISSING_FOLDER: marketplace deklaruje "${plugin.name}" ale brak katalogu skills/${plugin.name}/`);
  }
}

// 2. foldery bez wpisu
for (const folder of skillFolders) {
  if (!manifestNames.has(folder)) {
    issues.push(`MISSING_MANIFEST: skills/${folder}/ istnieje ale brak wpisu w marketplace.json`);
  }
}

// 3. spojnosc name vs folder dla istniejacych
for (const plugin of manifest.plugins) {
  const expectedSource = `./skills/${plugin.name}`;
  if (plugin.source && plugin.source !== expectedSource) {
    issues.push(`SOURCE_MISMATCH: ${plugin.name} ma source "${plugin.source}", oczekiwano "${expectedSource}"`);
  }
}

// 4. SKILL.md + frontmatter
for (const folder of skillFolders) {
  const skillMd = join(SKILLS_DIR, folder, 'SKILL.md');
  if (!existsSync(skillMd)) {
    issues.push(`MISSING_SKILL_MD: skills/${folder}/SKILL.md nie istnieje`);
    continue;
  }
  const content = readFileSync(skillMd, 'utf-8');
  if (!content.startsWith('---')) {
    issues.push(`NO_FRONTMATTER: skills/${folder}/SKILL.md nie ma frontmatter YAML`);
    continue;
  }
  // wez blok miedzy pierwszym a drugim "---"
  const end = content.indexOf('\n---', 3);
  if (end < 0) {
    issues.push(`UNCLOSED_FRONTMATTER: skills/${folder}/SKILL.md frontmatter nie ma zamykajacego ---`);
    continue;
  }
  const fm = content.slice(3, end);
  if (!/^name:\s*\S/m.test(fm)) {
    issues.push(`NO_NAME: skills/${folder}/SKILL.md frontmatter bez pola "name"`);
  }
  if (!/^description:/m.test(fm)) {
    issues.push(`NO_DESCRIPTION: skills/${folder}/SKILL.md frontmatter bez pola "description"`);
  }
}

// 5. wartosci w marketplace
for (const plugin of manifest.plugins) {
  if (!plugin.description || plugin.description.trim().length < 10) {
    issues.push(`SHORT_DESCRIPTION: ${plugin.name} ma za krotki opis w marketplace.json (< 10 znakow)`);
  }
  if (!plugin.version) {
    issues.push(`NO_VERSION: ${plugin.name} brak pola "version" w marketplace.json`);
  }
  if (!plugin.license) {
    issues.push(`NO_LICENSE: ${plugin.name} brak pola "license" w marketplace.json`);
  }
  if (!plugin.author || !plugin.author.name) {
    issues.push(`NO_AUTHOR: ${plugin.name} brak "author.name" w marketplace.json`);
  }
}

// raport
if (issues.length === 0) {
  process.stdout.write(`[check-marketplace] OK - ${manifest.plugins.length} skilli, ${skillFolders.length} folderow, zero niezgodnosci.\n`);
  process.exit(0);
}

process.stderr.write(`[check-marketplace] FAIL - ${issues.length} niezgodnosci:\n`);
for (const i of issues) process.stderr.write(`  - ${i}\n`);
process.exit(1);
