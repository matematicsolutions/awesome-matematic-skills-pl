import { test } from "node:test";
import assert from "node:assert/strict";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { mkdtemp, rm, readFile } from "node:fs/promises";
import {
    isValidPesel, isValidNip, isValidRegon, isValidIbanPl, isValidDowodOsobisty,
    detect, pseudonimizuj, anonimizuj, odwroc,
    detectResidualPII, ResidualPIIError, AuditLog, formatAuditLine,
    MappingStore, sourceHash, encryptArchive, decryptArchive,
} from "../src/index.mjs";

// Syntetyczne, poprawne checksumowo wartosci testowe (nie sa niczyimi danymi).
const PESEL = "44051401359";
const NIP = "5260250274";
const REGON = "123456785";

test("checksumy: poprawne wartosci przechodza", () => {
    assert.ok(isValidPesel(PESEL));
    assert.ok(isValidNip(NIP));
    assert.ok(isValidRegon(REGON));
});

test("checksumy: bledne wartosci odrzucone", () => {
    assert.ok(!isValidPesel("44051401358"));
    assert.ok(!isValidNip("5260250275"));
    assert.ok(!isValidRegon("123456784"));
    assert.ok(!isValidPesel("123"));
});

test("detect: wykrywa PESEL/NIP/REGON/email/osoba", () => {
    const text = `Jan Kowalski, PESEL ${PESEL}, NIP ${NIP}, REGON ${REGON}, jan@kancelaria.pl`;
    const pii = detect(text).entities.filter((e) => e.isPii);
    const types = new Set(pii.map((e) => e.type));
    assert.ok(types.has("PESEL"));
    assert.ok(types.has("NIP"));
    assert.ok(types.has("REGON"));
    assert.ok(types.has("EMAIL"));
    assert.ok(types.has("OSOBA"));
});

test("checksumy: IBAN PL i dowod osobisty", () => {
    assert.ok(isValidIbanPl("PL61109010140000071219812874"));
    assert.ok(isValidIbanPl("PL61 1090 1014 0000 0712 1981 2874"));
    assert.ok(!isValidIbanPl("PL61109010140000071219812875"));
    assert.ok(isValidDowodOsobisty("ABA300000"));
    assert.ok(!isValidDowodOsobisty("ABA300001"));
});

test("detect: IBAN, dowod osobisty, adres", () => {
    const text = "Konto PL61 1090 1014 0000 0712 1981 2874, dowod ABA300000, ul. Marszalkowska 12/3, 00-950 Warszawa.";
    const types = new Set(detect(text).entities.filter((e) => e.isPii).map((e) => e.type));
    assert.ok(types.has("IBAN"));
    assert.ok(types.has("DOWOD_OSOBISTY"));
    assert.ok(types.has("ADRES"));
});

test("detect: minConfidence odsiewa slabe dopasowania", () => {
    const text = `PESEL ${PESEL}, Przyklad Sp. z o.o.`;
    const wszystkie = detect(text).entities.filter((e) => e.isPii).map((e) => e.type);
    const tylkoMocne = detect(text, { minConfidence: 1.0 }).entities.filter((e) => e.isPii).map((e) => e.type);
    assert.ok(wszystkie.includes("FIRMA"));   // 0.75
    assert.ok(!tylkoMocne.includes("FIRMA")); // odsiane progiem 1.0
    assert.ok(tylkoMocne.includes("PESEL"));  // 1.0 zostaje
});

test("detect: telefon z prefiksem +48 i bez", () => {
    const a = detect("tel +48 600 700 800").entities.filter((e) => e.type === "PHONE");
    const b = detect("tel 600700800").entities.filter((e) => e.type === "PHONE");
    assert.equal(a.length, 1);
    assert.equal(b.length, 1);
    assert.equal(a[0].normalized, "600700800");
});

test("detect: sygnatury domyslnie NIE sa PII, z opcja sa", () => {
    const text = "Wyrok II FSK 1234/22 oraz K 12/19.";
    const bez = detect(text).entities.filter((e) => e.isPii);
    assert.equal(bez.length, 0);
    const z = detect(text, { includeSignatures: true }).entities.filter((e) => e.isPii);
    assert.ok(z.length >= 1);
});

test("detect: nakladajace sie spany rozwiazane (PESEL > telefon)", () => {
    const { entities } = detect(`PESEL ${PESEL}`);
    const pesel = entities.find((e) => e.type === "PESEL");
    assert.ok(pesel);
    // zaden inny PII nie nachodzi na span PESEL
    const nakladajace = entities.filter(
        (e) => e !== pesel && e.start < pesel.end && pesel.start < e.end,
    );
    assert.equal(nakladajace.length, 0);
});

test("pseudonimizuj + odwroc: round-trip odtwarza oryginal", () => {
    const text = `Powod Jan Kowalski (PESEL ${PESEL}) kontakt jan@kancelaria.pl tel +48 600 700 800.`;
    const res = pseudonimizuj(text);
    assert.notEqual(res.text, text);
    assert.ok(!res.text.includes(PESEL));
    assert.ok(res.text.includes("[PESEL_1]"));
    assert.equal(odwroc(res.text, res.map), text);
});

test("pseudonimizuj: korreferencja - ten sam oryginal ten sam token", () => {
    const text = `Jan Kowalski zlozyl pozew. Jan Kowalski wygral.`;
    const res = pseudonimizuj(text);
    const count = (res.text.match(/\[OSOBA_1\]/g) || []).length;
    assert.equal(count, 2);
    assert.ok(!res.text.includes("[OSOBA_2]"));
});

test("anonimizuj: nieodwracalne - brak mapy i surowych wartosci w API", () => {
    const text = `Anna Nowak, PESEL ${PESEL}.`;
    const res = anonimizuj(text);
    assert.equal(res.map, undefined);
    assert.ok(!res.text.includes(PESEL));
    for (const e of res.entities) {
        assert.equal(e.raw, undefined);
        assert.equal(e.normalized, undefined);
    }
});

test("residual gate: wykrywa pozostawione PII", () => {
    const { count, samples } = detectResidualPII(`zostal ${PESEL} w tekscie`, [PESEL]);
    assert.equal(count, 1);
    assert.deepEqual(samples, [PESEL]);
});

test("residual gate: ResidualPIIError nie ujawnia wartosci w .message", () => {
    const err = new ResidualPIIError(1, [PESEL]);
    assert.ok(!err.message.includes(PESEL));
    assert.deepEqual(err.samples, [PESEL]);
});

test("AuditLog.appendLlmCallOut rzuca gdy PII zostalo", async () => {
    const dir = await mkdtemp(join(tmpdir(), "lib-"));
    const log = new AuditLog(join(dir, "audit.log"));
    await assert.rejects(
        () => log.appendLlmCallOut(`tekst ${PESEL}`, [PESEL]),
        ResidualPIIError,
    );
    await rm(dir, { recursive: true, force: true });
});

test("AuditLog: format linii czytelny i bez wartosci PII", async () => {
    const line = formatAuditLine(new Date("2026-05-22T10:00:00Z"), {
        event: "pseudonim-applied", source_hash: "sha256:abc",
        entities: { OSOBA: 2, PESEL: 1 }, bytes_in: 100, bytes_out: 90,
    });
    assert.ok(line.includes("pseudonim-applied"));
    assert.ok(line.includes("entities={OSOBA:2,PESEL:1}"));
    assert.ok(line.startsWith("2026-05-22T10:00:00.000Z"));
});

test("sourceHash: deterministyczny sha256", () => {
    assert.equal(sourceHash("abc"), sourceHash("abc"));
    assert.ok(sourceHash("abc").startsWith("sha256:"));
    assert.notEqual(sourceHash("abc"), sourceHash("abd"));
});

test("MappingStore: save/load + TTL wygasanie", async () => {
    const dir = await mkdtemp(join(tmpdir(), "store-"));
    let now = new Date("2026-05-22T10:00:00Z");
    const store = new MappingStore({ dir, ttlMs: 1000, clock: () => now });
    await store.save("sesja1", { map: { "[OSOBA_1]": "Jan Kowalski" }, sourceHash: "sha256:x" });
    assert.ok(await store.load("sesja1"));
    now = new Date("2026-05-22T10:00:02Z"); // po TTL
    assert.equal(await store.load("sesja1"), null);
    await rm(dir, { recursive: true, force: true });
});

test("MappingStore: cleanup usuwa wygasle", async () => {
    const dir = await mkdtemp(join(tmpdir(), "store-"));
    let now = new Date("2026-05-22T10:00:00Z");
    const store = new MappingStore({ dir, ttlMs: 1000, clock: () => now });
    await store.save("a", { map: {} });
    await store.save("b", { map: {} });
    now = new Date("2026-05-22T10:00:05Z");
    assert.equal(await store.cleanup(), 2);
    await rm(dir, { recursive: true, force: true });
});

test("MappingStore: odrzuca niebezpieczny sessionId", async () => {
    const store = new MappingStore({ dir: tmpdir() });
    await assert.rejects(() => store.save("../etc/passwd", { map: {} }));
});

test("archiwum AES-GCM: round-trip + zle haslo rzuca", () => {
    const obj = { map: { "[OSOBA_1]": "Jan Kowalski" } };
    const blob = encryptArchive(obj, "tajne-haslo");
    assert.ok(!blob.includes("Kowalski"));
    assert.deepEqual(decryptArchive(blob, "tajne-haslo"), obj);
    assert.throws(() => decryptArchive(blob, "zle-haslo"));
});
