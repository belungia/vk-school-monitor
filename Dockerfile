# ponytail: uv base image already has Python + uv; no hand-rolled venv setup.
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Deps first for layer caching. --no-install-project: we run from /app via
# `src.` imports, so the project itself never needs to be a built package.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY . .

EXPOSE 8000

# Migrate (incl. status seed) then serve. DB host/port come from compose env.
CMD uv run alembic -c src/db/alembic.ini upgrade head && \
    uv run uvicorn src.api.routes:app --host 0.0.0.0 --port 8000
