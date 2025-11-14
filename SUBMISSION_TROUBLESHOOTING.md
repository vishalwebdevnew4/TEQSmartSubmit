# ❌ SUBMISSIONS NOT RECEIVED - TROUBLESHOOTING GUIDE

## Summary of Investigation

All core systems are **running and operational**:
- ✅ Node.js/Next.js API server running on port 3000
- ✅ PostgreSQL database running
- ✅ Python 3 and Playwright installed
- ✅ Form website is accessible

**However**: Submissions might not be completing due to:
1. CAPTCHA not being solved
2. Form submission not reaching the backend
3. Backend not recording submissions properly
4. Network/connectivity issues

---

## Root Cause Analysis

### What Should Happen (Complete Flow)

```
1. User fills form → name, email, phone, message
2. CAPTCHA appears (reCAPTCHA v2)
3. CAPTCHA solved (local solver or manual)
4. Form submitted to backend
5. Backend records in database
6. Confirmation shown to user
```

### Likely Issues

#### Issue 1: CAPTCHA Not Being Solved ⚠️
- **Symptom**: Form won't submit, CAPTCHA checkbox unchecked
- **Cause**: Local solver timing out or not working
- **Solution**: Check CAPTCHA solver logs
  ```bash
  grep -i "captcha\|timeout" /tmp/submission*.log 2>/dev/null | tail -20
  ```

#### Issue 2: Form Not Actually Submitting 🔴
- **Symptom**: Form stays filled but doesn't send
- **Cause**: Submit button click not working or form has JS error
- **Solution**: Check browser console
  ```bash
  python3 test_manual_submission.py  # Opens browser to test manually
  ```

#### Issue 3: Backend Not Receiving Data 🔴
- **Symptom**: API called but no submission logged in database
- **Cause**: API endpoint issue or database connection problem
- **Solution**: Check API logs
  ```bash
  npm run dev 2>&1 | grep -i "error\|post\|run" | tail -20
  ```

#### Issue 4: Database Not Recording 📊
- **Symptom**: API says "success" but database empty
- **Cause**: Prisma connection or migration issue
- **Solution**: Run migrations
  ```bash
  npm run db:migrate
  npm run db:push
  ```

---

## Quick Fix Checklist

### Step 1: Verify Services Running
```bash
# Check all services
bash quick_status_check.sh

# Expected output:
# ✅ Node.js/Next.js is running
# ✅ Port 3000 is listening
# ✅ PostgreSQL is running
# ✅ Python 3 is installed
# ✅ Playwright is installed
```

### Step 2: Check Database Connection
```bash
# Test database
psql -U postgres -d teq_smart_submit -c "SELECT COUNT(*) FROM SubmissionLog;"

# If error: run migrations
cd /var/www/html/TEQSmartSubmit
npm run db:push
```

### Step 3: Test Form Submission Manually
```bash
# Opens browser for interactive test
python3 test_manual_submission.py

# Manual steps:
# 1. Fill form with test data
# 2. Solve CAPTCHA manually
# 3. Submit form
# 4. Check if submission is recorded
```

### Step 4: Check API Response
```bash
# Test API directly
curl -X POST http://localhost:3000/api/run \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://interiordesign.xcelanceweb.com/",
    "template": {
      "fields": [
        {"selector": "input[name=\"name\"]", "value": "Test"},
        {"selector": "input[name=\"email\"]", "value": "test@test.com"},
        {"selector": "input[name=\"phone\"]", "value": "123456"},
        {"selector": "textarea[name=\"comment\"]", "value": "Test"}
      ],
      "use_local_captcha_solver": true
    }
  }' -w "\nStatus: %{http_code}\n"

# Expected response: JSON with status and submission ID
```

### Step 5: Check Logs
```bash
# Python automation logs
python3 -u /var/www/html/TEQSmartSubmit/automation/run_submission.py \
  --url "https://interiordesign.xcelanceweb.com/" \
  --template /path/to/template.json 2>&1 | tail -50

# Frontend logs
npm run dev 2>&1 | head -100
```

---

## Specific Fixes by Symptom

### Symptom: "No network connection"

**Solution 1: Restart frontend**
```bash
cd /var/www/html/TEQSmartSubmit
pkill -f "next.*dev|node.*dev"
npm run dev
```

**Solution 2: Check ports**
```bash
# See what's using port 3000
lsof -i :3000
# or
ss -tuln | grep 3000
```

### Symptom: "Submissions in database but form shows error"

**Solution: Check submission status**
```bash
# Query recent submissions
psql -U postgres -d teq_smart_submit -c \
  "SELECT id, status, message, createdAt FROM SubmissionLog ORDER BY createdAt DESC LIMIT 5;"
```

### Symptom: "Form submits but nothing happens"

**Solution 1: Check CAPTCHA is being solved**
```bash
# Look for CAPTCHA logs
grep -r "CAPTCHA\|captcha" /var/log/syslog 2>/dev/null | tail -10
```

**Solution 2: Check form submission in browser**
```bash
# Open browser and watch network tab
python3 test_manual_submission.py

# Look for:
# - Form POST request
# - Response status (should be 200)
# - Response body (should have submission ID)
```

### Symptom: "Playwright timeout"

**Solution: Reinstall Playwright browsers**
```bash
python3 -m playwright install
python3 -m playwright install-deps
```

---

## Configuration Changes to Try

### 1. Increase Timeout
Edit `automation/run_submission.py` and increase timeout values:
```python
# Around line 29
page.set_default_navigation_timeout(60000)  # 60 seconds
page.set_default_timeout(60000)
```

### 2. Add Debug Logging
Edit `src/app/api/run/route.ts` and add:
```typescript
console.log('API /run called with:', { url, template });
console.log('Python script output:', stdout);
console.log('Python script error:', stderr);
```

### 3. Verify Database URL
```bash
# Check if set
echo $DATABASE_URL

# If not set, add to .env.local
DATABASE_URL="postgresql://user:password@localhost:5432/teq_smart_submit"
```

---

## Testing Commands

### Complete End-to-End Test
```bash
# 1. Check all services
bash quick_status_check.sh

# 2. Test database
npm run db:push

# 3. Test API
curl -X POST http://localhost:3000/api/run -H "Content-Type: application/json" \
  -d '{"url":"https://interiordesign.xcelanceweb.com/","template":{"use_local_captcha_solver":true}}'

# 4. Test manual form submission
python3 test_manual_submission.py

# 5. Check submissions recorded
psql -U postgres -d teq_smart_submit -c "SELECT * FROM SubmissionLog ORDER BY createdAt DESC LIMIT 1;"
```

### Submission Diagnostic Test
```bash
python3 check_submission_status.py
```

### Form Loading Test
```bash
python3 test_form_loading.py
```

---

## Expected Behavior After Fix

✅ **Successful Submission Flow**
1. Form loads in ~9 seconds
2. All fields fill automatically or manually
3. CAPTCHA detected and solved within 50 seconds
4. Form submitted successfully
5. Confirmation message appears ("Bedankt" or similar)
6. Submission recorded in database within 1 second
7. User can see submission in logs

---

## Next Steps

1. **Run diagnostic test**:
   ```bash
   python3 check_submission_status.py
   ```

2. **Test manual submission**:
   ```bash
   python3 test_manual_submission.py
   ```

3. **Check which step is failing** and refer to "Specific Fixes" section

4. **If still not working**: 
   - Check frontend logs: `npm run dev`
   - Check Python logs: Run automation script directly
   - Check database: Query SubmissionLog table

---

## Support Information

- **Frontend Logs**: `npm run dev`
- **Database**: `psql -U postgres -d teq_smart_submit`
- **Python Script**: `/var/www/html/TEQSmartSubmit/automation/run_submission.py`
- **API Route**: `/src/app/api/run/route.ts`
- **Test Files**:
  - `check_submission_status.py`
  - `test_manual_submission.py`
  - `test_form_loading.py`
  - `quick_status_check.sh`

---

## Summary

**Current Status**: ✅ All infrastructure operational, submissions mechanism requires debugging

**Most Likely Issue**: CAPTCHA solving or form submission not completing

**Next Action**: Run `python3 test_manual_submission.py` to interactively test the submission flow
