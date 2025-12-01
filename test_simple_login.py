"""Simple login test without database."""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

print("Creating simple login test...")

root = tk.Tk()
root.withdraw()  # Hide main window

# Create login dialog
dialog = tk.Toplevel(root)
dialog.title("Login Test")
dialog.geometry("400x300")
dialog.configure(bg="#0f172a")
dialog.transient(root)
dialog.grab_set()

# Center dialog
dialog.update_idletasks()
x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
y = (dialog.winfo_screenheight() // 2) - (300 // 2)
dialog.geometry(f"400x300+{x}+{y}")

# Make visible
dialog.lift()
dialog.attributes('-topmost', True)
dialog.focus_force()

# Container
container = tk.Frame(dialog, bg="#0f172a", padx=40, pady=40)
container.pack(fill=tk.BOTH, expand=True)

# Title
title = tk.Label(container, text="TEQSmartSubmit", font=("Arial", 20, "bold"), fg="white", bg="#0f172a")
title.pack(pady=(0, 10))

# Username
tk.Label(container, text="Username", font=("Arial", 10), fg="#cbd5e1", bg="#0f172a", anchor=tk.W).pack(fill=tk.X, pady=(0, 5))
username_entry = tk.Entry(container, font=("Arial", 11), bg="#1e293b", fg="white", relief=tk.FLAT, borderwidth=0, highlightthickness=1, highlightbackground="#334155")
username_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)

# Password
tk.Label(container, text="Password", font=("Arial", 10), fg="#cbd5e1", bg="#0f172a", anchor=tk.W).pack(fill=tk.X, pady=(0, 5))
password_entry = tk.Entry(container, font=("Arial", 11), bg="#1e293b", fg="white", show="•", relief=tk.FLAT, borderwidth=0, highlightthickness=1, highlightbackground="#334155")
password_entry.pack(fill=tk.X, pady=(0, 20), ipady=8)

# Button
def test_login():
    username = username_entry.get()
    password = password_entry.get()
    messagebox.showinfo("Test", f"Username: {username}\nPassword: {password}")
    dialog.destroy()
    root.destroy()

login_btn = tk.Button(container, text="Sign in", font=("Arial", 11, "bold"), bg="#6366f1", fg="white", 
                     activebackground="#4f46e5", relief=tk.FLAT, padx=20, pady=10, cursor="hand2", command=test_login)
login_btn.pack(fill=tk.X)

# Remove topmost
dialog.attributes('-topmost', False)
dialog.update()
username_entry.focus()

print("Login dialog should be visible now!")
print("Do you see the login window with username, password fields and Sign in button?")

root.mainloop()
print("Test complete")


