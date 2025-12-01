# Template Customization Feature

## Overview
This feature allows users to select a pre-built template and automatically customize it with their business information, logo, and dynamic pages.

## Features Implemented

### 1. Template Selection
- **Location**: Generate Website page (`/businesses/[id]/generate`)
- **Feature**: Dropdown to select from available templates
- **Required**: Template must be selected before generating

### 2. Business Data Collection
Automatically collects:
- Business name
- Phone number
- Address
- Website URL
- Email (auto-generated from website if not provided)
- Description
- Categories

### 3. Logo Generation
- **Endpoint**: `/api/logo/generate?name=BusinessName&category=restaurant`
- **Current**: Generates SVG placeholder logo with business initials
- **Future**: Can integrate with:
  - DALL-E API
  - Midjourney API
  - LogoMaker API
  - Other logo generation services

### 4. Template Processing
- **Service**: `process-template-handler.ts`
- **What it does**:
  - Reads selected template HTML
  - Replaces logo with generated logo
  - Injects business name in header/nav
  - Updates page title and meta description
  - Fills footer with business contact info
  - Replaces placeholders in content
  - **Preserves all styling** - only changes data

### 5. Dynamic Pages Generation
Automatically creates:
- **About Page** (`about.html`):
  - Business story
  - Why choose us section
  - Contact information
  
- **Contact Page** (`contact.html`):
  - Contact form
  - Business contact details
  - Address, phone, email display

### 6. Data Injection Points

#### Header/Navigation
- Logo replacement
- Business name in brand/logo text
- Navigation links (preserved)

#### Footer
- Phone number
- Address
- Email
- Website URL

#### Content
- Placeholder replacement (`{{business.name}}`, etc.)
- Meta tags (title, description)

## How It Works

1. **User selects template** from dropdown
2. **Clicks "Generate Website"**
3. **System**:
   - Generates logo for business
   - Processes template HTML
   - Injects business data
   - Creates dynamic pages
   - Saves to database
4. **Result**: Fully customized website ready for deployment

## API Endpoints

### POST `/api/businesses/generate-website`
**Request:**
```json
{
  "businessId": 7,
  "copyStyle": "friendly",
  "templateCategory": "restaurant",
  "templateName": "foodie"
}
```

**Response:**
```json
{
  "success": true,
  "templateId": 123,
  "templateVersionId": 456,
  "templateSource": "restaurant/foodie"
}
```

### POST `/api/businesses/process-template`
**Request:**
```json
{
  "templateCategory": "restaurant",
  "templateName": "foodie",
  "businessData": {
    "name": "Gobind Sweets",
    "phone": "+1-234-567-8900",
    "address": "123 Main St",
    "email": "contact@gobindsweets.com",
    "website": "https://gobindsweets.com",
    "description": "Best sweets in town"
  }
}
```

### GET `/api/logo/generate?name=BusinessName&category=restaurant`
Returns SVG logo with business initials

## Template Requirements

Templates should have:
- `index.html` file
- Standard HTML structure
- Logo images (will be replaced)
- Header/navigation (business name will be injected)
- Footer (contact info will be filled)

## Styling Preservation

✅ **Preserved**:
- All CSS classes
- All inline styles
- Layout structure
- Color schemes
- Typography
- Animations

❌ **Changed**:
- Logo images (replaced with generated logo)
- Text content (business data)
- Meta tags (title, description)
- Contact information

## Future Enhancements

1. **Logo Generation**:
   - Integrate DALL-E for custom logo generation
   - Use business category for logo style
   - Generate multiple logo variations

2. **More Dynamic Pages**:
   - Services page
   - Gallery page
   - Menu page (for restaurants)
   - Testimonials page

3. **Content Generation**:
   - AI-generated about page content
   - Service descriptions
   - Product listings

4. **Image Integration**:
   - Use business images from Google Places
   - Generate placeholder images
   - Optimize images for web

## Usage Example

```typescript
// User selects "foodie" template
// System processes:
1. Generate logo: "/api/logo/generate?name=Gobind Sweets&category=restaurant"
2. Read template: "templates/restaurant/foodie/index.html"
3. Inject data:
   - Logo: Replace all logo images
   - Header: Replace brand name
   - Footer: Fill contact info
   - Content: Replace placeholders
4. Create pages:
   - about.html
   - contact.html
5. Save to database
```

## Testing

To test the feature:
1. Go to any business → "Generate Website"
2. Select a template from dropdown (e.g., "foodie")
3. Choose copy style
4. Click "Generate Website"
5. System will process template and create customized version

