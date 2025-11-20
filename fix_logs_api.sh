#!/bin/bash
# Script to fix /api/logs 404 issue

echo "============================================"
echo "Fixing /api/logs 404 Issue"
echo "============================================"

# 1. Verify route works on localhost
echo ""
echo "Step 1: Testing localhost endpoint..."
curl -s http://localhost:3000/api/logs?limit=3 | python3 -m json.tool | head -10
if [ $? -eq 0 ]; then
    echo "✅ Localhost endpoint works"
else
    echo "❌ Localhost endpoint failed"
fi

# 2. Check PM2 status
echo ""
echo "Step 2: Checking PM2 status..."
pm2 list

# 3. Restart Next.js server
echo ""
echo "Step 3: Restarting Next.js server..."
pm2 restart nextjs
sleep 5

# 4. Test localhost again
echo ""
echo "Step 4: Testing localhost after restart..."
curl -s -o /dev/null -w "Localhost Status: %{http_code}\n" http://localhost:3000/api/logs?limit=3

# 5. Restart Apache
echo ""
echo "Step 5: Restarting Apache..."
sudo systemctl restart apache2
sleep 3

# 6. Test HTTPS endpoint
echo ""
echo "Step 6: Testing HTTPS endpoint..."
curl -s -o /dev/null -w "HTTPS Status: %{http_code}\n" https://teqsmartsubmit.xcelanceweb.com/api/logs?limit=3

# 7. If still 404, show Apache logs
echo ""
echo "Step 7: Checking Apache error logs (last 10 lines)..."
sudo tail -10 /var/log/apache2/error.log

echo ""
echo "============================================"
echo "Done! Check the status codes above."
echo "============================================"

