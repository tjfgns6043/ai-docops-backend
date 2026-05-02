"""Async database session setup."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..core.config import get_settings


def make_session_factory(database_url: str | None = None) -> async_sessionmaker[AsyncSession]:
    """Create an async session factory.

    The asyncpg driver is only required when this factory is used to connect.
    """
    settings = get_settings()
    engine = create_async_engine(database_url or settings.database_url, pool_pre_ping=True)
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield an async SQLAlchemy session for FastAPI dependencies."""
    session_factory = make_session_factory()
    async with session_factory() as session:
        yield session
