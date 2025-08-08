from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .config import load_db_config

# Create SQLAlchemy engine and session factory based on environment configuration
_config = load_db_config()
_engine = create_engine(_config.sqlalchemy_url, pool_pre_ping=True, future=True)
_SessionLocal = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True, expire_on_commit=False)


def get_engine():
    return _engine


def get_session_factory():
    return _SessionLocal


@contextmanager
def get_session() -> Iterator[Session]:
    """Provide a transactional scope around a series of operations."""
    session: Session = _SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
