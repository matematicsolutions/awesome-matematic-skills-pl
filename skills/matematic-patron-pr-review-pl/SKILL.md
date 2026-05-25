---
name: matematic-patron-pr-review-pl
description: Recenzent PR/diffow dla PATRONa - polski LegalTech AI agent dla kancelarii. Wylapuje regresje specyficzne dla repo PATRON ktorych nie zlapie generyczny lint - org scoping multi-tenant, authless routes, niespodzianki w migracjach SQLite/Postgres, bezposredni SQL poza warstwa db, brak worker sync w cache, UI bez generated SDK, sekrety w logach, regresje audit_log, brak grounding cytatow, AI Act art. 12 record-keeping. Format findings file:line -> problem -> correct pattern, 3 buckets Blocker/Should-fix/Nit. Cherry-pick struktury z dograh v1.31.0 review-pr (BSD-2). Uzywaj gdy - recenzja PR/diff PATRON przed merge, code review pre-commit, audyt zmian w mcp-security-gateway/audit_log/ring-policy/auth, review zmian w MCP serverach matematicsolutions/*, weryfikacja czy nowy kod nie wprowadza wyciekow danych klienta kancelarii (RODO/tajemnica adwokacka), audyt drift dokumentacji vs kod. Trigger - "marko review PR", "code review PATRON", "audyt diff", "review tej zmiany", "sprawdz PR", "czy bezpiecznie merge", "PR audit", "security review PATRON", "blast radius zmiany".
---

# matematic-patron-pr-review-pl

Recenzent PR/diffow PATRON - polskiego LegalTech AI agenta dla kancelarii. Cherry-pick struktury z [dograh v1.31.0 review-pr](https://github.com/dograh-hq/dograh/blob/main/.agents/skills/review-pr/SKILL.md) (BSD-2, 286 linii), zaadaptowane pod kontekst MateMatic.

**Komplementarny do:**
- `marko-pl-content` (skill MateMatic) - ocena tresci (artykuly, copy LI, BW). Ten ocenia **diff kodu**.
- [matematic-konstytucja-ai](../matematic-konstytucja-ai) (w tym hubie) - dokument governance dla klienta. Ten chroni kod produktu.
- Self-review pre-commit (6 zasad MateMatic) - poprzedza ten skill, sprawdza ogolne, ten skill nad nimi sprawdza repo-specific risks.

## Kiedy uzywac

- Recenzja PR przed merge do `main` w repo PATRON / KGLF / matematicsolutions MCP serwery
- Pre-commit audit wlasnego diffu w PATRONie
- Audyt zmian w komponentach krytycznych: mcp-security-gateway, audit_log, ring-policy, auth
- Po duzej refaktoryzacji - sweep pod katem regresji
- Przed pushem do `origin` po sesji 3+ commitow

## Glowne tryby awarii w repo PATRON

1. **Multi-tenant - brak org scoping** na request-reachable read/write (kancelaria A widzi sprawe kancelarii B)
2. **Authless route lub websocket** - silently public endpoint
3. **Webhook bez signature verification** lub trust w unsigned fields
4. **SQL pisany poza `lib/db/*_client.ts`** - inkasacja warstwy
5. **Cache per-worker bez worker sync** - stale state w innych procesach
6. **UI bypassuje generated SDK** - direct `fetch('/api/v1/...')` zamiast typed client
7. **Migracja niebezpieczna na produkcji** - NOT NULL bez backfilla, brak downgrade()
8. **MCP tool reimplementuje auth** zamiast `authenticate_mcp_request()` (patrz [matematic-mcp-fastmcp-instructions-pl](../matematic-mcp-fastmcp-instructions-pl) w tym hubie)
9. **PII/cytat prawniczy w logach** - naruszenie RODO + tajemnica adwokacka (art. 6 ust. 1 PrAdw + art. 3 ust. 3 RadcPrU)
10. **Brak audit_log entry** dla operacji decyzyjnej (AI Act art. 12 record-keeping)

## Jak prowadzic review

1. Pobierz diff:
   - GitHub PR: `gh pr diff <N>` lub `gh pr view <N> --json files,additions,deletions`
   - Local branch: `git diff origin/main...HEAD`
   - Pre-commit: `git diff HEAD`
2. Bucketuj zmienione pliki do sekcji nizej
3. **Czytaj aktualny kod jako source of truth** przed finalizacja findings:
   - `AGENTS.md` (root + per-package) - org scoping i worker sync
   - Dotknieci modele, db clients, routes, services, migrations
4. Run TYLKO sekcje istotne dla zmienionych plikow
5. Raportuj `<plik>:<linia> -> <problem> -> <correct pattern>`

## Freshness rule (KRYTYCZNE)

Traktuj ten plik jako **review policy + navigation**, NIE jako frozen inventory.

- Jesli aktualne repo PATRON klocy sie z tym skillem, ufaj repo i wymien drift jako problem.
- NIE polegaj na statycznych allowlistach ani konkretnych liniach z tego pliku.
- Recenzuj **kod w PR i aktualnym repo**, nie ten plik.

## Mapa: sciezka w diffie -> sekcje do uruchomienia

| Ścieżka w diffie | Sekcje |
|---|---|
| `app/routes/*.ts`, `apps/api/routes/` | 1, 2, 8 |
| `lib/db/*_client.ts`, `lib/db/schema.ts`, `lib/db/models.ts` | 2, 3 |
| `lib/services/**/*.ts`, `apps/api/services/` | 2, 3, 4 |
| `lib/tasks/*.ts`, `apps/worker/` | 2, 3, 5 |
| `db/migrations/*.sql`, `lib/db/migrations/` | 6 |
| `mcp-servers/**`, `matematicsolutions/mcp-*` | 1, 2, 7, kanon MCP (patrz `matematic-mcp-fastmcp-instructions-pl`) |
| `apps/ui/**`, `apps/dashboard/**` | 9 |
| `lib/constants.ts`, anything `process.env` outside lib/constants | 10 |
| `tests/**`, `__tests__/**` | 11 |
| `lib/schemas/*.ts`, `lib/dto/*.ts` | 12 |
| `lib/audit/**`, `lib/pii/**`, `lib/anonimizacja/**` | 13 (MateMatic-specific) |

---

## 1. Route authentication

Brak globalnego middleware auth w PATRON. Kazda trasa deklaruje swoja auth.

Zaleznosci auth z `lib/auth/depends.ts`:
- `getUser` (user kancelarii w organizacji)
- `getUserWs` (websocket - kancelaria realtime)
- `getSuperuser` (root MateMatic, NIE klient kancelaria)
- `requireRing(N)` (ring-policy ADR-0027) - dla decyzji authorization

Checks:
- Nowy `@router.<verb>(...)` bez auth dependency = silently public. Finding chyba ze plik ustanawia public auth pattern (np. webhook signed, public token).
- `getUser` na impersonation / cross-org / global reporting -> powinno byc `getSuperuser`.
- Route reimplementujaca Bearer/X-API-Key parsing zamiast shared dependency = finding.
- WebSocket bez `Depends(getUserWs)` i bez public-token flow = finding.
- Tightening CORS do fixed origin list potrzebuje strong justification - PATRON polega na cross-origin embedding (widget kancelarii).
- Nowy endpoint zwracajacy dane kancelarii BEZ wpiecia w ring-policy (`requireRing(2)+`) = finding.

Komendy:
```bash
rg -n "Depends\((getUser|getUserWs|getSuperuser|requireRing)" app/routes/ apps/api/
rg -n "@router\.(get|post|put|delete|patch|websocket)" app/routes/
```

---

## 2. Organization scoping (THE CROSS-TENANT RULE - PRIORYTET #1)

NAJWAZNIEJSZA regula w PATRON. Kancelaria A NIGDY nie widzi danych kancelarii B. Kazdy request-reachable read/write resourca org-scoped MUSI filtrowac/walidowac przez `organization_id`.

Polega na: `AGENTS.md` canonical summary + ADR-0027 ring-policy.

Determinacja scope:
- **Direct scope**: model ma `organization_id` (cases, documents, prompts, agents)
- **Indirect scope**: model siega org przez parent FK (e.g. comments -> document -> org)
- Legacy spelling moze istniec w starych migracjach (`org_id`, `tenant_id`), ale **nowy kod uzywa `organization_id`**

Checks:
- Kazdy `*ById(...)` / `getXById(...)` w route handler = suspicious. Jesli request-reachable i unscoped = finding.
- Nowe `list*` / `get*` endpointy filtruja w SQL (`WHERE organization_id = ?`), NIE w TS po `.all()`.
- Jesli request pisze FK do innego org-scoped resourca, route MUSI najpierw fetch target row z `user.selectedOrganizationId` i odrzucic jesli nie nalezy do org.
- Services wolane z routes preserva scoping. Drop `organization_id` w DB client call = trace caller.
- **Background tasks NIE dostaja org context for free.** Musza reload parent row i derive org z tego.
- **Webhooki derive org z signed identifier**, NIE z caller-supplied body fields `organization_id`.
- Nowy kod uzywa kanoniczne `organizationId`, nie `orgId`, `tenantId`, `organisationId`.

Komendy:
```bash
rg -n "ById\(" app/routes/ lib/services/ apps/worker/
rg -n "dbClient\.get\w+\(" app/routes/ lib/services/
rg -n "organizationId|selectedOrganizationId|requireRing" app/routes/ lib/services/ apps/worker/ lib/db/
```

---

## 3. DB query layering

Production SQL nalezy do `lib/db/*_client.ts`. Routes, services, tasks WOLAJA db client methods, NIE pisza Drizzle/SQL bezposrednio.

Checks:
- `db.select`, `db.update`, `db.delete`, `db.insert`, `sql\`\``, `prepare(`, `transaction(` w `app/routes/`, `lib/services/`, `apps/worker/` = finding.
- `lib/services/adminUtils/` to wyjatek - NIE jest template'em dla production.
- Session lifecycle w db client.
- Nowe params db client uzywaja kanoniczne `organizationId`.

Komendy:
```bash
rg -n "(db\.select|db\.update|db\.delete|db\.insert|sql\`)" app/routes/ lib/services/ apps/worker/
```

---

## 4. Worker sync - multi-process state coherence

Production PATRON ma multi-worker. Per-process mutable caches stale unless broadcast.

Checks:
- Nowy module-level / class-level mutable cache pisany przez endpoint potrzebuje WorkerSyncManager broadcast path.
- Local invalidation alone NIE wystarcza jesli inni workerzy moga jeszcze serwowac stale state.
- Jesli PR wprowadza nowy cached object, diff powinien zawierac:
  - broadcast call
  - event type / signal definition
  - handler registration ktory reload fresh state

---

## 5. Background tasks / queue workers

Checks:
- User-triggered enqueue paths waliduja org ownership przed enqueue.
- Tasks ktore akceptuja ID i reload row musza derive org z tego row, NIE assume shared context.
- Tasks idempotentne lub explicit retry-safe.
- Tylko real task entrypoints w `apps/worker/queue.ts::routes`.
- Secret logging rules z sekcji 10 dotycza tu.

---

## 6. Migrations (`db/migrations/*.sql` lub Drizzle migrations)

Checks:
- `up` i `down` istnieja i sa meaningfully reversible chyba ze zmiana naprawde nie da sie cofnac.
- `NOT NULL` column do zaludnionej tabeli potrzebuje safe default lub backfilla przed constraint.
- Tightening nullable -> NOT NULL potrzebuje backfilla PRZED `ALTER COLUMN ... SET NOT NULL`.
- Nowe JSON columny match JSON/JSONB convention tabeli.
- Big backfills w migracji - pytaj. Czesto naleza out-of-band.
- Indexy na duzych tabelach (kancelarii produkcyjnych) potrzebuja concurrent-safe handling (`CREATE INDEX CONCURRENTLY`).
- NIE traktuj historical migration naming jako finding sam w sobie. Recenzuj zmieniana migracje, nie stara prose.

---

## 7. MCP servers (`mcp-servers/**`, `matematicsolutions/mcp-*`)

Reguly z [matematic-mcp-fastmcp-instructions-pl](../matematic-mcp-fastmcp-instructions-pl) - 5 elementow kanonu.

Checks:
- Nowe tools uzywaja `authenticateMcpRequest()` (lub Pythonowy `authenticate_mcp_request()`), NIE reimplementuja API-key validation.
- Nowe tool DB lookups preserva org scoping jak REST routes.
- Tools wolajace external URLs waliduja URL i konsideruja SSRF.
- Nowe MCP tool wymieniony w `instructions` ma istniec w registry (drift test).
- `errorCode` zwracane przez tool sa w docstring tool (drift test).
- ToolAnnotations dla read-only (`readOnlyHint=true`) dla tooli ktore nie mutuja.

---

## 8. Telephony / webhook handlers

Checks:
- Nowy provider webhook flow implementuje `verifyInboundSignature()` lub provider equivalent.
- Minimal pre-verification work moze byc wymagana zeby zidentyfikowac candidate config, ALE route NIE robi unrelated workflow/user/stateful work przed verification.
- Org derivation z provider identifiers walidowanych przez webhook auth flow.
- Webhook NIE ufa raw body `organizationId`.
- Jesli webhook referencuje numer telefonu, walidacja ze numer istnieje dla derived org.

---

## 9. UI (`apps/ui/**`, `apps/dashboard/**`) - generated SDK only

Frontend rozmawia z backendem przez `apps/ui/src/client/` (generated typed SDK).

Checks:
- `fetch('/api/v1/...')` lub `fetch(\`${backendUrl}/api/v1/...\`)` w app code = finding chyba ze aktualny kod udowadnia narrow exception.
- Hardcoded backend URLs = finding.
- Manualna konstrukcja `Authorization` header w zwyklych komponentach = finding (auth injected centrally).
- SDK calls firowane przed auth state ready = finding.
- Local interfaces duplikujace generated types = finding.
- Backend API shape zmienione + UI konsumuje = `apps/ui/src/client/` powinno tez sie zmienic.

---

## 10. Logging, secrets, constants

Checks:
- Nowy kod uzywa shared logger (np. `pino` z PII masking), NIE `console.log`.
- Nowy `process.env.X` poza `lib/constants.ts` = finding.
- NIE logujemy: API keys, bearer tokens, credentials, full webhook bodies, **PII klienta kancelarii (PESEL, NIP, imiona, sygnatury aktualnych spraw)**.
- Common offender shapes:
  - `logger.info(\`config: ${JSON.stringify(config)}\`)`
  - `logger.debug(requestBody)`
  - Logging raw config / user configuration rows

---

## 11. Tests (`tests/**`, `__tests__/**`)

Checks:
- Async waits uzywaja bounded timeout (`pTimeout`, `setTimeout race`), NIE `while (!done)`.
- Tests run against `.env.test`, NIE `.env`.
- Integration tests NIE neutered przez mockowanie zeby test passed - musza hit prawdziwy testowy DB.
- Tests zalezne od mutable shared DB state across test cases = suspicious.

---

## 12. Schemas (`lib/schemas/*.ts`, `lib/dto/*.ts`)

Checks:
- Nowe response schemas NIE expose internal FKs / IDs chyba ze caller naprawde potrzebuje.
- Request schemas akceptujace org-scoped FK values = trigger do inspekcji corresponding route pod katem section 2 ownership validation.

---

## 13. PATRON-specific - PII, audit_log, AI Act art. 12

**Tej sekcji NIE ma w dograh** - to MateMatic-specific dla legal AI.

Checks:
- Operacja decyzyjna (klasyfikacja dokumentu, rekomendacja, generowanie pisma, anonimizacja) MUSI zapisac do `audit_log` (ADR-0033). Brak entry = finding (AI Act art. 12 record-keeping).
- PII detection / anonimizacja inline PRZED storage uzytkowych logow ([matematic-anonimizacja-pl](https://github.com/matematicsolutions/matematic-anonimizacja-pl) jako pre-storage filter). Bypass = finding.
- Cytat z orzeczenia / ustawy w odpowiedzi LLM musi przejsc [citation-grounding-pl](../citation-grounding-pl) (mechaniczna weryfikacja string-match). Jesli kod generuje odpowiedz LLM bez tego layera = finding.
- Pisma procesowe MUSZA przejsc [humanizer-pl](../humanizer-pl) + zewnetrzny senior review (marko-pl-content) min 2 rundy przed docx (wewnetrzny pipeline kancelaryjny MateMatic). Kod generujacy .docx bez tej walidacji = finding.
- Dane z prawdziwych akt klienta (kwoty, sygnatury, inicjaly) w README/aktualnosci/post LI = czerwona linia tajemnicy adwokackiej (art. 6 ust. 1 PrAdw) / radcowskiej (art. 3 ust. 3 RadcPrU). Grep przed push.
- Nowy retention policy: dane klienta kancelarii max 90 dni in-memory / 7 lat archive (RODO + KPK + KC).
- ADR rezerwacja: kazdy duza zmiana decyzyjna potrzebuje ADR proposed przed implementacja (NIE post-hoc).

Komendy:
```bash
rg -n "auditLog|writeAuditEntry|recordDecision" lib/audit/ lib/services/
rg -n "anonymize|piiDetect|let-it-be" lib/pii/ lib/services/
rg -n "PESEL|NIP|REGON" README.md docs/ aktualnosci/   # zero hits expected w public
```

---

## 14. Konstytucja drift - per AGENTS.md

Po `gh repo create` / push nowego komponentu PUBLICZNEGO uruchom 7-stopniowa checkliste catchup (zasada hub kuratorski MateMatic - kod wyprzedza dokumentacje). Ten skill sprawdza w PR diffe:

Checks:
- Nowy komponent zarejestrowany w main? README repo update? AGENTS.md update? CHANGELOG entry?
- Konstytucja PATRON wymaga SEMVER bump przy nowym ADR przyjetym (rezerwacja chronologii przy sesjach rownoleglych).
- Errata: jesli ADR rodzic mial nazwe tabeli/funkcji ktora sie zmienila, sprawdz literal cytat w nowych ADR (propagacja erraty przez literal cytat).

---

## Final pass: shape the report

Findings w 3 buckets:

**Blocker** (MUST fix przed merge):
- Missing org scope na request-reachable lookup (sekcja 2)
- Route bez auth bez deliberate public auth mechanism (sekcja 1)
- Webhook bez signature verification lub significant unrelated work przed verification (sekcja 8)
- Migracja bez safe backfilla lub meaningful downgrade (sekcja 6)
- UI bypassuje generated SDK dla internal API calls (sekcja 9)
- Secrets/PII klienta logowane (sekcja 10, 13)
- Operacja decyzyjna BEZ audit_log entry (sekcja 13)
- Generowanie LLM bez citation-grounding lub pisma docx bez marko-pl-content (sekcja 13)
- Dane z realnych akt w public artefactach (sekcja 13)

**Should-fix** (mocno polecane):
- Cached state mutowany bez worker sync (sekcja 4)
- JSON vs JSONB inconsistency (sekcja 6)
- Response schema leak internal identifiers (sekcja 12)
- Backend API zmienione bez client regen tam gdzie UI konsumuje (sekcja 9)
- Test path moze hang indefinitely (sekcja 11)
- MCP tool reimplementuje auth zamiast `authenticate_mcp_request()` (sekcja 7)
- Drift dokumentacji vs kod (sekcja 14)

**Nit** (drobne):
- Naming inconsistencies
- Minor convention drift
- Low-risk schema / report-shape cleanup

Cytuj `plik:linia` dla kazdego finding. Pomin to co formatter/linter/IDE i tak zlapie chyba ze laczy sie z jednym z repo-specific risks powyzej.

## Anti-pattern w sposobie review

- NIE pisanie generic FastAPI/Next.js comments - tylko repo-specific
- NIE polegaj na statycznych allowlistach z tego pliku - czytaj aktualny repo
- NIE marudz na styl bez `repo-specific risk connection`
- NIE chwalenie w findings - tylko problemy
- NIE post-merge findings (znajdzeli sie zalozenia ze mergowali bo ja przepuscilem) - read przed merge

## Walidowane na

- [dograh-hq/dograh](https://github.com/dograh-hq/dograh) v1.31.0 review-pr.md (BSD-2, 286 linii) - source pattern
- PATRON ADR-0033 (audit_log) + ADR-0028 (mcp-security-gateway) - 401/406 testow, 3 rundy senior review, errata z parent ADR (sesja 2026-05-24)

## Linki

- [matematic-mcp-fastmcp-instructions-pl](../matematic-mcp-fastmcp-instructions-pl) - kanon MCP (sekcja 7)
- [citation-grounding-pl](../citation-grounding-pl) - anti-halucynacja cytatu (sekcja 13)
- [humanizer-pl](../humanizer-pl) - higiena tekstu PL (sekcja 13, pre-docx)
- [legal-ai-audit-bundle](../legal-ai-audit-bundle) - audit AI Act art. 12 (sekcja 13)
- [matematic-anonimizacja-pl](https://github.com/matematicsolutions/matematic-anonimizacja-pl) - PII anonimizacja (sekcja 13)
- [dograh-hq/dograh](https://github.com/dograh-hq/dograh) - source pattern (BSD-2)
