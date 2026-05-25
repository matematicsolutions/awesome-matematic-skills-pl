"""Kanonowy MCP server MateMatic - template.

Cherry-pick z dograh v1.31.0 (api/mcp_server/server.py).
Zastapic 'matematic-saos' nazwa wlasciwego serwera.
Zastapic importy tools/ wlasciwymi nazwami.
"""

from fastmcp import FastMCP
from mcp.types import ToolAnnotations

from .instructions import MATEMATIC_MCP_INSTRUCTIONS
from .tools.read_only_tool_a import read_only_tool_a
from .tools.read_only_tool_b import read_only_tool_b
from .tools.mutating_tool import mutating_tool

mcp = FastMCP("matematic-saos", instructions=MATEMATIC_MCP_INSTRUCTIONS)

# Mutating / destructive tools - wymagaja approval klienta
for _tool in (mutating_tool,):
    mcp.tool(_tool)

# Read-only tools - klient moze auto-approve
_READ_ONLY = ToolAnnotations(
    readOnlyHint=True,
    idempotentHint=True,
    destructiveHint=False,
    openWorldHint=False,
)

for _tool in (read_only_tool_a, read_only_tool_b):
    mcp.tool(_tool, annotations=_READ_ONLY)
