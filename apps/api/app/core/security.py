"""Password hashing and opaque session token primitives."""

from __future__ import annotations

import hashlib
import secrets
from typing import Final

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

SESSION_TOKEN_BYTES: Final = 32

_password_hasher = PasswordHasher()

# Verifying a wrong password against this hash costs the same as verifying a real
# one, which keeps a login attempt on an unknown email indistinguishable in time
# from an attempt on an existing account.
_DUMMY_PASSWORD_HASH: Final = _password_hasher.hash("studentconnect-dummy-password")


def hash_password(password: str) -> str:
    """Return an Argon2id hash of the given password."""
    return _password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Return whether the password matches the stored hash."""
    try:
        return _password_hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def spend_dummy_verification(password: str) -> None:
    """Burn a verification's worth of time without revealing anything.

    Called when no account matches the submitted email, so that response times do
    not disclose which addresses are registered.
    """
    verify_password(password, _DUMMY_PASSWORD_HASH)


def needs_rehash(password_hash: str) -> bool:
    """Return whether a stored hash predates the current Argon2 parameters."""
    try:
        return _password_hasher.check_needs_rehash(password_hash)
    except InvalidHashError:
        return False


def generate_session_token() -> str:
    """Return a fresh opaque session token."""
    return secrets.token_urlsafe(SESSION_TOKEN_BYTES)


def hash_session_token(token: str) -> str:
    """Return the digest under which a session token is stored.

    Sessions are keyed by this digest rather than by the token itself, so a
    leaked Redis dump cannot be replayed as a cookie. A plain SHA-256 is enough
    here because the token is 32 random bytes, not a low-entropy secret.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
