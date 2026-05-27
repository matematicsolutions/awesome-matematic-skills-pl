# Third-party inspirations i atrybucja

Ten projekt powstał metodą cherry-pick MateMatic: bierzemy pattern strukturalny, treść piszemy od zera z dodaną wartością. Poniżej źródła i dokładny zakres zapożyczenia.

## 1. MateMatic `pl-entities` (projekt Patron) - kod własny

- **Źródło**: `backend/src/lib/pl-entities/` w repozytorium Patron (MateMatic Solutions).
- **Status**: kod własny MateMatic, relicencjonowany przez właściciela praw do Apache-2.0 w tym repo (w Patronie żyje pod powłoką AGPL-3.0).
- **Co wzięte (1:1, bo to algorytmy urzędowe)**: walidatory checksum PESEL/NIP/REGON9/REGON14/KRS (algorytmy z ustaw i rozporządzeń), regexy sygnatur orzeczeń (SN/NSA/WSA/KIO/TK), CELEX, ELI, firmy z formą prawną.
- **Co dopisane od zera tutaj** (czego `pl-entities` nie miał):
  - deterministyczna detekcja OSOBA przez gazetteer imion (w Patronie OSOBA była LLM-fallback),
  - rozwiązywanie nakładających się spanów (`detect.mjs`) - w Patronie zostawione "do T2",
  - dwa tryby RODO (anonimizacja nieodwracalna vs pseudonimizacja odwracalna) z wymuszeniem nieodwracalności na poziomie API,
  - port całości do czystego ESM bez zależności i bez kroku budowania.

## 2. gregmos/PII-Shield - cherry-pick patternu (MIT)

- **Źródło**: https://github.com/gregmos/PII-Shield
- **Licencja**: MIT (Grigorii Moskalev, zespół Microsoft Presidio).
- **Snapshot**: 2026-05-22 (v2.0.2).
- **Co wzięte (pattern strukturalny, NIE kod)**:
  1. TTL mapping cleanup (`MappingStore` - domyślnie 7 dni, konfigurowalne),
  2. `source_hash` per dokument (sha256),
  3. plain-text audit log "proves no PII leaves" dla Inspektora (`AuditLog`),
  4. szyfrowane archiwum mapy AES-256-GCM z kluczem scrypt (`encryptArchive`/`decryptArchive`).
- **Co napisane od zera**: cała implementacja w ESM na `node:crypto`/`node:fs`, polskie nazewnictwo zdarzeń, integracja z bramką `ResidualPIIError`.
- **Czego NIE wzięto**: GLiNER zero-shot NER + ONNX Runtime (>100 MB modeli, łamie zasadę zero-LLM/offline), architektura MCP server, 33 typy encji US/UK/zach.EU (nie rozszerzamy zakresu poza polskie PII).

## Zgodność z kanonem cherry-pick MateMatic

- **Snapshot permissive licencji** zachowany (data 2026-05-22 w LICENSE i tutaj).
- **Pattern bierzemy, treść piszemy od zera** - powyższe listy "co dopisane / od zera".
- **Atrybucja w 3 miejscach**: [LICENSE](LICENSE), [README.md](README.md), [governance/CONSTITUTION.md](governance/CONSTITUTION.md).
