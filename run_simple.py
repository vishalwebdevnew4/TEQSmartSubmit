"""Simplified run script to test if application opens."""

import sys
import os

print("=" * 50)
print("TEQSmartSubmit - Simple Test")
print("=" * 50)

# Test tkinter first
print("\n1. Testing tkinter...")
try:
    import tkinter as tk
    print("   ✓ Tkinter imported successfully")
    
    root = tk.Tk()
    root.withdraw()
    print("   ✓ Tkinter root window created")
    
    # Test if we can create a simple window
    test_window = tk.Toplevel(root)
    test_window.title("Test")
    test_window.geometry("200x100")
    test_window.lift()
    test_window.update()
    print("   ✓ Test window created and should be visible")
    print("   Do you see a small window? (It will close in 2 seconds)")
    
    root.after(2000, test_window.destroy)
    root.after(2500, root.destroy)
    root.mainloop()
    print("   ✓ Tkinter test complete")
    
except Exception as e:
    print(f"   ✗ Tkinter error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Now try the actual application
print("\n2. Testing application import...")
try:
    # Add paths
    project_root = os.path.dirname(os.path.abspath(__file__))
    backend_path = os.path.join(project_root, 'backend')
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    
    import importlib.util
    gui_main_path = os.path.join(project_root, 'app', 'gui', 'main_window.py')
    spec = importlib.util.spec_from_file_location("main_window", gui_main_path)
    main_window_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(main_window_module)
    MainWindow = main_window_module.MainWindow
    print("   ✓ Application module loaded")
    
    print("\n3. Creating application window...")
    print("   This should open a login dialog")
    print("   If nothing appears, there may be a display issue")
    
    app = MainWindow()
    print("   ✓ MainWindow created")
    print("   Starting application loop...")
    app.run()
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    input("\nPress Enter to exit...")


