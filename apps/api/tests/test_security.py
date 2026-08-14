"""Unit tests for secret hashing, session tokens and cookie hardening."""

from app.core.config import Settings
from app.core.security import (
    FAMILY_CODE_ALPHABET,
    FAMILY_CODE_LENGTH,
    generate_family_code,
    generate_session_token,
    hash_password,
    hash_pin,
    hash_session_token,
    needs_rehash,
    normalise_family_code,
    verify_password,
    verify_pin,
)

PASSWORD = "correct-horse-battery"
PIN = "428173"


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


def test_pins_are_hashed_with_argon2id_like_passwords() -> None:
    """Six digits get the full per-guess cost, since they have little else."""
    assert hash_pin(PIN).startswith("$argon2id$")


def test_verify_pin_accepts_the_matching_pin() -> None:
    assert verify_pin(PIN, hash_pin(PIN)) is True


def test_verify_pin_rejects_a_wrong_pin() -> None:
    assert verify_pin("999182", hash_pin(PIN)) is False


def test_a_stored_pin_hash_never_contains_the_pin() -> None:
    assert PIN not in hash_pin(PIN)


def test_family_codes_avoid_characters_a_child_would_misread() -> None:
    """Zero and O, one and I and L are indistinguishable on a handwritten note."""
    assert set(FAMILY_CODE_ALPHABET).isdisjoint({"0", "O", "1", "I", "L"})

    codes = {generate_family_code() for _ in range(200)}

    assert all(len(code) == FAMILY_CODE_LENGTH for code in codes)
    assert all(set(code) <= set(FAMILY_CODE_ALPHABET) for code in codes)


def test_family_codes_are_unpredictable() -> None:
    """Collisions in two hundred draws would mean far too small a space."""
    assert len({generate_family_code() for _ in range(200)}) == 200


def test_a_family_code_is_read_as_typed_by_a_child() -> None:
    assert normalise_family_code("  7kq3f2 ") == "7KQ3F2"


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
