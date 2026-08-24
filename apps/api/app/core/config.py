"""StudentConnect API configuration settings."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any, Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API
    API_TITLE: str = "StudentConnect API"
    API_DESCRIPTION: str = "FastAPI backend for StudentConnect EdTech platform"
    API_VERSION: str = "0.1.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_DOCS_URL: str = ""
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # PostgreSQL
    DATABASE_URL: str = "postgresql+asyncpg://localhost/studentconnect"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"
    REDIS_CACHE_TTL: int = 3600

    # Celery
    CELERY_BROKER_URL: str = "redis://redis:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/2"

    # Security. No default: an empty or well-known key would let anyone
    # recompute the pseudonyms `actor_key` derives from it (see
    # `app/xapi/statements.py`), so a missing value must fail startup rather
    # than silently sign with `""`. CI and Render already provide one.
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Sessions (ADR-005: opaque identifiers held in Redis, never in PostgreSQL)
    SESSION_COOKIE_NAME: str = "studentconnect_session"
    SESSION_COOKIE_SAMESITE: Literal["lax", "strict", "none"] = "lax"
    SESSION_TTL_SECONDS: int = 7 * 24 * 60 * 60
    SESSION_COOKIE_SECURE: bool | None = None

    # Child access (ADR-005: a child session lives a day, not a week, and six
    # digits only resist guessing if the attempts themselves are capped)
    CHILD_SESSION_TTL_SECONDS: int = 24 * 60 * 60
    CHILD_PIN_MAX_ATTEMPTS: int = 5
    CHILD_PIN_LOCKOUT_SECONDS: int = 15 * 60

    # Parent login: a password is not a six-digit PIN, but nothing else in
    # front of `/parent/login` caps repeated guesses either, so the same
    # Redis-backed lockout applies here (see `app/core/lockout.py`).
    PARENT_LOGIN_MAX_ATTEMPTS: int = 5
    PARENT_LOGIN_LOCKOUT_SECONDS: int = 15 * 60

    # S3-compatible storage
    S3_ENDPOINT_URL: str = "http://storage:9000"
    S3_PUBLIC_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_REGION: str = "us-east-1"

    S3_BUCKET_H5P_PACKAGES: str = "studentconnect-h5p-packages"
    S3_BUCKET_H5P_RUNTIME: str = "studentconnect-h5p-runtime"
    S3_BUCKET_MEDIA: str = "studentconnect-media"
    S3_BUCKET_PRIVATE_EVIDENCE: str = "studentconnect-private-evidence"
    S3_BUCKET_THUMBNAILS: str = "studentconnect-thumbnails"

    # Content runtime (ADR-012, condition 5: a runtime isolated behind its own
    # origin, so that a content cannot read the application's cookies). The API
    # writes the deployed tree, the content origin serves it read-only.
    CONTENT_RUNTIME_ROOT: str = "/srv/content"
    CONTENT_ORIGIN_URL: str = "http://localhost:8081"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # Rate limiting
    RATE_LIMIT: int = 100
    RATE_LIMIT_PERIOD: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    @property
    def session_cookie_secure(self) -> bool:
        """Whether the session cookie is restricted to HTTPS.

        Left unset, the flag is on everywhere except local development, so a
        forgotten environment variable fails closed rather than shipping a
        cookie a proxy could read in clear.
        """
        if self.SESSION_COOKIE_SECURE is not None:
            return self.SESSION_COOKIE_SECURE
        return self.ENVIRONMENT != "development"

    @field_validator("SECRET_KEY")
    @classmethod
    def reject_empty_secret_key(cls, value: str) -> str:
        """Reject a present-but-empty key, not only a missing one.

        `SECRET_KEY` having no default already fails startup when the
        variable is absent, but pydantic-settings accepts an explicitly
        empty value (`SECRET_KEY=`, exactly what `.env.example` ships as a
        template) as a valid string — silently reintroducing the empty key
        the missing default was meant to rule out.
        """
        if not value.strip():
            raise ValueError(
                "SECRET_KEY must not be empty: generate one with "
                'python3 -c "import secrets; print(secrets.token_urlsafe(48))"'
            )
        return value

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> Any:
        """Accept a JSON array or a comma-separated origins list."""
        if not isinstance(value, str):
            return value

        stripped = value.strip()

        if stripped.startswith("["):
            return json.loads(stripped)

        return [origin.strip() for origin in stripped.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings."""
    # `SECRET_KEY` has no default, so pydantic-settings' generated `__init__`
    # requires it — mypy sees that signature and reports the argument
    # missing, without knowing that `BaseSettings` fills it from the
    # environment or `.env` at runtime, exactly where the real check belongs.
    return Settings()  # type: ignore[call-arg]


settings = get_settings()
