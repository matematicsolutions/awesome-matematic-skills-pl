// Audit log plain-text "proves no PII leaves" - dla Inspektora RODO.
//
// Cherry-pick patternu z gregmos/PII-Shield (MIT, pattern 5): osobny log
// w czytelnej formie, ktora Inspektor / kontroler kancelarii moze przeczytac
// bez deszyfrowania. AI Act art. 12 (record-keeping) + art. 13 wymagaja
// zrozumialych logow dla podmiotu wdrazajacego AI.
//
// Format linii (pipe-separated, sortowalny po timestamp):
//   2026-05-22T18:42:13.123Z | pseudonim-applied | doc_id=... | source_hash=sha256:... | entities={OSOBA:3,PESEL:1} | bytes_in=12450 | bytes_out=12180
//
// Walidacja krytyczna: appendLlmCallOut() RZUCA ResidualPIIError jezeli
// pseudonimizacja pominela ktorykolwiek "original" - LLM call ZATRZYMANY.
//
// Log NIE zawiera tresci ani wartosci PII - tylko liczniki, hashe, typy.

import { appendFile } from "node:fs/promises";

/**
 * Wyjatek gdy PII przecieklo do tekstu wyjsciowego. `.message` zawiera
 * WYLACZNIE licznik (bez wartosci) - bezpieczny do zalogowania. Wartosci
 * sa w `.samples` (do incident-only logu z restricted access).
 */
export class ResidualPIIError extends Error {
    constructor(piiCount, samples) {
        super(
            `Tekst zawiera ${piiCount} PII residual po przetworzeniu - operacja ZATRZYMANA. ` +
            `Wartosci dostepne w polu .samples (do incident-only log).`,
        );
        this.name = "ResidualPIIError";
        this.piiCount = piiCount;
        this.samples = samples;
    }
}

/** Originaly krotsze niz 2 znaki daja masowe false-positives (inicjaly). */
const MIN_ORIGINAL_LENGTH = 2;

/**
 * Sprawdza czy KAZDY `original` z mapy wystepuje w tekscie wynikowym.
 * Jezeli tak - podmiana go pominela i PII zostalo.
 *
 * @param {string} text tekst po podmianie.
 * @param {Iterable<string>} originals oryginalne wartosci PII.
 * @returns {{count:number, samples:string[]}}
 */
export function detectResidualPII(text, originals) {
    let count = 0;
    const samples = [];
    for (const original of originals) {
        if (original.length < MIN_ORIGINAL_LENGTH) continue;
        if (text.includes(original)) {
            count += 1;
            if (samples.length < 3) samples.push(original);
        }
    }
    return { count, samples };
}

function formatField(key, value) {
    if (value === undefined || value === null) return null;
    if (value instanceof Date) return `${key}=${value.toISOString()}`;
    if (key === "entities" && typeof value === "object") {
        const formatted = Object.entries(value).map(([k, v]) => `${k}:${v}`).join(",");
        return `${key}={${formatted}}`;
    }
    if (typeof value === "object") return `${key}=${JSON.stringify(value)}`;
    return `${key}=${String(value)}`;
}

const ORDERED_KEYS = [
    "doc_id", "source_hash", "mode", "entities",
    "bytes_in", "bytes_out", "pii_count", "removed_sessions", "expires_at",
];

/** Serializuje zdarzenie do linii audit logu. Eksportowany dla testow. */
export function formatAuditLine(timestamp, event) {
    const parts = [timestamp.toISOString(), event.event];
    for (const key of ORDERED_KEYS) {
        const formatted = formatField(key, event[key]);
        if (formatted !== null) parts.push(formatted);
    }
    return parts.join(" | ");
}

/**
 * Logger plain-text dla zdarzen anonimizacji/pseudonimizacji.
 *
 * Typy zdarzen (lista zamknieta):
 *   pseudonim-applied | anonimizacja-applied | pseudonim-reversed
 *   llm-call-out | mapping-stored | mapping-cleanup | archive-created
 */
export class AuditLog {
    constructor(logPath, clock = () => new Date()) {
        this.logPath = logPath;
        this.clock = clock;
    }

    /** Appenduje zdarzenie. Throws jezeli appendFile fails. */
    async append(event) {
        const line = formatAuditLine(this.clock(), event) + "\n";
        await appendFile(this.logPath, line, { encoding: "utf8" });
    }

    /**
     * Wariant krytyczny dla wyslania tekstu na zewnatrz (LLM / publikacja).
     * PRZED logowaniem waliduje ze tekst NIE zawiera zadnego oryginalu.
     * Jezeli zawiera - rzuca ResidualPIIError, log NIE zapisuje sukcesu.
     *
     * @param {string} outText tekst po podmianie, gotowy do wyslania.
     * @param {Iterable<string>} originals oryginalne wartosci PII.
     */
    async appendLlmCallOut(outText, originals) {
        const residual = detectResidualPII(outText, originals);
        if (residual.count > 0) throw new ResidualPIIError(residual.count, residual.samples);
        await this.append({
            event: "llm-call-out",
            bytes_out: Buffer.byteLength(outText, "utf8"),
            pii_count: 0,
        });
    }
}
