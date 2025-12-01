"""Test script to verify all imports work correctly."""

import sys
import os

# Add paths
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test all critical imports."""
    print("Testing imports...")
    
    try:
        # Test backend imports
        print("  Testing backend imports...")
        from app.db.session import get_session
        from app.db.models.admin import Admin
        from app.db.models.domain import Domain
        from app.db.models.template import Template
        from app.db.models.submission import SubmissionLog
        from app.core.security import verify_password, hash_password
        print("    ✓ Backend imports successful")
        
        # Test GUI imports - need to ensure app is in path
        print("  Testing GUI imports...")
        # Add app directory to path if not already there
        app_dir = os.path.join(os.path.dirname(__file__), 'app')
        if app_dir not in sys.path:
            sys.path.insert(0, app_dir)
        
        # Import using the full path structure
        import importlib.util
        gui_path = os.path.join(os.path.dirname(__file__), 'app', 'gui', 'main_window.py')
        spec = importlib.util.spec_from_file_location("main_window", gui_path)
        if spec and spec.loader:
            main_window = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main_window)
            print("    ✓ GUI imports successful (using direct file import)")
        else:
            # Try regular import
            from app.gui.main_window import MainWindow
            from app.gui.login import LoginDialog
            from app.gui.dashboard import DashboardFrame
            from app.gui.domains import DomainsFrame
            from app.gui.templates import TemplatesFrame
            from app.gui.logs import LogsFrame
            from app.gui.settings import SettingsFrame
            print("    ✓ GUI imports successful")
        
        # Test tkinter
        print("  Testing tkinter...")
        import tkinter as tk
        from tkinter import ttk
        print("    ✓ Tkinter available")
        
        print("\n✅ All imports successful! Application should work.")
        return True
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)

