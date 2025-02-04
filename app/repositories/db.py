from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL = "sqlite:///./weather.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Создание таблиц
def create_tables():
    Base.metadata.create_all(bind=engine)


def get_db():
    """Создаёт и управляет сессией базы данных."""
    db = SessionLocal()
    try:
        yield db
    finally:
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
    except Exception as e:
        session.rollback()
        raise e
