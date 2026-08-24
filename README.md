# Wordle Race

A production-quality MVP for a real-time multiplayer Wordle-style race game. It includes a FastAPI backend, a React + TypeScript frontend, deterministic daily scheduling, PostgreSQL-ready persistence, and a lightweight in-memory game engine designed for multiplayer race gameplay.

## Prerequisites

- Python 3.14
- uv
- Node.js 20+
- npm
- Docker Desktop or Docker Compose for the PostgreSQL container

## Installation

```bash
# Install the backend environment
cd backend
uv sync --dev

# Install the frontend dependencies
cd ../frontend
npm install
```

## Local development

Start PostgreSQL:

```bash
docker compose up -d postgres
```

Start the backend:

```bash
cd backend
PYTHONPATH=src uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Start the frontend:

```bash
cd frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

Or use the root helpers:

```bash
make dev
```

## Running tests

```bash
# Backend
cd backend
uv run pytest -q

# Frontend
cd frontend
npm run test -- --run

# Browser end-to-end check
npx playwright test
```

## Linting and type checking

```bash
cd frontend
npm run lint
npm run build
```

```bash
cd backend
uv run ruff check src tests
```

## Generate word data

```bash
cd scripts
python3 build_word_lists.py
python3 generate_daily_schedule.py
```

The word data lives in `data/words_en.json` and `data/words_hu.json`.

## Database setup

The repository includes a PostgreSQL service in `docker-compose.yml` and a `DATABASE_URL` example in `.env.example`.

## Production build

```bash
cd frontend
npm run build
```

The generated static site can be deployed to a static host such as Cloudflare Pages. The FastAPI backend can be containerised and deployed to Render or a similar provider.

## Deployment notes

- Static frontend: deploy the `frontend/dist` output to a CDN or static host.
- API: run the FastAPI backend in Docker or a container platform.
- Database: use PostgreSQL and configure the `DATABASE_URL` environment variable.
- Keep host-specific assumptions out of the code and instead rely on environment variables.

## Project layout

- `backend/`: FastAPI backend and Python tests
- `frontend/`: Vite + React + TypeScript client
- `data/`: curated word lists and provenance notes
- `scripts/`: word generation and daily schedule tooling
- `docker-compose.yml`: local PostgreSQL service
- `Makefile`: quick local developer commands
