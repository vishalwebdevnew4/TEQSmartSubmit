# Verify Installation and Test

## Step 1: Verify xvfb-run is Available

Run this command:
```bash
which xvfb-run
```

**Expected output:** `/usr/bin/xvfb-run`

If it shows a path, you're all set! ✅

## Step 2: Test Xvfb Works

Test that Xvfb can start a virtual display:
```bash
Xvfb :99 -screen 0 1280x720x24 &
export DISPLAY=:99
echo "DISPLAY is now: $DISPLAY"
# Clean up
killall Xvfb
unset DISPLAY
```

If this runs without errors, Xvfb is working! ✅

## Step 3: Restart Your Application

Restart your Next.js/PM2 application so it picks up the new environment:
```bash
# If using PM2
pm2 restart all

# Or restart your Next.js app however you normally do
```

## Step 4: Test the Automation

1. Go to your dashboard: https://teqsmartsubmit.xcelanceweb.com/
2. Try running an automation on a test domain
3. Check the logs - you should see:
   - ✅ "Found xvfb-run wrapper" OR
   - ✅ "Started Xvfb virtual display"
   - ✅ "Browser launched: chromium"

## What Should Happen Now

The automation will automatically:
1. Detect that Xvfb is available
2. Start a virtual display
3. Launch browser in visible mode
4. Allow CAPTCHA verification

## Troubleshooting

If you still see "Missing X server" errors:
1. Make sure PM2/app is restarted
2. Check logs for "xvfb-run" or "Xvfb" messages
3. Verify the automation code is updated (should be automatic)

## Success Indicators

You'll know it's working when you see in the logs:
- ✅ "Found xvfb-run wrapper" OR
- ✅ "Started Xvfb virtual display: :XX"
- ✅ "Browser launched: chromium"
- ✅ No "Missing X server" errors

