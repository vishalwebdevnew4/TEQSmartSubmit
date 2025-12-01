"""Desktop application entry point."""

from __future__ import annotations

import sys

from app.gui.main_window import MainWindow
from app.core.logging import setup_logging

if __name__ == "__main__":
    setup_logging("INFO")
    app = MainWindow()
    app.run()

