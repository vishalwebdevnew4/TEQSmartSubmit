# Troubleshooting - Application Not Opening

## Issue: Nothing Opens When Running `python run.py`

### Possible Causes

1. **Tkinter Display Issue** - Windows might be opening off-screen or behind other windows
2. **Database Connection Blocking** - Application might be waiting for database connection
3. **Event Loop Issue** - Tkinter event loop might not be starting

### Quick Tests

**Test 1: Check if Tkinter works**
```powershell
python test_tkinter.py
```
You should see a small test window. If not, there's a display issue.

**Test 2: Simple login test**
```powershell
python test_simple_login.py
```
This tests the login dialog without database.

**Test 3: Step-by-step test**
```powershell
python run_simple.py
```
This will test each step and show where it fails.

### Solutions

**If windows are opening but not visible:**
- Try Alt+Tab to find hidden windows
- Check if windows are on a different monitor
- Try minimizing and restoring windows

**If application hangs:**
- Check database connection: `$env:DATABASE_URL` should be set
- Check if PostgreSQL is running
- Look for error messages in the console

**If nothing appears at all:**
- Verify tkinter is installed: `python -c "import tkinter; print('OK')"`
- Check if you're running in a headless environment (no display)
- Try running from a different terminal

### Manual Check

1. Run with verbose output:
   ```powershell
   python run.py
   ```
   Look for messages like "Login dialog should be visible now"

2. Check if process is running:
   ```powershell
   Get-Process python
   ```

3. Try the simple test:
   ```powershell
   python test_tkinter.py
   ```

### Alternative: Run Without GUI

If GUI doesn't work, you can still use the backend API directly or create a simpler interface.


