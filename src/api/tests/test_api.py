import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Import directly from the project structure
from src.db.database import Base, get_db
from src.api.main import app
from src.db.models import Project, FMEA, FailureMode, Action

# Create test database URL
SQLALCHEMY_DATABASE_URL = "postgresql://fmea:fmea_password@localhost:5432/fmea_db_test"

# Create test engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Set up the database once for the entire test session
@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    # Create tables outside of any transaction
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Verify tables were created
    with engine.connect() as conn:
        result = conn.execute(text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public'"))
        tables = [row[0] for row in result]
        print(f"Tables created in test database: {tables}")
    
    yield
    
    # Clean up after all tests
    Base.metadata.drop_all(bind=engine)

# Create a fresh database session for each test
@pytest.fixture
def db():
    # Create a new session for each test
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a test client with the database session
@pytest.fixture
def client(db):
    # Override the get_db dependency
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    # Set up the override
    app.dependency_overrides[get_db] = override_get_db
    
    # Create and yield the test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear the override after the test
    app.dependency_overrides.clear()

def test_read_root(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the FMEA Tracker API"}

def test_create_project(client):
    """Test creating a project."""
    project_data = {
        "name": "Test Project",
        "description": "A test project for API testing"
    }
    response = client.post("/projects/", json=project_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == project_data["name"]
    assert data["description"] == project_data["description"]
    assert "id" in data
    assert "created_at" in data

def test_read_projects(client):
    """Test reading all projects."""
    # First create a project
    project_data = {
        "name": "Another Test Project",
        "description": "Another test project for API testing"
    }
    client.post("/projects/", json=project_data)
    
    # Now get all projects
    response = client.get("/projects/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1  # At least one project should exist

def test_read_project(client):
    """Test reading a specific project."""
    # First create a project
    project_data = {
        "name": "Project to Read",
        "description": "A project to test reading"
    }
    create_response = client.post("/projects/", json=project_data)
    project_id = create_response.json()["id"]
    
    # Now get the project
    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == project_data["name"]
    assert data["description"] == project_data["description"]

def test_update_project(client):
    """Test updating a project."""
    # First create a project
    project_data = {
        "name": "Project to Update",
        "description": "A project to test updating"
    }
    create_response = client.post("/projects/", json=project_data)
    project_id = create_response.json()["id"]
    
    # Now update the project
    update_data = {
        "name": "Updated Project",
        "description": "This project has been updated"
    }
    response = client.put(f"/projects/{project_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]

def test_delete_project(client):
    """Test deleting a project."""
    # First create a project
    project_data = {
        "name": "Project to Delete",
        "description": "A project to test deletion"
    }
    create_response = client.post("/projects/", json=project_data)
    project_id = create_response.json()["id"]
    
    # Now delete the project
    response = client.delete(f"/projects/{project_id}")
    assert response.status_code == 200
    
    # Verify it's gone
    get_response = client.get(f"/projects/{project_id}")
    assert get_response.status_code == 404
