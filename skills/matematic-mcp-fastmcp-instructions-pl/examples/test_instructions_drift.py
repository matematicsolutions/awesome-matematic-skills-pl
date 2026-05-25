"""Drift test - instrukcje MCP musza byc spojne z registered tools.

Cherry-pick wzorca z dograh v1.31.0 (api/mcp_server/test_mcp_instructions_drift.py).

Fail jesli:
1. Instructions wymienia tool nie registered w `mcp`
2. Tool ma error_code ktorego nie ma w docstring

Uruchom w CI przed merge: `pytest tests/test_instructions_drift.py`
"""

import re
from pathlib import Path

import pytest

from app.mcp_server.server import mcp
from app.mcp_server.instructions import MATEMATIC_MCP_INSTRUCTIONS


def _registered_tool_names() -> set[str]:
    """Imiona wszystkich toolow zarejestrowanych w FastMCP."""
    # FastMCP API moze sie zmienic - zaadaptuj jesli refactor
    return {tool.name for tool in mcp.list_tools()}


def _referenced_tool_names_in_instructions() -> set[str]:
    """Wyciagnij nazwy toolow z instructions (backtick code spans)."""
    # Match `tool_name` w backticks - tool names sa snake_case
    matches = re.findall(r"`([a-z_]+)`", MATEMATIC_MCP_INSTRUCTIONS)
    # Filter tylko te ktore wygladaja jak tool names (heuristic - co najmniej
    # jedno _ albo dluzsze niz 6 znakow). Zaadaptuj jesli false positives.
    return {m for m in matches if "_" in m or len(m) > 6}


def test_instructions_only_reference_registered_tools():
    """Kazdy tool name w instructions musi byc registered."""
    registered = _registered_tool_names()
    referenced = _referenced_tool_names_in_instructions()
    orphan = referenced - registered
    assert not orphan, (
        f"Instructions referencuja tools ktore nie sa registered: {orphan}. "
        f"Usun z instructions albo zarejestruj w server.py. "
        f"Registered: {sorted(registered)}"
    )


def test_tool_error_codes_documented_in_docstring():
    """Kazdy error_code zwracany przez tool musi byc w jego docstring."""
    for tool in mcp.list_tools():
        if not tool.description:
            continue

        # Wez sciezke do pliku tooli z tool.fn lub innej meta
        # Zaadaptuj do twojej struktury - tutaj heuristic
        source = Path(__file__).parent.parent / "tools" / f"{tool.name}.py"
        if not source.exists():
            continue

        src = source.read_text(encoding="utf-8")

        # Znajdz wszystkie 'error_code=' wartosci w kodzie
        codes_in_src = set(re.findall(r'error_code=["\']([a-z_]+)["\']', src))
        # Znajdz wszystkie wymienione w docstring (sekcja Errors / error_code)
        codes_in_doc = set(re.findall(r"`([a-z_]+)`", tool.description))

        undocumented = codes_in_src - codes_in_doc
        assert not undocumented, (
            f"Tool {tool.name} ma error_codes ktore nie sa w docstring: "
            f"{undocumented}. Dodaj do docstring sekcji 'Errors'."
        )
