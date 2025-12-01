"""CSV upload dialog for bulk domain import."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import asyncio
import csv
from urllib.parse import urlparse

import sys
import os

# Add backend to path for imports
backend_path = os.path.join(os.path.dirname(__file__), '..', '..', 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.db.session import get_session
from app.db.models.domain import Domain
from sqlalchemy import select


class CSVUploadDialog:
    """CSV upload dialog for bulk domain import."""

    def __init__(self, parent):
        """Initialize CSV upload dialog."""
        self.imported = False
        self.results = {
            "created": 0,
            "skipped": 0,
            "errors": []
        }
        self.csv_data = []
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Upload Domains from CSV")
        self.dialog.geometry("700x550")
        self.dialog.configure(bg="#0f172a")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (550 // 2)
        self.dialog.geometry(f"700x550+{x}+{y}")

        self.create_widgets()

    def create_widgets(self):
        """Create dialog widgets."""
        container = tk.Frame(self.dialog, bg="#0f172a", padx=30, pady=30)
        container.pack(fill=tk.BOTH, expand=True)

        # Title
        title = tk.Label(
            container,
            text="Upload Domains from CSV",
            font=("Segoe UI", 18, "bold"),
            fg="white",
            bg="#0f172a"
        )
        title.pack(anchor=tk.W, pady=(0, 10))

        # Instructions
        instructions = tk.Label(
            container,
            text="Select a CSV file with domains. Expected format:\n"
                 "  url,category (optional)\n"
                 "  https://example.com,interior-design\n"
                 "  https://example2.com,web-design",
            font=("Segoe UI", 10),
            fg="#94a3b8",
            bg="#0f172a",
            justify=tk.LEFT,
            anchor=tk.W
        )
        instructions.pack(anchor=tk.W, pady=(0, 20))

        # File selection
        file_frame = tk.Frame(container, bg="#0f172a")
        file_frame.pack(fill=tk.X, pady=(0, 20))

        self.file_path_var = tk.StringVar(value="No file selected")
        file_label = tk.Label(
            file_frame,
            textvariable=self.file_path_var,
            font=("Segoe UI", 10),
            fg="#cbd5e1",
            bg="#1e293b",
            padx=12,
            pady=10,
            anchor=tk.W,
            relief=tk.FLAT
        )
        file_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        browse_btn = tk.Button(
            file_frame,
            text="Browse...",
            font=("Segoe UI", 10),
            bg="#475569",
            fg="white",
            activebackground="#64748b",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            borderwidth=0,
            command=self.browse_file
        )
        browse_btn.pack(side=tk.RIGHT)

        # Options
        options_frame = tk.Frame(container, bg="#0f172a")
        options_frame.pack(fill=tk.X, pady=(0, 20))

        self.active_var = tk.BooleanVar(value=True)
        active_check = tk.Checkbutton(
            options_frame,
            text="Set domains as active",
            font=("Segoe UI", 10),
            fg="#cbd5e1",
            bg="#0f172a",
            selectcolor="#1e293b",
            activebackground="#0f172a",
            activeforeground="#cbd5e1",
            variable=self.active_var
        )
        active_check.pack(anchor=tk.W)

        # Preview area
        preview_label = tk.Label(
            container,
            text="Preview (first 5 rows):",
            font=("Segoe UI", 10, "bold"),
            fg="white",
            bg="#0f172a",
            anchor=tk.W
        )
        preview_label.pack(anchor=tk.W, pady=(0, 5))

        preview_frame = tk.Frame(container, bg="#1e293b", relief=tk.FLAT)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

        self.preview_text = tk.Text(
            preview_frame,
            bg="#1e293b",
            fg="white",
            font=("Courier", 9),
            wrap=tk.NONE,
            padx=10,
            pady=10,
            state=tk.DISABLED,
            relief=tk.FLAT
        )
        preview_text_scrollbar = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=self.preview_text.yview)
        self.preview_text.configure(yscrollcommand=preview_text_scrollbar.set)
        
        self.preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Buttons
        button_frame = tk.Frame(container, bg="#0f172a")
        button_frame.pack(fill=tk.X)

        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            font=("Segoe UI", 10),
            bg="#475569",
            fg="white",
            activebackground="#64748b",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            borderwidth=0,
            command=self.dialog.destroy
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(10, 0))

        upload_btn = tk.Button(
            button_frame,
            text="Upload",
            font=("Segoe UI", 10, "bold"),
            bg="#10b981",
            fg="white",
            activebackground="#059669",
            relief=tk.FLAT,
            padx=20,
            pady=10,
            cursor="hand2",
            borderwidth=0,
            command=self.upload
        )
        upload_btn.pack(side=tk.RIGHT)

    def browse_file(self):
        """Browse for CSV file."""
        file_path = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            self.file_path_var.set(file_path)
            self.parse_csv(file_path)

    def parse_csv(self, file_path):
        """Parse CSV file and show preview."""
        try:
            self.csv_data = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                # Validate headers
                fieldnames = reader.fieldnames
                if not fieldnames or 'url' not in [f.lower() for f in fieldnames]:
                    messagebox.showerror("Error", "CSV must have a 'url' column")
                    return
                
                # Read data
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
                    url = None
                    category = None
                    
                    # Find URL column (case-insensitive)
                    for key in row.keys():
                        if key.lower() == 'url':
                            url = row[key].strip() if row[key] else None
                        elif key.lower() == 'category':
                            category = row[key].strip() if row[key] else None
                    
                    if url:
                        self.csv_data.append({
                            'url': url,
                            'category': category,
                            'row': row_num
                        })
            
            # Show preview
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete("1.0", tk.END)
            
            preview_rows = self.csv_data[:5]
            if preview_rows:
                preview_text = "url,category\n"
                for item in preview_rows:
                    preview_text += f"{item['url']},{item['category'] or ''}\n"
                if len(self.csv_data) > 5:
                    preview_text += f"\n... and {len(self.csv_data) - 5} more rows"
                self.preview_text.insert("1.0", preview_text)
            else:
                self.preview_text.insert("1.0", "No valid data found in CSV")
            
            self.preview_text.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to parse CSV file:\n{str(e)}")

    def upload(self):
        """Upload domains from CSV."""
        if not self.csv_data:
            messagebox.showerror("Error", "No data to upload. Please select a valid CSV file.")
            return
        
        # Confirm upload
        if not messagebox.askyesno(
            "Confirm Upload",
            f"Upload {len(self.csv_data)} domain(s) from CSV?\n\n"
            f"Domains will be set as {'active' if self.active_var.get() else 'inactive'}."
        ):
            return
        
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.upload_async())
            loop.close()
            self.imported = True
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to upload domains:\n{str(e)}")

    async def upload_async(self):
        """Async upload domains."""
        async for session in get_session():
            is_active = self.active_var.get()
            
            for item in self.csv_data:
                url = item['url']
                category = item['category'] or None
                
                # Validate URL
                if not url:
                    self.results['skipped'] += 1
                    self.results['errors'].append(f"Row {item['row']}: Empty URL")
                    continue
                
                try:
                    # Validate URL format
                    parsed = urlparse(url)
                    if not parsed.scheme or not parsed.netloc:
                        self.results['skipped'] += 1
                        self.results['errors'].append(f"Row {item['row']}: Invalid URL format: {url}")
                        continue
                except Exception:
                    self.results['skipped'] += 1
                    self.results['errors'].append(f"Row {item['row']}: Invalid URL format: {url}")
                    continue
                
                # Check if domain already exists
                result = await session.execute(
                    select(Domain).where(Domain.url == url)
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    self.results['skipped'] += 1
                    continue
                
                try:
                    # Create new domain
                    domain = Domain(
                        url=url,
                        category=category,
                        is_active=is_active
                    )
                    session.add(domain)
                    await session.commit()
                    self.results['created'] += 1
                except Exception as e:
                    await session.rollback()
                    self.results['skipped'] += 1
                    self.results['errors'].append(f"Row {item['row']}: {str(e)}")

