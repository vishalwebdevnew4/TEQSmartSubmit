# 🚀 TEQSmartSubmit - Quick Start

## Get Running in 3 Steps

### 1️⃣ Setup (One-time)
```bash
# Windows
.\setup.ps1

# Linux/Mac
chmod +x setup.sh && ./setup.sh
```

### 2️⃣ Configure
Edit `.env.local` with your:
- Database URL
- API keys (Google Places, Vercel, etc.)

### 3️⃣ Start
```bash
# Windows
.\start.ps1

# Linux/Mac
./start.sh

# Or manually
npm run dev
```

## First Time Setup

1. **Create Database**:
   ```bash
   createdb teqsmartsubmit
   ```

2. **Run Migrations**:
   ```bash
   npx prisma migrate dev
   ```

3. **Create Admin User**:
   ```bash
   python create_admin.py admin yourpassword
   ```

4. **Access Dashboard**:
   - Open http://localhost:3000
   - Login with your admin credentials

## What's Included

✅ Google Places API integration  
✅ AI Website Generator  
✅ Automatic Vercel Deployment  
✅ Form Submission Automation  
✅ Client Outreach & Tracking  
✅ Analytics Dashboard  
✅ Template Versioning  
✅ Background Workers  
✅ Error Monitoring  

## Full Documentation

- `QUICK_START.md` - Detailed setup guide
- `DEPLOYMENT_GUIDE.md` - Production deployment
- `SYSTEM_OVERVIEW.md` - Architecture details
- `COMPLETE_SYSTEM_SUMMARY.md` - Feature list

---

**Ready to automate! 🎉**

