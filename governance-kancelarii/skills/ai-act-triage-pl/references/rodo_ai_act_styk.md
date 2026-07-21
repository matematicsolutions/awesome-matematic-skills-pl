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

## Polska ustawa wdrozeniowa (stan do WERYFIKACJI)

AI Act jest rozporzadzeniem UE - obowiazuje bezposrednio, ale wymaga krajowego
wyznaczenia organow nadzoru i przepisow proceduralnych.

- **Projekt ustawy o systemach sztucznej inteligencji** przygotowany przez
  Ministerstwo Cyfryzacji, przyjety przez Rade Ministrow **31 marca 2026**.
  Na dzien budowy tego skilla (2026-07-21) jest w procesie legislacyjnym -
  **zweryfikuj aktualny status i tekst przed cytowaniem w memo dla klienta.**
- Ustawa ustanawia **Komisje Rozwoju i Bezpieczenstwa Sztucznej Inteligencji
  (KRiBSI)** jako krajowy organ nadzoru rynku dla systemow AI i pojedynczy punkt
  kontaktowy wobec instytucji UE.
- Sklad KRiBSI ma obejmowac przedstawicieli **UOKiK, KNF, KRRiT i UKE**.
- Zadania: kontrola zgodnosci, wydawanie decyzji i nakazow, rejestr skarg,
  indywidualne opinie i wyjasnienia, piaskownice regulacyjne (regulatory
  sandboxes), dzialalnosc informacyjno-edukacyjna.
- Termin krajowy na ramy organow: **2 sierpnia 2026** (zgodnie z art. 113 AI Act
  dla obowiazkow wysokiego ryzyka z tytulu III).

**Governance MateMatic:** organ krajowy jest sparametryzowany, nie zaszyty w
kodzie skryptow - gdy ustawa wejdzie w zycie, zaktualizuj TE referencje (nie kod).
Nie podawaj klientowi statusu "obowiazuje" dopoki nie potwierdzisz publikacji w
Dzienniku Ustaw.

## Zrodla (stan na 2026-07-21)

- [Ministerstwo Cyfryzacji - projekt ustawy przyjety przez RM](https://www.gov.pl/web/cyfryzacja/koniec-ery-nieuchwytnych-algorytmow--projekt-ustawy-o-systemach-sztucznej-inteligencji-przyjety-przez-rade-ministrow)
- [KPRM - projekt ustawy o systemach sztucznej inteligencji](https://www.gov.pl/web/premier/projekt-ustawy-o-systemach-sztucznej-inteligencji)
- [rp.pl - ustawa o AI, komisja ds. AI i piaskownice regulacyjne](https://www.rp.pl/prawo-w-polsce/art44606901-sejm-przyjal-ustawe-o-sztucznej-inteligencji-komisja-ds-ai-i-piaskownice-regulacyjne-dla-firm)
- [Sejm - druk 2443 (przebieg procesu)](https://orka.sejm.gov.pl/proc10.nsf/ustawy/2443_u.htm)

Pelny tekst rozporzadzenia unijnego 2024/1689: pobierz przez `eu-sparql-search`
(CELEX `32024R1689`), zweryfikuj cytat `citation-grounding-pl`.
