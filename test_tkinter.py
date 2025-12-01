"""Test if tkinter works."""

import tkinter as tk

print("Testing tkinter...")
try:
    root = tk.Tk()
    root.title("Test Window")
    root.geometry("300x200")
    
    label = tk.Label(root, text="If you see this, tkinter works!", font=("Arial", 12))
    label.pack(pady=50)
    
    button = tk.Button(root, text="Close", command=root.destroy)
    button.pack()
    
    print("Tkinter window should be visible now")
    print("If you don't see a window, there's a display issue")
    
    root.mainloop()
    print("Window closed")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()


