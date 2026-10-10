# AGENTS.md - Let It Be (matematic-anonimizacja-pl)

An [agents.md](https://agents.md) standard file (Linux Foundation / Agentic AI Foundation) - canonical instructions for AI agents working with this repository.

## Project goal

A standalone engine for anonymization and pseudonymization of Polish personal data in text. GDPR-safe, offline, zero dependencies (`node:*` only). Three interfaces: a Claude Code skill ([SKILL.md](SKILL.md)), a CLI ([bin/cli.mjs](bin/cli.mjs)), a library ([src/index.mjs](src/index.mjs)).

## MateMatic context (hard constraints)

The repo is maintained by [MateMatic Solutions](https://matematicsolutions.com). [governance/CONSTITUTION.md](governance/CONSTITUTION.md) applies - 7 articles. The most important:

- **Locality** - do not add a dependency on any API/model. Detection stays deterministic (regex + checksum + gazetteer).
- **Two modes** - do not combine anonymization with pseudonymization. Anonymization mode MUST NOT return a map or raw values.
- **Residual gate** - do not remove the "no PII leaves" check. Error messages do not contain PII values.

## Build and test

```bash
node --test          # zero dependencies, no build step
node bin/cli.mjs --help
```

Do not commit if tests fail. Organization convention: **no Polish characters in commit messages** (a->a, e->e, l->l, o->o, s->s, n->n, c->c, z->z) and **the dash is always a hyphen "-"**, never an em-dash. Enforced by `.githooks/commit-msg`; after cloning run `git config core.hooksPath .githooks`.

## Code rules

- Pure ESM (`.mjs`), Node >=20, `node:*` only. No build step, no `node_modules`.
- Every new detection rule = a test in `test/silnik.test.mjs`.
- Test values must be synthetic and checksum-valid (not someone's real data).

## Sources of truth (reading order)

1. [README.md](README.md)
2. [governance/CONSTITUTION.md](governance/CONSTITUTION.md)
3. [THIRD_PARTY_INSPIRATIONS.md](THIRD_PARTY_INSPIRATIONS.md)
4. [SKILL.md](SKILL.md)

## License

Apache-2.0. Operational pattern cherry-picked from gregmos/PII-Shield (MIT). See [LICENSE](LICENSE).
