"""Request and response schemas for parent and child authentication."""

from __future__ import annotations

import re
import uuid
from datetime import UTC, date, datetime
from typing import Final

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator

from app.core.security import FAMILY_CODE_LENGTH, normalise_family_code

# OWASP ASVS asks for twelve characters on an account that guards a child's
# activity history. Argon2 has no input length ceiling of its own, so the upper
# bound only exists to keep a single request from hashing an unbounded payload.
PASSWORD_MIN_LENGTH: Final = 12
PASSWORD_MAX_LENGTH: Final = 128

# ADR-005 fixes the PIN at six digits. A child of six to eleven types it on a
# keypad, so nothing longer or mixed-case is realistic.
PIN_LENGTH: Final = 6

# A pseudonym is unique inside its family, never across the whole platform, so
# the same first name may be taken in as many families as there are children.
# The database already refuses a pseudonym below three characters; the pattern
# adds the part SQL cannot express. Lowercase letters, digits, hyphen and
# underscore only, never at the edges, so two pseudonyms cannot differ by
# invisible punctuation alone.
PSEUDONYM_MIN_LENGTH: Final = 3
PSEUDONYM_MAX_LENGTH: Final = 50
PSEUDONYM_PATTERN: Final = re.compile(r"^[a-z0-9](?:[a-z0-9_-]*[a-z0-9])?$")


class ParentRegisterRequest(BaseModel):
    """Payload creating a parent account."""

    email: EmailStr
    password: SecretStr = Field(
        min_length=PASSWORD_MIN_LENGTH, max_length=PASSWORD_MAX_LENGTH
    )
    display_name: str = Field(min_length=1, max_length=100)

    @field_validator("email")
    @classmethod
    def normalise_email(cls, value: str) -> str:
        """Store one canonical form so an address cannot be registered twice."""
        return value.strip().lower()

    @field_validator("display_name")
    @classmethod
    def strip_display_name(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("display_name must not be blank")
        return stripped


class ParentLoginRequest(BaseModel):
    """Credentials submitted by a parent."""

    email: EmailStr
    password: SecretStr

    @field_validator("email")
    @classmethod
    def normalise_email(cls, value: str) -> str:
        return value.strip().lower()


def _is_trivial_pin(pin: str) -> bool:
    """Return whether the PIN is one an attacker would try in its first guesses.

    A repeated digit or a straight run covers the handful of codes that show up
    at the top of every leaked PIN ranking, and they are exactly the ones a
    parent picks when in a hurry.
    """
    digits = [int(digit) for digit in pin]
    if len(set(digits)) == 1:
        return True
    # `strict` stays off on purpose: the pairs walk consecutive digits, so the
    # second sequence is shorter by one by construction.
    steps = {second - first for first, second in zip(digits, digits[1:], strict=False)}
    return steps in ({1}, {-1})


def _normalise_pseudonym(value: str) -> str:
    """Return the canonical form under which a pseudonym is stored and matched."""
    return value.strip().lower()


def validate_new_pin(value: SecretStr) -> SecretStr:
    """Refuse a PIN that is malformed or among the first an attacker would try.

    Shared by every route that sets a PIN, so a PIN chosen at creation, reset by
    a parent or changed by a child all pass exactly the same bar.
    """
    pin = value.get_secret_value()
    if len(pin) != PIN_LENGTH or not pin.isdecimal() or not pin.isascii():
        raise ValueError(f"pin must be exactly {PIN_LENGTH} digits")
    if _is_trivial_pin(pin):
        raise ValueError("pin must not be a repeated digit or a straight run")
    return value


class ParentPublic(BaseModel):
    """Parent fields the API is allowed to return.

    ``password_hash`` is absent by construction rather than by filtering, so no
    later edit can leak it through this schema.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    family_code: str
    display_name: str
    is_verified: bool
    created_at: datetime


class ChildCreateRequest(BaseModel):
    """Payload a parent submits to open a child profile.

    The child has neither email nor phone, by ADR-005: a pseudonym and a PIN are
    the only identifiers, and nothing here can be used to contact the child.
    """

    pseudonym: str = Field(
        min_length=PSEUDONYM_MIN_LENGTH, max_length=PSEUDONYM_MAX_LENGTH
    )
    pin: SecretStr
    display_name: str = Field(min_length=1, max_length=100)
    date_of_birth: date | None = None

    @field_validator("pseudonym")
    @classmethod
    def validate_pseudonym(cls, value: str) -> str:
        normalised = _normalise_pseudonym(value)
        if not PSEUDONYM_PATTERN.fullmatch(normalised):
            raise ValueError(
                "pseudonym must use lowercase letters, digits, hyphen or underscore"
            )
        if len(normalised) < PSEUDONYM_MIN_LENGTH:
            raise ValueError("pseudonym is too short")
        return normalised

    @field_validator("pin")
    @classmethod
    def validate_pin(cls, value: SecretStr) -> SecretStr:
        return validate_new_pin(value)

    @field_validator("display_name")
    @classmethod
    def strip_display_name(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("display_name must not be blank")
        return stripped

    @field_validator("date_of_birth")
    @classmethod
    def refuse_a_future_birth_date(cls, value: date | None) -> date | None:
        if value is not None and value > datetime.now(UTC).date():
            raise ValueError("date_of_birth must not be in the future")
        return value


class ChildSelfRegisterRequest(ChildCreateRequest):
    """Payload a child submits to open its own profile.

    The family code takes the place of the parent session: it is what attaches
    the profile to a family. The profile it creates stays pending until that
    parent activates it, so knowing a code is never enough to join a family.
    """

    family_code: str = Field(min_length=1, max_length=FAMILY_CODE_LENGTH)

    @field_validator("family_code")
    @classmethod
    def normalise_code(cls, value: str) -> str:
        return normalise_family_code(value)


class ChildLoginRequest(BaseModel):
    """Credentials submitted by a child.

    The family code comes first because the pseudonym alone no longer designates
    anyone: uniqueness is familial. Unlike the creation payload, neither field is
    checked for shape here, only case-folded: running the format rules would
    answer a malformed pseudonym differently from an unknown one, and both must
    look the same from outside.
    """

    family_code: str = Field(min_length=1, max_length=FAMILY_CODE_LENGTH)
    pseudonym: str = Field(min_length=1, max_length=PSEUDONYM_MAX_LENGTH)
    pin: SecretStr

    @field_validator("family_code")
    @classmethod
    def normalise_code(cls, value: str) -> str:
        return normalise_family_code(value)

    @field_validator("pseudonym")
    @classmethod
    def normalise_pseudonym(cls, value: str) -> str:
        return _normalise_pseudonym(value)


class ChildPinResetRequest(BaseModel):
    """New PIN chosen by the parent for one of their children.

    No current PIN is asked: this is the route for a PIN nobody remembers, and
    the parent's own session is the proof of who is asking.
    """

    pin: SecretStr

    @field_validator("pin")
    @classmethod
    def validate_pin(cls, value: SecretStr) -> SecretStr:
        return validate_new_pin(value)


class ChildPinChangeRequest(BaseModel):
    """New PIN chosen by a child for itself, against the current one."""

    current_pin: SecretStr
    new_pin: SecretStr

    @field_validator("new_pin")
    @classmethod
    def validate_pin(cls, value: SecretStr) -> SecretStr:
        return validate_new_pin(value)


class ChildPublic(BaseModel):
    """Child fields the API is allowed to return.

    ``pin_hash`` is absent by construction rather than by filtering, so no later
    edit can leak it through this schema.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    pseudonym: str
    display_name: str
    date_of_birth: date | None
    status: str
    created_at: datetime
