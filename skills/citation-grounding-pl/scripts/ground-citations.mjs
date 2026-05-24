#!/usr/bin/env node
// citation-grounding-pl - mechaniczny weryfikator cytatu (zero-dep ESM).
// Usage: node ground-citations.mjs <task.json>
// task.json: { "items": [ { id, source_id, source_text, quote } ] }
// Wynik: JSON na stdout z polem status per cytat (NIE semantyczny - czysty string-match po normalizacji).

import { readFileSync } from "node:fs";

const QUOTE_CHARS = /[„""»«’‘'`]/g;
const DASHES = /[—–]/g;

function normalize(s) {
  if (s == null) return "";
  return String(s)
    .replace(/-\s*\n\s*/g, "")        // myślnik przenoszenia na końcu wiersza
    .replace(QUOTE_CHARS, '"')        // ujednolicenie cudzysłowów
    .replace(DASHES, "-")             // ujednolicenie myślników
    .toLowerCase()
    .replace(/\s+/g, " ")             // zwinięcie białych znaków
    .trim();
}

// Cytat może zawierać luki [...] lub ... oznaczające pominięty fragment.
// Dzielimy cytat na segmenty i sprawdzamy, że występują w źródle w kolejności.
function splitGaps(normQuote) {
  return normQuote
    .split(/\s*(?:\[\s*\.\.\.\s*\]|\.\.\.)\s*/)
    .map((seg) => seg.trim())
    .filter((seg) => seg.length > 0);
}

// Lewenshtein na krótkich stringach - tylko do oceny "ZMODYFIKOWANY".
function editDistance(a, b) {
  const m = a.length, n = b.length;
  if (Math.abs(m - n) > 40) return Math.max(m, n);
  const dp = Array.from({ length: m + 1 }, (_, i) => i);
  for (let j = 1; j <= n; j++) {
    let prev = dp[0];
    dp[0] = j;
    for (let i = 1; i <= m; i++) {
      const tmp = dp[i];
      dp[i] = Math.min(
        dp[i] + 1,
        dp[i - 1] + 1,
        prev + (a[i - 1] === b[j - 1] ? 0 : 1)
      );
      prev = tmp;
    }
  }
  return dp[m];
}

// Najlepsze przybliżone dopasowanie segmentu w źródle (przesuwane okno o długości segmentu).
function bestApprox(segment, source) {
  const L = segment.length;
  if (L === 0 || source.length < L) return { dist: L, at: -1 };
  let best = { dist: Infinity, at: -1 };
  const step = L > 200 ? 5 : 1;
  for (let i = 0; i + L <= source.length; i += step) {
    const window = source.slice(i, i + L);
    const d = editDistance(segment, window);
    if (d < best.dist) best = { dist: d, at: i };
    if (d === 0) break;
  }
  return best;
}

function verify(item) {
  const sourceText = item.source_text;
  if (sourceText == null || normalize(sourceText).length === 0) {
    return { id: item.id, source_id: item.source_id, status: "BRAK_ZRODLA", note: "nie dostarczono tekstu źródłowego" };
  }
  const src = normalize(sourceText);
  const segments = splitGaps(normalize(item.quote));
  if (segments.length === 0) {
    return { id: item.id, source_id: item.source_id, status: "BRAK_ZRODLA", note: "pusty cytat" };
  }

  // 1) próba dokładna - wszystkie segmenty w kolejności
  let cursor = 0;
  let firstOffset = -1;
  let exact = true;
  for (const seg of segments) {
    const idx = src.indexOf(seg, cursor);
    if (idx === -1) { exact = false; break; }
    if (firstOffset === -1) firstOffset = idx;
    cursor = idx + seg.length;
  }
  if (exact) {
    return { id: item.id, source_id: item.source_id, status: "ZWERYFIKOWANY", offset: firstOffset };
  }

  // 2) próba przybliżona - sygnał "ZMODYFIKOWANY" vs "NIEZWERYFIKOWANY"
  let worstRatio = 0;
  let detail = [];
  for (const seg of segments) {
    const { dist, at } = bestApprox(seg, src);
    const ratio = seg.length > 0 ? dist / seg.length : 1;
    worstRatio = Math.max(worstRatio, ratio);
    detail.push({ seg: seg.slice(0, 60), dist, at });
  }
  if (worstRatio <= 0.15) {
    return { id: item.id, source_id: item.source_id, status: "ZMODYFIKOWANY", note: "drobne różnice (interpunkcja/ucięcie)", detail };
  }
  return { id: item.id, source_id: item.source_id, status: "NIEZWERYFIKOWANY", note: "brak trafienia - potencjalna halucynacja", detail };
}

function main() {
  const path = process.argv[2];
  if (!path) {
    console.error("Usage: node ground-citations.mjs <task.json>");
    process.exit(2);
  }
  const task = JSON.parse(readFileSync(path, "utf8").replace(/^﻿/, ""));
  const items = Array.isArray(task.items) ? task.items : [];
  const results = items.map(verify);
  const summary = {
    total: results.length,
    zweryfikowane: results.filter((r) => r.status === "ZWERYFIKOWANY").length,
    zmodyfikowane: results.filter((r) => r.status === "ZMODYFIKOWANY").length,
    niezweryfikowane: results.filter((r) => r.status === "NIEZWERYFIKOWANY").length,
    brak_zrodla: results.filter((r) => r.status === "BRAK_ZRODLA").length,
  };
  const blokada = summary.niezweryfikowane > 0 || summary.brak_zrodla > 0;
  console.log(JSON.stringify({ summary, blokada, results }, null, 2));
  process.exit(blokada ? 1 : 0);
}

main();
