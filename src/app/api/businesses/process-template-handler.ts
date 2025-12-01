import fs from "fs/promises";
import path from "path";
import { JSDOM } from "jsdom";

/**
 * Process template and inject business data
 */
export async function processTemplateWithBusinessData(
  templateCategory: string,
  templateName: string,
  businessData: any
) {
  const templatePath = path.join(
    process.cwd(),
    "templates",
    templateCategory,
    templateName
  );

  // Check if template exists
  try {
    await fs.access(templatePath);
  } catch {
    throw new Error("Template not found");
  }

  // Read template HTML
  const indexPath = path.join(templatePath, "index.html");
  const html = await fs.readFile(indexPath, "utf-8");
  const dom = new JSDOM(html);
  const document = dom.window.document;

  // Generate logo URL
  const logoUrl = `/api/logo/generate?name=${encodeURIComponent(businessData.name)}&category=${encodeURIComponent(Array.isArray(businessData.categories) ? businessData.categories[0] || "business" : "business")}`;

  // Inject business data into template
  await injectBusinessData(document, businessData, logoUrl, templatePath);

  // Create dynamic pages (about, contact, etc.)
  const dynamicPages = await createDynamicPages(businessData, templatePath, document);

  // Get modified HTML
  const modifiedHtml = dom.serialize();

  return {
    success: true,
    html: modifiedHtml,
    logoUrl,
    dynamicPages,
  };
}

/**
 * Inject business data into template HTML
 */
async function injectBusinessData(
  document: Document,
  businessData: any,
  logoUrl: string,
  templatePath: string
): Promise<void> {
  // Replace logo images
  const logoImages = document.querySelectorAll("img[src*='logo'], .logo img, header img, nav img, [class*='logo'] img");
  logoImages.forEach((img: any) => {
    if (img.src && (img.src.includes("logo") || img.alt?.toLowerCase().includes("logo") || img.className?.toLowerCase().includes("logo"))) {
      img.src = logoUrl;
      img.alt = `${businessData.name} Logo`;
    }
  });

  // Replace text-based logos (like .logo, .brand, etc.)
  // Try multiple selector patterns to catch all logo variations
  const logoSelectors = [
    "a.logo",
    "a.brand", 
    "a[class*='logo']",
    ".logo a",
    ".brand a",
    "h1 a.logo",
    "h2 a.logo",
    "header a.logo",
    "nav a.logo",
    ".navbar a.logo",
    ".header a.logo"
  ];
  
  const processedElements = new Set();
  
  logoSelectors.forEach(selector => {
    try {
      const logoLinks = document.querySelectorAll(selector);
      logoLinks.forEach((logoEl: any) => {
        // Skip if already processed
        if (processedElements.has(logoEl)) {
          return;
        }
        
        // Skip if it contains an img (already handled above)
        if (logoEl.querySelector("img")) {
          return;
        }
        
        // Only process anchor tags
        if (logoEl.tagName !== "A" && logoEl.tagName !== "a") {
          return;
        }
        
        processedElements.add(logoEl);
        
        // Create logo image
        const logoImg = document.createElement("img");
        logoImg.setAttribute("src", logoUrl);
        logoImg.setAttribute("alt", `${businessData.name} Logo`);
        logoImg.style.cssText = "max-height: 50px; height: auto; width: auto; vertical-align: middle; display: inline-block; margin-right: 8px;";
        
        // Keep the span structure if it exists (like "Foodie<span>.</span>")
        const span = logoEl.querySelector("span");
        if (span) {
          // Replace content with image + business name + span
          logoEl.innerHTML = "";
          logoEl.appendChild(logoImg);
          logoEl.appendChild(document.createTextNode(businessData.name));
          logoEl.appendChild(span.cloneNode(true));
        } else {
          // Replace content with image + business name
          logoEl.innerHTML = "";
          logoEl.appendChild(logoImg);
          logoEl.appendChild(document.createTextNode(businessData.name));
        }
      });
    } catch (e) {
      // Ignore invalid selectors
      console.warn(`Invalid selector: ${selector}`, e);
    }
  });

  // Also handle .logo elements that are not links (div.logo, h1.logo, etc.)
  const textLogos = document.querySelectorAll(".logo:not(a):not(img), .brand:not(a):not(img), .logo-text, [class*='logo']:not(a):not(img)");
  textLogos.forEach((logoEl: any) => {
    // Skip if it contains an img (already handled above) or if it's a link (handled above)
    if (logoEl.querySelector("img") || logoEl.tagName === "A" || logoEl.tagName === "a") {
      return;
    }
    
    // Check if it contains a logo link (already processed)
    if (logoEl.querySelector("a.logo, a.brand")) {
      return;
    }
    
    // Create logo image
    const logoImg = document.createElement("img");
    logoImg.src = logoUrl;
    logoImg.alt = `${businessData.name} Logo`;
    logoImg.style.maxHeight = "50px";
    logoImg.style.height = "auto";
    logoImg.style.width = "auto";
    logoImg.style.verticalAlign = "middle";
    logoImg.style.marginRight = "10px";
    logoImg.style.display = "inline-block";
    
    // Insert image before existing content
    if (logoEl.firstChild) {
      logoEl.insertBefore(logoImg, logoEl.firstChild);
    } else {
      logoEl.appendChild(logoImg);
    }
    
    // Update text content in child nodes
    const updateTextContent = (node: any) => {
      if (node.nodeType === 3) { // Text node
        const text = node.textContent.trim();
        if (text.length > 0 && text.length < 50 && !text.toLowerCase().includes("home")) {
          node.textContent = businessData.name;
        }
      } else if (node.nodeType === 1) { // Element node
        // Skip if it's a span (might be decorative)
        if (node.tagName === "SPAN" || node.tagName === "span") {
          return;
        }
        // Recursively update text nodes
        Array.from(node.childNodes).forEach(updateTextContent);
      }
    };
    
    Array.from(logoEl.childNodes).forEach(updateTextContent);
  });

  // Replace business name in header/nav (fallback for elements not caught by logo selectors)
  const headers = document.querySelectorAll("header, nav, .header, .navbar, [class*='header'], [class*='nav']");
  headers.forEach((header) => {
    const nameElements = header.querySelectorAll("h1, h2, .brand, .logo-text");
    nameElements.forEach((el) => {
      // Skip if already processed as logo
      if (el.classList.contains("logo") || el.classList.contains("brand")) {
        return;
      }
      
      if (el.textContent && el.textContent.length < 50 && !el.textContent.includes("Home")) {
        const text = el.textContent.trim();
        if (text.length > 0 && text.length < 30) {
          el.textContent = businessData.name;
        }
      }
    });
  });

  // Replace title
  const title = document.querySelector("title");
  if (title) {
    title.textContent = `${businessData.name} - ${businessData.description || "Professional Services"}`;
  }

  // Replace meta description
  let metaDesc = document.querySelector('meta[name="description"]');
  if (!metaDesc) {
    metaDesc = document.createElement("meta");
    metaDesc.setAttribute("name", "description");
    document.head.appendChild(metaDesc);
  }
  metaDesc.setAttribute("content", businessData.description || `${businessData.name} - Professional Services`);

  // Replace contact information in footer
  const footers = document.querySelectorAll("footer, .footer, [class*='footer']");
  footers.forEach((footer) => {
    // Replace phone numbers
    if (businessData.phone) {
      const phoneLinks = footer.querySelectorAll("a[href^='tel:']");
      phoneLinks.forEach((link: any) => {
        link.href = `tel:${businessData.phone}`;
        link.textContent = businessData.phone;
      });
    }

    // Replace address
    const addressElements = footer.querySelectorAll(".address, [class*='address'], [class*='location']");
    addressElements.forEach((el) => {
      if (businessData.address && el.textContent && el.textContent.length < 100) {
        el.textContent = businessData.address;
      }
    });

    // Replace email
    const emailElements = footer.querySelectorAll("a[href^='mailto:'], .email, [class*='email']");
    emailElements.forEach((el: any) => {
      if (businessData.email) {
        el.href = `mailto:${businessData.email}`;
        el.textContent = businessData.email;
      }
    });

    // Replace website
    const websiteElements = footer.querySelectorAll("a[href^='http'], .website, [class*='website']");
    websiteElements.forEach((el: any) => {
      if (businessData.website && !el.href.includes("mailto") && el.href !== "#") {
        el.href = businessData.website;
        if (el.textContent && el.textContent.length < 50) {
          el.textContent = businessData.website.replace(/^https?:\/\//, "");
        }
      }
    });
  });

  // Replace placeholders in content
  const body = document.body;
  if (body) {
    const placeholders: Record<string, string> = {
      "{{business.name}}": businessData.name,
      "{{business.phone}}": businessData.phone || "",
      "{{business.email}}": businessData.email || "",
      "{{business.address}}": businessData.address || "",
      "{{business.website}}": businessData.website || "",
      "{{business.description}}": businessData.description || "",
    };

    Object.entries(placeholders).forEach(([placeholder, value]) => {
      body.innerHTML = body.innerHTML.replace(
        new RegExp(placeholder.replace(/[{}]/g, "\\$&"), "g"),
        value
      );
    });
  }
}

/**
 * Create dynamic pages (about, contact, etc.)
 */
async function createDynamicPages(
  businessData: any,
  templatePath: string,
  document: Document
): Promise<Record<string, string>> {
  const pages: Record<string, string> = {};

  // Create About page
  const aboutHtml = generateAboutPage(businessData, document);
  pages["about.html"] = aboutHtml;

  // Create Contact page
  const contactHtml = generateContactPage(businessData, document);
  pages["contact.html"] = contactHtml;

  return pages;
}

/**
 * Generate About page HTML
 */
function generateAboutPage(businessData: any, baseDocument: Document): string {
  const aboutDoc = baseDocument.cloneNode(true) as Document;
  const body = aboutDoc.body;

  // Find main content area
  const main = body.querySelector("main, .main, .content, #content") || body;

  main.innerHTML = `
    <section class="about-section" style="padding: 4rem 2rem; max-width: 1200px; margin: 0 auto;">
      <h1 style="font-size: 2.5rem; margin-bottom: 2rem; text-align: center;">About ${businessData.name}</h1>
      
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 3rem; margin-bottom: 3rem;">
        <div>
          <h2 style="font-size: 1.8rem; margin-bottom: 1rem;">Our Story</h2>
          <p style="line-height: 1.8; color: #666; margin-bottom: 1rem;">
            ${businessData.description || `Welcome to ${businessData.name}! We are dedicated to providing exceptional service and quality products to our customers.`}
          </p>
          <p style="line-height: 1.8; color: #666;">
            With years of experience in the industry, we have built a reputation for excellence and customer satisfaction. 
            Our team is committed to delivering the best possible experience for every customer.
          </p>
        </div>
        
        <div>
          <h2 style="font-size: 1.8rem; margin-bottom: 1rem;">Why Choose Us?</h2>
          <ul style="list-style: none; padding: 0;">
            <li style="padding: 0.5rem 0; border-bottom: 1px solid #eee;">
              <strong>Quality Service:</strong> We prioritize quality in everything we do
            </li>
            <li style="padding: 0.5rem 0; border-bottom: 1px solid #eee;">
              <strong>Expert Team:</strong> Our experienced professionals are here to help
            </li>
            <li style="padding: 0.5rem 0; border-bottom: 1px solid #eee;">
              <strong>Customer Focus:</strong> Your satisfaction is our top priority
            </li>
            <li style="padding: 0.5rem 0;">
              <strong>Local Business:</strong> Proudly serving our community
            </li>
          </ul>
        </div>
      </div>
      
      <div style="background: #f5f5f5; padding: 2rem; border-radius: 8px; margin-top: 3rem;">
        <h2 style="font-size: 1.8rem; margin-bottom: 1rem;">Contact Information</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.5rem;">
          ${businessData.address ? `<div><strong>Address:</strong><br>${businessData.address}</div>` : ""}
          ${businessData.phone ? `<div><strong>Phone:</strong><br><a href="tel:${businessData.phone}">${businessData.phone}</a></div>` : ""}
          ${businessData.email ? `<div><strong>Email:</strong><br><a href="mailto:${businessData.email}">${businessData.email}</a></div>` : ""}
          ${businessData.website ? `<div><strong>Website:</strong><br><a href="${businessData.website}" target="_blank">${businessData.website}</a></div>` : ""}
        </div>
      </div>
    </section>
  `;

  // Update page title
  const title = aboutDoc.querySelector("title");
  if (title) {
    title.textContent = `About Us - ${businessData.name}`;
  }

  return aboutDoc.documentElement.outerHTML;
}

/**
 * Generate Contact page HTML
 */
function generateContactPage(businessData: any, baseDocument: Document): string {
  const contactDoc = baseDocument.cloneNode(true) as Document;
  const body = contactDoc.body;

  const main = body.querySelector("main, .main, .content, #content") || body;

  main.innerHTML = `
    <section class="contact-section" style="padding: 4rem 2rem; max-width: 1200px; margin: 0 auto;">
      <h1 style="font-size: 2.5rem; margin-bottom: 2rem; text-align: center;">Contact ${businessData.name}</h1>
      
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 3rem;">
        <div>
          <h2 style="font-size: 1.8rem; margin-bottom: 1.5rem;">Get in Touch</h2>
          <p style="line-height: 1.8; color: #666; margin-bottom: 2rem;">
            We'd love to hear from you! Reach out to us using any of the methods below.
          </p>
          
          <div style="margin-bottom: 2rem;">
            ${businessData.address ? `
              <div style="margin-bottom: 1.5rem;">
                <h3 style="font-size: 1.2rem; margin-bottom: 0.5rem;">📍 Address</h3>
                <p style="color: #666;">${businessData.address}</p>
              </div>
            ` : ""}
            
            ${businessData.phone ? `
              <div style="margin-bottom: 1.5rem;">
                <h3 style="font-size: 1.2rem; margin-bottom: 0.5rem;">📞 Phone</h3>
                <p style="color: #666;"><a href="tel:${businessData.phone}" style="color: inherit; text-decoration: none;">${businessData.phone}</a></p>
              </div>
            ` : ""}
            
            ${businessData.email ? `
              <div style="margin-bottom: 1.5rem;">
                <h3 style="font-size: 1.2rem; margin-bottom: 0.5rem;">✉️ Email</h3>
                <p style="color: #666;"><a href="mailto:${businessData.email}" style="color: inherit; text-decoration: none;">${businessData.email}</a></p>
              </div>
            ` : ""}
          </div>
        </div>
        
        <div>
          <h2 style="font-size: 1.8rem; margin-bottom: 1.5rem;">Send us a Message</h2>
          <form style="display: flex; flex-direction: column; gap: 1rem;">
            <input type="text" placeholder="Your Name" required style="padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px;">
            <input type="email" placeholder="Your Email" required style="padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px;">
            <input type="tel" placeholder="Your Phone" style="padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px;">
            <textarea placeholder="Your Message" rows="6" required style="padding: 0.75rem; border: 1px solid #ddd; border-radius: 4px; resize: vertical;"></textarea>
            <button type="submit" style="padding: 0.75rem 2rem; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 1rem;">
              Send Message
            </button>
          </form>
        </div>
      </div>
    </section>
  `;

  const title = contactDoc.querySelector("title");
  if (title) {
    title.textContent = `Contact Us - ${businessData.name}`;
  }

  return contactDoc.documentElement.outerHTML;
}

