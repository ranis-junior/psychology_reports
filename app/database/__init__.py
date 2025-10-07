from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.settings import settings

db_url = f'{settings.DATABASE_TYPE}://{settings.DATABASE_HOST}/{settings.DATABASE_NAME}'
engine = create_async_engine(db_url,
                             connect_args={"user": settings.DB_USER, "password": settings.DB_PASSWORD}, echo=False)

AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_session_generator() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


@asynccontextmanager
async def get_session_contextmanager():
    async with AsyncSessionLocal() as session:
        yield session
