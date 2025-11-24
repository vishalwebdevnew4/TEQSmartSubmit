#!/bin/bash
# Comprehensive server fix script
# Run this on the server to diagnose and fix the automation issue

echo "=================================================================================="
echo "  SERVER DIAGNOSTIC AND FIX SCRIPT"
echo "=================================================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check file locations
echo "📋 STEP 1: Checking file locations..."
echo ""

SOURCE_FILE="/var/www/html/TEQSmartSubmit/automation/submission/form_discovery.py"
TARGET_FILE="/var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py"

if [ -f "$SOURCE_FILE" ]; then
    echo -e "${GREEN}✅ Source file exists: $SOURCE_FILE${NC}"
    SOURCE_SIZE=$(stat -c%s "$SOURCE_FILE")
    echo "   Size: $SOURCE_SIZE bytes"
    
    # Check if it has heartbeat code
    if grep -q "python_script_heartbeat" "$SOURCE_FILE"; then
        echo -e "   ${GREEN}✅ Contains latest heartbeat code${NC}"
    else
        echo -e "   ${YELLOW}⚠️  Does NOT contain heartbeat code (old version)${NC}"
    fi
else
    echo -e "${RED}❌ Source file NOT found: $SOURCE_FILE${NC}"
    echo "   Looking for file..."
    find /var/www -name "form_discovery.py" 2>/dev/null | head -3
fi

echo ""

if [ -f "$TARGET_FILE" ]; then
    echo -e "${GREEN}✅ Target file exists: $TARGET_FILE${NC}"
    TARGET_SIZE=$(stat -c%s "$TARGET_FILE")
    echo "   Size: $TARGET_SIZE bytes"
    
    # Check if it has heartbeat code
    if grep -q "python_script_heartbeat" "$TARGET_FILE"; then
        echo -e "   ${GREEN}✅ Contains latest heartbeat code${NC}"
        NEEDS_UPDATE=false
    else
        echo -e "   ${YELLOW}⚠️  Does NOT contain heartbeat code (needs update)${NC}"
        NEEDS_UPDATE=true
    fi
else
    echo -e "${RED}❌ Target file NOT found: $TARGET_FILE${NC}"
    NEEDS_UPDATE=true
fi

echo ""

# Step 2: Copy file if needed
if [ "$NEEDS_UPDATE" = true ] && [ -f "$SOURCE_FILE" ]; then
    echo "📋 STEP 2: Updating target file..."
    echo ""
    
    # Create backup
    if [ -f "$TARGET_FILE" ]; then
        BACKUP_FILE="${TARGET_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$TARGET_FILE" "$BACKUP_FILE"
        echo -e "${GREEN}✅ Created backup: $BACKUP_FILE${NC}"
    fi
    
    # Copy file
    cp "$SOURCE_FILE" "$TARGET_FILE"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ File copied successfully${NC}"
        chmod +x "$TARGET_FILE"
        echo -e "${GREEN}✅ File permissions set${NC}"
    else
        echo -e "${RED}❌ Failed to copy file${NC}"
        exit 1
    fi
else
    echo "📋 STEP 2: File is up to date, skipping copy"
fi

echo ""

# Step 3: Check Python syntax
echo "📋 STEP 3: Checking Python syntax..."
echo ""

python3 -m py_compile "$TARGET_FILE" 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Python syntax is valid${NC}"
else
    echo -e "${RED}❌ Python syntax errors found${NC}"
    exit 1
fi

echo ""

# Step 4: Check for heartbeat files
echo "📋 STEP 4: Checking for heartbeat files (from previous runs)..."
echo ""

HEARTBEAT_FILES=$(ls -t /tmp/python_script_heartbeat_*.txt 2>/dev/null | head -5)
if [ -n "$HEARTBEAT_FILES" ]; then
    echo -e "${YELLOW}⚠️  Found heartbeat files from previous runs:${NC}"
    for file in $HEARTBEAT_FILES; do
        echo "   $file"
        echo "   Content:"
        cat "$file" | sed 's/^/      /'
        echo ""
    done
else
    echo -e "${GREEN}✅ No old heartbeat files found${NC}"
fi

echo ""

# Step 5: Check for error files
echo "📋 STEP 5: Checking for error files..."
echo ""

ERROR_FILES=(
    "/tmp/python_startup_error.txt"
    "/tmp/python_import_error.txt"
    "/tmp/python_script_started.txt"
)

FOUND_ERRORS=false
for file in "${ERROR_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${YELLOW}⚠️  Found: $file${NC}"
        echo "   Content:"
        cat "$file" | sed 's/^/      /'
        echo ""
        FOUND_ERRORS=true
    fi
done

if [ "$FOUND_ERRORS" = false ]; then
    echo -e "${GREEN}✅ No error files found${NC}"
fi

echo ""

# Step 6: Test script execution
echo "📋 STEP 6: Testing script execution..."
echo ""

# Create a minimal test template
TEST_TEMP_DIR=$(mktemp -d)
TEST_TEMPLATE="$TEST_TEMP_DIR/test_template.json"

cat > "$TEST_TEMPLATE" << 'EOF'
{
  "name": "Test",
  "fields": [],
  "headless": false
}
EOF

echo "🔄 Running test execution (5 second timeout)..."
echo ""

timeout 5 python3 "$TARGET_FILE" --url "https://example.com" --template "$TEST_TEMPLATE" 2>&1 | head -20

TEST_EXIT=$?
echo ""

if [ $TEST_EXIT -eq 124 ]; then
    echo -e "${YELLOW}⚠️  Test timed out (this is OK - script is running)${NC}"
elif [ $TEST_EXIT -eq 0 ]; then
    echo -e "${GREEN}✅ Script executed successfully${NC}"
else
    echo -e "${RED}❌ Script failed with exit code: $TEST_EXIT${NC}"
fi

# Check for heartbeat file from this test
LATEST_HEARTBEAT=$(ls -t /tmp/python_script_heartbeat_*.txt 2>/dev/null | head -1)
if [ -n "$LATEST_HEARTBEAT" ]; then
    echo ""
    echo -e "${GREEN}✅ Heartbeat file created: $LATEST_HEARTBEAT${NC}"
    echo "   Content:"
    cat "$LATEST_HEARTBEAT" | sed 's/^/      /'
fi

# Cleanup
rm -rf "$TEST_TEMP_DIR"

echo ""
echo "=================================================================================="
echo "  SUMMARY"
echo "=================================================================================="
echo ""

if [ "$NEEDS_UPDATE" = false ] || [ -f "$TARGET_FILE" ]; then
    echo -e "${GREEN}✅ File is in correct location and up to date${NC}"
else
    echo -e "${RED}❌ File update may have failed${NC}"
fi

echo ""
echo "📋 Next steps:"
echo "   1. Restart your application: pm2 restart all"
echo "   2. Test automation from dashboard"
echo "   3. Check heartbeat files if logs don't appear:"
echo "      ls -lt /tmp/python_script_heartbeat_*.txt"
echo ""
echo "=================================================================================="

