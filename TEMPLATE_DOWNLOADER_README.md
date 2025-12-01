# Category-Based Template Downloader

A comprehensive system for downloading, processing, and converting HTML templates for various business categories.

## 🚀 Quick Start

### 1. Download Templates for a Category

```bash
npm run download-category restaurant 12
```

This will:
- Search for 10-15 high-quality HTML templates
- Download ZIP files
- Extract them
- Save in `/templates/restaurant/{template-name}/`
- Generate metadata.json for each template

### 2. Preview a Template

```bash
npm run preview-template restaurant restaurant-template-1
```

Opens the template in your default browser.

### 3. Process & Normalize Template

```bash
npm run process-template restaurant restaurant-template-1
```

This will:
- ✅ Validate folder structure
- ✅ Normalize HTML/CSS/JS
- ✅ Fix broken asset paths
- ✅ Remove external tracking scripts
- ✅ Convert inline CSS → external stylesheet
- ✅ Prepare for dynamic integration

### 4. Convert Template to Framework

```bash
npm run convert-template -- --category=restaurant --name=restaurant-template-1 --to=nextjs
```

Supported frameworks:
- `nextjs` - Next.js/React
- `laravel` - Laravel/PHP
- `vue` - Vue.js

### 5. Create Client Site

```bash
npm run create-client-site -- --client="Gobind Sweets" --category=restaurant --template=restaurant-template-1
```

This will:
- Auto-fill business data
- Generate dynamic website
- Create preview link

## 📁 Folder Structure

```
/templates/
  /restaurant/
    /restaurant-template-1/
      index.html
      assets/
        css/
        js/
        images/
      metadata.json
  /cafe/
  /hotel/
  ...

/scripts/
  downloader.js          # Main downloader
  template-processor.js  # Normalization & fixes
  converter.js           # Framework conversion
  client-generator.js    # Client site generation
  cli.js                 # Command router

/converted/              # Converted templates
/client-sites/           # Generated client sites
```

## 🎯 Supported Categories

- `restaurant`
- `cafe`
- `hotel`
- `bakery`
- `sweets-shop`
- `grocery`
- `salon`
- `barber`
- `gym`
- `portfolio`
- `real-estate`
- `e-commerce`
- `medical`
- `doctor`
- `construction`
- `travel`

## 📋 Template Metadata

Each downloaded template includes a `metadata.json`:

```json
{
  "name": "restaurant-template-1",
  "category": "restaurant",
  "source": "template-download-url",
  "status": "downloaded",
  "preview": "/templates/restaurant/restaurant-template-1/index.html",
  "downloadedAt": "2025-01-01T00:00:00.000Z",
  "version": "1.0.0"
}
```

## 🔧 Advanced Usage

### Direct Script Usage

```bash
# Downloader
node scripts/downloader.js download-category restaurant 15

# Processor
node scripts/template-processor.js

# Converter
node scripts/converter.js --category=restaurant --name=restaurant-template-1 --to=nextjs

# Client Generator
node scripts/client-generator.js --client="My Business" --category=restaurant --template=restaurant-template-1
```

### Batch Processing

```bash
# Download multiple categories
npm run download-category restaurant 12
npm run download-category cafe 10
npm run download-category hotel 8

# Process all templates in a category
for template in templates/restaurant/*/; do
  npm run process-template restaurant $(basename $template)
done
```

## 🛠️ Installation

Required dependencies are automatically installed with:

```bash
npm install
```

The system uses:
- `jsdom` - HTML parsing and manipulation
- `adm-zip` - ZIP file extraction
- `open` - Browser opening

## 📝 Workflow Example

1. **Download templates:**
   ```bash
   npm run download-category restaurant 12
   ```

2. **Process templates:**
   ```bash
   npm run process-template restaurant restaurant-template-1
   ```

3. **Preview:**
   ```bash
   npm run preview-template restaurant restaurant-template-1
   ```

4. **Convert to Next.js:**
   ```bash
   npm run convert-template -- --category=restaurant --name=restaurant-template-1 --to=nextjs
   ```

5. **Create client site:**
   ```bash
   npm run create-client-site -- --client="Gobind Sweets" --category=restaurant --template=restaurant-template-1
   ```

## 🎨 Template Processing Features

- **Path Normalization**: Fixes relative/absolute paths
- **CSS Extraction**: Moves inline styles to external files
- **Tracking Removal**: Removes Google Analytics, Facebook Pixel, etc.
- **Structure Validation**: Ensures proper folder structure
- **Asset Organization**: Organizes CSS, JS, and images

## 🔄 Conversion Features

### Next.js
- Creates React components
- Sets up Next.js structure
- Configures package.json
- Copies assets to public folder

### Laravel
- Creates Blade templates
- Sets up Laravel structure
- Configures routes
- Uses Vite for assets

### Vue.js
- Creates Vue components
- Sets up Vite configuration
- Configures package.json
- Organizes assets

## 📦 Client Site Generation

When creating a client site, the system:
1. Loads the template
2. Injects business data (name, phone, email, address)
3. Replaces placeholders
4. Generates metadata
5. Creates preview link

Business data can be customized in `client-generator.js`.

## 🚨 Troubleshooting

### Templates not downloading
- Check internet connection
- Verify category name is correct
- Check template source URLs

### Processing fails
- Ensure template has `index.html`
- Check file permissions
- Verify assets folder exists

### Conversion errors
- Ensure template is processed first
- Check framework name (nextjs/laravel/vue)
- Verify output directory permissions

## 📚 Next Steps

After downloading templates, you can:
1. Customize templates for your needs
2. Convert to your preferred framework
3. Generate client sites automatically
4. Deploy to production

## 🤝 Contributing

To add new template sources or categories, edit:
- `scripts/downloader.js` - Add sources to `TEMPLATE_SOURCES`
- `scripts/cli.js` - Add category to help text

---

**Happy Template Downloading! 🎉**

