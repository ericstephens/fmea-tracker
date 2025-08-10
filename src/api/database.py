from __future__ import annotations

from sqlalchemy.orm import Session

from db.database import get_session_factory


def get_db() -> Session:
    session_factory = get_session_factory()
    session = session_factory()
    try:
        yield session
    finally:
        session.close()