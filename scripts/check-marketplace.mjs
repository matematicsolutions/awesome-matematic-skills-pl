#!/usr/bin/env node
/**
 * check-marketplace.mjs - walidator `.claude-plugin/marketplace.json` (model bundli + plaski)
 *
 * Zero dependencies (Node >= 18). Uruchamiac z root repo: `node scripts/check-marketplace.mjs`
 *
 * Modele wpisow (dozwolone rownolegle - Claude Code wspiera mieszane layouty):
 *  - BUNDLE: source -> katalog z podkatalogiem `skills/<skill>/SKILL.md` (1+ skilli).
 *            Opcjonalnie `.mcp.json` (mcpServers) i `.claude-plugin/plugin.json` (name).
 *  - PLASKI: source -> katalog z `SKILL.md` w korzeniu (pojedynczy skill).
 *
 * Sprawdza dla kazdego wpisu:
 *  1. source istnieje na dysku
 *  2. bundle: skills/ ma >=1 podkatalog, kazdy z SKILL.md + frontmatter (name, description)
 *     plaski: SKILL.md w korzeniu + frontmatter (name, description)
 *  3. jesli .mcp.json istnieje: poprawny JSON z obiektem `mcpServers`; serwer zdalny (type http/sse)
 *     ma adres https, lokalny ma `command`
 *  4. .claude-plugin/plugin.json istnieje (obowiazkowo): poprawny JSON, `name` i `version` jak we wpisie;
 *     nazwa wpisu = nazwa katalogu source
 *  5. wpis ma niepuste description (>=10), version, license, author.name
 *  6. kazdy katalog w ./skills/ ma odpowiadajacy wpis (brak osieroconych plaskich skilli)
 *
 * Exit: 0 = OK | 1 = niezgodnosci | 2 = blad uruchomienia
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

let manifest;
try {
  manifest = JSON.parse(readFileSync(MARKETPLACE, 'utf-8'));
} catch (e) {
  fail(`marketplace.json nie jest poprawnym JSON: ${e.message}`);
}
if (!Array.isArray(manifest.plugins)) fail('marketplace.json brakuje pola "plugins" (array)');

const issues = [];
const isDir = (p) => existsSync(p) && statSync(p).isDirectory();

function checkSkillMd(skillMd, label) {
  if (!existsSync(skillMd)) {
    issues.push(`MISSING_SKILL_MD: ${label} - brak SKILL.md`);
    return;
  }
  const content = readFileSync(skillMd, 'utf-8');
  if (!content.startsWith('---')) {
    issues.push(`NO_FRONTMATTER: ${label} - SKILL.md bez frontmatter`);
    return;
  }
  const end = content.indexOf('\n---', 3);
  if (end < 0) {
    issues.push(`UNCLOSED_FRONTMATTER: ${label} - frontmatter bez zamykajacego ---`);
    return;
  }
  const fm = content.slice(3, end);
  if (!/^name:\s*\S/m.test(fm)) issues.push(`NO_NAME: ${label} - frontmatter bez "name"`);
  if (!/^description:/m.test(fm)) issues.push(`NO_DESCRIPTION: ${label} - frontmatter bez "description"`);
}

function checkJson(file, label, requireKey) {
  try {
    const obj = JSON.parse(readFileSync(file, 'utf-8'));
    if (requireKey && !(requireKey in obj)) {
      issues.push(`BAD_JSON: ${label} - brak klucza "${requireKey}"`);
    }
    return obj;
  } catch (e) {
    issues.push(`BAD_JSON: ${label} - niepoprawny JSON (${e.message})`);
    return null;
  }
}

for (const plugin of manifest.plugins) {
  const name = plugin.name || '(bez nazwy)';
  // 5. pola wpisu
  if (!plugin.description || plugin.description.trim().length < 10)
    issues.push(`SHORT_DESCRIPTION: ${name} - opis < 10 znakow`);
  if (!plugin.version) issues.push(`NO_VERSION: ${name} - brak "version"`);
  if (!plugin.license) issues.push(`NO_LICENSE: ${name} - brak "license"`);
  if (!plugin.author || !plugin.author.name) issues.push(`NO_AUTHOR: ${name} - brak "author.name"`);

  // 1. source istnieje
  const src = plugin.source ? join(ROOT, plugin.source) : null;
  if (!src || !isDir(src)) {
    issues.push(`MISSING_SOURCE: ${name} - source "${plugin.source}" nie istnieje`);
    continue;
  }

  // 2. bundle vs plaski
  const skillsSub = join(src, 'skills');
  if (isDir(skillsSub)) {
    const subdirs = readdirSync(skillsSub).filter((e) => !e.startsWith('.') && isDir(join(skillsSub, e)));
    if (subdirs.length === 0) issues.push(`EMPTY_BUNDLE: ${name} - skills/ bez podkatalogow`);
    for (const sd of subdirs) checkSkillMd(join(skillsSub, sd, 'SKILL.md'), `${name}/skills/${sd}`);
  } else if (existsSync(join(src, 'SKILL.md'))) {
    checkSkillMd(join(src, 'SKILL.md'), name);
  } else if (existsSync(join(src, '.mcp.json'))) {
    // plugin connector-only (samo .mcp.json, bez skilli) - dozwolony
  } else {
    issues.push(`NO_CONTENT: ${name} - brak skills/, SKILL.md i .mcp.json`);
  }

  // 3. .mcp.json (opcjonalny); serwer zdalny (type http/sse) musi miec adres https
  const mcp = join(src, '.mcp.json');
  if (existsSync(mcp)) {
    const m = checkJson(mcp, `${name}/.mcp.json`, 'mcpServers');
    for (const [srv, cfg] of Object.entries((m && m.mcpServers) || {})) {
      if (cfg && (cfg.type === 'http' || cfg.type === 'sse') && !/^https:\/\/\S+$/.test(String(cfg.url || '')))
        issues.push(`BAD_REMOTE_MCP: ${name}/.mcp.json - serwer "${srv}" typu ${cfg.type} bez adresu https`);
      if (cfg && !cfg.type && !cfg.command)
        issues.push(`BAD_MCP_SERVER: ${name}/.mcp.json - serwer "${srv}" bez "command" i bez "type"`);
    }
  }

  // 4. plugin.json OBOWIAZKOWY (AGENTS.md "Consistency test"): name i version zgodne z wpisem,
  // nazwa wpisu = nazwa katalogu. Do 17.11 plugin.json byl opcjonalny, a wersji nikt nie porownywal.
  const pj = join(src, '.claude-plugin', 'plugin.json');
  const folder = plugin.source.replace(/\/+$/, '').split('/').pop();
  if (folder !== plugin.name)
    issues.push(`FOLDER_MISMATCH: ${name} - katalog "${folder}" inny niz nazwa wpisu`);
  if (!existsSync(pj)) {
    issues.push(`NO_PLUGIN_JSON: ${name} - brak ${plugin.source}/.claude-plugin/plugin.json`);
  } else {
    const p = checkJson(pj, `${name}/.claude-plugin/plugin.json`, 'name');
    if (p && p.name && p.name !== plugin.name)
      issues.push(`NAME_MISMATCH: ${name} - plugin.json ma name "${p.name}"`);
    if (p && !p.version)
      issues.push(`NO_PLUGIN_VERSION: ${name} - plugin.json bez "version"`);
    else if (p && plugin.version && p.version !== plugin.version)
      issues.push(`VERSION_MISMATCH: ${name} - marketplace.json ${plugin.version}, plugin.json ${p.version}`);
  }
}

// 6. osierocone plaskie skille w ./skills/
if (isDir(SKILLS_DIR)) {
  const declaredSources = new Set(manifest.plugins.map((p) => p.source));
  const flatFolders = readdirSync(SKILLS_DIR).filter((e) => !e.startsWith('.') && isDir(join(SKILLS_DIR, e)));
  for (const f of flatFolders) {
    if (!declaredSources.has(`./skills/${f}`)) {
      issues.push(`ORPHAN_SKILL: skills/${f}/ istnieje ale brak wpisu w marketplace.json`);
    }
  }
}

const pluginCount = manifest.plugins.length;
if (issues.length === 0) {
  process.stdout.write(`[check-marketplace] OK - ${pluginCount} pluginow, zero niezgodnosci.\n`);
  process.exit(0);
}
process.stderr.write(`[check-marketplace] FAIL - ${issues.length} niezgodnosci:\n`);
for (const i of issues) process.stderr.write(`  - ${i}\n`);
process.exit(1);
