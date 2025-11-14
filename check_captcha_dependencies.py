#!/usr/bin/env python3
"""
Check if all dependencies for CAPTCHA resolver are installed.
"""

import sys

def check_dependencies():
    """Check if required dependencies are available."""
    print("=" * 70)
    print("🔍 CHECKING CAPTCHA RESOLVER DEPENDENCIES")
    print("=" * 70)
    
    missing = []
    optional_missing = []
    
    # Required dependencies
    print("\n📦 Required Dependencies:")
    
    try:
        import playwright
        print("   ✅ playwright - OK")
    except ImportError:
        print("   ❌ playwright - MISSING")
        missing.append("playwright")
    
    try:
        import speech_recognition
        print("   ✅ SpeechRecognition - OK")
    except ImportError:
        print("   ❌ SpeechRecognition - MISSING")
        missing.append("SpeechRecognition")
    
    try:
        import pydub
        print("   ✅ pydub - OK")
    except ImportError:
        print("   ❌ pydub - MISSING")
        missing.append("pydub")
    
    # Optional dependencies
    print("\n📦 Optional Dependencies:")
    
    try:
        import ffmpeg
        print("   ✅ ffmpeg-python - OK")
    except ImportError:
        print("   ⚠️  ffmpeg-python - MISSING (optional, but recommended)")
        optional_missing.append("ffmpeg-python")
    
    # System dependencies
    print("\n🔧 System Dependencies:")
    
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              timeout=5)
        if result.returncode == 0:
            print("   ✅ ffmpeg - OK")
        else:
            print("   ⚠️  ffmpeg - NOT FOUND")
            optional_missing.append("ffmpeg (system package)")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        print("   ⚠️  ffmpeg - NOT FOUND")
        optional_missing.append("ffmpeg (system package)")
    
    # Summary
    print("\n" + "=" * 70)
    if missing:
        print("❌ MISSING REQUIRED DEPENDENCIES:")
        for dep in missing:
            print(f"   - {dep}")
        print("\n📥 Install with:")
        print("   pip install " + " ".join(missing))
        print("\n   # Also install playwright browsers:")
        print("   playwright install chromium")
        return False
    elif optional_missing:
        print("⚠️  SOME OPTIONAL DEPENDENCIES ARE MISSING:")
        for dep in optional_missing:
            print(f"   - {dep}")
        print("\n💡 These are optional but recommended for better performance.")
        print("✅ Required dependencies are installed - CAPTCHA resolver should work!")
        return True
    else:
        print("✅ ALL DEPENDENCIES ARE INSTALLED!")
        print("\n🚀 You're ready to test the CAPTCHA resolver:")
        print("   python3 test_captcha_resolver.py")
        return True


if __name__ == "__main__":
    success = check_dependencies()
    sys.exit(0 if success else 1)

