"""Modern entry point using CustomTkinter."""

import sys
import os

# Get project root
project_root = os.path.dirname(os.path.abspath(__file__))

# Add backend to path (for backend/app imports)
backend_path = os.path.join(project_root, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import ModernApp
gui_path = os.path.join(project_root, 'app', 'gui')
if gui_path not in sys.path:
    sys.path.insert(0, gui_path)

from modern_app import ModernApp

if __name__ == "__main__":
    try:
        app = ModernApp()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)



