# 🚀 HOW TO RUN THE PROJECT

## ⚡ Fastest Way (3 Commands)

### Windows:
```powershell
.\setup.ps1
npx prisma migrate dev
.\start.ps1
```

### Linux/Mac:
```bash
chmod +x setup.sh start.sh
./setup.sh
npx prisma migrate dev
./start.sh
```

## 📋 Complete Step-by-Step

### Step 1: Prerequisites
- ✅ Node.js 18+ (`node --version`)
- ✅ Python 3.10+ (`python --version`)
- ✅ PostgreSQL installed and running

### Step 2: Run Setup Script

**Windows:**
```powershell
.\setup.ps1
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

This installs all dependencies automatically.

### Step 3: Configure Environment

Edit `.env.local` (created by setup script):

```env
# REQUIRED: Database
DATABASE_URL=postgresql://user:password@localhost:5432/teqsmartsubmit

# REQUIRED: Security
JWT_SECRET=your-secret-key-here

# Optional but recommended:
GOOGLE_PLACES_API_KEY=your_key
VERCEL_TOKEN=your_token
GITHUB_TOKEN=your_token
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_password
```

### Step 4: Create Database

```bash
# Create PostgreSQL database
createdb teqsmartsubmit

# Or using psql
psql -U postgres
CREATE DATABASE teqsmartsubmit;
\q
```

### Step 5: Run Database Migrations

```bash
# Generate Prisma client
npx prisma generate

# Run migrations
npx prisma migrate dev
```

### Step 6: Create Admin User

```bash
python create_admin.py admin yourpassword
```

### Step 7: Start the Server

**Windows:**
```powershell
.\start.ps1
```

**Linux/Mac:**
```bash
./start.sh
```

**Or manually:**
```bash
npm run dev
```

### Step 8: Access Dashboard

1. Open browser: http://localhost:3000
2. Login with admin credentials
3. Start using the system!

## ✅ Verification Checklist

- [ ] Setup script completed without errors
- [ ] `.env.local` file exists and configured
- [ ] Database created and migrations run
- [ ] Admin user created
- [ ] Server starts on http://localhost:3000
- [ ] Can login to dashboard
- [ ] No errors in console

## 🎯 Quick Test

1. Go to `/businesses`
2. Enter a business name
3. Click "Fetch"
4. See business data appear

## 🐛 Common Issues

### "Cannot find module"
```bash
npm install
pip install -r requirements.txt
```

### "Database connection error"
- Check PostgreSQL is running
- Verify `DATABASE_URL` in `.env.local`
- Ensure database exists

### "Port 3000 in use"
```bash
PORT=3001 npm run dev
```

### "Prisma errors"
```bash
npx prisma generate
npx prisma migrate dev
```

## 📚 More Help

- `START_HERE.md` - Quick start guide
- `QUICK_START.md` - Detailed setup
- `RUN_PROJECT.md` - Alternative methods
- `DEPLOYMENT_GUIDE.md` - Production setup

---

**🎉 You're ready to run!**

