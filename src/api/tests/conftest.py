from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Ensure 'src' is on sys.path when running tests from repo root
REPO_ROOT = Path(__file__).resolve().parents[3]
SRC_PATH = REPO_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from db.config import load_db_config
from db.database import get_engine, get_session_factory
from db.models import Base
from ..main import app
from ..database import get_db


@pytest.fixture(scope="session", autouse=True)
def ensure_db_url_env() -> None:
    _ = load_db_config()


@pytest.fixture(scope="session")
def engine() -> Iterator:
    engine = get_engine()
    # Create all tables once for the session
    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        # Drop all tables after the session to leave a clean DB
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(engine) -> Iterator[Session]:
    # Use a connection-level transaction for proper test isolation
    connection = engine.connect()
    transaction = connection.begin()
    
    SessionLocal = get_session_factory()
    session: Session = SessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        session.close()
        # Only rollback if transaction is still active
        if transaction.is_active:
            transaction.rollback()
        connection.close()


def override_get_db(db_session):
    def _override():
        yield db_session
    return _override


@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = override_get_db(db_session)
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()