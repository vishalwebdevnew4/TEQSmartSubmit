"""Modern login dialog using CustomTkinter."""

from __future__ import annotations

import customtkinter as ctk
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


class LoginDialog:
    """Modern login dialog."""

    def __init__(self, parent):
        """Initialize login dialog."""
        self.current_user = None
        
        # Create dialog window
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("Login - TEQSmartSubmit")
        self.dialog.geometry("400x450")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (450 // 2)
        self.dialog.geometry(f"400x450+{x}+{y}")
        
        self.create_widgets()
        
        # Make dialog modal
        self.dialog.focus()
        self.dialog.lift()
    
    def create_widgets(self):
        """Create login form widgets."""
        # Container
        container = ctk.CTkFrame(self.dialog, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Header
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 30))
        
        title = ctk.CTkLabel(
            header,
            text="TEQSmartSubmit",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            header,
            text="Sign in to manage automation runs",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        subtitle.pack(anchor="w", pady=(5, 0))
        
        # Form fields
        form_frame = ctk.CTkFrame(container, fg_color="transparent")
        form_frame.pack(fill="x", pady=(0, 25))
        
        # Username
        username_label = ctk.CTkLabel(
            form_frame,
            text="Username",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        username_label.pack(fill="x", pady=(0, 8))
        
        self.username_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter username",
            height=40,
            font=ctk.CTkFont(size=13)
        )
        self.username_entry.pack(fill="x", pady=(0, 20))
        
        # Password
        password_label = ctk.CTkLabel(
            form_frame,
            text="Password",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        password_label.pack(fill="x", pady=(0, 8))
        
        self.password_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter password",
            height=40,
            font=ctk.CTkFont(size=13),
            show="•"
        )
        self.password_entry.pack(fill="x", pady=(0, 25))
        
        # Bind Enter key to login
        self.password_entry.bind("<Return>", lambda e: self.login())
        
        # Error label (initially hidden)
        self.error_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="red",
            anchor="w"
        )
        self.error_label.pack(fill="x", pady=(0, 10))
        
        # Login button
        login_btn = ctk.CTkButton(
            container,
            text="Sign in",
            corner_radius=10,
            height=45,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.login
        )
        login_btn.pack(fill="x")
        
        # Focus on username field
        self.username_entry.focus()
    
    def login(self):
        """Handle login."""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            self.error_label.configure(text="Please enter both username and password")
            return
        
        # Clear error
        self.error_label.configure(text="")
        
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
                self.error_label.configure(text="Incorrect username or password")
        except Exception as e:
            self.error_label.configure(text=f"Database connection error: {str(e)}")
    
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


