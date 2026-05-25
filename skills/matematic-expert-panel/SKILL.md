---
name: matematic-expert-panel
description: Generuje warsztat "MateMatic Expert Panel" - multi-perspective analiza casu kancelarii przez 5-7 ekspertow z roznych dziedzin (compliance officer, IT security, etyk AI, partner zarzadzajacy, junior prawnik, klient kancelarii, regulator). Cherry-pick patternu SuperClaude Business Panel mode (MIT) - 9 modeli person, scoring, decision matrix. Output - 90-min warsztat fakturowany 5-15k PLN dla zarzadu kancelarii + raport pozegnal. Uzywaj gdy kancelaria pyta o wieloperspektywiczna analize ryzyka AI, decyzje strategiczne wdrozenia AI, drugi opinion od ekspertow, war-gaming wdrozenia, pre-mortem nowego narzedzia. Trigger - "expert panel", "panel ekspertow", "wieloperspektywiczna analiza", "war game AI", "pre-mortem", "drugi opinion AI", "warsztat decyzyjny", "multi-perspective", "decision matrix AI". Bazuje na SuperClaude-Org/SuperClaude_Framework (MIT) - cherry-pick mode, NIE pelna instalacja frameworka.
metadata:
  author: Wieslaw Mazur / MateMatic
  version: 1.0.0
  project: MateMatic Expert Panel Product
  source_pattern: SuperClaude-Org/SuperClaude_Framework (MIT) - Business Panel mode only
  format: 90-min warsztat live (online lub on-site)
  pricing_range: 5-15k PLN per warsztat (single case)
  output_format: live warsztat + raport pozegnal markdown/PDF
---

# MateMatic Expert Panel - multi-perspective warsztat kancelarii

Generuje warsztat decyzyjny dla zarzadu kancelarii. Cherry-pick z `SuperClaude-Org/SuperClaude_Framework` (MIT) - Business Panel mode z 9 person. Adaptacja na potrzeby kancelarii prawnych: zamiast generic business persons, mamy 7 kluczowych perspektyw rolnych w organizacji prawnej.

**Format:** 90-minutowy warsztat live z zarzadem kancelarii (online lub on-site), facilitated przez MateMatic. Analiza konkretnego casu (np. "Czy wdrazac voice clone dla obslugi infolinii?") przez 7 person z roznych perspektyw + final decision matrix.

**Pricing:** 5-15k PLN per warsztat (zalezy od wielkosci kancelarii i zlozonosci casu). Drugi poziom oferty MateMatic, kierowany do partnerow zarzadzajacych.

---

## Geneza - dlaczego ten skill istnieje

**Problem klienta:** zarzad kancelarii podejmuje decyzje wdrazenia AI w "echo chamber" partnerow. Brakuje perspektyw IT, compliance, junior prawnikow, regulatora. Skutek: blind spots, post-deployment bolesc.

**SuperClaude pattern:** Business Panel mode aktywuje multiple specialized "persons" w jednym kontekscie, kazda z innym mental modelem. Adaptujemy: zamiast generic CEO/CTO/CFO mamy role typowe dla wdrozenia AI w kancelarii.

**Wartosc dla MateMatic:** sprzedazowo - latwy do zakupu produkt (90 min warsztat vs 6-tygodniowy playbook), low commitment, daje insights ktore zazwyczaj przegapia partner-only dyskusja. Output: raport ktory zarzad moze zaprezentowac wlasnej organizacji.

---

## 7 person panelu (default skład)

Modyfikowalne per kancelaria. Default 7 person dla pelnej analizy:

### 1. Compliance Officer / DPO
**Perspektywa:** RODO, AI Act, tajemnica zawodowa, audit logs.
**Pyta:** "Jakie dane wchodza? Gdzie wychodza? Czy mamy DPA? Czy mamy podstawe prawna przetwarzania?"
**Wartosc:** chroni przed greaszczamy regulacyjnymi. Czesto najbardziej konserwatywny.

### 2. IT Security Lead
**Perspektywa:** infrastruktura, integracje, attack surface, key management.
**Pyta:** "Gdzie zyje klucz API? Co sie stanie po breach? Czy mamy MFA? Czy log jest tamper-evident?"
**Wartosc:** unmasks technical debt + supply chain risk.

### 3. Etyk AI (zewnetrzny, np. MateMatic)
**Perspektywa:** bias, fairness, transparentnosc, AI Act art. 14 human oversight, evolution.
**Pyta:** "Czy decyzja ma wplyw na klienta? Czy klient wie ze AI uczestniczy? Co jezeli AI zwroci wynik dyskryminujacy?"
**Wartosc:** dotyka tych pytan ktore inni unikaja.

### 4. Partner Zarzadzajacy
**Perspektywa:** strategia, ROI, brand, lojalnosc partnerow.
**Pyta:** "Ile to kosztuje? Kiedy zwraca? Jak komunikujemy klientom? Czy konkurencja juz to ma?"
**Wartosc:** kotwica biznesowa. Bez Partnera nie ma decyzji.

### 5. Junior Prawnik / Aplikant
**Perspektywa:** day-to-day operations, frustration points, learning curve.
**Pyta:** "Czy to ma latwy interfejs? Czy mnie zwolnia czy pomoze? Czy ucze sie mniej przez AI?"
**Wartosc:** glos osoby ktora najczesciej bedzie uzywac narzedzia. Czesto pomijany.

### 6. Klient Kancelarii (persona, nie real client)
**Perspektywa:** zaufanie, transparentnosc, value-for-money, lojalnosc.
**Pyta:** "Czy chce zeby AI dotykalo mojej sprawy? Czy zaplacę mniej? Czy moge zaufac?"
**Wartosc:** market sense check. Klient kancelarii nie zawsze chce AI.

### 7. Regulator (persona - UODO + AI Office)
**Perspektywa:** worst-case audit, RODO + AI Act enforcement.
**Pyta:** "Jak udowodnicie ze AI Act art. X jest spelniony? Pokazcie audit log per case. Co bylo inputem do tej decyzji?"
**Wartosc:** test odpornosci dokumentacji. Jezeli zarzad nie umie odpowiedziec, regulator tez nie.

---

## Custom persons (opcjonalnie)

Per kancelaria mozna swap 1-2 default persons na:

- **Specjalista IP / Litigation** - dla kancelarii butikowych specjalistycznych
- **Marketing/Business Development** - dla kancelarii rosnacych
- **HR / People Lead** - jezeli kwestia dotyczy adopcji w zespole
- **Insurer / Risk Manager** - dla kancelarii w grupie kapitalowej
- **Klient Korporacyjny vs Klient Indywidualny** - rozne persony klientow
- **Generyczny "AI Skeptic"** - intencjonalna kontrnarracja (rola devil's advocate)

---

## Architektura warsztatu (90 min)

### Faza 1 - Setup + case framing (15 min)

- Powitanie + rules (Chatham House Rule, free discussion, no judgment)
- MateMatic prezentuje **case w 5 zdaniach** (np. "Kancelaria rozwaza wdrozenie voice clone Wieslawa do automatycznych odpowiedzi na klientow przez infolinia. Inwestycja 50k PLN, czas 3 mc. Zarzad chce decyzji do konca miesiaca.")
- Wprowadzenie 7 person + ich perspektyw

### Faza 2 - Round Robin Analysis (40 min, 5-6 min per persona)

Per persona facilitated przez MateMatic:

1. **Compliance Officer** - 5-6 min: czyta case z perspektywy regulacyjnej, identifies pytania ktore zostaja unaddressed
2. **IT Security** - 5-6 min: technical due diligence questions
3. **Etyk AI** - 5-6 min: ethical and fairness analysis
4. **Partner** - 5-6 min: business case challenge
5. **Junior** - 5-6 min: operational adoption analysis
6. **Klient** - 5-6 min: trust + value analysis (MateMatic gra role)
7. **Regulator** - 5-6 min: audit readiness test (MateMatic gra role)

**Output per persona:** 3 najwazniejsze pytania / risks / blind spots ktore powinny byc adresowane przed decision.

### Faza 3 - Scoring (15 min)

Decision Matrix z 7 wymiarami (1 per persona). Skala 1-10 per wymiar.

| Wymiar | Waga | Skor | Wazone | Uzasadnienie |
|---|---|---|---|---|
| Compliance readiness | 20% | X/10 | X.X | ... |
| Security posture | 15% | X/10 | X.X | ... |
| Ethical clearance | 15% | X/10 | X.X | ... |
| Business ROI | 20% | X/10 | X.X | ... |
| Operational fit | 10% | X/10 | X.X | ... |
| Klient acceptance | 10% | X/10 | X.X | ... |
| Audit readiness | 10% | X/10 | X.X | ... |
| **TOTAL** | 100% | - | **X.X/10** | - |

Threshold akceptacji:
- **>= 7.0/10** - REKOMENDACJA WDROZENIE (z warunkami z analizy)
- **5.0-6.9** - DOPRACUJ I WROC (które wymiary < 6 wymagaja akcji)
- **< 5.0** - WSTRZYMAJ / PRZEPROJEKTUJ

### Faza 4 - Decision + Action Items (15 min)

Pelna grupa:
- Czy wynik scoringu odpowiada intuicji?
- Top 3-5 action items wynikajacych z analizy
- Owner per action item + deadline
- Trigger dla re-konsultacji panelu (np. po wdrozeniu pilotu)

### Faza 5 - Closeout (5 min)

- MateMatic obiecuje raport pozegnal w 5 dni roboczych
- Confirm follow-up call po 30 dniach (jezeli zakontraktowany)
- Thank you + summary key insights

---

## Output raport pozegnal (5-15 stron PDF)

```markdown
# MateMatic Expert Panel - Raport pozegnal
**Kancelaria:** [nazwa]
**Data warsztatu:** YYYY-MM-DD
**Case analizowany:** [case w 1-2 zdaniach]
**Facilitator:** Wieslaw Mazur / MateMatic

---

## Executive Summary (1 strona)

- **Case:** [streszczenie]
- **Werdykt:** REKOMENDACJA / DOPRACUJ I WROC / WSTRZYMAJ
- **Skor calkowity:** X.X / 10
- **Top 3 risks:** ...
- **Top 3 opportunities:** ...
- **Action items:** [lista z owners + deadlines]

## Analiza per persona (5-8 stron)

### 1. Compliance Officer / DPO
**Kluczowe pytania:** ...
**Identified risks:** ...
**Recommendations:** ...

[powtorz dla 2-7 person]

## Decision Matrix (1 strona)

[Tabela scoring z Faza 3 + uzasadnienia per wymiar]

## Action Items (1 strona)

| # | Item | Owner | Deadline | Status |
|---|---|---|---|---|
| 1 | ... | ... | ... | OPEN |
| ... | ... | ... | ... | ... |

## Appendix A - Methodology

Methodology adapted from SuperClaude-Org/SuperClaude_Framework (MIT License) - Business Panel mode. Adaptacja na kancelarie prawne z 7 default persons.

## Appendix B - Polecane next steps (jezeli sprzedazowo)

- Konstytucja AI (skill matematic-konstytucja-ai) dla pelnej governance struktury
- AI Implementation Playbook 6-8 tygodni
- Stack zero-cloud audit (matematic-stack-zero-cloud)

## Podpisy

[Facilitator] [data]
[AI Steward kancelarii] [data]
```

---

## Workflow generowania warsztatu

### Krok 1 - Pre-warsztat call (30 min)

Z partnerem zarzadzajacym kancelarii:
- Co to za case (precyzyjnie)
- Kto bedzie w sali (lista 4-8 osob z zarzadu)
- Custom persons (jezeli inne niz default 7)
- Cel decyzyjny (binary GO/NO-GO vs multi-option)
- Logistyka (online / on-site, kanal, czas)

### Krok 2 - Preparation (4-6h MateMatic)

- Case framing - 5 zdan + 3 kluczowe parametry (cena, czas, ryzyko)
- Persona briefs - per persona 1 strona ze specyficznym kontekstem dla tej kancelarii
- Decision matrix template z wagami dopasowanymi do kancelarii
- Slides facilitation 6-8 slidow

### Krok 3 - Warsztat 90 min

Jak opisane wyzej. MateMatic facilituje + gra role Klient + Regulator + Etyk AI (jezeli kancelaria nie ma wlasnego).

### Krok 4 - Raport pozegnal (4-8h MateMatic)

Output w 5 dni roboczych. Raport markdown + PDF (skill `anthropic-skills:pdf`).

### Krok 5 - Optional follow-up (30 min po 30 dniach)

Sprawdzenie action items. Jezeli kancelaria chce - zakontraktowanie kolejnego warsztatu lub Playbook 6-tyg.

---

## Anti-patterny

- **Personifikacja bez przygotowania** - "play role" wymaga rzeczywistych briefingow, nie improwizacji
- **MateMatic gra wszystkich 7 person** - zatraca kontekst kancelarii. MUST: 4-5 person to ludzie z kancelarii, 2-3 person to MateMatic
- **Scoring bez merit** - same liczby bez uzasadnienia. Wagi musza miec sens dla tej kancelarii
- **Brak action items** - warsztat bez "co dalej" to teatr
- **Pytanie zamknieté "ile inwestujemy?"** - to dyskusja decyzyjna, nie procurement. Cena jest INPUTEM, nie outputem
- **Generic personae bez kontekstu kancelarii** - butikowa IP rozni sie od duzej kancelarii ogolnej. Adaptuj briefingi

---

## Komercyjne wariacje produktu

### Variant A - Single Case Panel (5-8k PLN)

Standardowy 90-min warsztat + raport. Single case. Default 7 person.

### Variant B - Strategy Panel (10-15k PLN)

3-godzinny warsztat (przerwy) + 3 cases naraz + comparative report. Wymaga dwoch facilitatorow MateMatic.

### Variant C - Quarterly Panel (subskrypcja 30-40k PLN/kwartal)

4 warsztaty rocznie + utrzymanie governance archive + roczna ewolucja Konstytucji AI. Tier 1 contract.

### Variant D - Multi-kancelaria Panel (50-80k PLN)

3-5 kancelarii partnerskich, mid-tier, dyskutuja wspolny case (np. "Czy NRA powinna wydac wytyczne AI?"). Premium content for thought leadership.

---

## Cross-reference

- `anthropic-skills:ai-law-firm` - kontekst kancelarii
- `matematic-konstytucja-ai` - downstream produkt (Konstytucja AI po warsztacie)
- `matematic-pricing` - wycena per Variant A/B/C/D
- `anthropic-skills:matematic-company` - voice firmowy MateMatic
- `anthropic-skills:matematic-ppt` - prezentacja slides na warsztat
- `legal-ai-plugin-governance` - input dla persona IT Security
- `anthropic-skills:pdf` - generacja raportu pozegnal PDF

## Powiazane memories

- `reference_narzedzia_oceny_2026-05-14.md` - pozycja #6 SuperClaude (source pattern)
- `reference_memo_ejaj_brand.md` - jezeli warsztat sluzy jako content do MEMO

## Source attribution

Methodology adapted from SuperClaude-Org/SuperClaude_Framework (MIT License) - Business Panel mode (9 person, scoring, decision matrix patterns). Adaptacja na warsztat kancelarii prawnej z 7 dedykowanymi persons. NIE pelna instalacja SuperClaude (nadpisalaby nasz custom stack).
