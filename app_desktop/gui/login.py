"""Login dialog."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
import asyncio

import sys
import os

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.db.session import get_session
from app.db.models.admin import Admin
from app.core.security import verify_password
from sqlalchemy import select
from theme import Colors, Fonts, Spacing, ButtonStyle, InputStyle, LabelStyle


class LoginDialog:
    """Login dialog window."""

    def __init__(self, parent):
        """Initialize login dialog."""
        print("  Creating Toplevel dialog...")
        self.current_user = None
        
        try:
            self.dialog = tk.Toplevel(parent)
            self.dialog.title("Login - TEQSmartSubmit")
            self.dialog.geometry("420x500")
            self.dialog.configure(bg=Colors.BG_PRIMARY)
            self.dialog.transient(parent)
            self.dialog.grab_set()
            self.dialog.resizable(False, False)
            
            print("  Positioning dialog...")
            # Center the dialog first
            parent.update_idletasks()
            self.dialog.update_idletasks()
            x = (self.dialog.winfo_screenwidth() // 2) - (420 // 2)
            y = (self.dialog.winfo_screenheight() // 2) - (500 // 2)
            self.dialog.geometry(f"420x500+{x}+{y}")
            
            # Make sure dialog appears on top and is visible
            self.dialog.lift()
            self.dialog.attributes('-topmost', True)
            self.dialog.focus_force()
            
            # Force it to be visible
            self.dialog.deiconify()
            self.dialog.update_idletasks()
            self.dialog.update()
            
            # Keep topmost for a bit longer to ensure visibility
            # Will be removed after widgets are created

            print("  Creating widgets...")
            self.create_widgets()
            
            # Force update to ensure all widgets are visible
            print("  Updating dialog...")
            self.dialog.update_idletasks()
            self.dialog.update()
            parent.update()
            print("  Login dialog ready and should be visible!")
        except Exception as e:
            print(f"  ERROR creating login dialog: {e}")
            import traceback
            traceback.print_exc()
            # Create a minimal dialog as fallback
            if hasattr(self, 'dialog'):
                self.dialog.destroy()
            raise

    def create_widgets(self):
        """Create login form widgets."""
        # Main container
        container = tk.Frame(self.dialog, bg=Colors.BG_PRIMARY, padx=Spacing.XXXL, pady=Spacing.XXXL)
        container.pack(fill=tk.BOTH, expand=True)

        # Header section
        header_frame = tk.Frame(container, bg=Colors.BG_PRIMARY)
        header_frame.pack(fill=tk.X, pady=(0, Spacing.XXXL))

        # Title with accent color
        title = tk.Label(
            header_frame,
            text="TEQSmartSubmit",
            font=Fonts.get_title_font(),
            fg=Colors.ACCENT_PRIMARY,
            bg=Colors.BG_PRIMARY
        )
        title.pack(anchor=tk.W)

        subtitle = tk.Label(
            header_frame,
            text="Sign in to manage automation runs",
            font=Fonts.get_body_font(),
            fg=Colors.TEXT_MUTED,
            bg=Colors.BG_PRIMARY
        )
        subtitle.pack(anchor=tk.W, pady=(Spacing.XS, 0))

        # Form fields container
        form_frame = tk.Frame(container, bg=Colors.BG_PRIMARY)
        form_frame.pack(fill=tk.X, pady=(0, Spacing.XXL))

        # Username field
        username_label = tk.Label(
            form_frame,
            text="Username",
            font=Fonts.get_body_font(),
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_PRIMARY,
            anchor=tk.W
        )
        username_label.pack(fill=tk.X, pady=(0, Spacing.XS))

        self.username_entry = tk.Entry(
            form_frame,
            font=Fonts.get_body_font(),
            bg=Colors.INPUT_BG,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.ACCENT_PRIMARY,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=2,
            highlightbackground=Colors.INPUT_BORDER,
            highlightcolor=Colors.INPUT_FOCUS
        )
        self.username_entry.pack(fill=tk.X, pady=(0, Spacing.XL), ipady=12)

        # Password field
        password_label = tk.Label(
            form_frame,
            text="Password",
            font=Fonts.get_body_font(),
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_PRIMARY,
            anchor=tk.W
        )
        password_label.pack(fill=tk.X, pady=(0, Spacing.XS))

        self.password_entry = tk.Entry(
            form_frame,
            font=Fonts.get_body_font(),
            bg=Colors.INPUT_BG,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.ACCENT_PRIMARY,
            relief=tk.FLAT,
            show="•",
            borderwidth=0,
            highlightthickness=2,
            highlightbackground=Colors.INPUT_BORDER,
            highlightcolor=Colors.INPUT_FOCUS
        )
        self.password_entry.pack(fill=tk.X, pady=(0, Spacing.XL), ipady=12)
        self.password_entry.bind("<Return>", lambda e: self.login())

        # Error label (initially empty)
        self.error_label = tk.Label(
            form_frame,
            text="",
            font=Fonts.get_small_font(),
            fg=Colors.ERROR,
            bg=Colors.BG_PRIMARY,
            height=1,
            wraplength=320
        )
        self.error_label.pack(fill=tk.X, pady=(0, Spacing.XL))

        # Login button with modern styling
        login_btn = tk.Button(
            container,
            text="Sign in",
            **ButtonStyle.primary(),
            command=self.login
        )
        login_btn.pack(fill=tk.X)

        # Make sure dialog is visible and on top
        self.dialog.lift()
        self.dialog.focus_force()
        self.dialog.attributes('-topmost', True)
        
        # Force visibility updates
        self.dialog.deiconify()
        self.dialog.update_idletasks()
        self.dialog.update()
        
        # Remove topmost after ensuring it's visible
        self.dialog.after(500, lambda: self.dialog.attributes('-topmost', False))
        
        # Focus on username
        self.username_entry.focus()
        self.dialog.update()

    def login(self):
        """Handle login."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        # Run async database query
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            user = loop.run_until_complete(self.authenticate(username, password))
            loop.close()

            if user:
                self.current_user = user
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Incorrect username or password")
        except Exception as e:
            messagebox.showerror("Error", f"Database connection error: {str(e)}")

    async def authenticate(self, username: str, password: str):
        """Authenticate user."""
        async for session in get_session():
            result = await session.execute(
                select(Admin).where(Admin.username == username, Admin.is_active == True)
            )
            admin = result.scalar_one_or_none()
            
            if admin and verify_password(password, admin.password_hash):
                return admin
            return None

