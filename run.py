"""Run script that sets up paths correctly."""

import sys
import os
import importlib.util
import traceback

# Get the project root directory
project_root = os.path.dirname(os.path.abspath(__file__))

print("Starting TEQSmartSubmit Desktop Application...")
print(f"Project root: {project_root}")

try:
    # Add backend to path (for backend/app imports)
    backend_path = os.path.join(project_root, 'backend')
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    print(f"Backend path added: {backend_path}")

    # Import MainWindow directly
    gui_main_path = os.path.join(project_root, 'app', 'gui', 'main_window.py')
    print(f"Loading GUI from: {gui_main_path}")
    
    if not os.path.exists(gui_main_path):
        print(f"ERROR: GUI file not found at {gui_main_path}")
        sys.exit(1)
    
    spec = importlib.util.spec_from_file_location("main_window", gui_main_path)
    if spec is None or spec.loader is None:
        print("ERROR: Failed to create module spec")
        sys.exit(1)
    
    main_window_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_window_module)
    MainWindow = main_window_module.MainWindow
    print("GUI module loaded successfully")

    if __name__ == "__main__":
        print("Creating MainWindow instance...")
        app = MainWindow()
        print("MainWindow created, starting application...")
        app.run()
        print("Application closed")
        
except KeyboardInterrupt:
    print("\nApplication interrupted by user")
    sys.exit(0)
except Exception as e:
    print(f"\nERROR: Failed to start application")
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    print("\nFull traceback:")
    traceback.print_exc()
    input("\nPress Enter to exit...")
    sys.exit(1)

