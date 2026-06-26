---
name: let-it-be
description: Anonimizacja i pseudonimizacja polskich danych osobowych (PESEL, NIP, REGON, KRS, telefon, e-mail, imiona i nazwiska, nazwy firm) w tekscie - RODO-safe, offline, deterministycznie (bez wysylania tresci do modelu). Uzywaj gdy uzytkownik chce zanonimizowac lub spseudonimizowac dokument, usunac dane osobowe z pisma, przygotowac tekst do publikacji albo do wyslania do LLM, lub mowi o PESEL/NIP/REGON/RODO/anonimizacji/pseudonimizacji.
---

# Let It Be - anonimizacja danych po polsku

Silnik bez zaleznosci zewnetrznych (Node >=20). Wykrywa polskie PII checksumowo
(PESEL/NIP/REGON/KRS/IBAN/dowod osobisty), heurystycznie (imiona z gazetteera,
firmy z forma prawna, e-mail, telefon, adres) i podmienia na tokeny. Dwa tryby
RODO. Cala praca lokalnie.

## Safety Tiers (KRYTYCZNE - dane osobowe)

| Tier | Operacje | Reguła |
|------|----------|--------|
| **R - Read-only** | `wykryj` (tylko raport, nic nie zmienia) | Bez potwierdzenia. Wykonaj od razu. |
| **M - Mutating** | `pseudonimizuj` + `odwroc` (odwracalne przez mapę) | Pokaż co zostanie zmienione. Czekaj na potwierdzenie słowne. |
| **D - Destructive** | `anonimizuj` (NIEODWRACALNE - mapa nie powstaje, danych nie przywrócisz) | Użytkownik musi wpisać dosłownie: **"potwierdzam"** zanim wykonasz. |

> Dotyczy zwłaszcza akt klientów i pism procesowych - `anonimizuj` na oryginale bez kopii = nieodwracalna utrata danych osobowych.

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
```

Wejscie `-` lub brak = stdin. Wynik na stdout albo do `--out`.

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
- Daty urodzenia, paszport, prawo jazdy, PWZ - poza zakresem v0.1.0.
- Adres bez prefiksu ulicy (ul./al./pl./os.) moze umknac.
- To narzedzie wspomaga, **nie zastepuje** weryfikacji przez prawnika.

## Biblioteka (programowo)

```js
import { pseudonimizuj, anonimizuj, odwroc } from "matematic-anonimizacja-pl";
const r = anonimizuj("Jan Kowalski, PESEL 44051401359");
// r.text -> "[OSOBA_1], PESEL [PESEL_1]"
```

Pelne API i wzorce operacyjne (TTL, szyfrowane archiwum, audit log): [README.md](README.md).
