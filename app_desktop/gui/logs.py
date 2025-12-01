"""Logs viewer frame."""

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
from app.db.models.submission import SubmissionLog
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class LogsFrame:
    """Logs viewer view."""

    def __init__(self, parent):
        """Initialize logs frame."""
        self.frame = tk.Frame(parent, bg="#0f172a")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_widgets()
        self.load_logs()

    def create_widgets(self):
        """Create logs widgets."""
        # Header
        header = tk.Frame(self.frame, bg="#0f172a", pady=20)
        header.pack(fill=tk.X, padx=20)

        title = tk.Label(
            header,
            text="Submission Logs",
            font=("Segoe UI", 26, "bold"),
            fg="white",
            bg="#0f172a"
        )
        title.pack(anchor=tk.W)

        subtitle = tk.Label(
            header,
            text="View automation submission history and results.",
            font=("Segoe UI", 11),
            fg="#94a3b8",
            bg="#0f172a"
        )
        subtitle.pack(anchor=tk.W, pady=(6, 0))

        # Toolbar
        toolbar = tk.Frame(self.frame, bg="#0f172a", pady=10)
        toolbar.pack(fill=tk.X, padx=20)

        refresh_btn = tk.Button(
            toolbar,
            text="Refresh",
            font=("Segoe UI", 10),
            bg="#475569",
            fg="white",
            activebackground="#64748b",
            relief=tk.FLAT,
            padx=18,
            pady=10,
            cursor="hand2",
            borderwidth=0,
            highlightthickness=0,
            command=self.load_logs
        )
        refresh_btn.pack(side=tk.LEFT)

        # Table frame
        table_frame = tk.Frame(self.frame, bg="#1e293b", relief=tk.FLAT)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Treeview for logs
        columns = ("Timestamp", "URL", "Status", "Domain", "Template", "Message")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview"
        )

        # Configure columns
        self.tree.heading("Timestamp", text="Timestamp")
        self.tree.heading("URL", text="URL")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Domain", text="Domain")
        self.tree.heading("Template", text="Template")
        self.tree.heading("Message", text="Message")

        self.tree.column("Timestamp", width=180)
        self.tree.column("URL", width=300)
        self.tree.column("Status", width=100)
        self.tree.column("Domain", width=200)
        self.tree.column("Template", width=150)
        self.tree.column("Message", width=400)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind double-click to show details
        self.tree.bind("<Double-1>", self.show_details)

    def load_logs(self):
        """Load logs from database."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            logs = loop.run_until_complete(self.fetch_logs())
            loop.close()
            if logs is None:
                logs = []
            self.update_tree(logs)
        except Exception as e:
            error_msg = f"Failed to load submission logs:\n\n{str(e)}"
            import traceback
            error_details = traceback.format_exc()
            print(f"Error loading logs:\n{error_details}")
            messagebox.showerror("Error Loading Logs", error_msg)

    async def fetch_logs(self):
        """Fetch logs from database."""
        try:
            async for session in get_session():
                try:
                    result = await session.execute(
                        select(SubmissionLog)
                        .options(selectinload(SubmissionLog.domain), selectinload(SubmissionLog.template))
                        .order_by(SubmissionLog.created_at.desc())
                        .limit(100)
                    )
                    logs = result.scalars().all()
                    return logs if logs else []
                except Exception as db_error:
                    print(f"Database query error: {db_error}")
                    import traceback
                    traceback.print_exc()
                    raise
        except Exception as e:
            print(f"Session error: {e}")
            import traceback
            traceback.print_exc()
            raise

    def update_tree(self, logs):
        """Update treeview with logs."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add logs
        for log in logs:
            timestamp = log.created_at.strftime("%Y-%m-%d %H:%M:%S") if log.created_at else "N/A"
            domain_url = log.domain.url if log.domain else "—"
            template_name = log.template.name if log.template else "—"
            message_preview = (log.message[:50] + "...") if log.message and len(log.message) > 50 else (log.message or "—")
            
            # Color code by status
            tags = []
            if log.status == "success":
                tags.append("success")
            elif log.status == "failed":
                tags.append("failed")
            elif log.status == "running":
                tags.append("running")

            self.tree.insert(
                "",
                tk.END,
                values=(timestamp, log.url, log.status, domain_url, template_name, message_preview),
                tags=tuple(tags)
            )

        # Configure tag colors
        self.tree.tag_configure("success", foreground="#10b981")
        self.tree.tag_configure("failed", foreground="#ef4444")
        self.tree.tag_configure("running", foreground="#3b82f6")

    def show_details(self, event):
        """Show log details dialog."""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        # Get full log details (would need to fetch from database or store reference)
        # For now, just show the message
        message = item["values"][5] if len(item["values"]) > 5 else "No details available"
        
        dialog = tk.Toplevel(self.frame)
        dialog.title("Log Details")
        dialog.geometry("800x600")
        dialog.configure(bg="#0f172a")
        
        text_widget = tk.Text(
            dialog,
            bg="#1e293b",
            fg="white",
            font=("Courier", 10),
            wrap=tk.WORD,
            padx=20,
            pady=20
        )
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert("1.0", message)
        text_widget.config(state=tk.DISABLED)

