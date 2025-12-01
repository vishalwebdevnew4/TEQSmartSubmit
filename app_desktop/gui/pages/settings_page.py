"""Settings page component."""

from __future__ import annotations

import customtkinter as ctk


class SettingsPage:
    """Settings page view."""

    def __init__(self, parent, app):
        """Initialize settings page."""
        self.parent = parent
        self.app = app
        
        # Create main frame
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        
        # Title
        title = ctk.CTkLabel(
            self.frame,
            text="Settings",
            font=ctk.CTkFont(size=32, weight="bold"),
            anchor="w"
        )
        title.pack(anchor="w", pady=(0, 10))
        
        subtitle = ctk.CTkLabel(
            self.frame,
            text="Configure your application preferences",
            font=ctk.CTkFont(size=14),
            text_color="gray",
            anchor="w"
        )
        subtitle.pack(anchor="w", pady=(0, 40))
        
        # Settings sections
        self.create_settings_sections()
    
    def create_settings_sections(self):
        """Create settings sections."""
        # Appearance section
        appearance_frame = ctk.CTkFrame(self.frame)
        appearance_frame.pack(fill="x", pady=(0, 15))
        
        appearance_label = ctk.CTkLabel(
            appearance_frame,
            text="Appearance",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        appearance_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Theme toggle
        theme_label = ctk.CTkLabel(
            appearance_frame,
            text="Dark Mode",
            font=ctk.CTkFont(size=13)
        )
        theme_label.pack(anchor="w", padx=20, pady=(0, 5))
        
        theme_switch = ctk.CTkSwitch(
            appearance_frame,
            text="Enable dark mode",
            command=self.toggle_theme
        )
        theme_switch.pack(anchor="w", padx=20, pady=(0, 20))
        theme_switch.select()  # Dark mode by default
        
        # Database section
        db_frame = ctk.CTkFrame(self.frame)
        db_frame.pack(fill="x", pady=(0, 15))
        
        db_label = ctk.CTkLabel(
            db_frame,
            text="Database",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        db_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        db_info = ctk.CTkLabel(
            db_frame,
            text="Database connection is configured via environment variables.",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w",
            justify="left",
            wraplength=500
        )
        db_info.pack(anchor="w", padx=20, pady=(0, 20))
    
    def toggle_theme(self):
        """Toggle theme."""
        current = ctk.get_appearance_mode()
        new_mode = "light" if current == "Dark" else "dark"
        ctk.set_appearance_mode(new_mode)
    
    def pack(self, **kwargs):
        """Pack the frame."""
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """Hide the frame."""
        self.frame.pack_forget()


