from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from .config import settings


# Decision: use SQLAlchemy AsyncEngine for non-blocking DB I/O in FastAPI endpoints.
DATABASE_URL = settings.DATABASE_URL


def _create_engine() -> AsyncEngine:
    # Use asyncpg dialect; settings.DATABASE_URL should be an async URL (postgresql+asyncpg://...)
    return create_async_engine(
        DATABASE_URL,
        echo=False,
        future=True,
    )


engine: AsyncEngine = _create_engine()

# async_sessionmaker factory
async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
