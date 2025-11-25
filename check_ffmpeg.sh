#!/bin/bash
# Quick script to check ffmpeg/ffprobe availability

echo "🔍 Checking ffmpeg/ffprobe availability..."
echo ""

# Check PATH
echo "📋 Current PATH:"
echo "$PATH"
echo ""

# Check for ffmpeg
echo "🔍 Checking for ffmpeg..."
if command -v ffmpeg &> /dev/null; then
    FFMPEG_PATH=$(command -v ffmpeg)
    echo "✅ ffmpeg found: $FFMPEG_PATH"
    ffmpeg -version | head -1
else
    echo "❌ ffmpeg NOT found in PATH"
    echo "   Trying common locations..."
    for path in /usr/bin/ffmpeg /usr/local/bin/ffmpeg /opt/ffmpeg/bin/ffmpeg; do
        if [ -f "$path" ]; then
            echo "   ✅ Found at: $path"
        fi
    done
fi
echo ""

# Check for ffprobe
echo "🔍 Checking for ffprobe..."
if command -v ffprobe &> /dev/null; then
    FFPROBE_PATH=$(command -v ffprobe)
    echo "✅ ffprobe found: $FFPROBE_PATH"
    ffprobe -version | head -1
else
    echo "❌ ffprobe NOT found in PATH"
    echo "   Trying common locations..."
    for path in /usr/bin/ffprobe /usr/local/bin/ffprobe /opt/ffmpeg/bin/ffprobe; do
        if [ -f "$path" ]; then
            echo "   ✅ Found at: $path"
        fi
    done
fi
echo ""

# Test Python's ability to find them
echo "🐍 Testing Python's ability to find ffmpeg/ffprobe..."
python3 << 'EOF'
import shutil
import subprocess

print("Checking with shutil.which()...")
ffmpeg_path = shutil.which('ffmpeg')
ffprobe_path = shutil.which('ffprobe')

if ffmpeg_path:
    print(f"✅ Python found ffmpeg: {ffmpeg_path}")
else:
    print("❌ Python could NOT find ffmpeg in PATH")

if ffprobe_path:
    print(f"✅ Python found ffprobe: {ffprobe_path}")
else:
    print("❌ Python could NOT find ffprobe in PATH")

# Try to run them
if ffmpeg_path:
    try:
        result = subprocess.run([ffmpeg_path, '-version'], capture_output=True, timeout=2, text=True)
        if result.returncode == 0:
            print("✅ ffmpeg is executable")
        else:
            print(f"⚠️  ffmpeg returned non-zero exit code: {result.returncode}")
    except Exception as e:
        print(f"⚠️  Error running ffmpeg: {e}")

if ffprobe_path:
    try:
        result = subprocess.run([ffprobe_path, '-version'], capture_output=True, timeout=2, text=True)
        if result.returncode == 0:
            print("✅ ffprobe is executable")
        else:
            print(f"⚠️  ffprobe returned non-zero exit code: {result.returncode}")
    except Exception as e:
        print(f"⚠️  Error running ffprobe: {e}")
EOF

echo ""
echo "💡 If ffmpeg/ffprobe are not found:"
echo "   1. Install: sudo apt-get update && sudo apt-get install -y ffmpeg"
echo "   2. Verify: which ffmpeg && which ffprobe"
echo "   3. If installed but not in PATH, add to PATH or create symlinks"
echo "   4. Restart the application/service to pick up PATH changes"

