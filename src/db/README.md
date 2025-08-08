# DB Layer (PostgreSQL via Podman)

This package contains the SQLAlchemy setup, ORM models, and real-database tests for the FMEA Tracker.

- Database: PostgreSQL (no SQLite).
- Containers: Podman / podman-compose.
- Tests: pytest hitting a real Postgres instance (no mocks).

## Layout

- `config.py` — loads DB configuration from environment/.env and builds a SQLAlchemy URL.
- `database.py` — engine and session management helpers.
- `models.py` — ORM `Base` and example `FailureMode` model.
- `tests/` — pytest fixtures and integration tests that operate on a real DB.
- `podman-compose.yml` — local Postgres service for development/testing.
- `.env.example` — template for environment variables.
 Dependencies are managed centrally via the root-level `environment.yaml`.

## Prerequisites

- Conda environment named after the project root folder (per project rules).
- Podman and podman-compose installed and configured.

## Setup

1) Create your `.env` from the example:

```bash
cp src/db/.env.example src/db/.env
```

2) Create/update and activate the root conda environment using the single `environment.yaml` at project root:

```bash
# From project root
conda env update -f environment.yaml --prune  # or: conda env create -f environment.yaml
conda activate fmea-tracker
```

3) Start PostgreSQL via Podman Compose:

```bash
podman-compose -f src/db/podman-compose.yml up -d
```

This exposes Postgres on `127.0.0.1:5433` by default.

## Run tests

From the repo root or from `src/db/`:

```bash
pytest -q src/db
```

The test suite will:
- Create tables (`Base.metadata.create_all`) at the start of the test session.
- Run tests using real transactions.
- Drop all tables at the end of the session to leave the DB clean.

## Notes

- Tests require a running Postgres instance. They will fail fast if the DB is unreachable.
- `config.py` reads environment variables automatically via `python-dotenv` if a `.env` file exists.
