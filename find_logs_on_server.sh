#!/bin/bash
# Comprehensive script to find all log files and check script status on server

echo "=================================================================================="
echo "  FINDING LOG FILES AND CHECKING SCRIPT STATUS"
echo "=================================================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Find all possible script locations
echo "📋 STEP 1: Finding script locations..."
echo ""

SCRIPT_LOCATIONS=(
    "/var/www/projects/teqsmartsubmit/teqsmartsubmit/automation/submission/form_discovery.py"
    "/var/www/html/TEQSmartSubmit/automation/submission/form_discovery.py"
    "$(pwd)/automation/submission/form_discovery.py"
    "$HOME/automation/submission/form_discovery.py"
)

FOUND_SCRIPT=""
for location in "${SCRIPT_LOCATIONS[@]}"; do
    if [ -f "$location" ]; then
        echo -e "${GREEN}✅ Found script at: $location${NC}"
        FOUND_SCRIPT="$location"
        ls -lh "$location" | awk '{print "   Size:", $5, "Modified:", $6, $7, $8}'
        
        # Check if it has heartbeat code
        if grep -q "python_script_heartbeat" "$location"; then
            echo -e "   ${GREEN}✅ Contains latest heartbeat code${NC}"
        else
            echo -e "   ${YELLOW}⚠️  Does NOT contain heartbeat code (old version)${NC}"
        fi
        echo ""
    else
        echo -e "${RED}❌ Not found: $location${NC}"
    fi
done

if [ -z "$FOUND_SCRIPT" ]; then
    echo -e "${RED}❌ Script not found in any expected location!${NC}"
    echo ""
    echo "Searching entire system..."
    find /var/www -name "form_discovery.py" 2>/dev/null | head -5
    find /home -name "form_discovery.py" 2>/dev/null | head -5
fi

echo ""
echo "=================================================================================="
echo ""

# Step 2: Check for heartbeat files in all possible locations
echo "📋 STEP 2: Checking for heartbeat files..."
echo ""

HEARTBEAT_PATTERNS=(
    "/var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp/python_script_heartbeat_*.txt"
    "/tmp/python_script_heartbeat_*.txt"
    "/tmp/python_script_started.txt"
    "$HOME/python_script_heartbeat_*.txt"
    "/var/tmp/python_script_heartbeat_*.txt"
)

FOUND_HEARTBEAT=false
for pattern in "${HEARTBEAT_PATTERNS[@]}"; do
    FILES=$(ls -t $pattern 2>/dev/null | head -5)
    if [ -n "$FILES" ]; then
        echo -e "${GREEN}✅ Found heartbeat files matching: $pattern${NC}"
        for file in $FILES; do
            echo ""
            echo "   File: $file"
            echo "   Size: $(stat -c%s "$file" 2>/dev/null || echo "unknown") bytes"
            echo "   Modified: $(stat -c%y "$file" 2>/dev/null || echo "unknown")"
            echo "   Content:"
            head -20 "$file" | sed 's/^/      /'
            echo ""
        done
        FOUND_HEARTBEAT=true
    fi
done

if [ "$FOUND_HEARTBEAT" = false ]; then
    echo -e "${YELLOW}⚠️  No heartbeat files found${NC}"
    echo "   This means either:"
    echo "   1. Script hasn't run yet"
    echo "   2. Script is crashing before creating heartbeat"
    echo "   3. Files are in a different location"
fi

echo ""
echo "=================================================================================="
echo ""

# Step 3: Check for error files
echo "📋 STEP 3: Checking for error files..."
echo ""

ERROR_PATTERNS=(
    "/var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp/python_*error*.txt"
    "/tmp/python_startup_error.txt"
    "/tmp/python_import_error.txt"
    "/tmp/python_*error*.txt"
    "$HOME/python_*error*.txt"
)

FOUND_ERRORS=false
for pattern in "${ERROR_PATTERNS[@]}"; do
    FILES=$(ls -t $pattern 2>/dev/null | head -5)
    if [ -n "$FILES" ]; then
        echo -e "${YELLOW}⚠️  Found error files matching: $pattern${NC}"
        for file in $FILES; do
            echo ""
            echo "   File: $file"
            echo "   Content:"
            cat "$file" | sed 's/^/      /'
            echo ""
        done
        FOUND_ERRORS=true
    fi
done

if [ "$FOUND_ERRORS" = false ]; then
    echo -e "${GREEN}✅ No error files found${NC}"
fi

echo ""
echo "=================================================================================="
echo ""

# Step 4: Check running Python processes
echo "📋 STEP 4: Checking running Python processes..."
echo ""

PYTHON_PROCS=$(ps aux | grep -E "form_discovery|python.*automation" | grep -v grep)
if [ -n "$PYTHON_PROCS" ]; then
    echo -e "${GREEN}✅ Found running Python processes:${NC}"
    echo "$PYTHON_PROCS" | while read line; do
        echo "   $line"
    done
    echo ""
    
    # Get PIDs
    PIDS=$(echo "$PYTHON_PROCS" | awk '{print $2}')
    echo "   Checking for heartbeat files for these PIDs:"
    for pid in $PIDS; do
        # Check custom location first
        HEARTBEAT_FILE="/var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp/python_script_heartbeat_${pid}.txt"
        if [ -f "$HEARTBEAT_FILE" ]; then
            echo -e "   ${GREEN}✅ Found heartbeat for PID $pid: $HEARTBEAT_FILE${NC}"
        else
            # Check fallback location
            HEARTBEAT_FILE="/tmp/python_script_heartbeat_${pid}.txt"
            if [ -f "$HEARTBEAT_FILE" ]; then
                echo -e "   ${GREEN}✅ Found heartbeat for PID $pid (fallback): $HEARTBEAT_FILE${NC}"
            else
                echo -e "   ${YELLOW}⚠️  No heartbeat file for PID $pid${NC}"
            fi
        fi
    done
else
    echo -e "${YELLOW}⚠️  No Python automation processes found${NC}"
fi

echo ""
echo "=================================================================================="
echo ""

# Step 5: Check /tmp directory permissions
echo "📋 STEP 5: Checking /tmp directory permissions..."
echo ""

if [ -w "/tmp" ]; then
    echo -e "${GREEN}✅ /tmp is writable${NC}"
    echo "   Permissions: $(stat -c%a /tmp)"
    echo "   Owner: $(stat -c%U /tmp)"
else
    echo -e "${RED}❌ /tmp is NOT writable${NC}"
    echo "   This could prevent heartbeat files from being created!"
fi

# Test write
TEST_FILE="/tmp/test_write_$(whoami)_$$.txt"
if touch "$TEST_FILE" 2>/dev/null; then
    echo -e "${GREEN}✅ Can create files in /tmp${NC}"
    rm -f "$TEST_FILE"
else
    echo -e "${RED}❌ Cannot create files in /tmp${NC}"
    echo "   Error: $(touch "$TEST_FILE" 2>&1)"
fi

echo ""
echo "=================================================================================="
echo ""

# Step 6: Test script directly (if found)
if [ -n "$FOUND_SCRIPT" ]; then
    echo "📋 STEP 6: Testing script directly (5 second timeout)..."
    echo ""
    
    # Create test template
    TEST_TEMP_DIR=$(mktemp -d)
    TEST_TEMPLATE="$TEST_TEMP_DIR/test_template.json"
    
    cat > "$TEST_TEMPLATE" << 'EOF'
{
  "name": "Test",
  "fields": [],
  "headless": false
}
EOF
    
    echo "🔄 Running: python3 $FOUND_SCRIPT --url https://example.com --template $TEST_TEMPLATE"
    echo ""
    
    timeout 10 python3 "$FOUND_SCRIPT" --url "https://example.com" --template "$TEST_TEMPLATE" 2>&1 | head -30
    
    TEST_EXIT=$?
    echo ""
    
    if [ $TEST_EXIT -eq 124 ]; then
        echo -e "${YELLOW}⚠️  Test timed out (script is running)${NC}"
    elif [ $TEST_EXIT -eq 0 ]; then
        echo -e "${GREEN}✅ Script executed successfully${NC}"
    else
        echo -e "${RED}❌ Script failed with exit code: $TEST_EXIT${NC}"
    fi
    
    # Check for new heartbeat file
    sleep 1
    # Check custom location first
    LATEST_HEARTBEAT=$(ls -t /var/www/projects/teqsmartsubmit/teqsmartsubmit/tmp/python_script_heartbeat_*.txt 2>/dev/null | head -1)
    if [ -z "$LATEST_HEARTBEAT" ]; then
        # Check fallback location
        LATEST_HEARTBEAT=$(ls -t /tmp/python_script_heartbeat_*.txt 2>/dev/null | head -1)
    fi
    if [ -n "$LATEST_HEARTBEAT" ]; then
        echo ""
        echo -e "${GREEN}✅ New heartbeat file created: $LATEST_HEARTBEAT${NC}"
        echo "   Content:"
        cat "$LATEST_HEARTBEAT" | sed 's/^/      /'
    fi
    
    # Cleanup
    rm -rf "$TEST_TEMP_DIR"
else
    echo "📋 STEP 6: Skipping direct test (script not found)"
fi

echo ""
echo "=================================================================================="
echo "  SUMMARY"
echo "=================================================================================="
echo ""

if [ -n "$FOUND_SCRIPT" ]; then
    echo -e "${GREEN}✅ Script found at: $FOUND_SCRIPT${NC}"
else
    echo -e "${RED}❌ Script NOT found${NC}"
fi

if [ "$FOUND_HEARTBEAT" = true ]; then
    echo -e "${GREEN}✅ Heartbeat files found${NC}"
else
    echo -e "${YELLOW}⚠️  No heartbeat files found${NC}"
fi

echo ""
echo "📋 Next steps:"
echo "   1. If script not found: Copy it to the correct location"
echo "   2. If no heartbeat files: Script may be crashing early"
echo "   3. Run this script again after testing automation"
echo ""
echo "=================================================================================="

