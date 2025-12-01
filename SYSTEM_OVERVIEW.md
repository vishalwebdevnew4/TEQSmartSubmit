# TEQSmartSubmit - Complete System Overview

## 🎯 System Architecture

This is a fully automated SaaS system that combines:
- **Google Places API** → Business data fetching
- **AI Website Generator** → Figma-style Next.js templates
- **Vercel Deployment** → Automatic hosting
- **Form Submission** → Multi-domain automation with CAPTCHA solving
- **Client Outreach** → Email automation with tracking
- **Analytics Dashboard** → Complete management interface

## 📁 Project Structure

```
TEQSmartSubmit/
├── src/                          # Next.js Frontend
│   ├── app/
│   │   ├── (dashboard)/         # Dashboard pages
│   │   │   ├── dashboard/       # Main overview
│   │   │   ├── businesses/      # Business management
│   │   │   ├── deployments/     # Deployment tracking
│   │   │   ├── clients/         # Client outreach
│   │   │   └── ...
│   │   └── api/                  # API routes
│   │       ├── businesses/      # Business APIs
│   │       ├── deployments/     # Deployment APIs
│   │       └── clients/          # Client APIs
│   └── lib/                      # Utilities
│       └── prisma.ts            # Database client
│
├── backend/                      # Python Backend
│   ├── app/
│   │   ├── services/            # Python automation services
│   │   │   ├── google_places_service.py
│   │   │   ├── website_generator.py
│   │   │   ├── vercel_deploy.py
│   │   │   ├── screenshot_service.py
│   │   │   └── email_service.py
│   │   ├── db/                   # Database models
│   │   └── api/                  # FastAPI endpoints (optional)
│   └── alembic/                  # Database migrations
│
├── prisma/                        # Prisma schema
│   └── schema.prisma             # Database schema
│
└── requirements.txt              # Python dependencies
```

## 🔄 Complete Workflow

### 1. Business Discovery
- User inputs: Business name, phone, or Google Places URL
- System fetches from Google Places API:
  - Name, address, phone, website
  - Reviews, ratings, categories
  - Images, description
- Data stored in PostgreSQL

### 2. Website Generation
- AI generates Next.js + Tailwind template:
  - Hero section with business info
  - About section
  - Services section
  - Contact form
- Color palette based on business type
- Typography and styling
- Copy style: Formal/Friendly/Marketing/Minimalist

### 3. Automatic Deployment
- Git repository initialization
- Push to GitHub (optional)
- Deploy to Vercel via API/CLI
- Take homepage screenshot
- Store deployment URL and status

### 4. Client Outreach
- Send personalized emails with:
  - Live preview URL
  - Screenshot
  - Custom message
- Track engagement:
  - Email opens
  - Link clicks
  - Time on preview page
- Store analytics in database

### 5. Form Submission
- Upload CSV of domains
- Detect contact forms automatically
- Fill with business-specific message
- Solve CAPTCHAs (reCAPTCHA, hCaptcha)
- Retry failed submissions
- Log all results

## 🗄️ Database Schema

### Core Models
- **Business**: Google Places data
- **Template**: Website templates
- **TemplateVersion**: Versioned template content
- **DeploymentLog**: Vercel deployments
- **Client**: Client information
- **ClientTracking**: Engagement analytics
- **FormSubmissionLog**: Form submission results
- **Task**: Background job queue

## 🚀 Key Features

### Frontend (Next.js)
- ✅ Modern dashboard with dark mode
- ✅ Business management interface
- ✅ Deployment tracking
- ✅ Client analytics
- ✅ Real-time status updates
- ✅ Responsive design

### Backend (Python)
- ✅ Google Places API integration
- ✅ AI website generation
- ✅ Vercel deployment automation
- ✅ Playwright screenshot capture
- ✅ Email sending with tracking
- ✅ Form submission automation

### Integration
- ✅ Next.js API routes call Python services
- ✅ PostgreSQL for all data storage
- ✅ Real-time status updates
- ✅ Error handling and logging

## 📊 Dashboard Pages

1. **Dashboard** (`/dashboard`)
   - Overview stats
   - Recent activity
   - Automation controls

2. **Businesses** (`/businesses`)
   - Fetch from Google Places
   - Upload CSV
   - Generate websites
   - View business details

3. **Deployments** (`/deployments`)
   - Track Vercel deployments
   - View deployment status
   - Screenshots

4. **Clients** (`/clients`)
   - Client list
   - Email analytics
   - Engagement tracking

5. **Domains** (`/domains`)
   - Domain management
   - Form detection
   - Submission logs

6. **Templates** (`/templates`)
   - Template management
   - Version control

7. **Logs** (`/logs`)
   - Submission logs
   - Error tracking

8. **Reports** (`/reports`)
   - Analytics
   - Export data

## 🔧 Python Services

All services can run standalone or be called from Next.js:

1. **google_places_service.py**
   ```bash
   python backend/app/services/google_places_service.py --input "Business Name" --type name
   ```

2. **website_generator.py**
   ```bash
   python backend/app/services/website_generator.py --business-data '{"name":"..."}' --style friendly
   ```

3. **vercel_deploy.py**
   ```bash
   python backend/app/services/vercel_deploy.py --template-path /path/to/template
   ```

4. **screenshot_service.py**
   ```bash
   python backend/app/services/screenshot_service.py --url https://example.com
   ```

5. **email_service.py**
   ```bash
   python backend/app/services/email_service.py --to client@example.com --business-name "Business" --preview-url https://...
   ```

## 🔐 Environment Variables

Required:
- `DATABASE_URL`: PostgreSQL connection
- `GOOGLE_PLACES_API_KEY`: Google Places API
- `VERCEL_TOKEN`: Vercel deployment
- `GITHUB_TOKEN`: GitHub integration
- `SMTP_*`: Email service credentials

Optional:
- `OPENAI_API_KEY`: Enhanced AI copy
- `ANTHROPIC_API_KEY`: Alternative AI
- `CAPTCHA_*_API_KEY`: CAPTCHA solving
- `SENTRY_DSN`: Error monitoring

## 📝 Next Steps

### To Complete:
1. ✅ Database schema - DONE
2. ✅ Python services - DONE
3. ✅ Next.js dashboard - DONE
4. ✅ API routes - DONE
5. ⏳ Background workers (Celery) - PENDING
6. ⏳ Enhanced form submission - PENDING
7. ⏳ Authentication with roles - PENDING
8. ⏳ Template versioning UI - PENDING
9. ⏳ Sentry integration - PENDING

### To Deploy:
1. Set up PostgreSQL database
2. Configure environment variables
3. Run database migrations
4. Deploy Next.js to Vercel
5. Deploy Python backend (optional, services can run standalone)
6. Test end-to-end workflow

## 🎨 UI Features

- Modern dark theme
- Responsive design
- Real-time updates
- Status indicators
- Charts and analytics
- Export functionality
- Search and filters

## 🔄 API Flow

```
Next.js Frontend
    ↓
API Route (/api/businesses/fetch)
    ↓
Python Service (google_places_service.py)
    ↓
PostgreSQL Database
    ↓
Response to Frontend
```

All services follow this pattern for seamless integration.

## 📚 Documentation

- `DEPLOYMENT_GUIDE.md`: Complete setup instructions
- `SYSTEM_OVERVIEW.md`: This file
- Code comments: Inline documentation

## 🎯 Production Ready Features

- ✅ Error handling
- ✅ Logging
- ✅ Database migrations
- ✅ Environment configuration
- ✅ Type safety (TypeScript)
- ✅ Responsive UI
- ✅ API documentation

