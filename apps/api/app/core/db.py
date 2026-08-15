from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# Read through the settings rather than from `os.environ` directly. Both work in
# the container, where Compose injects the values as real environment variables;
# only this one also reads `apps/api/.env`, which is what a developer running the
# migrations or the tests from the machine has. Two ways of reaching the same
# setting, one of which ignores a file the other honours, is how a check ends up
# passing on one side and failing on the other.
DATABASE_URL = settings.DATABASE_URL


def sync_database_url(url: str = DATABASE_URL) -> str:
    """The same database, reached by a synchronous driver.

    The application speaks asyncpg because it serves requests on an event loop.
    A command-line tool has no loop to serve and no reason to open one, so it
    borrows psycopg2, which is already installed for Alembic.
    """
    return url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")


engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)
AsyncSessionFactory = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


class Base(DeclarativeBase):
    pass


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionFactory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def dispose_engine() -> None:
    await engine.dispose()
