"""Wyszukiwarka po tekscie akt z OCR / search the OCR'd case files - lokalnie, SQLite FTS5, zero zaleznosci.

    python szukaj.py --buduj [--lang pol|eng]   # indeks z *.txt w tym katalogu / build the index
    python szukaj.py "opinia bieglej"           # fraza, kolejnosc slow dowolna / any word order
    python szukaj.py "biegl" --dokladnie        # PL: bez dopasowania odmiany
    python szukaj.py "contract" --prefix        # EN: dopasuj tez contracts, contractor

Zwraca plik, strone, fragment. Wielkosc liter i znaki diakrytyczne nie maja znaczenia
("lodz" znajdzie "Łódź"): skladamy je sami, bo FTS5 `remove_diacritics` NIE sklada litery "ł".
Jezyk zapisany w indeksie decyduje o odmianie: `pol` ucina 2 znaki koncowki od 6 liter
("bieglej" -> "biegl*"), `eng` szuka dokladnych slow (chyba ze --prefix).
Tekst zapytania idzie do MATCH jako frazy w cudzyslowie - surowy tekst w MATCH to skladnia.
Tekst pochodzi z OCR: przed cytowaniem porownaj z oryginalem PDF.
"""
import argparse, glob, os, re, sqlite3, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(HERE, 'indeks.sqlite')
PAGE_RE = re.compile(r'^===== (?:strona|page) (\d+) =====$', re.M)
MSG = {
    'pol': dict(built='indeks: {f} plikow, {p} stron -> {db}', empty='BLAD: zero plikow ({f}) albo stron ({p}) - indeks pusty',
                noidx='brak indeksu - uruchom: python szukaj.py --buduj', noq='puste zapytanie', page='s.',
                hits='[{n} trafien{lim}]', lim=' (limit)'),
    'eng': dict(built='index: {f} files, {p} pages -> {db}', empty='ERROR: zero files ({f}) or pages ({p}) - empty index',
                noidx='no index - run: python szukaj.py --buduj', noq='empty query', page='p.',
                hits='[{n} hits{lim}]', lim=' (limit)'),
}


def fold(s: str) -> str:
    s = s.lower().replace('ł', 'l')
    s = unicodedata.normalize('NFD', s)
    return ''.join(c for c in s if not unicodedata.combining(c))


def build(lang: str):
    m = MSG[lang]
    if os.path.exists(DB):
        os.remove(DB)
    con = sqlite3.connect(DB)
    con.execute("CREATE VIRTUAL TABLE strony USING fts5(plik UNINDEXED, strona UNINDEXED, tekst UNINDEXED, zlozony, tokenize='unicode61')")
    con.execute("CREATE TABLE meta (k TEXT PRIMARY KEY, v TEXT)")
    con.execute("INSERT INTO meta VALUES ('lang', ?)", (lang,))
    n_files = n_pages = 0
    for path in sorted(glob.glob(os.path.join(HERE, '*.txt'))):
        parts = PAGE_RE.split(open(path, encoding='utf-8').read())
        n_files += 1
        for i in range(1, len(parts) - 1, 2):
            text = parts[i + 1].strip()
            con.execute('INSERT INTO strony VALUES (?,?,?,?)', (os.path.basename(path), int(parts[i]), text, fold(text)))
            n_pages += 1
    con.commit()
    if n_files == 0 or n_pages == 0:
        print(m['empty'].format(f=n_files, p=n_pages), file=sys.stderr)
        return 20
    print(m['built'].format(f=n_files, p=n_pages, db=DB))
    return 0


def term(w: str, lang: str, exact: bool, prefix: bool) -> str:
    if lang == 'pol' and not exact and len(w) >= 4:
        return '"' + (w[:max(4, len(w) - 2)] if len(w) >= 6 else w) + '"*'
    if lang == 'eng' and prefix and len(w) >= 3:
        return '"' + w + '"*'
    return '"' + w + '"'


def query(q: str, limit: int, exact: bool = False, prefix: bool = False):
    if not os.path.exists(DB):
        print(MSG['pol']['noidx'] + ' / ' + MSG['eng']['noidx'], file=sys.stderr)
        return 20
    con = sqlite3.connect(DB)
    try:
        lang = con.execute("SELECT v FROM meta WHERE k='lang'").fetchone()[0]
    except sqlite3.Error:
        lang = 'pol'    # indeks sprzed pola meta
    m = MSG.get(lang, MSG['pol'])
    words = [w for w in re.findall(r'\w+', fold(q)) if w]
    if not words:
        print(m['noq'], file=sys.stderr)
        return 2
    terms = [term(w, lang, exact, prefix) for w in words]
    rows = con.execute('SELECT plik, strona, tekst, zlozony FROM strony WHERE strony MATCH ? ORDER BY rank LIMIT ?',
                       (' '.join(terms), limit)).fetchall()
    anchor = terms[0].strip('"*')
    for plik, strona, tekst, zl in rows:
        i = max(0, zl.find(anchor))
        frag = ' '.join(tekst[max(0, i - 120):i + 200].split())
        print(f'{plik}  {m["page"]} {strona}\n    ...{frag}...\n')
    print(m['hits'].format(n=len(rows), lim=m['lim'] if len(rows) == limit else ''))
    return 0 if rows else 1


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('fraza', nargs='?')
    ap.add_argument('--buduj', '--build', dest='buduj', action='store_true')
    ap.add_argument('--lang', default='pol', choices=sorted(MSG))
    ap.add_argument('--limit', type=int, default=20)
    ap.add_argument('--dokladnie', '--exact', dest='dokladnie', action='store_true')
    ap.add_argument('--prefix', '--prefiks', dest='prefix', action='store_true')
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    sys.exit(build(a.lang) if a.buduj else query(a.fraza or '', a.limit, a.dokladnie, a.prefix))
