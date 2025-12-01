# 🚀 Quick Start Guide

Get TEQSmartSubmit running in 5 minutes!

## Prerequisites

- **Node.js 18+** - [Download](https://nodejs.org)
- **Python 3.10+** - [Download](https://python.org)
- **PostgreSQL** - [Download](https://www.postgresql.org/download/)

## Step 1: Setup

### Windows
```powershell
.\setup.ps1
```

### Linux/Mac
```bash
chmod +x setup.sh
./setup.sh
```

This will:
- ✅ Install all Node.js dependencies
- ✅ Install all Python dependencies
- ✅ Install Playwright browsers
- ✅ Create `.env.local` file

## Step 2: Configure Environment

Edit `.env.local` and add your configuration:

```env
# Database (REQUIRED)
DATABASE_URL=postgresql://user:password@localhost:5432/teqsmartsubmit

# Google Places API (REQUIRED for business fetching)
GOOGLE_PLACES_API_KEY=your_key_here

# Vercel (REQUIRED for deployments)
VERCEL_TOKEN=your_token_here
GITHUB_TOKEN=your_token_here

# Email (REQUIRED for client outreach)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Security
JWT_SECRET=change-this-secret-key-in-production
```

## Step 3: Create Database

```bash
# Create PostgreSQL database
createdb teqsmartsubmit

# Or using psql
psql -U postgres
CREATE DATABASE teqsmartsubmit;
```

## Step 4: Run Migrations

```bash
# Generate Prisma Client
npx prisma generate

# Run migrations
npx prisma migrate dev
```

## Step 5: Start the Server

### Windows
```powershell
.\start.ps1
```

### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

Or manually:
```bash
npm run dev
```

## Step 6: Access the Dashboard

Open your browser and go to:
- **Frontend**: http://localhost:3000
- **Login**: Use your admin credentials (create one if needed)

## Create Admin User

If you don't have an admin user yet:

```bash
# Using Python script
python create_admin.py admin yourpassword

# Or using Prisma Studio
npx prisma studio
```

## Optional: Start Backend Services

### FastAPI Backend (Optional)
```bash
cd backend
uvicorn app.main:app --reload
```

### Celery Worker (Optional, for background tasks)
```bash
celery -A backend.app.services.celery_worker worker --loglevel=info
```

## Troubleshooting

### Database Connection Error
- Check PostgreSQL is running: `pg_isready`
- Verify `DATABASE_URL` in `.env.local`
- Ensure database exists: `psql -l | grep teqsmartsubmit`

### Port Already in Use
- Change port: `PORT=3001 npm run dev`
- Or kill process: `lsof -ti:3000 | xargs kill` (Mac/Linux)

### Python Services Not Found
- Ensure Python is in PATH: `python --version`
- Install dependencies: `pip install -r requirements.txt`

### Prisma Errors
- Regenerate client: `npx prisma generate`
- Reset database: `npx prisma migrate reset` (⚠️ deletes data)

## Next Steps

1. **Fetch a Business**: Go to `/businesses` and enter a business name
2. **Generate Website**: Click "Generate Website" on a business
3. **Deploy**: System will automatically deploy to Vercel
4. **Track**: Monitor everything in the dashboard

## Need Help?

- Check `DEPLOYMENT_GUIDE.md` for detailed setup
- Check `SYSTEM_OVERVIEW.md` for architecture
- Check logs in `/logs` dashboard page

---

**🎉 You're all set! Happy automating!**
