from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from utils.log import logger

DATABASE_URL = "sqlite:///./weather.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def create_tables():
    """Создаёт таблицы в базе данных."""
    logger.info("Creating database tables")
    Base.metadata.create_all(bind=engine)


def get_db():
    """Создаёт и управляет сессией базы данных."""
    logger.info("Creating database session")
    db = SessionLocal()
    try:
        yield db
    finally:
        logger.info("Closing database session")
        db.close()


@contextmanager
def get_db_context():
    """Используется в синхронном контексте (например, в фоновых задачах)."""
    yield from get_db()


@contextmanager
def transaction(session: Session):
    """Контекстный менеджер для транзакций.
    После выхода из блока yield выполняется commit,
    а в случае возникновения исключения — rollback.
    """
    try:
        yield
        session.commit()
        logger.debug("Transaction committed successfully")
    except Exception as e:
        session.rollback()
        logger.error(f"Transaction rolled back due to error: {e}")
        raise e
