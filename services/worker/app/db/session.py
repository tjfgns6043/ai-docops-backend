"""Worker database session setup."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from ..core.config import get_settings


def make_session_factory(database_url: str | None = None) -> async_sessionmaker[AsyncSession]:
    """Create async session factory.

    Celery tasks run async code through ``asyncio.run()``, which creates a fresh
    event loop per task. NullPool avoids reusing asyncpg connections across
    those loops.
    """
    settings = get_settings()
    engine = create_async_engine(
        database_url or settings.database_url,
        pool_pre_ping=True,
        poolclass=NullPool,
    )
    return async_sessionmaker(engine, expire_on_commit=False)
