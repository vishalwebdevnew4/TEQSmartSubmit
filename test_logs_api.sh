#!/bin/bash
# Diagnostic script to test logs API on remote server

echo "================================================================================"
echo "Testing Logs API on Remote Server"
echo "================================================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the project directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: Must run from project root directory${NC}"
    exit 1
fi

echo "1. Checking environment variables..."
if [ -f ".env" ]; then
    if grep -q "DATABASE_URL" .env; then
        echo -e "${GREEN}✅ DATABASE_URL found in .env${NC}"
        DB_URL=$(grep "DATABASE_URL" .env | cut -d '=' -f2- | head -c 50)
        echo "   Preview: ${DB_URL}..."
    else
        echo -e "${RED}❌ DATABASE_URL not found in .env${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  .env file not found${NC}"
fi

echo ""
echo "2. Checking Prisma client..."
if [ -d "node_modules/.prisma/client" ]; then
    echo -e "${GREEN}✅ Prisma client exists${NC}"
else
    echo -e "${YELLOW}⚠️  Prisma client not found - run 'npx prisma generate'${NC}"
fi

echo ""
echo "3. Testing database connection..."
if command -v psql &> /dev/null; then
    DB_URL=$(grep "DATABASE_URL" .env 2>/dev/null | cut -d '=' -f2-)
    if [ -n "$DB_URL" ]; then
        # Extract connection details (simplified)
        echo "   Attempting to connect to database..."
        # Note: This is a simplified check - actual connection test would need proper parsing
        echo -e "${YELLOW}   ℹ️  Use 'npx prisma db pull' to test connection${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  psql not available - skipping direct DB test${NC}"
fi

echo ""
echo "4. Testing Prisma schema..."
if [ -f "prisma/schema.prisma" ]; then
    echo -e "${GREEN}✅ Prisma schema found${NC}"
    if grep -q "model SubmissionLog" prisma/schema.prisma; then
        echo -e "${GREEN}✅ SubmissionLog model found${NC}"
    else
        echo -e "${RED}❌ SubmissionLog model not found${NC}"
    fi
else
    echo -e "${RED}❌ Prisma schema not found${NC}"
fi

echo ""
echo "5. Checking Next.js API route..."
if [ -f "src/app/api/logs/route.ts" ]; then
    echo -e "${GREEN}✅ Logs API route exists${NC}"
else
    echo -e "${RED}❌ Logs API route not found${NC}"
fi

echo ""
echo "6. Testing API endpoint (if server is running)..."
if curl -s http://localhost:3000/api/logs > /dev/null 2>&1; then
    echo -e "${GREEN}✅ API endpoint is accessible${NC}"
    echo "   Response:"
    curl -s http://localhost:3000/api/logs | head -c 200
    echo ""
else
    echo -e "${YELLOW}⚠️  API endpoint not accessible (server may not be running)${NC}"
    echo "   Try: curl http://localhost:3000/api/logs"
fi

echo ""
echo "================================================================================"
echo "Quick Fixes to Try:"
echo "================================================================================"
echo ""
echo "1. Regenerate Prisma client:"
echo "   npx prisma generate"
echo ""
echo "2. Test database connection:"
echo "   npx prisma db pull"
echo ""
echo "3. Check database migrations:"
echo "   npx prisma migrate status"
echo ""
echo "4. Restart Next.js server:"
echo "   pm2 restart teqsmartsubmit"
echo "   # or"
echo "   npm run dev"
echo ""
echo "5. Check server logs:"
echo "   pm2 logs teqsmartsubmit"
echo "   # or check browser console for errors"
echo ""
echo "6. Enable debug logging:"
echo "   Add to .env: DEBUG_LOGS=true"
echo "   Then restart server"
echo ""

