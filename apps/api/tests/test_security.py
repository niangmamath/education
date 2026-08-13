"""Unit tests for password hashing, session tokens and cookie hardening."""

from app.core.config import Settings
from app.core.security import (
    generate_session_token,
    hash_password,
    hash_session_token,
    needs_rehash,
    verify_password,
)

PASSWORD = "correct-horse-battery"


def test_passwords_are_hashed_with_argon2id() -> None:
    assert hash_password(PASSWORD).startswith("$argon2id$")


def test_the_same_password_never_produces_the_same_hash() -> None:
    """A per-hash salt is what stops one leak from cracking every account."""
    assert hash_password(PASSWORD) != hash_password(PASSWORD)


def test_verify_password_accepts_the_matching_password() -> None:
    assert verify_password(PASSWORD, hash_password(PASSWORD)) is True


def test_verify_password_rejects_a_wrong_password() -> None:
    assert verify_password("autre-mot-de-passe", hash_password(PASSWORD)) is False


def test_verify_password_rejects_a_malformed_hash() -> None:
    """A corrupted stored hash must read as a failed login, not as a crash."""
    assert verify_password(PASSWORD, "pas-un-hash-argon2") is False


def test_needs_rehash_is_false_for_a_fresh_hash() -> None:
    assert needs_rehash(hash_password(PASSWORD)) is False


def test_needs_rehash_tolerates_a_malformed_hash() -> None:
    assert needs_rehash("pas-un-hash-argon2") is False


def test_session_tokens_are_unpredictable() -> None:
    tokens = {generate_session_token() for _ in range(100)}
    assert len(tokens) == 100
    assert all(len(token) >= 32 for token in tokens)


def test_session_token_digest_is_stable_and_hides_the_token() -> None:
    token = generate_session_token()
    digest = hash_session_token(token)

    assert digest == hash_session_token(token)
    assert len(digest) == 64
    assert token not in digest


def test_session_cookie_is_not_secure_in_local_development() -> None:
    assert Settings(ENVIRONMENT="development").session_cookie_secure is False


def test_session_cookie_is_secure_outside_development() -> None:
    """An unset flag must fail closed rather than ship a readable cookie."""
    assert Settings(ENVIRONMENT="production").session_cookie_secure is True
    assert Settings(ENVIRONMENT="staging").session_cookie_secure is True


def test_session_cookie_security_can_be_overridden_explicitly() -> None:
    settings = Settings(ENVIRONMENT="production", SESSION_COOKIE_SECURE=False)
    assert settings.session_cookie_secure is False
