# TEQSmartSubmit Backend

FastAPI-based service that powers the TEQSmartSubmit automation platform. This project exposes REST APIs for administration, orchestrates Playwright automation runs, and manages persistence in PostgreSQL.

## Project Structure
```
backend/
├── app/
│   ├── api/                # Routers and dependency utilities
│   ├── core/               # Configuration, security, logging
│   ├── db/                 # Database session management
│   ├── schemas/            # Pydantic models
│   ├── services/           # Business logic and automation services
│   └── main.py             # FastAPI application entry point
├── tests/                  # Pytest-based automated tests
└── pyproject.toml          # Poetry configuration
```

## Getting Started
1. Install Poetry if not available: `pip install poetry`.
2. Install dependencies: `poetry install`.
3. Copy environment template: `cp env.example .env` (update secrets & `TEQ_DATABASE_URL` accordingly).
4. Run database migrations: `poetry run alembic upgrade head`.
5. Start the development server: `poetry run uvicorn app.main:app --reload`.

## Notes
- Playwright requires a one-time browser install: `poetry run playwright install`.
- For local development without PostgreSQL, you can set `TEQ_DATABASE_URL=sqlite+aiosqlite:///./dev.db` before running Alembic.
- Domain CRUD endpoints now persist to the configured database connection.
- Admin registration endpoint is available at `POST /api/v1/auth/register` and requires the `X-Admin-Token` header matching `TEQ_ADMIN_REGISTRATION_TOKEN`.
- Admin login is handled via `POST /api/v1/auth/login` which returns a Bearer token that must be supplied to protected endpoints.

