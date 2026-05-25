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
