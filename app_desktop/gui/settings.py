"""Settings frame."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox


class SettingsFrame:
    """Settings view."""

    def __init__(self, parent):
        """Initialize settings frame."""
        self.frame = tk.Frame(parent, bg="#0f172a")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_widgets()

    def create_widgets(self):
        """Create settings widgets."""
        # Header
        header = tk.Frame(self.frame, bg="#0f172a", pady=20)
        header.pack(fill=tk.X, padx=20)

        title = tk.Label(
            header,
            text="Settings",
            font=("Segoe UI", 26, "bold"),
            fg="white",
            bg="#0f172a"
        )
        title.pack(anchor=tk.W)

        subtitle = tk.Label(
            header,
            text="Configure application settings and preferences.",
            font=("Segoe UI", 11),
            fg="#94a3b8",
            bg="#0f172a"
        )
        subtitle.pack(anchor=tk.W, pady=(6, 0))

        # Settings container
        settings_container = tk.Frame(self.frame, bg="#0f172a")
        settings_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Database settings
        db_frame = tk.LabelFrame(
            settings_container,
            text="Database Configuration",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#1e293b",
            padx=20,
            pady=15
        )
        db_frame.pack(fill=tk.X, pady=(0, 15))

        db_info = tk.Label(
            db_frame,
            text="Database connection is configured via environment variables.\n"
                 "Set DATABASE_URL or TEQ_DATABASE_URL in your environment.",
            font=("Arial", 10),
            fg="#cbd5e1",
            bg="#1e293b",
            justify=tk.LEFT
        )
        db_info.pack(anchor=tk.W)

        # Automation settings
        auto_frame = tk.LabelFrame(
            settings_container,
            text="Automation Settings",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#1e293b",
            padx=20,
            pady=15
        )
        auto_frame.pack(fill=tk.X, pady=(0, 15))

        auto_info = tk.Label(
            auto_frame,
            text="Automation settings are configured in the automation scripts.\n"
                 "Check automation/submission/ directory for configuration options.",
            font=("Arial", 10),
            fg="#cbd5e1",
            bg="#1e293b",
            justify=tk.LEFT
        )
        auto_info.pack(anchor=tk.W)

        # About
        about_frame = tk.LabelFrame(
            settings_container,
            text="About",
            font=("Arial", 12, "bold"),
            fg="white",
            bg="#1e293b",
            padx=20,
            pady=15
        )
        about_frame.pack(fill=tk.X)

        about_text = tk.Label(
            about_frame,
            text="TEQSmartSubmit v0.1.0\n"
                 "Automation Control Center\n\n"
                 "Python + PostgreSQL Desktop Application",
            font=("Arial", 10),
            fg="#cbd5e1",
            bg="#1e293b",
            justify=tk.LEFT
        )
        about_text.pack(anchor=tk.W)

