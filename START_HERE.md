# 🚀 START HERE - Get TEQSmartSubmit Running

## ⚡ Quick Start (3 Commands)

### Windows PowerShell:
```powershell
# 1. Setup (one-time)
.\setup.ps1

# 2. Configure database in .env.local
# Edit .env.local and add your DATABASE_URL

# 3. Run migrations
npx prisma migrate dev

# 4. Create admin user
python create_admin.py admin yourpassword

# 5. Start server
.\start.ps1
```

### Linux/Mac:
```bash
# 1. Setup (one-time)
chmod +x setup.sh start.sh
./setup.sh

# 2. Configure database in .env.local
# Edit .env.local and add your DATABASE_URL

# 3. Run migrations
npx prisma migrate dev

# 4. Create admin user
python create_admin.py admin yourpassword

# 5. Start server
./start.sh
```

## 📋 Prerequisites Checklist

- [ ] Node.js 18+ installed (`node --version`)
- [ ] Python 3.10+ installed (`python --version`)
- [ ] PostgreSQL installed and running
- [ ] Database created: `createdb teqsmartsubmit`

## 🔧 Configuration

### Required Environment Variables

Edit `.env.local` (created by setup script):

```env
# Database (REQUIRED)
DATABASE_URL=postgresql://user:password@localhost:5432/teqsmartsubmit

# Google Places API (for business fetching)
GOOGLE_PLACES_API_KEY=your_key_here

# Vercel (for deployments)
VERCEL_TOKEN=your_token_here
GITHUB_TOKEN=your_token_here

# Email (for client outreach)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Security
JWT_SECRET=change-this-secret-key-in-production
```

## 🗄️ Database Setup

1. **Create Database**:
   ```bash
   # PostgreSQL
   createdb teqsmartsubmit
   
   # Or using psql
   psql -U postgres
   CREATE DATABASE teqsmartsubmit;
   \q
   ```

2. **Run Migrations**:
   ```bash
   npx prisma generate
   npx prisma migrate dev
   ```

3. **Create Admin User**:
   ```bash
   python create_admin.py admin yourpassword
   ```

## 🎯 Start the Application

### Development Mode:
```bash
npm run dev
```

Server will start at: **http://localhost:3000**

### Access Dashboard:
1. Open http://localhost:3000
2. Login with admin credentials
3. Start using the system!

## 🧪 Test the System

1. **Fetch Business**: Go to `/businesses` → Enter business name → Click "Fetch"
2. **Generate Website**: Click "Generate Website" on a business
3. **View Dashboard**: Check `/dashboard` for overview
4. **Check Analytics**: Visit `/analytics` for charts

## 🐛 Troubleshooting

### "Database connection error"
- ✅ Check PostgreSQL is running: `pg_isready` (Linux/Mac) or check Services (Windows)
- ✅ Verify `DATABASE_URL` in `.env.local`
- ✅ Ensure database exists: `psql -l | grep teqsmartsubmit`

### "Module not found"
- ✅ Run `npm install` again
- ✅ Run `pip install -r requirements.txt` again

### "Prisma errors"
- ✅ Run `npx prisma generate`
- ✅ Check `DATABASE_URL` is correct

### "Port 3000 already in use"
- ✅ Change port: `PORT=3001 npm run dev`
- ✅ Or kill process using port 3000

## 📚 Documentation

- `QUICK_START.md` - Detailed setup guide
- `DEPLOYMENT_GUIDE.md` - Production deployment
- `SYSTEM_OVERVIEW.md` - Architecture
- `COMPLETE_SYSTEM_SUMMARY.md` - All features

## ✅ Success Checklist

- [ ] Setup script completed
- [ ] `.env.local` configured
- [ ] Database created and migrated
- [ ] Admin user created
- [ ] Server starts without errors
- [ ] Can access http://localhost:3000
- [ ] Can login to dashboard

## 🎉 You're Ready!

Once you see the dashboard, you can:
- Fetch businesses from Google Places
- Generate websites automatically
- Deploy to Vercel
- Submit forms to multiple domains
- Send client outreach emails
- Track everything in analytics

**Happy automating! 🚀**

