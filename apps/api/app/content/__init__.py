"""The isolated runtime: laying contents out, and letting one be fetched.

The runtime lives on its own origin, per ADR-012's fifth condition, so the
session cookie cannot travel with a content request. A short-lived ticket takes
its place. See `docs/backend/runtime-contenu.md`.
"""

from app.content.deploy import (
    DeploymentRefused,
    DeploymentReport,
    content_store,
    deploy_libraries,
    deploy_package,
    deployed_contents,
    is_deployed,
)
from app.content.tokens import (
    CONTENT_TICKET_TTL_SECONDS,
    ContentTicket,
    mint_ticket,
    read_ticket,
    revoke_ticket,
)

__all__ = [
    "CONTENT_TICKET_TTL_SECONDS",
    "ContentTicket",
    "DeploymentRefused",
    "DeploymentReport",
    "content_store",
    "deploy_libraries",
    "deploy_package",
    "deployed_contents",
    "is_deployed",
    "mint_ticket",
    "read_ticket",
    "revoke_ticket",
]
