"""Modern GUI application using CustomTkinter."""

from __future__ import annotations

import customtkinter as ctk
import sys
import os

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import pages
gui_dir = os.path.dirname(__file__)
if gui_dir not in sys.path:
    sys.path.insert(0, gui_dir)

from pages.home_page import HomePage
from pages.settings_page import SettingsPage
from pages.about_page import AboutPage
from login_dialog import LoginDialog


class ModernApp:
    """Modern application window with CustomTkinter."""

    def __init__(self):
        """Initialize the modern application."""
        # Configure CustomTkinter appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("Modern App")
        self.root.geometry("600x400")
        
        # Center window on screen
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (600 // 2)
        y = (screen_height // 2) - (400 // 2)
        self.root.geometry(f"600x400+{x}+{y}")
        
        # Check authentication
        self.current_user = None
        self.show_login()
        
        if self.current_user:
            self.setup_main_interface()
        else:
            self.root.destroy()
    
    def show_login(self):
        """Show login dialog."""
        login = LoginDialog(self.root)
        self.root.wait_window(login.dialog)
        self.current_user = login.current_user
    
    def setup_main_interface(self):
        """Setup the main interface after login."""
        # Create main container
        main_container = ctk.CTkFrame(self.root, corner_radius=0, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Create sidebar
        self.create_sidebar(main_container)
        
        # Create content area
        self.content_frame = ctk.CTkFrame(main_container, corner_radius=0)
        self.content_frame.pack(side="right", fill="both", expand=True, padx=0, pady=0)
        
        # Initialize pages
        self.pages = {}
        self.current_page = None
        
        # Create pages
        self.pages["home"] = HomePage(self.content_frame, self)
        self.pages["settings"] = SettingsPage(self.content_frame, self)
        self.pages["about"] = AboutPage(self.content_frame, self)
        
        # Show home page by default
        self.show_page("home")
    
    def create_sidebar(self, parent):
        """Create the sidebar navigation."""
        sidebar = ctk.CTkFrame(parent, width=180, corner_radius=0)
        sidebar.pack(side="left", fill="y", padx=0, pady=0)
        sidebar.pack_propagate(False)
        
        # Header
        header_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=30)
        
        title = ctk.CTkLabel(
            header_frame,
            text="TEQSmartSubmit",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Automation Control",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        subtitle.pack(anchor="w", pady=(5, 0))
        
        if self.current_user:
            user_label = ctk.CTkLabel(
                header_frame,
                text=f"Signed in as {self.current_user.username}",
                font=ctk.CTkFont(size=10),
                text_color="gray"
            )
            user_label.pack(anchor="w", pady=(15, 0))
        
        # Navigation buttons
        nav_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        nav_frame.pack(fill="x", padx=15, pady=20)
        
        self.nav_buttons = {}
        nav_items = [
            ("Home", "home"),
            ("Settings", "settings"),
            ("About", "about"),
        ]
        
        for label, page_id in nav_items:
            btn = ctk.CTkButton(
                nav_frame,
                text=label,
                corner_radius=8,
                height=40,
                font=ctk.CTkFont(size=13),
                anchor="w",
                command=lambda pid=page_id: self.show_page(pid)
            )
            btn.pack(fill="x", pady=5)
            self.nav_buttons[page_id] = btn
        
        # Footer
        footer_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        footer_frame.pack(side="bottom", fill="x", padx=15, pady=20)
        
        logout_btn = ctk.CTkButton(
            footer_frame,
            text="Logout",
            corner_radius=8,
            height=35,
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            border_width=1,
            command=self.logout
        )
        logout_btn.pack(fill="x")
        
        version_label = ctk.CTkLabel(
            footer_frame,
            text="v0.1.0",
            font=ctk.CTkFont(size=9),
            text_color="gray"
        )
        version_label.pack(pady=(10, 0))
    
    def show_page(self, page_id: str):
        """Show a specific page."""
        # Hide current page
        if self.current_page:
            self.current_page.pack_forget()
        
        # Show new page
        if page_id in self.pages:
            self.current_page = self.pages[page_id]
            self.current_page.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Update button states
            for pid, btn in self.nav_buttons.items():
                if pid == page_id:
                    btn.configure(fg_color=("gray75", "gray25"))
                else:
                    btn.configure(fg_color=("gray70", "gray30"))
    
    def logout(self):
        """Handle logout."""
        self.current_user = None
        self.root.destroy()
        # Restart application
        app = ModernApp()
        app.run()
    
    def run(self):
        """Run the application."""
        if self.current_user:
            self.root.mainloop()
        else:
            self.root.destroy()


if __name__ == "__main__":
    app = ModernApp()
    app.run()

