#!/usr/bin/env bash
set -euo pipefail

# FMEA Tracker management script
# Controls local services and dev tasks per project rules.
# Requires: podman, podman-compose, pytest

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
DB_COMPOSE_FILE="$ROOT_DIR/src/db/podman-compose.yml"
ENV_FILE="$ROOT_DIR/environment.yaml"
CONDA_ENV_NAME="fmea-tracker"

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Error: required command '$1' not found in PATH" >&2
    exit 1
  fi
}

ensure_podman_machine() {
  require_cmd podman
  # If machine subcommand exists, ensure it's running
  if podman machine --help >/dev/null 2>&1; then
    # If there are no machines at all, create the default
    local machine_count
    machine_count=$(podman machine list --noheading --quiet 2>/dev/null | wc -l | tr -d ' ')
    if [ "${machine_count:-0}" -eq 0 ]; then
      echo "Creating default podman machine..."
      podman machine init
    fi

    # If no machine is running, start the default (no name implies default)
    if ! podman machine list --format json 2>/dev/null | grep -q '"Running": true'; then
      echo "Starting podman machine..."
      podman machine start || true
    fi
  fi
}

# -----------------------------
# Conda environment management
# -----------------------------
ensure_conda_available() {
  require_cmd conda
}

update_conda_env() {
  ensure_conda_available
  if [ -f "$ENV_FILE" ]; then
    echo "Updating conda environment ($CONDA_ENV_NAME) from $ENV_FILE..."
    conda env update -f "$ENV_FILE" --prune || {
      echo "Warning: failed to update conda env. Continuing may fail if deps are missing." >&2
    }
  else
    echo "Warning: $ENV_FILE not found; skipping conda env update." >&2
  fi
}

run_in_conda() {
  ensure_conda_available
  conda run -n "$CONDA_ENV_NAME" "$@"
}

compose_up() {
  require_cmd podman-compose
  ensure_podman_machine
  echo "Starting services (DB) with podman-compose..."
  podman-compose -f "$DB_COMPOSE_FILE" up -d
}

compose_down() {
  require_cmd podman-compose
  ensure_podman_machine
  echo "Stopping services (DB) with podman-compose..."
  podman-compose -f "$DB_COMPOSE_FILE" down
}

compose_restart() {
  compose_down
  compose_up
}

compose_logs() {
  require_cmd podman-compose
  ensure_podman_machine
  podman-compose -f "$DB_COMPOSE_FILE" logs -f --tail=200
}

compose_ps() {
  require_cmd podman-compose
  ensure_podman_machine
  podman-compose -f "$DB_COMPOSE_FILE" ps
}

run_tests_db() {
  update_conda_env
  echo "Running DB tests (in conda env '$CONDA_ENV_NAME')..."
  (cd "$ROOT_DIR" && run_in_conda pytest -q src/db)
}

migrate_db() {
  update_conda_env
  echo "Running Alembic migrations (in conda env '$CONDA_ENV_NAME')..."
  (cd "$ROOT_DIR" && run_in_conda alembic upgrade head)
}

run_tests_api() {
  update_conda_env
  echo "Running API tests (in conda env '$CONDA_ENV_NAME')..."
  (cd "$ROOT_DIR" && run_in_conda pytest -q src/api/tests)
}

start_api() {
  update_conda_env
  echo "Starting API server (in conda env '$CONDA_ENV_NAME')..."
  (cd "$ROOT_DIR" && run_in_conda uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload)
}

usage() {
  cat <<EOF
FMEA Tracker manage.sh

Usage: $0 <command>

Commands:
  start         Start local services (PostgreSQL via Podman Compose)
  stop          Stop local services
  restart       Restart local services
  status        Show service status
  logs          Tail service logs
  migrate       Apply DB migrations (alembic upgrade head)
  test:db       Run database tests (pytest src/db)
  test:api      Run API tests (pytest src/api/tests)
  api           Start API development server (uvicorn with reload)
  help          Show this help
EOF
}

cmd="${1:-help}"
case "$cmd" in
  start)
    compose_up
    ;;
  stop)
    compose_down
    ;;
  restart)
    compose_restart
    ;;
  status)
    compose_ps
    ;;
  logs)
    compose_logs
    ;;
  migrate)
    migrate_db
    ;;
  test:db)
    run_tests_db
    ;;
  test:api)
    run_tests_api
    ;;
  api)
    start_api
    ;;
  help|--help|-h)
    usage
    ;;
  *)
    echo "Unknown command: $cmd" >&2
    echo >&2
    usage
    exit 1
    ;;
esac
