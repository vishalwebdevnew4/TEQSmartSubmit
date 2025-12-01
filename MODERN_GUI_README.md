# Modern CustomTkinter GUI Application

## Overview

A modern, sleek Python GUI application built with **CustomTkinter** featuring:
- ✅ Dark mode theme
- ✅ Rounded buttons and inputs
- ✅ Sidebar navigation
- ✅ Clean, modular code structure
- ✅ Consistent spacing and modern fonts

## Installation

1. **Install CustomTkinter:**
   ```bash
   pip install customtkinter
   ```

   Or install from requirements:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Simple Version (No Authentication)
```bash
python run_modern.py
```

### Full Version (With Authentication)
```bash
python modern_main.py
```

## Features

### Main Window
- **Size**: 600x400 pixels
- **Title**: "Modern App"
- **Theme**: Dark mode with blue accent color
- **Auto-centered**: Automatically centers on screen

### Sidebar Navigation
- **Home** - Welcome page with clickable button
- **Settings** - Application settings
- **About** - Application information

### Design Characteristics
- **Rounded Components**: All buttons and inputs have rounded corners
- **Modern Fonts**: Segoe UI with clear hierarchy
- **Consistent Spacing**: Generous padding (20px, 30px, 40px)
- **Dark Theme**: Professional dark mode appearance
- **Smooth Interactions**: Button hover effects and state changes

## Code Structure

```
app/gui/
├── simple_modern_app.py    # Simple standalone version
├── modern_app.py            # Full version with authentication
├── login_dialog.py          # Modern login dialog
└── pages/
    ├── home_page.py         # Home page component
    ├── settings_page.py     # Settings page component
    └── about_page.py        # About page component
```

## Component Details

### Home Page
- Welcome message
- Subtitle text
- Clickable button with action
- Clean, centered layout

### Settings Page
- Theme toggle switch
- Database configuration info
- Settings sections with cards

### About Page
- Application information
- Version details
- Credits

## Customization

All styling is handled by CustomTkinter's built-in theme system:
- `ctk.set_appearance_mode("dark")` - Dark mode
- `ctk.set_default_color_theme("blue")` - Blue accent color
- Rounded corners: `corner_radius=8` or `corner_radius=10`
- Consistent fonts: `ctk.CTkFont(size=13)` or `ctk.CTkFont(size=32, weight="bold")`

## Requirements

- Python 3.8+
- CustomTkinter >= 5.2.0
- Pillow >= 10.0.0 (for image support)

Enjoy your modern GUI! 🎨



