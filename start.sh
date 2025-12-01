#!/bin/bash
# TEQSmartSubmit Startup Script for Linux/Mac

echo "🚀 Starting TEQSmartSubmit..."

# Check if .env.local exists
if [ ! -f .env.local ]; then
    echo "❌ .env.local not found. Please run ./setup.sh first"
    exit 1
fi

# Check if database is configured
if ! grep -q "DATABASE_URL" .env.local; then
    echo "⚠️  DATABASE_URL not found in .env.local"
fi

# Start Next.js dev server
echo ""
echo "🌐 Starting Next.js development server..."
echo "📱 Server will be available at http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev

