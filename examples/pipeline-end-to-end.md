# Przyklad - 6-warstwowy lancuch walidacji outputu LLM

Ten dokument pokazuje, jak 14 skilli z tego hubu lacza sie w jeden lancuch
walidacji wokol pisma prawnego. Wszystkie dane w przykladzie sa **syntetyczne**
(`Jan Kowalski` to polski odpowiednik John Doe). Hub konsekwentnie respektuje
tajemnice adwokacka (art. 6 PrAdw) i radcowska (art. 3 RadcPrU) - patrz
SECURITY.md i AGENTS.md.

## Scenariusz

Hipotetyczny brief (wszystkie dane fikcyjne): klient prosi o opinie prawna na
temat klauzuli kar umownych w umowie B2B (dostawa uslug IT). Zakres - czy
klauzula jest skuteczna pod art. 484 k.c. + ewentualne miarkowanie kary pod
art. 484 § 2 k.c. Hipotetyczna ekspozycja klienta: ok. 0,5 mln zl, hipotetyczny
deadline: 7 dni.

## Sciezka przez lancuch

```
brief klienta + umowa.docx
        |
        v
1. intake-sufficiency-pl   --(luki / pytania uzupelniajace)--> klient
        |
        v
2. legal-request-router-pl   --(decyzja: high-stakes => pelna sciezka)
        |
        v
3. wlasciwa analiza (LLM + saos-orzecznictwo + eu-sparql-search)
        |
        v
4. citation-grounding-pl    --(weryfikacja Art. 484 + cytaty SN/SA)
        |
        v
5. adversarial-legal-review-pl   --(builder/attacker/synthesizer/verifier)
        |
        v
6. deliverable-fidelity-pl   --(czy zadna flaga RED nie wypadla)
        |
        v
7. redline-docx-pl (opcjonalnie)   --(jezeli klient chce redline umowy)
        |
        v
8. legal-ai-audit-bundle   --(SHA256 manifest, AI Act art. 12)
        |
        v
deliverable.docx + audit/
```

## Krok po kroku

### Warstwa 0: konwersja dokumentow zrodlowych

Klient przyslal `umowa.docx`. Konwertujemy do markdown na potrzeby pracy LLM:

```bash
# alternatywa A: prosty PDF/Word -> Markdown
markitdown umowa.docx > umowa.md

# alternatywa B: skomplikowany PDF z tabelami (np. KRS, postanowienie sadu)
opendataloader-pdf input.pdf -o input.md
```

Zachowujemy strukture (headings, tabele, listy) bez metadanych autora.

### Warstwa 1: intake-sufficiency-pl

Bramka wejsciowa - czy brief wystarczy, by zaczac?

Wejscie: brief klienta + umowa.md.

Wyjscie:
- ocena "ile mam dosc kontekstu?" (skala 1-5)
- lista luk (np. "brak informacji o branzy klienta", "brak informacji o stosunku negocjacyjnym")
- 3-5 pytan uzupelniajacych do klienta
- szkielet karty zlecenia

Jezeli ocena < 3 - wstrzymujemy sie i pytamy klienta. Nie pracujemy na niepelnym briefie.

### Warstwa 2: legal-request-router-pl

Klasyfikator zadania. Patrzy na cele, zakres, stawke, deadline.

Wyjscie - decyzja:
- `quick` - zwykla odpowiedz, bez warstw 4-6
- `grounded` - + warstwa 4 (citation-grounding-pl)
- `high-stakes` - + warstwa 4 + 5 (adversarial) + 6 (fidelity) + 7 (audit-bundle)

W naszym scenariuszu (ekspozycja 0,5 mln zl, sprawa potencjalnie sadowa)
router zwraca `high-stakes`.

### Warstwa 3: wlasciwa analiza

Tu LLM pracuje na briefie i umowie. Skille z hubu wspomagaja:
- `saos-orzecznictwo` - szukamy orzecznictwa SN i SA o miarkowaniu kar umownych pod art. 484 § 2 k.c.
- `eu-sparql-search` - dyrektywa 2011/7/UE o opoznieniach w platnosciach (kontekst B2B)
- `legal-data-hunter-pl` - jezeli potrzebujemy harvest opinii UOKiK lub KIS

Wyjscie: draft opinii.docx (markdown roboczy) z cytatami orzecznictwa.

### Warstwa 4: citation-grounding-pl

Mechaniczna weryfikacja - czy KAZDY cytat z draftu istnieje w zrodle?

Wyjscie:
- raport cytatow:
  - `Art. 484 k.c.` - znaleziono w isap.sejm.gov.pl, OK
  - `wyrok SN z dnia 8 sierpnia 2008 r., V CSK 85/08` - znaleziono w SAOS, OK
  - `wyrok SA w Krakowie z dnia 12 marca 2024 r., I ACa 1234/24` - **BRAK w SAOS**, RED FLAG

Halucynacje wylapane mechanicznie, nie "na oko" przez recenzenta.

### Warstwa 5: adversarial-legal-review-pl

Czerwony zespol dla pisma:
- **builder** - buduje najmocniejsza wersje tezy ("klauzula jest skuteczna i nie podlega miarkowaniu")
- **attacker** - kontrargumenty + kontr-orzecznictwo (przyklad hipotetyczny: "kontr-orzecznictwo SN o miarkowaniu kary umownej bez wniosku strony, sprawdz aktualne wyroki w SAOS przez `saos-orzecznictwo` przed cytowaniem")
- **synthesizer** - godzi: gdzie teza jest najmocniejsza, gdzie najslabsza
- **verifier** - 10-punktowa kontrola koncowa

Wyjscie: lista wzmocnien tezy i lista ryzyk z poziomami (RED / YELLOW / GREEN).

Ta warstwa ma bramke kosztu - uruchamia sie tylko gdy router zwrocil `high-stakes`.

### Warstwa 6: deliverable-fidelity-pl

Po obsludze zarzutow adversarial + naprawieniu cytatow - finalny dokument
gotowy do wyslania. Ale - czy zadna flaga RED z analizy nie wypadla z
podsumowania?

Wyjscie:
- mechaniczny check (skrypt): kazda flaga RED z warstwy 5 → grep w finalnym docx
- osad LLM na 3 najciezszych ustaleniach: czy zostaly zachowane w executive summary
- jezeli pominieto choc 1 RED - blokada deliverable, wracamy do warstwy 5

### Warstwa 7 (opcjonalnie): redline-docx-pl

Jezeli klient chce nie tylko opinii, ale tez konkretnych zmian w umowie:

```bash
uvx adeu extract umowa.docx > umowa.md
# operator przygotowuje edits.json z propozycjami redline
uvx adeu apply umowa.docx --edits edits.json --author "Kancelaria"
uvx adeu sanitize umowa-redlined.docx --keep-markup
```

Wyjscie: `umowa-redlined.docx` z natywnymi Word Track Changes + sanitize
metadanych autora i historii wersji (RODO przy wysylce).

### Warstwa 8: legal-ai-audit-bundle

Pakujemy slad pracy AI w paczke audytowa zgodna z AI Act art. 12:

```
audit-2026-05-24-kancelaria-XYZ-sprawa-N/
  manifest.json           # SHA256 wszystkich plikow + metadane (model, data, koszt)
  deliverable.docx        # finalna opinia
  trace/
    01-intake.md          # output intake-sufficiency-pl
    02-router.md          # decyzja routera
    03-analysis.md        # draft + queries do SAOS/EUR-Lex
    04-grounding.md       # raport cytatow
    05-adversarial.md     # debata + lista ryzyk
    06-fidelity.md        # raport wiernosci
    07-redline.docx       # (opcjonalnie)
  cost.log                # koszt API / tokeny / czas
  config.yaml             # model, temperatura, system prompt
```

Manifest SHA256 + struktura plikow daje dowod nalezytej starannosci na
wypadek audytu / sporu / kontroli kancelarii.

## Klucz - co Lawve.ai NIE dostarcza

Hub Lawve oferuje atomowe klocki (NDA review, DPIA, GDPR breach itd.).
Nie laczy ich w jeden walidowany lancuch. Czytelnik dostaje narzedzia,
ale musi sam zbudowac pipeline.

Ten hub dostarcza pelny lancuch jako pierwszorzedny artefakt. Skille
dzialaja samodzielnie (atomowy use), ale tez maja jasna kompozycje przez
pole `companion_skills` we frontmatter SKILL.md. To roznica strategiczna,
nie tylko techniczna.

## Dalsza lektura

- [README.md](../README.md) - taksonomia i lista 14 skilli
- [matematic-legal-verify-pl](https://github.com/matematicsolutions/matematic-legal-verify-pl) - plugin Claude Code pakujacy 4 z 6 warstw walidacji
- [patron](https://github.com/matematicsolutions/patron) - lokalny agent ktory moze uruchamiac caly lancuch self-host
