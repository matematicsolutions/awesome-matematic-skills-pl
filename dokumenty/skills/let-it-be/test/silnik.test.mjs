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

test("detect: PESEL/NIP/REGON z etykieta i ZLA suma ida do przegladu, nie do kosza", () => {
    // Literowka albo blad OCR w numerze z etykieta nie moze oznaczac, ze dana wychodzi jawna.
    const text = "PESEL 44051401358, NIP: 526-025-02-75, REGON 123456784.";
    const pii = detect(text).entities.filter((e) => e.isPii);
    const wg = (t) => pii.find((e) => e.type === t);
    for (const [typ, regula] of [["PESEL", "pesel-zla-suma"], ["NIP", "nip-zla-suma"], ["REGON", "regon-zla-suma"]]) {
        const e = wg(typ);
        assert.ok(e, `${typ} ze zla suma zgubiony`);
        assert.equal(e.ruleId, regula);
        assert.equal(e.confidence, 0.9);
    }
    const { text: wynik } = pseudonimizuj(text);
    for (const surowe of ["44051401358", "526-025-02-75", "123456784"]) {
        assert.ok(!wynik.includes(surowe), `${surowe} zostal jawny`);
    }
});

test("detect: poprawny numer z etykieta raz, z pelna pewnoscia (bez duplikatu z regula zlej sumy)", () => {
    const pesele = detect(`PESEL ${PESEL}`).entities.filter((e) => e.type === "PESEL");
    assert.equal(pesele.length, 1);
    assert.equal(pesele[0].ruleId, "pesel");
    assert.equal(pesele[0].confidence, 1.0);
});

test("detect: 11 cyfr ze zla suma BEZ etykiety nie sa PESEL (granica reguly)", () => {
    const pii = detect("Faktura nr 44051401358 z dnia 1 marca.").entities.filter((e) => e.type === "PESEL");
    assert.equal(pii.length, 0);
});

test("detect: NIP w zapisie 123-45-67-890 wykryty", () => {
    const nip = detect("NIP 526-02-50-274").entities.filter((e) => e.type === "NIP");
    assert.equal(nip.length, 1);
    assert.equal(nip[0].ruleId, "nip");
    assert.equal(nip[0].normalized, NIP);
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

test("OSOBA: polskie wielkie litery i pelne nazwisko z diakrytykami", () => {
    const osoby = (t) => detect(t).entities.filter((e) => e.type === "OSOBA").map((e) => e.raw);
    assert.deepEqual(osoby("Świadek Łukasz Nowak zeznał."), ["Łukasz Nowak"]);
    assert.deepEqual(osoby("Pani Zofia Żółkiewska wniosła."), ["Zofia Żółkiewska"]);
    assert.deepEqual(osoby("Sławomir Ścibor-Rylski"), ["Sławomir Ścibor-Rylski"]);
    assert.deepEqual(osoby("Jan Łoś podpisał."), ["Jan Łoś"]);
    assert.deepEqual(osoby("Anna Kość podpisała."), ["Anna Kość"]);
});

test("OSOBA: odrzucona para nie zjada imienia nastepnej osoby", () => {
    const osoby = (t) => detect(t).entities.filter((e) => e.type === "OSOBA").map((e) => e.raw);
    assert.deepEqual(
        osoby("Wnioskodawca Anna Nowak oraz Pozwany Jan Kowalski"),
        ["Anna Nowak", "Jan Kowalski"],
    );
    // Kontrola negatywna: bez znanego imienia nadal nic.
    assert.deepEqual(osoby("Sad Okregowy Wydzial Cywilny"), []);
});

test("wejscie NFD: detekcja jak dla NFC, zero przecieku po anonimizacji", () => {
    const nfc = "Pani Zofia Żółkiewska, ul. Świętojańska 12, PESEL 44051401359.";
    const nfd = nfc.normalize("NFD");
    assert.notEqual(nfd, nfc);
    const typy = (t) => detect(t).entities.filter((e) => e.isPii).map((e) => e.type).sort();
    assert.deepEqual(typy(nfd), typy(nfc));
    const out = anonimizuj(nfd).text;
    for (const oryginal of ["Żółkiewska", "Świętojańska"]) {
        assert.ok(!out.includes(oryginal) && !out.includes(oryginal.normalize("NFD")), oryginal);
    }
    // Offsety odnosza sie do tekstu zwroconego przez detect().
    const { entities, text } = detect(nfd);
    for (const e of entities) assert.equal(text.slice(e.start, e.end), e.raw);
});

// --- Propagacja osoby na dalsze wystapienia nazwiska (src/propaguj.mjs) ---

const osobyWykryte = (t) => detect(t).entities.filter((e) => e.type === "OSOBA").map((e) => e.raw);

test("odmiana nazwiska po pierwszym przedstawieniu osoby", () => {
    const t = "Powodka Anna Zielińska wniosła pozew. Zdaniem Zielińskiej umowa wygasła, a Zielińska zażądała zwrotu.";
    assert.deepEqual(osobyWykryte(t), ["Anna Zielińska", "Zielińskiej", "Zielińska"]);
});

test("nazwiska rzeczownikowe z e ruchomym i -owicz", () => {
    const t = "Świadek Jan Wróbel zeznał. Wróbla przesłuchano ponownie. Pozwany Adam Kaczmarek i Tomasz Adamowicz. Kaczmarkowi doręczono, Adamowicza wezwano.";
    const o = osobyWykryte(t);
    for (const f of ["Wróbla", "Kaczmarkowi", "Adamowicza"]) assert.ok(o.includes(f), f);
});

test("wersaliki i brak ogonków po OCR", () => {
    const t = "Pozwana Joanna Kowalska. W komparycji: KOWALSKA. Po OCR: Kowalskiej bez ogonkow, Kowalska.";
    const o = osobyWykryte(t);
    assert.ok(o.includes("KOWALSKA"));
    assert.ok(o.includes("Kowalskiej"));
});

test("nazwisko dwuczłonowe", () => {
    const t = "Pełnomocnik Maria Nowak-Zielińska. Nowak-Zielińskiej udzielono głosu.";
    assert.ok(osobyWykryte(t).includes("Nowak-Zielińskiej"));
});

test("kontrola negatywna: sygnatury, sądy, przepisy i słowa o innym rdzeniu nietknięte", () => {
    const t = "Anna Zielińska, sygn. akt I C 123/24, art. 415 k.c. Sąd Okręgowy w Zielonej Górze. Zielony pojazd.";
    assert.deepEqual(osobyWykryte(t), ["Anna Zielińska"]);
});

test("bez wykrytej osoby nie ma propagacji (nie zgadujemy nazwisk)", () => {
    assert.deepEqual(osobyWykryte("Zielińska wniosła pozew."), []);
});

test("odmiany nie przeciekają po anonimizacji, a pseudonimizacja odwraca się co do znaku", () => {
    const t = "Powód Jan Kowalski. Kowalskiego reprezentuje adwokat. KOWALSKI podpisał.";
    const a = anonimizuj(t).text;
    for (const f of ["Kowalski", "Kowalskiego", "KOWALSKI"]) assert.ok(!a.includes(f), f);
    const p = pseudonimizuj(t);
    assert.equal(odwroc(p.text, p.map), t);
});

test("imię w odmianie rozpoznaje osobę, a za nią dalsze wystąpienia nazwiska", () => {
    const t = "W imieniu powódki Anny Zielińskiej wnoszę o zasądzenie. Pozwanemu Janowi Kowalskiemu doręczono odpis, a Kowalski nie odpowiedział.";
    const o = osobyWykryte(t);
    for (const f of ["Anny Zielińskiej", "Janowi Kowalskiemu", "Kowalski"]) assert.ok(o.includes(f), f);
});

test("nazwisko rzeczownikowe w odmianie przy pierwszym wystąpieniu", () => {
    const t = "Umowę zawarto z Pawłem Nowakiem. Nowak nie zapłacił, więc Nowaka wezwano.";
    const o = osobyWykryte(t);
    for (const f of ["Pawłem Nowakiem", "Nowak", "Nowaka"]) assert.ok(o.includes(f), f);
});

test("odwrócona kolejność w tabeli: Nazwisko Imię", () => {
    assert.ok(osobyWykryte("Lp. 1 | Kowalczyk Jan | ul. Polna 5").includes("Kowalczyk Jan"));
    // dalsze wystąpienie nazwiska z tabeli też maskowane
    assert.ok(osobyWykryte("Kowalczyk Jan, 1980. Kowalczykowi doręczono wezwanie.").includes("Kowalczykowi"));
});

test("komparycja wersalikami i dwa imiona", () => {
    assert.ok(osobyWykryte("JAN KOWALCZYK, zamieszkały w Łodzi.").includes("JAN KOWALCZYK"));
    assert.ok(osobyWykryte("Stawiła się Anna Maria Nowak, legitymująca się dowodem.").includes("Anna Maria Nowak"));
    assert.ok(osobyWykryte("ANNA MARIA NOWAK oraz Nowak podpisali.").includes("Nowak"));
});

test("kontrola negatywna dla wersalików i tabel: tytuły i nagłówki nietknięte", () => {
    assert.deepEqual(osobyWykryte("UMOWA SPRZEDAŻY. PROTOKÓŁ ZGROMADZENIA WSPÓLNIKÓW. Imię Nazwisko | Adres"), []);
    assert.deepEqual(osobyWykryte("Sąd Okręgowy w Łodzi, Wydział Cywilny. Kodeks Pracy."), []);
});

test("odwrócona kolejność tylko w kontekście tabeli, nie na początku zdania", () => {
    assert.deepEqual(osobyWykryte("Pozwany Jan zeznał, że nie pamięta."), []);
    assert.deepEqual(osobyWykryte("Świadek Anna odmówiła odpowiedzi."), []);
});

// --- Firmy: formy prawne w każdej wielkości liter i pełnym brzmieniu ---

const firmyWykryte = (t) => detect(t).entities.filter((e) => e.type === "FIRMA").map((e) => e.raw);

test("forma prawna małymi literami, wersalikami i pełnym brzmieniem", () => {
    assert.deepEqual(firmyWykryte("Dostawca: Termika Wschód sp. z o.o. z siedzibą w Lublinie."), ["Termika Wschód sp. z o.o."]);
    assert.deepEqual(firmyWykryte("ORLIK TRANSPORT SP. Z O.O. wezwał dłużnika."), ["ORLIK TRANSPORT SP. Z O.O."]);
    assert.deepEqual(firmyWykryte("Zawarta z Baltic Freight Solutions spółką z ograniczoną odpowiedzialnością."), ["Baltic Freight Solutions spółką z ograniczoną odpowiedzialnością"]);
    assert.deepEqual(firmyWykryte("Kancelaria Nowicki Zawadzka Adwokaci spółka partnerska."), ["Kancelaria Nowicki Zawadzka Adwokaci spółka partnerska"]);
    assert.deepEqual(firmyWykryte("Hurtownia „Cegiełka” Dudek i Syn s.c. wystawiła fakturę."), ["Hurtownia „Cegiełka” Dudek i Syn s.c."]);
    assert.deepEqual(firmyWykryte("AGROMEX-BIS sp. z o.o. sp.k. jest wierzycielem."), ["AGROMEX-BIS sp. z o.o. sp.k."]);
});

test("firma: tytuł w linii wyżej i słowo strony nie wchodzą do nazwy", () => {
    assert.deepEqual(firmyWykryte("ZESTAWIENIE WIERZYTELNOŚCI\nprzysługujących Zielony Młyn S.A."), ["Zielony Młyn S.A."]);
    assert.deepEqual(firmyWykryte("Pozwana Termika Wschód sp. z o.o. wniosła odpowiedź."), ["Termika Wschód sp. z o.o."]);
    assert.deepEqual(firmyWykryte("Spółka z ograniczoną odpowiedzialnością jest formą prawną."), []);
});

test("firma: tytuł dokumentu z formą prawną to nie firma", () => {
    assert.deepEqual(firmyWykryte("UMOWA SPÓŁKI Z OGRANICZONĄ ODPOWIEDZIALNOŚCIĄ"), []);
    assert.deepEqual(firmyWykryte("Statut spółki akcyjnej oraz uchwała spółki jawnej."), []);
});

test("firma: dalsze wystąpienia nazwy bez formy prawnej, także w odmianie", () => {
    const f = firmyWykryte("Termika Wschód sp. z o.o. wezwała dłużnika. Termika żąda zapłaty, a pełnomocnik Termiki odpowie. TERMIKA WSCHÓD też.");
    for (const x of ["Termika", "Termiki", "TERMIKA WSCHÓD"]) assert.ok(f.includes(x), x);
    const g = firmyWykryte("SoftPol Systems S.A. i Agrolux sp. j. Umowa z SoftPolem i dostawa od Agroluxu.");
    for (const x of ["SoftPolem", "Agroluxu"]) assert.ok(g.includes(x), x);
});

test("firma: forma mieszana i organizacje bez formy prawnej", () => {
    assert.ok(firmyWykryte("Centrum Logistyczne Wola spółka z o.o. wynajmuje.").includes("Centrum Logistyczne Wola spółka z o.o."));
    assert.ok(firmyWykryte("Darczyńcą jest Fundacja Rozwoju Przedsiębiorczości „Kompas”.").some((x) => x.startsWith("Fundacja Rozwoju")));
    assert.ok(firmyWykryte("Członkiem jest Stowarzyszenie Kupców Rynku Jeżyckiego.").includes("Stowarzyszenie Kupców Rynku Jeżyckiego"));
});

test("firma: rzeczownik ogólny z nazwy spółki nie jest maskowany wszędzie", () => {
    const f = firmyWykryte("Centrum Logistyczne Wola sp. z o.o. Centrum miasta jest zakorkowane.");
    assert.ok(!f.includes("Centrum"));
    assert.deepEqual(firmyWykryte("Fundacja to forma prawna. Stowarzyszenie ma członków."), []);
});
