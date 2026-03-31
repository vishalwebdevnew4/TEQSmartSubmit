# Build Fix - Too Many Database Connections

## Problem
Next.js is trying to prerender the dashboard page during build, which opens database connections and exceeds PostgreSQL's limit.

## Immediate Solution

### Step 1: Clear Existing Database Connections

```bash
# Kill idle database connections
psql -U postgres -d teqsmartsubmit -c "
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'teqsmartsubmit'
  AND pid <> pg_backend_pid()
  AND state = 'idle';
"

# Or use the script:
bash fix_database_connections.sh
```

### Step 2: Build Without Static Generation

The dashboard page is now configured as fully dynamic, but Next.js 15 might still try to analyze it during build.

**Option A: Build with ISR disabled (Recommended)**

```bash
# Clear build cache first
rm -rf .next

# Build
npm run build
```

**Option B: Skip the problematic page during build**

Temporarily rename the dashboard page, build, then restore:

```bash
mv src/app/\(dashboard\)/dashboard/page.tsx src/app/\(dashboard\)/dashboard/page.tsx.bak
npm run build
mv src/app/\(dashboard\)/dashboard/page.tsx.bak src/app/\(dashboard\)/dashboard/page.tsx
```

**Option C: Use environment variable to skip database calls during build**

Modify the dashboard page to check for build-time:

```typescript
// In page.tsx
const isBuildTime = process.env.NODE_ENV === 'production' && !process.env.NEXT_RUNTIME;

if (isBuildTime) {
  // Return empty data during build
  return <div>Loading...</div>;
}
```

### Step 3: Alternative - Use Output: 'standalone'

Add to `next.config.ts`:

```typescript
output: 'standalone',
```

This changes how Next.js builds and may avoid the prerendering issue.

## Permanent Solution

### Increase PostgreSQL Connection Limit

```sql
-- Check current limit
SHOW max_connections;

-- Increase limit (requires server restart)
ALTER SYSTEM SET max_connections = 200;

-- Restart PostgreSQL
sudo systemctl restart postgresql
```

### Use Connection Pooling

Update your `DATABASE_URL` to use connection pooling:

```bash
# In .env
# Instead of direct connection:
# DATABASE_URL=postgresql://user:pass@localhost:5432/teqsmartsubmit

# Use with connection limit:
DATABASE_URL=postgresql://user:pass@localhost:5432/teqsmartsubmit?connection_limit=5&pool_timeout=10
```

Or use PgBouncer:

```bash
# Install PgBouncer
sudo apt-get install pgbouncer

# Configure to listen on port 6432
# Update DATABASE_URL to use pgbouncer port
DATABASE_URL=postgresql://user:pass@localhost:6432/teqsmartsubmit
```

## Quick Fix Command

Run this sequence:

```bash
# Clear connections
psql -U postgres -d teqsmartsubmit -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = 'teqsmartsubmit' AND pid <> pg_backend_pid();" 2>/dev/null || true

# Clear build cache
rm -rf .next

# Rebuild
npm run build
```

## Verify Fix

After building, check:

```bash
# Build should complete without errors
npm run build

# Start the app
npm start
# or
pm2 restart all
```

