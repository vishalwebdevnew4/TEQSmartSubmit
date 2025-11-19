# Debugging Logs Not Showing on Remote Server

## Issue
Logs are not displaying on the remote server (https://teqsmartsubmit.xcelanceweb.com/logs) but work locally.

## Possible Causes

### 1. Database Connection Issue
- **Check**: `DATABASE_URL` environment variable is set correctly
- **Check**: Database is accessible from the remote server
- **Check**: Database credentials are correct

### 2. Prisma Client Not Generated
- **Fix**: Run `npx prisma generate` on the remote server
- **Fix**: Run `npx prisma db push` or migrations if schema changed

### 3. API Route Error
- **Check**: Browser console for API errors
- **Check**: Server logs for errors
- **Check**: Network tab in browser dev tools

### 4. CORS or Network Issues
- **Check**: API route is accessible
- **Check**: No firewall blocking database connections

## Debugging Steps

### Step 1: Check Browser Console
1. Open https://teqsmartsubmit.xcelanceweb.com/logs
2. Open browser DevTools (F12)
3. Check Console tab for errors
4. Check Network tab for `/api/logs` request

### Step 2: Check Server Logs
```bash
# On remote server, check Next.js logs
pm2 logs teqsmartsubmit
# or
tail -f /var/log/nextjs.log
```

### Step 3: Test Database Connection
```bash
# SSH to remote server
cd /var/www/html/TEQSmartSubmit

# Test Prisma connection
npx prisma db pull

# Check if logs exist
npx prisma studio
# Then navigate to SubmissionLog table
```

### Step 4: Check Environment Variables
```bash
# On remote server
cd /var/www/html/TEQSmartSubmit
cat .env | grep DATABASE_URL
```

### Step 5: Test API Route Directly
```bash
# On remote server
curl http://localhost:3000/api/logs
# or
curl https://teqsmartsubmit.xcelanceweb.com/api/logs
```

## Quick Fixes

### Fix 1: Regenerate Prisma Client
```bash
cd /var/www/html/TEQSmartSubmit
npx prisma generate
npm run build
pm2 restart teqsmartsubmit
```

### Fix 2: Check Database URL
```bash
# Ensure DATABASE_URL is set in .env
echo $DATABASE_URL

# Should be something like:
# postgresql://user:password@host:port/database
```

### Fix 3: Enable Debug Logging
Add to `.env`:
```
DEBUG_LOGS=true
NODE_ENV=development
```

Then check server logs for detailed error messages.

## Common Issues

### Issue: "Can't reach database server"
- **Cause**: Database not accessible from remote server
- **Fix**: Check database firewall rules, ensure database allows connections from server IP

### Issue: "Table 'submission_logs' doesn't exist"
- **Cause**: Database schema not migrated
- **Fix**: Run `npx prisma migrate deploy` or `npx prisma db push`

### Issue: "Prisma Client not generated"
- **Cause**: Prisma client not generated after schema changes
- **Fix**: Run `npx prisma generate`

### Issue: "Connection timeout"
- **Cause**: Database server not responding
- **Fix**: Check database server status, network connectivity

## Testing the Fix

After applying fixes:
1. Restart the Next.js app: `pm2 restart teqsmartsubmit`
2. Clear browser cache
3. Refresh the logs page
4. Check browser console for errors
5. Check server logs for database queries

## Enhanced Error Messages

The updated code now:
- ✅ Tests database connection before querying
- ✅ Returns detailed error messages
- ✅ Logs errors to console (server-side)
- ✅ Shows user-friendly error messages (client-side)
- ✅ Includes error type in response

Check the browser console and server logs for specific error messages.

