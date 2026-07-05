# Format plugina dziedzinowego

Anatomia plugina „per dziedzina prawa" (prawo pracy, spółki, zamówienia publiczne…) -
wzorzec do rozbudowy tego marketplace o kolejne bundle i do skill-packów PATRONa.
Zaadaptowany z formatu 24 plugarów `akunikkola/claude-for-legal-finland` (MIT), który
z kolei odwzorowuje `anthropics/claude-for-legal`.

## Anatomia (co zawiera jeden plugin)

```
<dziedzina>/
├── .claude-plugin/plugin.json    # nazwa kebab-case, semver, opis bez "cyfra,cyfra"
├── CLAUDE.md                     # SIATKA BEZPIECZEŃSTWA (varaverkko) - patrz niżej
├── .mcp.json                     # konektory, których skille faktycznie używają (minimum!)
├── skills/<nazwa>/SKILL.md       # 2-4 skille, każdy = jeden workflow
│   └── references/*.md           # doktryna ładowana na żądanie, nie do frontmatteru
├── agents/<nazwa>.md             # opcjonalnie: delegowalne etapy (np. weryfikator źródeł)
└── examples/ lub link do ../examples/   # fixture'y + kryteria behawioralne
```

## Reguły, które czynią plugin dobrym

1. **SKILL.md mówi CO robić; CLAUDE.md pluginu jest siatką bezpieczeństwa.** Jeśli
   poprawny wynik skilla zależy od tego, że guardrail z CLAUDE.md ratuje błąd - wada
   jest w skillu; przenieś wiedzę do skilla. Siatka to polisa, nie mechanizm główny.
2. **Substancja ze źródła, nie z pamięci** - skill dziedzinowy wskazuje konektor
   (SAOS / ISAP / eu-sparql) i tabelę podstaw prawnych; ustawy, na których się opiera,
   dopisuje do rejestru [`../seuranta/ustawy.json`](../seuranta/ustawy.json)
   (wachta legislacyjna alarmuje o uchyleniu/zmianie nazwy).
3. **Placeholdery sygnatur w przykładach** (`II CSK NN/RR`) albo realne sprawy jawnie
   oznaczone jako zweryfikowane (wzór: `kio-grounding-pl`, KIO 1564/18 + id SAOS).
   Realistyczne fikcyjne sygnatury wyciekają do outputów - patrz
   [`styl-cytatu.md`](styl-cytatu.md).
4. **Jawny zakres ujemny** - plugin mówi, czego NIE pokrywa (wzór: SAOS nie indeksuje
   WSA/NSA; skill podatkowy nie podaje stawek z pamięci).
5. **Fixture'y przed publikacją** - co najmniej jeden „brudny" materiał ćwiczebny
   (sprzeczności jak w realnym zleceniu, bez ukrytej modelowej odpowiedzi) + lista
   kryteriów behawioralnych. To samo służy potem za test regresji.
6. **Konektory minimum** - `.mcp.json` zawiera tylko to, czego skille używają;
   pluginy czysto metodyczne (fundament) nie mają konektorów wcale.

## Checklist nowego plugina (bramka przed merge)

- [ ] `plugin.json` zgodny z manifestem (`node scripts/check-marketplace.mjs` zielony)
- [ ] CLAUDE.md pluginu obecny i **trackowany w git** (`.gitignore` ma `/CLAUDE.md`, nie `CLAUDE.md`)
- [ ] skille przechodzą `skill-audit --marketplace`
- [ ] ustawy cytowane przez skille dopisane do `seuranta/ustawy.json`
- [ ] przykłady: placeholdery NN/RR albo realne sprawy z oznaczeniem i źródłem
- [ ] fixture + kryteria behawioralne w `examples/`
- [ ] sekcja „Czego NIE robi" w każdym SKILL.md
