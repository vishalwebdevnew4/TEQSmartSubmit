# TEQSmartSubmit

## Quick Start

1. Install dependencies and generate the Prisma client.
   ```bash
   npm install
   npx prisma generate
   ```

2. Apply database migrations (or push the schema) using a configured `DATABASE_URL`.
   ```bash
   npx prisma migrate dev --name init
   # or
   npx prisma db push
   ```

3. Seed the testing domain and template (Housefolio interior design site).
   ```bash
   npm run db:seed
   ```
   This will upsert the domain `https://interiordesign.xcelanceweb.com/` and a starter automation template (`Interior Design Contact Form`) in PostgreSQL.

4. Start the Next.js development server.
   ```bash
   npm run dev
   ```

5. Use the admin registration page (`/register?token=<your-token>`) to create an admin, then log in at `/login` to manage automation runs.

## Environment Variables

Set these in `.env.local` (not tracked in git):

```
DATABASE_URL=postgresql://user:password@localhost:5432/teqsmartsubmit
NEXT_PUBLIC_API_BASE_URL=/api
TEQ_ADMIN_REGISTRATION_TOKEN=teq-admin-access
AUTH_JWT_SECRET=replace-with-strong-secret
AUTH_JWT_EXPIRES=1h
```

### CAPTCHA Solving

#### Option 1: Manual Solving (Free - For Development/Testing)

For development and testing, you can solve CAPTCHAs manually:

1. **Set the browser to visible mode** by adding to `.env.local`:
   ```bash
   HEADLESS=false
   ```
   Or add to your template JSON:
   ```json
   {
     "headless": false,
     ...
   }
   ```

2. When automation runs, a browser window will open
3. When CAPTCHA appears, solve it manually in the browser
4. The script will wait up to 5 minutes for you to solve it
5. After solving, automation continues automatically

**Perfect for testing without paying for CAPTCHA solving services!**

#### Option 2: Automatic Solving (Paid - For Production)

The system supports multiple CAPTCHA solving services. Set the API key for your preferred service:

**2captcha (Default):**
```bash
CAPTCHA_2CAPTCHA_API_KEY=your-api-key
# or
TEQ_CAPTCHA_API_KEY=your-api-key
```

**AntiCaptcha:**
```bash
CAPTCHA_ANTICAPTCHA_API_KEY=your-api-key
```

**CapSolver:**
```bash
CAPTCHA_CAPSOLVER_API_KEY=your-api-key
```

**Getting API Keys:**
- **2captcha**: Sign up at [2captcha.com](https://2captcha.com) - ~$2.99 per 1000 solves
- **AntiCaptcha**: Sign up at [anti-captcha.com](https://anti-captcha.com)
- **CapSolver**: Sign up at [capsolver.com](https://capsolver.com)

**Template Configuration:**
You can also specify the service in your template:
```json
{
  "captcha_service": "2captcha",  // or "anticaptcha", "capsolver", "auto"
  ...
}
```

The automation script will automatically:
- Detect reCAPTCHA on forms
- Submit the CAPTCHA to the configured service for solving
- Inject the solved token into the form
- Proceed with form submission

#### Option 3: Self-Made Local Solver (Free - Fully Automated)

A fully automated local CAPTCHA solver that works without external services:

```bash
# Install dependencies
pip install SpeechRecognition pydub
sudo apt-get install ffmpeg  # For audio processing

# Enable in .env.local
TEQ_USE_LOCAL_CAPTCHA_SOLVER=true
```

Or in template:
```json
{
  "use_local_captcha_solver": true,
  ...
}
```

**Features:**
- ✅ Fully automated (no manual intervention)
- ✅ Free (no API costs)
- ✅ Solves checkbox and audio CAPTCHAs
- ✅ Uses Google's free speech recognition API

**See [LOCAL_CAPTCHA_SOLVER.md](./LOCAL_CAPTCHA_SOLVER.md) for complete documentation.**

**Note:** See [CAPTCHA_SOLVER.md](./CAPTCHA_SOLVER.md) for detailed documentation on all CAPTCHA solving options.

Restart the Next.js server whenever environment variables change.
