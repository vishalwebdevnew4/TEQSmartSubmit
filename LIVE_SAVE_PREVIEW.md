# Live Save & Preview Feature

## Current Status

**No live save or preview functionality exists currently.**

The application currently requires manual save actions for:
- Domain forms (add/edit)
- Template forms (add/edit)
- Settings

## Proposed Features

### 1. Auto-Save Functionality

**For Form Fields:**
- Automatically save form data as users type
- Save to local cache file
- Restore data if form is closed and reopened
- Show auto-save status indicator

**Implementation:**
- Debounced saves (wait 500ms after typing stops)
- Save to `~/.cache/teqsmartsubmit/autosave/`
- JSON format for easy restoration
- Per-form ID for tracking

### 2. Live Preview

**For Templates:**
- Real-time preview of template field mappings
- Preview JSON structure as you edit
- Syntax validation in real-time
- Show formatted preview

**For Domains:**
- Preview URL validation
- Show domain status before saving
- Validate format live

**Implementation:**
- Debounced preview updates (300ms delay)
- Side-by-side preview pane
- Syntax highlighting
- Error highlighting

### 3. Visual Indicators

- "Auto-saved" status badge
- Last saved timestamp
- Unsaved changes warning
- Preview refresh indicator

## Would you like me to implement these features?

I can add:
1. ✅ Auto-save system for forms
2. ✅ Live preview for template editing
3. ✅ Visual status indicators
4. ✅ Restore unsaved changes on reopen


