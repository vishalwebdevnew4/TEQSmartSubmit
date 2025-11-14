#!/bin/bash
# Quick fix script for build issues
# Run this before building

echo "=========================================="
echo "Preparing for Build"
echo "=========================================="

# Step 1: Kill existing database connections
echo "[1/4] Clearing database connections..."
psql -U postgres -d postgres -c "
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'teqsmartsubmit'
  AND pid <> pg_backend_pid();
" 2>/dev/null && echo "✅ Connections cleared" || echo "⚠️  Could not clear connections (may need sudo)"

# Step 2: Clear Next.js build cache
echo "[2/4] Clearing build cache..."
rm -rf .next
echo "✅ Build cache cleared"

# Step 3: Regenerate Prisma client
echo "[3/4] Regenerating Prisma client..."
npx prisma generate
echo "✅ Prisma client regenerated"

# Step 4: Build
echo "[4/4] Building application..."
npm run build

echo ""
echo "=========================================="
if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "=========================================="
else
    echo "❌ Build failed. Check errors above."
    echo "=========================================="
    exit 1
fi

