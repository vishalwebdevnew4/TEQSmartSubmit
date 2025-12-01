"""Domains management frame."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox

import sys
import os

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.db.session import get_session
from app.db.models.domain import Domain
from sqlalchemy import select
from sqlalchemy.orm import selectinload

# Import CSV upload dialog
from csv_upload import CSVUploadDialog
from theme import Colors, Fonts, Spacing, ButtonStyle, InputStyle, LabelStyle


class DomainsFrame:
    """Domains management view."""

    def __init__(self, parent):
        """Initialize domains frame."""
        self.frame = tk.Frame(parent, bg="#0f172a")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        self.domains = []
        self.create_widgets()
        self.load_domains()

    def create_widgets(self):
        """Create domains widgets."""
        # Header with modern styling
        header = tk.Frame(self.frame, bg=Colors.BG_PRIMARY, pady=Spacing.XXXL)
        header.pack(fill=tk.X, padx=Spacing.XXL, pady=(Spacing.XXL, Spacing.LG))

        title = tk.Label(
            header,
            text="Domain Manager",
            font=Fonts.get_title_font(),
            fg=Colors.TEXT_PRIMARY,
            bg=Colors.BG_PRIMARY
        )
        title.pack(anchor=tk.W)

        subtitle = tk.Label(
            header,
            text="Manage the queue of domains for automated submissions.",
            font=Fonts.get_body_font(),
            fg=Colors.TEXT_MUTED,
            bg=Colors.BG_PRIMARY
        )
        subtitle.pack(anchor=tk.W, pady=(Spacing.XS, 0))

        # Toolbar with modern button styling
        toolbar = tk.Frame(self.frame, bg=Colors.BG_PRIMARY, pady=Spacing.MD)
        toolbar.pack(fill=tk.X, padx=Spacing.XXL)

        add_btn = tk.Button(
            toolbar,
            text="+ Add Domain",
            **ButtonStyle.primary(),
            command=self.add_domain
        )
        add_btn.pack(side=tk.LEFT, padx=(0, Spacing.MD))

        upload_csv_btn = tk.Button(
            toolbar,
            text="📄 Upload CSV",
            **ButtonStyle.success(),
            command=self.upload_csv
        )
        upload_csv_btn.pack(side=tk.LEFT, padx=(0, Spacing.MD))

        refresh_btn = tk.Button(
            toolbar,
            text="Refresh",
            **ButtonStyle.secondary(),
            command=self.load_domains
        )
        refresh_btn.pack(side=tk.LEFT)

        # Table frame with modern styling
        table_frame = tk.Frame(self.frame, bg=Colors.BG_TERTIARY, relief=tk.FLAT)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=Spacing.XXL, pady=Spacing.LG)

        # Treeview for domains
        columns = ("URL", "Status", "Category", "Contact Status", "Actions")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview"
        )

        # Configure columns
        self.tree.heading("URL", text="Domain URL")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Contact Status", text="Contact Status")
        self.tree.heading("Actions", text="Actions")

        self.tree.column("URL", width=400)
        self.tree.column("Status", width=100)
        self.tree.column("Category", width=150)
        self.tree.column("Contact Status", width=150)
        self.tree.column("Actions", width=150)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind double-click
        self.tree.bind("<Double-1>", self.edit_domain)

        # Context menu
        self.context_menu = tk.Menu(self.frame, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self.edit_selected)
        self.context_menu.add_command(label="Delete", command=self.delete_selected)
        self.tree.bind("<Button-3>", self.show_context_menu)

    def load_domains(self):
        """Load domains from database."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            domains = loop.run_until_complete(self.fetch_domains())
            loop.close()
            if domains is None:
                domains = []
            self.update_tree(domains)
        except Exception as e:
            error_msg = f"Failed to load domains:\n\n{str(e)}"
            import traceback
            error_details = traceback.format_exc()
            print(f"Error loading domains:\n{error_details}")
            messagebox.showerror("Error Loading Domains", error_msg)

    async def fetch_domains(self):
        """Fetch domains from database."""
        try:
            async for session in get_session():
                try:
                    result = await session.execute(
                        select(Domain)
                        .options(selectinload(Domain.templates))
                        .order_by(Domain.created_at.desc())
                    )
                    domains = result.scalars().all()
                    return domains if domains else []
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

    def update_tree(self, domains):
        """Update treeview with domains."""
        self.domains = domains
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add domains
        for domain in domains:
            status = "Active" if domain.is_active else "Disabled"
            contact_status = domain.contact_check_status or "Not checked"
            category = domain.category or "—"
            
            self.tree.insert(
                "",
                tk.END,
                values=(domain.url, status, category, contact_status, "Edit | Delete"),
                tags=(domain.id,)
            )

    def add_domain(self):
        """Show add domain dialog."""
        dialog = DomainDialog(self.frame, None)
        self.frame.wait_window(dialog.dialog)
        if dialog.saved:
            self.load_domains()

    def edit_domain(self, event):
        """Edit domain on double-click."""
        selection = self.tree.selection()
        if selection:
            self.edit_selected()

    def edit_selected(self):
        """Edit selected domain."""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        domain_id = item["tags"][0]
        domain = next((d for d in self.domains if d.id == domain_id), None)
        
        if domain:
            dialog = DomainDialog(self.frame, domain)
            self.frame.wait_window(dialog.dialog)
            if dialog.saved:
                self.load_domains()

    def delete_selected(self):
        """Delete selected domain."""
        selection = self.tree.selection()
        if not selection:
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this domain?"):
            item = self.tree.item(selection[0])
            domain_id = item["tags"][0]
            self.delete_domain(domain_id)

    def delete_domain(self, domain_id):
        """Delete domain from database."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.delete_domain_async(domain_id))
            loop.close()
            self.load_domains()
            messagebox.showinfo("Success", "Domain deleted successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete domain: {str(e)}")

    async def delete_domain_async(self, domain_id):
        """Async delete domain."""
        async for session in get_session():
            result = await session.execute(select(Domain).where(Domain.id == domain_id))
            domain = result.scalar_one_or_none()
            if domain:
                await session.delete(domain)
                await session.commit()

    def show_context_menu(self, event):
        """Show context menu."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def upload_csv(self):
        """Show CSV upload dialog."""
        dialog = CSVUploadDialog(self.frame)
        self.frame.wait_window(dialog.dialog)
        if dialog.imported:
            self.load_domains()
            messagebox.showinfo(
                "Success",
                f"CSV upload completed!\n\n"
                f"✅ Created: {dialog.results['created']}\n"
                f"⏭️  Skipped: {dialog.results['skipped']}\n"
                f"❌ Errors: {len(dialog.results['errors'])}"
            )


class DomainDialog:
    """Domain add/edit dialog."""

    def __init__(self, parent, domain=None):
        """Initialize domain dialog."""
        self.domain = domain
        self.saved = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Domain" if domain else "Add Domain")
        self.dialog.geometry("540x360")
        self.dialog.configure(bg=Colors.BG_PRIMARY)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (540 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (360 // 2)
        self.dialog.geometry(f"540x360+{x}+{y}")

        self.create_widgets()

    def create_widgets(self):
        """Create dialog widgets."""
        container = tk.Frame(self.dialog, bg=Colors.BG_PRIMARY, padx=Spacing.XXXL, pady=Spacing.XXXL)
        container.pack(fill=tk.BOTH, expand=True)

        # URL field with modern styling
        url_label = tk.Label(
            container,
            text="Domain URL *",
            font=Fonts.get_body_font(),
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_PRIMARY,
            anchor=tk.W
        )
        url_label.pack(fill=tk.X, pady=(0, Spacing.XS))

        self.url_entry = tk.Entry(
            container,
            font=Fonts.get_body_font(),
            bg=Colors.INPUT_BG,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.ACCENT_PRIMARY,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=2,
            highlightbackground=Colors.INPUT_BORDER,
            highlightcolor=Colors.INPUT_FOCUS
        )
        self.url_entry.pack(fill=tk.X, pady=(0, Spacing.LG), ipady=12)

        # Category field
        category_label = tk.Label(
            container,
            text="Category",
            font=Fonts.get_body_font(),
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_PRIMARY,
            anchor=tk.W
        )
        category_label.pack(fill=tk.X, pady=(0, Spacing.XS))

        self.category_entry = tk.Entry(
            container,
            font=Fonts.get_body_font(),
            bg=Colors.INPUT_BG,
            fg=Colors.TEXT_PRIMARY,
            insertbackground=Colors.ACCENT_PRIMARY,
            relief=tk.FLAT,
            borderwidth=0,
            highlightthickness=2,
            highlightbackground=Colors.INPUT_BORDER,
            highlightcolor=Colors.INPUT_FOCUS
        )
        self.category_entry.pack(fill=tk.X, pady=(0, Spacing.LG), ipady=12)

        # Active checkbox with modern styling
        self.active_var = tk.BooleanVar(value=True)
        active_check = tk.Checkbutton(
            container,
            text="Active",
            font=Fonts.get_body_font(),
            fg=Colors.TEXT_SECONDARY,
            bg=Colors.BG_PRIMARY,
            selectcolor=Colors.BG_ELEVATED,
            activebackground=Colors.BG_PRIMARY,
            activeforeground=Colors.ACCENT_PRIMARY,
            variable=self.active_var
        )
        active_check.pack(anchor=tk.W, pady=(0, Spacing.XXL))

        # Buttons with modern styling
        button_frame = tk.Frame(container, bg=Colors.BG_PRIMARY)
        button_frame.pack(fill=tk.X)

        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            **ButtonStyle.secondary(),
            command=self.dialog.destroy
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(Spacing.MD, 0))

        save_btn = tk.Button(
            button_frame,
            text="Save",
            **ButtonStyle.primary(),
            command=self.save
        )
        save_btn.pack(side=tk.RIGHT)

        # Populate if editing
        if self.domain:
            self.url_entry.insert(0, self.domain.url)
            if self.domain.category:
                self.category_entry.insert(0, self.domain.category)
            self.active_var.set(self.domain.is_active)

    def save(self):
        """Save domain."""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "URL is required")
            return

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.save_async(url))
            loop.close()
            self.saved = True
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save domain: {str(e)}")

    async def save_async(self, url):
        """Async save domain."""
        from app.db.models.domain import Domain
        
        async for session in get_session():
            category = self.category_entry.get().strip() or None
            is_active = self.active_var.get()

            if self.domain:
                # Update existing
                self.domain.url = url
                self.domain.category = category
                self.domain.is_active = is_active
                session.add(self.domain)
            else:
                # Create new
                domain = Domain(
                    url=url,
                    category=category,
                    is_active=is_active
                )
                session.add(domain)
            
            await session.commit()

