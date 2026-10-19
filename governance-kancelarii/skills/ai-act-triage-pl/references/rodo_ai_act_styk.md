# Styk AI Act <-> RODO + polska warstwa wdrozeniowa

Referencja pokazujaca, gdzie klasyfikacja AI Act zazebia sie z RODO, oraz gdzie
wchodzi polskie prawo krajowe. To warstwa wartosci dodanej MateMatic ponad
oryginalny upstream (ktory jest jurysdykcyjnie neutralny/anglojezyczny).

## Dlaczego oba akty naraz

Wiekszosc systemow AI przetwarza dane osobowe (dane treningowe, dane wejsciowe,
wyniki). Wtedy obowiazuja RÓWNOLEGLE AI Act i RODO - to dwa niezalezne rezimy,
nie alternatywa.

| Punkt styku | AI Act | RODO | Skill MateMatic |
|---|---|---|---|
| Dane treningowe / jakosc | art. 10 (zarzadzanie danymi, ograniczanie stronniczosci) | art. 5, 6, 9 (podstawa prawna, dane wrazliwe) | `rodo-ropa-dpa-pl` |
| Ocena ryzyka przed wdrozeniem | art. 27 OWPP (prawa podstawowe) | art. 35 DPIA (ochrona danych) | `rodo-dpia-pl` |
| Transparentnosc wobec osoby | art. 50 (info: "to jest AI") | art. 13-14 (obowiazek informacyjny) | - |
| Decyzje zautomatyzowane | art. 86 (prawo do wyjasnienia) | art. 22 (zakaz decyzji wylacznie zautomatyzowanej + prawo do interwencji) | - |
| Rejestrowanie / logi | art. 12 (logi systemu wysokiego ryzyka) | art. 5 ust. 2 (rozliczalnosc) | - |

**Praktyka:** OWPP (art. 27 AI Act) i DPIA (art. 35 RODO) to osobne oceny, ale
moga byc prowadzone jako jeden skoordynowany proces - motyw 96 AI Act wprost na
to pozwala. Nie rob ich dwa razy od zera; zmapuj wspolne elementy.

## Polska ustawa wdrozeniowa (stan na 2026-10-19)

AI Act jest rozporzadzeniem UE - obowiazuje bezposrednio, ale wymaga krajowego
wyznaczenia organow nadzoru i przepisow proceduralnych.

- **Ustawa z dnia 3 lipca 2026 r. o systemach sztucznej inteligencji
  (Dz.U. 2026 poz. 1003)** - uchwalona (druk sejmowy 2443), opublikowana, status
  w ISAP: obowiazuje. Sprawdzone w Repertorium (`eli:DU/2026/1003`) 2026-10-19.
  Przed cytowaniem przepisu w memo dla klienta pobierz jego tekst; termin
  wejscia w zycie poszczegolnych przepisow sprawdz w przepisach koncowych ustawy.
- Ustawa ustanawia **Komisje Rozwoju i Bezpieczenstwa Sztucznej Inteligencji
  (KRiBSI)** jako krajowy organ nadzoru rynku dla systemow AI. Przewodniczacy
  KRiBSI powolany uchwala Sejmu z 18 wrzesnia 2026 r. za zgoda Senatu z 24 wrzesnia
  2026 r. (M.P. 2026 poz. 945 i 946).
- Sklad i zadania KRiBSI (wg projektu: przedstawiciele UOKiK, KNF, KRRiT i UKE;
  kontrola zgodnosci, decyzje i nakazy, skargi, opinie, piaskownice regulacyjne,
  edukacja) - [DO SPRAWDZENIA w tekscie uchwalonej ustawy].
- Terminy AI Act dla wysokiego ryzyka przesunelo rozporzadzenie (UE) 2026/1744:
  zalacznik III od 2 grudnia 2027 r., zalacznik I od 2 sierpnia 2028 r.
  (art. 113 akapit trzeci lit. c AI Act w nowym brzmieniu).

**Governance MateMatic:** organ krajowy jest sparametryzowany, nie zaszyty w
kodzie skryptow - przy zmianie ustawy zaktualizuj TE referencje (nie kod).

## Zrodla (stan na 2026-10-19)

- [Ustawa o systemach sztucznej inteligencji, Dz.U. 2026 poz. 1003 (Sejm ELI)](https://api.sejm.gov.pl/eli/acts/DU/2026/1003)
- [Rozporzadzenie (UE) 2026/1744 (EUR-Lex)](https://eur-lex.europa.eu/eli/reg/2026/1744/oj)

Zrodla z etapu projektu (stan na 2026-07-21):

- [Ministerstwo Cyfryzacji - projekt ustawy przyjety przez RM](https://www.gov.pl/web/cyfryzacja/koniec-ery-nieuchwytnych-algorytmow--projekt-ustawy-o-systemach-sztucznej-inteligencji-przyjety-przez-rade-ministrow)
- [KPRM - projekt ustawy o systemach sztucznej inteligencji](https://www.gov.pl/web/premier/projekt-ustawy-o-systemach-sztucznej-inteligencji)
- [rp.pl - ustawa o AI, komisja ds. AI i piaskownice regulacyjne](https://www.rp.pl/prawo-w-polsce/art44606901-sejm-przyjal-ustawe-o-sztucznej-inteligencji-komisja-ds-ai-i-piaskownice-regulacyjne-dla-firm)
- [Sejm - druk 2443 (przebieg procesu)](https://orka.sejm.gov.pl/proc10.nsf/ustawy/2443_u.htm)

Pelny tekst rozporzadzenia unijnego 2024/1689: pobierz przez `eu-sparql-search`
(CELEX `32024R1689`), zweryfikuj cytat `citation-grounding-pl`.
