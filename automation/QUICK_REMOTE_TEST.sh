#!/bin/bash
# Quick command to test on remote server
# Usage: ./QUICK_REMOTE_TEST.sh

echo "🔌 Connecting to remote server..."
echo ""

ssh -p 3129 teqsmartsftpuser@teqsmartsubmit.xcelanceweb.com "cd /var/www/html/TEQSmartSubmit/automation && python3 test_remote_server.py"

