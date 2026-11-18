// citation-grounding-pl v3 - porownanie cytatu ze zrodlem NA SLOWACH (zero-dep ESM).
//
// Po co: dopasowanie znakowe z progiem 15% wrzucalo do jednego worka "drobne roznice" zmiane
// "14 dni" -> "15 dni", dopisane "nie" i cudzyslow wokol cytatu. Pomiar 2026-11-18 na 8 kodeksach:
// 76 z 77 cytatow ze ZMIENIONA trescia wychodzilo jako "drobne roznice" (status miekki, kod 0),
// a 50 ze 120 WIERNYCH cytatow po zwyklej typografii - tak samo. Worek nie odroznial jednych od drugich.
//
// Zasady (kazda z testem i z kontrola na czerwono):
//  - typografia, przecinki i nawiasy nie sa trescia; kropka, srednik, dwukropek, "§", "%" i liczby - sa;
//  - KAZDA roznica slowa to zmieniona tresc. Nie ma progu "prawie pasuje": slownika antonimow nie da sie
//    zamknac ("mniej"/"wiecej", "dni"/"miesiecy"). Wyjatek: slowo rozniace sie WYLACZNIE znakami
//    diakrytycznymi ("sadu"/"sądu") - typowy slad OCR albo klawiatury, zglaszany osobno i lagodniej;
//  - opuszczenie w cytacie ("(...)", "[...]", "...") musi miescic sie w jednym miejscu zrodla, a wyciety
//    tekst ZAWSZE wraca w wyniku. Czyste jest tylko opuszczenie zwyklych slow: liczba, spojnik,
//    przeczenie, wyjatek, slowo kierunku albo slowo z przedrostkiem nie-/bez- w wycieciu to odmowa;
//  - odnosnik redakcyjny tekstu jednolitego przyklejony do slowa ("zdrowia.4)") jest znakowany, nie
//    wycinany: brak odnosnika w cytacie nie szkodzi, INNY numer odnosnika w cytacie jest roznica.
//
// Czego ten modul NIE ocenia: kompletnosci mysli. Wierny fragment urwany PRZED wyjatkiem ("Kara wynosi
// 5 lat" przy zrodlowym "..., chyba ze sad orzeknie inaczej") jest zgodny - sprawdzamy slowa, ktore
// cytujacy podal. Lista slow istotnych jest lista form, nie analiza skladni; dlatego wyciety tekst
// dostaje czlowiek, a nie sam werdykt.
//
// Idea dopasowania na slowach z podzialem roznic: altanziya/eu-ai-act-mcp (Apache-2.0). Kod, slowniki
// polskie i progi napisane od zera.

export const MIN_SLOW = 3; // krotszy cytat zostaje przy dopasowaniu znakowym (za malo slow na glosowanie)
export const MIN_SEGMENT = 3; // segment cytatu z opuszczeniem: mniej slow = przypadkowe trafienie
export const MAKS_ODSTEP = 40; // tyle slow wolno opuscic miedzy segmentami; dalej to dwa rozne miejsca
const MAKS_KANDYDATOW = 8;

const ZNAKI = new Set([".", ";", ":"]);
// Odnosnik redakcyjny przyklejony do slowa albo znaku; punkt wyliczenia po spacji ("gdy: 5) ...") zostaje.
const ODNOSNIK = /(?<=[\p{Ll}.,;:])(\d{1,3})\)(?=\s|$|[.,;:])/gu;
const ZNACZNIK = "\u0001"; // zamiast ")" - ta sama dlugosc napisu, wiec pozycje znakow sie nie przesuwaja
const OPUSZCZENIE = /\s*\.\.\.\s*/u; // takze "(...)" i "[...]": nawiasy nie sa tokenami
const SLOWO = /\u0001\d+|\d+(?:[.,]\d+)+|[\p{L}\p{N}]+(?:[-/][\p{L}\p{N}]+)*|[%‰§]|[.;:]/gu;

const PRZECZENIA = new Set(["nie", "ani", "bez", "chyba", "wyjątkiem", "wyjątek", "wyjąwszy", "poza", "oprócz",
  "wyłączając", "tylko", "wyłącznie", "jedynie", "żaden", "żadna", "żadne", "nigdy", "zakaz", "zakazuje", "zakazane",
  "wyłącza", "wyłączeniem", "ile", "warunkiem", "zastrzeżeniem"]);
const SPOJNIKI = new Set(["lub", "albo", "bądź", "i", "oraz", "może", "mogą", "musi", "muszą", "wolno", "każdy", "każda",
  "każde", "najmniej", "najwyżej", "najpóźniej", "niż", "jeżeli", "obowiązany", "obowiązana", "uprawniony", "uprawniona"]);
const KIERUNKOWE = new Set(["przed", "po", "wcześniej", "później", "mniej", "więcej", "powyżej", "poniżej", "ponad", "do",
  "od", "wyższy", "wyższa", "wyższe", "niższy", "niższa", "niższe", "dłużej", "krócej", "zawsze", "także", "również"]);
const MIESIACE = new Set(["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca", "sierpnia", "września",
  "października", "listopada", "grudnia"]);
const LICZEBNIK = new RegExp("^(?:pół|półtora|jed(?:en|na|no|nego|nej|nym)|dw(?:a|ie|óch|u|oma|ukrotn\\p{L}*)|" +
  "trz(?:y|ech|ema)|czter\\p{L}*|pię[ćc]\\p{L}*|sze[śs][ćc]\\p{L}*|siedem\\p{L}*|siedm\\p{L}*|osiem\\p{L}*|ośm\\p{L}*|" +
  "dziewię[ćc]\\p{L}*|dziesię[ćc]\\p{L}*|\\p{L}*naś(?:cie|tu)\\p{L}*|\\p{L}*dzie(?:ści|stu|siąt|sięciu)\\p{L}*|sto|stu|" +
  "dwieście|\\p{L}*set|tysi[ąę]c\\p{L}*|milion\\p{L}*|pierwsz(?:y|a|e|ego|ej|emu|ym|ych|ą)|drug(?:i|a|ie|iego|iej)|" +
  "trzeci(?:a|e|ego|ej|emu|m|ch|ą)?|połow\\p{L}+|podwójn\\p{L}+|potrójn\\p{L}+)$", "u");
// slowa na "nie...", ktore przeczeniem nie sa: przedrostki oraz CALE slowa (zaimki). Zaimek jako przedrostek
// polykalby "niejawny" i "niegodny".
const NIE_PRZEDROSTKI = ["niniejsz", "niekied", "niektór", "niemiec", "nieruchomo"];
const NIE_ZAIMKI = new Set(["niego", "niej", "nich", "nimi", "nieco"]);
const DIAKRYTYKI = { "ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n", "ó": "o", "ś": "s", "ź": "z", "ż": "z" };

export function bezDiakrytykow(s) {
  return s.replace(/[ąćęłńóśźż]/g, (c) => DIAKRYTYKI[c]);
}

export function twardy(t) {
  return /\p{N}/u.test(t) || t === "%" || t === "‰" || t === "§" || PRZECZENIA.has(t) || SPOJNIKI.has(t) ||
    MIESIACE.has(t) || LICZEBNIK.test(t);
}

// Slowo, ktorego wyciecie z cytatu moze zmienic sens. Regula jest celowo za szeroka: falszywa odmowa przy
// opuszczeniu kosztuje mniej niz falszywe potwierdzenie.
export function istotnyWOpuszczeniu(t) {
  if (twardy(t) || KIERUNKOWE.has(t)) return true;
  if (t.length > 3 && t.startsWith("bez")) return true;
  return t.length > 3 && t.startsWith("nie") && !NIE_PRZEDROSTKI.some((p) => t.startsWith(p)) && !NIE_ZAIMKI.has(t);
}

function oznaczOdnosniki(s) {
  return s.replace(ODNOSNIK, (_m, nr) => ZNACZNIK + nr);
}

// Tokeny z pozycjami znakow w napisie wejsciowym (znormalizowanym): { t, a, b }.
export function tokeny(norm) {
  const out = [];
  for (const m of oznaczOdnosniki(norm).matchAll(SLOWO)) out.push({ t: m[0], a: m.index, b: m.index + m[0].length });
  return out;
}

const toOdnosnik = (t) => t.charCodeAt(0) === 1;
// "10 000" albo "10000": same cyfry, pierwsza grupa 1-3 cyfry, kazda nastepna dokladnie 3.
// ciagi cyfr w kolejnosci, granica slowa konczy ciag: ["5","6"] -> "5|6", ["56"] -> "56", ["45poz"] -> "45"
const ciagiCyfr = (toks) => toks.flatMap((t) => t.match(/\p{N}+/gu) || []).join("|");
const zapisTysiecy = (toks) => toks.every((t) => /^\d+$/.test(t)) &&
  (toks.length === 1 || (toks[0].length <= 3 && toks.slice(1).every((t) => t.length === 3)));
const ileSlow = (toks) => toks.reduce((n, x) => n + (ZNAKI.has(x.t) || toOdnosnik(x.t) ? 0 : 1), 0);

// Wtracenie cytujacego w nawiasie kwadratowym ("jezeli [spolka] zostala zawarta") nie jest czescia cytatu.
// "[...]" to opuszczenie, a "[1]" przy numerze jednostki to zapis indeksu gornego w tekstach jednolitych -
// wtraceniem jest tylko nawias z litera i bez cyfry. Zwraca cytat bez wtracen i ich liste.
const WTRACENIE = /\[(?=[^\[\]]*\p{L})([^\[\]\p{N}]{1,80})\]/gu;
export function bezWtracen(normQuote) {
  const wtracenia = [];
  const tekst = normQuote.replace(WTRACENIE, (_m, w) => { wtracenia.push(w.trim()); return " "; });
  return { tekst, wtracenia };
}

function segmentyCytatu(normQuote) {
  // Cudzyslowy i nawiasy nie sa tokenami, wiec "(...)" dzieli sie tak samo jak "..." i nie trzeba ich zdejmowac.
  return normQuote.trim().split(OPUSZCZENIE).map((x) => x.trim()).filter((x) => x.length > 0);
}

function tokenySegmentu(seg) {
  let t = tokeny(seg);
  while (t.length && ZNAKI.has(t[0].t)) t = t.slice(1);
  while (t.length && ZNAKI.has(t[t.length - 1].t)) t = t.slice(0, -1);
  return t;
}

// Dopasowanie cytatu q do okna zrodla z WOLNYMI koncami okna (prefiks i sufiks okna nic nie kosztuja).
// Zwraca roznice (zgrupowane), koszt oraz [poczatek, koniec) dopasowania w oknie.
function wyrownaj(q, okno) {
  const n = q.length, m = okno.length;
  const dp = Array.from({ length: n + 1 }, () => new Int32Array(m + 1));
  for (let i = 1; i <= n; i++) dp[i][0] = i;
  for (let i = 1; i <= n; i++) {
    for (let j = 1; j <= m; j++) {
      const rowne = q[i - 1] === okno[j - 1] ? 0 : 1;
      // odnosnik redakcyjny, ktory jest tylko w zrodle, nic nie kosztuje
      const pominZrodlo = toOdnosnik(okno[j - 1]) ? 0 : 1;
      dp[i][j] = Math.min(dp[i - 1][j - 1] + rowne, dp[i - 1][j] + 1, dp[i][j - 1] + pominZrodlo);
    }
  }
  let koniec = 0;
  // Przy remisie bierzemy DALSZY koniec: zle ostatnie slowo cytatu ma wyjsc jako zamiana ("abuzywne" zamiast
  // "abuzywna"), a nie jako slowo bez odpowiednika w zrodle.
  for (let j = 1; j <= m; j++) if (dp[n][j] <= dp[n][koniec]) koniec = j;
  // ...ale nie wciagamy odnosnika redakcyjnego stojacego ZA cytatem (nic nie kosztuje, wiec remisuje).
  while (koniec > 0 && toOdnosnik(okno[koniec - 1]) && dp[n][koniec] === dp[n][koniec - 1]) koniec--;
  const kroki = [];
  let i = n, j = koniec;
  while (i > 0) {
    if (j > 0 && dp[i][j] === dp[i - 1][j - 1] + (q[i - 1] === okno[j - 1] ? 0 : 1)) {
      kroki.push(q[i - 1] === okno[j - 1] ? null : { c: q[i - 1], z: okno[j - 1] });
      i--; j--;
    } else if (dp[i][j] === dp[i - 1][j] + 1) {
      kroki.push({ c: q[i - 1], z: null });
      i--;
    } else {
      kroki.push(toOdnosnik(okno[j - 1]) ? { odnosnik: okno[j - 1].slice(1) } : { c: null, z: okno[j - 1] });
      j--;
    }
  }
  kroki.reverse();
  const roznice = [], odnosniki = [];
  let biezaca = null;
  for (const k of kroki) {
    if (k && k.odnosnik) { odnosniki.push(k.odnosnik); continue; }
    if (!k) { biezaca = null; continue; }
    if (!biezaca) { biezaca = { c: [], z: [] }; roznice.push(biezaca); }
    if (k.c != null) biezaca.c.push(k.c);
    if (k.z != null) biezaca.z.push(k.z);
  }
  const opis = roznice.map((r) => {
    const slowa = [...r.c, ...r.z];
    const diakrytyki = r.c.length === r.z.length && r.c.every((x, k) => x !== r.z[k] && bezDiakrytykow(x) === bezDiakrytykow(r.z[k]));
    const pokaz = (x) => x.map((t) => (toOdnosnik(t) ? t.slice(1) + ")" : t)).join(" ");
    // Ten sam ciag znakow inaczej podzielony na slowa ("zwol nienia" / "zwolnienia", "45 poz" / "45poz") to slad
    // lamania wiersza albo sklejenia przy kopiowaniu z PDF, nie zmiana tresci. Podzial CYFR jest trescia
    // ("art. 5 6" to nie "art. 56", "100 00" to nie "10 000"): ciagi cyfr musza byc po obu stronach te same,
    // z jednym wyjatkiem - poprawny zapis tysiecy po obu stronach ("10 000" / "10000").
    const sklejenie = r.c.length > 0 && r.z.length > 0 && !slowa.some(toOdnosnik) && r.c.join("") === r.z.join("") &&
      (ciagiCyfr(r.c) === ciagiCyfr(r.z) || (zapisTysiecy(r.c) && zapisTysiecy(r.z)));
    return { cytat: pokaz(r.c), zrodlo: pokaz(r.z), ile: Math.max(r.c.length, r.z.length),
      twarda: slowa.some((t) => toOdnosnik(t) || twardy(t)), tylko_diakrytyki: diakrytyki, sklejenie };
  });
  const realne = opis.filter((r) => !r.sklejenie).map(({ sklejenie, ...r }) => r);
  // koszt = liczba slow REALNIE roznych; sklejenia, odnosniki tylko ze zrodla i slowa rozniace sie wylacznie
  // znakami diakrytycznymi nie licza sie do progu (cytat przepisany bez polskich znakow to nadal ten cytat)
  return { roznice: realne, koszt: realne.reduce((a, r) => a + (r.tylko_diakrytyki ? 0 : r.ile), 0), poczatek: j, koniec, odnosniki };
}

function kandydaci(q, art, indeks, od) {
  const n = q.length;
  const glosy = new Map();
  q.forEach((t, i) => {
    for (const p of indeks.get(bezDiakrytykow(t)) || []) if (p - i >= od - 2) glosy.set(p - i, (glosy.get(p - i) || 0) + 1);
  });
  // Slowo dopisane albo zgubione w srodku cytatu przesuwa dalsze slowa o jedno miejsce i dzieli glosy miedzy
  // sasiednie pozycje - liczymy wiec glosy z sasiedztwa +-2.
  const laczne = [...glosy.keys()].map((s) => [s, [-2, -1, 0, 1, 2].reduce((a, d) => a + (glosy.get(s + d) || 0), 0)]);
  laczne.sort((x, y) => y[1] - x[1] || (glosy.get(y[0]) || 0) - (glosy.get(x[0]) || 0) || x[0] - y[0]);
  const out = [], widziane = new Set();
  const zapas = Math.max(2, Math.floor(n / 8) + 1);
  for (const [start, ile] of laczne.slice(0, MAKS_KANDYDATOW)) {
    if (ile < Math.max(2, Math.floor(0.6 * n))) break;
    const a = Math.max(od, start - zapas);
    const w = wyrownaj(q, art.slice(a, start + n + zapas));
    const klucz = `${a + w.poczatek}:${a + w.koniec}`;
    if (widziane.has(klucz)) continue;
    widziane.add(klucz);
    out.push({ roznice: w.roznice, koszt: w.koszt, poczatek: a + w.poczatek, koniec: a + w.koniec, odnosniki: w.odnosniki });
  }
  const najnizszy = Math.min(...out.map((k) => k.koszt));
  return out.filter((k) => k.koszt === najnizszy);
}

// Wszystkie segmenty po kolei w jednym tekscie; z kilku wystapien frazy wygrywa wiernosc, potem bliskosc.
function dopasuj(segmenty, art) {
  const indeks = new Map();
  // glosowanie po formie bez znakow diakrytycznych: "sadu" ma trafic w okolice "sądu" (porownanie zostaje scisle)
  art.forEach((t, p) => { const k = bezDiakrytykow(t); if (!indeks.has(k)) indeks.set(k, []); indeks.get(k).push(p); });
  const pamiec = new Map();
  const dalej = (nr, od) => {
    if (nr === segmenty.length) return { roznice: [], koszt: 0, odstepy: [], zakresy: [], odnosniki: [] };
    const klucz = `${nr}:${od}`;
    if (pamiec.has(klucz)) return pamiec.get(klucz);
    let najlepszy = null;
    for (const w of kandydaci(segmenty[nr], art, indeks, od)) {
      const reszta = dalej(nr + 1, w.koniec);
      if (!reszta) continue;
      const wynik = {
        roznice: [...w.roznice, ...reszta.roznice], koszt: w.koszt + reszta.koszt,
        odstepy: [...(nr ? [[od, w.poczatek]] : []), ...reszta.odstepy],
        zakresy: [[w.poczatek, w.koniec], ...reszta.zakresy], odnosniki: [...w.odnosniki, ...reszta.odnosniki],
      };
      const miara = [wynik.koszt, wynik.odstepy.reduce((a, o) => a + (o[1] - o[0]), 0)];
      if (!najlepszy || miara[0] < najlepszy.miara[0] || (miara[0] === najlepszy.miara[0] && miara[1] < najlepszy.miara[1])) {
        najlepszy = { miara, wynik };
      }
    }
    const zwrot = najlepszy ? najlepszy.wynik : null;
    pamiec.set(klucz, zwrot);
    return zwrot;
  };
  return dalej(0, 0);
}

// normQuote, normSource: napisy PO normalizacji skilla (male litery, ujednolicona typografia).
// Stany: DOKLADNY, DOKLADNY_Z_OPUSZCZENIEM, OPUSZCZENIE_ISTOTNE, OPUSZCZENIE_ZA_SZEROKIE, ROZJAZD, BRAK, ZA_KROTKI.
// `zakres` i `segmenty` to pozycje ZNAKOW w normSource [a, b).
export function porownajSlowa(normQuoteZWtraceniami, normSource) {
  const { tekst: normQuote, wtracenia } = bezWtracen(normQuoteZWtraceniami);
  // Wtracenie ze slowem, ktore zmienia sens ("Sad [nie] moze"), to nie objasnienie, tylko zmiana tresci cytatu:
  // pominiete przy porownaniu przeszloby na zielono (odbior 2026-11-18).
  const istotne = [...new Set(wtracenia.flatMap((w) => tokeny(w).map((x) => x.t)).filter(istotnyWOpuszczeniu))].sort();
  if (istotne.length) return { stan: "WTRACENIE_ISTOTNE", wtracenia, wtracenia_istotne: istotne };
  const wynik = porownajBezWtracen(normQuote, normSource);
  return wtracenia.length ? { ...wynik, wtracenia } : wynik;
}

function porownajBezWtracen(normQuote, normSource) {
  const seg = segmentyCytatu(normQuote).map(tokenySegmentu).filter((s) => s.length > 0);
  const razem = seg.reduce((a, s) => a + ileSlow(s), 0);
  if (seg.length === 0 || razem < MIN_SLOW) return { stan: "ZA_KROTKI" };
  if (seg.length > 1 && seg.some((s) => ileSlow(s) < MIN_SEGMENT)) return { stan: "ZA_KROTKI", powod: "segment cytatu z opuszczeniem ma mniej niz 3 slowa" };
  const zrodlo = tokeny(normSource);
  const art = zrodlo.map((x) => x.t);
  const w = dopasuj(seg.map((s) => s.map((x) => x.t)), art);
  const n = seg.reduce((a, s) => a + s.length, 0);
  if (!w || w.koszt > Math.max(2, Math.floor(n / 8))) return { stan: "BRAK" };
  const naZnaki = ([a, b]) => ({ a: zrodlo[a].a, b: zrodlo[b - 1].b });
  const segmenty = w.zakresy.filter(([a, b]) => b > a).map(naZnaki);
  const baza = { segmenty, zakres: segmenty.length ? { a: segmenty[0].a, b: segmenty[segmenty.length - 1].b } : null,
    ...(w.odnosniki.length ? { odnosniki_pominiete: w.odnosniki } : {}) };
  if (w.roznice.length) {
    const tylkoDiakrytyki = w.roznice.every((r) => r.tylko_diakrytyki);
    return { stan: "ROZJAZD", roznice: w.roznice, twardy: w.roznice.some((r) => r.twarda), tylko_diakrytyki: tylkoDiakrytyki, ...baza };
  }
  if (seg.length === 1) return { stan: "DOKLADNY", ...baza };
  const odstepy = w.odstepy.map(([a, b]) => zrodlo.slice(a, b).filter((x) => !toOdnosnik(x.t)));
  const tekst = w.odstepy.map(([a, b]) => (b > a ? normSource.slice(zrodlo[a].a, zrodlo[b - 1].b) : ""));
  const opuszczonoSlow = odstepy.reduce((a, o) => a + ileSlow(o), 0);
  if (odstepy.some((o) => ileSlow(o) > MAKS_ODSTEP)) return { stan: "OPUSZCZENIE_ZA_SZEROKIE", opuszczono_slow: opuszczonoSlow, ...baza };
  const istotne = [...new Set(odstepy.flat().map((x) => x.t).filter(istotnyWOpuszczeniu))].sort();
  if (istotne.length) return { stan: "OPUSZCZENIE_ISTOTNE", opuszczono_slow: opuszczonoSlow, opuszczone_istotne: istotne, opuszczone: tekst, ...baza };
  return { stan: "DOKLADNY_Z_OPUSZCZENIEM", opuszczono_slow: opuszczonoSlow, opuszczone: tekst, ...baza };
}
