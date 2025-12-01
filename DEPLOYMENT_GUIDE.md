# TEQSmartSubmit - Complete Deployment Guide

## Overview

This is a comprehensive SaaS automation system that:
- Fetches business data from Google Places API
- Generates Figma-style Next.js websites with AI-powered content
- Automatically deploys to Vercel
- Submits forms to multiple domains with CAPTCHA solving
- Sends client outreach emails with tracking
- Provides a full admin dashboard

## Architecture

- **Frontend**: Next.js 15 with TypeScript, Tailwind CSS, Prisma
- **Backend**: Python FastAPI with services for automation
- **Database**: PostgreSQL
- **Background Jobs**: Celery (optional) or direct Python script execution
- **Deployment**: Vercel (frontend) + Render/Railway (backend)

## Prerequisites

1. Node.js 18+ and npm
2. Python 3.10+
3. PostgreSQL database
4. Google Places API key
5. Vercel account and token
6. GitHub account and token (for deployments)
7. SMTP credentials (for email)

## Setup Instructions

### 1. Database Setup

```bash
# Create PostgreSQL database
createdb teqsmartsubmit

# Or using psql
psql -U postgres
CREATE DATABASE teqsmartsubmit;
```

### 2. Environment Variables

Copy `.env.example` to `.env.local` and fill in all values:

```bash
cp .env.example .env.local
```

Required variables:
- `DATABASE_URL`: PostgreSQL connection string
- `GOOGLE_PLACES_API_KEY`: From Google Cloud Console
- `VERCEL_TOKEN`: From Vercel dashboard
- `GITHUB_TOKEN`: From GitHub settings
- `SMTP_*`: Email service credentials

### 3. Install Dependencies

**Frontend:**
```bash
npm install
```

**Backend:**
```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Database Migrations

**Prisma (Next.js):**
```bash
npx prisma generate
npx prisma migrate dev
```

**Alembic (Python backend):**
```bash
cd backend
alembic upgrade head
```

### 5. Run Development Servers

**Frontend (Next.js):**
```bash
npm run dev
# Runs on http://localhost:3000
```

**Backend (FastAPI - optional, services can run standalone):**
```bash
cd backend
uvicorn app.main:app --reload
# Runs on http://localhost:8000
```

## Usage Workflow

### 1. Fetch Business Data

1. Go to `/businesses` page
2. Enter business name, phone, or Google Places URL
3. Click "Fetch" to retrieve business data from Google Places API

### 2. Generate Website

1. Click "Generate Website" on a business
2. Select AI copy style (Formal/Friendly/Marketing/Minimalist)
3. System generates Next.js + Tailwind template with:
   - AI-generated copy
   - Color palette based on business type
   - Responsive design
   - Contact forms

### 3. Deploy to Vercel

1. System automatically:
   - Initializes Git repo
   - Pushes to GitHub (if repo URL provided)
   - Deploys to Vercel
   - Takes homepage screenshot
   - Updates deployment status

### 4. Client Outreach

1. Add client email addresses
2. System sends personalized emails with:
   - Live preview URL
   - Screenshot
   - Custom message
3. Tracks engagement:
   - Email opens
   - Link clicks
   - Time on page

### 5. Form Submission

1. Upload CSV of domains
2. System automatically:
   - Detects contact forms
   - Fills with business-specific message
   - Solves CAPTCHAs
   - Submits forms
   - Logs all results

## Production Deployment

### Vercel (Frontend)

1. Connect GitHub repository
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push

### Render/Railway (Backend)

1. Create new service
2. Set build command: `pip install -r requirements.txt && playwright install chromium`
3. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables

### Database

Use managed PostgreSQL:
- Vercel Postgres
- Supabase
- Railway PostgreSQL
- Render PostgreSQL

## API Endpoints

### Businesses
- `GET /api/businesses` - List all businesses
- `POST /api/businesses/fetch` - Fetch from Google Places
- `POST /api/businesses/generate-website` - Generate website template
- `POST /api/businesses/deploy` - Deploy to Vercel
- `POST /api/businesses/screenshot` - Take screenshot
- `POST /api/businesses/send-email` - Send client email

### Deployments
- `GET /api/deployments` - List all deployments

### Clients
- `GET /api/clients` - List all clients with stats

## Python Services

All Python services can be run standalone:

```bash
# Google Places
python backend/app/services/google_places_service.py --input "Business Name" --type name

# Website Generator
python backend/app/services/website_generator.py --business-data '{"name":"..."}' --style friendly

# Vercel Deploy
python backend/app/services/vercel_deploy.py --template-path /path/to/template

# Screenshot
python backend/app/services/screenshot_service.py --url https://example.com

# Email
python backend/app/services/email_service.py --to client@example.com --business-name "Business" --preview-url https://...
```

## Troubleshooting

### Database Connection Issues
- Check `DATABASE_URL` format
- Ensure PostgreSQL is running
- Verify network access

### Python Services Not Found
- Ensure Python scripts are executable: `chmod +x backend/app/services/*.py`
- Check Python path in API routes

### Vercel Deployment Fails
- Verify `VERCEL_TOKEN` is valid
- Check Vercel CLI is installed: `npm i -g vercel`
- Ensure project has valid `package.json`

### Email Not Sending
- Verify SMTP credentials
- Check firewall/network restrictions
- Test with `python backend/app/services/email_service.py` directly

## Security Notes

- Never commit `.env.local` or `.env` files
- Use environment variables for all secrets
- Enable 2FA on all service accounts
- Use strong database passwords
- Regularly rotate API keys

## Support

For issues or questions, check:
- Logs in `/logs` dashboard page
- Python service stderr output
- Vercel deployment logs
- Database query logs

