# How to Enable Google Cloud Billing

## Quick Steps

### 1. Go to Google Cloud Console
Visit: https://console.cloud.google.com/

### 2. Select Your Project
- Click on the project dropdown at the top
- Select the project you're using for TEQSmartSubmit

### 3. Navigate to Billing
**Option A: Direct Link**
- Go to: https://console.cloud.google.com/billing

**Option B: Through Menu**
- Click the hamburger menu (☰) in the top left
- Go to **"Billing"**

### 4. Link a Billing Account
1. If you don't have a billing account:
   - Click **"Create Account"** or **"Link a billing account"**
   - Click **"Create billing account"**
   - Fill in your account details:
     - Account name (e.g., "TEQSmartSubmit Billing")
     - Country/Region
     - Currency
   - Click **"Submit and enable billing"**

2. If you already have a billing account:
   - Click **"Link a billing account"**
   - Select your existing billing account
   - Click **"Set account"**

### 5. Add Payment Method
- Enter your credit/debit card information
- Accept the terms of service
- Click **"Submit and enable billing"**

### 6. Verify Billing is Enabled
- You should see a green checkmark or "Active" status
- Your project should now be linked to the billing account

## Important Notes

### Free Tier Credits
- **Google provides $200 free credit per month**
- Most small projects stay within the free tier
- Autocomplete API: $2.83 per 1,000 requests
- $200 credit = ~70,000 autocomplete requests/month

### Set Budget Alerts (Recommended)
1. Go to: https://console.cloud.google.com/billing/budgets
2. Click **"Create Budget"**
3. Set a budget limit (e.g., $10/month)
4. Add email alerts
5. This helps prevent unexpected charges

### Monitor Usage
- Go to: https://console.cloud.google.com/billing
- Click on your billing account
- View **"Reports"** to see current usage
- Check **"Cost breakdown"** to see which APIs are being used

## After Enabling Billing

1. **Wait 1-2 minutes** for changes to propagate
2. **Restart your Next.js dev server** (if running)
3. **Try the autocomplete again** - it should work now!

## Troubleshooting

### "Billing account not found"
- Make sure you're logged into the correct Google account
- Check that you have billing account creation permissions

### "Payment method declined"
- Verify your card details
- Check with your bank if international transactions are enabled
- Try a different payment method

### Still getting REQUEST_DENIED after enabling billing
- Wait 2-3 minutes for propagation
- Check that the correct project is selected
- Verify the API key is from the same project
- Make sure "Places API" (legacy) is enabled, not just "Places API (New)"

## Cost Estimates

### Google Places API Pricing (as of 2024)
- **Autocomplete (per session)**: $2.83 per 1,000 sessions
- **Place Details**: $17 per 1,000 requests
- **Text Search**: $32 per 1,000 requests

### Example Monthly Costs
- 1,000 autocomplete requests: ~$2.83
- 1,000 place details: ~$17
- 1,000 text searches: ~$32

**With $200 free credit, you can make:**
- ~70,000 autocomplete requests
- ~11,000 place details requests
- ~6,000 text search requests

Most development/testing stays well within the free tier!

## Quick Links

- [Enable Billing](https://console.cloud.google.com/billing)
- [Create Billing Account](https://console.cloud.google.com/billing/create)
- [Set Budget Alerts](https://console.cloud.google.com/billing/budgets)
- [View Usage](https://console.cloud.google.com/billing)
- [Places API Pricing](https://developers.google.com/maps/billing-and-pricing/pricing)

