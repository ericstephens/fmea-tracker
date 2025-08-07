# FMEA Tracker

A Failure Modes and Effects Analysis (FMEA) tracking application that helps teams identify, analyze, and mitigate potential failures in products or processes.

## Project Structure

```
fmea-tracker/
├── environment.yaml    # Conda environment configuration
├── podman-compose.yml  # Container configuration for PostgreSQL
├── manage.sh           # Script to start/stop/restart the application
├── src/
│   ├── api/            # FastAPI backend
│   ├── db/             # Database models and migrations
│   └── frontend/       # React frontend
└── tests/
    ├── api/            # API tests
    └── db/             # Database tests
```

## Technology Stack

- **Backend**: Python with FastAPI
- **Database**: PostgreSQL running in a Podman container
- **Frontend**: JavaScript with React
- **Environment Management**: Conda
- **Container Management**: Podman and podman-compose

## Getting Started

### Prerequisites

- Conda (for Python environment management)
- Podman (for container management)
- Node.js and npm (for frontend development)

### Setup

1. Clone the repository:
   ```
   git clone <repository-url>
   cd fmea-tracker
   ```

2. Create and activate the conda environment:
   ```
   conda env create -f environment.yaml
   conda activate fmea-tracker
   ```

3. Start the application using the management script:
   ```
   ./manage.sh start
   ```

   This will:
   - Start the PostgreSQL database in a Podman container
   - Start the FastAPI backend server
   - Start the React frontend development server

4. Access the application:
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Management Commands

- Start all components: `./manage.sh start`
- Stop all components: `./manage.sh stop`
- Restart all components: `./manage.sh restart`

## Development

### API Development

The API is built with FastAPI and provides endpoints for managing:
- Projects
- FMEAs
- Failure Modes
- Actions

### Database Development

The database uses SQLAlchemy ORM with PostgreSQL. Migrations are managed with Alembic.

### Frontend Development

The frontend is built with React and communicates with the API to provide a user-friendly interface for managing FMEA data.
