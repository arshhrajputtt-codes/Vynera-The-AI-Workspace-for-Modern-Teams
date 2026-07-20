from collections.abc import Generator

from sqlalchemy.orm import Session

from app.db.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a DB session and guarantees it's closed,
    even if the request handler raises.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
