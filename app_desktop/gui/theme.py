"""Centralized theme and styling configuration for the GUI."""

from __future__ import annotations

from typing import Dict, Tuple

# Color Palette - Modern Dark Theme with High Contrast Accents
class Colors:
    """Color palette for the application."""
    
    # Background colors (from darkest to lightest)
    BG_PRIMARY = "#0a0e27"      # Deep dark blue-black
    BG_SECONDARY = "#151b3d"    # Darker slate
    BG_TERTIARY = "#1e293b"     # Slate-800
    BG_ELEVATED = "#273549"     # Elevated surfaces
    
    # Text colors
    TEXT_PRIMARY = "#ffffff"    # Pure white
    TEXT_SECONDARY = "#e2e8f0"  # Slate-200
    TEXT_TERTIARY = "#cbd5e1"   # Slate-300
    TEXT_MUTED = "#94a3b8"      # Slate-400
    TEXT_DISABLED = "#64748b"   # Slate-500
    
    # Accent colors - Vibrant and high contrast
    ACCENT_PRIMARY = "#00d4ff"      # Bright cyan
    ACCENT_PRIMARY_HOVER = "#00b8e6" # Darker cyan
    ACCENT_SECONDARY = "#6366f1"    # Indigo
    ACCENT_SECONDARY_HOVER = "#4f46e5" # Darker indigo
    
    # Status colors
    SUCCESS = "#10b981"         # Emerald
    SUCCESS_HOVER = "#059669"   # Darker emerald
    WARNING = "#f59e0b"         # Amber
    ERROR = "#ef4444"           # Red
    ERROR_HOVER = "#dc2626"     # Darker red
    INFO = "#3b82f6"            # Blue
    
    # Border colors
    BORDER_DEFAULT = "#334155"  # Slate-700
    BORDER_HOVER = "#475569"    # Slate-600
    BORDER_FOCUS = "#00d4ff"    # Accent primary
    
    # Input colors
    INPUT_BG = "#1e293b"        # Slate-800
    INPUT_BORDER = "#334155"    # Slate-700
    INPUT_FOCUS = "#00d4ff"     # Accent primary


class Fonts:
    """Typography configuration."""
    
    # Font families
    PRIMARY = ("Segoe UI", "system-ui", "sans-serif")
    MONOSPACE = ("Consolas", "Monaco", "Courier New", "monospace")
    
    # Font sizes
    TITLE = 28
    HEADING = 20
    SUBHEADING = 16
    BODY = 11
    SMALL = 10
    TINY = 9
    
    # Font weights
    BOLD = "bold"
    SEMIBOLD = "normal"  # Will be handled by size/color
    REGULAR = "normal"
    
    @staticmethod
    def get_title_font() -> Tuple:
        """Get title font configuration."""
        return (Fonts.PRIMARY[0], Fonts.TITLE, Fonts.BOLD)
    
    @staticmethod
    def get_heading_font() -> Tuple:
        """Get heading font configuration."""
        return (Fonts.PRIMARY[0], Fonts.HEADING, Fonts.BOLD)
    
    @staticmethod
    def get_subheading_font() -> Tuple:
        """Get subheading font configuration."""
        return (Fonts.PRIMARY[0], Fonts.SUBHEADING, Fonts.BOLD)
    
    @staticmethod
    def get_body_font() -> Tuple:
        """Get body font configuration."""
        return (Fonts.PRIMARY[0], Fonts.BODY, Fonts.REGULAR)
    
    @staticmethod
    def get_small_font() -> Tuple:
        """Get small font configuration."""
        return (Fonts.PRIMARY[0], Fonts.SMALL, Fonts.REGULAR)


class Spacing:
    """Spacing and padding configuration."""
    
    # Standard spacing scale
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 20
    XXL = 24
    XXXL = 32
    
    # Component-specific spacing
    CARD_PADDING = 20
    DIALOG_PADDING = 32
    SECTION_SPACING = 24
    ELEMENT_SPACING = 12


class BorderRadius:
    """Border radius for rounded corners."""
    
    SM = 4
    MD = 8
    LG = 12
    XL = 16


class Shadows:
    """Shadow/elevation effects."""
    
    SM = "0 1px 2px rgba(0, 0, 0, 0.3)"
    MD = "0 4px 6px rgba(0, 0, 0, 0.4)"
    LG = "0 10px 20px rgba(0, 0, 0, 0.5)"


# Style configurations for common widgets
class ButtonStyle:
    """Button styling presets."""
    
    @staticmethod
    def primary() -> Dict:
        """Primary button style."""
        return {
            "font": Fonts.get_body_font(),
            "bg": Colors.ACCENT_PRIMARY,
            "fg": Colors.BG_PRIMARY,
            "activebackground": Colors.ACCENT_PRIMARY_HOVER,
            "activeforeground": Colors.BG_PRIMARY,
            "relief": "flat",
            "borderwidth": 0,
            "cursor": "hand2",
            "padx": Spacing.LG,
            "pady": Spacing.MD,
        }
    
    @staticmethod
    def secondary() -> Dict:
        """Secondary button style."""
        return {
            "font": Fonts.get_body_font(),
            "bg": Colors.BG_ELEVATED,
            "fg": Colors.TEXT_PRIMARY,
            "activebackground": Colors.BG_TERTIARY,
            "activeforeground": Colors.TEXT_PRIMARY,
            "relief": "flat",
            "borderwidth": 0,
            "cursor": "hand2",
            "padx": Spacing.LG,
            "pady": Spacing.MD,
        }
    
    @staticmethod
    def success() -> Dict:
        """Success button style."""
        return {
            "font": Fonts.get_body_font(),
            "bg": Colors.SUCCESS,
            "fg": Colors.TEXT_PRIMARY,
            "activebackground": Colors.SUCCESS_HOVER,
            "activeforeground": Colors.TEXT_PRIMARY,
            "relief": "flat",
            "borderwidth": 0,
            "cursor": "hand2",
            "padx": Spacing.LG,
            "pady": Spacing.MD,
        }
    
    @staticmethod
    def danger() -> Dict:
        """Danger button style."""
        return {
            "font": Fonts.get_body_font(),
            "bg": Colors.ERROR,
            "fg": Colors.TEXT_PRIMARY,
            "activebackground": Colors.ERROR_HOVER,
            "activeforeground": Colors.TEXT_PRIMARY,
            "relief": "flat",
            "borderwidth": 0,
            "cursor": "hand2",
            "padx": Spacing.LG,
            "pady": Spacing.MD,
        }


class InputStyle:
    """Input field styling presets."""
    
    @staticmethod
    def default() -> Dict:
        """Default input style."""
        return {
            "font": Fonts.get_body_font(),
            "bg": Colors.INPUT_BG,
            "fg": Colors.TEXT_PRIMARY,
            "insertbackground": Colors.ACCENT_PRIMARY,
            "relief": "flat",
            "borderwidth": 0,
            "highlightthickness": 2,
            "highlightbackground": Colors.INPUT_BORDER,
            "highlightcolor": Colors.INPUT_FOCUS,
        }


class LabelStyle:
    """Label styling presets."""
    
    @staticmethod
    def title() -> Dict:
        """Title label style."""
        return {
            "font": Fonts.get_title_font(),
            "fg": Colors.TEXT_PRIMARY,
            "bg": Colors.BG_PRIMARY,
        }
    
    @staticmethod
    def heading() -> Dict:
        """Heading label style."""
        return {
            "font": Fonts.get_heading_font(),
            "fg": Colors.TEXT_PRIMARY,
            "bg": Colors.BG_PRIMARY,
        }
    
    @staticmethod
    def subtitle() -> Dict:
        """Subtitle label style."""
        return {
            "font": Fonts.get_body_font(),
            "fg": Colors.TEXT_MUTED,
            "bg": Colors.BG_PRIMARY,
        }
    
    @staticmethod
    def body() -> Dict:
        """Body label style."""
        return {
            "font": Fonts.get_body_font(),
            "fg": Colors.TEXT_SECONDARY,
            "bg": Colors.BG_PRIMARY,
        }


