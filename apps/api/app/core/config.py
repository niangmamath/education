"""
StudentConnect API Configuration Settings

Pydantic Settings management for environment variables.
"""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Environment
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=True, env="DEBUG")
    
    # API Configuration
    API_TITLE: str = Field(default="StudentConnect API", env="API_TITLE")
    API_DESCRIPTION: str = Field(
        default="FastAPI backend for StudentConnect EdTech platform",
        env="API_DESCRIPTION"
    )
    API_VERSION: str = Field(default="0.1.0", env="API_VERSION")
    API_HOST: str = Field(default="0.0.0.0", env="API_HOST")
    API_PORT: int = Field(default=8000, env="API_PORT")
    API_DOCS_URL: str = Field(default="", env="API_DOCS_URL")
    API_V1_PREFIX: str = Field(default="/api/v1", env="API_V1_PREFIX")
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        env="CORS_ORIGINS"
    )
    
    # Database (PostgreSQL)
    DATABASE_URL: str = Field(
        default="postgresql://studentconnect:studentconnect@localhost:5432/studentconnect_dev",
        env="DATABASE_URL"
    )
    DATABASE_POOL_SIZE: int = Field(default=5, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, env="DATABASE_MAX_OVERFLOW")
    
    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    REDIS_CACHE_TTL: int = Field(default=3600, env="REDIS_CACHE_TTL")
    
    # Celery
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1",
        env="CELERY_BROKER_URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/2",
        env="CELERY_RESULT_BACKEND"
    )
    
    # Security
    SECRET_KEY: str = Field(
        default="change-me-in-production-use-secrets-manager",
        env="SECRET_KEY"
    )
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Storage (S3-compatible)
    STORAGE_ENDPOINT: str = Field(
        default="http://localhost:9000",
        env="STORAGE_ENDPOINT"
    )
    STORAGE_ACCESS_KEY: str = Field(
        default="minioadmin",
        env="STORAGE_ACCESS_KEY"
    )
    STORAGE_SECRET_KEY: str = Field(
        default="minioadmin",
        env="STORAGE_SECRET_KEY"
    )
    STORAGE_BUCKET: str = Field(
        default="studentconnect-content",
        env="STORAGE_BUCKET"
    )
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", env="LOG_FORMAT")
    
    # Rate Limiting
    RATE_LIMIT: int = Field(default=100, env="RATE_LIMIT")
    RATE_LIMIT_PERIOD: int = Field(default=60, env="RATE_LIMIT_PERIOD")
    
    # Model configuration
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
