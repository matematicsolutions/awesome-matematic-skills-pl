# AGENTS.md - Let It Be (matematic-anonimizacja-pl)

Plik standardu [agents.md](https://agents.md) (Linux Foundation / Agentic AI Foundation) - kanoniczne instrukcje dla agentów AI pracujących z tym repozytorium.

## Cel projektu

Samodzielny silnik anonimizacji i pseudonimizacji polskich danych osobowych w tekście. RODO-safe, offline, zero zależności (`node:*` only). Trzy interfejsy: skill Claude Code ([SKILL.md](SKILL.md)), CLI ([bin/cli.mjs](bin/cli.mjs)), biblioteka ([src/index.mjs](src/index.mjs)).

## Kontekst MateMatic (twarde ograniczenia)

Repo prowadzi [MateMatic Solutions](https://matematicsolutions.com). Obowiązuje [governance/CONSTITUTION.md](governance/CONSTITUTION.md) - 7 artykułów. Najważniejsze:

- **Lokalność** - nie dodawaj zależności od żadnego API/modelu. Detekcja zostaje deterministyczna (regex + checksuma + gazetteer).
- **Dwa tryby** - nie łącz anonimizacji z pseudonimizacją. Tryb anonimizacji NIE może zwracać mapy ani surowych wartości.
- **Bramka residual** - nie usuwaj sprawdzenia "no PII leaves". Komunikaty błędów nie zawierają wartości PII.

## Build i test

```bash
node --test          # 18 testów, zero zależności, brak kroku budowania
node bin/cli.mjs --help
```

Nie commituj jeśli testy fail. Konwencja organizacji: **bez polskich znaków w commit messages** (a->a, e->e, l->l, o->o, s->s, n->n, c->c, z->z) i **myślnik to zawsze hyphen "-"**, nigdy em-dash.

## Zasady kodu

- Czysty ESM (`.mjs`), Node >=20, tylko `node:*`. Bez build stepu, bez `node_modules`.
- Każda nowa reguła detekcji = test w `test/silnik.test.mjs`.
- Wartości testowe muszą być syntetyczne i poprawne checksumowo (nie czyjeś realne dane).

## Źródła prawdy (kolejność czytania)

1. [README.md](README.md)
2. [governance/CONSTITUTION.md](governance/CONSTITUTION.md)
3. [THIRD_PARTY_INSPIRATIONS.md](THIRD_PARTY_INSPIRATIONS.md)
4. [SKILL.md](SKILL.md)

## Licencja

Apache-2.0. Pattern operacyjny cherry-pick z gregmos/PII-Shield (MIT). Patrz [LICENSE](LICENSE).
