"""Async SQLAlchemy database setup with aiosqlite."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

import os

# Use DATABASE_URL env var if set (e.g., Railway Postgres), fall back to local SQLite
# On Railway/cloud: persist data with Postgres or keep SQLite in /data which survives restarts
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "sqlite+aiosqlite:////data/skillforge.db" if os.path.exists("/data") else "sqlite+aiosqlite:///skillforge.db"
)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:  # type: ignore[misc]
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
