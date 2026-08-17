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

## 3. Rizzo-AI-Academy/rizzo-pii - cherry-pick patternu (MIT)

- **Źródło**: https://github.com/Rizzo-AI-Academy/rizzo-pii
- **Licencja**: MIT.
- **Snapshot**: 2026-07-13.
- **Co wzięte (pattern strukturalny, NIE kod)**:
  1. stabilny placeholder per (label, wartość znormalizowana) - ten sam byt zawsze dostaje ten sam placeholder,
  2. lokalny słownik odwracania {placeholder -> wartość} z eksportem/importem JSON, który przeżywa restart aplikacji,
  3. osobny krok "Restore" - wklejasz odpowiedź LLM, oryginały wracają lokalnie.
- **Co napisane od zera**: `SlownikOdwracania` w ESM (klucz `KATEGORIA:znormalizowana`, odtwarzanie liczników z sufiksów placeholderów), integracja z istniejącą detekcją checksumową i bramką residual.
- **Czego NIE wzięto**: UI (Streamlit), detekcja przez Presidio/spaCy (łamie zasadę zero zależności), kategorie encji US.

## 4. moyupeng0422/legal-doc-redactor - cherry-pick patternu (MIT)

- **Źródło**: https://github.com/moyupeng0422/legal-doc-redactor
- **Licencja**: MIT.
- **Snapshot**: 2026-07-13.
- **Co wzięte (pattern strukturalny, NIE kod)**:
  1. batch wielu plików z JEDNOLITĄ numeracją placeholderów między plikami (liczniki nie resetują się per plik),
  2. mapping w sidecarze obok dokumentów (u nas: `*.mapa-pii.json` - ostrzeżenie w samej nazwie pliku).
- **Co napisane od zera**: `pseudonimizujPaczke` w ESM na wspólnym słowniku, bramka residual rozszerzona na całą paczkę (każdy wynik vs wszystkie oryginały słownika), zdarzenia audit logu per plik.
- **Czego NIE wzięto (roadmap v2)**: restore `.docx` z zachowaniem tracked changes przez podmianę na poziomie runs - nasz silnik jest dziś tekstowy; odnotowane w CHANGELOG jako v2.

## Zgodność z kanonem cherry-pick MateMatic

- **Snapshot permissive licencji** zachowany (data 2026-05-22 w LICENSE i tutaj).
- **Pattern bierzemy, treść piszemy od zera** - powyższe listy "co dopisane / od zera".
- **Atrybucja w 3 miejscach**: [LICENSE](LICENSE), [README.md](README.md), [governance/CONSTITUTION.md](governance/CONSTITUTION.md).
