# Visual Style Guide - TEQSmartSubmit GUI

## Design Philosophy

The GUI features a **modern, sleek, professional dark theme** with high-contrast cyan accents and clean, elegant typography. The layout is responsive, well-spaced, and optimized for readability and visual hierarchy.

## Color Palette

### Background Colors
- **Primary Background**: `#0a0e27` - Deep dark blue-black for main areas
- **Secondary Background**: `#151b3d` - Darker slate for sidebar
- **Tertiary Background**: `#1e293b` - Slate-800 for cards/panels
- **Elevated Surfaces**: `#273549` - For elevated UI elements

### Text Colors
- **Primary Text**: `#ffffff` - Pure white for headings
- **Secondary Text**: `#e2e8f0` - Slate-200 for body text
- **Tertiary Text**: `#cbd5e1` - Slate-300 for supporting text
- **Muted Text**: `#94a3b8` - Slate-400 for subtitles
- **Disabled Text**: `#64748b` - Slate-500 for inactive elements

### Accent Colors
- **Primary Accent**: `#00d4ff` - Bright cyan (high contrast)
- **Primary Accent Hover**: `#00b8e6` - Darker cyan
- **Secondary Accent**: `#6366f1` - Indigo
- **Secondary Accent Hover**: `#4f46e5` - Darker indigo

### Status Colors
- **Success**: `#10b981` - Emerald green
- **Warning**: `#f59e0b` - Amber
- **Error**: `#ef4444` - Red
- **Info**: `#3b82f6` - Blue

### Border & Input Colors
- **Default Border**: `#334155` - Slate-700
- **Hover Border**: `#475569` - Slate-600
- **Focus Border**: `#00d4ff` - Bright cyan (accent)

## Typography

### Font Family
- **Primary**: Segoe UI, system-ui, sans-serif
- **Monospace**: Consolas, Monaco, Courier New, monospace

### Font Sizes
- **Title**: 28pt (Bold) - Main page titles
- **Heading**: 20pt (Bold) - Section headings
- **Subheading**: 16pt (Bold) - Subsection headings
- **Body**: 11pt (Regular) - Default text
- **Small**: 10pt (Regular) - Supporting text
- **Tiny**: 9pt (Regular) - Labels, metadata

### Typography Hierarchy
1. **Titles** - Large, bold, high contrast white
2. **Headings** - Medium, bold, primary white
3. **Subheadings** - Smaller, bold, secondary white
4. **Body Text** - Regular weight, secondary/tertiary white
5. **Muted Text** - Lighter weight, muted slate for subtitles

## Spacing System

### Standard Spacing Scale
- **XS**: 4px - Tight spacing
- **SM**: 8px - Small spacing
- **MD**: 12px - Medium spacing
- **LG**: 16px - Large spacing
- **XL**: 20px - Extra large spacing
- **XXL**: 24px - Section spacing
- **XXXL**: 32px - Major section spacing

### Component Spacing
- **Card Padding**: 20px
- **Dialog Padding**: 32px
- **Section Spacing**: 24px
- **Element Spacing**: 12px

## Layout Principles

### Spacing & Padding
- Generous whitespace for breathing room
- Consistent padding throughout components
- Clear visual separation between sections
- Responsive spacing that adapts to content

### Visual Hierarchy
- Clear distinction between primary and secondary elements
- High contrast for important actions (cyan accents)
- Subtle backgrounds for supporting content
- Elevation through color and spacing

### Component Design
- Flat design with subtle depth through color
- Rounded corners for modern feel (4-12px radius)
- Clean borders with focus states
- Smooth hover transitions

## Button Styles

### Primary Button
- Background: Bright cyan (`#00d4ff`)
- Text: Dark background color
- Use: Main actions, primary CTAs

### Secondary Button
- Background: Elevated surface (`#273549`)
- Text: White
- Use: Secondary actions

### Success Button
- Background: Emerald green (`#10b981`)
- Text: White
- Use: Positive actions (save, confirm)

### Danger Button
- Background: Red (`#ef4444`)
- Text: White
- Use: Destructive actions (delete, remove)

## Input Fields

- Background: Dark slate (`#1e293b`)
- Border: Slate-700 (`#334155`)
- Focus Border: Bright cyan (`#00d4ff`)
- Text: White
- Cursor: Cyan accent

## Cards & Panels

- Background: Elevated surface (`#273549`)
- Border: None (using background color for separation)
- Padding: 20px
- Spacing: Consistent margins between cards

## Accessibility

- High contrast ratios for text readability
- Clear focus indicators (cyan borders)
- Large clickable areas (minimum 44x44px)
- Consistent visual feedback on interactions

## Implementation

All styling is centralized in `app/gui/theme.py` with:
- `Colors` class for color constants
- `Fonts` class for typography
- `Spacing` class for spacing constants
- `ButtonStyle` class for button presets
- `InputStyle` class for input presets
- `LabelStyle` class for label presets

This ensures consistency across all components and makes theme changes easy.


