from typing import Generator
from sqlalchemy.orm import Session

from src.db.session import SessionLocal as _SessionLocal

SessionLocal = _SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
