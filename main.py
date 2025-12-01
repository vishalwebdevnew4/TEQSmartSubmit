"""Main entry point for TEQSmartSubmit desktop application."""

import sys
import os
import importlib.util

# Get project root
project_root = os.path.dirname(os.path.abspath(__file__))

# Add backend to path (for backend/app imports)
backend_path = os.path.join(project_root, 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import MainWindow directly from file
gui_main_path = os.path.join(project_root, 'app', 'gui', 'main_window.py')
spec = importlib.util.spec_from_file_location("main_window", gui_main_path)
main_window_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_window_module)
MainWindow = main_window_module.MainWindow

if __name__ == "__main__":
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

