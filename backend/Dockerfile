# Build context should be the repository root:
#   docker build -f backend/Dockerfile -t multi-wordle-backend .
FROM python:3.14-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY backend/pyproject.toml backend/uv.lock backend/README.md ./
RUN uv sync --no-dev --no-install-project

COPY backend/src ./src
COPY data ./data

ENV PYTHONPATH=/app/src
EXPOSE 8000

CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
