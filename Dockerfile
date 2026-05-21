FROM python:3.12-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy workspace config and packages
COPY pyproject.toml .
COPY packages/skillforge-core/pyproject.toml packages/skillforge-core/pyproject.toml
COPY packages/skillforge-core/src packages/skillforge-core/src
COPY packages/skillforge-api/pyproject.toml packages/skillforge-api/pyproject.toml
COPY packages/skillforge-api/src packages/skillforge-api/src

# Copy reference skills for auto-seeding
COPY skills/ skills/

# Install dependencies
RUN uv sync --package skillforge-api --no-dev

# Ensure /data exists for persistent SQLite
RUN mkdir -p /data

# Run the API
CMD ["uv", "run", "uvicorn", "skillforge_api.app:app", "--host", "0.0.0.0", "--port", "8000"]
