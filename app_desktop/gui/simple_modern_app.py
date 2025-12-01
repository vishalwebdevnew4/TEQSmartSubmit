"""Simple modern GUI application using CustomTkinter."""

from __future__ import annotations

import customtkinter as ctk


class SimpleModernApp:
    """Simple modern application window with CustomTkinter."""

    def __init__(self):
        """Initialize the modern application."""
        # Configure CustomTkinter appearance - dark mode
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
        
        # Setup interface
        self.setup_main_interface()
    
    def setup_main_interface(self):
        """Setup the main interface."""
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
            text="Modern App",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(anchor="w")
        
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
    
    def run(self):
        """Run the application."""
        self.root.mainloop()


# Page classes
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
            text="Welcome",
            font=ctk.CTkFont(size=32, weight="bold"),
            anchor="w"
        )
        welcome_label.pack(anchor="w", pady=(0, 10))
        
        subtitle = ctk.CTkLabel(
            self.frame,
            text="This is the home page of your modern application.",
            font=ctk.CTkFont(size=14),
            text_color="gray",
            anchor="w"
        )
        subtitle.pack(anchor="w", pady=(0, 40))
        
        # Clickable button
        action_btn = ctk.CTkButton(
            self.frame,
            text="Click Me",
            corner_radius=10,
            height=45,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self.on_button_click
        )
        action_btn.pack(anchor="w", pady=(0, 20))
    
    def pack(self, **kwargs):
        """Pack the frame."""
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """Hide the frame."""
        self.frame.pack_forget()
    
    def on_button_click(self):
        """Handle button click."""
        dialog = ctk.CTkInputDialog(
            text="Enter your name:",
            title="Hello"
        )
        name = dialog.get_input()
        if name:
            print(f"Hello, {name}!")


class SettingsPage:
    """Settings page view."""

    def __init__(self, parent, app):
        """Initialize settings page."""
        self.parent = parent
        self.app = app
        
        # Create main frame
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        
        title = ctk.CTkLabel(
            self.frame,
            text="Settings",
            font=ctk.CTkFont(size=32, weight="bold"),
            anchor="w"
        )
        title.pack(anchor="w", pady=(0, 30))
        
        # Settings content
        settings_label = ctk.CTkLabel(
            self.frame,
            text="Application settings and preferences",
            font=ctk.CTkFont(size=14),
            text_color="gray",
            anchor="w"
        )
        settings_label.pack(anchor="w")
    
    def pack(self, **kwargs):
        """Pack the frame."""
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """Hide the frame."""
        self.frame.pack_forget()


class AboutPage:
    """About page view."""

    def __init__(self, parent, app):
        """Initialize about page."""
        self.parent = parent
        self.app = app
        
        # Create main frame
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        
        title = ctk.CTkLabel(
            self.frame,
            text="About",
            font=ctk.CTkFont(size=32, weight="bold"),
            anchor="w"
        )
        title.pack(anchor="w", pady=(0, 30))
        
        # About content
        about_text = ctk.CTkLabel(
            self.frame,
            text="Modern App v1.0\n\nBuilt with CustomTkinter\nA modern Python GUI framework",
            font=ctk.CTkFont(size=14),
            text_color="gray",
            anchor="w",
            justify="left"
        )
        about_text.pack(anchor="w")
    
    def pack(self, **kwargs):
        """Pack the frame."""
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """Hide the frame."""
        self.frame.pack_forget()


if __name__ == "__main__":
    app = SimpleModernApp()
    app.run()


