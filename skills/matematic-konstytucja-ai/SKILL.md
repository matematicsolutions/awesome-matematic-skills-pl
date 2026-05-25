---
name: matematic-konstytucja-ai
description: Generuje "Konstytucje AI" dla kancelarii prawnej - dokument governance definiujacy zasady uzycia AI w organizacji, na bazie cherry-pick patternu github/spec-kit (constitution -> spec -> plan -> tasks). 6 sekcji - mission, principles (max 9 articles), boundaries, governance roles, audit, evolution. Output - dokument PDF/MD 10-25 stron + plan wdrozenia 6-8 tygodni (AI Implementation Playbook). Uzywaj gdy kancelaria pyta o AI governance, polityke AI, etyke AI, AI policy, regulamin AI, Konstytucja AI, zasady AI w kancelarii, AI Act compliance, RODO + AI. Trigger - "Konstytucja AI", "polityka AI", "AI governance dla kancelarii", "zasady AI", "regulamin AI", "audyt AI policy", "AI Act compliance", "wdrozenie AI plan", "AI Implementation Playbook". Bazuje na github/spec-kit (MIT) - cherry-pick methodology pattern, NIE pelna instalacja.
metadata:
  author: Wieslaw Mazur / MateMatic
  version: 1.0.0
  project: MateMatic AI Governance Product
  source_pattern: github/spec-kit (MIT) - constitution pattern only
  output_format: markdown + PDF
  target_audience: kancelarie 10-200 prawnikow
  pricing_range: 15-40k PLN (single deployment), 60-150k PLN (multi-kancelaria framework license)
---

# MateMatic Konstytucja AI - generator dokumentu governance

Generuje "Konstytucje AI" - flagowy dokument governance dla kancelarii prawnej. Cherry-pick methodology z `github/spec-kit` (MIT), adaptacja pod B2B services dla kancelarii prawnych w Polsce.

**Source pattern:** spec-kit's Spec-Driven Development zaczyna od `constitution.md` - dokumentu ktory definiuje **niezmienne zasady projektu**. Caly downstream (spec, plan, tasks, impl) musi byc z nim zgodny. Adaptujemy ten pattern na kancelarie: constitution = "Konstytucja AI" definiujaca zasady uzycia AI w organizacji prawnej, downstream = AI Implementation Playbook 6-8 tygodni.

---

## Geneza - dlaczego ten skill istnieje

**Problem klienta:** kancelarie prawne wdrazaja AI ad-hoc, kazdy partner inaczej, brak spojnej polityki. Po incydencie (np. wyslanie poufnych danych do ChatGPT przez asystenta) zarzad pyta "jaka mamy polityke AI?". Odpowiedz: nie mamy.

**Wartosc MateMatic:** dostarczamy spojny dokument **Konstytucja AI** ktory:
- Ustala granice (boundaries) - co wolno / czego nie wolno
- Definiuje role governance - kto ma prawo wdrazac nowe narzedzia AI
- Mapuje sie na RODO + AI Act + tajemnice zawodowa
- Jest podstawa do downstream procesow (procedury, szkolenia, audyty)

**Pricing range:**
- Single kancelaria deployment: 15-40k PLN (10-25 stron dokument + 4-6 warsztatow + 60-min playbook)
- Multi-kancelaria framework license: 60-150k PLN (template + uprawnienia do reuse w n kancelariach)

---

## Architektura Konstytucji - 6 sekcji

### Sekcja 1 - Mission (cel)

Jedno zdanie: **dlaczego ta kancelaria uzywa AI**. Nie generycznie ("zwiekszenie produktywnosci") ale specyficznie dla tej organizacji.

Przyklady (dla rozneych typow kancelarii):
- Kancelaria butikowa M&A: "Uzywamy AI by skrocic czas due diligence z 80h do 30h przy zachowaniu pelnej tajemnicy zawodowej wobec stron transakcji."
- Kancelaria duza ogolna: "Uzywamy AI by zwiekszyc dostepnosc obslugi klientow biznesowych przy ograniczeniach kosztowych, NIE zastepujac judgement adwokata."
- Kancelaria specjalistyczna IP: "Uzywamy AI by zautomatyzowac prior art search i ograniczenie due diligence patentowe do najwazniejszych kwestii."

**Cel sekcji:** kazda decyzja w Konstytucji wynika z Mission. Mission jest TEST: "czy ta zasada / to narzedzie sluzy naszej Mission?"

### Sekcja 2 - Principles (zasady - max 9 articles)

Wzorowane na spec-kit's articles. Kazda zasada to **niezmienny imperatyw** sformulowany w MUST / MUST NOT / SHOULD.

Domyslne 9 articles (modyfikowalne per kancelaria):

```
Article I - Tajemnica zawodowa nadrzedna
MUST: Zadne narzedzie AI nie moze wysylac danych objetych tajemnica zawodowa
do uslugi zewnetrznej bez DPA + EU data residency + szyfrowania end-to-end.

Article II - Human-in-the-loop dla decyzji prawnych
MUST: Kazda opinia prawna / pismo procesowe / umowa wygenerowana z udzialem AI
musi miec weryfikacje co najmniej jednego prawnika z uprawnieniami w danej dziedzinie.

Article III - Audytowalnosc decyzji AI
MUST: Kazde uzycie AI w sprawie klienta musi pozostawiac sciezke decyzyjna
(model, prompt, output, weryfikacja) zachowywana minimum 5 lat (AI Act art. 12).

Article IV - Zakaz autonomic actions
MUST NOT: Zaden agent AI nie moze wykonywac dzialania w imieniu kancelarii
(wysylanie email, zlozenie pisma w sadzie, podpisanie umowy) bez explicit human approval per action.

Article V - Transparentnosc wobec klienta
MUST: Klient musi byc poinformowany o uzyciu AI w sprawie minimum w umowie o swiadczenie pomocy prawnej.
SHOULD: Klient ma prawo zazyczyc nie-AI sciezki obslugi sprawy (cena moze byc wyzsza).

Article VI - Zatwierdzanie nowych narzedzi
MUST: Kazde nowe narzedzie AI (plugin, MCP server, model lokalny, SaaS) musi przejsc
governance review przed pierwszym uzyciem w sprawie klienta. Lista zatwierdzonych narzedzi
jest dokumentem zywym, review co kwartal.

Article VII - Edukacja prawnikow
MUST: Kazdy prawnik korzystajacy z AI musi przejsc co najmniej 8-godzinne szkolenie
podstawowe (Akademia MateMatic lub equivalent). Refresh co 12 miesiecy.

Article VIII - Brak dyskryminacji algorytmicznej
MUST: Jezeli narzedzie AI ma wplyw na decyzje dotyczace klientow (acceptance, pricing tiers, prioritization),
musi byc audytowane pod katem bias minimum raz na 12 miesiecy.

Article IX - Evolution
MUST: Konstytucja AI jest dokumentem zywym. Co 12 miesiecy zarzad kancelarii dokonuje review
i amendmentu w oparciu o nowe regulacje (AI Act updates, EDPB guidance), incydenty, nowe narzedzia.
```

**Per kancelaria:** wybierz 5-9 articles z listy + opcjonalnie dodaj 1-2 specyficzne dla organizacji. Numeracja zachowana (Article I jest najwazniejszy, IX najnizej w hierarchii).

### Sekcja 3 - Boundaries (granice)

Konkretne LISTY co wolno / czego nie wolno. Trzy poziomy:

| Poziom | Definicja | Przyklad zatwierdzenia |
|---|---|---|
| **ZIELONY** | Wolne uzycie, brak approval | ChatGPT do skladni gramatyki maila, NIE umowy. Internal Claude Project z testowym datasetem |
| **ZOLTY** | Wymaga approval IT/governance | Nowy plugin Claude Code (audyt legal-ai-plugin-governance), nowy MCP server, narzedzie SaaS z DPA |
| **CZERWONY** | Zakazane | Wysylanie tresci umow do nieklientowych chatbotow, voice clone klienta bez zgody, autonomic AI actions w sprawie sadowej |

**Wzor tabeli zatwierdzanych narzedzi:**

```markdown
## Zatwierdzone narzedzia AI - status 2026-MM-DD

| Narzedzie | Poziom | Zakres uzycia | DPA | Data residency | Audyt expire |
|---|---|---|---|---|---|
| Claude (Anthropic) Enterprise | ZIELONY | Analiza tekstu, draft pisma, research | TAK | UK + US | 2026-12 |
| ChatGPT Enterprise | ZIELONY | Jak wyzej | TAK | EU | 2026-12 |
| Cline z lokalnym LLM (ollama) | ZIELONY | Wszystko (zero leak) | n/a | lokalnie | n/a |
| Random nowy plugin GitHub | ZOLTY | Brak | - | - | review |
| Voice clone klienta przez ElevenLabs | CZERWONY | Zakaz | - | - | - |
```

### Sekcja 4 - Governance Roles

Kto odpowiada za co:

```
**AI Steward** (1 osoba, partner zarzadzajacy lub designated):
- Final approver Konstytucji i amendment
- Approval procesu governance review nowych narzedzi
- Liaison z DPO i compliance

**AI Operations Lead** (1-3 osoby, IT/operations):
- Wdrozenie technicznych srodkow ochrony (Article I, III)
- Maintain liste zatwierdzonych narzedzi
- Audit log infrastructure (Article III)

**AI Champions** (1 osoba per dzial/zespol prawniczy):
- Edukacja w zespole (Article VII)
- First-line approval rozszerzonych uzyc w zespole
- Feedback loop do AI Steward

**External Counsel** (MateMatic lub inny):
- Coroczny review (Article IX)
- Update przy zmianach regulacyjnych (AI Act, RODO update)
- Audit zgodnosci
```

### Sekcja 5 - Audit Trail (sledzenie zgodnosci)

Co dokumentujemy, jak dlugo:

```
| Co | Format | Retencja | Storage |
|---|---|---|---|
| Audit log uzycia AI w sprawie | strukturalny log per case | 5 lat (AI Act art. 12 + RODO) | Lokalny zaszyfrowany + backup |
| Audit log zatwierdzania narzedzi | minutes + decision rationale | 7 lat | Zarzad |
| Audit log incydentow AI | incident report | 5 lat | DPO + AI Steward |
| Audit log szkolen prawnikow | attendance + cert | 3 lata (RODO art. 5(2)) | HR |
| Audit log changes do Konstytucji | git-style version control | unlimited | Repository (private) |
```

### Sekcja 6 - Evolution & Amendment Process

Jak zmienia sie Konstytucja:

```
**Annual Review** (Article IX):
- Quarter 4 kazdego roku
- AI Steward + External Counsel + 2-3 prawnikow z roznych dzialow
- Output: amendment proposal (jezeli sa zmiany)

**Triggered Review** (incident-driven):
- W ciagu 30 dni od incydentu (data leak, bias finding, audit issue)
- AI Steward decides scope
- Output: emergency amendment lub utrzymanie status quo

**Amendment Process:**
1. Proposal w git repository (private)
2. Discussion miedzy AI Steward / External Counsel / Champions
3. Approval przez zarzad kancelarii (wymagane 2/3 partnerow)
4. Communication do calego zespolu w 14 dni
5. Mandatory refresh training jezeli zmiana dotyczy Articles
6. Update audit log o zmiane

**Version control:**
- Konstytucja v1.0 (data publikacji)
- v1.1, v1.2 ... (minor amendments)
- v2.0 (major rewrite - rzadko)
```

---

## Downstream - AI Implementation Playbook 6-8 tygodni

Po Konstytucji generujemy **wykonawczy plan wdrozenia** wzorowany na spec-kit phases:

```
Konstytucja (zatwierdzona)
   |
   v
Spec (per use case): "Chcemy wdrozyc X dla zespolu Y"
   |
   v
Plan: timeline + roles + ryzyko + measurables
   |
   v
Tasks: konkretne kroki w 6-8 tygodni
   |
   v
Implementation: wykonanie + audit log
   |
   v
Retro: co dalej, amendment Konstytucji?
```

### Typowy Playbook 6 tygodni

**Tydzien 1 - Discovery**
- Audyt aktualnych uzyc AI w kancelarii (anonimowa ankieta + 5 wywiadow)
- **Shadow AI Discovery** (pattern z [microsoft/agent-governance-toolkit](https://github.com/microsoft/agent-governance-toolkit), MIT) - aktywne skanowanie srodowiska kancelarii pod **nieautoryzowane narzedzia AI**: rozszerzenia przegladarki (Grammarly, Copilot for Web), wpiete LLM-y w Outlook/Word, lokalne instalacje (LM Studio, Ollama), API keys w `.env` projektow, integracje Zapier/Make wywolujace LLM. Wynik to **lista wszystkich miejsc gdzie kancelaria juz uzywa AI** - czesto wiekszy szok dla zarzadu niz ankieta. Bramka skoku z dyskusji "powinnismy zaczac mysliec o AI policy" do "musimy natychmiast bo wlasnie odkrylismy 23 miejsca o ktorych nie wiedzielismy".
- Mapowanie use cases (top 10) + ryzyka per use case
- Output: discovery report + Shadow AI inventory

**Tydzien 2 - Konstytucja draft**
- Workshop 4h z zarzadem - definicja Mission + wybor 7-9 Articles
- External Counsel (MateMatic) prepares draft v0.9
- Output: Konstytucja draft

**Tydzien 3 - Konstytucja approval + governance setup**
- Zarzad approval Konstytucji v1.0
- Designation AI Steward + AI Ops Lead + AI Champions (1 per dzial)
- Output: Konstytucja v1.0 + governance team

**Tydzien 4 - Tooling setup**
- Audyt aktualnych narzedzi -> lista zatwierdzonych
- Setup audit log infrastructure (Article III)
- Boundaries communication do calego zespolu
- Output: lista narzedzi + audit infrastructure

**Tydzien 5 - Training**
- Akademia MateMatic 8h dla wszystkich prawnikow
- Deep dive 4h dla AI Champions
- Output: certyfikat dla 100% zespolu

**Tydzien 6 - Pilot use case**
- Wybor 1 use case z discovery report (np. "AI-assisted due diligence dla M&A")
- Pilot 2-tygodniowy z monitoring
- Output: pilot retro + amendment proposals do Konstytucji

**Opcjonalnie tygodnie 7-8:** rollout drugiego/trzeciego use case na bazie pilotu.

---

## Output template Konstytucji (markdown)

```markdown
# Konstytucja AI - [NAZWA KANCELARII]

**Data publikacji:** YYYY-MM-DD
**Wersja:** 1.0
**Status:** OBOWIAZUJACA
**Nastepny review:** YYYY-MM-DD (Q4 roku nastepnego)

---

## I. Mission

[Jedno zdanie dlaczego ta kancelaria uzywa AI]

---

## II. Principles (Articles I-IX)

### Article I - [TYTUL]
**MUST:** [imperatyw]
**Uzasadnienie:** [krotkie why]
**Mapping:** [RODO art. X / AI Act art. Y / tajemnica zawodowa]

[powtorz dla Articles II-IX]

---

## III. Boundaries

### Zielony - wolne uzycie
[lista narzedzi + zakres]

### Zolty - approval wymagany
[lista + proces]

### Czerwony - zakaz
[lista + uzasadnienie]

### Zatwierdzone narzedzia (zywa lista)
[tabela jak w Sekcji 3]

---

## IV. Governance Roles

[AI Steward, AI Ops Lead, AI Champions, External Counsel - z imionami/dzialami]

---

## V. Audit Trail

[Tabela co/format/retencja/storage]

---

## VI. Evolution & Amendment Process

[Annual Review + Triggered Review + Amendment Process + Version Control]

---

## Appendix A - Glossary
[Definicje: tajemnica zawodowa, dane osobowe, AI system high-risk, etc.]

## Appendix B - Mapping na regulacje
[Article I -> RODO + tajemnica adwokacka. Article II -> AI Act art. 14 (human oversight). etc.]

## Appendix C - Lista incydentow (template, pusty na start)
[Format do uzupelniania w trakcie zycia Konstytucji]

## Appendix D - Lista amendmentow (template, pusty na start)
[Format do uzupelniania przy kazdym amendmentu]

## Appendix E - OWASP Agentic Top 10 mapping na Articles Konstytucji

Cherry-pick referencji z [OWASP Top 10 for Agentic Applications (2026)](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) - branzowy konsensus 10 najwyzszych ryzyk dla aplikacji agentowych AI. Pelny mapping `docs/OWASP-COMPLIANCE.md` z [microsoft/agent-governance-toolkit](https://github.com/microsoft/agent-governance-toolkit) (MIT, snapshot 2026-05-24) - patterny zaadaptowane do polskich realiow kancelaryjnych.

**Dla kancelarii**: kazda Konstytucja AI MateMatic dla klienta musi adresowac wszystkie 10 ryzyk OWASP. To zewnetrzny, uznany standard - klient nie kwestionuje "skad to ryzyko", bo OWASP odpowiada. Sprzedazowy efekt: Konstytucja nie jest naszym wymyslem - jest implementacja standardu branzowego dla polskich kancelarii.

| OWASP | Ryzyko | Artykul Konstytucji ktory adresuje |
|---|---|---|
| ASI-01 | Agent Goal Hijack (manipulacja celow agenta przez prompt injection) | Art. III Boundaries (czego AI NIE robi) + Art. V Audit Trail (kazda akcja logowana) |
| ASI-02 | Tool Misuse & Exploitation (naduzycie autoryzowanych narzedzi do eksfiltracji) | Art. III Boundaries + Lista zatwierdzonych narzedzi (sekcja gornaa skilla) |
| ASI-03 | Identity & Privilege Abuse (eskalacja przez nadmiarowe credentials) | Art. IV Governance Roles (AI Steward / Ops Lead / Champions z scoped capabilities) |
| ASI-04 | Agentic Supply Chain Vulnerabilities (luki w narzedziach 3rd-party, MCP, model provenance) | Lista zatwierdzonych narzedzi + audyt dostawcy (procedura w Tydzien 4 Tooling setup) |
| ASI-05 | Unexpected Code Execution (RCE przez tooly/interpretery/API) | Art. III Boundaries (zakaz wykonania kodu/komend bez review) + Art. VI Human in the loop |
| ASI-06 | Memory & Context Poisoning (zatrucie pamieci dlugotrwalej) | Art. III Boundaries + procedura audytu memory na Tydzien 5 Training |
| ASI-07 | Insecure Inter-Agent Communication (komunikacja agent-agent bez auth/encryption) | Art. III Boundaries (no agent-to-agent bez ludzkiej akceptacji) - kancelaria nie buduje multi-agentowych systemow autonomicznie |
| ASI-08 | Cascading Agent Failures (kaskada bledow w lancuchach) | Art. V Audit Trail + nowa sekcja "Co kancelaria mierzy" (patrz nizej, SRE inspired) |
| ASI-09 | Human-Agent Trust Exploitation (naduzycie zaufania uzytkownika do autonomii AI) | Art. VI Human in the loop (wszystkie decyzje high-stakes wymagaja zatwierdzenia czlowieka) |
| ASI-10 | Rogue Agents (agenci dzialajacy poza zakresem przez drift/reprogramming) | Art. V Audit Trail (immutable log) + procedura amendment (Art. VI Evolution) |

**Walidator gotowosci Konstytucji**: po napisaniu Konstytucji dla klienta przejrzec ta tabele i upewnic sie, ze KAZDE ryzyko ma odpowiednik. Jezeli ktoryms artykul jest "n/a" - uzasadnij dlaczego (np. ASI-07 dla solo-kancelarii ktora nie buduje multi-agent).

## Appendix F - "Co kancelaria mierzy" - SLO i error budgety AI (Agent SRE inspired)

Cherry-pick z [microsoft/agent-governance-toolkit `AGENT-SRE-GOVERNANCE-1.0.md`](https://github.com/microsoft/agent-governance-toolkit/blob/main/docs/specs/AGENT-SRE-GOVERNANCE-1.0.md) (MIT, RFC 2119 spec). Inspiracja, nie kopia: SRE jest dla 100+ agentow, kancelaria ma 1-5 use case'ow. Adaptacja do skali kancelaryjnej.

**Pytanie klienta po 6 miesiacach: "skad wiemy ze AI dziala?"**. Dzis kancelarie nie wiedza co mierzyc. Konstytucja MateMatic daje szablon **4 mierzalnych metryk per use case AI**:

1. **Task Success Rate (TSR)** - % zadan AI zakonczonych z akceptowalnym wynikiem (recenzja czlowieka).
   - SLO startowy: >= 80% (kancelaria moze zaostrzyc po pierwszym kwartale)
   - SLI: tygodniowy raport "ile odpowiedzi AI zostalo zaakceptowanych w pierwszej iteracji"

2. **Hallucination Rate** - % odpowiedzi AI zawierajacych zmyslony fakt (nieistniejacy wyrok, blednie zacytowany przepis, fikcyjna data).
   - SLO startowy: <= 2% (jeden blad na 50 odpowiedzi)
   - SLI: review wybranych odpowiedzi przez Champions (sampling 5% tygodniowo)
   - **Bramka twarda**: > 5% w 2 tygodnie z rzedu -> circuit break (wylacz use case do diagnostyki)

3. **Sensitivity Exposure Risk** - liczba incydentow gdzie AI otrzymalo dane wrazliwe poza zatwierdzonym scope.
   - SLO startowy: 0 (zero tolerancji - to dotyka tajemnicy zawodowej art. 6 Pr.Adw.)
   - SLI: kazdy zgloszony incydent kierowany do AI Steward; tygodniowa pelnia
   - **Bramka twarda**: 1 incydent -> obowiazkowy retrospect + amendment Konstytucji

4. **Adoption Rate** - % zespolu uzywajacego AI w ramach use case'u (gdzie >0 = zaadoptowane).
   - SLO startowy: >= 50% docelowego zespolu w 90 dni
   - SLI: miesieczny self-report Champions
   - Niska adopcja nie blokuje AI, ale wymusza retro: "dlaczego zespol nie korzysta?" - czesto sygnal o niedopasowaniu use case'u

**Error budget**: kancelaria moze definiowac error budget per use case ("akceptujemy do 5% tasks zakonczonych niesatysfakcjonujaco w danym kwartale"). Wyczerpanie budgetu -> freeze nowych use case'ow w tym obszarze do retrospektywy.

**Circuit breaker** (przeniesione z Microsoft AGT): automatyczne wstrzymanie use case'u AI gdy TSR < 60% przez 7 dni z rzedu LUB Hallucination Rate > 5% przez 14 dni. Decyzja: AI Steward + AI Ops Lead razem.

**Dla wdrozenia**: Tydzien 4 Tooling setup (Playbook 6-tyg) zawiera "Setup monitoring infrastructure" - tu wlasnie te 4 metryki dostarczane sa jako Google Sheets / Notion / dashboard wewn. kancelarii.

## Appendix G - 5 polityk legal AI dla kancelarii (gold template) + iterator polityki

Cherry-pick z [hshadab/preflight-mike](https://github.com/hshadab/preflight-mike) (MIT, Houman Shadab, Stanford CodeX Fellow, snapshot 2026-05-24) - dokumentacja `docs/mikeoss-legal-ai.md` listuje 5 polityk dla deploymentu legal AI. **Adaptacja na PL kancelarie** + bramka iteracyjna.

### Pieic polityk-szablonow ktore KAZDA Konstytucja kancelarii powinna miec

**Polityka 1: No unauthorized legal advice (zakaz porady prawnej bez kontekstu jurysdykcyjnego)**
- Tresc PL: "Kazda odpowiedz AI zawierajaca interpretacje przepisu lub propozycje dzialania prawnego MUSI zawierac (a) wskazanie jurysdykcji (PL/UE/inny), (b) zastrzezenie 'projekt do weryfikacji przez prawnika', (c) cytat zrodla z grafu wiedzy kancelarii."
- Decyzja AI bez tych 3 elementow = BLOCKED.
- Rationale: art. 28 ust. 1 Pr.Adw. - wykonywanie zawodu adwokata to wylacznosc, AI nie moze emulowac porady. Tajemnica zawodowa nie obejmuje "rad" wprost, ale obejmuje **interpretacje sytuacji klienta**.

**Polityka 2: Privilege boundary (granica uprzywilejowania - sprawa-do-sprawy)**
- Tresc PL: "Referencje (cytaty, akta, dokumenty) w odpowiedzi AI MUSZA pochodzic z biezacego `project_id` / `matter_id`. AI nie laczy spraw klienta X z klientem Y nawet w celu uogolniajacym."
- Decyzja AI uzywajaca dokumentu Z innego matter_id = BLOCKED.
- Rationale: tajemnica zawodowa art. 6 Pr.Adw. - oddzielenie informacji per klient.

**Polityka 3: PII egress (zakaz wycieku danych osobowych w output)**
- Tresc PL: "Odpowiedz AI nie zawiera PESEL, numerow kont, dat urodzenia, adresow zamieszkania, NIP osob fizycznych - nawet jezeli te dane sa w input. Output ma byc spseudonimizowany (Klient A / Adres 1)."
- Decyzja AI z wykrytymi tymi wzorcami w output = BLOCKED.
- Rationale: RODO art. 5 (minimalizacja), art. 32 (bezpieczenstwo).

**Polityka 4: Citation integrity (integralnosc cytowania)**
- Tresc PL: "Kazdy cytat wyroku, ustawy, artykulu lub klauzuli umownej w odpowiedzi AI MUSI rozwiazywac sie do dokumentu istniejacego w korpusie kancelarii lub publicznym MCP konektorze (SAOS, EUR-Lex, KRS, ISAP). Halucynacja cytatu = BLOCKED."
- Mechanizm: lookup w grafie wiedzy lub MCP query. Brak match = nieistniejacy cytat.
- Rationale: zasada `citation-grounding-pl` - mechaniczna walidacja cytatu chroni przed halucynacja modelu.

**Polityka 5: Escalation scope (zakres eskalacji do czlowieka)**
- Tresc PL: "Pytania dotyczace: papierow wartosciowych (KSH, ustawa o ofercie publicznej), zdrowia/leczenia (Kodeks Etyki Lekarskiej), fuzji i przejec (KSH, prawo konkurencji), spraw karnych - WYMAGAJA review przez prawnika prowadzacego sprawe przed wyslaniem klientowi. AI nie autoryzuje tych odpowiedzi samodzielnie."
- Decyzja AI w tym scope bez ludzkiej akceptacji = BLOCKED.
- Rationale: Art. 6 Konstytucji (human in the loop) - dla obszarow wysokiej stawki, gdzie blad ma konsekwencje.

### Iterator polityki - "polityka jako kod"

Pattern z ICME Preflight (dokumentacja `docs.icme.io`, snapshot 2026-05-24): polityka traktowana jak kod, kompilowana i testowana przed deploymentem. Adaptacja na MateMatic delivery:

1. **Generate scenarios** - dla kazdej polityki kancelarii sgenerowac 20-30 scenariuszy testowych (mix oczekiwany ALLOWED + oczekiwany BLOCKED + edge cases). Sortowanie wedlug "likelihood of being wrong" (zaczynamy od najbardziej watpliwych).
2. **Manual feedback** - kancelaria (AI Steward + Champions) przechodzi scenariusze i annotuje: "to powinno byc allowed", "to powinno byc blocked", "to jest niezdefiniowane - dopisz exception".
3. **Refine policy** - na podstawie feedback rebuild polityki (zachowana ta sama `policy_id`, nowy `policy_hash`).
4. **Run tests** - wszystkie zaakceptowane scenariusze stana sie test suite polityki. Re-run przy kazdej zmianie polityki.

**Wartosc**: kancelaria nie deployuje polityki AI ad-hoc. Iteruje az pokrycie scenariuszy jest >= 80% poprawne. Audit log zawiera historie iteracji (`policy_hash` per moment, nie tylko aktualnie obowiazujacy).

### Wartosc dla kancelarii

- **Klient nie wie "co napisac" w Konstytucji** - dostaje 5 gotowych polityk-szablonow zaadaptowanych do polskich realiow.
- **Klient nie wie "czy nasza polityka dziala"** - dostaje iterator polityki (scenarios + feedback + tests).
- **Pozycjonowanie**: kierunek deterministycznej walidacji polityk jest reprezentowany m.in. przez [Microsoft Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit) i [ICME Preflight](https://docs.icme.io). MateMatic adresuje ten obszar w wersji lokalnej (zero cloud) dla kancelarii polskich.

### Atrybucja
5 polityk: wzor z [hshadab/preflight-mike `docs/mikeoss-legal-ai.md`](https://github.com/hshadab/preflight-mike/blob/main/docs/mikeoss-legal-ai.md) (MIT). Polskie sformulowanie + adaptacja na realia kancelaryjne PL napisane od zera w tym Appendix. Iterator polityki: wzor z [docs.icme.io](https://docs.icme.io) endpointy `scenarios/feedback/refinePolicy/runPolicyTests`. NIE wpinamy ICME jako zaleznosc - patrz [ADR-0031 PATRON](https://github.com/matematicsolutions/patron/blob/main/governance/adr/0031-deterministyczna-walidacja-z-lokalnym-proof-receipt.md) dla peinych granic.

---

**Podpisy:**
[Imie partnera zarzadzajacego] [data]
[Imie AI Steward] [data]
[Imie External Counsel - MateMatic / Wieslaw Mazur] [data]
```

---

## Workflow generowania Konstytucji dla kancelarii

### Krok 1 - Discovery call (1h)

Z partnerem zarzadzajacym / AI Steward kancelarii:
- Typ kancelarii (specjalizacja, wielkosc, klienci typ)
- Aktualne uzycie AI (lista narzedzi, incydenty jezeli byly)
- Top 3 use cases pozadane
- Ograniczenia (budzet, timeline, regulacyjne)

### Krok 2 - Draft Konstytucji v0.9 (4-8h pracy MateMatic)

- Mission - 3 warianty do wyboru kancelarii
- Articles - wybor 7-9 z listy domyslnej + custom
- Boundaries - mapowanie aktualnych narzedzi na Z/Z/C
- Governance Roles - propozycja struktury
- Audit Trail - template do dostosowania
- Evolution Process - standard

### Krok 3 - Workshop z zarzadem (4h)

- Prezentacja drafta v0.9
- Dyskusja Mission + Articles (intensywna)
- Boundaries decision miedzy konserwatywnym a permisywnym
- Designation governance roles
- Approval do v1.0

### Krok 4 - Finalizacja + publikacja (2-4h)

- Konstytucja v1.0 z poprawkami z workshop
- Communication template do calego zespolu kancelarii
- Setup audit infrastructure
- Schedule kolejnych etapow Playbook

### Krok 5 - Playbook rollout (6-8 tygodni)

Jak opisane wyzej.

---

## Anti-patterny

- **Generyczna Konstytucja** - skopiowanie wzoru bez adaptacji do specyficznej kancelarii. Worthless.
- **Wiecej niz 9 Articles** - rozcienczanie hierarchii. Co ma byc nadrzedne, gubi sie w 15 Articles.
- **MUST bez MUST NOT** - same pozytywne zasady to "ladne slowa". Konieczne sa konkretne zakazy.
- **Brak Roles** - Konstytucja bez wlasciciela = papier. Jezeli nikt nie odpowiada za audit log, nie ma audit log.
- **Bez Evolution Process** - dokument szybko sie zestarzeje. AI Act updates, EDPB guidance, nowe narzedzia kazdy kwartal.
- **Skupienie tylko na regulacjach** - to nie compliance checklist. Mission + judgment > checkbox.
- **Bez Appendix B (mapping)** - bez mapowania na RODO/AI Act, inspekcja moze nie uznac.

---

## Cross-reference

- `anthropic-skills:ai-law-firm` - kontekst kancelarii prawnych
- `anthropic-skills:matematic-company` - voice firmowy MateMatic (oferta dla klienta)
- `anthropic-skills:matematic-reviewer` - recenzja dokumentow eksperckich
- `legal-ai-plugin-governance` - checklist audytu pluginow (input do Boundaries)
- `matematic-stack-zero-cloud` - zatwierdzony stack RODO-safe (input do tabeli narzedzi)
- `matematic-workspace-backup` - art. 32 RODO mapping
- `security-and-hardening` - RODO art. 32 environment
- `anthropic-skills:investor-materials` - jezeli ofertujemy Konstytucje jako produkt na pitch
- `matematic-pricing` - wycena 15-40k / 60-150k PLN
- `matematic-expert-panel` - alternatywny format warsztatu

## Powiazane memories

- `feedback_typografia_myslnik.md` - "-" zawsze w dokumencie
- `reference_narzedzia_oceny_2026-05-14.md` - pozycja #5 spec-kit (source pattern)

## Source attribution

Methodology adapted from github/spec-kit (MIT License) - Constitution -> Spec -> Plan -> Tasks pattern. Adaptacja na B2B services dla kancelarii prawnych. NIE pelna instalacja spec-kit (CLI tool dla developers).
