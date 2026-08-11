from app.core.db import DATABASE_URL, Base


def test_database_url_uses_async_postgresql_driver() -> None:
    assert DATABASE_URL.startswith("postgresql+asyncpg://")


def test_base_metadata_is_available() -> None:
    assert Base.metadata is not None
