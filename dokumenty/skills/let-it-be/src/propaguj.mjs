// Propagacja wykrytej osoby na dalsze wystapienia jej nazwiska.
//
// W pismie osoba pojawia sie raz pelnym imieniem i nazwiskiem ("powodka Anna
// Zielinska"), a potem sama, w odmianie ("Zielinska wniosla", "zdaniem
// Zielinskiej"). Regula OSOBA lapie tylko pare imie + nazwisko, wiec kazde
// dalsze wystapienie przeciekalo. Tu bierzemy nazwisko z KAZDEJ wykrytej
// osoby, wyznaczamy jego rdzen i maskujemy slowa z tym rdzeniem i polska
// koncowka fleksyjna - takze WERSALIKAMI i po zgubieniu ogonkow przez OCR.
//
// Granica: propagujemy tylko to, co detektor juz znalazl. Osoba nigdy nie
// przedstawiona z imieniem nie zostanie wykryta. Kazda forma dostaje wlasny
// token (odwracalnosc co do znaku), wiec model widzi "Zielinska" i
// "Zielinskiej" jako dwa rozne tokeny.

import { FIRST_NAME_FORMS } from "./gazetteers.mjs";
import { FORMA } from "./regex.mjs";

const MIN_RDZEN = 4;

/** Male litery bez ogonkow - "Ł" nie rozklada sie w NFD, stad osobna zamiana. */
export function zloz(slowo) {
    return slowo
        .toLowerCase()
        .replace(/ł/g, "l")
        .normalize("NFD")
        .replace(/\p{M}/gu, "");
}

// Koncowki po rdzeniu (juz w postaci zlozonej, bez ogonkow).
const PRZYMIOTNIKOWE = ["i", "iego", "iemu", "im", "a", "iej", "ich", "imi", "y", "ego", "emu", "ym", "ej", "ych", "ymi"];
const RZECZOWNIKOWE = ["", "a", "owi", "iem", "em", "u", "ie", "owie", "ow", "om", "y", "e", "o", "ami", "ach"];

/** Rdzenie nazwiska wraz z dopuszczalnymi koncowkami. */
export function rdzenie(nazwisko) {
    const s = zloz(nazwisko);
    const out = [];
    // Pierwsze wystapienie tez bywa w odmianie ("pozwanemu Janowi Kowalskiemu").
    const m = s.match(/^(.*(?:sk|ck|dzk))(?:i|a|iego|iemu|im|iej|ich|imi)$/);
    if (m) {
        out.push({ rdzen: m[1], koncowki: PRZYMIOTNIKOWE });
        return out.filter((r) => r.rdzen.length >= MIN_RDZEN);
    }
    if (s.endsWith("a")) {
        // Nazwisko meskie na -a (Zagloba) albo zenskie rzeczownikowe (Kowalowa).
        out.push({ rdzen: s.slice(0, -1), koncowki: ["a", "y", "i", "e", "ie", "o"] });
    }
    // Pierwsze wystapienie w odmianie ("z Pawlem Nowakiem"): zdejmujemy koncowke,
    // zeby dotrzec do mianownika. Rdzen za krotki odpada nizej (MIN_RDZEN).
    const kandydaci = new Set([s]);
    for (const k of RZECZOWNIKOWE) if (k && s.endsWith(k)) kandydaci.add(s.slice(0, -k.length));
    for (const r of kandydaci) {
        out.push({ rdzen: r, koncowki: RZECZOWNIKOWE });
        // e ruchome: Wrobel -> Wrobla, Kaczmarek -> Kaczmarka, Stasiec -> Stasca.
        const ruchome = r.match(/^(.*)e([lkc])$/);
        if (ruchome) out.push({ rdzen: ruchome[1] + ruchome[2], koncowki: RZECZOWNIKOWE.filter((k) => k !== "") });
    }
    return out.filter((r) => r.rdzen.length >= MIN_RDZEN);
}

function pasuje(slowo, listaRdzeni) {
    const z = zloz(slowo);
    return listaRdzeni.some(({ rdzen, koncowki }) =>
        z.startsWith(rdzen) && koncowki.includes(z.slice(rdzen.length)),
    );
}

/**
 * Nazwiska z encji OSOBA ("Anna Nowak-Zielinska" -> ["Nowak", "Zielinska"]).
 * Nazwiskiem jest kazdy czlon, ktory nie jest imieniem - dziala dla kolejnosci
 * "Imie Nazwisko", "Nazwisko Imie" z tabel i dla dwoch imion.
 */
function nazwiskaOsob(encje) {
    const out = new Set();
    for (const e of encje) {
        if (e.type !== "OSOBA") continue;
        const czlony = e.raw.trim().split(/\s+/);
        for (const czlon of czlony.filter((c) => !FIRST_NAME_FORMS.has(zloz(c)))) {
            for (const czesc of czlon.split("-")) if (czesc) out.add(czesc);
        }
    }
    return [...out];
}

// Slowo z wielkiej litery albo wersalikami, z opcjonalnym lacznikiem.
const SLOWO_RE = /(?<![\p{L}\p{N}])\p{Lu}[\p{L}]*(?:-\p{Lu}[\p{L}]*)?(?![\p{L}\p{N}])/gu;

/**
 * Dodatkowe encje OSOBA dla dalszych wystapien nazwisk juz wykrytych osob.
 * `encje` to wszystkie rozlaczne dopasowania (takze nie-PII: sygnatury,
 * sady) - nowe wystapienie nie moze na nie nachodzic.
 */
export function propagujNazwiska(text, encje) {
    const listaRdzeni = nazwiskaOsob(encje).flatMap(rdzenie);
    if (listaRdzeni.length === 0) return [];
    const zajete = encje.map((e) => [e.start, e.end]);
    const out = [];
    for (const m of text.matchAll(SLOWO_RE)) {
        const start = m.index;
        const end = start + m[0].length;
        if (zajete.some(([s, e]) => start < e && s < end)) continue;
        const czesci = m[0].split("-");
        if (!czesci.some((c) => c && pasuje(c, listaRdzeni))) continue;
        out.push({
            raw: m[0],
            normalized: m[0],
            type: "OSOBA",
            confidence: 0.8,
            ruleId: "osoba-odmiana",
            start,
            end,
        });
    }
    return out;
}

// --- Firmy: dalsze wystapienia nazwy bez formy prawnej ---
//
// "Termika Wschod sp. z o.o." wraca w pismie jako "Termika", "Termiki",
// "TERMIKA WSCHOD". Maskujemy pelny rdzen nazwy i jego pierwszy czlon, takze w
// odmianie. Rzeczownik ogolny ("Centrum", "Apteka", "Galeria") jako pierwszy
// czlon NIE jest propagowany sam - inaczej kazde "Centrum miasta" byloby firma.
const OGOLNE = new Set(["centrum", "galeria", "dom", "apteka", "drukarnia", "hurtownia", "pracownia",
    "zaklad", "zaklady", "przedsiebiorstwo", "biuro", "kancelaria", "fundacja", "stowarzyszenie",
    "spoldzielnia", "grupa", "firma", "sklep", "studio", "instytut", "fabryka", "uslugi", "transport",
    "logistyka", "systems", "polska", "poland", "handel", "serwis", "bank", "klinika", "szkola",
    "agencja", "wydawnictwo", "restauracja", "hotel", "oddzial", "zespol", "osrodek", "centrala",
    "przychodnia", "gabinet", "salon", "warsztat", "spolka", "zielony", "nowy", "stary", "wielki"]);

const SAMA_FORMA_KONIEC = new RegExp(String.raw`[ \t]+${FORMA}(?:[ \t]+${FORMA})?$`, "u");
const NAZWA_RE = /(?<![\p{L}\p{N}])[\p{Lu}\d][\p{L}\d-]*(?:[ \t]+[\p{Lu}\d][\p{L}\d-]*)*(?![\p{L}\p{N}])/gu;

/** Rdzen nazwy firmy: bez formy prawnej, jako lista czlonow. */
function rdzenFirmy(raw) {
    const bez = raw.replace(SAMA_FORMA_KONIEC, "").replace(/[„”"]/g, "").trim();
    if (bez === raw.trim()) return null; // tylko firmy z forma prawna sa zrodlem propagacji
    return bez.split(/[ \t]+/).filter(Boolean);
}

export function propagujFirmy(text, encje) {
    const wzorce = []; // { czlony: [zlozone...], ostatniRdzenie }
    for (const e of encje) {
        if (e.type !== "FIRMA") continue;
        const czlony = rdzenFirmy(e.raw);
        if (!czlony || czlony.length === 0) continue;
        wzorce.push(czlony.map(zloz));
        const pierwszy = zloz(czlony[0]);
        if (czlony.length > 1 && !OGOLNE.has(pierwszy) && pierwszy.length >= MIN_RDZEN) wzorce.push([pierwszy]);
    }
    if (wzorce.length === 0) return [];
    // Ostatni czlon moze byc odmieniony ("Termiki", "Agroluxu"); poprzednie - dokladnie.
    const pasuje = (fraza) => {
        const slowa = fraza.split(/[ \t]+/).map(zloz);
        return wzorce.some((w) => {
            if (w.length > slowa.length) return false;
            if (w.length === 1 && OGOLNE.has(w[0])) return false;
            for (let i = 0; i + w.length <= slowa.length; i++) {
                const ok = w.every((c, j) => {
                    const s = slowa[i + j];
                    if (j < w.length - 1) return s === c;
                    return s === c || rdzenie(c).some(({ rdzen, koncowki }) =>
                        s.startsWith(rdzen) && koncowki.includes(s.slice(rdzen.length)));
                });
                if (ok) return true;
            }
            return false;
        });
    };
    const zajete = encje.map((e) => [e.start, e.end]);
    const out = [];
    for (const m of text.matchAll(NAZWA_RE)) {
        // Z frazy z wielkich liter bierzemy najdluzszy fragment pasujacy do wzorca.
        const slowa = [...m[0].matchAll(/[^ \t]+/g)];
        let najlepszy = null;
        for (let i = 0; i < slowa.length && !najlepszy; i++) {
            for (let j = slowa.length; j > i; j--) {
                const s0 = m.index + slowa[i].index;
                const s1 = m.index + slowa[j - 1].index + slowa[j - 1][0].length;
                const fraza = text.slice(s0, s1);
                const w = fraza.split(/[ \t]+/);
                if (w.length > 4) continue;
                if (pasuje(fraza)) {
                    // Fraza musi pokrywac caly wzorzec: dopasowanie od poczatku frazy.
                    const zl = w.map(zloz);
                    const trafia = wzorce.some((wz) => wz.length === zl.length && wz.every((c, k) =>
                        k < wz.length - 1 ? zl[k] === c : (zl[k] === c || rdzenie(c).some(({ rdzen, koncowki }) =>
                            zl[k].startsWith(rdzen) && koncowki.includes(zl[k].slice(rdzen.length))))));
                    if (trafia) { najlepszy = [s0, s1, fraza]; break; }
                }
            }
        }
        if (!najlepszy) continue;
        const [start, end, raw] = najlepszy;
        if (zajete.some(([s, e]) => start < e && s < end)) continue;
        out.push({ raw, normalized: raw, type: "FIRMA", confidence: 0.7, ruleId: "firma-odmiana", start, end });
    }
    return out;
}
