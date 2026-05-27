// Rdzen silnika: dwa tryby RODO.
//
//   pseudonimizuj() - ODWRACALNY. Zwraca mape token<->oryginal. Do pracy
//   z LLM: podmieniasz PII przed wyslaniem, odwracasz odpowiedz. Zgodne
//   z RODO art. 4 pkt 5 (pseudonimizacja - dane nadal osobowe).
//
//   anonimizuj() - NIEODWRACALNY. Mapa NIE jest zwracana ani zapisywana,
//   surowe wartosci sa usuwane z wyniku API. Do publikacji / dzielenia
//   dokumentu (RODO motyw 26 - dane zanonimizowane nie podlegaja RODO).
//
// Ten sam oryginal -> ten sam token w obrebie dokumentu (zachowana
// korreferencja: "Jan Kowalski" wszedzie staje sie tym samym [OSOBA_1]).

import { detect, countByType } from "./detect.mjs";
import { sourceHash } from "./mapping-store.mjs";

/** Buduje tekst z tokenami. `entities` musza byc rozlaczne i posortowane. */
function buildTokens(text, entities) {
    const counters = {};
    const tokenByKey = new Map();
    const map = {};
    let out = "";
    let cursor = 0;
    for (const e of entities) {
        out += text.slice(cursor, e.start);
        const key = `${e.type}:${e.normalized}`;
        let token = tokenByKey.get(key);
        if (!token) {
            counters[e.type] = (counters[e.type] || 0) + 1;
            token = `[${e.type}_${counters[e.type]}]`;
            tokenByKey.set(key, token);
            map[token] = e.raw;
        }
        out += token;
        cursor = e.end;
    }
    out += text.slice(cursor);
    return { out, map };
}

/**
 * Pseudonimizacja ODWRACALNA. Zwraca mape do pozniejszego `odwroc()`.
 *
 * @param {string} text
 * @param {object} [opts] przekazywane do detect() (np. includeSignatures).
 * @returns {{text:string, map:Object, entities:Array, counts:Object, sourceHash:string}}
 */
export function pseudonimizuj(text, opts = {}) {
    const pii = detect(text, opts).entities.filter((e) => e.isPii);
    const { out, map } = buildTokens(text, pii);
    return {
        text: out,
        map,
        entities: pii,
        counts: countByType(pii),
        sourceHash: sourceHash(text),
    };
}

/**
 * Anonimizacja NIEODWRACALNA. NIE zwraca mapy ani surowych wartosci -
 * nieodwracalnosc jest wymuszona na poziomie API (caller nie moze
 * przypadkiem zalogowac oryginalow).
 *
 * @param {string} text
 * @param {object} [opts]
 * @returns {{text:string, entities:Array, counts:Object, sourceHash:string}}
 */
export function anonimizuj(text, opts = {}) {
    const pii = detect(text, opts).entities.filter((e) => e.isPii);
    const { out } = buildTokens(text, pii);
    const redacted = pii.map(({ type, start, end, confidence, ruleId }) =>
        ({ type, start, end, confidence, ruleId }));
    return {
        text: out,
        entities: redacted,
        counts: countByType(pii),
        sourceHash: sourceHash(text),
    };
}

/**
 * Odwraca pseudonimizacje - podstawia oryginaly w miejsce tokenow.
 * `map` to obiekt { token: original } zwrocony przez pseudonimizuj().
 */
export function odwroc(text, map) {
    let out = text;
    const tokens = Object.keys(map).sort((a, b) => b.length - a.length);
    for (const token of tokens) out = out.split(token).join(map[token]);
    return out;
}
