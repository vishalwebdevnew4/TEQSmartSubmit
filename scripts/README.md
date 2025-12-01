# Template Downloader Scripts

## Overview

This directory contains scripts for the Category-Based Template Downloader system.

## Scripts

### `cli.js`
Main command-line interface that routes commands to appropriate scripts.

**Usage:**
```bash
node scripts/cli.js <command> [options]
```

### `downloader.js`
Downloads HTML templates from trusted sources for various categories.

**Features:**
- Web search for templates
- ZIP file download
- Automatic extraction
- Metadata generation

**Usage:**
```bash
node scripts/downloader.js download-category restaurant 12
```

### `template-processor.js`
Processes and normalizes downloaded templates.

**Features:**
- Extract inline CSS to external stylesheets
- Fix broken asset paths
- Remove tracking scripts
- Validate folder structure

**Usage:**
```bash
node scripts/template-processor.js
```

### `converter.js`
Converts HTML templates to modern frameworks.

**Supported Frameworks:**
- Next.js (React)
- Laravel (PHP/Blade)
- Vue.js

**Usage:**
```bash
node scripts/converter.js --category=restaurant --name=restaurant-template-1 --to=nextjs
```

### `client-generator.js`
Generates client sites from templates with business data injection.

**Features:**
- Business data injection
- Placeholder replacement
- Preview server
- Metadata generation

**Usage:**
```bash
node scripts/client-generator.js --client="Business Name" --category=restaurant --template=restaurant-template-1
```

## Dependencies

- `jsdom` - HTML parsing and manipulation
- `adm-zip` - ZIP file extraction
- `open` - Browser opening

## Integration

All scripts can be used via npm scripts:

```bash
npm run download-category restaurant 12
npm run preview-template restaurant restaurant-template-1
npm run convert-template -- --category=restaurant --name=restaurant-template-1 --to=nextjs
npm run create-client-site -- --client="Name" --category=restaurant --template=restaurant-template-1
npm run process-template restaurant restaurant-template-1
```

