# TEQSmartSubmit – Updated Architecture & Implementation Plan

## Overview
TEQSmartSubmit now runs entirely off the Next.js application while using Python **scripts** (no live FastAPI server required) for Playwright-based automation. The frontend orchestrates automation by spawning the helper script on demand and exposes REST-style endpoints from `/app/api`.

```
teqsmartsubmit/
├─ automation/
│  └─ run_submission.py      # Python helper invoked per request
├─ prisma/
│  └─ schema.prisma          # Prisma schema describing DB models
├─ src/
│  └─ app/
│     ├─ api/run/route.ts    # Next.js API route that launches Python + logs in DB
│     ├─ (auth)/...          # Login/Register pages
│     └─ (dashboard)/...     # Domains, templates, logs, settings
├─ next.config.ts            # Build config (lint/types errors ignored in prod build)
├─ package.json
├─ tsconfig.json
└─ automation scripts, env files, etc.
```

(The old `frontend/` wrapper is no longer needed—Next.js now runs directly from the repository root.)

## Core Components
1. **Next.js Frontend**
   - Routes under `/app/(dashboard)` provide admin UI (domains, templates, logs, settings).
   - `/app/(auth)` handles login/register with client-side auth context.
   - `/app/api/run/route.ts` receives automation requests, writes a temp JSON template, spawns `automation/run_submission.py`, and streams its JSON result back to the caller.
   - `next.config.ts` is configured to skip lint/type errors during production builds and runs in strict mode.

2. **Python Automation Helper**
   - `automation/run_submission.py` accepts `--url` and `--template` (JSON path) arguments.
   - Uses Playwright to load the page, fill selectors, handle captcha hook (placeholder), and submit.
   - Prints a JSON payload to stdout to let the API route detect success/failure.
   - Extend this script with retries, proxy support, screenshot capture, or captcha solving as requirements grow.

3. **Legacy FastAPI Backend (optional)**
   - Existing FastAPI/SQLAlchemy service remains in `/backend/` for reference or future extraction.
   - If you wish to decommission it, copy/paste required database/report logic into Node or keep it running as a dedicated worker service.

## Iteration Roadmap
1. **Finalize Helper Flow**
   - Confirm Playwright is installed system-wide (`playwright install chromium`).
   - Flesh out template format (selectors, dynamic values, defaults).
   - Implement captcha solving strategy (external service or manual fallback).

2. **Frontend Enhancements**
   - Build UI to edit/store templates as JSON.
   - Add job history/log endpoints (could log to Postgres via Prisma/pg).
   - Show live execution status: poll the API route or store job results.

3. **Persistence & Reporting**
   - If you need historical data, integrate Prisma (or other ORM) with PostgreSQL directly from Next.js API routes.
   - Port CSV/PDF exports to Node libraries (`json2csv`, `pdfkit`, etc.) or call a small Python script for those exports.

4. **Deployment**
   - PM2 process for Next.js: `npm run start` on port 3014 (already proxied by Nginx).
   - Optional PM2 process for a Python “worker” if you later schedule background jobs.
   - Nginx directs `/` to port 3014; `/api` continues to hit Next.js API routes.
   - Ensure `NEXT_PUBLIC_API_BASE_URL` points to `https://teqsmartsubmit.xcelanceweb.com/api`.

5. **Testing & QA**
   - Add Jest/Playwright tests for Next.js components and `route.ts`.
   - For automation script, create small Python unit tests or run integration tests via CI.
   - Validate error handling (missing fields, captcha failure, DOM changes).

## Notes & Reminders
- **Security**: Validate inputs carefully; only allow authenticated admins to spawn automation tasks.
- **Resource usage**: Each run spawns its own Python/Playwright process. Consider a job queue if concurrency grows.
- **Logging**: Capture stdout/stderr and persist job results; expose them in the dashboard.
- **Extensibility**: You can still reintroduce FastAPI or a Python worker later (e.g., for scheduled runs) without changing the frontend contract.

This plan keeps the UI and HTTP layer in Next.js while allowing Python to do what it’s best at—browser automation. Follow the roadmap to incrementally add the remaining features (DB, exports, notifications) as needed. Let me know if you want sample Prisma schema or queue integration next.*** End Patch

