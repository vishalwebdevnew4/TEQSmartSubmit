#!/bin/bash
# TEQSmartSubmit Setup Script for Linux/Mac

echo "🚀 Setting up TEQSmartSubmit..."

# Check Node.js
echo ""
echo "📦 Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+ from https://nodejs.org"
    exit 1
fi
NODE_VERSION=$(node --version)
echo "✅ Node.js $NODE_VERSION found"

# Check Python
echo ""
echo "🐍 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.10+ from https://python.org"
    exit 1
fi
PYTHON_VERSION=$(python3 --version)
echo "✅ $PYTHON_VERSION found"

# Install Node.js dependencies
echo ""
echo "📦 Installing Node.js dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install Node.js dependencies"
    exit 1
fi
echo "✅ Node.js dependencies installed"

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
python3 -m pip install --upgrade pip
pip3 install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi
echo "✅ Python dependencies installed"

# Install Playwright browsers
echo ""
echo "🌐 Installing Playwright browsers..."
python3 -m playwright install chromium
if [ $? -ne 0 ]; then
    echo "⚠️  Playwright browser installation failed (optional)"
fi

# Setup environment file
echo ""
echo "⚙️  Setting up environment..."
if [ ! -f .env.local ]; then
    if [ -f .env.example ]; then
        cp .env.example .env.local
        echo "✅ Created .env.local from .env.example"
        echo "⚠️  Please edit .env.local with your configuration"
    else
        echo "⚠️  .env.example not found. Creating basic .env.local..."
        cat > .env.local << EOF
DATABASE_URL=postgresql://user:password@localhost:5432/teqsmartsubmit
GOOGLE_PLACES_API_KEY=your_key_here
VERCEL_TOKEN=your_token_here
GITHUB_TOKEN=your_token_here
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password
JWT_SECRET=change-this-secret-key-in-production
EOF
        echo "✅ Created basic .env.local"
    fi
else
    echo "✅ .env.local already exists"
fi

# Generate Prisma Client
echo ""
echo "🗄️  Generating Prisma Client..."
npx prisma generate
if [ $? -ne 0 ]; then
    echo "⚠️  Prisma generate failed. Make sure DATABASE_URL is set in .env.local"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "1. Edit .env.local with your configuration"
echo "2. Create PostgreSQL database: createdb teqsmartsubmit"
echo "3. Run migrations: npx prisma migrate dev"
echo "4. Start dev server: npm run dev"
echo ""
echo "🚀 Ready to run!"
