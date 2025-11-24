#!/bin/bash
# Script to ensure tmp directory exists and has correct permissions

echo "=================================================================================="
echo "  SETTING UP LOG DIRECTORY"
echo "=================================================================================="
echo ""

LOG_DIR="/var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp"

# Create directory if it doesn't exist
if [ ! -d "$LOG_DIR" ]; then
    echo "📁 Creating log directory: $LOG_DIR"
    mkdir -p "$LOG_DIR"
    if [ $? -eq 0 ]; then
        echo "✅ Directory created"
    else
        echo "❌ Failed to create directory"
        exit 1
    fi
else
    echo "✅ Directory already exists: $LOG_DIR"
fi

# Set permissions
echo ""
echo "🔐 Setting permissions..."
chmod 755 "$LOG_DIR"
if [ $? -eq 0 ]; then
    echo "✅ Permissions set to 755"
else
    echo "⚠️  Could not set permissions (may need sudo)"
fi

# Check if writable
echo ""
echo "🔍 Checking if directory is writable..."
if [ -w "$LOG_DIR" ]; then
    echo "✅ Directory is writable"
else
    echo "❌ Directory is NOT writable"
    echo "   Trying to fix with chmod..."
    chmod 777 "$LOG_DIR" 2>/dev/null
    if [ -w "$LOG_DIR" ]; then
        echo "✅ Fixed - directory is now writable"
    else
        echo "❌ Still not writable - may need to run with sudo"
    fi
fi

# Test write
echo ""
echo "🧪 Testing write access..."
TEST_FILE="$LOG_DIR/test_write_$$.txt"
if touch "$TEST_FILE" 2>/dev/null; then
    echo "✅ Can write to directory"
    rm -f "$TEST_FILE"
else
    echo "❌ Cannot write to directory"
    echo "   Current permissions: $(stat -c%a "$LOG_DIR")"
    echo "   Owner: $(stat -c%U "$LOG_DIR")"
    echo "   Group: $(stat -c%G "$LOG_DIR")"
fi

echo ""
echo "=================================================================================="
echo "  SUMMARY"
echo "=================================================================================="
echo ""
echo "Log directory: $LOG_DIR"
echo "Exists: $([ -d "$LOG_DIR" ] && echo "Yes" || echo "No")"
echo "Writable: $([ -w "$LOG_DIR" ] && echo "Yes" || echo "No")"
echo "Permissions: $(stat -c%a "$LOG_DIR" 2>/dev/null || echo "unknown")"
echo ""
echo "Heartbeat files will be created at:"
echo "  $LOG_DIR/python_script_heartbeat_<PID>.txt"
echo ""
echo "Error files will be created at:"
echo "  $LOG_DIR/python_startup_error.txt"
echo "  $LOG_DIR/python_import_error.txt"
echo ""
echo "=================================================================================="

