// Walidatory checksum dla polskich identyfikatorow rejestrowych.
//
// Wszystkie funkcje sa pure (deterministyczne, bez I/O) - audyt
// reprodukowalny. Algorytmy z urzedowych zalacznikow:
// - PESEL: Ustawa z dnia 24 wrzesnia 2010 r. o ewidencji ludnosci,
//   zalacznik nr 1 (wagi 1-3-7-9-1-3-7-9-1-3 mod 10)
// - NIP: Ustawa o zasadach ewidencji i identyfikacji podatnikow
//   (wagi 6-5-7-2-3-4-5-6-7 mod 11; cyfra 10 nie istnieje - jezeli mod
//   da 10, numer jest niepoprawny)
// - REGON 9-cyfrowy: rozporzadzenie GUS, wagi 8-9-2-3-4-5-6-7 mod 11
//   (mod 10 -> cyfra 0)
// - REGON 14-cyfrowy: pierwsze 9 walidowane jak wyzej + dodatkowe 5 cyfr
//   z wagami 2-4-8-5-0-9-7-3-6-1-2-4-8 mod 11 (mod 10 -> cyfra 0)
// - KRS: 10-cyfrowy identyfikator bez publicznej checksumy - walidujemy
//   wylacznie format.

/** PESEL - 11 cyfr + checksuma wagowa (1,3,7,9,1,3,7,9,1,3) mod 10. */
export function isValidPesel(pesel) {
    if (!/^\d{11}$/.test(pesel)) return false;
    const weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3];
    let sum = 0;
    for (let i = 0; i < 10; i++) sum += Number(pesel[i]) * weights[i];
    const checksum = (10 - (sum % 10)) % 10;
    return checksum === Number(pesel[10]);
}

/** NIP - 10 cyfr + checksuma wagowa (6,5,7,2,3,4,5,6,7) mod 11. */
export function isValidNip(nip) {
    const digits = nip.replace(/[\s-]/g, "");
    if (!/^\d{10}$/.test(digits)) return false;
    const weights = [6, 5, 7, 2, 3, 4, 5, 6, 7];
    let sum = 0;
    for (let i = 0; i < 9; i++) sum += Number(digits[i]) * weights[i];
    const checksum = sum % 11;
    if (checksum === 10) return false;
    return checksum === Number(digits[9]);
}

/** REGON 9-cyfrowy - wagi 8-9-2-3-4-5-6-7 mod 11 (mod 10 -> 0). */
export function isValidRegon9(regon) {
    if (!/^\d{9}$/.test(regon)) return false;
    const weights = [8, 9, 2, 3, 4, 5, 6, 7];
    let sum = 0;
    for (let i = 0; i < 8; i++) sum += Number(regon[i]) * weights[i];
    const mod = sum % 11;
    const checksum = mod === 10 ? 0 : mod;
    return checksum === Number(regon[8]);
}

/** REGON 14-cyfrowy - pierwsze 9 valid + cyfra 14 (wagi 2-4-8-5-0-9-7-3-6-1-2-4-8). */
export function isValidRegon14(regon) {
    if (!/^\d{14}$/.test(regon)) return false;
    if (!isValidRegon9(regon.substring(0, 9))) return false;
    const weights = [2, 4, 8, 5, 0, 9, 7, 3, 6, 1, 2, 4, 8];
    let sum = 0;
    for (let i = 0; i < 13; i++) sum += Number(regon[i]) * weights[i];
    const mod = sum % 11;
    const checksum = mod === 10 ? 0 : mod;
    return checksum === Number(regon[13]);
}

/** REGON - akceptuje format 9 lub 14 cyfr. */
export function isValidRegon(regon) {
    const digits = regon.replace(/[\s-]/g, "");
    if (digits.length === 9) return isValidRegon9(digits);
    if (digits.length === 14) return isValidRegon14(digits);
    return false;
}

/** KRS - 10 cyfr (mozliwe wiodace zera). Brak publicznej checksumy. */
export function isValidKrsFormat(krs) {
    return /^\d{10}$/.test(krs);
}

/** Reszta z dzielenia dlugiego ciagu cyfr przez 97 (iteracyjnie, bez bignum). */
function mod97(digits) {
    let rem = 0;
    for (let i = 0; i < digits.length; i++) {
        rem = (rem * 10 + (digits.charCodeAt(i) - 48)) % 97;
    }
    return rem;
}

/**
 * IBAN / NRB polski - "PL" + 2 cyfry kontrolne + 26 cyfr BBAN.
 * Akceptuje z prefiksem PL lub sam 26-cyfrowy NRB (dodajemy PL przed walidacja),
 * spacje i grupy ignorowane. Walidacja: przenies 4 pierwsze znaki na koniec,
 * zamien litery na liczby (A=10..Z=35), reszta mod 97 musi byc 1 (ISO 13616).
 */
export function isValidIbanPl(input) {
    const s = input.replace(/\s/g, "").toUpperCase();
    const iban = s.startsWith("PL") ? s : "PL" + s;
    if (!/^PL\d{26}$/.test(iban)) return false;
    const rearr = iban.slice(4) + iban.slice(0, 4);
    const numeric = rearr.replace(/[A-Z]/g, (c) => String(c.charCodeAt(0) - 55));
    return mod97(numeric) === 1;
}

/**
 * Numer dowodu osobistego - 3 litery + 6 cyfr (4. znak to cyfra kontrolna).
 * Litery A=10..Z=35, wagi 7-3-1-9-7-3-1-7-3 nad wszystkimi 9 znakami,
 * suma wazona mod 10 == 0. Zrodlo algorytmu: algorytm.org (potwierdzone
 * matematycznie - wariant "z cyfra kontrolna w sumie" rownowazny wariantowi
 * "pomijajacemu pozycje 4").
 */
export function isValidDowodOsobisty(input) {
    const v = input.replace(/\s/g, "").toUpperCase();
    if (!/^[A-Z]{3}\d{6}$/.test(v)) return false;
    const weights = [7, 3, 1, 9, 7, 3, 1, 7, 3];
    let sum = 0;
    for (let i = 0; i < 9; i++) {
        const ch = v.charCodeAt(i);
        const val = ch >= 65 ? ch - 55 : ch - 48; // litera A=10.. / cyfra
        sum += val * weights[i];
    }
    return sum % 10 === 0;
}
