// Warstwa ODWRACALNEJ redakcji dla PACZKI dokumentow.
//
// Co dodaje ponad pseudonimizuj():
//   1. Stabilny placeholder per (kategoria, wartosc znormalizowana) w obrebie
//      CALEJ paczki - ten sam byt w pliku 1 i pliku 3 to ten sam [OSOBA_1].
//   2. Jednolita numeracja miedzy plikami - liczniki NIE resetuja sie per plik.
//   3. Slownik odwracania jako JSON sidecar (eksport/import) - numeracja
//      przezywa restart procesu: wczytany slownik kontynuuje od ostatniego
//      numeru, znane wartosci trzymaja stare placeholdery.
//
// Wzorce (pattern strukturalny, NIE kod - atrybucja THIRD_PARTY_INSPIRATIONS.md):
//   - Rizzo-AI-Academy/rizzo-pii (MIT): stabilny placeholder per (label,
//     wartosc znormalizowana) + lokalny slownik {placeholder -> wartosc}
//     z eksportem/importem JSON + zakladka Restore.
//   - moyupeng0422/legal-doc-redactor (MIT): batch z JEDNOLITA numeracja
//     miedzy plikami + mapping w sidecarze obok dokumentow.
//
// Granica governance: modul przygotowuje i przywraca LOKALNIE. Niczego sam
// nie wysyla - co idzie do LLM decyduje czlowiek.

import { detect, countByType } from "./detect.mjs";
import { sourceHash } from "./mapping-store.mjs";
import { odwroc } from "./pseudonimizuj.mjs";

export const SLOWNIK_FORMAT = "mapa-pii/1";

export const SLOWNIK_OSTRZEZENIE =
    "UWAGA: ten plik zawiera DANE OSOBOWE (oryginaly PII). Chron go jak akta " +
    "sprawy: nie wysylaj do LLM, nie commituj do repo, nie udostepniaj. " +
    "Utrata pliku = utrata mozliwosci odwrocenia pseudonimizacji.";

/**
 * Slownik odwracania paczki: placeholder <-> oryginal, stabilny per
 * (kategoria, wartosc znormalizowana), z jednolita numeracja.
 */
export class SlownikOdwracania {
    constructor() {
        /** @type {Map<string, {wartosc:string, kategoria:string, znormalizowana:string, wystapienia:number}>} */
        this.wpisy = new Map();
        /** klucz "KATEGORIA:znormalizowana" -> placeholder */
        this.placeholderByKey = new Map();
        /** kategoria -> najwyzszy przydzielony numer */
        this.liczniki = {};
        /** nazwa pliku -> source_hash (sha256) */
        this.pliki = {};
        this.createdAt = new Date().toISOString();
    }

    /**
     * Zwraca placeholder dla encji - istniejacy, jezeli (kategoria,
     * znormalizowana) juz widziane, inaczej nowy z kolejnym numerem.
     * Pierwsza napotkana forma surowa (raw) staje sie wartoscia odwracania.
     */
    przydziel(entity) {
        const key = `${entity.type}:${entity.normalized}`;
        let placeholder = this.placeholderByKey.get(key);
        if (!placeholder) {
            this.liczniki[entity.type] = (this.liczniki[entity.type] || 0) + 1;
            placeholder = `[${entity.type}_${this.liczniki[entity.type]}]`;
            this.placeholderByKey.set(key, placeholder);
            this.wpisy.set(placeholder, {
                wartosc: entity.raw,
                kategoria: entity.type,
                znormalizowana: entity.normalized,
                wystapienia: 0,
            });
        }
        this.wpisy.get(placeholder).wystapienia += 1;
        return placeholder;
    }

    /** Mapa { placeholder: oryginal } - wejscie dla odwroc(). */
    mapaOdwracania() {
        const map = {};
        for (const [placeholder, wpis] of this.wpisy) map[placeholder] = wpis.wartosc;
        return map;
    }

    /** Wszystkie oryginaly (do bramki residual). */
    oryginaly() {
        return [...this.wpisy.values()].map((w) => w.wartosc);
    }

    /** Eksport do JSON (sidecar *.mapa-pii.json). */
    toJSON() {
        const wpisy = {};
        for (const [placeholder, w] of this.wpisy) wpisy[placeholder] = { ...w };
        return {
            format: SLOWNIK_FORMAT,
            ostrzezenie: SLOWNIK_OSTRZEZENIE,
            created_at: this.createdAt,
            updated_at: new Date().toISOString(),
            liczniki: { ...this.liczniki },
            pliki: { ...this.pliki },
            wpisy,
        };
    }

    /**
     * Import z JSON - kontynuuje numeracje po restarcie. Liczniki sa
     * odtwarzane takze z sufiksow placeholderow, gdyby pole `liczniki`
     * bylo niepelne lub usuniete.
     */
    static fromJSON(obj) {
        if (!obj || obj.format !== SLOWNIK_FORMAT) {
            throw new Error(`Nieznany format slownika (oczekiwano "${SLOWNIK_FORMAT}").`);
        }
        const slownik = new SlownikOdwracania();
        slownik.createdAt = obj.created_at ?? slownik.createdAt;
        slownik.liczniki = { ...(obj.liczniki ?? {}) };
        slownik.pliki = { ...(obj.pliki ?? {}) };
        for (const [placeholder, w] of Object.entries(obj.wpisy ?? {})) {
            if (!w || typeof w.wartosc !== "string" || typeof w.kategoria !== "string") {
                throw new Error(`Uszkodzony wpis slownika: ${placeholder}`);
            }
            slownik.wpisy.set(placeholder, {
                wartosc: w.wartosc,
                kategoria: w.kategoria,
                znormalizowana: w.znormalizowana ?? w.wartosc,
                wystapienia: w.wystapienia ?? 0,
            });
            slownik.placeholderByKey.set(`${w.kategoria}:${w.znormalizowana ?? w.wartosc}`, placeholder);
            const m = new RegExp(`^\\[${w.kategoria}_(\\d+)\\]$`).exec(placeholder);
            if (m) {
                const n = Number(m[1]);
                if (n > (slownik.liczniki[w.kategoria] || 0)) slownik.liczniki[w.kategoria] = n;
            }
        }
        return slownik;
    }
}

/**
 * Pseudonimizuje paczke dokumentow z jednolita numeracja.
 *
 * @param {Array<{nazwa:string, text:string}>} pliki
 * @param {object} [opts] opcje detect() (includeSignatures, minConfidence)
 *        plus `slownik` - istniejacy SlownikOdwracania do kontynuacji.
 * @returns {{wyniki: Array<{nazwa:string, text:string, counts:Object, sourceHash:string}>, slownik: SlownikOdwracania}}
 */
export function pseudonimizujPaczke(pliki, opts = {}) {
    const { slownik = new SlownikOdwracania(), ...detectOpts } = opts;
    const wyniki = [];
    for (const { nazwa, text } of pliki) {
        const pii = detect(text, detectOpts).entities.filter((e) => e.isPii);
        let out = "";
        let cursor = 0;
        for (const e of pii) {
            out += text.slice(cursor, e.start) + slownik.przydziel(e);
            cursor = e.end;
        }
        out += text.slice(cursor);
        const hash = sourceHash(text);
        slownik.pliki[nazwa] = hash;
        wyniki.push({ nazwa, text: out, counts: countByType(pii), sourceHash: hash });
    }
    return { wyniki, slownik };
}

/**
 * Przywraca oryginaly w tekscie (np. odpowiedzi LLM) ze slownika paczki.
 * Przyjmuje SlownikOdwracania albo sparsowany JSON sidecara.
 *
 * @param {string} text tekst z placeholderami.
 * @param {SlownikOdwracania|object} slownik
 * @returns {{text:string, nieznanePlaceholdery:string[]}} tekst po
 *          przywroceniu + placeholdery, ktorych slownik nie zna (np. z innej
 *          paczki albo zmyslone przez model - do recznej weryfikacji).
 */
export function przywroc(text, slownik) {
    const s = slownik instanceof SlownikOdwracania ? slownik : SlownikOdwracania.fromJSON(slownik);
    const out = odwroc(text, s.mapaOdwracania());
    const kategorie = new Set([...s.wpisy.values()].map((w) => w.kategoria));
    const nieznane = new Set();
    for (const m of out.matchAll(/\[([A-Z][A-Z_]*)_(\d+)\]/g)) {
        if (kategorie.has(m[1])) nieznane.add(m[0]);
    }
    return { text: out, nieznanePlaceholdery: [...nieznane].sort() };
}
