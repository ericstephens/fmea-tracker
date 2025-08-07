import pytest
import os
import sys
from sqlalchemy import text

# Add the parent directory to the path so we can import the database module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database and models
from database import get_db, engine
from models import Base, Project, FMEA, FailureMode, Action

@pytest.fixture(scope="module")
def setup_database():
    """Set up the test database."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up (optional - depends on your testing strategy)
    # Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db_session(setup_database):
    """Get a test database session."""
    db = next(get_db())
    yield db
    db.close()

# Test database connection
def test_database_connection(db_session):
    """Test that we can connect to the database."""
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1

# Test session creation
def test_session_creation(db_session):
    """Test that we can create a database session."""
    assert db_session is not None

# Test model creation
def test_create_tables(db_session):
    """Test that we can create database tables from models."""
    # Check if tables were created
    result = db_session.execute(
        text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    )
    tables = [row[0] for row in result]
    # Verify we have at least one table
    assert len(tables) > 0
