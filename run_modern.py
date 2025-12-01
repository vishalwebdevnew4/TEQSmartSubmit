"""Run the modern CustomTkinter application."""

import sys
import os

# Get project root
project_root = os.path.dirname(os.path.abspath(__file__))

# Add GUI to path
gui_path = os.path.join(project_root, 'app', 'gui')
if gui_path not in sys.path:
    sys.path.insert(0, gui_path)

try:
    from simple_modern_app import SimpleModernApp
    
    if __name__ == "__main__":
        try:
            app = SimpleModernApp()
            app.run()
        except Exception as e:
            print(f"Error starting application: {e}")
            import traceback
            traceback.print_exc()
            input("\nPress Enter to exit...")
            sys.exit(1)
except ImportError as e:
    print(f"Error importing CustomTkinter: {e}")
    print("\nPlease install CustomTkinter:")
    print("  pip install customtkinter")
    input("\nPress Enter to exit...")
    sys.exit(1)



