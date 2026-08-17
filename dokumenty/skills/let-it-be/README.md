# matematic-anonimizacja-pl - "Let It Be"

[![CI](https://github.com/matematicsolutions/matematic-anonimizacja-pl/actions/workflows/ci.yml/badge.svg)](https://github.com/matematicsolutions/matematic-anonimizacja-pl/actions/workflows/ci.yml)

Samodzielny silnik **anonimizacji i pseudonimizacji polskich danych osobowych** w tekście. Offline, zero zależności zewnętrznych, deterministyczny - cała praca lokalnie, treść nie opuszcza maszyny (nie idzie do żadnego modelu ani API).

Skill MateMatic dla kancelarii i działów prawnych: wykrywa PESEL, NIP, REGON, KRS, numery telefonów, adresy e-mail, imiona i nazwiska oraz nazwy spółek i podmienia je na tokeny. Działa na trzy sposoby: jako skill Claude Code, jako CLI w terminalu i jako biblioteka.

## Dwa tryby - to nie to samo (RODO)

| | `anonimizuj` | `pseudonimizuj` |
|---|---|---|
| Odwracalność | nieodwracalna | odwracalna przez mapę |
| Mapa token↔oryginał | nie powstaje | zapisywana (chroń ją) |
| Podstawa RODO | motyw 26 (dane anonimowe poza RODO) | art. 4 pkt 5 (dane nadal osobowe) |
| Zastosowanie | publikacja, udostępnienie, anonimizacja akt | wysyłka treści do LLM i odzyskanie wyniku |

## Instalacja

Wymaga Node 20+. Zero zależności - nic do `npm install`.

```bash
git clone https://github.com/matematicsolutions/matematic-anonimizacja-pl
cd matematic-anonimizacja-pl
node --test          # 32 testy, powinny przejść
```

Jako skill Claude Code: skopiuj katalog do `~/.claude/skills/let-it-be/`.

## CLI

```bash
# Raport: co jest w dokumencie (nic nie zmienia)
node bin/cli.mjs wykryj pismo.txt

# Anonimizacja nieodwracalna
node bin/cli.mjs anonimizuj pismo.txt --out pismo-anon.txt

# Pseudonimizacja odwracalna + mapa + audit log
node bin/cli.mjs pseudonimizuj pismo.txt --map mapa.json --audit audit.log --out pismo-pseudo.txt
node bin/cli.mjs odwroc odpowiedz.txt --map mapa.json
```

Wejście `-` lub brak argumentu = stdin. Po podmianie obie komendy uruchamiają **bramkę "no PII leaves"**: jeśli jakiś oryginał przetrwał (np. fleksja nazwiska), operacja jest przerywana z kodem 2.

## Paczka dokumentów - odwracalna redakcja z jednolitą numeracją

`pseudonimizuj` działa na jednym dokumencie i w każdym pliku numeruje od nowa: `[OSOBA_1]` w pozwie i `[OSOBA_1]` w zeznaniu mogą być dwiema różnymi osobami. Przy sprawie złożonej z kilku pism to psuje korreferencję i utrudnia modelowi rozumowanie. Komenda `paczka` rozwiązuje to wspólnym słownikiem odwracania:

- **stabilny placeholder** per (kategoria, wartość znormalizowana) - ten sam byt w każdym pliku paczki to ten sam `[OSOBA_1]`,
- **jednolita numeracja między plikami** - liczniki nie resetują się per plik,
- **słownik przeżywa restart** - kolejne wywołanie z tym samym `--slownik` kontynuuje numerację, znane wartości trzymają stare placeholdery.

```bash
# 1. Pseudonimizacja paczki (sidecar *.mapa-pii.json powstaje obok)
node bin/cli.mjs paczka pozew.txt zeznanie.txt --slownik sprawa.mapa-pii.json --audit audit.log
# -> pozew.pseudo.txt, zeznanie.pseudo.txt

# 2. Człowiek wysyła pliki *.pseudo.txt do LLM i zapisuje odpowiedź.

# 3. Przywrócenie oryginałów w odpowiedzi - lokalnie
node bin/cli.mjs przywroc odpowiedz-llm.txt --slownik sprawa.mapa-pii.json --out odpowiedz-jawna.txt

# 4. Dokument doszedł później? Dołóż go - numeracja jest kontynuowana.
node bin/cli.mjs paczka aneks.txt --slownik sprawa.mapa-pii.json
```

`przywroc` raportuje na stderr placeholdery, których słownik nie zna (pochodzą z innej paczki albo zmyślił je model) - to sygnał do ręcznej weryfikacji. Bramka "no PII leaves" dla paczki jest szersza niż dla pojedynczego pliku: każdy wynik jest sprawdzany przeciw wszystkim oryginałom słownika, także tym z innych plików i z poprzednich sesji; przy porażce nic nie jest zapisywane.

### Plik `*.mapa-pii.json` to dane wrażliwe

Słownik odwracania zawiera oryginały PII - to jest klucz do całej pseudonimizacji. Konwencja `*.mapa-pii.json` istnieje po to, żeby nazwa pliku sama ostrzegała każdego, kto go zobaczy. Zasady: nie wysyłaj do LLM, nie commituj do repo, nie udostępniaj; utrata pliku = utrata możliwości odwrócenia. Do transferu użyj `encryptArchive` (AES-256-GCM).

### Granica governance

Narzędzie **przygotowuje** teksty z placeholderami i **przywraca** oryginały - wyłącznie lokalnie. Niczego samo nie wysyła; o tym, co idzie do LLM, decyduje człowiek. Wariant `AuditLog.appendLlmCallOut` pozwala dodatkowo zatrzymać wysyłkę, jeśli w tekście zostało cokolwiek z oryginałów.

### Biblioteka (paczka)

```js
import { pseudonimizujPaczke, przywroc, SlownikOdwracania } from "matematic-anonimizacja-pl";

const { wyniki, slownik } = pseudonimizujPaczke([
  { nazwa: "pozew.txt", text: "..." },
  { nazwa: "zeznanie.txt", text: "..." },
]);
// eksport/import JSON (przeżywa restart):
const json = slownik.toJSON();
const wznowiony = SlownikOdwracania.fromJSON(json);
const { text, nieznanePlaceholdery } = przywroc(odpowiedzLlm, wznowiony);
```

### Roadmap v2

- Tryb `.docx` z zachowaniem tracked changes (podmiana na poziomie runs, mapping w sidecarze) - dziś silnik jest tekstowy, `.docx` wymaga osobnej ścieżki.

Wzorce tej warstwy (pattern, nie kod): [Rizzo-AI-Academy/rizzo-pii](https://github.com/Rizzo-AI-Academy/rizzo-pii) (MIT) - stabilny placeholder + słownik odwracania z eksportem/importem; [moyupeng0422/legal-doc-redactor](https://github.com/moyupeng0422/legal-doc-redactor) (MIT) - jednolita numeracja w batchu + mapping w sidecarze. Szczegóły: [THIRD_PARTY_INSPIRATIONS.md](THIRD_PARTY_INSPIRATIONS.md).

## Biblioteka

```js
import { pseudonimizuj, anonimizuj, odwroc, detect } from "matematic-anonimizacja-pl";

const a = anonimizuj("Powód Jan Kowalski, PESEL 44051401359.");
// a.text  -> "Powód [OSOBA_1], PESEL [PESEL_1]."
// a.counts -> { OSOBA: 1, PESEL: 1 }

const p = pseudonimizuj("Jan Kowalski, NIP 5260250274");
const wynik = odwroc(p.text, p.map); // odtwarza oryginał
```

### Wzorce operacyjne (z PII-Shield)

```js
import { MappingStore, encryptArchive, decryptArchive, AuditLog } from "matematic-anonimizacja-pl";

// TTL na mapy sesji (domyślnie 7 dni) + cleanup
const store = new MappingStore({ dir: ".sesje", ttlMs: 7 * 864e5 });
await store.save("sesja-123", { map: p.map, sourceHash: p.sourceHash, entities: p.counts });
await store.cleanup(); // usuwa wygasłe

// Szyfrowane archiwum mapy (AES-256-GCM, klucz scrypt) - bezpieczny transfer
const blob = encryptArchive({ map: p.map }, "hasło");
const odzyskane = decryptArchive(blob, "hasło");

// Audit log plain-text dla Inspektora RODO (AI Act art. 12)
await new AuditLog("audit.log").append({ event: "anonimizacja-applied", entities: a.counts });
```

## Co wykrywa

| Typ | Metoda | Confidence |
|---|---|---|
| PESEL, NIP, REGON | checksuma urzędowa | 1.0 |
| IBAN / NRB | checksuma mod-97 (ISO 13616) | 1.0 |
| KRS | format 10 cyfr + prefiks | 0.95 |
| e-mail | regex | 0.9 |
| dowód osobisty | checksuma (3 litery + 6 cyfr) | 0.9 |
| telefon (z/bez +48) | regex + 9 cyfr krajowych | 0.85 |
| imię i nazwisko | gazetteer imion + heurystyka | 0.85 |
| firma z formą prawną | regex (Sp. z o.o., S.A. ...) | 0.75 |
| adres (ulica + numer) | regex (ul./al./pl./os.) | 0.7 |
| adres (kod pocztowy NN-NNN) | regex | 0.6 |
| sygnatury SN/NSA/WSA/KIO/TK, CELEX, ELI | regex | 0.6-1.0 (domyślnie **nie** podmieniane - to nie PII) |

Próg czułości regulujesz flagą `--min-confidence <n>` (np. `--min-confidence 0.9` zostawia PESEL/NIP/REGON/IBAN, KRS, dowód i e-mail, a odsiewa telefon, osobę i adres).

`Confidence` to pewność, że dopasowanie jest poprawne **formalnie** (np. checksuma przeszła, format się zgadza) - nie gwarancja, że ciąg należy do realnej osoby. Losowy ciąg 11 cyfr może przejść checksumę PESEL. Dlatego nadal obowiązuje weryfikacja przez prawnika.

## Ograniczenia

- **Fleksja**: imiona i nazwiska w odmianie ("Kowalskiego") nie zawsze są łapane poza pierwszym wystąpieniem. Bramka residual to wykryje i zatrzyma - zweryfikuj dokument.
- **Gazetteer imion**: ~120 najczęstszych. Rzadkie lub obce imiona mogą umknąć.
- **Daty urodzenia, paszport, prawo jazdy, PWZ**: poza zakresem v0.2.0.
- **`.docx` z tracked changes**: roadmap v2 - dziś silnik jest tekstowy.
- **Adres**: łapane `ul./al./pl./os. Nazwa numer` i kod pocztowy; adres bez prefiksu ulicy może umknąć.
- To narzędzie **wspomaga**, nie zastępuje weryfikacji przez prawnika.

## Pochodzenie

- **Logika polskich PII** (checksumy PESEL/NIP/REGON/KRS, regexy sygnatur sądów, gazetteer) pochodzi z własnej biblioteki MateMatic `pl-entities` (projekt Patron). Detekcja osób przez gazetteer imion oraz rozwiązywanie nakładających się spanów - dopisane tutaj od zera (czego `pl-entities` nie miał).
- **Wzorce operacyjne** (TTL na mapy, source_hash, audit log "proves no PII leaves", szyfrowane archiwum AES-GCM) - pattern strukturalny cherry-pick z [gregmos/PII-Shield](https://github.com/gregmos/PII-Shield) (MIT), napisany od zera w czystym ESM. Pełna atrybucja: [THIRD_PARTY_INSPIRATIONS.md](THIRD_PARTY_INSPIRATIONS.md).

To nie jest tłumaczenie 1:1 - to przepisanie pod polski rynek prawniczy z funkcjami, których źródła nie miały: deterministyczną detekcją osób, rozwiązywaniem nakładających się dopasowań i dwoma trybami RODO.

## Licencja

Apache-2.0. Patrz [LICENSE](LICENSE) i [governance/CONSTITUTION.md](governance/CONSTITUTION.md).

Cytowanie: *MateMatic Solutions (2026), Let It Be - anonimizacja danych po polsku, https://github.com/matematicsolutions/matematic-anonimizacja-pl, Apache-2.0.*

---

> *"Speaking words of wisdom, let it be."* Puść dokument w świat - bez danych osobowych w środku.
