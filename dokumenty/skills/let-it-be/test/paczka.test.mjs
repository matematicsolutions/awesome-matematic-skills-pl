// Testy warstwy ODWRACALNEJ redakcji paczki (src/paczka.mjs) + CLI.
//
// Wszystkie PII w testach sa SYNTETYCZNE: wartosci przechodza checksume
// urzedowa, ale nie naleza do zadnej realnej osoby ani firmy.

import test from "node:test";
import assert from "node:assert/strict";
import { mkdtemp, readFile, writeFile, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { fileURLToPath } from "node:url";

import {
    SlownikOdwracania, pseudonimizujPaczke, przywroc,
    SLOWNIK_FORMAT, SLOWNIK_OSTRZEZENIE,
} from "../src/paczka.mjs";

const execFileAsync = promisify(execFile);
const CLI = fileURLToPath(new URL("../bin/cli.mjs", import.meta.url));

// Syntetyczne, checksumowo poprawne, fikcyjne:
const PESEL = "44051401359";
const NIP = "5260250274";

// Uwaga na fixture: OSOBA_RE wymaga, zeby przed imieniem NIE stalo inne slowo
// z wielkiej litery ("Powod Jan Kowalski" polknie "Powod Jan" i odrzuci) -
// to znane ograniczenie detekcji v0.1.0, nie tej warstwy.
const PLIK_1 = `Pozew wniosl Jan Kowalski (PESEL ${PESEL}). Pelnomocnik pisze, ze Jan Kowalski zada zaplaty.`;
const PLIK_2 = `Zeznala swiadek Anna Nowak, ze Jan Kowalski (NIP ${NIP}) prowadzil biuro.`;

function paczkaDwochPlikow(opts = {}) {
    return pseudonimizujPaczke([
        { nazwa: "pozew.txt", text: PLIK_1 },
        { nazwa: "zeznanie.txt", text: PLIK_2 },
    ], opts);
}

test("paczka: ten sam byt = ten sam placeholder w KAZDYM pliku", () => {
    const { wyniki } = paczkaDwochPlikow();
    assert.ok(wyniki[0].text.includes("[OSOBA_1]"));
    assert.ok(wyniki[1].text.includes("[OSOBA_1]"), "Jan Kowalski w pliku 2 musi byc tym samym [OSOBA_1]");
    assert.ok(!wyniki[0].text.includes(PESEL));
    assert.ok(!wyniki[1].text.includes(NIP));
});

test("paczka: jednolita numeracja - licznik NIE resetuje sie per plik", () => {
    const { wyniki } = paczkaDwochPlikow();
    // Anna Nowak pojawia sie dopiero w pliku 2 - dostaje NASTEPNY numer,
    // nie [OSOBA_1] od nowa.
    assert.ok(wyniki[1].text.includes("[OSOBA_2]"));
});

test("paczka: determinizm - dwa przebiegi daja identyczne wyniki", () => {
    const a = paczkaDwochPlikow();
    const b = paczkaDwochPlikow();
    assert.equal(a.wyniki[0].text, b.wyniki[0].text);
    assert.equal(a.wyniki[1].text, b.wyniki[1].text);
    assert.deepEqual(a.slownik.mapaOdwracania(), b.slownik.mapaOdwracania());
});

test("paczka: roundtrip - przywroc(pseudonimizowany) == oryginal", () => {
    const { wyniki, slownik } = paczkaDwochPlikow();
    assert.equal(przywroc(wyniki[0].text, slownik).text, PLIK_1);
    assert.equal(przywroc(wyniki[1].text, slownik).text, PLIK_2);
});

test("paczka: PESEL i NIP z checksuma trafiaja do slownika z kategoria", () => {
    const { slownik } = paczkaDwochPlikow();
    const wpisy = [...slownik.wpisy.values()];
    const pesel = wpisy.find((w) => w.kategoria === "PESEL");
    const nip = wpisy.find((w) => w.kategoria === "NIP");
    assert.equal(pesel.wartosc, PESEL);
    assert.equal(nip.wartosc, NIP);
    assert.ok(pesel.wystapienia >= 1);
});

test("slownik: eksport JSON ma format, ostrzezenie i hashe plikow", () => {
    const { slownik } = paczkaDwochPlikow();
    const json = slownik.toJSON();
    assert.equal(json.format, SLOWNIK_FORMAT);
    assert.equal(json.ostrzezenie, SLOWNIK_OSTRZEZENIE);
    assert.ok(json.pliki["pozew.txt"].startsWith("sha256:"));
    assert.ok(Object.keys(json.wpisy).length >= 3); // OSOBA x2 + PESEL + NIP
});

test("slownik: import kontynuuje numeracje po restarcie", () => {
    const pierwsza = paczkaDwochPlikow();
    const odtworzony = SlownikOdwracania.fromJSON(
        JSON.parse(JSON.stringify(pierwsza.slownik.toJSON())),
    );
    const { wyniki } = pseudonimizujPaczke(
        [{ nazwa: "aneks.txt", text: "Jan Kowalski spotkal sie, a Piotr Wisniewski podpisal aneks." }],
        { slownik: odtworzony },
    );
    // znana wartosc trzyma stary placeholder, nowa dostaje kolejny numer
    assert.ok(wyniki[0].text.includes("[OSOBA_1]"));
    assert.ok(wyniki[0].text.includes("[OSOBA_3]"));
    assert.ok(!wyniki[0].text.match(/\[OSOBA_1\].*\[OSOBA_2\]/s), "Piotr nie moze dostac numeru Anny");
});

test("slownik: fromJSON odtwarza liczniki z sufiksow placeholderow", () => {
    const json = paczkaDwochPlikow().slownik.toJSON();
    delete json.liczniki; // symulacja recznie edytowanego / okrojonego sidecara
    const s = SlownikOdwracania.fromJSON(json);
    assert.equal(s.liczniki.OSOBA, 2);
    assert.equal(s.liczniki.PESEL, 1);
});

test("slownik: fromJSON odrzuca nieznany format", () => {
    assert.throws(() => SlownikOdwracania.fromJSON({ format: "cos-innego" }), /Nieznany format/);
});

test("przywroc: raportuje placeholdery spoza slownika (halucynacja modelu)", () => {
    const { slownik } = paczkaDwochPlikow();
    const odpowiedzLlm = "Pelnomocnik [OSOBA_1] oraz [OSOBA_9] zawarli ugode.";
    const wynik = przywroc(odpowiedzLlm, slownik);
    assert.ok(wynik.text.includes("Jan Kowalski"));
    assert.deepEqual(wynik.nieznanePlaceholdery, ["[OSOBA_9]"]);
});

test("CLI paczka + przywroc: roundtrip przez pliki i restart procesu", async () => {
    const dir = await mkdtemp(join(tmpdir(), "let-it-be-paczka-"));
    try {
        const p1 = join(dir, "pozew.txt");
        const p2 = join(dir, "zeznanie.txt");
        const slownikPath = join(dir, "sprawa.mapa-pii.json");
        await writeFile(p1, PLIK_1, "utf8");
        await writeFile(p2, PLIK_2, "utf8");

        // bieg 1: dwa pliki na raz
        await execFileAsync(process.execPath, [CLI, "paczka", p1, p2, "--slownik", slownikPath]);
        const pseudo1 = await readFile(join(dir, "pozew.pseudo.txt"), "utf8");
        const pseudo2 = await readFile(join(dir, "zeznanie.pseudo.txt"), "utf8");
        assert.ok(pseudo1.includes("[OSOBA_1]"));
        assert.ok(pseudo2.includes("[OSOBA_1]") && pseudo2.includes("[OSOBA_2]"));

        const sidecar = JSON.parse(await readFile(slownikPath, "utf8"));
        assert.equal(sidecar.format, SLOWNIK_FORMAT);
        assert.ok(sidecar.ostrzezenie.includes("DANE OSOBOWE"));

        // bieg 2 (osobny proces = restart): numeracja kontynuowana
        const p3 = join(dir, "aneks.txt");
        await writeFile(p3, "Jan Kowalski oraz pan Piotr Wisniewski podpisali aneks.", "utf8");
        await execFileAsync(process.execPath, [CLI, "paczka", p3, "--slownik", slownikPath]);
        const pseudo3 = await readFile(join(dir, "aneks.pseudo.txt"), "utf8");
        assert.ok(pseudo3.includes("[OSOBA_1]"), "Jan trzyma placeholder z biegu 1");
        assert.ok(pseudo3.includes("[OSOBA_3]"), "Piotr dostaje kolejny numer po restarcie");

        // przywroc odpowiedzi LLM
        const odpowiedz = join(dir, "odpowiedz.txt");
        await writeFile(odpowiedz, pseudo1, "utf8");
        const { stdout } = await execFileAsync(
            process.execPath, [CLI, "przywroc", odpowiedz, "--slownik", slownikPath],
        );
        assert.equal(stdout.replace(/\r?\n$/, ""), PLIK_1);
    } finally {
        await rm(dir, { recursive: true, force: true });
    }
});
