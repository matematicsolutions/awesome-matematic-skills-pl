// Orchestrator detekcji: uruchamia reguly regex, rozwiazuje nakladajace
// sie spany (czego pl-entities NIE robil - tam detectAll zwracal konflikty
// "do rozwiazania w T2"). Tutaj rozwiazujemy je deterministycznie:
// wyzsze confidence wygrywa, przy remisie dluzszy span, potem wczesniejszy.

import { detectAll, PL_EXTRACTION_RULES } from "./regex.mjs";

/**
 * Typy traktowane jako dane osobowe (RODO) - tylko te sa domyslnie
 * podmieniane. Sygnatury orzeczen i aktow prawnych to informacja publiczna,
 * NIE dane osobowe - domyslnie zostaja w tekscie (mozna wlaczyc opcja).
 */
export const PII_TYPES = new Set([
    "PESEL", "NIP", "REGON", "KRS", "EMAIL", "PHONE", "OSOBA", "FIRMA",
    "IBAN", "DOWOD_OSOBISTY", "ADRES",
]);

const overlaps = (a, b) => a.start < b.end && b.start < a.end;

/** Rozwiazuje nakladajace sie dopasowania - zwraca rozlaczne, posortowane. */
function resolveOverlaps(matches) {
    const ranked = [...matches].sort((a, b) =>
        b.confidence - a.confidence ||
        (b.end - b.start) - (a.end - a.start) ||
        a.start - b.start,
    );
    const accepted = [];
    for (const m of ranked) {
        if (!accepted.some((a) => overlaps(a, m))) accepted.push(m);
    }
    return accepted.sort((a, b) => a.start - b.start);
}

/**
 * Wykrywa encje w tekscie i oznacza ktore sa danymi osobowymi.
 *
 * @param {string} text
 * @param {object} [opts]
 * @param {boolean} [opts.includeSignatures=false] traktuj sygnatury orzeczen
 *        i aktow jako podlegajace podmianie (domyslnie NIE - to nie PII).
 * @param {number}  [opts.minConfidence=0] odrzuc dopasowania ponizej progu
 *        (np. 0.8 zostawia tylko PESEL/NIP/REGON/IBAN/KRS/email/osoba).
 * @param {Array}  [opts.rules] niestandardowy zestaw regul.
 * @returns {{entities: Array}} encje rozlaczne, posortowane wg pozycji,
 *          kazda z polem `isPii`.
 */
export function detect(text, opts = {}) {
    const { includeSignatures = false, minConfidence = 0, rules = PL_EXTRACTION_RULES } = opts;
    const matches = detectAll(text, rules).filter((m) => m.confidence >= minConfidence);
    const resolved = resolveOverlaps(matches);
    const entities = resolved.map((m) => ({
        ...m,
        isPii: PII_TYPES.has(m.type) ||
            (includeSignatures && m.type.startsWith("SYGNATURA")),
    }));
    return { entities };
}

/** Liczniki encji per typ - dla audit logu i raportu. */
export function countByType(entities) {
    const counts = {};
    for (const e of entities) counts[e.type] = (counts[e.type] || 0) + 1;
    return counts;
}
