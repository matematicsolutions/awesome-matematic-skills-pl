---
name: let-it-be
description: Anonimizacja i pseudonimizacja polskich danych osobowych (PESEL, NIP, REGON, KRS, telefon, e-mail, imiona i nazwiska, nazwy firm) w tekscie - RODO-safe, offline, deterministycznie (bez wysylania tresci do modelu). Uzywaj gdy uzytkownik chce zanonimizowac lub spseudonimizowac dokument, usunac dane osobowe z pisma, przygotowac tekst do publikacji albo do wyslania do LLM, lub mowi o PESEL/NIP/REGON/RODO/anonimizacji/pseudonimizacji.
license: Apache-2.0
allowed-tools: [Bash, Read, Write]
data-residency: local
requires-human-approval: true
pii-egress: none
---

# Let It Be - anonimizacja danych po polsku

Samodzielny silnik (zero zaleznosci, Node >=20). Wykrywa polskie PII checksumowo
(PESEL/NIP/REGON/KRS/IBAN/dowod osobisty), heurystycznie (imiona z gazetteera,
firmy z forma prawna, e-mail, telefon, adres) i podmienia na tokeny. Dwa tryby
RODO. Cala praca lokalnie.

## Safety Tiers (KRYTYCZNE - dane osobowe)

| Tier | Operacje | Regula |
|------|----------|--------|
| **R - Read-only** | `wykryj` (tylko raport, nic nie zmienia) | Bez potwierdzenia. Wykonaj od razu. |
| **M - Mutating** | `pseudonimizuj` + `odwroc`, `paczka` + `przywroc` (odwracalne przez mape/slownik) | Pokaz co zostanie zmienione. Czekaj na potwierdzenie slowne. |
| **D - Destructive** | `anonimizuj` (NIEODWRACALNE - mapa nie powstaje, danych nie przywrocisz) | Uzytkownik musi wpisac doslownie: **"potwierdzam"** zanim wykonasz. |

> Dotyczy zwlaszcza akt klientow i pism procesowych - `anonimizuj` na oryginale bez kopii = nieodwracalna utrata danych osobowych. Slownik `*.mapa-pii.json` zawiera oryginaly PII - chron go, nie wysylaj do LLM, nie commituj.

---

## Quick start

Z katalogu skilla:

```bash
# Raport co jest w dokumencie (nic nie zmienia)
node bin/cli.mjs wykryj pismo.txt

# ANONIMIZACJA - nieodwracalna, do publikacji/dzielenia (brak mapy)
node bin/cli.mjs anonimizuj pismo.txt --out pismo-anon.txt

# PSEUDONIMIZACJA - odwracalna, do pracy z LLM (zapisuje mape)
node bin/cli.mjs pseudonimizuj pismo.txt --map mapa.json --out pismo-pseudo.txt
node bin/cli.mjs odwroc odpowiedz-llm.txt --map mapa.json   # przywraca oryginaly

# PACZKA - odwracalna redakcja WIELU plikow, jednolita numeracja (v0.2.0)
node bin/cli.mjs paczka pozew.txt zeznanie.txt --slownik sprawa.mapa-pii.json
node bin/cli.mjs przywroc odpowiedz-llm.txt --slownik sprawa.mapa-pii.json
```

Wejscie `-` lub brak = stdin. Wynik na stdout albo do `--out`.

## Workflow: paczka dokumentow do LLM (v0.2.0)

Gdy sprawa sklada sie z kilku pism, `paczka` trzyma JEDEN slownik odwracania:
ten sam byt w kazdym pliku = ten sam `[OSOBA_1]`, liczniki nie resetuja sie
per plik, a kolejne wywolanie z tym samym `--slownik` kontynuuje numeracje
(takze po restarcie). `przywroc` podstawia oryginaly w odpowiedzi LLM lokalnie
i ostrzega o placeholderach, ktorych slownik nie zna (zmyslone przez model).

1. `paczka pozew.txt zeznanie.txt --slownik sprawa.mapa-pii.json --audit audit.log`
2. Czlowiek wysyla pliki `*.pseudo.txt` do modelu, odbiera odpowiedz.
3. `przywroc odpowiedz.txt --slownik sprawa.mapa-pii.json --out odpowiedz-jawna.txt`
4. Doszedl nowy dokument? `paczka aneks.txt --slownik sprawa.mapa-pii.json` - numeracja kontynuowana.

Granica governance: narzedzie przygotowuje i przywraca LOKALNIE, niczego samo
nie wysyla - co idzie do LLM decyduje czlowiek.

## Wybor trybu (RODO)

| Cel | Tryb | Czemu |
|---|---|---|
| Udostepnic dokument na zewnatrz, opublikowac, anonimizacja akt | `anonimizuj` | Nieodwracalne. Mapa NIE powstaje. RODO motyw 26 - dane zanonimizowane nie podlegaja RODO. |
| Wyslac tresc do LLM (Gemini/Claude/...) i odzyskac wynik | `pseudonimizuj` + `odwroc` | Odwracalne przez mape. RODO art. 4 pkt 5 - dane nadal osobowe, trzymaj mape bezpiecznie. |

## Workflow: dokument do LLM

1. `pseudonimizuj pismo.txt --map mapa.json --audit audit.log` -> tekst z tokenami + mapa.
2. Wyslij tekst z tokenami do modelu, odbierz odpowiedz.
3. `odwroc odpowiedz.txt --map mapa.json` -> odpowiedz z prawdziwymi danymi.
4. Mapa wygasa wg TTL (domyslnie 7 dni) - patrz `MappingStore` w README.

## Bramka "no PII leaves"

Obie komendy po podmianie sprawdzaja, czy zaden oryginal nie przetrwal
(np. przez fleksje nazwiska). Jezeli cos zostalo - **operacja jest przerywana**
z kodem wyjscia 2 i komunikatem na stderr, zeby zweryfikowac recznie.

## Ograniczenia (przeczytaj)

- Fleksja: "Kowalski" zlapane, ale "Kowalskiego/Kowalskiemu" w innym miejscu - nie
  zawsze. Bramka residual to wykryje i zatrzyma; przejrzyj dokument.
- Imiona: gazetteer ~120 najczestszych. Rzadkie/obce imie moze umknac.
- Daty urodzenia, paszport, prawo jazdy, PWZ - poza zakresem v0.2.0.
- Adres bez prefiksu ulicy (ul./al./pl./os.) moze umknac.
- Tryb `.docx` z tracked changes - roadmap v2 (silnik jest tekstowy).
- To narzedzie wspomaga, **nie zastepuje** weryfikacji przez prawnika.

## Biblioteka (programowo)

```js
import { pseudonimizuj, anonimizuj, odwroc } from "matematic-anonimizacja-pl";
const r = anonimizuj("Jan Kowalski, PESEL 44051401359");
// r.text -> "[OSOBA_1], PESEL [PESEL_1]"

// paczka (v0.2.0): wspolny slownik, jednolita numeracja, restart-safe
import { pseudonimizujPaczke, przywroc, SlownikOdwracania } from "matematic-anonimizacja-pl";
const { wyniki, slownik } = pseudonimizujPaczke([{ nazwa: "pozew.txt", text: "..." }]);
const wznowiony = SlownikOdwracania.fromJSON(slownik.toJSON());
const { text } = przywroc(odpowiedzLlm, wznowiony);
```

Pelne API i wzorce operacyjne (TTL, szyfrowane archiwum, audit log): [README.md](README.md).
