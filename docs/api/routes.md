# TEQSmartSubmit API Routes

Base URLs  
- Development: `http://localhost:3000/api`  
- Production: `https://teqsmartsubmit.xcelanceweb.com/api`

## Automation

### `POST /api/run`

Launches a Playwright automation job via the Python helper script and logs the run in PostgreSQL.

#### Request (JSON)
```jsonc
{
  "url": "https://example.com/contact",
  "template": {
    "fields": [
      { "selector": "input[name='name']", "value": "John Doe" },
      { "selector": "#email", "value": "john@example.com" }
    ],
    "submit_selector": "button[type='submit']",
    "post_submit_wait_ms": 3000,
    "captcha": false
  },
  "domainId": 1,
  "templateId": 3,
  "adminId": 2
}
```

- `url` (string, required): Page containing the form to submit.
- `template` (required): JSON specifying selectors and values. Arbitrary fields are persisted to the temporary template passed to the helper.
- `domainId`, `templateId`, `adminId` (optional integers): Provide relational links for logging purposes.

#### Response (JSON)
```jsonc
{
  "status": "success",
  "message": "Submission completed",
  "submissionId": 42
}
```

- `status`: `success` or `failed` (or any status specified by the helper).
- `message`: detailed message from the script or standard fallback.
- `submissionId`: ID of the log stored in the `SubmissionLog` table.

On failure, returns HTTP 500 with:
```jsonc
{
  "status": "error",
  "message": "Detailed error message"
}
```

## Authentication

### `POST /auth/register`

Creates a new admin user. Requires the registration token in the `X-Admin-Token` header (`TEQ_ADMIN_REGISTRATION_TOKEN`).

#### Request
```jsonc
{
  "username": "admin@example.com",
  "password": "StrongPassword123!"
}
```

#### Response
```jsonc
{
  "status": "success"
}
```

### `POST /auth/login`

Authenticates an admin and returns a JWT.

#### Request
```jsonc
{
  "username": "admin@example.com",
  "password": "StrongPassword123!"
}
```

#### Response
```jsonc
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin@example.com"
  }
}
```

## Domains / Templates / Logs

> CRUD endpoints for domains, templates, and log retrieval are not yet exposed server-side. Data will be surfaced via future Prisma-backed API routes.

## Health

If the legacy FastAPI service is running, the health endpoint remains available at:

- `GET /api/v1/health/` – returns `{ "status": "ok" }`

This is optional and only used if the Python backend stays in service.


