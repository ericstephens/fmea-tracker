# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

All project management is handled through the `manage.sh` script:

- `./manage.sh start` - Start PostgreSQL database container (podman-compose)
- `./manage.sh stop` - Stop database container  
- `./manage.sh restart` - Restart database container
- `./manage.sh status` - Check container status
- `./manage.sh logs` - View database logs
- `./manage.sh migrate` - Run Alembic migrations (`alembic upgrade head`)
- `./manage.sh test:db` - Run database layer tests (`pytest src/db`)
- `./manage.sh test:api` - Run API layer tests (`pytest src/api/tests`)
- `./manage.sh api` - Start FastAPI development server with hot reload

## Environment & Dependencies

- **Python Environment**: Conda environment named `fmea-tracker` (matches project folder name)
- **Database**: PostgreSQL only (no SQLite anywhere)
- **Container Runtime**: Podman (not Docker) with podman-compose
- **Dependencies**: Managed via `environment.yaml` in project root
- **Database URL**: Default PostgreSQL on `127.0.0.1:5433`

## Architecture

### Three-Layer Structure
- `src/db/` - Database layer with SQLAlchemy models and migrations
- `src/api/` - FastAPI REST API with routers and CRUD operations  
- `src/frontend/` - Frontend layer (planned, not yet implemented)

### Key Components
- **Database Models**: Complete FMEA domain model in `src/db/models.py`
  - `FMEA` - Main FMEA records with versioning and lifecycle management
  - `FailureMode` - Failure modes with severity/occurrence/detection ratings and computed RPN
  - `Action`, `FailureCause`, `FailureEffect`, `Control` - Supporting entities
- **API Routers**: FastAPI routers in `src/api/routers/` for each entity type
- **Migrations**: Alembic migrations in `alembic/versions/` with complete schema history

### Database Design
- PostgreSQL with proper foreign keys and constraints
- Computed columns (RPN = severity × occurrence × detection)
- Lifecycle management with status enums and approval workflows
- FMEA versioning with `supersedes_fmea_id` relationships
- Cascade deletes from FMEA → FailureMode → related entities

## Development Rules

### Structure & Dependencies  
- Use relative imports within each layer (avoid absolute imports)
- No circular dependencies between layers (db ← api ← frontend)
- Frontend must access database only through API endpoints
- Create tests in parallel `tests/` folders for each layer

### Database & Testing
- Use PostgreSQL exclusively (never SQLite)
- Run PostgreSQL in local podman container via `src/db/podman-compose.yml`
- All tests use real database connections (no mocking)
- Tests create/drop tables for isolation

### Package Management
- Use conda for all Python package management
- Update environment with `conda env update -f environment.yaml --prune`
- Run commands in conda environment via `conda run -n fmea-tracker <command>`

## Testing Strategy

- **Database Tests**: `src/db/tests/` - Integration tests with real PostgreSQL
- **API Tests**: `src/api/tests/` - FastAPI endpoint tests with test database
- **No Mocking**: All tests use real implementations per project rules
- **pytest**: Test framework for all Python testing

## Migration Workflow

1. Make model changes in `src/db/models.py`
2. Generate migration: `alembic revision --autogenerate -m "description"`
3. Review and edit migration file if needed
4. Apply migration: `./manage.sh migrate` or `alembic upgrade head`
5. Test migration with `./manage.sh test:db`