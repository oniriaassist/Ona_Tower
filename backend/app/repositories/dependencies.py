from collections.abc import Generator

from app.database.session import SessionLocal, get_engine
from app.repositories.base import BackendRepository
from app.repositories.sqlalchemy_repository import SQLAlchemyRepository


def get_repository() -> Generator[BackendRepository, None, None]:
    """Provide a request-scoped SQLAlchemy repository."""
    db = SessionLocal(bind=get_engine())
    try:
        yield SQLAlchemyRepository(db)
    finally:
        db.close()
