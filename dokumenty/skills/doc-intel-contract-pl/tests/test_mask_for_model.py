"""Maska dlugosciowa dla kopii do modelu: PII PL + sekrety, offsety nietkniete."""
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))

import mask_for_model as M  # noqa: E402

PESEL_OK = "44051401359"      # poprawna suma kontrolna
NIP_OK = "5260250274"          # poprawna suma kontrolna
IBAN = "PL61109010140000071219812874"


class MaskaDlugosc(unittest.TestCase):
    def test_dlugosc_zawsze_identyczna(self):
        for t in ("", "bez pii", f"PESEL {PESEL_OK} i mail a@b.pl", "x" * 500 + PESEL_OK):
            w = M.maskuj(t)
            self.assertEqual(len(w.tekst), len(t))

    def test_pesel_z_suma_kontrolna_zamaskowany_a_losowe_11_cyfr_nie(self):
        w = M.maskuj(f"PESEL {PESEL_OK} oraz numer 12345678901")
        self.assertIn("*" * 11, w.tekst)
        self.assertIn("12345678901", w.tekst)
        self.assertEqual([z["kategoria"] for z in w.zamaskowane], ["pesel"])

    def test_pozycje_pozostalych_znakow_nie_ruszaja_sie(self):
        t = f"Strona: Jan Kowalski, PESEL {PESEL_OK}, ul. Dluga 5"
        w = M.maskuj(t)
        i = t.index("ul. Dluga")
        self.assertEqual(w.tekst[i:i + 9], "ul. Dluga")
        self.assertEqual(w.tekst.index("Strona:"), 0)

    def test_offsety_w_wyniku_wskazuja_oryginal(self):
        t = f"Konto {IBAN} nadawcy"
        w = M.maskuj(t)
        z = w.zamaskowane[0]
        self.assertEqual(t[z["start"]:z["koniec"]], IBAN)
        self.assertEqual(w.tekst[z["start"]:z["koniec"]], "*" * len(IBAN))

    def test_email_i_nip_i_dowod(self):
        t = f"kontakt@kancelaria.pl NIP {NIP_OK} dowod ABC 123456"
        w = M.maskuj(t)
        kat = {z["kategoria"] for z in w.zamaskowane}
        self.assertEqual(kat, {"email", "nip", "dowod"})
        self.assertNotIn("kancelaria", w.tekst)

    def test_klucz_api_i_bearer_i_przypisanie(self):
        t = ('Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.abc.def\n'
             'API_KEY = "sk-live-9f2b71ce4a0011"\n'
             'ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        w = M.maskuj(t)
        self.assertNotIn("eyJhbGciOiJIUzI1NiJ9", w.tekst)
        self.assertNotIn("sk-live", w.tekst)
        self.assertNotIn("ghp_ABC", w.tekst)
        self.assertIn('API_KEY = "', w.tekst)   # nazwa zmiennej i cudzyslowy zostaja
        self.assertIn("Bearer ", w.tekst)
        self.assertEqual(w.tekst.count("\n"), 2)  # numery linii nietkniete

    def test_spacje_wewnatrz_zakresu_zostaja(self):
        t = "IBAN 61 1090 1014 0000 0712 1981 2874 koniec"
        w = M.maskuj(t)
        self.assertEqual(w.tekst.count(" "), t.count(" "))

    def test_bez_pii_bez_zmian(self):
        t = "Zwykle pismo procesowe bez danych. Sygn. II CSK 123/24."
        w = M.maskuj(t)
        self.assertEqual(w.tekst, t)
        self.assertEqual(w.liczba, 0)

    def test_deterministyczne(self):
        t = f"a {PESEL_OK} b {NIP_OK} c x@y.pl"
        self.assertEqual(M.maskuj(t).tekst, M.maskuj(t).tekst)

    def test_nakladajace_sie_zakresy_bez_podwojnego_liczenia(self):
        # 14 cyfr moze trafic REGON-14; wewnatrz mogloby siedziec 11 cyfr wygladajacych na PESEL
        t = "nr 12345678901234 x"
        w = M.maskuj(t)
        zakresy = [(z["start"], z["koniec"]) for z in w.zamaskowane]
        for i, a in enumerate(zakresy):
            for b in zakresy[i + 1:]:
                self.assertFalse(a[0] < b[1] and b[0] < a[1], "zakresy sie nakladaja")


if __name__ == "__main__":
    unittest.main()
