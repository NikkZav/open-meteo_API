from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                    create_async_engine, )
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from utils.log import logger
from typing import AsyncGenerator


DATABASE_URL = "sqlite+aiosqlite:///./weather.db"

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession,
                                 expire_on_commit=False)
Base = declarative_base()


async def create_tables():
    """Создает таблицы в базе данных асинхронно."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")


@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Асинхронный контекстный менеджер для работы с сессией базы данных.
       Используется как FastAPI dependency и для фоновых задач."""
    logger.info("Creating asynchronous database session")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            logger.info("Closing asynchronous database session")
            await session.close()


@asynccontextmanager
async def transaction(session: AsyncSession):
    """
    Асинхронный контекстный менеджер для транзакций.
    При успешном выполнении блока вызывается commit, при ошибке — rollback.
    """
    try:
        yield
        await session.commit()
        logger.debug("Transaction committed successfully")
    except Exception as e:
        await session.rollback()
        logger.error(f"Transaction rolled back due to error: {e}")
        raise e
