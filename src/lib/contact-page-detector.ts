/**
 * Contact page detection utility
 * Searches for contact page links in website header and footer
 * Uses Playwright to verify contact page links for JavaScript-rendered sites
 */

import { chromium, Browser, Page } from 'playwright';

interface ContactCheckResult {
  found: boolean;
  contactUrl: string | null;
  hasForm: boolean;
  message: string;
  status: "found" | "not_found" | "error" | "no_form";
}

// Helper function to sleep/delay
const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

// Helper function to fetch with retry
async function fetchWithRetry(
  url: string,
  options: RequestInit,
  maxRetries: number = 2,
  retryDelay: number = 1000
): Promise<Response> {
  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      if (attempt > 0) {
        // Wait before retry with exponential backoff
        await sleep(retryDelay * attempt);
        console.log(`[ContactDetector] Retry attempt ${attempt}/${maxRetries} for ${url}`);
      }

      const response = await fetch(url, options);

      // If we get a retryable status code, retry with longer backoff for rate limiting
      if (response.status === 429 || response.status === 503 || response.status === 502 || response.status === 504) {
        if (attempt < maxRetries) {
          // For 429 (rate limiting), wait longer before retry (exponential backoff)
          const backoffDelay = response.status === 429 ? retryDelay * Math.pow(2, attempt + 1) * 2 : retryDelay * (attempt + 1);
          console.log(`[ContactDetector] Got ${response.status}, waiting ${backoffDelay}ms before retry...`);
          await sleep(backoffDelay);
          continue;
        }
      }

      return response;
    } catch (error: any) {
      lastError = error;

      // Don't retry on certain errors
      if (
        error.name === "AbortError" ||
        error.name === "TimeoutError" ||
        error.message?.includes("CORS") ||
        error.message?.includes("Invalid URL") ||
        error.message?.includes("certificate") ||
        error.message?.includes("SSL")
      ) {
        throw error;
      }

      // If this is the last attempt, throw the error
      if (attempt === maxRetries) {
        throw error;
      }
      
      // Log retry for network errors
      if (error.message?.includes("fetch failed") || error.message?.includes("ECONNREFUSED") || error.message?.includes("ENOTFOUND")) {
        console.log(`[ContactDetector] Network error on attempt ${attempt + 1}, will retry...`);
      }
    }
  }

  throw lastError || new Error("Failed to fetch after retries");
}

export async function detectContactPage(domainUrl: string): Promise<ContactCheckResult> {
  try {
    // Normalize URL
    let baseUrl = domainUrl.trim();
    
    // Remove fragments and query params for initial check (we'll use homepage)
    const urlWithoutFragment = baseUrl.split('#')[0];
    const urlWithoutQuery = urlWithoutFragment.split('?')[0];
    baseUrl = urlWithoutQuery;
    
    if (!baseUrl.startsWith("http://") && !baseUrl.startsWith("https://")) {
      baseUrl = `https://${baseUrl}`;
    }

    let url: URL;
    try {
      url = new URL(baseUrl);
    } catch {
      // If URL parsing fails, try adding https://
      if (!baseUrl.includes("://")) {
        baseUrl = `https://${baseUrl}`;
        url = new URL(baseUrl);
      } else {
        throw new Error("Invalid URL format");
      }
    }
    
    // Extract just the domain (origin)
    const origin = url.origin;
    const isHomepage = (url.pathname === '/' || url.pathname === '') && !url.hash && !url.search;
    const homepageUrl = `${origin}/`;
    
    // Determine which URL to check
    // For blog/resource pages, check both the page and homepage (page might have contact forms)
    // For other paths, prefer homepage but also check the provided page
    const isResourcePage = /\/blog\/|\/resources\/|\/articles\/|\/posts\/|\/news\/|\/help\/|\/support\/|\/docs\//i.test(url.pathname);
    
    if (!isHomepage) {
      if (isResourcePage) {
        console.log(`[ContactDetector] Resource/blog page detected (${url.pathname}), will check both this page and homepage`);
      } else {
        console.log(`[ContactDetector] URL has path (${url.pathname}), will check homepage first, then this page if needed`);
      }
    }
    
    console.log(`[ContactDetector] Checking contact page for domain: ${origin}`);
    console.log(`[ContactDetector] Provided URL: ${baseUrl}, isHomepage: ${isHomepage}`);

    // Fetch homepage (or provided page) with better error handling and retry logic
    // For resource pages, check the page itself first; otherwise check homepage
    let response: Response;
    let urlToFetch = (isHomepage || isResourcePage) ? baseUrl : homepageUrl;
    let finalUrl = urlToFetch; // Track final URL after redirects
    let finalOrigin = origin; // Track final origin after redirects
    
    try {
      // Create abort controller for better timeout handling
      // Increased timeout for slow sites
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 20000); // 20 second timeout (increased from 15s)

      try {
        console.log(`[ContactDetector] Fetching URL: ${urlToFetch}`);
        response = await fetchWithRetry(
          urlToFetch,
          {
            method: "GET",
            headers: {
              "User-Agent":
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
              Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
              "Accept-Language": "en-US,en;q=0.9",
              "Accept-Encoding": "gzip, deflate, br",
              Connection: "keep-alive",
              "Upgrade-Insecure-Requests": "1",
              Referer: origin, // Use origin instead of full URL
              "Cache-Control": "no-cache",
            },
            signal: controller.signal,
            redirect: "follow",
          },
          2, // 2 retries (3 total attempts) - increased retries
          3000 // 3 second delay between retries
        );
        clearTimeout(timeoutId);
        
        // Get final URL after redirects (if redirected)
        finalUrl = response.url || urlToFetch;
        try {
          const finalUrlObj = new URL(finalUrl);
          finalOrigin = finalUrlObj.origin;
          console.log(`[ContactDetector] Final URL after redirects: ${finalUrl}, Final origin: ${finalOrigin}`);
          
          // If redirected to a different domain, update origin for contact link search
          if (finalOrigin !== origin) {
            console.log(`[ContactDetector] Domain redirected from ${origin} to ${finalOrigin}`);
          }
        } catch {
          // If URL parsing fails, keep original origin
          console.log(`[ContactDetector] Could not parse final URL: ${finalUrl}`);
        }
      } catch (fetchError) {
        clearTimeout(timeoutId);
        throw fetchError;
      }
    } catch (fetchError: any) {
      // Handle specific fetch errors
      if (fetchError.name === "AbortError" || fetchError.name === "TimeoutError") {
        return {
          found: false,
          contactUrl: null,
          hasForm: false,
          message: "Request timeout - site took too long to respond",
          status: "error",
        };
      }
      if (fetchError.message?.includes("ECONNREFUSED") || fetchError.message?.includes("ENOTFOUND")) {
        return {
          found: false,
          contactUrl: null,
          hasForm: false,
          message: "Connection refused - site may be down or blocking requests",
          status: "error",
        };
      }
      if (fetchError.message?.includes("CERT") || fetchError.message?.includes("SSL") || fetchError.message?.includes("certificate") || fetchError.message?.includes("tlsv1 alert") || fetchError.message?.includes("SSL routines")) {
        // Try with http:// if https:// fails due to SSL
        if (urlToFetch.startsWith("https://")) {
          console.log(`[ContactDetector] SSL error with HTTPS, trying HTTP...`);
          try {
            const httpUrl = urlToFetch.replace("https://", "http://");
            const httpController = new AbortController();
            const httpTimeoutId = setTimeout(() => httpController.abort(), 20000);
            
            try {
              const httpResponse = await fetchWithRetry(
                httpUrl,
                {
                  method: "GET",
                  headers: {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.9",
                  },
                  signal: httpController.signal,
                  redirect: "follow",
                },
                1, // 1 retry for HTTP fallback
                2000
              );
              clearTimeout(httpTimeoutId);
              
              if (httpResponse.ok) {
                // Use HTTP response if it works - set response and continue
                response = httpResponse;
                finalUrl = httpResponse.url || httpUrl;
                try {
                  const finalUrlObj = new URL(finalUrl);
                  finalOrigin = finalUrlObj.origin;
                  console.log(`[ContactDetector] HTTP fallback successful: ${finalUrl}`);
                } catch {
                  // Keep original origin
                }
                // Break out of error handling - response is set, continue to normal flow
                // We'll skip the rest of the catch block by not returning/throwing
              } else {
                clearTimeout(httpTimeoutId);
                return {
                  found: false,
                  contactUrl: null,
                  hasForm: false,
                  message: `HTTP fallback failed: ${httpResponse.status} ${httpResponse.statusText}`,
                  status: "error",
                };
              }
            } catch (httpFetchError: any) {
              clearTimeout(httpTimeoutId);
              return {
                found: false,
                contactUrl: null,
                hasForm: false,
                message: `SSL certificate error - HTTP fallback also failed: ${httpFetchError.message || "Unknown error"}`,
                status: "error",
              };
            }
          } catch (httpError: any) {
            return {
              found: false,
              contactUrl: null,
              hasForm: false,
              message: `SSL certificate error - site may have certificate issues: ${httpError.message || "HTTPS and HTTP both failed"}`,
              status: "error",
            };
          }
        } else {
          return {
            found: false,
            contactUrl: null,
            hasForm: false,
            message: "SSL certificate error - site may have certificate issues",
            status: "error",
          };
        }
      }
      if (fetchError.message?.includes("fetch failed") || fetchError.message?.includes("network") || fetchError.message?.includes("ECONNRESET")) {
        // Try Playwright as fallback - some sites block standard fetch but allow browser requests
        console.log(`[ContactDetector] Fetch failed with network error, trying Playwright as fallback for ${urlToFetch}...`);
        try {
          // Use Playwright to get HTML and final URL in one go
          let browser: Browser | null = null;
          let playwrightHtml = '';
          try {
            browser = await chromium.launch({
              headless: true,
              args: ['--no-sandbox', '--disable-setuid-sandbox'],
            });
            const page = await browser.newPage();
            page.setDefaultTimeout(20000);
            await page.goto(urlToFetch, { waitUntil: 'domcontentloaded', timeout: 20000 });
            finalUrl = page.url();
            try {
              const finalUrlObj = new URL(finalUrl);
              finalOrigin = finalUrlObj.origin;
              if (finalOrigin !== origin) {
                console.log(`[ContactDetector] Domain redirected from ${origin} to ${finalOrigin}`);
              }
            } catch {
              // Keep original origin if URL parsing fails
            }
            
            // Wait for page to fully load
            await sleep(5000);
            
            // Scroll to trigger lazy loading
            await page.evaluate(() => {
              window.scrollTo(0, document.body.scrollHeight);
            });
            await sleep(3000);
            
            // Get the rendered HTML
            playwrightHtml = await page.content();
            await page.close();
          } finally {
            if (browser) {
              try {
                await browser.close();
              } catch {
                // Ignore close errors
              }
            }
          }
          
          console.log(`[ContactDetector] Playwright fallback successful, got ${playwrightHtml.length} chars`);
          
          // Create a proper mock response object so we can continue with normal flow
          // Store HTML in a variable that text() can access
          const htmlContent = playwrightHtml;
          response = {
            ok: true,
            status: 200,
            statusText: 'OK',
            url: finalUrl,
            text: async () => htmlContent,
            headers: new Headers(),
            redirected: false,
            type: 'basic' as ResponseType,
            clone: function() { return this; },
            body: null,
            bodyUsed: false,
            arrayBuffer: async () => new ArrayBuffer(0),
            blob: async () => new Blob(),
            formData: async () => new FormData(),
            json: async () => ({}),
          } as Response;
          
          console.log(`[ContactDetector] Mock response created, continuing with normal flow...`);
          // Break out of error handling - response is set, continue to normal flow
          // We'll skip the rest of the catch block by not returning/throwing
        } catch (playwrightError: any) {
          console.log(`[ContactDetector] Playwright fallback also failed: ${playwrightError.message}`);
          // If Playwright also fails, fall through to the error handler below
        }
      }
      
      // Only return error if we didn't successfully use Playwright fallback
      // Check if response was set (meaning Playwright succeeded)
      if (!response) {
        // Provide more specific error message
        const errorMsg = fetchError.message || fetchError.toString() || "Unknown error";
        return {
          found: false,
          contactUrl: null,
          hasForm: false,
          message: errorMsg.length > 100 ? errorMsg.substring(0, 100) + "..." : errorMsg,
          status: "error",
        };
      }
      // If response is set (Playwright succeeded), continue with normal flow below
    }
    
    // If we got here after SSL error handling with HTTP fallback, response should be set
    // Continue with normal flow

    console.log(`[ContactDetector] Checking response.ok: ${response.ok}, status: ${response.status}`);
    if (!response.ok) {
      // Handle specific HTTP error codes
      let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
      let status: "error" | "not_found" = "error";
      
      if (response.status === 403) {
        // HTTP 403 is a legitimate response - site is blocking automated requests
        // This doesn't mean the site is broken, just that we can't access it
        // Mark as "not_found" instead of "error" since the site likely exists
        errorMessage = "HTTP 403: Forbidden - site may be blocking automated requests";
        status = "not_found";
      } else if (response.status === 401) {
        errorMessage = "HTTP 401: Unauthorized - site requires authentication";
        status = "not_found"; // Site exists but requires auth
      } else if (response.status === 404) {
        errorMessage = "HTTP 404: Page not found";
        status = "not_found";
      } else if (response.status === 429) {
        errorMessage = "HTTP 429: Too Many Requests - rate limited, try again later";
        status = "error"; // Rate limiting is a temporary error
      } else if (response.status === 500) {
        errorMessage = "HTTP 500: Internal Server Error - site may be temporarily down";
        status = "error";
      } else if (response.status === 503 || response.status === 502 || response.status === 504) {
        errorMessage = `HTTP ${response.status}: Service Unavailable - site may be temporarily down`;
        status = "error";
      } else if (response.status === 525) {
        errorMessage = "HTTP 525: SSL Handshake Failed - Cloudflare SSL error";
        status = "error";
      } else if (response.status >= 400 && response.status < 500) {
        errorMessage = `HTTP ${response.status}: Client Error`;
        status = "not_found"; // Client errors often mean page doesn't exist or access denied
      } else if (response.status >= 500) {
        errorMessage = `HTTP ${response.status}: Server Error - site may be temporarily down`;
        status = "error";
      }
      
      return {
        found: false,
        contactUrl: null,
        hasForm: false,
        message: errorMessage,
        status,
      };
    }

    console.log(`[ContactDetector] Extracting HTML from response...`);
    let html = await response.text();
    console.log(`[ContactDetector] Got HTML, length: ${html.length} chars`);

    // Check if page might be JavaScript-rendered (React, Vue, Angular, etc.)
    const hasJSFramework = /react|vue|angular|__NEXT_DATA__|id=["']root["']|id=["']app["']|data-reactroot|_next/i.test(html);
    const hasMinimalContent = html.length < 5000 && !/<body[^>]*>[\s\S]{100,}/i.test(html);
    const hasNoContactLinks = !/(contact|support|help)/i.test(html.toLowerCase());

    // Find contact page links in initial HTML - use finalOrigin after redirects
    let contactUrl = findContactPageLink(html, finalOrigin);
    console.log(`[ContactDetector] Contact URL found in initial HTML: ${contactUrl || 'none'}`);
    
    // Track if we found the URL via common paths (already verified)
    let foundViaCommonPath = false;
    
    // Check if there's a contact form directly on the homepage (before searching for links)
    // This helps with sites that embed forms on homepage
    const hasContactForm7 = /contact-form-7|contactform7/i.test(html);
    const hasFormOnPage = /<form[^>]*>[\s\S]*?<(input|textarea)[^>]*(name|id|placeholder|class)=["'][^"']*(email|contact|message|name)[^"']*["']/i.test(html);
    
    // If Contact Form 7 is present and no contact URL found, check homepage for form
    // Also check if form might be in the HTML (even if regex didn't catch it)
    if (hasContactForm7 && !contactUrl) {
      console.log(`[ContactDetector] Contact Form 7 detected, checking homepage for contact form...`);
      try {
        const hasFormOnHomepage = await checkContactPageHasForm(finalUrl);
        if (hasFormOnHomepage) {
          contactUrl = finalUrl;
          foundViaCommonPath = true;
          console.log(`[ContactDetector] ✅ Found contact form directly on homepage: ${contactUrl}`);
        } else {
          console.log(`[ContactDetector] No form found on homepage, will try common paths...`);
        }
      } catch (error: any) {
        console.log(`[ContactDetector] Homepage form check failed: ${error.message}`);
      }
    }

    // If no contact URL found from initial HTML, also check the provided page (if different from homepage)
    // This helps with resource/blog pages that might have contact forms
    if (!contactUrl && !isHomepage && urlToFetch === homepageUrl) {
      console.log(`[ContactDetector] No contact link found on homepage, checking provided page: ${baseUrl}`);
      try {
        const pageResponse = await fetchWithRetry(
          baseUrl,
          {
            ...options,
            redirect: "follow",
          },
          1,
          2000
        );
        if (pageResponse.ok) {
          const pageHtml = await pageResponse.text();
          const pageContactUrl = findContactPageLink(pageHtml, finalOrigin);
          if (pageContactUrl) {
            contactUrl = pageContactUrl;
            console.log(`[ContactDetector] Found contact link on provided page: ${contactUrl}`);
          }
        }
      } catch (error: any) {
        console.log(`[ContactDetector] Failed to check provided page: ${error.message}`);
      }
    }

    // If page is JavaScript-rendered or no contact links found, use Playwright to get rendered HTML
    if ((hasJSFramework || hasNoContactLinks) && !contactUrl) {
      console.log(`[ContactDetector] JavaScript-rendered site detected or no contact links in static HTML, using Playwright to render page...`);
      try {
        // Use final URL after redirects for Playwright
        const playwrightUrl = finalUrl;
        html = await fetchHomepageWithPlaywright(playwrightUrl);
        console.log(`[ContactDetector] Playwright rendered HTML (${html.length} chars)`);
        // Try finding contact link again in rendered HTML - use finalOrigin
        contactUrl = findContactPageLink(html, finalOrigin);
        console.log(`[ContactDetector] Contact URL found in Playwright-rendered HTML: ${contactUrl || 'none'}`);
      } catch (playwrightError: any) {
        console.log(`[ContactDetector] Playwright failed: ${playwrightError.message}, using static HTML`);
        // Continue with original HTML if Playwright fails
      }
    }
    
    // If still no contact URL found and we tried a non-homepage, try the provided URL with Playwright
    if (!contactUrl && !isHomepage) {
      console.log(`[ContactDetector] No contact link found on homepage, trying provided URL with Playwright...`);
      try {
        html = await fetchHomepageWithPlaywright(finalUrl);
        contactUrl = findContactPageLink(html, finalOrigin);
        console.log(`[ContactDetector] Contact URL found in provided URL HTML: ${contactUrl || 'none'}`);
      } catch (playwrightError: any) {
        console.log(`[ContactDetector] Playwright on provided URL failed: ${playwrightError.message}`);
      }
    }

    // If no contact URL found in links, try common contact page paths directly
    // Also check if site has Contact Form 7 plugin (WordPress) - try common paths
    // (hasContactForm7 already checked above)
    if (hasContactForm7 && !contactUrl) {
      console.log(`[ContactDetector] Contact Form 7 plugin detected, trying common WordPress contact paths...`);
      const cf7Paths = ['/contact/', '/contact-us/', '/contact', '/contact-us'];
      for (const path of cf7Paths) {
        try {
          const cf7Url = `${finalOrigin}${path}`;
          console.log(`[ContactDetector] Trying Contact Form 7 path: ${cf7Url}`);
          const isAccessible = await verifyContactPageWithPlaywright(cf7Url);
          if (isAccessible) {
            const hasForm = await checkContactPageHasForm(cf7Url);
            if (hasForm) {
              contactUrl = cf7Url;
              foundViaCommonPath = true;
              console.log(`[ContactDetector] ✅ Found contact page via Contact Form 7: ${contactUrl}`);
              break;
            }
          }
        } catch (error: any) {
          console.log(`[ContactDetector] Contact Form 7 path ${path} check failed: ${error.message}`);
          continue;
        }
      }
    }
    
    // Also check if there's a contact form directly on the homepage (some sites embed forms)
    if (!contactUrl && !hasContactForm7) {
      console.log(`[ContactDetector] Checking if contact form exists on homepage...`);
      try {
        const hasFormOnHomepage = await checkContactPageHasForm(finalUrl);
        if (hasFormOnHomepage) {
          contactUrl = finalUrl;
          foundViaCommonPath = true;
          console.log(`[ContactDetector] ✅ Found contact form directly on homepage: ${contactUrl}`);
        }
      } catch (error: any) {
        console.log(`[ContactDetector] Homepage form check failed: ${error.message}`);
      }
    }
    
    if (!contactUrl) {
      console.log(`[ContactDetector] No contact link found, trying common contact page paths...`);
      const commonContactPaths = [
        '/p/contact-us.html', // Try this first as it's a common pattern
        '/contact-us/', // WordPress style with trailing slash
        '/contact-us.html',
        '/contact/', // WordPress style with trailing slash
        '/contact',
        '/contact-us',
        '/contact.html',
        '/contact.php',
        '/contactus',
        '/get-in-touch',
        '/reach-us',
        '/contact-page',
        '/contact_page',
        '/support',
        '/support/contact',
        '/help',
        '/help-center',
        '/contact-support',
      ];
      
      // Try each common path to see if it exists and has a form
      // Use finalOrigin after redirects
      for (const path of commonContactPaths) {
        const testUrl = `${finalOrigin}${path}`;
        console.log(`[ContactDetector] Trying common path: ${testUrl}`);
        
        try {
          // Verify it's a contact page and has a form using Playwright
          console.log(`[ContactDetector] Checking accessibility for: ${testUrl}`);
          const isAccessible = await verifyContactPageWithPlaywright(testUrl);
          console.log(`[ContactDetector] Path ${testUrl} accessible: ${isAccessible}`);
          
          if (isAccessible) {
            console.log(`[ContactDetector] Checking for form on: ${testUrl}`);
            const hasForm = await checkContactPageHasForm(testUrl);
            console.log(`[ContactDetector] Path ${testUrl} has form: ${hasForm}`);
            
            if (hasForm) {
              contactUrl = testUrl;
              foundViaCommonPath = true;
              console.log(`[ContactDetector] ✅ Found contact page via common path: ${contactUrl}`);
              break;
            } else {
              console.log(`[ContactDetector] ⚠️ Path ${testUrl} accessible but no form detected`);
            }
          } else {
            console.log(`[ContactDetector] ⚠️ Path ${testUrl} not accessible or not a contact page`);
          }
        } catch (error: any) {
          // Continue to next path if this one fails
          console.log(`[ContactDetector] ❌ Path ${testUrl} failed: ${error.message}`);
          if (error.stack) {
            console.log(`[ContactDetector] Error stack: ${error.stack.substring(0, 200)}`);
          }
          continue;
        }
      }
    }
    
    if (!contactUrl) {
      return {
        found: false,
        contactUrl: null,
        hasForm: false,
        message: "Contact page link not found in header or footer, and common contact paths not accessible",
        status: "not_found",
      };
    }

    // If we found via common path, we already verified it and checked for form
    // So we can return success directly
    if (foundViaCommonPath) {
      return {
        found: true,
        contactUrl,
        hasForm: true,
        message: "Contact page found with contact form (via common path)",
        status: "found",
      };
    }

    // Verify contact page link is accessible using Playwright
    // This helps with JavaScript-rendered sites where links might be dynamically loaded
    console.log(`[ContactDetector] Verifying contact page link with Playwright: ${contactUrl}`);
    const isContactPageAccessible = await verifyContactPageWithPlaywright(contactUrl);
    
    if (!isContactPageAccessible) {
      return {
        found: false,
        contactUrl: null,
        hasForm: false,
        message: "Contact page link found but page is not accessible",
        status: "not_found",
      };
    }

    // Check if contact page has a contact form (not search/newsletter/etc.)
    const hasContactForm = await checkContactPageHasForm(contactUrl);

    if (!hasContactForm) {
      return {
        found: true,
        contactUrl,
        hasForm: false,
        message: "Contact page found but no contact form detected (may have search/newsletter forms only)",
        status: "no_form",
      };
    }

    return {
      found: true,
      contactUrl,
      hasForm: true,
      message: "Contact page found with contact form",
      status: "found",
    };
  } catch (error: any) {
    // Provide more specific error messages
    let errorMessage = "Error checking contact page";
    
    if (error.message) {
      errorMessage = error.message;
    } else if (error.name === "TypeError" && error.message?.includes("fetch")) {
      errorMessage = "Network error - unable to connect to site";
    } else if (error.message?.includes("CORS")) {
      errorMessage = "CORS error - site blocked the request";
    } else if (error.message?.includes("timeout")) {
      errorMessage = "Request timeout - site took too long to respond";
    } else if (error.message?.includes("redirect")) {
      errorMessage = `Redirect error: ${error.message}`;
    }
    
    // Log the full error for debugging with more context
    console.error(`[ContactDetector] Error checking contact page for ${domainUrl}:`, {
      message: error.message,
      name: error.name,
      stack: error.stack?.substring(0, 500), // First 500 chars of stack
      domainUrl,
    });
    
    return {
      found: false,
      contactUrl: null,
      hasForm: false,
      message: errorMessage,
      status: "error",
    };
  }
}

/**
 * Fetch homepage HTML using Playwright (for JavaScript-rendered sites)
 */
async function fetchHomepageWithPlaywright(url: string): Promise<string> {
  let browser: Browser | null = null;
  try {
    browser = await chromium.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });
    
    const page = await browser.newPage();
    page.setDefaultTimeout(45000);
    
    // Navigate to the page
    // Use 'domcontentloaded' which is faster and more reliable
    try {
      await page.goto(url, {
        waitUntil: 'domcontentloaded', // Faster and more reliable
        timeout: 20000,
      });
    } catch (timeoutError: any) {
      // If timeout, check if page still loaded
      const currentUrl = page.url();
      if (currentUrl && currentUrl !== 'about:blank') {
        console.log(`[ContactDetector] Navigation timeout but page did load to ${currentUrl}, continuing...`);
      } else {
        throw timeoutError;
      }
    }
    
    // Wait for page to fully load
    console.log(`[ContactDetector] Waiting for homepage to fully load...`);
    await sleep(5000); // Wait 5 seconds for initial content
    
    // Scroll to trigger lazy loading
    await page.evaluate(() => {
      window.scrollTo(0, document.body.scrollHeight);
    });
    await sleep(3000); // Wait after scroll
    
    // Get the rendered HTML
    const html = await page.content();
    return html;
  } catch (error: any) {
    console.log(`[ContactDetector] Playwright fetch failed: ${error.message}`);
    throw error;
  } finally {
    if (browser) {
      try {
        await browser.close();
      } catch {
        // Ignore close errors
      }
    }
  }
}

/**
 * Verify contact page link is accessible using Playwright
 * This helps with JavaScript-rendered sites where links might be dynamically loaded
 */
async function verifyContactPageWithPlaywright(contactUrl: string): Promise<boolean> {
  let browser: Browser | null = null;
  try {
    browser = await chromium.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });
    
    const page = await browser.newPage();
    page.setDefaultTimeout(20000); // 20 second timeout
    
    // Navigate to the contact page
    // Use 'domcontentloaded' which is faster and more reliable than 'load' or 'networkidle'
    let response;
    try {
      response = await page.goto(contactUrl, {
        waitUntil: 'domcontentloaded', // Faster and more reliable
        timeout: 20000,
      });
    } catch (timeoutError: any) {
      // If timeout, check if page still loaded (sometimes page loads but network never idles)
      console.log(`[ContactDetector] Navigation timeout, but checking if page loaded anyway...`);
      const currentUrl = page.url();
      if (currentUrl && currentUrl !== 'about:blank') {
        // Page did navigate, just didn't finish loading - continue anyway
        console.log(`[ContactDetector] Page did navigate to ${currentUrl}, continuing...`);
        response = { ok: () => true, status: () => 200 } as any;
      } else {
        console.log(`[ContactDetector] Page did not navigate, timeout error: ${timeoutError.message}`);
        return false;
      }
    }
    
    // Check if page loaded successfully
    if (!response || (response.ok && !response.ok())) {
      console.log(`[ContactDetector] Contact page returned ${response?.status?.() || 'no response'}`);
      return false;
    }
    
    // Wait for page to fully load - wait for additional time for dynamic content
    console.log(`[ContactDetector] Waiting for page to fully load...`);
    await sleep(5000); // Wait 5 seconds for initial content
    
    // Scroll to trigger lazy loading
    await page.evaluate(() => {
      window.scrollTo(0, document.body.scrollHeight);
    });
    await sleep(2000); // Wait after scroll
    
    // Try to wait for common contact form elements to appear (optional, won't fail if not found)
    try {
      await page.waitForSelector('form, input[type="email"], textarea, [name*="contact"], [name*="email"]', {
        timeout: 10000,
      }).catch(() => {
        // Ignore if selectors not found - page might still be valid
        console.log(`[ContactDetector] Form elements not found, but continuing verification`);
      });
    } catch {
      // Continue even if form elements aren't found
    }
    
    // Additional wait for any remaining dynamic content
    await sleep(3000); // Final wait for any remaining content
    
    // Get the final URL (in case of redirects)
    const finalUrl = page.url();
    
    // Check if we're still on a contact-related page (not redirected to 404, etc.)
    const pageTitle = await page.title();
    const pageContent = await page.content();
    
    // Check if page content suggests it's a contact page
    const hasContactContent = /contact|get in touch|reach us|send message|write us|support|help center/i.test(pageContent.toLowerCase());
    const urlPath = new URL(finalUrl).pathname.toLowerCase();
    const isContactPage = /contact|get-in-touch|reach-us|contactus|support|help/i.test(finalUrl) || 
                          /contact|get-in-touch|reach-us|contactus|support|help/i.test(pageTitle) ||
                          /contact|get-in-touch|reach-us|contactus|support|help/i.test(urlPath) ||
                          hasContactContent;
    
    // If URL clearly indicates contact page (e.g., /p/contact-us.html), be more lenient
    const isClearContactUrl = /\/p\/contact|\/contact-us|\/contact\.html|\/contact\.php|\/support|\/help/i.test(urlPath);
    
    console.log(`[ContactDetector] Contact page verified: ${finalUrl}, isContactPage: ${isContactPage}, isClearContactUrl: ${isClearContactUrl}`);
    
    // Accept if it's clearly a contact URL or has contact content
    return isContactPage || (isClearContactUrl && response.ok());
  } catch (error: any) {
    console.log(`[ContactDetector] Playwright verification failed: ${error.message}`);
    return false;
  } finally {
    if (browser) {
      try {
        await browser.close();
      } catch {
        // Ignore close errors
      }
    }
  }
}

function findContactPageLink(html: string, origin: string): string | null {
  // Common contact page patterns - more comprehensive
  // Added support for "contact us" (with space), "support", "help", etc.
  const contactPatterns = [
    /href=["']([^"']*\/contact[^"']*?)["']/gi,
    /href=["']([^"']*\/contact-us[^"']*?)["']/gi,
    /href=["']([^"']*\/contact\.html[^"']*?)["']/gi,
    /href=["']([^"']*\/contact\.php[^"']*?)["']/gi,
    /href=["']([^"']*\/get-in-touch[^"']*?)["']/gi,
    /href=["']([^"']*\/reach-us[^"']*?)["']/gi,
    /href=["']([^"']*\/contactus[^"']*?)["']/gi,
    /href=["']([^"']*\/contact_page[^"']*?)["']/gi,
    /href=["']([^"']*\/p\/contact[^"']*?)["']/gi, // For /p/contact-us.html style URLs
    /href=["']([^"']*\/p\/contact-us[^"']*?)["']/gi,
    /href=["']([^"']*\/support[^"']*?)["']/gi, // Support pages
    /href=["']([^"']*\/help[^"']*?)["']/gi, // Help pages
    /href=["']([^"']*\/contact.*us[^"']*?)["']/gi, // "contact us" with space or hyphen
  ];

  // Extract header and footer sections
  const headerMatch = html.match(/<header[^>]*>([\s\S]*?)<\/header>/i);
  const footerMatch = html.match(/<footer[^>]*>([\s\S]*?)<\/footer>/i);
  const navMatch = html.match(/<nav[^>]*>([\s\S]*?)<\/nav>/gi);
  
  // Also search in menu containers (common in WordPress and other CMS)
  // Look for menu items with contact links directly
  const menuItemsMatch = html.match(/<li[^>]*>[\s\S]*?<a[^>]*href=["'][^"']*contact[^"']*["'][^>]*>[\s\S]*?<\/a>[\s\S]*?<\/li>/gi);

  const sectionsToSearch = [
    headerMatch ? headerMatch[1] : "",
    footerMatch ? footerMatch[1] : "",
    ...(navMatch || []),
    ...(menuItemsMatch || []),
  ].join(" ");

  // Helper function to find contact URL in text
  const findContactInText = (text: string): string | null => {
    for (const pattern of contactPatterns) {
      const matches = [...text.matchAll(pattern)];
      for (const match of matches) {
        if (match[1]) {
          let contactUrl = match[1].trim();

          // Skip if it's clearly not a contact page
          // Filter out CSS, JS, image files, and other assets
          // Check both the raw URL and normalized URL
          const urlToCheck = contactUrl.toLowerCase();
          const hasAssetExtension = urlToCheck.match(/\.(css|js|jpg|jpeg|png|gif|svg|ico|woff|woff2|ttf|eot|pdf|zip|xml|json|map)(\?|$|#)/i);
          const isAssetPath = urlToCheck.includes('/wp-content/') ||
            urlToCheck.includes('/assets/') ||
            urlToCheck.includes('/static/') ||
            urlToCheck.includes('/css/') ||
            urlToCheck.includes('/js/') ||
            urlToCheck.includes('/images/') ||
            urlToCheck.includes('/img/') ||
            urlToCheck.includes('/fonts/') ||
            urlToCheck.includes('/plugins/') ||
            urlToCheck.includes('/themes/') ||
            urlToCheck.includes('/includes/');
          
          if (
            (contactUrl.includes('#') && !contactUrl.includes('/contact')) ||
            hasAssetExtension ||
            isAssetPath
          ) {
            continue;
          }

          // Handle relative URLs
          if (contactUrl.startsWith("/")) {
            contactUrl = origin + contactUrl;
          } else if (!contactUrl.startsWith("http")) {
            contactUrl = origin + "/" + contactUrl;
          }

          // Normalize trailing slashes for comparison (but keep them in the URL)
          // Remove trailing slash for pathname comparison
          const normalizedContactUrl = contactUrl.endsWith('/') && contactUrl.length > origin.length + 1
            ? contactUrl.slice(0, -1)
            : contactUrl;

          // Validate it's from the same domain
          try {
            const contactUrlObj = new URL(normalizedContactUrl);
            const originObj = new URL(origin);
            
            // Compare origins (handle www vs non-www as same domain)
            const contactHost = contactUrlObj.hostname.replace(/^www\./, '');
            const originHost = originObj.hostname.replace(/^www\./, '');
            
            if (contactHost === originHost || contactUrlObj.origin === originObj.origin) {
              // Additional validation: URL should contain "contact" in path
              // Normalize pathname by removing trailing slash for comparison
              let urlPath = contactUrlObj.pathname.toLowerCase();
              if (urlPath.endsWith('/') && urlPath.length > 1) {
                urlPath = urlPath.slice(0, -1);
              }
              
              if (urlPath.includes('contact') || urlPath.includes('get-in-touch') || urlPath.includes('reach-us') || 
                  urlPath.includes('/p/contact') || urlPath.includes('/p/contact-us') ||
                  urlPath.includes('support') || urlPath.includes('help')) {
                // Return the original URL (with trailing slash if it had one)
                return contactUrl;
              }
            }
          } catch {
            // Invalid URL, continue
          }
        }
      }
    }
    return null;
  };

  // First, try header/footer/nav sections (most reliable)
  if (sectionsToSearch.trim()) {
    const result = findContactInText(sectionsToSearch);
    if (result) {
      return result;
    }
  }

  // If not found in header/footer, search the full HTML as fallback
  // But filter more aggressively to avoid matching asset files
  const fullHtmlResult = findContactInText(html);
  if (fullHtmlResult) {
    // Double-check it's not an asset file
    const urlObj = new URL(fullHtmlResult);
    const pathname = urlObj.pathname.toLowerCase();
    if (!pathname.match(/\.(css|js|jpg|jpeg|png|gif|svg|ico|woff|woff2|ttf|eot|pdf|zip|xml|json|map)$/i) &&
        !pathname.includes('/wp-content/') &&
        !pathname.includes('/assets/') &&
        !pathname.includes('/static/') &&
        !pathname.includes('/css/') &&
        !pathname.includes('/js/') &&
        !pathname.includes('/images/') &&
        !pathname.includes('/img/') &&
        !pathname.includes('/fonts/') &&
        !pathname.includes('/plugins/') &&
        !pathname.includes('/themes/') &&
        !pathname.includes('/includes/')) {
      return fullHtmlResult;
    }
  }
  
  return null;
}

async function checkContactPageHasForm(contactUrl: string): Promise<boolean> {
  let browser: Browser | null = null;
  try {
    // Use Playwright to get fully rendered HTML (handles JavaScript-rendered forms)
    browser = await chromium.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });
    
    const page = await browser.newPage();
    page.setDefaultTimeout(20000); // 20 second timeout
    
    // Navigate to the contact page
    // Use 'domcontentloaded' which is faster and more reliable
    let response;
    try {
      response = await page.goto(contactUrl, {
        waitUntil: 'domcontentloaded', // Faster and more reliable
        timeout: 20000,
      });
    } catch (timeoutError: any) {
      // If timeout, check if page still loaded (sometimes page loads but network never idles)
      console.log(`[ContactDetector] Navigation timeout in form check, but checking if page loaded anyway...`);
      const currentUrl = page.url();
      if (currentUrl && currentUrl !== 'about:blank' && currentUrl.includes(contactUrl.split('/').pop() || '')) {
        // Page did navigate, just didn't finish loading - continue anyway
        console.log(`[ContactDetector] Page did navigate to ${currentUrl}, continuing form check...`);
        response = { ok: () => true, status: () => 200 } as any;
      } else {
        console.log(`[ContactDetector] Page did not navigate, timeout error: ${timeoutError.message}`);
        return false;
      }
    }
    
    // Check if page loaded successfully
    if (!response || (response.ok && !response.ok())) {
      console.log(`[ContactDetector] Contact page returned ${response?.status?.() || 'no response'}`);
      return false;
    }
    
    // Wait for page to fully load - wait for additional time for dynamic content
    console.log(`[ContactDetector] Waiting for contact page to fully load...`);
    await sleep(5000); // Wait 5 seconds for initial content
    
    // Scroll to trigger lazy loading
    await page.evaluate(() => {
      window.scrollTo(0, document.body.scrollHeight);
    });
    await sleep(2000); // Wait after scroll
    
    // Try to wait for form elements to appear (optional, won't fail if not found)
    try {
      await page.waitForSelector('form, input[type="email"], textarea, [name*="contact"], [name*="email"]', {
        timeout: 10000,
      }).catch(() => {
        // Ignore if selectors not found - page might still be valid
        console.log(`[ContactDetector] Form elements not found immediately, but continuing check`);
      });
    } catch {
      // Continue even if form elements aren't found immediately
    }
    
    // Additional wait for any remaining dynamic content
    await sleep(3000); // Final wait for any remaining content
    
    // Use Playwright to evaluate form fields directly (more reliable than regex)
    const formInfo = await page.evaluate(() => {
      const forms = Array.from(document.querySelectorAll('form'));
      if (forms.length === 0) return null;
      
      for (const form of forms) {
        const inputs = Array.from(form.querySelectorAll('input, textarea, select'));
        const fields = inputs
          .filter(f => {
            const type = (f as HTMLInputElement).type?.toLowerCase();
            return type !== 'submit' && type !== 'button' && type !== 'hidden' && type !== 'reset';
          })
          .map(f => {
            const name = (f as HTMLInputElement).name || (f as HTMLElement).id || '';
            const type = (f as HTMLInputElement).type?.toLowerCase() || '';
            const placeholder = (f as HTMLInputElement).placeholder || '';
            const label = f.closest('label')?.textContent || 
                        (f.previousElementSibling?.tagName === 'LABEL' ? f.previousElementSibling.textContent : '') ||
                        '';
            
            return {
              name: name.toLowerCase(),
              type: type,
              placeholder: placeholder.toLowerCase(),
              label: label.toLowerCase(),
              tagName: f.tagName.toLowerCase()
            };
          });
        
        if (fields.length === 0) continue;
        
        // Check for contact form indicators
        let hasName = false;
        let hasEmail = false;
        let hasMessage = false;
        let hasPhone = false;
        
        for (const field of fields) {
          const combined = `${field.name} ${field.placeholder} ${field.label}`;
          
          if (/name|fullname|firstname|lastname|your.?name/i.test(combined)) hasName = true;
          if (/email|e-mail/i.test(combined) || field.type === 'email') hasEmail = true;
          if (/message|comment|inquiry|enquiry|query|question|feedback|tell.?us/i.test(combined) || field.tagName === 'textarea') hasMessage = true;
          if (/phone|telephone|tel|mobile/i.test(combined)) hasPhone = true;
        }
        
        // Check if it's a non-contact form (search, newsletter, login)
        const isSearch = fields.some(f => /search|q|query|s/i.test(f.name + f.placeholder + f.label));
        const isNewsletter = fields.some(f => /newsletter|subscribe|sign.?up/i.test(f.name + f.placeholder + f.label));
        const isLogin = fields.some(f => /username|user|login|password|pass/i.test(f.name + f.placeholder + f.label));
        
        if (isSearch || (isNewsletter && !hasName && !hasMessage) || isLogin) {
          continue; // Skip this form
        }
        
        // Contact form should have at least email OR (name + message) OR (email + message)
        if (hasEmail || (hasName && hasMessage) || (hasEmail && hasMessage) || (hasEmail && hasName) || (hasMessage && fields.length >= 2)) {
          return {
            found: true,
            hasName,
            hasEmail,
            hasMessage,
            hasPhone,
            fieldCount: fields.length
          };
        }
      }
      
      return null;
    });
    
    if (formInfo && formInfo.found) {
      console.log(`[ContactDetector] Form detected via Playwright evaluation: name=${formInfo.hasName}, email=${formInfo.hasEmail}, message=${formInfo.hasMessage}, fields=${formInfo.fieldCount}`);
      return true;
    }
    
    // Fallback to HTML regex check if Playwright evaluation didn't find it
    const html = await page.content();

    // Check for form elements
    const hasFormTag = /<form[^>]*>/i.test(html);
    if (!hasFormTag) {
      return false;
    }

    // Extract all form fields (input, textarea, select)
    const formFields = html.match(/<(input|textarea|select)[^>]*>/gi) || [];
    
    if (formFields.length === 0) {
      return false;
    }

    // Contact form field indicators (name, id, placeholder, label text)
    const contactFormIndicators = [
      // Field names
      /name=["'](name|fullname|full_name|firstname|first_name|lastname|last_name|contact_name|your_name)/i,
      /name=["'](email|e-mail|email_address|contact_email|your_email)/i,
      /name=["'](message|msg|comment|comments|inquiry|enquiry|query|questions|feedback)/i,
      /name=["'](subject|topic|subject_line)/i,
      /name=["'](phone|telephone|tel|mobile|contact_phone|phone_number)/i,
      // Field IDs
      /id=["'](name|fullname|full_name|firstname|first_name|lastname|last_name|contact_name|your_name)/i,
      /id=["'](email|e-mail|email_address|contact_email|your_email)/i,
      /id=["'](message|msg|comment|comments|inquiry|enquiry|query|questions|feedback)/i,
      /id=["'](subject|topic|subject_line)/i,
      /id=["'](phone|telephone|tel|mobile|contact_phone|phone_number)/i,
      // Placeholders
      /placeholder=["']([^"']*(name|full name|your name|first name|last name)[^"']*)/i,
      /placeholder=["']([^"']*(email|e-mail|your email|contact email)[^"']*)/i,
      /placeholder=["']([^"']*(message|comment|inquiry|enquiry|query|question|feedback|tell us)[^"']*)/i,
      /placeholder=["']([^"']*(subject|topic)[^"']*)/i,
      /placeholder=["']([^"']*(phone|telephone|mobile|contact)[^"']*)/i,
      // Labels (check nearby text)
      /<label[^>]*>([^<]*(name|full name|your name|first name|last name)[^<]*)<\/label>/i,
      /<label[^>]*>([^<]*(email|e-mail|your email|contact email)[^<]*)<\/label>/i,
      /<label[^>]*>([^<]*(message|comment|inquiry|enquiry|query|question|feedback|tell us)[^<]*)<\/label>/i,
      /<label[^>]*>([^<]*(subject|topic)[^<]*)<\/label>/i,
      /<label[^>]*>([^<]*(phone|telephone|mobile|contact)[^<]*)<\/label>/i,
    ];

    // Non-contact form indicators (search, newsletter, login, etc.)
    const nonContactFormIndicators = [
      /name=["'](search|q|query|s)/i,
      /id=["'](search|q|query|s)/i,
      /placeholder=["']([^"']*(search|find|look for)[^"']*)/i,
      /name=["'](newsletter|subscribe|email_signup|newsletter_email)/i,
      /id=["'](newsletter|subscribe|email_signup|newsletter_email)/i,
      /placeholder=["']([^"']*(newsletter|subscribe|sign up)[^"']*)/i,
      /name=["'](username|user|login|password|pass)/i,
      /id=["'](username|user|login|password|pass)/i,
      /placeholder=["']([^"']*(username|login|password|sign in)[^"']*)/i,
      /action=["']([^"']*\/(search|login|signin|signup|subscribe|newsletter)[^"']*)/i,
      /<form[^>]*action=["']([^"']*\/(search|login|signin|signup|subscribe|newsletter)[^"']*)/i,
    ];

    // Check if form has non-contact indicators (exclude these)
    const hasNonContactIndicators = nonContactFormIndicators.some(pattern => 
      pattern.test(html)
    );

    if (hasNonContactIndicators) {
      // Check if it also has contact indicators (might be a mixed form)
      const hasContactIndicators = contactFormIndicators.some(pattern => 
        pattern.test(html)
      );
      
      // If it has non-contact indicators but no contact indicators, it's not a contact form
      if (!hasContactIndicators) {
        return false;
      }
    }

    // Check for contact form indicators
    const hasContactIndicators = contactFormIndicators.some(pattern => 
      pattern.test(html)
    );

    // Must have at least one contact form indicator
    if (!hasContactIndicators) {
      return false;
    }

    // Check for email field specifically (contact forms usually have email)
    // More flexible: check for email in any attribute or type
    const hasEmailField = /<(input|textarea)[^>]*(name|id|placeholder|class|type)=["']([^"']*email[^"']*)["']/i.test(html) ||
                          /type=["']email["']/i.test(html) ||
                          /<input[^>]*type=["']email["']/i.test(html);

    // Check for message/comment field (contact forms usually have a message field)
    // More flexible: check for message/comment in any attribute
    const hasMessageField = /<(input|textarea)[^>]*(name|id|placeholder|class)=["']([^"']*(message|comment|inquiry|enquiry|query|question|feedback)[^"']*)["']/i.test(html) ||
                            /<textarea[^>]*>/i.test(html); // Textarea is often used for messages

    // Check for name field (contact forms often have name field)
    const hasNameField = /<(input|textarea)[^>]*(name|id|placeholder|class)=["']([^"']*(name|fullname|full_name|firstname|first_name|lastname|last_name|contact_name|your_name)[^"']*)["']/i.test(html);

    // Contact form should have at least:
    // 1. Email field, OR
    // 2. Message field (textarea or message/comment field), OR  
    // 3. Name + Email combination (typical contact form)
    // Also, if we're on a contact page and have a form with multiple fields, it's likely a contact form
    const hasMultipleFields = formFields.length >= 2;
    const isLikelyContactForm = (hasEmailField && hasMessageField) || 
                                (hasEmailField && hasNameField) ||
                                (hasEmailField && hasMultipleFields) ||
                                (hasMessageField && hasMultipleFields);

    return isLikelyContactForm || hasEmailField || hasMessageField;
  } catch (error: any) {
    console.log(`[ContactDetector] Playwright form check failed: ${error.message}`);
    return false;
  } finally {
    if (browser) {
      try {
        await browser.close();
      } catch {
        // Ignore close errors
      }
    }
  }
}

