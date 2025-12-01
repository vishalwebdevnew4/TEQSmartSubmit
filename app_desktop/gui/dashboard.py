"""Dashboard frame."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
import asyncio

import sys
import os

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.db.session import get_session
from app.db.models.domain import Domain
from app.db.models.submission import SubmissionLog
from app.db.models.template import Template
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from theme import Colors, Fonts, Spacing, ButtonStyle, LabelStyle


class DashboardFrame:
    """Dashboard view."""

    def __init__(self, parent):
        """Initialize dashboard frame."""
        self.frame = tk.Frame(parent, bg=Colors.BG_PRIMARY)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        """Create dashboard widgets."""
        # Header with modern styling
        header = tk.Frame(self.frame, bg=Colors.BG_PRIMARY, pady=Spacing.XXXL)
        header.pack(fill=tk.X, padx=Spacing.XXL, pady=(Spacing.XXL, Spacing.LG))

        title = tk.Label(
            header,
            text="Overview",
            font=Fonts.get_title_font(),
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_PRIMARY
        )
        title.pack(anchor=tk.W)

        subtitle = tk.Label(
            header,
            text="Monitor automation health and recent submission activity.",
            font=Fonts.get_body_font(),
            fg=Colors.TEXT_MUTED,
            bg=Colors.BG_PRIMARY
        )
        subtitle.pack(anchor=tk.W, pady=(Spacing.XS, 0))

        # Stats container with better spacing
        self.stats_frame = tk.Frame(self.frame, bg=Colors.BG_PRIMARY)
        self.stats_frame.pack(fill=tk.X, padx=Spacing.XXL, pady=(Spacing.XXL, Spacing.LG))

        # Stats will be populated by load_data
        self.stats_labels = {}

        # Recent activity
        activity_frame = tk.Frame(self.frame, bg="#0f172a")
        activity_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        activity_title = tk.Label(
            activity_frame,
            text="Recent Activity",
            font=("Segoe UI", 18, "bold"),
            fg="white",
            bg="#0f172a"
        )
        activity_title.pack(anchor=tk.W, pady=(0, 12))

        # Activity listbox with scrollbar
        listbox_frame = tk.Frame(activity_frame, bg="#1e293b", relief=tk.FLAT)
        listbox_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(listbox_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.activity_listbox = tk.Listbox(
            listbox_frame,
            bg="#1e293b",
            fg="white",
            font=("Segoe UI", 10),
            selectbackground="#334155",
            relief=tk.FLAT,
            borderwidth=0,
            yscrollcommand=scrollbar.set,
            activestyle="none"
        )
        self.activity_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.activity_listbox.yview)

    def load_data(self):
        """Load dashboard data."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            data = loop.run_until_complete(self.fetch_data())
            loop.close()
            self.update_display(data)
        except Exception as e:
            print(f"Error loading dashboard data: {e}")

    async def fetch_data(self):
        """Fetch dashboard data from database."""
        async for session in get_session():
            total_domains = await session.scalar(select(func.count(Domain.id)))
            active_domains = await session.scalar(select(func.count(Domain.id)).where(Domain.is_active == True))
            domains_with_forms = await session.scalar(
                select(func.count(Domain.id)).where(Domain.contact_check_status == "found")
            )
            total_submissions = await session.scalar(select(func.count(SubmissionLog.id)))
            success_submissions = await session.scalar(
                select(func.count(SubmissionLog.id)).where(SubmissionLog.status == "success")
            )
            failed_submissions = await session.scalar(
                select(func.count(SubmissionLog.id)).where(SubmissionLog.status == "failed")
            )

            # Recent activity
            recent_result = await session.execute(
                select(SubmissionLog)
                .options(selectinload(SubmissionLog.domain))
                .order_by(SubmissionLog.created_at.desc())
                .limit(10)
            )
            recent_activity = recent_result.scalars().all()

            return {
                "total_domains": total_domains or 0,
                "active_domains": active_domains or 0,
                "domains_with_forms": domains_with_forms or 0,
                "total_submissions": total_submissions or 0,
                "success_submissions": success_submissions or 0,
                "failed_submissions": failed_submissions or 0,
                "recent_activity": recent_activity,
            }

    def update_display(self, data):
        """Update dashboard display with data."""
        # Clear existing stats
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        # Calculate success rate
        success_rate = (
            round((data["success_submissions"] / data["total_submissions"] * 100))
            if data["total_submissions"] > 0
            else 0
        )

        # Create stat cards
        stats = [
            ("Total Domains", str(data["total_domains"]), f"{data['active_domains']} active", "white"),
            ("Forms Found", str(data["domains_with_forms"]), "Ready for automation", "#10b981"),
            ("Success Rate", f"{success_rate}%", f"{data['success_submissions']} of {data['total_submissions']} succeeded", "white"),
            ("Total Submissions", str(data["total_submissions"]), "All time submissions", "white"),
        ]

        for i, (label, value, subtitle, color) in enumerate(stats):
            # Card with better padding and spacing
            card = tk.Frame(self.stats_frame, bg="#1e293b", relief=tk.FLAT, padx=20, pady=20)
            card.grid(row=0, column=i, padx=(0, 12) if i < len(stats) - 1 else (0, 0), sticky="ew")

            label_widget = tk.Label(
                card,
                text=label.upper(),
                font=("Segoe UI", 9),
                fg="#94a3b8",
                bg="#1e293b"
            )
            label_widget.pack(anchor=tk.W)

            value_widget = tk.Label(
                card,
                text=value,
                font=("Segoe UI", 28, "bold"),
                fg=color,
                bg="#1e293b"
            )
            value_widget.pack(anchor=tk.W, pady=(8, 0))

            subtitle_widget = tk.Label(
                card,
                text=subtitle,
                font=("Segoe UI", 9),
                fg="#64748b",
                bg="#1e293b"
            )
            subtitle_widget.pack(anchor=tk.W, pady=(4, 0))

        # Configure grid weights
        self.stats_frame.grid_columnconfigure(0, weight=1)
        self.stats_frame.grid_columnconfigure(1, weight=1)
        self.stats_frame.grid_columnconfigure(2, weight=1)
        self.stats_frame.grid_columnconfigure(3, weight=1)

        # Update activity list
        self.activity_listbox.delete(0, tk.END)
        for activity in data["recent_activity"]:
            domain_url = activity.domain.url if activity.domain else "Unknown"
            status = activity.status
            timestamp = activity.created_at.strftime("%Y-%m-%d %H:%M:%S") if activity.created_at else "N/A"
            self.activity_listbox.insert(
                tk.END,
                f"[{timestamp}] {domain_url} - {status}"
            )

