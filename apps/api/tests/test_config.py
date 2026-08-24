"""SECRET_KEY validation: presence alone is not enough.

`SECRET_KEY` has no default so pydantic-settings fails startup when the
variable is entirely absent, but a present-and-empty value (`SECRET_KEY=`,
exactly what `.env.example` ships as a template) is still a valid string and
would otherwise pass silently — reintroducing the empty key the missing
default was meant to rule out.
"""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_an_empty_secret_key_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(SECRET_KEY="")


def test_a_blank_secret_key_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(SECRET_KEY="   ")


def test_a_real_secret_key_is_accepted() -> None:
    settings = Settings(SECRET_KEY="a-real-generated-secret")

    assert settings.SECRET_KEY == "a-real-generated-secret"
