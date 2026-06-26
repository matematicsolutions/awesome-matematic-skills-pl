# awesome-matematic-skills-pl (Boutique marketplace) - Konstytucja

## Mission (1 zdanie)
Darmowy, instalowalny jedną komendą hub polskich i europejskich umiejętności AI dla prawa, w którym zaufanie bierze się z mechanizmów (weryfikacja, grounding, multi-jurysdykcja), nie z obietnic - przewaga MateMatic to substancja konektorów EU, a forma dorównuje najlepszym w Europie.

## Core Principles (articles)

### Article I - Suoja syntyy mekanismeista (zaufanie z mechanizmów, nie deklaracji)
MUST: każdy skill nosi realny mechanizm ochrony (weryfikacja źródła / grounding / negative scope / bramka człowieka), nie sam disclaimer. Jeśli błąd przechodzi mimo mechanizmów - wina jest w skillu, naprawiamy narzędzie, nie dopisujemy noty. Adaptacja zasady Aku Nikkoli ("Loppuhuomautus ei siirrä vastuuta").

### Article II - RODO-safe by default
MUST: skille działają lokalnie tam, gdzie dotykają danych osobowych (grounding, anonimizacja, konwersja). MUST NOT: wymuszać wysyłki danych klienta do chmury jako warunku działania. Dane wrażliwe / objęte tajemnicą - domyślnie nie transferujemy, jeśli niepewne.

### Article III - Vendor-agnostic
MUST: skille są przenośne między dostawcami AI (Claude Code / Cowork i dalej), nie zaszywają zależności od jednego vendora w warstwie metody.

### Article IV - Granica metoda / substancja
MUST: rdzeń weryfikacyjny (router, intake, grounding, adversarial, fidelity, audit-bundle) jest NEUTRALNY jurysdykcyjnie i językowo - przenośny na każdy kraj. Głęboka substancja prawa (orzecznictwo PL, przepisy PL) ZOSTAJE per-jurysdykcja. Konektor jurysdykcji dobiera się do prawnika, nie odwrotnie.

### Article V - Negative scope jawny
MUST: każdy SKILL.md deklaruje wprost, czego NIE robi (sekcja "Czego ten skill NIE robi"). Granica jurysdykcyjna i granica kompetencji widoczne, nie domyślne.

### Article VI - Każdy output to draft, człowiek jest bramką
MUST: produkty skilli to luonnos/draft do weryfikacji przez uprawnionego człowieka. Akty nieodwracalne / na zewnątrz (złożenie pisma, podpis, wysyłka) ZAWSZE zostają człowiekowi. AI Act art. 50 - transparentność, że to wynik AI.

### Article VII - Generosity jako fosa
MUST: skille są PEŁNE i DARMOWE, zero bramek/waitlist/gatingu. Otwartość to przewaga konkurencyjna, nie koszt - zaprasza, nie wypycha (zasada współpracy nie konkurencji).

## Boundaries
**Robi:**
- Hostuje instalowalne (one-command) skille + konektory MCP dla prawa PL/EU
- Bundluje rdzeń weryfikacyjny jako fundament "instaluj zawsze"
- Wynosi wspólne standardy (cytat / odpowiedzialność+RODO / wdrożenie) dziedziczone przez skille

**Nie robi (anti-zakres):**
- NIE jest produktem sprzedażowym (to PATRON / konstytucja-ai dla kancelarii)
- NIE hostuje cudzych skilli pod licencją zakazującą republikacji (NC-ND)
- NIE wprowadza cennika ani gatingu na skille
- NIE udaje porady prawnej

**Współpraca (zależności):**
- PATRON (konsumuje te konektory + rdzeń jako produkt local-first)
- eu-legal-mcp / *-eli-mcp (osobne repo konektorów, bundlowane przez .mcp.json)
- www-matematic/boutique (witryna prezentująca ten marketplace)

## Governance
- **Owner:** Wiesław Mazur
- **Reviewers:** humanizer-pl + marko-pl-content (KAŻDY polski tekst: references/, CLAUDE.md, opisy pluginów, README - bramka obowiązkowa przed push, nie tylko na końcu), matematic-patron-pr-review-pl (struktura), reviewer-en (treści EN)
- **Amendment process:** zmiana konstytucji = SEMVER bump + wpis w ## Amendments, zatwierdza WM
- **Bramka publikacji:** zmiany w repo publicznym = zielone WM + leak-scan przed push

## Compliance Map
- **AI Act art. 12** (record-keeping) - legal-ai-audit-bundle realizuje
- **AI Act art. 50** (transparentność) - Article VI
- **RODO** - Article II (lokalnie), DPA gdy chmura
- **Licencje:** per-skill zachowane (Apache-2.0 / MIT); marketplace jako całość nie nadpisuje licencji komponentów

## Amendments
- 2026-06-26 v0.1.0 - ratyfikacja initjalna (zielone WM).

**Version:** 0.1.0 | **Ratified:** 2026-06-26 | **Last Amended:** 2026-06-26
