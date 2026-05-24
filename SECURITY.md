# Polityka bezpieczenstwa

## Zglaszanie podatnosci

Jezeli znalazles podatnosc w ktoryms ze skilli lub w infrastrukturze repo (skrypty walidacyjne, marketplace.json, examples):

1. **NIE otwieraj publicznego issue.**
2. Wyslij email na `kontakt@matematic.co` z prefiksem tematu `[SECURITY] awesome-matematic-skills-pl: ...`.
3. Opisz wektor + krok-po-kroku reprodukcji + zakres skutkow.
4. Otrzymasz potwierdzenie w 72 godziny i aktualizacje co tydzien do czasu wydania patcha.

Po wydaniu patcha publikujemy CVE-style advisory w `CHANGELOG.md` + opcjonalnie GitHub Security Advisory.

## Co uznajemy za podatnosc

### Krytyczne (patch w 7 dni)
- Skill ktory w trakcie pracy wysyla dane klienta do cloud LLM bez wiedzy operatora (np. domyslny endpoint w SKILL.md wskazuje hosted API).
- Skill ktory zapisuje PII do trwalego logu bez anonimizacji.
- Skrypt walidacyjny ktory wstrzykuje shell command z trustless input.

### Wysokie (patch w 30 dni)
- Skill z domyslna konfiguracja, ktora obchodzi tajemnice zawodowa (np. wysylka pisma do US bez DPA).
- Skill z domyslnym API key wbudowanym w repo lub przykladach.
- Skrypt walidacyjny ktory generuje false-negative dla naruszen tajemnicy.

### Srednie (patch w 90 dni)
- Skill z domyslnym ustawieniem, ktore zwieksza ryzyko halucynacji cytatu (np. wylaczone grounding).
- Brakujace ostrzezenia o ograniczeniach jurysdykcyjnych.

### Nie uznajemy za podatnosc
- Skille ktore wymagaja cloud LLM jezeli wymaganie jest **explicit w SKILL.md** (sekcja Ograniczenia / Wymagania), a operator dostaje jasna informacje przed pierwszym uruchomieniem. Domyslna konfiguracja musi zostawiac wybor (lokalna inference lub cloud z DPA / SCC) - bez ukrytego defaultu cloud.
- Halucynacje LLM nie zwiazane z konkretnym skillem - to natura modeli, dlatego wbudowalismy `citation-grounding-pl` i `adversarial-legal-review-pl`.

## Zasady RODO i tajemnicy zawodowej

Hub jest projektowany pod twarda regule: **zaden skill w bundle nie moze byc skonfigurowany tak, zeby wysylac dane klienta poza srodowisko operatora bez jego swiadomej zgody**.

- Skille uzywajace LLM domyslnie: cloud LLM lokalna izolacja (Ollama / vLLM / cloud z DPA). Operator wybiera.
- Skille uzywajace external APIs (np. SAOS / EUR-Lex): tylko publiczne dane, brak wysylki PII.
- Skille uzywajace lokalnego storage (cache, audit bundle): operator kontroluje retencje.

Naruszenie tajemnicy zawodowej przez skill = automatyczne RED w trzeciej warstwie walidacji (`deliverable-fidelity-pl`) i blokada deliverable.

## Atrybucja CVE / GHSA

Jezeli zgloszenie skutkuje patchem, beda atrybuowani:

- W `CHANGELOG.md` przy wpisie patcha
- W GitHub Security Advisory (jezeli wystawione)
- Opcjonalnie w `THIRD_PARTY_INSPIRATIONS.md` jezeli wektor doprowadzil do strukturalnej zmiany

## Kontakt

- Email: kontakt@matematic.co (prefix `[SECURITY] awesome-matematic-skills-pl`)
- Maintainer: [Wieslaw Mazur](https://www.linkedin.com/in/wieslawmazur/)
