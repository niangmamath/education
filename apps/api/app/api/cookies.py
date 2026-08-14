"""The session cookie, written the same way for every kind of caller.

Parent and child sessions differ only by how long they last; every other
hardening flag is shared, so it is defined once here rather than at each login.
"""

from __future__ import annotations

from fastapi import Response

from app.core.config import settings


def set_session_cookie(response: Response, token: str, max_age: int) -> None:
    """Attach the session token to the response as a hardened cookie."""
    response.set_cookie(
        key=settings.SESSION_COOKIE_NAME,
        value=token,
        max_age=max_age,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite=settings.SESSION_COOKIE_SAMESITE,
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    """Remove the session cookie from the caller."""
    response.delete_cookie(settings.SESSION_COOKIE_NAME, path="/")
