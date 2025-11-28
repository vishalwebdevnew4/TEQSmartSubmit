/**
 * Contact page detection utility
 * Searches for contact page links in website header and footer
 */

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

    // Fetch homepage with better error handling and retry logic
    let response: Response;
    try {
      // Create abort controller for better timeout handling
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 15000); // 15 second timeout

      try {
        response = await fetchWithRetry(
          baseUrl,
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

    const html = await response.text();

    // Find contact page links in header and footer
    const contactUrl = findContactPageLink(html, origin);

    if (!contactUrl) {
      return {
        found: false,
        contactUrl: null,
        hasForm: false,
        message: "Contact page link not found in header or footer",
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

function findContactPageLink(html: string, origin: string): string | null {
  // Common contact page patterns
  const contactPatterns = [
    /href=["']([^"']*\/contact[^"']*?)["']/gi,
    /href=["']([^"']*\/contact-us[^"']*?)["']/gi,
    /href=["']([^"']*\/contact\.html[^"']*?)["']/gi,
    /href=["']([^"']*\/contact\.php[^"']*?)["']/gi,
    /href=["']([^"']*\/get-in-touch[^"']*?)["']/gi,
    /href=["']([^"']*\/reach-us[^"']*?)["']/gi,
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

  // Also search the full HTML as fallback
  const searchText = sectionsToSearch || html;

  // Try each pattern
  for (const pattern of contactPatterns) {
    const matches = [...searchText.matchAll(pattern)];
    for (const match of matches) {
      if (match[1]) {
        let contactUrl = match[1].trim();

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
            return contactUrl;
          }
        } catch {
          // Invalid URL, continue
        }
      }
    }
  }

  return null;
}

async function checkContactPageHasForm(contactUrl: string): Promise<boolean> {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 15000);

    try {
      const response = await fetchWithRetry(
        contactUrl,
        {
          method: "GET",
          headers: {
            "User-Agent":
              "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            Accept: "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            Referer: contactUrl,
          },
          signal: controller.signal,
          redirect: "follow",
        },
        1, // 1 retry
        1000 // 1 second delay
      );
      clearTimeout(timeoutId);

      if (!response.ok) {
        return false;
      }

      const html = await response.text();

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
      const hasEmailField = /<(input|textarea)[^>]*(name|id|placeholder)=["']([^"']*email[^"']*)["']/i.test(html) ||
                            /type=["']email["']/i.test(html);

      // Check for message/comment field (contact forms usually have a message field)
      const hasMessageField = /<(input|textarea)[^>]*(name|id|placeholder)=["']([^"']*(message|comment|inquiry|enquiry|query|question|feedback)[^"']*)["']/i.test(html);

      // Contact form should have at least email OR message field
      return hasEmailField || hasMessageField;
    } catch (fetchError) {
      clearTimeout(timeoutId);
      throw fetchError;
    }
  } catch (error: any) {
    // Silently fail - if we can't check the form, assume no form
    return false;
  }
}

