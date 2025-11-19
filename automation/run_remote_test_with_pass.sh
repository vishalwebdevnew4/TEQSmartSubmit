#!/bin/bash
# Script to SSH into remote server with password and run test
# Requires: sshpass (install with: sudo apt-get install sshpass)

PASSWORD="XFho65rfr@uj()7y8"
SERVER="teqsmartsftpuser@teqsmartsubmit.xcelanceweb.com"
PORT="3129"

echo "🔌 Connecting to remote server..."
echo ""

sshpass -p "$PASSWORD" ssh -p $PORT -o StrictHostKeyChecking=no $SERVER << 'ENDSSH'
cd /var/www/html/TEQSmartSubmit/automation
echo "📁 Current directory: $(pwd)"
echo "🚀 Running test script..."
echo ""
python3 test_remote_server.py
ENDSSH

echo ""
echo "✅ Test completed!"

