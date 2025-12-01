# How to Get Google Places API Key

## Step-by-Step Guide

### 1. Create a Google Cloud Account
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Sign in with your Google account (or create one if needed)

### 2. Create a New Project
1. Click on the project dropdown at the top of the page
2. Click **"New Project"**
3. Enter a project name (e.g., "TEQSmartSubmit")
4. Click **"Create"**
5. Wait for the project to be created, then select it from the dropdown

### 3. Enable Google Places API
1. Go to **"APIs & Services"** → **"Library"** (or visit: https://console.cloud.google.com/apis/library)
2. Search for **"Places API"**
3. Click on **"Places API"** (make sure it's the one by Google)
4. Click **"Enable"**

### 4. Create API Key
1. Go to **"APIs & Services"** → **"Credentials"** (or visit: https://console.cloud.google.com/apis/credentials)
2. Click **"+ CREATE CREDENTIALS"** at the top
3. Select **"API key"**
4. Your API key will be created and displayed
5. **Copy the API key** - you'll need it in the next step

### 5. Restrict API Key (Recommended for Security)
1. Click on the API key you just created to edit it
2. Under **"API restrictions"**, select **"Restrict key"**
3. Check **"Places API"** from the list
4. Under **"Application restrictions"**, you can optionally:
   - Restrict by IP addresses (for server-side use)
   - Restrict by HTTP referrers (for web apps)
5. Click **"Save"**

### 6. Add API Key to Your Project
1. Open your `.env` file in the project root
2. Add or update this line:
   ```
   GOOGLE_PLACES_API_KEY=your_actual_api_key_here
   ```
3. Replace `your_actual_api_key_here` with the API key you copied
4. Save the file

### 7. Enable Billing (Required)
⚠️ **Important**: Google Places API requires billing to be enabled, even for free tier usage.

1. Go to **"Billing"** in the Google Cloud Console
2. Link a billing account (credit card required)
3. Don't worry - Google provides $200 free credit per month
4. Most small projects stay within the free tier

### 8. Set Usage Limits (Optional but Recommended)
1. Go to **"APIs & Services"** → **"Quotas"**
2. Find **"Places API"**
3. Set daily usage limits to prevent unexpected charges
4. Set up billing alerts to get notified of usage

## Pricing Information

Google Places API pricing (as of 2024):
- **Places API (New)**: 
  - Text Search: $17 per 1,000 requests
  - Place Details: $17 per 1,000 requests
  - Place Photos: $7 per 1,000 requests
- **Free Tier**: $200 credit per month (covers ~11,000 requests)

## Quick Links

- [Google Cloud Console](https://console.cloud.google.com/)
- [Places API Documentation](https://developers.google.com/maps/documentation/places/web-service)
- [API Key Best Practices](https://developers.google.com/maps/api-security-best-practices)

## Troubleshooting

### "API key not valid" error
- Make sure you've enabled Places API
- Check that billing is enabled
- Verify the API key is correct in your `.env` file

### "This API project is not authorized" error
- Enable Places API in the API Library
- Wait a few minutes for changes to propagate

### "Request denied" error
- Check API key restrictions
- Make sure Places API is enabled
- Verify billing is set up

## Security Tips

1. **Never commit your API key to Git**
   - Make sure `.env` is in `.gitignore`
   - Use environment variables in production

2. **Restrict your API key**
   - Limit to specific APIs (Places API only)
   - Restrict by IP or referrer if possible

3. **Monitor usage**
   - Set up billing alerts
   - Check usage regularly in Cloud Console

4. **Rotate keys if compromised**
   - Create new keys and update your `.env`
   - Delete old keys

