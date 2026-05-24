# Changelog - redline-docx-pl

## v0.1.0 - 2026-05-22

Pierwsza wersja. Skill-wrapper nad **adeu** 1.7.5 (MIT, (c) 2026 Dealfluence Oy).

- Workflow 4-krokowy: extract -> edits.json -> apply (natywne Track Changes) -> sanitize.
- Smoke test na polskim .docx: extract / apply (`w:ins`+`w:del`) / sanitize (`Result: CLEAN`) - PASS.
- Integracja z [[let-it-be]]: tresc (PII) vs metadane (sanitize) jako dwie warstwy.
- Atrybucja adeu w 3 miejscach: SKILL.md, THIRD_PARTY_INSPIRATIONS.md, ten plik.

Zrodlo discovery: awesome-legaltech (Vaquill) -> sekcja MCP Servers.
