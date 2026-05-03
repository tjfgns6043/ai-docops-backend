"""Worker database session setup."""

from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from ..core.config import get_settings


@lru_cache
def make_session_factory(database_url: str | None = None) -> async_sessionmaker[AsyncSession]:
    """Create async session factory."""
    settings = get_settings()
    engine = create_async_engine(database_url or settings.database_url, pool_pre_ping=True)
    return async_sessionmaker(engine, expire_on_commit=False)
