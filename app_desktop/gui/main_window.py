"""Main application window."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

# Import GUI modules - using absolute imports
import sys
import os

# Ensure backend is in path
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import GUI modules
gui_dir = os.path.dirname(__file__)
sys.path.insert(0, gui_dir)

from dashboard import DashboardFrame
from domains import DomainsFrame
from templates import TemplatesFrame
from logs import LogsFrame
from settings import SettingsFrame
from login import LoginDialog
from theme import Colors, Fonts, Spacing


class MainWindow:
    """Main application window."""

    def __init__(self):
        """Initialize the main window."""
        print("Initializing Tkinter root window...")
        self.root = tk.Tk()
        self.root.title("TEQSmartSubmit - Automation Control Center")
        self.root.geometry("1400x900")
        self.root.configure(bg=Colors.BG_PRIMARY)
        
        # Position root window off-screen initially so it doesn't interfere
        # but don't withdraw it - that can cause issues with dialogs on Windows
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # Position it off-screen (to the right)
        self.root.geometry(f"1400x900+{screen_width + 100}+100")
        self.root.update()
        print("Main window positioned, showing login dialog...")
        
        # Check authentication
        self.current_user = None
        try:
            self.show_login()
            print(f"Login completed. User: {self.current_user.username if self.current_user else 'None'}")
        except Exception as e:
            print(f"Error during login: {e}")
            import traceback
            traceback.print_exc()
            self.current_user = None
        
        if self.current_user:
            # Show main window after successful login - center it on screen
            print("Setting up main interface...")
            self.root.update_idletasks()
            x = (screen_width // 2) - (1400 // 2)
            y = (screen_height // 2) - (900 // 2)
            self.root.geometry(f"1400x900+{x}+{y}")
            self.root.lift()
            self.root.focus_force()
            self.setup_main_interface()
            print("Main interface setup complete")
        else:
            # Close if login cancelled
            print("No user logged in, closing application")
            try:
                self.root.destroy()
            except:
                pass

    def show_login(self):
        """Show login dialog."""
        print("Creating login dialog...")
        try:
            # Make sure root window is ready and visible (even if off-screen)
            self.root.update_idletasks()
            self.root.update()
            
            login = LoginDialog(self.root)
            print("Login dialog created, waiting for user input...")
            
            # Force the dialog to be visible - multiple attempts
            for _ in range(3):
                login.dialog.lift()
                login.dialog.focus_force()
                login.dialog.attributes('-topmost', True)
                login.dialog.deiconify()
                login.dialog.update_idletasks()
                login.dialog.update()
                self.root.update()
            
            print("Login dialog should be visible now - check your screen!")
            print("If you don't see it, try Alt+Tab to find it")
            
            # Wait for dialog to close
            self.root.wait_window(login.dialog)
            print("Login dialog closed")
            self.current_user = login.current_user
        except Exception as e:
            print(f"Error showing login dialog: {e}")
            import traceback
            traceback.print_exc()
            self.current_user = None

    def setup_main_interface(self):
        """Setup the main interface after login."""
        # Create main container
        main_container = tk.Frame(self.root, bg=Colors.BG_PRIMARY)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Create sidebar
        self.create_sidebar(main_container)

        # Create content area with clean border
        self.content_frame = tk.Frame(main_container, bg="#0f172a")
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Create notebook for different views with custom style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TNotebook", background=Colors.BG_PRIMARY, borderwidth=0)
        style.configure("TNotebook.Tab", 
                       background=Colors.BG_SECONDARY, 
                       foreground=Colors.TEXT_MUTED,
                       padding=[24, 14],
                       borderwidth=0,
                       font=Fonts.get_body_font())
        style.map("TNotebook.Tab",
                 background=[("selected", Colors.BG_PRIMARY)],
                 foreground=[("selected", Colors.TEXT_PRIMARY)],
                 expand=[("selected", [1, 1, 1, 0])])
        
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Add tabs
        self.dashboard_frame = DashboardFrame(self.notebook)
        self.notebook.add(self.dashboard_frame.frame, text="Dashboard")

        self.domains_frame = DomainsFrame(self.notebook)
        self.notebook.add(self.domains_frame.frame, text="Domains")

        self.templates_frame = TemplatesFrame(self.notebook)
        self.notebook.add(self.templates_frame.frame, text="Templates")

        self.logs_frame = LogsFrame(self.notebook)
        self.notebook.add(self.logs_frame.frame, text="Logs")

        self.settings_frame = SettingsFrame(self.notebook)
        self.notebook.add(self.settings_frame.frame, text="Settings")

    def create_sidebar(self, parent):
        """Create the sidebar navigation."""
        sidebar = tk.Frame(parent, bg=Colors.BG_SECONDARY, width=300)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=0, pady=0)
        sidebar.pack_propagate(False)

        # Header with better spacing
        header = tk.Frame(sidebar, bg=Colors.BG_SECONDARY, pady=Spacing.XXXL)
        header.pack(fill=tk.X, padx=Spacing.XXL)
        
        # Logo/Title area
        title_container = tk.Frame(header, bg=Colors.BG_SECONDARY)
        title_container.pack(fill=tk.X)
        
        title = tk.Label(
            title_container,
            text="TEQSmartSubmit",
            font=Fonts.get_heading_font(),
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_SECONDARY
        )
        title.pack(anchor=tk.W)
        
        subtitle = tk.Label(
            title_container,
            text="Automation Control Center",
            font=Fonts.get_small_font(),
            fg=Colors.TEXT_MUTED,
            bg=Colors.BG_SECONDARY
        )
        subtitle.pack(anchor=tk.W, pady=(Spacing.XS, 0))

        if self.current_user:
            # User info card with accent border
            user_card = tk.Frame(header, bg=Colors.BG_ELEVATED, relief=tk.FLAT, padx=Spacing.MD, pady=Spacing.MD)
            user_card.pack(fill=tk.X, pady=(Spacing.LG, 0))
            
            user_label = tk.Label(
                user_card,
                text=f"Signed in as {self.current_user.username}",
                font=Fonts.get_small_font(),
                fg=Colors.TEXT_SECONDARY,
                bg=Colors.BG_ELEVATED
            )
            user_label.pack(anchor=tk.W)

        # Navigation buttons with cleaner styling
        nav_frame = tk.Frame(sidebar, bg=Colors.BG_SECONDARY)
        nav_frame.pack(fill=tk.X, padx=Spacing.XL, pady=(Spacing.LG, Spacing.XXL))

        nav_items = [
            ("Dashboard", 0),
            ("Domains", 1),
            ("Templates", 2),
            ("Logs", 3),
            ("Settings", 4),
        ]

        self.nav_buttons = []
        for label, index in nav_items:
            btn_frame = tk.Frame(nav_frame, bg=Colors.BG_SECONDARY)
            btn_frame.pack(fill=tk.X, pady=Spacing.XS)
            
            btn = tk.Button(
                btn_frame,
                text=label,
                font=Fonts.get_body_font(),
                bg=Colors.BG_ELEVATED,
                fg=Colors.TEXT_SECONDARY,
                activebackground=Colors.ACCENT_PRIMARY,
                activeforeground=Colors.BG_PRIMARY,
                relief=tk.FLAT,
                padx=Spacing.LG,
                pady=Spacing.MD,
                anchor=tk.W,
                cursor="hand2",
                borderwidth=0,
                highlightthickness=0,
                command=lambda idx=index: self.switch_tab(idx)
            )
            btn.pack(fill=tk.X)
            self.nav_buttons.append(btn)

        # Footer with cleaner design
        footer = tk.Frame(sidebar, bg=Colors.BG_SECONDARY)
        footer.pack(side=tk.BOTTOM, fill=tk.X, padx=Spacing.XL, pady=Spacing.XXL)

        logout_btn = tk.Button(
            footer,
            text="Logout",
            font=Fonts.get_small_font(),
            bg=Colors.BG_ELEVATED,
            fg=Colors.TEXT_PRIMARY,
            activebackground=Colors.ERROR,
            activeforeground=Colors.TEXT_PRIMARY,
            relief=tk.FLAT,
            padx=Spacing.LG,
            pady=Spacing.MD,
            cursor="hand2",
            borderwidth=0,
            command=self.logout
        )
        logout_btn.pack(fill=tk.X)

        version_label = tk.Label(
            footer,
            text="v0.1.0",
            font=Fonts.get_small_font(),
            fg=Colors.TEXT_DISABLED,
            bg=Colors.BG_SECONDARY
        )
        version_label.pack(pady=(Spacing.MD, 0))

    def switch_tab(self, index):
        """Switch to a specific tab."""
        self.notebook.select(index)

    def logout(self):
        """Handle logout."""
        self.current_user = None
        self.root.destroy()
        # Restart application
        app = MainWindow()
        app.run()

    def run(self):
        """Run the application."""
        if self.current_user:
            self.root.mainloop()
        else:
            self.root.destroy()

