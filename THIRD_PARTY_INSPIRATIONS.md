# Third-party inspirations - kanon cherry-pick

Ten plik dokumentuje, ktore pomysly z otwartego ekosystemu zostaly zaadaptowane
w tym hubie i z jakim ograniczeniem licencyjnym. Kanon MateMatic dla cherry-pick
wymaga snapshotu licencji, atrybucji w 3 miejscach (SKILL.md, THIRD_PARTY, NOTICE)
i jasnego rozroznienia: "pattern" vs "kod".

## Klucz: pattern vs kod

- **Pattern** = pomysl, struktura, taksonomia, schemat decyzyjny. Pomysly nie
  podlegaja prawu autorskiemu. Mozna przejmowac i adaptowac niezaleznie od
  licencji oryginalu.
- **Kod / tekst** = konkretne fragmenty kodu, prompty, SKILL.md tresc.
  Podlega prawu autorskiemu. Przejmowane tylko zgodnie z licencja oryginalu.

W tym repo: pattern adaptowany od wielu projektow OSS. Kod i prompty napisane
od zera pod polskie realia, polski jezyk i polskie organy prawne.

## Inspiracje na poziomie hubu (curation)

### lawve-ai / awesome-legal-skills (CC BY-NC-ND 4.0)

**Repo**: https://github.com/lawve-ai/awesome-legal-skills + https://github.com/lawvable/agent-skills
**Snapshot**: 2026-05-24 - 42 skille w mirrorze GitHub `awesome-legal-skills`; lawve.ai web hub deklaruje 110+ skilli zawierajacych dodatkowe wpisy spoza publicznego mirroru. W weryfikacji bazujemy na publicznie dostepnym GitHub.
**Licencja**: CC BY-NC-ND 4.0 (curation) + AGPL-3.0 lub Apache-2.0 per-skill
**Relacja**: PATTERN ONLY. Zaden tekst SKILL.md ani opis nie skopiowany. Adaptujemy:

- Idea kuratorskiego hubu kuratorskiego skilli legal-AI z `.claude-plugin/marketplace.json` jako manifest plugin marketplace
- Taksonomia (Commercial / Privacy / Compliance / Employment / Corporate / Methodology / Tooling) - adaptowana do polskich jurysdykcji (Walidacja outputu LLM / Umowy / Orzecznictwo PL+UE / Narzedzia / Higiena tresci)
- Multi-tool deployment narracja (Claude / Cowork / Code / OpenAI Codex / Gemini CLI / Manus / Mistral Vibe)
- Per-skill frontmatter standard z `author`, `license`, `version` (CalVer)

**Czego NIE czerpiemy**:
- Tekst zadnego SKILL.md (CC-BY-NC-ND blokuje derywaty + komercyjne uzycie)
- Brand assets (SVG badges, gif demos)

**Werdykt MateMatic 4-bramkowy**: TRAFIONE warunkowo (pattern OK, kopia blocked).

**Refresh 2026-07-05** (repo: https://github.com/lawvable/awesome-legal-skills,
rebrand "Lawve AI x Anthropic", 139 skilli, 549 gwiazdek). Kluczowe ustalenie:
licencje sa deklarowane PER-SKILL we frontmatterze SKILL.md (czesto bez pliku
LICENSE) - ok. 62 AGPL, 32 Apache-2.0, 11 MIT, 6 CC-BY-4.0, 6 proprietary,
reszta bez deklaracji (spada na CC BY-NC-ND repo). Zero skilli polskich.
Adaptacje z tego refreshu:

- **opposing-counsel-review** (Larissa Meredith-Flister, Apache-2.0 wg frontmatteru
  autorki) -> FORK z adaptacja i przekladem: `atak-przeciwnika-pl` +
  `opposing-counsel-attack-en`. Atrybucja we frontmatterze obu skilli.
- **judicial-first-impression** (Larissa Meredith-Flister, Apache-2.0 wg frontmatteru)
  -> FORK: `pierwsze-wrazenie-sedziego-pl` + `judicial-first-impression-en`.
- **privilege-sentinel** (AGPL-3.0) -> PATTERN ONLY (pasma SAFE/CAUTION/STOP):
  `tajemnica-preflight-pl` + `privilege-preflight-en` napisane od zera na
  polskich/unijnych podstawach prawnych.
- **suite EU AI Act** (Oliver Schmidt-Prietz AGPL / Werner Plutat proprietary) ->
  PATTERN ONLY (dekompozycja triage -> rola -> obowiazki -> raport):
  `ai-act-triage-pl` + `eu-ai-act-triage-en` od zera na tekscie 2024/1689.
- **nis2-navigator** (AGPL-3.0) -> PATTERN ONLY (nawigator zakresu):
  `nis2-ksc-pl` + `nis2-compliance-triage-en` od zera na tekscie 2022/2555.
- **swiss-legal-source-authority-triage** (Enrique G. Zbinden, MIT) -> PATTERN
  ("route authority before answer"): `hierarchia-zrodel-pl` + `authority-triage-en`,
  tresc PL/UE od zera.
- **litigation-deadline-calendar** (MIT, tresc US) -> IDEA ONLY: `terminy-procesowe-pl`
  w calosci od zera (KC/KPC/KPA).
- **raisonnement-juridique** (Amaury Fouret, MIT) -> STAGED FORK 1:1 do edycji FR
  PATRONa (`~/Projects/_ref/lawve-harvest/`), nie w tym repo.
- **skill-security-auditor** (AGPL) -> FAKTY ONLY: taksonomia 10 kategorii zagrozen
  (w tym Trojan Source/homoglify) jako reczny checklist wewnetrznego skill-audit;
  implementacja wlasna.

Uwaga na kolizje nazwy: ich `legal-data-hunter` (installer komercyjnego hostowanego
MCP legaldatahunter.com, brak licencji) to INNY byt niz nasz `legal-data-hunter-pl`.

### Anthropic / claude-for-legal (Apache-2.0)

**Repo**: https://github.com/anthropics/claude-for-legal
**Snapshot**: 2026-05-24
**Licencja**: Apache-2.0
**Relacja**: PATTERN. Skille Anthropic (canned-responses, contract-review, compliance,
legal-risk-assessment, meeting-briefing, nda-triage, skill-creator, docx-processing,
pdf-processing, pptx-processing, xlsx-processing) jako referencja formatu Agent Skills
i scope. Apache-2.0 pozwala na komercyjne uzycie, ale wlasne skille w tym hubie
napisane od zera pod polskie realia.

## Inspiracje na poziomie skilli (walidacja outputu LLM)

### AnttiHero / lavern (Apache 2.0)

**Repo**: https://github.com/AnttiHero/lavern
**Snapshot**: 2026-04 (najnowszy commit)
**Licencja**: Apache 2.0
**Relacja**: PATTERN. 6 skilli walidacji w tym hubie czerpie pattern z architektury
lavern - debata builder/attacker/synthesizer/verifier, mechanical citation grounding,
post-assembly verifier, router classification, audit bundle. Kod i prompty napisane
od zera pod polski jezyk i polskie cytaty (Art. X k.p.k. / sygnatury PL).

**Wykorzystane wzorce**:
- ADR-010 debate + 3-layer verification -> `adversarial-legal-review-pl`
- `src/mcp/tools/dissent.ts` panel rozbieznosci (multiple-choice do niezaleznych ocen,
  split = FINDING, resolveDissent -> re-vote -> eskalacja) -> `adversarial-legal-review-pl` sekcja 4c
- ADR-011 mechanical grounding verifier -> `citation-grounding-pl`
- `src/api/briefing` analiza wystarczalnosci -> `intake-sufficiency-pl`
- `router/RouterClassification` -> `legal-request-router-pl`
- `src/assembly/post-assembly-verifier.ts` -> `deliverable-fidelity-pl`
- `audit-bundle` -> `legal-ai-audit-bundle` (plus wlasny wzor matematic-video-governance)

### microsoft / agent-governance-toolkit (MIT)

**Repo**: https://github.com/microsoft/agent-governance-toolkit
**Snapshot**: 2026-05-24 (1904 gwiazd, 992 testow)
**Licencja**: MIT
**Relacja**: PATTERN. Wzorce OWASP Agentic Top 10 i shadow AI discovery zaadaptowane
w companion repo MateMatic (Patron, matematic-konstytucja-ai). Wpiete tez do
`legal-ai-audit-bundle` jako roadmap Merkle proof.

### hshadab / preflight-mike (MIT)

**Repo**: https://github.com/hshadab/preflight-mike
**Snapshot**: 2026-05-24
**Licencja**: MIT
**Relacja**: PATTERN czesciowo zaadaptowany. SMT-LIB compilation, proof receipt,
offline verifier wpiete jako roadmap 2 w `legal-ai-audit-bundle`.

## Inspiracje na poziomie skilli (narzedzia)

### Dealfluence Oy / adeu (MIT)

**Repo**: https://github.com/dealfluence/adeu
**Snapshot**: v1.7.5 (2026-05-22)
**Licencja**: MIT
**Relacja**: ZALEZNOSC CLI. `redline-docx-pl` to wrapper workflow PL nad CLI adeu
(`uvx adeu ...`). Nie kopiujemy kodu adeu - wolamy go. Smoke test PL na polskim
.docx w skill THIRD_PARTY_INSPIRATIONS.md.

### evolsb / legal-redline-tools (MIT)

**Repo**: https://github.com/evolsb/legal-redline-tools
**Snapshot**: 2026-07-13
**Licencja**: MIT
**Relacja**: PATTERN. Dwa wzorce zaadaptowane w `redline-docx-pl` v0.2.0:
memo negocjacyjne (pola tier/rationale/walkaway/precedent, grupowanie wg
tierow 1-3) oraz skan placeholderow przed wysylka. Oba skrypty napisane od
zera (Python stdlib) pod polskie wzorce i format edits.json adeu.

### Microsoft / MarkItDown (MIT)

**Repo**: https://github.com/microsoft/markitdown
**Licencja**: MIT
**Relacja**: ZALEZNOSC CLI. `markitdown` skill to thin wrapper konfiguracji uzycia
MarkItDown z poziomu Claude Code. Instalacja przez `pip install markitdown markitdown-mcp`.

### OpenDataLoader / opendataloader-pdf (Apache 2.0)

**Repo**: https://github.com/opendataloader/opendataloader-pdf
**Licencja**: Apache 2.0
**Relacja**: ZALEZNOSC CLI. `opendataloader-pdf` skill to wrapper na ten konwerter
PDF -> JSON/MD wysokiej jakosci (reading order, tabele, headings).

### crankshift / lawpowers (MIT)

**Repo**: https://github.com/crankshift/lawpowers
**Snapshot**: 2026-07-13 (namierzony jako upstream agregatora ThomasMoreAI;
22 skille PL + skille UA, autorstwo raz w `skills/<jur>/`, adaptery
per-platforma generowane)
**Licencja**: MIT
**Relacja**: PATTERN. `kalkulatory-procesowe-pl` adaptuje dwa wzorce:
dekompozycje kalkulatorow procesowych na 4 osobne rachunki (oplata sadowa /
przedawnienie / odsetki / WPS) oraz protokol "parameter retrieval" - tabela
zrodel zywych wartosci + fallback z data weryfikacji przed kazdym
obliczeniem. Tresc, tabele i rachunki napisane od zera na tekstach
UKSC/KC/KPC; przy adaptacji poprawiono 4 nieaktualne wartosci zrodla:

- limit oplaty stosunkowej 200 000 zl -> 100 000 zl (nowela Dz.U. 2025
  poz. 1157, od 23.09.2025),
- odsetki w transakcjach handlowych +8 p.p. -> +10 p.p. dla zwyklego
  dluznika (od 2020 r.; +8 zostalo tylko dla publicznych leczniczych),
- mediacja jako przerwanie biegu przedawnienia -> zawieszenie
  (art. 121 pkt 5-6 KC, od 30.06.2022),
- najem na czas nieoznaczony w WPS: 6 miesiecy -> suma czynszu za
  3 miesiace (art. 23 KPC).

**Werdykt MateMatic 4-bramkowy**: TRAFIONE (MIT, jakosc probek wysoka,
ale wartosci liczbowe wymagaly odswiezenia - stad wlasna wachta parametrow
w CI zamiast zaufania tabelom).

### Lum1104 / Understand-Anything (MIT)

**Repo**: https://github.com/Lum1104/Understand-Anything
**Snapshot**: 22.5k gwiazd
**Licencja**: MIT
**Relacja**: PATTERN dla companion repo KGLF (Knowledge Graph for Law Firms),
nie bezposrednio w tym hubie. 9 wzorcow architektury grafu wiedzy zaadaptowanych
w KGLF blueprint.

## Inspiracje na poziomie zrodel danych (orzecznictwo, prawo)

### Fundacja ePanstwo / SAOS API

**API**: https://www.saos.org.pl
**Licencja danych**: CC0 / public domain
**Relacja**: ZRODLO DANYCH. `saos-orzecznictwo` i `szukaj-orzeczen-v2` uzywaja
publicznego REST API SAOS. Dane orzecznictwa = public domain (Art. 4 ustawy
o prawie autorskim - akty normatywne i orzeczenia organow wladzy nie sa
przedmiotem prawa autorskiego).

### Publications Office of the EU / EUR-Lex SPARQL

**Endpoint**: https://publications.europa.eu/webapi/rdf/sparql
**Licencja danych**: ECDL (European Commission Decisional License) - swobodne
uzycie z atrybucja
**Relacja**: ZRODLO DANYCH. `eu-sparql-search` uzywa SPARQL endpoint Cellar
do zapytan o akty UE i orzecznictwo TSUE.

### worldwidelaw / legal-sources (AGPL-3.0)

**Repo**: https://github.com/worldwidelaw/legal-sources
**Licencja repo (skrypty)**: AGPL-3.0
**Licencja danych**: per-zrodlo w `config.yaml` (SAOS = public domain etc.)
**Relacja**: ZALEZNOSC CLI. `legal-data-hunter-pl` skill uzywa kolektorow
z tego repo jako osobnych procesow (wolanych przez `runner.py`). Uruchamianie
kolektorow jako osobnych procesow i uzywanie zebranych danych nie czyni
powloki tego hubu dzielem zaleznym AGPL.

## Discovery, NIE zaadaptowane (mapowanie nisz)

- **Tucuxi Inc** (CC BY-NC) - blocked dla kanonu komercyjnego MateMatic
- **gh-attach** - anty-OS (kradziez cookies), odrzucone
- **herdr** - brak binarki Windows, odlozone

Pelna mapa: patrz `reference_narzedzia_oceny_*.md` w prywatnym memory MateMatic
(nie publikowane).

## Zasady kanonu cherry-pick

1. **Snapshot licencji** zawsze przy adopcji (data + URL + nota o prawach autorskich)
2. **Pattern vs kod** rozroznione explicit
3. **Atrybucja w 3 miejscach**: SKILL.md frontmatter (`inspiration:`), ten plik
   THIRD_PARTY_INSPIRATIONS.md, NOTICE
4. **4 bramki MateMatic** przed adopcja: licencja, anty-OS, jakosc, strategia
5. **Werdykt zapisany w memory** - rejestr ocen (NIE oceniaj URL ponownie)

## Kontakt

Watpliwosci licencyjne / zglozenie ze cos pominieto: `kontakt@matematic.co`
prefix `[LICENSE] awesome-matematic-skills-pl`.
