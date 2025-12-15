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
      }

      const response = await fetch(url, options);

      // If we get a 429 (Too Many Requests) or 503 (Service Unavailable), retry
      if (response.status === 429 || response.status === 503) {
        if (attempt < maxRetries) {
          continue;
        }
      }

      return response;
    } catch (error: any) {
      lastError = error;

      // Don't retry on certain errors
      if (
        error.name === "AbortError" ||
        error.message?.includes("CORS") ||
        error.message?.includes("Invalid URL")
      ) {
        throw error;
      }

      // If this is the last attempt, throw the error
      if (attempt === maxRetries) {
        throw error;
      }
    }
  }

  throw lastError || new Error("Failed to fetch after retries");
}

export async function detectContactPage(domainUrl: string): Promise<ContactCheckResult> {
  try {
    // Normalize URL
    let baseUrl = domainUrl.trim();
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
    const origin = url.origin;
    
    // If the provided URL is not the homepage, try the homepage first for better contact link detection
    // But also keep the original URL as a fallback
    const isHomepage = url.pathname === '/' || url.pathname === '';
    const homepageUrl = `${origin}/`;
    
    console.log(`[ContactDetector] Checking contact page for domain: ${origin}`);
    console.log(`[ContactDetector] Provided URL: ${baseUrl}, isHomepage: ${isHomepage}`);

    // Fetch homepage (or provided page) with better error handling and retry logic
    // Prefer homepage for better contact link detection, but fallback to provided URL
    let response: Response;
    let urlToFetch = isHomepage ? baseUrl : homepageUrl;
    
    try {
      // Create abort controller for better timeout handling
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout

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
              Referer: baseUrl, // Add referer to appear more legitimate
            },
            signal: controller.signal,
            redirect: "follow",
          },
          1, // 1 retry (2 total attempts)
          2000 // 2 second delay between retries
        );
        clearTimeout(timeoutId);
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
      if (fetchError.message?.includes("CERT") || fetchError.message?.includes("SSL")) {
        return {
          found: false,
          contactUrl: null,
          hasForm: false,
          message: "SSL certificate error",
          status: "error",
        };
      }
      throw fetchError; // Re-throw if it's an unknown error
    }

    if (!response.ok) {
      return {
        found: false,
        contactUrl: null,
        hasForm: false,
        message: `HTTP ${response.status}: ${response.statusText}`,
        status: "error",
      };
    }

    let html = await response.text();

    // Check if page might be JavaScript-rendered (React, Vue, Angular, etc.)
    const hasJSFramework = /react|vue|angular|__NEXT_DATA__|id=["']root["']|id=["']app["']|data-reactroot|_next/i.test(html);
    const hasMinimalContent = html.length < 5000 && !/<body[^>]*>[\s\S]{100,}/i.test(html);
    const hasNoContactLinks = !/contact/i.test(html.toLowerCase());

    // Find contact page links in initial HTML
    let contactUrl = findContactPageLink(html, origin);
    console.log(`[ContactDetector] Contact URL found in initial HTML: ${contactUrl || 'none'}`);

    // If page is JavaScript-rendered or no contact links found, use Playwright to get rendered HTML
    if ((hasJSFramework || hasNoContactLinks) && !contactUrl) {
      console.log(`[ContactDetector] JavaScript-rendered site detected or no contact links in static HTML, using Playwright to render page...`);
      try {
        const playwrightUrl = isHomepage ? baseUrl : homepageUrl;
        html = await fetchHomepageWithPlaywright(playwrightUrl);
        console.log(`[ContactDetector] Playwright rendered HTML (${html.length} chars)`);
        // Try finding contact link again in rendered HTML
        contactUrl = findContactPageLink(html, origin);
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
        html = await fetchHomepageWithPlaywright(baseUrl);
        contactUrl = findContactPageLink(html, origin);
        console.log(`[ContactDetector] Contact URL found in provided URL HTML: ${contactUrl || 'none'}`);
      } catch (playwrightError: any) {
        console.log(`[ContactDetector] Playwright on provided URL failed: ${playwrightError.message}`);
      }
    }

    // Track if we found the URL via common paths (already verified)
    let foundViaCommonPath = false;
    
    // If no contact URL found in links, try common contact page paths directly
    if (!contactUrl) {
      console.log(`[ContactDetector] No contact link found, trying common contact page paths...`);
      const commonContactPaths = [
        '/p/contact-us.html', // Try this first as it's a common pattern
        '/contact-us.html',
        '/contact',
        '/contact-us',
        '/contact.html',
        '/contact.php',
        '/contactus',
        '/get-in-touch',
        '/reach-us',
        '/contact-page',
        '/contact_page',
      ];
      
      // Try each common path to see if it exists and has a form
      for (const path of commonContactPaths) {
        const testUrl = `${origin}${path}`;
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
      errorMessage = "Request timeout";
    }
    
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
    const hasContactContent = /contact|get in touch|reach us|send message|write us/i.test(pageContent.toLowerCase());
    const urlPath = new URL(finalUrl).pathname.toLowerCase();
    const isContactPage = /contact|get-in-touch|reach-us|contactus/i.test(finalUrl) || 
                          /contact|get-in-touch|reach-us|contactus/i.test(pageTitle) ||
                          /contact|get-in-touch|reach-us|contactus/i.test(urlPath) ||
                          hasContactContent;
    
    // If URL clearly indicates contact page (e.g., /p/contact-us.html), be more lenient
    const isClearContactUrl = /\/p\/contact|\/contact-us|\/contact\.html|\/contact\.php/i.test(urlPath);
    
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
  ];

  // Extract header and footer sections
  const headerMatch = html.match(/<header[^>]*>([\s\S]*?)<\/header>/i);
  const footerMatch = html.match(/<footer[^>]*>([\s\S]*?)<\/footer>/i);
  const navMatch = html.match(/<nav[^>]*>([\s\S]*?)<\/nav>/gi);

  const sectionsToSearch = [
    headerMatch ? headerMatch[1] : "",
    footerMatch ? footerMatch[1] : "",
    ...(navMatch || []),
  ].join(" ");

  // Helper function to find contact URL in text
  const findContactInText = (text: string): string | null => {
    for (const pattern of contactPatterns) {
      const matches = [...text.matchAll(pattern)];
      for (const match of matches) {
        if (match[1]) {
          let contactUrl = match[1].trim();

          // Skip if it's clearly not a contact page (e.g., contains "contact-form" in wrong context)
          if (contactUrl.includes('#') && !contactUrl.includes('/contact')) {
            continue;
          }

          // Handle relative URLs
          if (contactUrl.startsWith("/")) {
            contactUrl = origin + contactUrl;
          } else if (!contactUrl.startsWith("http")) {
            contactUrl = origin + "/" + contactUrl;
          }

          // Validate it's from the same domain
          try {
            const contactUrlObj = new URL(contactUrl);
            const originObj = new URL(origin);
            if (contactUrlObj.origin === originObj.origin) {
              // Additional validation: URL should contain "contact" in path
              const urlPath = contactUrlObj.pathname.toLowerCase();
              if (urlPath.includes('contact') || urlPath.includes('get-in-touch') || urlPath.includes('reach-us') || 
                  urlPath.includes('/p/contact') || urlPath.includes('/p/contact-us')) {
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
  return findContactInText(html);
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

