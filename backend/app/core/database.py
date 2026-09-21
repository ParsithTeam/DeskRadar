# from sqlalchemy.ext.declarative import declarative_base
from contextlib import asynccontextmanager
from typing import AsyncIterator

# # بیس اصلی دیتا بیس
# Base = declarative_base()

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass

#------ default ------
engine = None
AsyncSessionLocal = None

if settings.DB_IS_ACTIVE:
    DATABASE_URL = settings.DATABASE_URL
    engine = create_async_engine(
        DATABASE_URL,
        echo=True,
        pool_size=10,
        max_overflow=10,
        pool_timeout=30,
    )

    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession | None]:
    """session می‌دهد؛ در حالت in-memory None."""
    if not settings.DB_IS_ACTIVE:
        yield None
        return

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise