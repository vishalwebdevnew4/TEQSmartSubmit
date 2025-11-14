#!/bin/bash
# Script to fix database connection issues
# This kills idle connections and resets the connection pool

echo "Fixing database connections..."

# Connect to PostgreSQL and kill idle connections
psql -U postgres -d teqsmartsubmit -c "
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'teqsmartsubmit'
  AND pid <> pg_backend_pid()
  AND state = 'idle'
  AND state_change < now() - interval '5 seconds';
" 2>/dev/null || echo "Could not kill idle connections (may require sudo)"

# Kill all connections to the database (more aggressive)
psql -U postgres -d postgres -c "
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'teqsmartsubmit'
  AND pid <> pg_backend_pid();
" 2>/dev/null || echo "Could not kill all connections (may require sudo)"

echo "Database connections cleared. You can now retry the build."

