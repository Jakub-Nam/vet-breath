# syntax=docker/dockerfile:1
# VetBreath backend image for Railway. Runtime deps only (uv --no-dev). Alembic
# migrations run at container start — safe for the single-instance MVP. Before scaling
# past one replica, move `alembic upgrade head` out of CMD into a dedicated release step.
FROM python:3.14-slim

# uv, pinned from the official image (bump the tag to upgrade)
COPY --from=ghcr.io/astral-sh/uv:0.11 /uv /uvx /bin/

WORKDIR /app

# Install runtime dependencies first for better layer caching
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# App source, then finish the install
COPY . .
RUN uv sync --frozen --no-dev

# Put the project venv on PATH so `alembic` / `uvicorn` resolve directly
ENV PATH="/app/.venv/bin:$PATH"

# Railway injects $PORT. Apply migrations, then serve.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
