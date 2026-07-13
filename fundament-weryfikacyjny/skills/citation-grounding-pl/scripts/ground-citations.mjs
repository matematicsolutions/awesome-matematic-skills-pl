#!/usr/bin/env node
// citation-grounding-pl v2.3 - mechaniczny weryfikator cytatu z GRADIENTEM weryfikacji (zero-dep ESM).
// Usage: node ground-citations.mjs <task.json>
//
// Gradient (adaptacja Existence/Content/Paragraph z jeannesulzer/international-criminal-tribunals-skills, CC BY 4.0):
//   ISTNIENIE (0) - kotwica (sygnatura/CELEX, data, organ) jest realna i zgadza sie z deklaracja.
//   TRESC     (1) - zrodlo CO DO ISTOTY zawiera to, co twierdzi output (parafraza / stanowisko sadu).
//   FRAGMENT  (2) - doslowny cytat / pinpoint akapitu istnieje w zrodle (czysty string-match - rdzen v1).
//
// claim_type ustawia WYMAGANY poziom; skrypt liczy OSIAGNIETY poziom i kalibruje.
// Rdzen mechaniczny pozostaje uczciwy: TRESC zwraca WYMAGA_OSADU (obecnosc terminow to warunek konieczny,
// nie wystarczajacy) - substancje potwierdza czlowiek / paraphrase-judge, jak w kaskadzie PATRON.
//
// task.json: { "items": [ { id, source_id, claim_type?, claim_text?, quote?, source_text?, anchor?, anchor_resolved? } ] }

import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

const QUOTE_CHARS = /[„""»«’‘'`]/g;
const DASHES = /[—–]/g;

const POZIOM = { ISTNIENIE: 0, TRESC: 1, FRAGMENT: 2 };
const POZIOM_NAZWA = ["ISTNIENIE", "TRESC", "FRAGMENT"];

// claim_type -> wymagany poziom weryfikacji
const WYMAGANY_POZIOM = {
  cytat_doslowny: POZIOM.FRAGMENT, // cytat w cudzyslowie
  teza_pinpoint: POZIOM.FRAGMENT, // "jak w pkt 15 uzasadnienia..." bez cudzyslowu
  stanowisko_sadu: POZIOM.TRESC, // parafraza holdingu: "SN przyjal, ze..."
  parafraza: POZIOM.TRESC,
  fakt_proceduralny: POZIOM.ISTNIENIE, // data, sklad, rozstrzygniecie
  powolanie: POZIOM.ISTNIENIE, // sama sygnatura jako autorytet: "por. II CSK 123/19"
  quote: POZIOM.FRAGMENT, // alias wsteczny (v1)
};

// Polskie stopwords - do ekstrakcji terminow nosnych przy poziomie TRESC.
const STOPWORDS = new Set(
  ("a aby albo ale ani az bez bo by byc byl byla bylo byly co czy dla do gdy gdyz i ich ile im " +
   "iz ja jak jako je jednak jego jej jest jesli juz ktore ktory ktora ktorych ktorym lub ma " +
   "majac mi mial mnie moze na nad nam nas nawet nie nim niz o od oraz po pod ponad poniewaz " +
   "przed przez przy sa sie tak takze tam te tego tej temu ten to tych tym u w we wiec za ze " +
   "zeby ze az nr poz art").split(" ")
);

// Fold polskich diakrytykow - dopasowanie frazy szablonowej musi lapac tez tekst ASCII
// (OCR, transliteracja, degradacja kodowania), a lista fraz jest pisana z diakrytykami.
const DIAKRYTYKI = { "ą": "a", "ć": "c", "ę": "e", "ł": "l", "ń": "n", "ó": "o", "ś": "s", "ź": "z", "ż": "z" };
function fold(s) {
  return s.replace(/[ąćęłńóśźż]/g, (ch) => DIAKRYTYKI[ch]);
}

// --- Dyskonto jezyka szablonowego (poziom TRESC) ---
// Frazy-wytrychy polskiego jezyka prawnego wystepuja w niemal kazdym akcie/umowie, wiec ich
// obecnosc w zrodle NIE jest dowodem, ze zrodlo mowi to, co twierdzi output. Termin nosny
// pochodzacy WYLACZNIE z frazy szablonowej liczy sie 0.5 zamiast 1.0 do pokrycia (wazonego).
// Wzorzec COMMON_LEGAL_PHRASES z AnttiHero/lavern (Apache-2.0); lista PL i kod od zera.
const BOILERPLATE_FRAZY = [
  "z zastrzeżeniem",
  "w szczególności",
  "nie ponosi odpowiedzialności",
  "ponosi odpowiedzialność",
  "chyba że umowa stanowi inaczej",
  "chyba że strony postanowiły inaczej",
  "o którym mowa",
  "o której mowa",
  "o których mowa",
  "stosuje się odpowiednio",
  "pod rygorem nieważności",
  "na zasadach określonych",
  "zgodnie z postanowieniami",
  "mając na uwadze",
  "w rozumieniu przepisów",
  "wchodzi w życie",
  "traci moc",
  "w drodze rozporządzenia",
  "z uwzględnieniem",
  "w zakresie nieuregulowanym",
  "postanowienia niniejszej umowy",
  "strony zgodnie postanawiają",
  "zasady współżycia społecznego",
  "należyta staranność",
  "należytej staranności",
].map((f) => fold(normalize(f)));

// Tokeny nosne (>=4 znaki, nie-stopword) pochodzace z fraz szablonowych obecnych w twierdzeniu.
// Zwraca tokeny w formie FOLDED - porownuj przez fold(t).
function boilerplateTokens(normClaim) {
  const foldedClaim = fold(normClaim);
  const toks = new Set();
  for (const fraza of BOILERPLATE_FRAZY) {
    if (!foldedClaim.includes(fraza)) continue;
    for (const t of fraza.split(" ")) {
      if (t.length >= 4 && !STOPWORDS.has(t)) toks.add(t);
    }
  }
  return toks;
}

// --- Zbieznosc fragmentu (poziom TRESC, sygnal pomocniczy) ---
// Trigram-Jaccard twierdzenia z najlepszym oknem zrodla. Lapie przypadek "terminy obecne, ale
// rozproszone po dokumencie" - zrodlo zawiera slowa twierdzenia, lecz zaden zwarty fragment
// nie odpowiada tezie (wariant "prawdziwe slowa, falszywa teza" na poziomie tresci).
// Wzorzec citation-content-matcher z chrisryugj/korean-law-mcp (MIT): tam bigramy znakowe dla
// koreanskiego (1 znak = sylaba); dla polskiego alfabetu lacinskiego odpowiednikiem informacyjnym
// jest TRIGRAM (bigram lacinski nakladal sie przypadkowo w kazdym tekscie prawniczym - zmierzone
// na fixture: bigram scatter 0.33 vs trigram scatter 0.15 przy parafrazie 0.45-0.78). Kod i progi
// od zera; u nas to wylacznie SYGNAL (uwaga dla czlowieka), nigdy samodzielna blokada.
const PROG_ZBIEZNOSC_NISKA = 0.2; // ponizej = terminy rozproszone, brak zwartego fragmentu

function trigramy(s) {
  const out = new Set();
  for (let i = 0; i <= s.length - 3; i++) {
    const g = s.slice(i, i + 3);
    if (!g.includes(" ")) out.add(g);
  }
  return out;
}

function jaccardZbiorow(a, b) {
  if (a.size === 0 || b.size === 0) return 0;
  let wspolne = 0;
  for (const x of a) if (b.has(x)) wspolne++;
  return wspolne / (a.size + b.size - wspolne);
}

// Maksymalny trigram-Jaccard twierdzenia z oknem zrodla dlugosci ~twierdzenia (krok 1/3 okna).
function zbieznoscFragmentu(normClaim, src) {
  const cb = trigramy(normClaim);
  if (cb.size === 0) return null;
  const L = Math.max(normClaim.length, 60);
  if (src.length <= L) return jaccardZbiorow(cb, trigramy(src));
  const step = Math.max(20, Math.floor(L / 3));
  let best = 0;
  for (let i = 0; i <= src.length - Math.floor(L / 2); i += step) {
    const j = jaccardZbiorow(cb, trigramy(src.slice(i, i + L)));
    if (j > best) best = j;
    if (best >= 0.95) break;
  }
  return best;
}

function normalize(s) {
  if (s == null) return "";
  return String(s)
    .replace(/-\s*\n\s*/g, "") // myslnik przenoszenia na koncu wiersza
    .replace(QUOTE_CHARS, '"') // ujednolicenie cudzyslowow
    .replace(DASHES, "-") // ujednolicenie myslnikow
    .toLowerCase()
    .replace(/\s+/g, " ") // zwiniecie bialych znakow
    .trim();
}

// "II CSK 123/19" -> "ii csk 123/19" (do porownania kotwic; tnie kropki i nadmiar spacji)
function normSig(s) {
  return normalize(s).replace(/[.,;]/g, "").replace(/\s+/g, " ").trim();
}

// Rozwiniecie skrotow organow - "SN" i "Sad Najwyzszy" to ta sama instytucja.
const SKROTY_ORGANOW = [
  [/\bsn\b/g, "sąd najwyższy"],
  [/\bnsa\b/g, "naczelny sąd administracyjny"],
  [/\bwsa\b/g, "wojewódzki sąd administracyjny"],
  [/\btk\b/g, "trybunał konstytucyjny"],
  [/\btsue\b/g, "trybunał sprawiedliwości unii europejskiej"],
  [/\bkio\b/g, "krajowa izba odwoławcza"],
  [/\bsokik\b/g, "sąd ochrony konkurencji i konsumentów"],
  [/\bp?uodo\b/g, "urzędu ochrony danych osobowych"], // "Prezes UODO" -> forma dopełniaczowa
  [/\buoku?ik\b/g, "urzędu ochrony konkurencji i konsumentów"],
  [/\bkrs\b/g, "krajowy rejestr sądowy"],
  [/\bsa\b/g, "sąd apelacyjny"],
  [/\bso\b/g, "sąd okręgowy"],
  [/\bsr\b/g, "sąd rejonowy"],
  [/\bso\b/g, "sąd okręgowy"],
];
function normOrgan(s) {
  let t = normalize(s);
  for (const [re, full] of SKROTY_ORGANOW) t = t.replace(re, full);
  return t.replace(/\s+/g, " ").trim();
}
// Czy wszystkie tokeny krotszego organu wystepuja w dluzszym (po rozwinieciu skrotow)?
function organZgodny(a, b) {
  const ta = new Set(normOrgan(a).split(" ").filter(Boolean));
  const tb = new Set(normOrgan(b).split(" ").filter(Boolean));
  const [maly, duzy] = ta.size <= tb.size ? [ta, tb] : [tb, ta];
  for (const t of maly) if (!duzy.has(t)) return false;
  return true;
}

// --- STRONY sprawy: guard "prawdziwy cytat, falszywa teza" na poziomie kotwicy ---
// Gdy sygnatura sie zgadza, ale STRONY zadeklarowane rozjezdzaja sie ze stronami rozwiazanego
// zrodla, to sygnal, ze realny cytat/sygnature doczepiono do INNEJ sprawy. Miara: nakladanie
// zbiorow tokenow nosnych nazw stron (Jaccard) - wzorzec _is_name_mismatch z
// john-walkoe/courtlistener_citations_mcp (MIT); kod, stop-lista PL/EU i progi napisane od zera.
const STRONY_STOP = new Set(
  ("v vs versus przeciwko przeciw p-ko pko ko oraz inni innych innymi innym inn " +
   "spolka spolki spolke z o oo sp s sa akcyjna akcyjnej ograniczona ograniczonej " +
   "odpowiedzialnoscia odpowiedzialnosci komandytowa komandytowo komandytowej jawna cywilna sc " +
   "przedsiebiorstwo panstwowe fundacja stowarzyszenie zaklad zaklady grupa " +
   "we sprawie the of and co ltd inc corp gmbh ag srl bv nv plc se sarl spa oy ab as").split(" ")
);
const STRONY_PROG_ZGODNE = 0.5; // Jaccard >= => strony zgodne (rozne formy tej samej nazwy)
const STRONY_PROG_ROZBIEZNE = 0.3; // Jaccard <  => strony rozbiezne (wzor progu z courtlistener)

// Tokeny nosne nazwy strony: normalizacja + odsianie form prawnych/spojnikow + czystych liczb.
function partyTokens(s) {
  if (s == null) return [];
  const joined = Array.isArray(s) ? s.join(" ") : String(s);
  return [...new Set(
    normalize(joined)
      .replace(/["'.,;:()\[\]/»«§-]/g, " ")
      .split(" ")
      .map((t) => t.replace(/[^a-ząćęłńóśźż0-9]/g, ""))
      .filter((t) => t.length >= 2 && !STRONY_STOP.has(t) && !/^\d+$/.test(t))
  )];
}

// Nakladanie zbiorow tokenow stron (Jaccard). overlap=null gdy ktoras strona bez tokenow nosnych.
function stronyOverlap(a, b) {
  const ta = new Set(partyTokens(a));
  const tb = new Set(partyTokens(b));
  if (ta.size === 0 || tb.size === 0) {
    return { overlap: null, wspolne: [], tylkoZadeklarowane: [...ta], tylkoZnalezione: [...tb], minSize: Math.min(ta.size, tb.size) };
  }
  const wspolne = [...ta].filter((t) => tb.has(t));
  const union = new Set([...ta, ...tb]).size;
  return {
    overlap: wspolne.length / union,
    wspolne,
    tylkoZadeklarowane: [...ta].filter((t) => !tb.has(t)),
    tylkoZnalezione: [...tb].filter((t) => !ta.has(t)),
    minSize: Math.min(ta.size, tb.size),
  };
}

// Data do postaci YYYY-MM-DD jesli sie da; inaczej znormalizowany string.
function normDate(s) {
  if (s == null) return "";
  const t = String(s).trim();
  const iso = t.match(/(\d{4})-(\d{2})-(\d{2})/);
  if (iso) return `${iso[1]}-${iso[2]}-${iso[3]}`;
  const pl = t.match(/(\d{1,2})[.\s]+(\d{1,2})[.\s]+(\d{4})/);
  if (pl) return `${pl[3]}-${String(pl[2]).padStart(2, "0")}-${String(pl[1]).padStart(2, "0")}`;
  return normalize(t);
}

function splitGaps(normQuote) {
  return normQuote
    .split(/\s*(?:\[\s*\.\.\.\s*\]|\.\.\.)\s*/)
    .map((seg) => seg.trim())
    .filter((seg) => seg.length > 0);
}

function editDistance(a, b) {
  const m = a.length, n = b.length;
  if (Math.abs(m - n) > 40) return Math.max(m, n);
  const dp = Array.from({ length: m + 1 }, (_, i) => i);
  for (let j = 1; j <= n; j++) {
    let prev = dp[0];
    dp[0] = j;
    for (let i = 1; i <= m; i++) {
      const tmp = dp[i];
      dp[i] = Math.min(dp[i] + 1, dp[i - 1] + 1, prev + (a[i - 1] === b[j - 1] ? 0 : 1));
      prev = tmp;
    }
  }
  return dp[m];
}

function bestApprox(segment, source) {
  const L = segment.length;
  if (L === 0 || source.length < L) return { dist: L, at: -1 };
  let best = { dist: Infinity, at: -1 };
  const step = L > 200 ? 5 : 1;
  for (let i = 0; i + L <= source.length; i += step) {
    const window = source.slice(i, i + L);
    const d = editDistance(segment, window);
    if (d < best.dist) best = { dist: d, at: i };
    if (d === 0) break;
  }
  return best;
}

// --- POZIOM FRAGMENT: string-match cytatu (rdzen v1) ---
function sprawdzFragment(quote, src) {
  const segments = splitGaps(normalize(quote));
  if (segments.length === 0) return { dopasowanie: "brak", offset: -1 };
  let cursor = 0, firstOffset = -1, exact = true;
  for (const seg of segments) {
    const idx = src.indexOf(seg, cursor);
    if (idx === -1) { exact = false; break; }
    if (firstOffset === -1) firstOffset = idx;
    cursor = idx + seg.length;
  }
  if (exact) return { dopasowanie: "dokladne", offset: firstOffset };

  let worstRatio = 0, detail = [];
  for (const seg of segments) {
    const { dist, at } = bestApprox(seg, src);
    const ratio = seg.length > 0 ? dist / seg.length : 1;
    worstRatio = Math.max(worstRatio, ratio);
    detail.push({ seg: seg.slice(0, 60), dist, at });
  }
  if (worstRatio <= 0.15) return { dopasowanie: "przyblizone", offset: -1, detail };
  return { dopasowanie: "brak", offset: -1, detail };
}

// --- POZIOM TRESC: obecnosc terminow nosnych twierdzenia w zrodle (warunek konieczny) ---
// v2.3: pokrycie WAZONE (termin szablonowy liczy sie 0.5) + pokrycie surowe + zbieznosc fragmentu.
function sprawdzTresc(claimText, src) {
  const normClaim = normalize(claimText);
  const terms = [...new Set(
    normClaim
      .replace(/[".,;:()\[\]»«]/g, " ")
      .split(" ")
      .filter((t) => t.length >= 4 && !STOPWORDS.has(t))
  )];
  if (terms.length === 0) return { pokrycie: 0, pokrycieSurowe: 0, obecne: [], brakujace: [], boilerplate: [], zbieznosc: null };
  const boiler = boilerplateTokens(normClaim);
  // Dopasowanie po RDZENIU (prefiks) - polska deklinacja: "Warszawie"~"Warszawa", "spółki"~"spółka".
  // Termin obecny, gdy zrodlo zawiera jego prefiks dlugosci max(4, len-3) (ucina do 3 znakow koncowki).
  const obecny = (t) => {
    if (src.includes(t)) return true;
    const pref = t.slice(0, Math.max(4, t.length - 3));
    return pref.length >= 4 && src.includes(pref);
  };
  const obecne = [], brakujace = [];
  let licznikWazony = 0;
  for (const t of terms) {
    if (obecny(t)) { obecne.push(t); licznikWazony += boiler.has(fold(t)) ? 0.5 : 1; }
    else brakujace.push(t);
  }
  return {
    pokrycie: licznikWazony / terms.length, // wazone: szablon nie zawyza dowodu
    pokrycieSurowe: obecne.length / terms.length,
    obecne, brakujace, liczbaTerminow: terms.length,
    boilerplate: obecne.filter((t) => boiler.has(fold(t))),
    zbieznosc: zbieznoscFragmentu(normClaim, src),
  };
}

// --- POZIOM ISTNIENIE: zgodnosc kotwicy zadeklarowanej z rozwiazana (SAOS/EUR-Lex dostarcza agent) ---
function sprawdzIstnienie(anchor, resolved) {
  if (!resolved) return { stan: anchor ? "nierozwiazana" : "brak_kotwicy", roznice: [], uwagi: [] };
  // TOZSAMOSC (twarda): sygnatura + data. Rozbieznosc = mozliwe falszerstwo.
  const roznice = [];
  const porTwarde = (klucz, fn) => {
    const a = anchor && anchor[klucz] != null ? fn(anchor[klucz]) : "";
    const b = resolved[klucz] != null ? fn(resolved[klucz]) : "";
    if (a && b && a !== b) roznice.push({ pole: klucz, zadeklarowano: a, znaleziono: b });
  };
  porTwarde("sygnatura", normSig);
  porTwarde("data", normDate);
  // ORGAN (miekki): tylko potwierdzenie. Niezgodnosc = uwaga, NIE blokada - tozsamosc niesie sygnatura.
  const uwagi = [];
  const oa = anchor && anchor.organ != null ? anchor.organ : "";
  const ob = resolved.organ != null ? resolved.organ : "";
  if (oa && ob && !organZgodny(oa, ob)) {
    uwagi.push({ pole: "organ", zadeklarowano: normOrgan(oa), znaleziono: normOrgan(ob), uwaga: "niezgodnosc organu (miekka) - sprawdz, ale tozsamosc niesie sygnatura" });
  }

  // STRONY (kalibrowane): rozbieznosc = twarda roznica (mozliwy "prawdziwy cytat, falszywa teza");
  // czesciowa zgodnosc = miekka uwaga (mozliwa rozna forma nazwy tej samej strony).
  const sa = anchor && (anchor.strony ?? anchor.parties);
  const sb = resolved.strony ?? resolved.parties;
  const ov = stronyOverlap(sa, sb);
  if (ov.overlap != null) {
    const overlapPct = Math.round(ov.overlap * 100) / 100;
    if (ov.overlap < STRONY_PROG_ROZBIEZNE && ov.minSize >= 2) {
      roznice.push({
        pole: "strony", zadeklarowano: partyTokens(sa).join(" "), znaleziono: partyTokens(sb).join(" "),
        overlap: overlapPct, wspolne: ov.wspolne,
        uwaga: "strony sprawy rozbiezne z rozwiazanym zrodlem - mozliwy 'prawdziwy cytat, falszywa teza' (sygnatura/cytat realne, ale dotycza innej sprawy)",
      });
    } else if (ov.overlap < STRONY_PROG_ZGODNE) {
      uwagi.push({
        pole: "strony", zadeklarowano: partyTokens(sa).join(" "), znaleziono: partyTokens(sb).join(" "),
        overlap: overlapPct, uwaga: "czesciowa zgodnosc stron - sprawdz, czy to ta sama sprawa (mozliwa rozna forma nazwy)",
      });
    }
  }
  return { stan: roznice.length === 0 ? "potwierdzona" : "rozbiezna", roznice, uwagi };
}

export { stronyOverlap, partyTokens, zbieznoscFragmentu, boilerplateTokens };

export function verify(item) {
  const claimType = item.claim_type || (item.quote ? "cytat_doslowny" : "powolanie");
  // required_level: jawny override poziomu - pozwala domenie zadeklarowac wlasne claim_type
  // (np. KRS: fakt_rejestrowy/numer_krs) bez wpisywania jej slownika do silnika. Backward-compat.
  let wymagany;
  if (item.required_level && POZIOM[item.required_level] != null) {
    wymagany = POZIOM[item.required_level];
  } else {
    wymagany = WYMAGANY_POZIOM[claimType] ?? POZIOM.FRAGMENT;
  }
  const out = { id: item.id, source_id: item.source_id, claim_type: claimType, wymagany_poziom: POZIOM_NAZWA[wymagany] };

  const maTekst = item.source_text != null && normalize(item.source_text).length > 0;
  const src = maTekst ? normalize(item.source_text) : "";

  // 1. ISTNIENIE
  const ist = sprawdzIstnienie(item.anchor, item.anchor_resolved);
  let poziomIstnienia = -1; // -1 brak, 0 domniemane, 0.5 potwierdzone (>= ISTNIENIE)
  if (ist.stan === "potwierdzona") poziomIstnienia = POZIOM.ISTNIENIE;
  else if (ist.stan === "rozbiezna") poziomIstnienia = -1; // rozbieznosc kotwicy = sygnal falszerstwa
  else if (maTekst) poziomIstnienia = POZIOM.ISTNIENIE; // domniemane na podstawie obecnosci tekstu
  const istnienieDomniemane = ist.stan !== "potwierdzona" && maTekst;

  // 2. FRAGMENT (gdy jest cytat)
  let frag = null;
  if (item.quote && maTekst) frag = sprawdzFragment(item.quote, src);

  // 3. TRESC (gdy jest twierdzenie/parafraza i tekst)
  let tresc = null;
  const claimText = item.claim_text || item.quote;
  if (claimText && maTekst) tresc = sprawdzTresc(claimText, src);

  // OSIAGNIETY poziom
  let osiagniety = istnienieDomniemane || poziomIstnienia >= 0 ? POZIOM.ISTNIENIE : -1;
  if (ist.stan === "rozbiezna") osiagniety = -1;
  if (tresc && tresc.pokrycie >= 0.7) osiagniety = Math.max(osiagniety, POZIOM.TRESC);
  if (frag && frag.dopasowanie === "dokladne") osiagniety = Math.max(osiagniety, POZIOM.FRAGMENT);
  if (frag && frag.dopasowanie === "przyblizone") osiagniety = Math.max(osiagniety, POZIOM.TRESC);

  out.osiagniety_poziom = osiagniety >= 0 ? POZIOM_NAZWA[osiagniety] : "BRAK";

  // --- DECYZJA ---
  // Rozbiezna kotwica - twardy czerwony niezaleznie od reszty.
  if (ist.stan === "rozbiezna") {
    out.status = "NIEZWERYFIKOWANY";
    const poleStrony = ist.roznice.some((r) => r.pole === "strony");
    out.note = poleStrony
      ? "rozbieznosc stron sprawy z rozwiazanym zrodlem - mozliwy 'prawdziwy cytat, falszywa teza' (BLOKADA)"
      : "rozbieznosc kotwicy (sygnatura/data) - mozliwe falszerstwo zrodla";
    out.detail = ist.roznice;
    return out;
  }

  // Brak zrodla tam, gdzie potrzebne (TRESC/FRAGMENT wymagaja tekstu).
  if (wymagany >= POZIOM.TRESC && !maTekst) {
    out.status = "BRAK_ZRODLA";
    out.note = "nie dostarczono tekstu zrodlowego do weryfikacji tresci/fragmentu";
    return out;
  }

  if (wymagany === POZIOM.FRAGMENT) {
    if (frag && frag.dopasowanie === "dokladne") {
      out.status = "ZWERYFIKOWANY"; out.offset = frag.offset; return out;
    }
    if (frag && frag.dopasowanie === "przyblizone") {
      out.status = "ZMODYFIKOWANY"; out.note = "drobne roznice (interpunkcja/uciecie) - patrz diff"; out.detail = frag.detail; return out;
    }
    // cytat nieznaleziony - ale czy dokument w ogole mowi o rzeczy (TRESC)?
    // v2.3: prog na pokryciu WAZONYM - obecnosc samych fraz szablonowych nie ratuje
    // brakujacego cytatu doslownego (lekcja lavern: boilerplate nie jest dowodem).
    if (tresc && tresc.pokrycie >= 0.7) {
      out.status = "KALIBRACJA";
      out.note = "doslowny cytat nieznaleziony, ale zrodlo dotyczy tematu (poziom TRESC). Zloagodz do parafrazy LUB oznacz pinpoint jako prowizoryczny.";
      out.detail = { brakujace_terminy: tresc.brakujace, zbieznosc_fragmentu: tresc.zbieznosc };
      return out;
    }
    out.status = "NIEZWERYFIKOWANY";
    out.note = tresc && tresc.pokrycieSurowe >= 0.7
      ? "brak cytatu; terminy obecne w zrodle to glownie jezyk szablonowy (pokrycie wazone " +
        `${Math.round(tresc.pokrycie * 100)}%, surowe ${Math.round(tresc.pokrycieSurowe * 100)}%) - potencjalna halucynacja, BLOKADA`
      : "brak cytatu i brak pokrycia terminow - potencjalna halucynacja, BLOKADA";
    out.detail = frag ? frag.detail : { powod: "brak tekstu/quote" };
    if (tresc) out.detail = { ...((typeof out.detail === "object" && out.detail) || {}), terminy_szablonowe: tresc.boilerplate, zbieznosc_fragmentu: tresc.zbieznosc };
    return out;
  }

  if (wymagany === POZIOM.TRESC) {
    if (!tresc) { out.status = "BRAK_ZRODLA"; out.note = "brak claim_text/quote lub tekstu zrodla"; return out; }
    if (tresc.pokrycie >= 0.7) {
      out.status = "WYMAGA_OSADU";
      out.note = `terminy nosne obecne (${Math.round(tresc.pokrycie * 100)}%) - substancje potwierdza czlowiek/paraphrase-judge`;
      // Sygnal zbieznosci (v2.3): terminy obecne, ale zaden zwarty fragment zrodla nie odpowiada
      // twierdzeniu - podwyzszone ryzyko "prawdziwe slowa, falszywa teza". Uwaga, nie blokada.
      if (tresc.zbieznosc != null && tresc.zbieznosc < PROG_ZBIEZNOSC_NISKA) {
        out.note += `; UWAGA: terminy rozproszone po zrodle (zbieznosc fragmentu ${Math.round(tresc.zbieznosc * 100)}%) - brak zwartego fragmentu odpowiadajacego twierdzeniu`;
      }
      out.detail = { pokrycie: tresc.pokrycie, pokrycie_surowe: tresc.pokrycieSurowe, brakujace_terminy: tresc.brakujace, terminy_szablonowe: tresc.boilerplate, zbieznosc_fragmentu: tresc.zbieznosc };
      return out;
    }
    // v2.3: pokrycie surowe wysokie, ale wazone ponizej progu = dowod glownie szablonowy.
    // Miekko (czlowiek osadza), bo wszystkie terminy SA w zrodle - to nie klasyczna halucynacja.
    if (tresc.pokrycieSurowe >= 0.7) {
      out.status = "WYMAGA_OSADU";
      out.note = `terminy obecne, ale pokrycie w przewazajacej mierze jezykiem szablonowym (wazone ${Math.round(tresc.pokrycie * 100)}%, surowe ${Math.round(tresc.pokrycieSurowe * 100)}%) - podwyzszona ostroznosc, substancje potwierdza czlowiek`;
      out.detail = { pokrycie: tresc.pokrycie, pokrycie_surowe: tresc.pokrycieSurowe, terminy_szablonowe: tresc.boilerplate, brakujace_terminy: tresc.brakujace, zbieznosc_fragmentu: tresc.zbieznosc };
      return out;
    }
    out.status = "NIEZWERYFIKOWANY";
    out.note = `zrodlo nie zawiera terminow nosnych twierdzenia (pokrycie ${Math.round(tresc.pokrycie * 100)}%) - potencjalna halucynacja`;
    out.detail = { pokrycie: tresc.pokrycie, brakujace_terminy: tresc.brakujace, obecne_terminy: tresc.obecne };
    return out;
  }

  // wymagany === ISTNIENIE
  if (ist.stan === "potwierdzona") {
    out.status = "ZWERYFIKOWANY";
    out.note = "kotwica (sygnatura+data) potwierdzona w rozwiazanym zrodle";
    if (ist.uwagi && ist.uwagi.length) { out.status = "WYMAGA_OSADU"; out.note = "tozsamosc potwierdzona, ale organ niezgodny - sprawdz"; out.uwagi = ist.uwagi; }
    return out;
  }
  if (istnienieDomniemane) {
    out.status = "WYMAGA_OSADU";
    out.note = "istnienie DOMNIEMANE (jest tekst, brak rozwiazanej kotwicy) - rozwiaz sygnature przez saos-orzecznictwo / eu-sparql przy wysokiej stawce";
    return out;
  }
  out.status = "BRAK_ZRODLA";
  out.note = "kotwica nierozwiazana i brak tekstu zrodla - rozwiaz sygnature lub dostarcz dokument";
  return out;
}

function main() {
  const path = process.argv[2];
  if (!path) {
    console.error("Usage: node ground-citations.mjs <task.json>");
    process.exit(2);
  }
  const task = JSON.parse(readFileSync(path, "utf8").replace(/^﻿/, ""));
  const items = Array.isArray(task.items) ? task.items : [];
  const results = items.map(verify);
  const liczba = (s) => results.filter((r) => r.status === s).length;
  const summary = {
    total: results.length,
    zweryfikowane: liczba("ZWERYFIKOWANY"),
    zmodyfikowane: liczba("ZMODYFIKOWANY"),
    wymaga_osadu: liczba("WYMAGA_OSADU"),
    kalibracja: liczba("KALIBRACJA"),
    niezweryfikowane: liczba("NIEZWERYFIKOWANY"),
    brak_zrodla: liczba("BRAK_ZRODLA"),
  };
  // BLOKADA twarda: halucynacja lub brak zrodla. KALIBRACJA/WYMAGA_OSADU = decyzja czlowieka (miekka).
  const blokada = summary.niezweryfikowane > 0 || summary.brak_zrodla > 0;
  const wymaga_decyzji = summary.kalibracja > 0 || summary.wymaga_osadu > 0;
  console.log(JSON.stringify({ summary, blokada, wymaga_decyzji, results }, null, 2));
  process.exit(blokada ? 1 : 0);
}

// Uruchom main() tylko jako CLI; przy imporcie (testy) silnik pozostaje biblioteka.
const argvPath = process.argv[1] ? pathToFileURL(process.argv[1]).href : "";
if (import.meta.url === argvPath) main();
