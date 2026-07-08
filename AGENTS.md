# AGENTS.md - awesome-matematic-skills-pl

An [agents.md](https://agents.md) standard file (Linux Foundation / Agentic AI Foundation) - canonical instructions for AI agents working with this repository. Read natively by Cursor, Codex (OpenAI), Jules (Google), Devin / Windsurf, Aider, Amp, Factory, GitHub Copilot, Claude Code.

## Project goal

This repo is a **curated hub of Agent Skills for law**. Two layers:

- `./skills/` - a bundle of 14 skills installed locally (a directly usable bundle).
- README + `.claude-plugin/marketplace.json` - an awesome list and a plugin marketplace manifest.

This is **not a commercial product** - it is an MIT curatorial canon. Its value is an organized map of AI skills for law that lets law firms and NGOs plug ready-made building blocks into their practice without building them from scratch.

## MateMatic context (HARD CONSTRAINTS)

[MateMatic Solutions](https://matematicsolutions.com) = local, GDPR-safe AI tools for law firms. Zero-cloud self-host, vendor-neutral, auditable.

The hub must be:

- **Bilingual, with a clear default language** - skill titles, descriptions, and triggers are grounded in legal practice and in the applicable law.
- **GDPR-safe by default** - no skill sends client data to the cloud without isolation or a DPA / SCC.
- **Vendor-agnostic** - the Agent Skills format (an Anthropic open standard) works in Claude Code, Cowork, Claude.ai, OpenAI Codex CLI, Gemini CLI, Manus, Mistral Vibe.
- **No citation hallucination** - every legal citation in a SKILL.md MUST pass `citation-grounding-pl` before the PR.

## Repo structure

```
.claude-plugin/
  marketplace.json     - plugin marketplace manifest (14 entries)
.github/
  (issue templates - planned)
skills/
  <name>/
    SKILL.md           - frontmatter + body
    references/        - lazy-loaded documentation
    scripts/           - executable code
    THIRD_PARTY_INSPIRATIONS.md  - per-skill cherry-pick canon (if present)
scripts/
  check-marketplace.mjs - consistency validator for marketplace.json vs ./skills/
examples/
  pipeline-end-to-end.md - how the 6-layer chain works step by step
README.md              - curated list + bundle of 14 skills
CONTRIBUTING.md        - how to add a skill
LICENSE                - MIT (curatorial)
NOTICE                 - per-skill license attribution
CHANGELOG.md           - change log
SECURITY.md            - security policy
THIRD_PARTY_INSPIRATIONS.md - cherry-pick canon at the repo level
CITATION.cff           - citation metadata for legal scholars
AGENTS.md              - this file
```

## Build and test

No compilation.

**Consistency test** = `node scripts/check-marketplace.mjs` - validates that:
- every entry in `.claude-plugin/marketplace.json` has a matching folder in `./skills/<name>/`
- every folder in `./skills/` is declared in marketplace.json
- every SKILL.md has frontmatter with `name`, `description`
- names in marketplace.json = folder names

**Visual test** = open `README.md` in the GitHub web UI and check that the tables render correctly.

## Writing rules (CRITICAL)

### Professional secrecy
- **NEVER** include data from real cases in README, SKILL.md, CONTRIBUTING, or in descriptions in marketplace.json. Attorney privilege (art. 6 PrAdw - Law on the Bar) + legal-adviser privilege (art. 3 RadcPrU - Law on Legal Advisers). See the policy described in SECURITY.md.
- No amounts, exact dates, case numbers, initials, or company names from real cases. Test placeholders: `Jan Kowalski` / `Anna Nowak` (the Polish John Doe / Jane Doe).

### Content
- **Match the repo's default language** in SKILL.md and README descriptions. English is acceptable in trigger keywords and in SKILL.md for skills that are English-first by nature (e.g. the saos-orzecznictwo description contains English fragments).
- **No em-dash** (`—`) - only the hyphen `-`.
- **No non-ASCII characters in commit messages**.
- **No decorative emoji** - deliberate brand emoji are OK (e.g. 🦅 in the context of the series cycle).
- **Polish quotation marks** „..." rather than plain English "...".

### Validation
- **Run the internal QA pipeline for Polish-language text** ALWAYS before committing changes to Polish files (README, CONTRIBUTING, SKILL.md, CHANGELOG, NOTICE). MateMatic maintainers use their own QA tools before publishing - external contributors are responsible for the readability and correctness of the Polish text.

## What NOT to do (hard rules)

- **Do NOT add client data**, leads, firm-specific pricing, or sales plans - that belongs in private memory, not a public repo.
- **Do NOT add `[[wiki-links]]`** to MateMatic private memory files - those are dead links in a public repo.
- **Do NOT insert sales marketing** ("revolutionary", "game changer", "must-have") - the GitHub buyer is a technical / legal buyer, not a marketing buyer.
- **Do NOT copy the content of CC-BY-NC-ND or AGPL skills** into this repo (curatorial MIT license) - only the pattern plus your own content. See `THIRD_PARTY_INSPIRATIONS.md`.
- **Do NOT leave outdated links** - if a skill is renamed or removed, fix it immediately.

## Related MateMatic repos (keep in sync)

| Repo | License | Use |
|---|---|---|
| [patron](https://github.com/matematicsolutions/patron) | AGPL-3.0 | Local AI agent - can use skills from this hub |
| [matematic-legal-verify-pl](https://github.com/matematicsolutions/matematic-legal-verify-pl) | Apache 2.0 | Plugin bundling 4 of the 6 validation layers into one install |
| [matematic-anonimizacja-pl](https://github.com/matematicsolutions/matematic-anonimizacja-pl) | Apache 2.0 | PII anonymization engine - companion to the grounding skills |
| [matematic-contract-review-pl](https://github.com/matematicsolutions/matematic-contract-review-pl) | Apache 2.0 | Bulk contract audit - pipeline uses redline-docx-pl |
| [matematic-pomoc-prawna-pl](https://github.com/matematicsolutions/matematic-pomoc-prawna-pl) | Apache 2.0 | Plugin for NGOs - uses the intake-sufficiency-pl pattern |
| [lpm-pl](https://github.com/matematicsolutions/lpm-pl) | Apache 2.0 | Legal Project Management - companion to audit-bundle |
| [mcp-saos](https://github.com/matematicsolutions/mcp-saos) | MIT | MCP connector - source data for the saos-orzecznictwo skill |
| [mcp-nsa](https://github.com/matematicsolutions/mcp-nsa) | MIT | MCP connector for NSA (Supreme Administrative Court) - source data |
| [mcp-isap](https://github.com/matematicsolutions/mcp-isap) | MIT | MCP connector for Sejm ELI |
| [mcp-krs](https://github.com/matematicsolutions/mcp-krs) | MIT | MCP connector for KRS (National Court Register) |
| [mcp-eu-sparql](https://github.com/matematicsolutions/mcp-eu-sparql) | MIT | MCP connector for EUR-Lex - source data for eu-sparql-search |
| [mcp-eu-compliance](https://github.com/matematicsolutions/mcp-eu-compliance) | MIT | Offline corpus of EU law |
| [praxis](https://github.com/matematicsolutions/praxis) | CC BY-SA 4.0 | LegalTech guides |
| [matematic-readiness](https://github.com/matematicsolutions/matematic-readiness) | CC BY-SA 4.0 | Law-firm readiness audit |
| [.github](https://github.com/matematicsolutions/.github) | CC BY-SA 4.0 | Organization profile |

## Agent compatibility

The [AGENTS.md](https://agents.md) standard. For Claude Code there is additionally a [CLAUDE.md](./CLAUDE.md) file (if present - currently this AGENTS.md is sufficient, as Claude Code reads `AGENTS.md` natively).

The skills in this repo follow the [Agent Skills format](https://github.com/anthropics/skills) - an open format, independent of the LLM vendor.

## License

- Curatorial (README, taxonomy, marketplace.json, this AGENTS.md): **MIT**
- Per-skill: the license declared in the `SKILL.md` frontmatter and `marketplace.json`. In bundle v0.1.0 all skills are Apache-2.0 or MIT (see NOTICE).

## Contact

- **Maintainer**: [Wieslaw Mazur](https://www.linkedin.com/in/wieslawmazur/)
- **Site**: [matematicsolutions.com](https://matematicsolutions.com)
- **Email**: kontakt@matematic.co
