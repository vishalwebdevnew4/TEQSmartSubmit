#!/bin/bash
# Deploy form_discovery.py fix using git workflow
# This script pulls latest changes and verifies the fix

set -e

echo "🚀 Deploying form_discovery.py fix using Git..."
echo ""

# Get the current directory (should be /var/www/html/TEQSmartSubmit)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "📍 Current directory: $SCRIPT_DIR"
echo ""

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not a git repository. Please run this from the git repo root."
    exit 1
fi

# Check current branch
CURRENT_BRANCH=$(git branch --show-current)
echo "📍 Current branch: $CURRENT_BRANCH"

# Check if there are uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "⚠️  Warning: You have uncommitted changes"
    echo "   Consider committing or stashing them first"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Pull latest changes
echo ""
echo "📥 Pulling latest changes from git..."
git pull origin "$CURRENT_BRANCH" || {
    echo "❌ Failed to pull from git"
    exit 1
}

echo "✅ Git pull successful"
echo ""

# Verify the fix is in the pulled code
SCRIPT_FILE="automation/submission/form_discovery.py"

if [ ! -f "$SCRIPT_FILE" ]; then
    echo "❌ Script file not found: $SCRIPT_FILE"
    exit 1
fi

echo "🔍 Verifying fix implementation..."
FIXES_FOUND=0

if grep -q "def safe_write" "$SCRIPT_FILE"; then
    echo "✅ safe_write function found"
    FIXES_FOUND=$((FIXES_FOUND + 1))
else
    echo "❌ safe_write function NOT found!"
    exit 1
fi

if grep -q "Only flush if it's a TTY" "$SCRIPT_FILE"; then
    echo "✅ TTY check found (prevents blocking on pipes)"
    FIXES_FOUND=$((FIXES_FOUND + 1))
else
    echo "⚠️  TTY check not found"
fi

if grep -q "safe_write.*Function called" "$SCRIPT_FILE"; then
    echo "✅ safe_write is being used in main_async"
    FIXES_FOUND=$((FIXES_FOUND + 1))
else
    echo "⚠️  safe_write may not be used everywhere"
fi

echo ""
echo "🧪 Running syntax check..."
python3 -m py_compile "$SCRIPT_FILE" 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Script syntax is valid"
else
    echo "❌ Script has syntax errors"
    exit 1
fi

echo ""
echo "✅ Git deployment successful!"
echo ""
echo "📋 Summary:"
echo "  - Latest code pulled from git"
echo "  - Fix verified: $FIXES_FOUND/3 components found"
echo "  - Syntax check: passed"
echo ""

# Check if target location needs updating (if using symlink or separate copy)
TARGET_FILE="/var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py"

if [ -f "$TARGET_FILE" ]; then
    if [ -L "$TARGET_FILE" ]; then
        TARGET_LINK=$(readlink -f "$TARGET_FILE")
        if [ "$TARGET_LINK" = "$(realpath "$SCRIPT_FILE")" ]; then
            echo "✅ Target is already symlinked to current file"
        else
            echo "⚠️  Target is symlinked to different location: $TARGET_LINK"
            echo "   Consider updating the symlink if needed"
        fi
    else
        # Check if files are different
        if ! cmp -s "$SCRIPT_FILE" "$TARGET_FILE"; then
            echo "⚠️  Target file exists and differs from source"
            echo "   Source: $SCRIPT_FILE"
            echo "   Target: $TARGET_FILE"
            echo ""
            read -p "Copy updated file to target location? (y/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                TARGET_DIR=$(dirname "$TARGET_FILE")
                mkdir -p "$TARGET_DIR"
                cp "$SCRIPT_FILE" "$TARGET_FILE"
                echo "✅ File copied to target location"
            fi
        else
            echo "✅ Target file is already up to date"
        fi
    fi
else
    echo "ℹ️  Target file not found: $TARGET_FILE"
    echo "   This is OK if the application uses the file from this location"
fi

echo ""
echo "🎯 Next steps:"
echo "  1. If using a separate target location, ensure it's updated"
echo "  2. Test a real submission through the web interface"
echo "  3. Monitor the submission log to see if it progresses"
echo "  4. Check that it gets past '📍 [main_async] Function called'"
echo ""

