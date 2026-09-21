"""Testy akta-przeszukiwalne-pl. Rdzen z podmienionym OCR (bez zaleznosci), plus test
integracyjny z prawdziwym LiteParse, gdy biblioteka jest zainstalowana. Dane syntetyczne."""
from __future__ import annotations

import os
import subprocess
import sys
import types

import pytest

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(HERE, "scripts")
sys.path.insert(0, SCRIPTS)
import akta  # noqa: E402

SEKRET = "Zdanie z akt ktore nie moze trafic na ekran"


def _pdf(folder, name, payload):
    p = folder / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b"%PDF-1.4 " + payload.encode())
    return p


class FakeExt:
    """Udaje liteparse_extract.extract: tresc strony zalezy od bajtow pliku."""

    def __init__(self, spec):
        self.spec, self.calls = spec, 0

    def extract(self, path, tessdata=None, lang='pol'):
        self.calls += 1
        self.lang = lang
        key = open(path, "rb").read().decode().split(" ", 1)[1]
        pages, total = self.spec[key]
        return {"parser": {"version": "test"}, "total_pages": total, "page_errors": [],
                "pages": [{"number": i, "text": t, "image": True, "ocr": True} for i, t in enumerate(pages, 1)]}


def _run(tmp_path, monkeypatch, spec, files, lang='pol'):
    src = tmp_path / "akta"
    for name, payload in files:
        _pdf(src, name, payload)
    ext = FakeExt(spec)
    monkeypatch.setattr(akta, "load_extractor", lambda t: ext)
    out = tmp_path / "akta-tekst"
    rc = akta.run(str(src), str(out), None, lang)
    return rc, out, ext


def test_tekst_ze_stronami_raport_i_indeks(tmp_path, monkeypatch):
    spec = {"a": (["WYROK sygn. akt II K 1/24", "Opinia biegłej z Łodzi"], 2)}
    rc, out, _ = _run(tmp_path, monkeypatch, spec, [("wyrok.pdf", "a")])
    assert rc == 0
    txt = (out / "wyrok.txt").read_text(encoding="utf-8")
    assert "===== strona 2 =====" in txt and "# KOMPLET" in txt
    assert (out / "RAPORT.md").exists() and (out / "indeks.sqlite").exists()
    r = subprocess.run([sys.executable, str(out / "szukaj.py"), "lodzi"], capture_output=True, text=True, encoding="utf-8")
    assert "s. 2" in r.stdout and r.returncode == 0


def test_ta_sama_tresc_w_innym_pliku_jest_nazwana(tmp_path, monkeypatch):
    """Zmierzone 09-21 na prawdziwych aktach: plik o nazwie pisma byl kopia innego dokumentu."""
    spec = {"a": (["POSTANOWIENIE tresc"], 1), "b": (["POSTANOWIENIE   tresc"], 1)}
    rc, out, _ = _run(tmp_path, monkeypatch, spec, [("postanowienie.pdf", "a"), ("wniosek.pdf", "b")])
    raport = (out / "RAPORT.md").read_text(encoding="utf-8")
    assert rc == 10
    assert "Ten sam tekst w roznych plikach" in raport and "ta sama tresc co" in raport


def test_duplikat_bajtowy_czytany_raz(tmp_path, monkeypatch):
    spec = {"a": (["tekst"], 1)}
    rc, out, ext = _run(tmp_path, monkeypatch, spec, [("x/pismo.pdf", "a"), ("y/pismo.pdf", "a")])
    assert ext.calls == 1 and rc == 10
    assert "duplikat pliku" in (out / "RAPORT.md").read_text(encoding="utf-8")


def test_strona_nieczytelna_oznaczona_i_w_raporcie(tmp_path, monkeypatch):
    spec = {"a": (["strona jeden", ""], 2)}
    rc, out, _ = _run(tmp_path, monkeypatch, spec, [("pismo.pdf", "a")])
    assert rc == 10
    assert "[STRONA NIECZYTELNA" in (out / "pismo.txt").read_text(encoding="utf-8")
    assert "| 2 |" in (out / "RAPORT.md").read_text(encoding="utf-8")


def test_obciecie_stron_to_blokada_a_nie_sukces(tmp_path, monkeypatch):
    """Biblioteka potrafi zwrocic mniej stron niz ma plik, bez bledu (zmierzone 09-21)."""
    spec = {"a": (["jedna"], 3)}
    rc, out, _ = _run(tmp_path, monkeypatch, spec, [("teczka.pdf", "a")])
    txt = (out / "teczka.txt").read_text(encoding="utf-8")
    assert rc == 20
    assert "# KOMPLET" not in txt and txt.count("[STRONA POMINIETA") == 2


def test_wznowienie_pomija_gotowe_i_powtarza_niekompletne(tmp_path, monkeypatch):
    spec = {"a": (["gotowe"], 1), "b": (["urwane"], 2)}
    rc, out, ext = _run(tmp_path, monkeypatch, spec, [("a.pdf", "a"), ("b.pdf", "b")])
    assert ext.calls == 2
    ext2 = FakeExt(spec)
    monkeypatch.setattr(akta, "load_extractor", lambda t: ext2)
    akta.run(str(tmp_path / "akta"), str(out), None)
    assert ext2.calls == 1, "gotowy dokument pominiety, niekompletny czytany ponownie"


def test_wynik_w_folderze_akt_i_pusty_folder_blokuja(tmp_path):
    src = tmp_path / "akta"
    src.mkdir()
    assert akta.run(str(src), str(src / "wynik"), None) == 20
    assert akta.run(str(src), str(tmp_path / "w"), None) == 20, "zero PDF = blokada, nie sukces"


def test_na_ekran_trafiaja_tylko_liczby(tmp_path, monkeypatch, capsys):
    spec = {"a": ([SEKRET], 1)}
    _run(tmp_path, monkeypatch, spec, [("pismo.pdf", "a")])
    assert SEKRET not in capsys.readouterr().out


def test_paragraf_czytany_jako_dolar(tmp_path, monkeypatch):
    spec = {"a": (["art. 190a $ 1 k.k. i $ la"], 1)}
    rc, out, _ = _run(tmp_path, monkeypatch, spec, [("pismo.pdf", "a")])
    txt = (out / "pismo.txt").read_text(encoding="utf-8")
    assert "§ 1 k.k." in txt and "§ 1a" in txt and "$" not in txt.split("=====", 2)[2]


def test_zablokowana_biblioteka_daje_czytelny_komunikat(monkeypatch):
    fake = types.ModuleType("liteparse_extract")
    monkeypatch.setitem(sys.modules, "liteparse_extract", fake)
    real_import = __builtins__["__import__"] if isinstance(__builtins__, dict) else __builtins__.__import__

    def imp(name, *a, **k):
        if name == "liteparse":
            raise ImportError("DLL load failed while importing _liteparse")
        return real_import(name, *a, **k)
    monkeypatch.setattr("builtins.__import__", imp)
    with pytest.raises(SystemExit) as e:
        akta.load_extractor(akta.T['pol'])
    assert "Smart App Control" in str(e.value)


def test_parytet_ekstraktora_i_reguly_paragrafu():
    """Kopie z doc-intel-contract-pl nie moga sie rozjechac z kanonem (gdy kanon jest obok)."""
    canon = os.path.join(HERE, "..", "doc-intel-contract-pl", "scripts")
    if not os.path.isdir(canon):
        pytest.skip("doc-intel-contract-pl nieobecny - paczka samodzielna")
    mine = open(os.path.join(SCRIPTS, "liteparse_extract.py"), encoding="utf-8").read().split("\n", 2)[2]
    theirs = open(os.path.join(canon, "liteparse_extract.py"), encoding="utf-8").read()
    assert mine.replace("\r\n", "\n") == theirs.replace("\r\n", "\n")
    sys.path.insert(0, canon)
    from adapters import liteparse as ltp  # noqa: PLC0415
    for s in ["art. 410 $ 2", "$ la k.k.", "$$ 3", "kwota $ USD", "w $"]:
        assert akta.repair_paragraf(s) == ltp.repair_paragraf(s), s


def test_integracja_prawdziwy_ocr(tmp_path):
    """Prawdziwy LiteParse na wygenerowanym skanie - pomijany bez biblioteki."""
    pytest.importorskip("liteparse")
    fitz = pytest.importorskip("pymupdf")
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 100), "SAD REJONOWY WYROK 123", fontsize=20)
    pix = page.get_pixmap(dpi=200)
    scan = fitz.open()
    scan.new_page().insert_image(fitz.Rect(0, 0, 595, 842), stream=pix.tobytes("png"))
    src = tmp_path / "akta"
    src.mkdir()
    scan.save(str(src / "skan.pdf"))
    out = tmp_path / "akta-tekst"
    assert akta.run(str(src), str(out), os.environ.get("DOC_INTEL_TESSDATA"), "pol") in (0, 10)
    assert "WYROK" in (out / "skan.txt").read_text(encoding="utf-8")


# --- Wersja EN (searchable-case-files-en): ten sam kod, jezyk eng -------------

def test_eng_nie_rusza_kwot_w_dolarach(tmp_path, monkeypatch):
    """W angielskich aktach `$ 5,000` to kwota - naprawa paragrafu tylko dla pol."""
    spec = {"a": (["The claim is $ 5,000 plus $ 1 fee under section 12."], 1)}
    rc, out, ext = _run(tmp_path, monkeypatch, spec, [("claim.pdf", "a")], lang="eng")
    txt = (out / "claim.txt").read_text(encoding="utf-8")
    assert "$ 5,000" in txt and "$ 1 fee" in txt and "§" not in txt
    assert ext.lang == "eng"


def test_eng_raport_i_znaczniki_po_angielsku(tmp_path, monkeypatch):
    spec = {"a": (["first page", ""], 2), "b": (["first  page", ""], 2)}
    rc, out, _ = _run(tmp_path, monkeypatch, spec, [("a.pdf", "a"), ("b.pdf", "b")], lang="eng")
    rep = (out / "REPORT.md").read_text(encoding="utf-8")
    txt = (out / "a.txt").read_text(encoding="utf-8")
    assert rc == 10 and "Same text in different files" in rep and "same text as" in rep
    assert "===== page 2 =====" in txt and "[UNREADABLE PAGE" in txt and "# COMPLETE" in txt
    assert not (out / "RAPORT.md").exists()


def test_eng_wyszukiwarka_dokladna_z_opcja_prefiksu(tmp_path, monkeypatch):
    spec = {"a": (["The contractor signed", "A contract was void"], 2)}
    rc, out, _ = _run(tmp_path, monkeypatch, spec, [("c.pdf", "a")], lang="eng")
    run = lambda *a: subprocess.run([sys.executable, str(out / "szukaj.py"), *a], capture_output=True, text=True, encoding="utf-8")
    exact = run("contract")
    assert "p. 2" in exact.stdout and "p. 1" not in exact.stdout, "EN: 'contract' nie lapie 'contractor'"
    assert "p. 1" in run("contract", "--prefix").stdout


def test_domyslny_jezyk_z_pliku(tmp_path, monkeypatch):
    (tmp_path / "DEFAULT_LANG").write_text("eng", encoding="utf-8")
    monkeypatch.setattr(akta, "HERE", str(tmp_path))
    assert akta.default_lang() == "eng"
    (tmp_path / "DEFAULT_LANG").write_text("klingon", encoding="utf-8")
    assert akta.default_lang() == "pol", "nieznany jezyk -> pol, nie wyjatek"


def test_blizniaki_maja_identyczny_kod():
    """akta-przeszukiwalne-pl i searchable-case-files-en: ten sam kod, rozni je tylko DEFAULT_LANG."""
    root = os.path.dirname(HERE)
    other = [os.path.join(root, n, "scripts") for n in ("akta-przeszukiwalne-pl", "searchable-case-files-en")]
    if not all(os.path.isdir(d) for d in other):
        pytest.skip("brak drugiego blizniaka obok - paczka samodzielna")
    for f in ("akta.py", "szukaj.py", "liteparse_extract.py"):
        a, b = (open(os.path.join(d, f), encoding="utf-8").read().replace("\r\n", "\n") for d in other)
        assert a == b, f"{f} rozjechal sie miedzy blizniakami"
