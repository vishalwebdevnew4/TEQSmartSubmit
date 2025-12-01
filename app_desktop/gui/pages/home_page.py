"""Home page component."""

from __future__ import annotations

import customtkinter as ctk


class HomePage:
    """Home page view."""

    def __init__(self, parent, app):
        """Initialize home page."""
        self.parent = parent
        self.app = app
        
        # Create main frame
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        
        # Welcome message
        welcome_label = ctk.CTkLabel(
            self.frame,
            text="Welcome to TEQSmartSubmit",
            font=ctk.CTkFont(size=32, weight="bold"),
            anchor="w"
        )
        welcome_label.pack(anchor="w", pady=(0, 10))
        
        subtitle = ctk.CTkLabel(
            self.frame,
            text="Modern automation control center",
            font=ctk.CTkFont(size=14),
            text_color="gray",
            anchor="w"
        )
        subtitle.pack(anchor="w", pady=(0, 40))
        
        # Action button
        action_btn = ctk.CTkButton(
            self.frame,
            text="Get Started",
            corner_radius=10,
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.on_button_click
        )
        action_btn.pack(anchor="w", pady=(0, 20))
        
        # Info text
        info_text = ctk.CTkLabel(
            self.frame,
            text="Click the button above or use the sidebar to navigate.",
            font=ctk.CTkFont(size=12),
            text_color="gray",
            anchor="w",
            justify="left"
        )
        info_text.pack(anchor="w")
    
    def pack(self, **kwargs):
        """Pack the frame."""
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """Hide the frame."""
        self.frame.pack_forget()
    
    def on_button_click(self):
        """Handle button click."""
        # Show a message
        dialog = ctk.CTkInputDialog(
            text="Enter your name:",
            title="Welcome"
        )
        name = dialog.get_input()
        if name:
            print(f"Hello, {name}!")


