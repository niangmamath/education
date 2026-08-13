"""Request and response schemas for parent authentication."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Final

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, field_validator

# OWASP ASVS asks for twelve characters on an account that guards a child's
# activity history. Argon2 has no input length ceiling of its own, so the upper
# bound only exists to keep a single request from hashing an unbounded payload.
PASSWORD_MIN_LENGTH: Final = 12
PASSWORD_MAX_LENGTH: Final = 128


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


class ParentPublic(BaseModel):
    """Parent fields the API is allowed to return.

    ``password_hash`` is absent by construction rather than by filtering, so no
    later edit can leak it through this schema.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    display_name: str
    is_verified: bool
    created_at: datetime
