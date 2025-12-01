"""Auto-save functionality for GUI forms."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, Callable


class AutoSaveManager:
    """Manages auto-save functionality for form data."""
    
    def __init__(self, app_name: str = "TEQSmartSubmit"):
        """Initialize auto-save manager."""
        self.app_name = app_name
        self.cache_dir = Path.home() / ".cache" / app_name.lower() / "autosave"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def save_form_data(self, form_id: str, data: Dict[str, Any]) -> None:
        """Save form data to cache."""
        cache_file = self.cache_dir / f"{form_id}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving form data: {e}")
    
    def load_form_data(self, form_id: str) -> Optional[Dict[str, Any]]:
        """Load cached form data."""
        cache_file = self.cache_dir / f"{form_id}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading form data: {e}")
        return None
    
    def clear_form_data(self, form_id: str) -> None:
        """Clear cached form data."""
        cache_file = self.cache_dir / f"{form_id}.json"
        if cache_file.exists():
            try:
                cache_file.unlink()
            except Exception as e:
                print(f"Error clearing form data: {e}")
    
    def has_unsaved_data(self, form_id: str) -> bool:
        """Check if there's unsaved data for a form."""
        cache_file = self.cache_dir / f"{form_id}.json"
        return cache_file.exists()


class LivePreviewManager:
    """Manages live preview functionality."""
    
    def __init__(self):
        """Initialize live preview manager."""
        self.preview_callbacks: Dict[str, Callable] = {}
        self.update_delays: Dict[str, int] = {}
        self.timers: Dict[str, Any] = {}
    
    def register_preview(self, preview_id: str, callback: Callable, delay_ms: int = 500):
        """Register a preview callback with auto-update delay."""
        self.preview_callbacks[preview_id] = callback
        self.update_delays[preview_id] = delay_ms
    
    def update_preview(self, preview_id: str, root, data: Any = None):
        """Update preview with optional data."""
        if preview_id in self.preview_callbacks:
            try:
                self.preview_callbacks[preview_id](data)
            except Exception as e:
                print(f"Error updating preview {preview_id}: {e}")
    
    def schedule_update(self, preview_id: str, root, data: Any = None):
        """Schedule a delayed preview update (debounced)."""
        delay = self.update_delays.get(preview_id, 500)
        
        # Cancel existing timer if any
        if preview_id in self.timers:
            try:
                root.after_cancel(self.timers[preview_id])
            except:
                pass
        
        # Schedule new update
        timer_id = root.after(delay, lambda: self.update_preview(preview_id, root, data))
        self.timers[preview_id] = timer_id


# Global instances
_auto_save_manager = None
_preview_manager = None


def get_auto_save_manager() -> AutoSaveManager:
    """Get or create global auto-save manager."""
    global _auto_save_manager
    if _auto_save_manager is None:
        _auto_save_manager = AutoSaveManager()
    return _auto_save_manager


def get_preview_manager() -> LivePreviewManager:
    """Get or create global preview manager."""
    global _preview_manager
    if _preview_manager is None:
        _preview_manager = LivePreviewManager()
    return _preview_manager


