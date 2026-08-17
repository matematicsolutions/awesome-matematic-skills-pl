---
name: matematic-mcp-fastmcp-instructions-pl
description: Buduj nowy MCP server MateMatic (lub retrofit istniejacego) z 7 elementami (5 zwalidowanych na dograh v1.31.0) - FastMCP(instructions=) z procedural orchestration, drift test, dwukanalowy auth X-API-Key LUB Bearer, OTel atrybut org_id dla per-tenant routing, ToolAnnotations dla read-only, stabilne kody bledow + trojstan ok/degraded/failed, allowlista atrybutow telemetrii na granicy emisji. Uzywaj gdy zaczynasz nowy MCP server (saos/eu-compliance/anonimizacja/pomoc-prawna/kio/isap/inny), retrofit istniejacego do tego patternu, dodajesz nowy tool do MCP, debugujesz dlaczego LLM nie wywoluje Twoich tooli w odpowiedniej kolejnosci, lub gdy klient MCP (Claude Code/Cursor) nie autoryzuje. Trigger - "nowy MCP", "buduj MCP server", "FastMCP", "instructions MCP", "dryft testu MCP", "Claude Code MCP", "auth MCP", "OTel MCP", "FastMCP setup", "retrofit MCP", "tools MCP audit", "tools MCP nie sa wywolywane".
license: Apache-2.0
attribution:
  - source: dograh-hq/dograh
    url: https://github.com/dograh-hq/dograh
    license: BSD-2-Clause
    relationship: pattern-only
    note: >
      Elementy 1-5: wzorzec zrodlowy dla FastMCP(instructions=) i orkiestracji
      proceduralnej, walidowany na v1.31.0. Tresc, testy driftu i kanon MateMatic
      napisane od zera. Licencja zweryfikowana przez GitHub API 2026-08-17.
  - source: firecrawl/anydoc
    url: https://github.com/firecrawl/anydoc
    license: MIT
    relationship: pattern-only
    note: >
      Element 6: stabilny `code()` oddzielony od komunikatu dla czlowieka plus test,
      ktorego jedynym zadaniem jest przypiecie tych stringow, bo konsumenci na nich
      branchuja. Anty-wzorzec z tego samego audytu (2026-08-08) uzasadnia sprzezenie
      z trojstanem: anydoc liczy poprawny mianownik pominietych stron i wysyla go do
      fasady `log`, ktorej nigdzie nie rejestruje. Kod napisany od zera.
  - source: sandbox-quantum/flintai-cli
    url: https://github.com/sandbox-quantum/flintai-cli
    license: Apache-2.0 WITH Commons-Clause
    relationship: pattern-only
    note: >
      Element 7: allowlista atrybutow egzekwowana w jednym miejscu na granicy emisji,
      swiadome wykluczenie `exception.message` (bo `str(blad)` niesie sciezki, prompty
      i output providera) oraz providery OTel trzymane prywatnie, zeby cudza
      instrumentacja nie wychodzila naszym eksporterem. Kod i testy wlasne. Commons
      Clause zabrania sprzedazy uslug opartych na tym oprogramowaniu, wiec kopiowanie
      kodu odpada.
allowed-tools: [Read, Write, Edit]
data-residency: local
requires-human-approval: false
pii-egress: none
---

# matematic-mcp-fastmcp-instructions-pl

Wzorzec kanoniczny dla MCP serverow MateMatic. Walidowany empirycznie na [dograh-hq/dograh](https://github.com/dograh-hq/dograh) v1.31.0 (production system, 3-4 dni release cycle, 2.6k gwiazdek, drift testy w CI, BSD-2).

## Kiedy uzywac

- Nowy MCP server MateMatic od pierwszego commita
- Retrofit istniejacych (saos-orzecznictwo, mcp-eu-compliance, matematic-anonimizacja-pl, mcp-pomoc-prawna-pl, sejm-eli-mcp, mcp-uodo, mcp-kio) - do konca Q3 2026
- Audit istniejacego MCP server (czy ma 7 elementow)
- Debug: LLM nie wywoluje tooli w odpowiedniej kolejnosci, klient MCP nie autoryzuje, error_codes ginace dla LLM

## 7 elementow kanonu

### 1. `FastMCP(instructions=...)` z procedural orchestration

Instrukcje wstrzykiwane do system promptu kazdego klienta MCP. LLM widzi je PRZED pierwszym tool call.

**Tresc:**
- Call order (ktora kolejnosc wywolywac tools)
- Error handling (jak iteorwac po failed tool call)
- Hard constraints (czego NIE robic)
- Field conventions (kanoniczne nazwy, format ID)
- Style (preferencje przy wyborze toolow gdy wiele rozwiazan)

**Anti-content:**
- NIE re-enumerowac tool signatures (drift - signatury sa w `tools/list`)
- NIE re-enumerowac error_codes (drift - error_codes w tool docstring)
- NIE per-field guidance (to lezy w `PropertySpec.llm_hint`)

Wzor (Python):
```python
from fastmcp import FastMCP
from .instructions import MY_MCP_INSTRUCTIONS
from .tools.foo import foo_tool
from .tools.bar import bar_tool

mcp = FastMCP("matematic-saos", instructions=MY_MCP_INSTRUCTIONS)

for _tool in (foo_tool, bar_tool):
    mcp.tool(_tool)
```

### 2. Drift test (`tests/test_mcp_instructions_drift.py`)

Fail jesli:
- Instructions wymienia tool nie registered
- Tool ma error_code ktorego nie ma w docstring

Wzor w `examples/test_instructions_drift.py`.

### 3. Auth dwukanalowy X-API-Key LUB Bearer

FastMCP domyslnie stripuje `Authorization` header. **MUSISZ** explicit `get_http_headers(include={"authorization"})`.

```python
from fastmcp.server.dependencies import get_http_headers

async def authenticate_mcp_request() -> User:
    headers = get_http_headers(include={"authorization"})
    api_key = headers.get("x-api-key")
    if not api_key:
        auth = headers.get("authorization", "")
        if auth.lower().startswith("bearer "):
            api_key = auth.split(" ", 1)[1].strip()
    if not api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key - send X-API-Key or Authorization: Bearer <key>",
        )
    return await _handle_api_key_auth(api_key)
```

### 4. OTel atrybut `<server>.org_id` per-tenant routing

Per-org routing do Langfuse/observability:

```python
from opentelemetry import trace

span = trace.get_current_span()
if span.is_recording():
    org_id = user.selected_organization_id
    span.set_attribute("mcp.org_id", str(org_id))
    span.set_attribute("mcp.user_id", str(user.id))
    span.set_attribute("langfuse.user.id", str(user.id))
```

**WAZNE rozroznienie z dograh-auth:**
- `<server>.org_id` (np. `dograh.org_id`) triggeruje per-org Langfuse project routing dla **pipeline spans**
- Dla **MCP traffic** uzyj `mcp.org_id` zeby zostalo na default (developer-facing) project
- Bez tego rozroznienia traffic deweloperski miesza sie z produkcyjnym multi-tenant

### 5. ToolAnnotations dla read-only tools

Pozwala klientowi MCP automatycznie zatwierdzac wywolania bez monitu (`readOnlyHint=True` + `destructiveHint=False`).

```python
from mcp.types import ToolAnnotations

_READ_ONLY = ToolAnnotations(
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False,
)

for _tool in (list_docs, search_docs, read_doc):
    mcp.tool(_tool, annotations=_READ_ONLY)
```

### 6. Stabilny `code` bledu + test, ktory go przypina

Wzorzec zmierzony na `firecrawl/anydoc` (MIT, audyt 2026-08-08). Ich `ConvertError`
ma metode `code()` zwracajaca **stabilny string maszynowy** (`unsupported`,
`encrypted`, `resourceLimit`, ...), oddzielony od komunikatu dla czlowieka - plus
test, ktorego jedynym zadaniem jest pilnowanie, ze te stringi sie nie zmienily,
z komentarzem "bindingi publikuja to doslownie, wiec zmiana lamie kazdego konsumenta".

Nasz odpowiednik: **agent branchuje na `code`, czlowiek czyta `message`**. Bez tego
LLM parsuje polski tekst bledu regexem i lamie sie przy pierwszej korekcie stylu.

```python
class ToolError(Exception):
    """Blad narzedzia MCP. `code` = kontrakt maszynowy, `message` = dla czlowieka."""
    CODES = ("not_found", "invalid_input", "upstream_unavailable",
             "rate_limited", "forbidden", "partial_result")

    def __init__(self, code: str, message: str, **detail):
        assert code in self.CODES, f"nieznany code: {code}"
        self.code, self.message, self.detail = code, message, detail

    def as_result(self) -> dict:
        return {"status": "failed", "code": self.code,
                "message": self.message, "detail": self.detail}
```

```python
# tests/test_error_codes_stable.py
def test_kody_bledow_sa_stabilne():
    """Konsumenci (agent, klient MCP) branchuja na tych stringach.
    Zmiana ktoregokolwiek = breaking change, wiec ma boles TUTAJ, nie u klienta."""
    assert set(ToolError.CODES) == {
        "not_found", "invalid_input", "upstream_unavailable",
        "rate_limited", "forbidden", "partial_result",
    }
```

**Sprzezenie z `partial_result` (kardynalna regula cichej niekompletnosci):** tool,
ktory zwrocil CZESC danych, NIE MOZE zwrocic `status: ok`. Trojstan
`ok | degraded | failed` plus **pelny mianownik** w tej samej odpowiedzi:

```python
return {"status": "degraded", "code": "partial_result",
        "coverage": {"unit": "pages", "total": 14, "usable": 9},
        "message": "9 z 14 stron bez warstwy tekstowej", "data": blocks}
```

Anty-wzorzec, ktory to unaocznil: anydoc liczy poprawny mianownik
(`"{} of {} pages need OCR"`), po czym wysyla go do fasady `log`, ktorej
**nigdzie nie rejestruje** - konsument dostaje `Ok` i niepelny dokument.
Zdarzenie niepelnosci ma isc TA SAMA droga co wynik, nie kanalem obok.

### 7. Allowlista atrybutow na granicy emisji telemetrii

Element 4 kaze wpisywac do spanu `org_id` i `user_id`. Element 7 pilnuje, zeby to
byly JEDYNE rzeczy, ktore wyjda z procesu. Bez tego telemetria konektora
kancelaryjnego jest kanalem wycieku danych objetych tajemnica zawodowa, a wyciek
nastapi przez atrybut, ktorego nikt swiadomie nie dodawal.

Trzy reguly.

**Jedno gardlo.** Kazdy zestaw atrybutow przechodzi przez jedna funkcje przed
eksportem. Klucz spoza listy jest odrzucany niezaleznie od tego, gdzie na spanie
zostal ustawiony.

```python
_DOZWOLONE_ATRYBUTY = frozenset({
    "mcp.org_id", "mcp.user_id", "mcp.tool", "mcp.status",
    "mcp.duration_ms", "mcp.code", "service.name", "service.version",
})

def _przesiej(atrybuty: dict) -> dict:
    """Jedyne miejsce, przez ktore atrybuty wychodza z procesu."""
    return {k: v for k, v in atrybuty.items() if k in _DOZWOLONE_ATRYBUTY}
```

**`exception.message` nigdy nie wychodzi.** `str(blad)` rutynowo niesie sciezki
dyskowe, fragmenty promptu, sygnatury spraw i output providera. Eksportuj
`exception.type`, czyli sama nazwe klasy, i nasz stabilny `code` z elementu 6.
Trescia bledu zajmuje sie log lokalny, ktory zostaje na maszynie.

**Providery prywatne, nie globalne.** Nie rejestruj swojego providera przez
`set_tracer_provider` ani `set_logger_provider`. Globalna rejestracja sprawia, ze
cudza instrumentacja w tym samym procesie (SDK modelu, framework agenta) zaczyna
wychodzic Twoim eksporterem, razem z tym, co akurat wkłada do swoich spanow.

```python
# tests/test_telemetry_allowlist.py
def test_atrybut_spoza_listy_nie_wychodzi():
    assert _przesiej({"mcp.org_id": "7", "prompt": "tresc pisma"}) == {"mcp.org_id": "7"}

def test_exception_message_nie_wychodzi():
    assert "exception.message" not in _przesiej({"exception.message": "C:/akta/…"})
```

Regula bez bramki nie trzyma, wiec allowlista bez tego testu jest komentarzem.
Deklaracja w README nie jest kontrola - kontrola jest funkcja, przez ktora
wszystko przechodzi, i test, ktory to przypina.

Wzorzec zaadaptowany z `flintai/cli/telemetry.py` w `sandbox-quantum/flintai-cli`
(Apache-2.0 z Commons Clause, wylacznie idea, zero kodu).

## Templatey gotowe do skopiowania

W `examples/`:
- `server.py` - kanon setup FastMCP + registration
- `instructions.py` - szkielet z 4 sekcjami (Call order / Allowed shape / Iterating on errors / Style)
- `auth.py` - dwukanalowy + OTel
- `test_instructions_drift.py` - drift test do CI

## Smoke test po wdrozeniu

```bash
claude mcp add --transport http <name> https://<your-mcp>/api/v1/mcp/ \
  --header "X-API-Key: <key>"
claude mcp list
# Powinno wyswietlic <name> + status connected + tools count
```

W Claude Code: "List my <resources> via <name>" - czy LLM wywoluje tool wlasciwy?

## Anti-patterns do unikania

| Anti-pattern | Konsekwencja |
|---|---|
| Restating tool signatures w instructions | Drift, signatury rosna z kodu |
| Re-enumerating error_codes w instructions | Drift, error_codes rosna z docstring |
| Hardcoded API key validation w kazdym tool | Reuse `authenticate_mcp_request()` |
| Stdlib `logging.info(request_body)` | Loguruj sekrety. Uzyj Loguru z masking PII |
| Brak ToolAnnotations na read-only | Klient pyta o approval przy kazdym wywolaniu |
| Single-channel auth (tylko X-API-Key lub tylko Bearer) | Niektorzy klienci wysylaja drugi - 401 |
| Brak OTel atrybutow org_id | Brak per-tenant observability w multi-tenant |

## Walidowane na

- **dograh v1.31.0** ([dograh-hq/dograh](https://github.com/dograh-hq/dograh), BSD-2) - source pattern, production 3-4 dni release cycle
- Kluczowe pliki referencyjne (kanon): `api/mcp_server/server.py`, `api/mcp_server/instructions.py`, `api/mcp_server/auth.py` w upstream repo

## Roadmapa retrofit MCP MateMatic

**LIVE 2026-05-25** (6 z 6 TypeScript MCP serverow MateMatic):

| MCP | Wersja | Release |
|---|---|---|
| [mcp-eu-compliance](https://github.com/matematicsolutions/mcp-eu-compliance) | v0.2.0 | pilot kanonu |
| [mcp-saos](https://github.com/matematicsolutions/mcp-saos) | v1.1.0 | orzecznictwo SAOS |
| [mcp-eu-sparql](https://github.com/matematicsolutions/mcp-eu-sparql) | v1.1.0 | EUR-Lex + CJEU |
| [mcp-isap](https://github.com/matematicsolutions/mcp-isap) | v1.1.0 | Sejm ELI (DU + MP) |
| [mcp-nsa](https://github.com/matematicsolutions/mcp-nsa) | v1.1.0 | CBOSA (sady admin) |
| [mcp-krs](https://github.com/matematicsolutions/mcp-krs) | v1.1.0 | KRS MS |

**Pozostalo** (Python stack + nowsze MCP): sejm-eli-mcp, kio-orzeczenia-mcp, ewentualne uodo-mcp / pomoc-prawna-mcp.

## Linki

- [dograh-hq/dograh](https://github.com/dograh-hq/dograh) - source pattern (BSD-2)
- [mcp-eu-compliance v0.2.0](https://github.com/matematicsolutions/mcp-eu-compliance/releases/tag/v0.2.0) - pierwszy MCP MateMatic z pelnym kanonem (TS adaptacja Python wzorca)
- [matematic-patron-pr-review-pl](../matematic-patron-pr-review-pl) - komplementarny skill (review PR repo PATRON)
