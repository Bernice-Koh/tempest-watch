# backend

FastAPI + SQLAlchemy backend for tempest-watch.

## Setup

```bash
# Install dependencies (creates .venv automatically)
uv sync

# Start local Postgres
docker compose -f ../deploy/docker-compose.yml up -d postgres

# Run the dev server
uv run uvicorn api.main:app --reload --app-dir src

# Run tests
uv run pytest

# Lint + type-check
uv run ruff check
uv run mypy src
```

Layout follows `docs/CONVENTIONS.md`. Folders are created when there's code to put in them.
