#!/bin/bash
# Quick deploy the non-blocking fix

REPO_DIR="${1:-$HOME/TEQSmartSubmit}"
TARGET_FILE="/var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py"

echo "🚀 Deploying non-blocking fix..."
echo ""

# Find source file
if [ -f "$REPO_DIR/automation/submission/form_discovery.py" ]; then
    SOURCE_FILE="$REPO_DIR/automation/submission/form_discovery.py"
elif [ -f "./automation/submission/form_discovery.py" ]; then
    SOURCE_FILE="./automation/submission/form_discovery.py"
else
    SOURCE_FILE=$(find ~ /var/www -name "form_discovery.py" -path "*/automation/submission/*" 2>/dev/null | head -1)
fi

if [ -z "$SOURCE_FILE" ] || [ ! -f "$SOURCE_FILE" ]; then
    echo "❌ Source file not found"
    echo "   Run: git pull origin main"
    exit 1
fi

echo "✅ Source: $SOURCE_FILE"

# Check if fix is present
if ! grep -q "select.select" "$SOURCE_FILE"; then
    echo "❌ Fix not found in source file"
    echo "   Make sure you pulled latest: git pull origin main"
    exit 1
fi

echo "✅ Fix verified in source"

# Copy to target
TARGET_DIR=$(dirname "$TARGET_FILE")
mkdir -p "$TARGET_DIR"
cp "$SOURCE_FILE" "$TARGET_FILE"

echo "✅ Copied to: $TARGET_FILE"

# Verify
if grep -q "select.select" "$TARGET_FILE"; then
    echo "✅ Fix verified in target file"
    echo ""
    echo "🎉 DEPLOYED! The script should no longer hang."
    echo "   Test a submission now!"
else
    echo "❌ Fix not found in target - deployment may have failed"
    exit 1
fi

