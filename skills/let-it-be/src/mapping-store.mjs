// Magazyn map placeholder<->oryginal z TTL + szyfrowane archiwum.
//
// Cherry-pick patternow z gregmos/PII-Shield (MIT):
//   - pattern 1: TTL mapping cleanup (default 7 dni, configurable)
//   - pattern 2: source_hash per dokument (sha256) - audit-relevant
//   - pattern 4: AES-256-GCM archiwum (klucz scrypt) - transfer szyfrowany
//
// Mapa jest potrzebna TYLKO w trybie pseudonimizacji (odwracalnym).
// Tryb anonimizacji (nieodwracalny) mapy NIE zapisuje - to roznica RODO.

import { createHash, randomBytes, scryptSync, createCipheriv, createDecipheriv } from "node:crypto";
import { mkdir, writeFile, readFile, readdir, unlink } from "node:fs/promises";
import { join } from "node:path";

const DAY_MS = 24 * 60 * 60 * 1000;

/** sha256 dokumentu zrodlowego - "sha256:<hex>". */
export function sourceHash(input) {
    return "sha256:" + createHash("sha256").update(input).digest("hex");
}

/**
 * Magazyn map sesji z TTL. Kazda sesja = osobny plik JSON w `dir`.
 */
export class MappingStore {
    /**
     * @param {object} [opts]
     * @param {string} [opts.dir] katalog sesji. Domyslnie ./.let-it-be-sessions
     * @param {number} [opts.ttlMs] czas zycia mapy. Domyslnie 7 dni.
     * @param {() => Date} [opts.clock] wstrzykiwalny zegar (testy).
     */
    constructor(opts = {}) {
        this.dir = opts.dir ?? ".let-it-be-sessions";
        this.ttlMs = opts.ttlMs ?? 7 * DAY_MS;
        this.clock = opts.clock ?? (() => new Date());
    }

    #path(sessionId) {
        if (!/^[A-Za-z0-9_-]+$/.test(sessionId)) {
            throw new Error(`Niedozwolony sessionId: ${sessionId}`);
        }
        return join(this.dir, `${sessionId}.json`);
    }

    /** Zapisuje mape sesji. `map` to obiekt { token: original }. */
    async save(sessionId, { map, sourceHash: srcHash, entities }) {
        await mkdir(this.dir, { recursive: true });
        const now = this.clock();
        const record = {
            session_id: sessionId,
            source_hash: srcHash ?? null,
            entities: entities ?? {},
            created_at: now.toISOString(),
            expires_at: new Date(now.getTime() + this.ttlMs).toISOString(),
            map,
        };
        await writeFile(this.#path(sessionId), JSON.stringify(record, null, 2), "utf8");
        return record;
    }

    /** Wczytuje mape sesji. Zwraca null jezeli brak lub wygasla. */
    async load(sessionId) {
        let raw;
        try {
            raw = await readFile(this.#path(sessionId), "utf8");
        } catch {
            return null;
        }
        const record = JSON.parse(raw);
        if (new Date(record.expires_at).getTime() <= this.clock().getTime()) {
            return null;
        }
        return record;
    }

    /** Usuwa wygasle sesje. Zwraca liczbe usunietych. */
    async cleanup() {
        let files;
        try {
            files = await readdir(this.dir);
        } catch {
            return 0;
        }
        const now = this.clock().getTime();
        let removed = 0;
        for (const f of files) {
            if (!f.endsWith(".json")) continue;
            try {
                const record = JSON.parse(await readFile(join(this.dir, f), "utf8"));
                if (new Date(record.expires_at).getTime() <= now) {
                    await unlink(join(this.dir, f));
                    removed += 1;
                }
            } catch {
                // uszkodzony plik - pomijamy, nie blokujemy cleanup
            }
        }
        return removed;
    }
}

// --- Szyfrowane archiwum (AES-256-GCM, klucz scrypt) ---

const SALT_LEN = 16;
const IV_LEN = 12;
const KEY_LEN = 32;

/** Szyfruje obiekt haslem. Zwraca string base64-pakowanego archiwum. */
export function encryptArchive(obj, password) {
    const salt = randomBytes(SALT_LEN);
    const iv = randomBytes(IV_LEN);
    const key = scryptSync(password, salt, KEY_LEN);
    const cipher = createCipheriv("aes-256-gcm", key, iv);
    const plaintext = Buffer.from(JSON.stringify(obj), "utf8");
    const ciphertext = Buffer.concat([cipher.update(plaintext), cipher.final()]);
    const tag = cipher.getAuthTag();
    return JSON.stringify({
        v: 1,
        salt: salt.toString("base64"),
        iv: iv.toString("base64"),
        tag: tag.toString("base64"),
        data: ciphertext.toString("base64"),
    });
}

/** Deszyfruje archiwum haslem. Throws jezeli haslo zle lub dane naruszone. */
export function decryptArchive(blob, password) {
    const { salt, iv, tag, data } = JSON.parse(blob);
    const key = scryptSync(password, Buffer.from(salt, "base64"), KEY_LEN);
    const decipher = createDecipheriv("aes-256-gcm", key, Buffer.from(iv, "base64"));
    decipher.setAuthTag(Buffer.from(tag, "base64"));
    const plaintext = Buffer.concat([
        decipher.update(Buffer.from(data, "base64")),
        decipher.final(),
    ]);
    return JSON.parse(plaintext.toString("utf8"));
}
