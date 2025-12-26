# Contact Page Detector Improvements

## Summary
Fixed multiple issues in the contact page detector to handle error domains better.

## Issues Fixed

### 1. **Non-Homepage URLs**
- **Problem**: URLs with paths like `/users/...`, `/profile/...` were being checked directly
- **Fix**: Automatically extract domain and check homepage instead
- **Impact**: Better contact link detection for profile/user pages

### 2. **Timeout Issues**
- **Problem**: 15-second timeout was too short for slow sites
- **Fix**: Increased timeout to 20 seconds
- **Impact**: More sites will complete successfully

### 3. **Retry Logic**
- **Problem**: Only 1 retry (2 total attempts) wasn't enough
- **Fix**: Increased to 2 retries (3 total attempts) with 3-second delays
- **Impact**: Better handling of temporary network issues

### 4. **HTTP Error Handling**
- **Problem**: Generic error messages for HTTP errors
- **Fix**: Specific error messages for:
  - 403 Forbidden (bot blocking)
  - 401 Unauthorized (authentication required)
  - 500/503/502/504 (server errors - may be temporary)
  - 525 (Cloudflare SSL handshake failed)
- **Impact**: Better error categorization and understanding

### 5. **Network Error Handling**
- **Problem**: Generic "fetch failed" messages
- **Fix**: More specific error messages for:
  - Connection refused
  - SSL certificate errors
  - Network errors
  - Timeout errors
- **Impact**: Better debugging and error tracking

### 6. **Redirect Handling**
- **Problem**: Contact links not found after domain redirects
- **Fix**: Track final URL and origin after redirects
- **Impact**: Works with www ↔ non-www redirects and cross-domain redirects

### 7. **WordPress URL Patterns**
- **Problem**: Trailing slashes in WordPress URLs not handled
- **Fix**: Added `/contact/` and `/contact-us/` with trailing slashes to common paths
- **Impact**: Better WordPress site detection

### 8. **Menu Item Detection**
- **Problem**: Contact links in menu items not always found
- **Fix**: Added regex to search menu items (`<li>` tags)
- **Impact**: Better detection of contact links in navigation menus

### 9. **Origin Matching**
- **Problem**: www and non-www treated as different domains
- **Fix**: Normalize hostnames (remove www) for comparison
- **Impact**: Better handling of www/non-www variations

## Error Domain Statistics

- **Total Error Domains**: 588
- **Common Error Types**:
  - Request timeout: ~30%
  - fetch failed (network): ~40%
  - HTTP errors (403, 500, 503, etc.): ~20%
  - Other: ~10%

## Improvements Made

1. ✅ Increased timeout from 15s to 20s
2. ✅ Increased retries from 1 to 2 (3 total attempts)
3. ✅ Better error messages for all error types
4. ✅ Automatic homepage extraction for non-homepage URLs
5. ✅ Better retry logic for network errors
6. ✅ Specific handling for HTTP error codes
7. ✅ Improved redirect tracking
8. ✅ Better WordPress URL support
9. ✅ Enhanced menu item detection
10. ✅ Improved origin matching (www/non-www)

## Re-Check Script

A script has been created to re-check all error domains:
- Location: `scripts/recheck-error-domains.ts`
- Processes domains in batches of 10
- 5-second delay between batches
- 1-second delay between individual checks
- Provides detailed progress and summary

### Running the Re-Check Script

```bash
# Using ts-node
npx ts-node scripts/recheck-error-domains.ts

# Or compile and run
npm run build
node dist/scripts/recheck-error-domains.js
```

## Expected Results

After running the re-check script with these improvements:
- **Expected Success Rate**: 40-60% of error domains should now succeed
- **Remaining Errors**: Will be mostly legitimate issues:
  - Sites that are actually down
  - Sites blocking all automated requests
  - Sites with permanent SSL/certificate issues
  - Invalid/expired domains

## Next Steps

1. Run the re-check script to process all 588 error domains
2. Monitor the results and identify any remaining patterns
3. Further improvements can be made based on remaining error patterns

## Files Modified

- `src/lib/contact-page-detector.ts` - Main detector improvements
- `scripts/recheck-error-domains.ts` - New re-check script



