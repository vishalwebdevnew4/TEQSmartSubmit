# Login Dialog Fix

## Issue
Password field and submit button were not visible in the login dialog.

## Fixes Applied

1. **Increased window size** - Changed from 400x300 to 450x450 to ensure all widgets fit
2. **Improved dialog visibility** - Added `lift()` and `attributes('-topmost')` to ensure dialog appears on top
3. **Fixed main window** - Hide main window initially, only show after successful login
4. **Force widget updates** - Added `update_idletasks()` to ensure all widgets are rendered

## Changes Made

### app/gui/login.py
- Increased dialog size to 450x450
- Added dialog lifting and topmost attributes
- Added error label for better feedback
- Force update after widget creation

### app/gui/main_window.py
- Hide main window initially with `withdraw()`
- Show main window only after successful login with `deiconify()`
- Close application if login is cancelled

## Testing

Run the application:
```powershell
python run.py
```

You should now see:
- ✅ Username field
- ✅ Password field (with dots for password masking)
- ✅ "Sign in" button
- ✅ All fields properly visible and functional

## Login Credentials

- Username: `admin`
- Password: `testpass123` (or the password you set when creating the admin)

