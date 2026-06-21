# Build stage
FROM node:22-slim AS web-build

WORKDIR /app
COPY package.json pnpm-workspace.yaml ./
COPY apps/web ./apps/web
RUN corepack enable pnpm && pnpm install --frozen-lockfile
RUN pnpm --filter @entelekx/web build

# Python backend stage
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS backend

WORKDIR /app/packages/backend
COPY packages/backend/pyproject.toml packages/backend/uv.lock* ./
COPY packages/backend/src ./src
COPY packages/backend/alembic ./alembic
COPY packages/backend/alembic.ini ./

RUN uv sync --no-dev

# Final stage
FROM python:3.12-slim-bookworm

WORKDIR /app

# Copy backend
COPY --from=backend /app/packages/backend/.venv ./packages/backend/.venv
COPY --from=backend /app/packages/backend/src ./packages/backend/src
COPY --from=backend /app/packages/backend/alembic ./packages/backend/alembic
COPY --from=backend /app/packages/backend/alembic.ini ./packages/backend/
COPY --from=backend /app/packages/backend/pyproject.toml ./packages/backend/

# Copy static frontend build
COPY --from=web-build /app/apps/web/.output/public ./packages/backend/src/entelekx_backend/static

ENV PATH=/app/packages/backend/.venv/bin:$PATH
ENV PYTHONPATH=/app/packages/backend/src

EXPOSE 7349

CMD ["sh", "-c", "cd /app/packages/backend && alembic upgrade head && python -m entelekx_backend.main"]
