"""Templates management frame."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import asyncio

import sys
import os

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.db.session import get_session
from app.db.models.template import Template
from app.db.models.domain import Domain
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class TemplatesFrame:
    """Templates management view."""

    def __init__(self, parent):
        """Initialize templates frame."""
        self.frame = tk.Frame(parent, bg="#0f172a")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.templates = []
        self.create_widgets()
        self.load_templates()

    def create_widgets(self):
        """Create templates widgets."""
        # Header
        header = tk.Frame(self.frame, bg="#0f172a", pady=20)
        header.pack(fill=tk.X, padx=20)

        title = tk.Label(
            header,
            text="Form Templates",
            font=("Segoe UI", 26, "bold"),
            fg="white",
            bg="#0f172a"
        )
        title.pack(anchor=tk.W)

        subtitle = tk.Label(
            header,
            text="Create reusable mappings that the automation engine relies on.",
            font=("Segoe UI", 11),
            fg="#94a3b8",
            bg="#0f172a"
        )
        subtitle.pack(anchor=tk.W, pady=(6, 0))

        # Toolbar
        toolbar = tk.Frame(self.frame, bg="#0f172a", pady=10)
        toolbar.pack(fill=tk.X, padx=20)

        add_btn = tk.Button(
            toolbar,
            text="+ New Template",
            font=("Arial", 10),
            bg="#6366f1",
            fg="white",
            activebackground="#4f46e5",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.add_template
        )
        add_btn.pack(side=tk.LEFT, padx=(0, 10))

        refresh_btn = tk.Button(
            toolbar,
            text="Refresh",
            font=("Arial", 10),
            bg="#475569",
            fg="white",
            activebackground="#64748b",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.load_templates
        )
        refresh_btn.pack(side=tk.LEFT)

        # Templates list
        list_frame = tk.Frame(self.frame, bg="#0f172a")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Scrollable frame for templates
        canvas = tk.Canvas(list_frame, bg="#0f172a", highlightthickness=0)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#0f172a")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.templates_container = scrollable_frame

    def load_templates(self):
        """Load templates from database."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            templates = loop.run_until_complete(self.fetch_templates())
            loop.close()
            self.update_display(templates)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load templates: {str(e)}")

    async def fetch_templates(self):
        """Fetch templates from database."""
        async for session in get_session():
            result = await session.execute(
                select(Template)
                .options(selectinload(Template.domain))
                .order_by(Template.created_at.desc())
            )
            return result.scalars().all()

    def update_display(self, templates):
        """Update templates display."""
        self.templates = templates
        
        # Clear existing
        for widget in self.templates_container.winfo_children():
            widget.destroy()

        if not templates:
            no_templates = tk.Label(
                self.templates_container,
                text="No templates found. Create your first template to get started.",
                font=("Arial", 11),
                fg="#94a3b8",
                bg="#0f172a"
            )
            no_templates.pack(pady=50)
            return

        # Display templates
        for template in templates:
            self.create_template_card(template)

    def create_template_card(self, template):
        """Create a template card."""
        card = tk.Frame(self.templates_container, bg="#1e293b", relief=tk.FLAT, padx=20, pady=15)
        card.pack(fill=tk.X, pady=10)

        # Header
        header = tk.Frame(card, bg="#1e293b")
        header.pack(fill=tk.X, pady=(0, 10))

        name_label = tk.Label(
            header,
            text=template.name,
            font=("Arial", 16, "bold"),
            fg="white",
            bg="#1e293b"
        )
        name_label.pack(side=tk.LEFT)

        button_frame = tk.Frame(header, bg="#1e293b")
        button_frame.pack(side=tk.RIGHT)

        edit_btn = tk.Button(
            button_frame,
            text="Edit",
            font=("Arial", 9),
            bg="#475569",
            fg="white",
            activebackground="#64748b",
            relief=tk.FLAT,
            padx=12,
            pady=5,
            cursor="hand2",
            command=lambda: self.edit_template(template)
        )
        edit_btn.pack(side=tk.LEFT, padx=(0, 5))

        delete_btn = tk.Button(
            button_frame,
            text="Delete",
            font=("Arial", 9),
            bg="#dc2626",
            fg="white",
            activebackground="#b91c1c",
            relief=tk.FLAT,
            padx=12,
            pady=5,
            cursor="hand2",
            command=lambda: self.delete_template(template)
        )
        delete_btn.pack(side=tk.LEFT)

        # Description
        if template.description:
            desc_label = tk.Label(
                card,
                text=template.description,
                font=("Arial", 10),
                fg="#cbd5e1",
                bg="#1e293b"
            )
            desc_label.pack(anchor=tk.W, pady=(0, 10))

        # Domain info
        domain_text = f"Domain: {template.domain.url}" if template.domain else "🌐 Universal Template (works with all domains)"
        domain_label = tk.Label(
            card,
            text=domain_text,
            font=("Arial", 9),
            fg="#94a3b8" if template.domain else "#6366f1",
            bg="#1e293b"
        )
        domain_label.pack(anchor=tk.W, pady=(0, 10))

        # Field mappings preview
        mappings = template.field_mappings or {}
        if mappings:
            fields_label = tk.Label(
                card,
                text="Mapped fields:",
                font=("Arial", 9),
                fg="#94a3b8",
                bg="#1e293b"
            )
            fields_label.pack(anchor=tk.W, pady=(0, 5))

            fields_text = ", ".join(mappings.keys())
            fields_display = tk.Label(
                card,
                text=fields_text,
                font=("Arial", 9),
                fg="#cbd5e1",
                bg="#1e293b",
                wraplength=600
            )
            fields_display.pack(anchor=tk.W)

    def add_template(self):
        """Show add template dialog."""
        dialog = TemplateDialog(self.frame, None)
        self.frame.wait_window(dialog.dialog)
        if dialog.saved:
            self.load_templates()

    def edit_template(self, template):
        """Edit template."""
        dialog = TemplateDialog(self.frame, template)
        self.frame.wait_window(dialog.dialog)
        if dialog.saved:
            self.load_templates()

    def delete_template(self, template):
        """Delete template."""
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete template '{template.name}'?"):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.delete_template_async(template.id))
                loop.close()
                self.load_templates()
                messagebox.showinfo("Success", "Template deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete template: {str(e)}")

    async def delete_template_async(self, template_id):
        """Async delete template."""
        async for session in get_session():
            result = await session.execute(select(Template).where(Template.id == template_id))
            template = result.scalar_one_or_none()
            if template:
                await session.delete(template)
                await session.commit()


class TemplateDialog:
    """Template add/edit dialog."""

    def __init__(self, parent, template=None):
        """Initialize template dialog."""
        self.template = template
        self.saved = False
        self.domains = []
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Template" if template else "New Template")
        self.dialog.geometry("700x600")
        self.dialog.configure(bg="#0f172a")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"700x600+{x}+{y}")

        self.load_domains()
        self.create_widgets()

    async def fetch_domains(self):
        """Fetch domains."""
        async for session in get_session():
            result = await session.execute(select(Domain).order_by(Domain.url))
            return result.scalars().all()

    def load_domains(self):
        """Load domains."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self.domains = loop.run_until_complete(self.fetch_domains())
            loop.close()
        except Exception as e:
            print(f"Error loading domains: {e}")
            self.domains = []

    def create_widgets(self):
        """Create dialog widgets."""
        container = tk.Frame(self.dialog, bg="#0f172a", padx=30, pady=30)
        container.pack(fill=tk.BOTH, expand=True)

        # Name
        name_label = tk.Label(
            container,
            text="Name *",
            font=("Arial", 10),
            fg="#cbd5e1",
            bg="#0f172a",
            anchor=tk.W
        )
        name_label.pack(fill=tk.X, pady=(0, 5))

        self.name_entry = tk.Entry(
            container,
            font=("Arial", 11),
            bg="#1e293b",
            fg="white",
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#334155",
            highlightcolor="#6366f1"
        )
        self.name_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)

        # Description
        desc_label = tk.Label(
            container,
            text="Description",
            font=("Arial", 10),
            fg="#cbd5e1",
            bg="#0f172a",
            anchor=tk.W
        )
        desc_label.pack(fill=tk.X, pady=(0, 5))

        self.desc_entry = tk.Entry(
            container,
            font=("Arial", 11),
            bg="#1e293b",
            fg="white",
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#334155",
            highlightcolor="#6366f1"
        )
        self.desc_entry.pack(fill=tk.X, pady=(0, 15), ipady=8)

        # Domain
        domain_label = tk.Label(
            container,
            text="Domain (optional - leave empty for universal template)",
            font=("Arial", 10),
            fg="#cbd5e1",
            bg="#0f172a",
            anchor=tk.W
        )
        domain_label.pack(fill=tk.X, pady=(0, 5))

        self.domain_var = tk.StringVar()
        domain_combo = ttk.Combobox(
            container,
            textvariable=self.domain_var,
            font=("Arial", 11),
            state="readonly"
        )
        domain_combo["values"] = ["🌐 Universal (all domains)"] + [d.url for d in self.domains]
        domain_combo.current(0)
        domain_combo.pack(fill=tk.X, pady=(0, 15), ipady=8)

        # Field mappings
        mappings_label = tk.Label(
            container,
            text="Field Mappings (JSON) *",
            font=("Arial", 10),
            fg="#cbd5e1",
            bg="#0f172a",
            anchor=tk.W
        )
        mappings_label.pack(fill=tk.X, pady=(0, 5))

        self.mappings_text = scrolledtext.ScrolledText(
            container,
            font=("Courier", 10),
            bg="#1e293b",
            fg="white",
            insertbackground="white",
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#334155",
            highlightcolor="#6366f1",
            height=15
        )
        self.mappings_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Buttons
        button_frame = tk.Frame(container, bg="#0f172a")
        button_frame.pack(fill=tk.X)

        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            font=("Arial", 10),
            bg="#475569",
            fg="white",
            activebackground="#64748b",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.dialog.destroy
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))

        save_btn = tk.Button(
            button_frame,
            text="Save",
            font=("Arial", 10, "bold"),
            bg="#6366f1",
            fg="white",
            activebackground="#4f46e5",
            relief=tk.FLAT,
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.save
        )
        save_btn.pack(side=tk.RIGHT)

        # Populate if editing
        if self.template:
            self.name_entry.insert(0, self.template.name)
            if self.template.description:
                self.desc_entry.insert(0, self.template.description)
            if self.template.domain:
                domain_combo.set(self.template.domain.url)
            self.mappings_text.insert("1.0", json.dumps(self.template.field_mappings, indent=2))
        else:
            self.mappings_text.insert("1.0", '{\n  "name": "input[name=\\"name\\"]",\n  "email": "input#email",\n  "message": "textarea"\n}')

    def save(self):
        """Save template."""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Name is required")
            return

        try:
            mappings_text = self.mappings_text.get("1.0", tk.END).strip()
            field_mappings = json.loads(mappings_text)
            if not isinstance(field_mappings, dict):
                raise ValueError("Field mappings must be a JSON object")
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON in field mappings")
            return
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.save_async(name, field_mappings))
            loop.close()
            self.saved = True
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save template: {str(e)}")

    async def save_async(self, name, field_mappings):
        """Async save template."""
        async for session in get_session():
            description = self.desc_entry.get().strip() or None
            
            # Get domain ID
            domain_id = None
            selected_domain = self.domain_var.get()
            if selected_domain and selected_domain != "🌐 Universal (all domains)":
                domain = next((d for d in self.domains if d.url == selected_domain), None)
                if domain:
                    domain_id = domain.id

            if self.template:
                # Update existing
                self.template.name = name
                self.template.description = description
                self.template.field_mappings = field_mappings
                self.template.domain_id = domain_id
                session.add(self.template)
            else:
                # Create new
                template = Template(
                    name=name,
                    description=description,
                    field_mappings=field_mappings,
                    domain_id=domain_id
                )
                session.add(template)
            
            await session.commit()

