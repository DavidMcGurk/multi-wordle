PYTHON ?= python3
UV ?= uv
FRONTEND_DIR := frontend
BACKEND_DIR := backend

.PHONY: dev backend frontend test lint typecheck e2e db-up db-down

dev:
	@$(MAKE) db-up
	@$(MAKE) backend &
	@$(MAKE) frontend

backend:
	cd $(BACKEND_DIR) && PYTHONPATH=src $(UV) run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

frontend:
	cd $(FRONTEND_DIR) && npm run dev -- --host 0.0.0.0

test:
	cd $(BACKEND_DIR) && $(UV) run pytest -q
	cd $(FRONTEND_DIR) && npm run test -- --run

lint:
	cd $(BACKEND_DIR) && $(UV) run ruff check src tests
	cd $(FRONTEND_DIR) && npm run lint

typecheck:
	cd $(FRONTEND_DIR) && npm run build

# Requires Playwright browsers to be installed
e2e:
	cd $(FRONTEND_DIR) && npx playwright test

db-up:
	docker compose up -d postgres

db-down:
	docker compose down
