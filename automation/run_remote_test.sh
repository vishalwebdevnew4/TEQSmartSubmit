#!/bin/bash
# Script to SSH into remote server and run the test

echo "Connecting to remote server and running test..."
echo ""

ssh -p 3129 teqsmartsftpuser@teqsmartsubmit.xcelanceweb.com << 'ENDSSH'
cd /var/www/html/TEQSmartSubmit/automation
echo "Current directory: $(pwd)"
echo "Running test script..."
echo ""
python3 test_remote_server.py
ENDSSH

echo ""
echo "Test completed!"

