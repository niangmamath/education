"""Password hashing and opaque session token primitives."""

from __future__ import annotations

import hashlib
import secrets
from typing import Final

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

SESSION_TOKEN_BYTES: Final = 32

# The family code is read aloud or copied from a sheet of paper by a child of six
# to eleven, so the alphabet drops every character that is confused when written
# by hand: zero and O, one and I and L. The thirty-one symbols left still give
# more than eight hundred million codes over six positions.
FAMILY_CODE_LENGTH: Final = 6
FAMILY_CODE_ALPHABET: Final = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"

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


def hash_pin(pin: str) -> str:
    """Return an Argon2id hash of a child PIN.

    A PIN gets the same parameters as a password even though it holds far less
    entropy: six digits are only a million combinations, so the per-guess cost
    of Argon2 is one of the two things standing between the profile and an
    attacker. The other is the attempt lockout in `app.core.lockout`.
    """
    return hash_password(pin)


def verify_pin(pin: str, pin_hash: str) -> bool:
    """Return whether the PIN matches the stored hash."""
    return verify_password(pin, pin_hash)


def needs_rehash(password_hash: str) -> bool:
    """Return whether a stored hash predates the current Argon2 parameters."""
    try:
        return _password_hasher.check_needs_rehash(password_hash)
    except InvalidHashError:
        return False


def generate_family_code() -> str:
    """Return a fresh family code identifying a parent to their children.

    The code is drawn at random rather than derived from the parent, so it can be
    handed to a child, and later replaced, without saying anything about the
    account behind it.
    """
    return "".join(
        secrets.choice(FAMILY_CODE_ALPHABET) for _ in range(FAMILY_CODE_LENGTH)
    )


def normalise_family_code(value: str) -> str:
    """Return the canonical form of a family code as typed by a child."""
    return value.strip().upper()


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
