"""Dwukanalowy auth MCP MateMatic + OTel per-tenant routing.

Cherry-pick z dograh v1.31.0 (api/mcp_server/auth.py).

Akceptuje OBA naglowki:
- X-API-Key: <key>
- Authorization: Bearer <key>

FastMCP domyslnie stripuje Authorization - explicit include={"authorization"}
jest KRYTYCZNY.

OTel atrybut `mcp.org_id` (nie `<server>.org_id`!) zostawia traffic dewa
na default project, nie miesza z multi-tenant pipeline spans.
"""

from fastapi import HTTPException
from fastmcp.server.dependencies import get_http_headers
from opentelemetry import trace

# Zastapic wlasciwym importem User modelu i auth handlera
from app.db.models import UserModel
from app.services.auth.depends import _handle_api_key_auth


async def authenticate_mcp_request() -> UserModel:
    """Resolve authenticated MateMatic user for MCP tool invocation.

    Accepts either `X-API-Key: <key>` or `Authorization: Bearer <key>`,
    reusing the API-key flow from `app.services.auth.depends`.

    Tags currently-active OTel span with resolved organization and user
    identifiers. Use `mcp.org_id` (NOT `<server>.org_id`) so MCP traffic
    lands on default (developer-facing) Langfuse project, not in the
    per-org pipeline routing.
    """
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

    user = await _handle_api_key_auth(api_key)

    span = trace.get_current_span()
    if span.is_recording():
        org_id = user.selected_organization_id
        span.set_attribute("mcp.org_id", str(org_id))
        span.set_attribute("mcp.user_id", str(user.id))
        span.set_attribute("langfuse.user.id", str(user.id))

    return user
