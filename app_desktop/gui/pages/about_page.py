"""About page component."""

from __future__ import annotations

import customtkinter as ctk


class AboutPage:
    """About page view."""

    def __init__(self, parent, app):
        """Initialize about page."""
        self.parent = parent
        self.app = app
        
        # Create main frame
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        
        # Title
        title = ctk.CTkLabel(
            self.frame,
            text="About",
            font=ctk.CTkFont(size=32, weight="bold"),
            anchor="w"
        )
        title.pack(anchor="w", pady=(0, 30))
        
        # App info
        app_info = ctk.CTkTextbox(
            self.frame,
            width=550,
            height=200,
            font=ctk.CTkFont(size=13),
            wrap="word"
        )
        app_info.pack(anchor="w", pady=(0, 20))
        
        about_text = """TEQSmartSubmit v0.1.0

A modern automation control center built with CustomTkinter.

Features:
• Modern dark mode interface
• Domain management
• Template configuration
• Automation logs
• Real-time monitoring

Built with Python, CustomTkinter, and PostgreSQL.
"""
        app_info.insert("1.0", about_text)
        app_info.configure(state="disabled")
        
        # Credits
        credits_label = ctk.CTkLabel(
            self.frame,
            text="© 2025 TEQSmartSubmit. All rights reserved.",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        credits_label.pack(anchor="w")
    
    def pack(self, **kwargs):
        """Pack the frame."""
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """Hide the frame."""
        self.frame.pack_forget()


