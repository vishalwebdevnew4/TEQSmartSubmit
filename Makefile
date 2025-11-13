# Makefile for TEQSmartSubmit project

PYTHON ?= python3
POETRY ?= poetry
BACKEND_DIR := backend
FRONTEND_DIR := frontend

.PHONY: all
all: install-backend install-frontend migrate-backend

.PHONY: install-backend
install-backend:
	cd $(BACKEND_DIR) && $(POETRY) install

.PHONY: install-frontend
install-frontend:
	cd $(FRONTEND_DIR) && npm install

.PHONY: migrate-backend
migrate-backend:
	cd $(BACKEND_DIR) && $(POETRY) run alembic upgrade head

.PHONY: backend
backend:
	cd $(BACKEND_DIR) && $(POETRY) run uvicorn app.main:app --reload

.PHONY: frontend
frontend:
	cd $(FRONTEND_DIR) && npm run dev

.PHONY: lint-backend
lint-backend:
	cd $(BACKEND_DIR) && $(POETRY) run ruff check .

.PHONY: lint-frontend
lint-frontend:
	cd $(FRONTEND_DIR) && npm run lint

.PHONY: test-backend
test-backend:
	cd $(BACKEND_DIR) && $(POETRY) run pytest

