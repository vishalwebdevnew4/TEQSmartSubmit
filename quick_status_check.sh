#!/bin/bash
"""
Quick diagnostics script to identify what's running and what's not
"""

echo "════════════════════════════════════════════════════════════════════════════════"
echo "QUICK SYSTEM STATUS CHECK"
echo "════════════════════════════════════════════════════════════════════════════════"

echo ""
echo "🔍 Checking running services..."
echo ""

# Check if Node.js process is running
if pgrep -f "node.*dev|next" > /dev/null; then
    echo "✅ Node.js/Next.js is running"
    pgrep -f "node.*dev|next" | head -1 | xargs ps -p
else
    echo "❌ Node.js/Next.js is NOT running"
    echo "   Solution: cd /var/www/html/TEQSmartSubmit && npm run dev"
fi

echo ""

# Check if port 3000 is listening
if netstat -tuln 2>/dev/null | grep -q ":3000 "; then
    echo "✅ Port 3000 is listening"
else
    if ss -tuln 2>/dev/null | grep -q ":3000 "; then
        echo "✅ Port 3000 is listening"
    else
        echo "❌ Port 3000 is NOT listening"
    fi
fi

echo ""

# Check PostgreSQL
if pgrep postgres > /dev/null; then
    echo "✅ PostgreSQL is running"
else
    echo "❌ PostgreSQL is NOT running"
    echo "   Solution: Start PostgreSQL service"
fi

echo ""

# Check Python version
python3 --version 2>/dev/null && echo "✅ Python 3 is installed" || echo "❌ Python 3 is NOT installed"

echo ""

# Check Playwright
python3 -c "import playwright" 2>/dev/null && echo "✅ Playwright is installed" || echo "❌ Playwright is NOT installed"

echo ""

# Check if form is accessible
echo "🌐 Testing form accessibility..."
curl -s -m 5 "https://interiordesign.xcelanceweb.com/" > /dev/null && echo "✅ Form website is accessible" || echo "❌ Form website is NOT accessible"

echo ""
echo "════════════════════════════════════════════════════════════════════════════════"
echo "TROUBLESHOOTING GUIDE"
echo "════════════════════════════════════════════════════════════════════════════════"

echo ""
echo "If API is NOT responding:"
echo "  1. Start frontend: cd /var/www/html/TEQSmartSubmit && npm run dev"
echo "  2. Check logs: npm run dev 2>&1 | head -50"
echo ""

echo "If database logs show NO submissions:"
echo "  1. Verify DATABASE_URL is set"
echo "  2. Check database is running: psql -U postgres"
echo "  3. Run migrations: npm run db:migrate"
echo ""

echo "If Python automation fails:"
echo "  1. Install Playwright browsers: python3 -m playwright install"
echo "  2. Check Playwright works: python3 -c 'from playwright.sync_api import sync_playwright; print(sync_playwright())'"
echo ""

echo "If form submissions still fail:"
echo "  1. Check frontend logs for errors"
echo "  2. Check Python automation logs"
echo "  3. Verify form is actually being filled correctly"
echo ""
