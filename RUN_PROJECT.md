# 🏃 How to Run the Project

## Method 1: Automated Scripts (Recommended)

### Windows:
```powershell
.\setup.ps1    # One-time setup
.\start.ps1    # Start server
```

### Linux/Mac:
```bash
chmod +x setup.sh start.sh
./setup.sh     # One-time setup
./start.sh     # Start server
```

## Method 2: Manual Steps

### 1. Install Dependencies
```bash
# Node.js
npm install

# Python
pip install -r requirements.txt

# Playwright browsers
python -m playwright install chromium
```

### 2. Configure Environment
```bash
# Copy example (if exists)
cp .env.example .env.local

# Or create manually
# Edit .env.local with your settings
```

### 3. Setup Database
```bash
# Create database
createdb teqsmartsubmit

# Generate Prisma client
npx prisma generate

# Run migrations
npx prisma migrate dev
```

### 4. Create Admin User
```bash
python create_admin.py admin yourpassword
```

### 5. Start Server
```bash
npm run dev
```

## Method 3: Using Docker (Optional)

```bash
# Build
docker-compose build

# Start
docker-compose up
```

## Verification

1. ✅ Server running on http://localhost:3000
2. ✅ No errors in console
3. ✅ Can access login page
4. ✅ Can login with admin credentials

## Common Commands

```bash
# Development
npm run dev              # Start Next.js dev server
npm run build            # Build for production
npm run start            # Start production server

# Database
npx prisma studio        # Open database GUI
npx prisma migrate dev   # Run migrations
npx prisma generate      # Generate Prisma client

# Python services
python create_admin.py admin password  # Create admin
python backend/app/services/google_places_service.py --input "Business" --type name
```

## Next Steps After Running

1. **Login**: http://localhost:3000/login
2. **Dashboard**: http://localhost:3000/dashboard
3. **Fetch Business**: Go to `/businesses`
4. **Generate Website**: Click on a business
5. **Deploy**: Automatic after generation
6. **Track**: View analytics in dashboard

---

**The project is now running! 🎉**

