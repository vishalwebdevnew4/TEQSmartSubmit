"""Test script to verify login dialog displays correctly."""

import sys
import os
import tkinter as tk

# Add paths
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import after path setup
from app.gui.login import LoginDialog

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide main window
    
    print("Creating login dialog...")
    dialog = LoginDialog(root)
    
    print("Login dialog created!")
    print("Window size:", dialog.dialog.winfo_width(), "x", dialog.dialog.winfo_height())
    print("Password entry exists:", hasattr(dialog, 'password_entry'))
    print("Username entry exists:", hasattr(dialog, 'username_entry'))
    
    # Check if widgets are visible
    try:
        dialog.dialog.update()
        print("Dialog updated")
        print("Password entry visible:", dialog.password_entry.winfo_viewable() if hasattr(dialog, 'password_entry') else "N/A")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nLogin dialog should be visible now.")
    print("Check if you can see:")
    print("  - Username field")
    print("  - Password field (with dots)")
    print("  - Sign in button")
    
    root.mainloop()

