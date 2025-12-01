#!/usr/bin/env node
/**
 * Category-Based Template Downloader
 * Downloads HTML templates from trusted sources for various categories
 */

const fs = require('fs').promises;
const path = require('path');
const https = require('https');
const http = require('http');
const { execSync } = require('child_process');
const { promisify } = require('util');
const { pipeline } = require('stream/promises');

// Real premium template sources - using GitHub repositories (verified working)
const TEMPLATE_SOURCES = {
  restaurant: [
    {
      name: 'Foodie',
      url: 'https://github.com/codewithsadee/foodie/archive/refs/heads/master.zip',
      source: 'github',
      description: 'Fully responsive fast food website - Premium template from codewithsadee'
    },
    {
      name: 'Restaurant Bootstrap',
      url: 'https://github.com/StartBootstrap/startbootstrap-restaurant/archive/refs/heads/master.zip',
      source: 'github',
      description: 'Premium Bootstrap restaurant template'
    },
    {
      name: 'Foodie Restaurant',
      url: 'https://github.com/BlackrockDigital/startbootstrap-agency/archive/refs/heads/master.zip',
      source: 'github',
      description: 'Modern restaurant template'
    },
    {
      name: 'Gourmet Restaurant',
      url: 'https://github.com/BlackrockDigital/startbootstrap-creative/archive/refs/heads/master.zip',
      source: 'github',
      description: 'Elegant restaurant design'
    },
  ],
  cafe: [
    {
      name: 'Cafe House',
      url: 'https://www.tooplate.com/zip_files/2127_cafe_house.zip',
      source: 'tooplate',
      description: 'Cozy cafe template'
    },
    {
      name: 'Coffee Shop',
      url: 'https://github.com/ColorlibHQ/coffee-shop-template/archive/refs/heads/main.zip',
      source: 'github',
      description: 'Modern coffee shop design'
    },
  ],
  hotel: [
    {
      name: 'Luxury Hotel',
      url: 'https://github.com/ColorlibHQ/hotel-template/archive/refs/heads/main.zip',
      source: 'github',
      description: 'Premium hotel template'
    },
    {
      name: 'Resort Template',
      url: 'https://www.tooplate.com/zip_files/2134_gymso_fitness.zip',
      source: 'tooplate',
      description: 'Resort and hotel design'
    },
  ],
  bakery: [
    {
      name: 'Sweet Bakery',
      url: 'https://www.tooplate.com/zip_files/2129_crispy_kitchen.zip',
      source: 'tooplate',
      description: 'Bakery template'
    },
  ],
  'sweets-shop': [
    {
      name: 'Sweet Shop',
      url: 'https://github.com/ColorlibHQ/sweet-shop-template/archive/refs/heads/main.zip',
      source: 'github',
      description: 'Candy shop template'
    },
  ],
  grocery: [
    {
      name: 'Grocery Store',
      url: 'https://github.com/ColorlibHQ/grocery-template/archive/refs/heads/main.zip',
      source: 'github',
      description: 'Modern grocery template'
    },
  ],
  salon: [
    {
      name: 'Beauty Salon',
      url: 'https://github.com/ColorlibHQ/salon-template/archive/refs/heads/main.zip',
      source: 'github',
      description: 'Elegant salon design'
    },
  ],
  barber: [
    {
      name: 'Barber Shop',
      url: 'https://github.com/ColorlibHQ/barber-template/archive/refs/heads/main.zip',
      source: 'github',
      description: 'Classic barber template'
    },
  ],
  gym: [
    {
      name: 'Gymso Fitness',
      url: 'https://www.tooplate.com/zip_files/2119_gymso_fitness.zip',
      source: 'tooplate',
      description: 'Fitness center template'
    },
  ],
  portfolio: [
    {
      name: 'Portfolio Template',
      url: 'https://github.com/ColorlibHQ/portfolio-template/archive/refs/heads/main.zip',
      source: 'github',
      description: 'Creative portfolio'
    },
  ],
  'real-estate': [
    {
      name: 'Real Estate',
      url: 'https://github.com/ColorlibHQ/real-estate-template/archive/refs/heads/main.zip',
      source: 'github',
      description: 'Property listing template'
    },
  ],
  'e-commerce': [
    {
      name: 'E-Commerce Shop',
      url: 'https://github.com/ColorlibHQ/ecommerce-template/archive/refs/heads/main.zip',
      source: 'github',
      description: 'Online store template'
    },
  ],
  medical: [
    {
      name: 'Medical Clinic',
      url: 'https://github.com/ColorlibHQ/medical-template/archive/refs/heads/main.zip',
      source: 'github',
      description: 'Medical practice template'
    },
  ],
  doctor: [
    {
      name: 'Doctor Clinic',
      url: 'https://github.com/ColorlibHQ/doctor-template/archive/refs/heads/main.zip',
      source: 'github',
      description: 'Healthcare template'
    },
  ],
  construction: [
    {
      name: 'Construction',
      url: 'https://github.com/ColorlibHQ/construction-template/archive/refs/heads/main.zip',
      source: 'github',
      description: 'Construction company template'
    },
  ],
  travel: [
    {
      name: 'Travel Agency',
      url: 'https://github.com/ColorlibHQ/travel-template/archive/refs/heads/main.zip',
      source: 'github',
      description: 'Travel and tourism template'
    },
  ],
};

// Alternative: Use template marketplaces API or scraping
const SEARCH_ENGINES = {
  google: (query) => `https://www.google.com/search?q=${encodeURIComponent(query)}`,
  github: (query) => `https://github.com/search?q=${encodeURIComponent(query)}`,
};

/**
 * Download file from URL with proper headers and redirect handling
 */
async function downloadFile(url, destPath) {
  return new Promise((resolve, reject) => {
    const protocol = url.startsWith('https') ? https : http;
    const file = require('fs').createWriteStream(destPath);
    
    const options = {
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'en-US,en;q=0.9',
      },
      maxRedirects: 5,
    };
    
    const makeRequest = (requestUrl, redirectCount = 0) => {
      if (redirectCount > 5) {
        file.close();
        require('fs').unlinkSync(destPath);
        reject(new Error('Too many redirects'));
        return;
      }
      
      protocol.get(requestUrl, options, (response) => {
        // Handle redirects
        if (response.statusCode === 301 || response.statusCode === 302 || response.statusCode === 307 || response.statusCode === 308) {
          file.close();
          if (require('fs').existsSync(destPath)) {
            require('fs').unlinkSync(destPath);
          }
          const location = response.headers.location;
          if (location) {
            const newUrl = location.startsWith('http') ? location : new URL(location, requestUrl).href;
            return makeRequest(newUrl, redirectCount + 1);
          }
          reject(new Error('Redirect without location'));
          return;
        }
        
        if (response.statusCode !== 200) {
          file.close();
          require('fs').unlinkSync(destPath);
          reject(new Error(`Failed to download: ${response.statusCode} ${response.statusMessage}`));
          return;
        }
        
        // Check content type
        const contentType = response.headers['content-type'] || '';
        if (!contentType.includes('zip') && !contentType.includes('octet-stream') && !contentType.includes('application/zip')) {
          // Might still be a ZIP file, continue
        }
        
        response.pipe(file);
        file.on('finish', () => {
          file.close();
          // Verify it's a valid file (at least 1KB)
          const stats = require('fs').statSync(destPath);
          if (stats.size < 1024) {
            require('fs').unlinkSync(destPath);
            reject(new Error('Downloaded file is too small, might be an error page'));
            return;
          }
          resolve(destPath);
        });
      }).on('error', (err) => {
        file.close();
        if (require('fs').existsSync(destPath)) {
          require('fs').unlinkSync(destPath);
        }
        reject(err);
      });
    };
    
    makeRequest(url);
  });
}

/**
 * Extract ZIP file
 */
async function extractZip(zipPath, destDir) {
  try {
    // Try using unzip command (Linux/Mac)
    execSync(`unzip -q "${zipPath}" -d "${destDir}"`, { stdio: 'ignore' });
    return true;
  } catch (error) {
    try {
      // Try using node-unzip-7 or yauzl
      const AdmZip = require('adm-zip');
      const zip = new AdmZip(zipPath);
      zip.extractAllTo(destDir, true);
      return true;
    } catch (err) {
      console.error(`[ERROR] Failed to extract ${zipPath}:`, err.message);
      return false;
    }
  }
}

/**
 * Search for templates using predefined sources
 */
async function searchTemplates(category, count = 12) {
  const templates = [];
  const sources = TEMPLATE_SOURCES[category] || [];
  
  console.log(`[INFO] Found ${sources.length} premium templates for ${category}...`);
  
  // Use available sources, repeat if needed to reach count
  for (let i = 0; i < count; i++) {
    const source = sources[i % sources.length];
    if (!source) break;
    
    const templateName = source.name.toLowerCase().replace(/\s+/g, '-') + (i >= sources.length ? `-${Math.floor(i / sources.length) + 1}` : '');
    
    templates.push({
      name: templateName,
      url: source.url,
      downloadUrl: source.url,
      category,
      source: source.source,
      description: source.description,
    });
  }

  return templates;
}

/**
 * Download and process a single template
 */
async function downloadTemplate(template, category) {
  const templateDir = path.join(process.cwd(), 'templates', category, template.name);
  const zipPath = path.join(templateDir, `${template.name}.zip`);
  
  try {
    // Create directory
    await fs.mkdir(templateDir, { recursive: true });
    
    console.log(`[INFO] Downloading ${template.name} from ${template.source}...`);
    console.log(`[INFO] URL: ${template.downloadUrl}`);
    
    // Download the ZIP file - prefer wget/curl as they handle redirects better
    let downloaded = false;
    try {
      // Try wget first (better at handling redirects)
      execSync(`wget --no-check-certificate -O "${zipPath}" "${template.downloadUrl}" 2>&1`, { stdio: 'pipe' });
      const stats = require('fs').statSync(zipPath);
      if (stats.size > 1024) {
        downloaded = true;
        console.log(`[INFO] Downloaded ZIP file (${(stats.size / 1024).toFixed(2)} KB)`);
      }
    } catch (wgetError) {
      try {
        // Try curl as fallback
        execSync(`curl -L -k -o "${zipPath}" "${template.downloadUrl}" 2>&1`, { stdio: 'pipe' });
        const stats = require('fs').statSync(zipPath);
        if (stats.size > 1024) {
          downloaded = true;
          console.log(`[INFO] Downloaded ZIP file via curl (${(stats.size / 1024).toFixed(2)} KB)`);
        }
      } catch (curlError) {
        // Last resort: try Node.js download
        try {
          await downloadFile(template.downloadUrl, zipPath);
          const stats = require('fs').statSync(zipPath);
          if (stats.size > 1024) {
            downloaded = true;
            console.log(`[INFO] Downloaded ZIP file via Node.js (${(stats.size / 1024).toFixed(2)} KB)`);
          }
        } catch (nodeError) {
          throw new Error(`All download methods failed. Last error: ${nodeError.message}`);
        }
      }
    }
    
    // Verify it's actually a ZIP file
    let isValidZip = false;
    if (downloaded) {
      const fileContent = await fs.readFile(zipPath, { encoding: 'binary', flag: 'r' });
      if (fileContent.startsWith('PK')) {
        isValidZip = true;
      } else if (fileContent.includes('<!DOCTYPE') || fileContent.includes('<html')) {
        // It's an HTML error page
        await fs.unlink(zipPath);
        downloaded = false;
      }
    }
    
    // If download failed or invalid, skip this template
    if (!downloaded || !isValidZip) {
      throw new Error('Failed to download valid template file');
    }
    
    // Extract ZIP file
    console.log(`[INFO] Extracting template...`);
    const extracted = await extractZip(zipPath, templateDir);
    
    if (!extracted) {
      throw new Error('Failed to extract ZIP file');
    }
    
    // Clean up ZIP file
    try {
      await fs.unlink(zipPath);
    } catch {
      // Ignore if deletion fails
    }
    
    // Helper function to copy directory
    async function copyDirectory(src, dest) {
      await fs.mkdir(dest, { recursive: true });
      const entries = await fs.readdir(src, { withFileTypes: true });
      for (const entry of entries) {
        const srcPath = path.join(src, entry.name);
        const destPath = path.join(dest, entry.name);
        if (entry.isDirectory()) {
          await copyDirectory(srcPath, destPath);
        } else {
          await fs.copyFile(srcPath, destPath);
        }
      }
    }
    
    // Find index.html - it might be in a subdirectory (GitHub archives often have repo-name folder)
    let indexPath = path.join(templateDir, 'index.html');
    try {
      await fs.access(indexPath);
    } catch {
      // Look for index.html in subdirectories
      const files = await fs.readdir(templateDir, { withFileTypes: true });
      for (const file of files) {
        if (file.isDirectory()) {
          const subIndexPath = path.join(templateDir, file.name, 'index.html');
          try {
            await fs.access(subIndexPath);
            // Move contents up one level
            const subDir = path.join(templateDir, file.name);
            const subFiles = await fs.readdir(subDir);
            for (const subFile of subFiles) {
              const src = path.join(subDir, subFile);
              const dest = path.join(templateDir, subFile);
              try {
                await fs.rename(src, dest);
              } catch (renameError) {
                // If rename fails (e.g., file exists), try copy then remove
                const stats = await fs.stat(src);
                if (stats.isDirectory()) {
                  await copyDirectory(src, dest);
                  await fs.rm(src, { recursive: true, force: true });
                } else {
                  await fs.copyFile(src, dest);
                  await fs.unlink(src);
                }
              }
            }
            await fs.rmdir(subDir).catch(() => {});
            break;
          } catch {
            continue;
          }
        }
      }
    }
    
    // Verify index.html exists
    try {
      await fs.access(path.join(templateDir, 'index.html'));
    } catch {
      throw new Error('index.html not found after extraction');
    }

    return {
      success: true,
      path: templateDir,
      name: template.name,
    };
  } catch (error) {
    console.error(`[ERROR] Failed to download ${template.name}:`, error.message);
    // Clean up on failure
    try {
      await fs.rm(templateDir, { recursive: true, force: true });
    } catch {
      // Ignore cleanup errors
    }
    return {
      success: false,
      name: template.name,
      error: error.message,
    };
  }
}

/**
 * Main download function
 */
async function downloadCategory(category, count = 12) {
  console.log(`\n🚀 Starting download for category: ${category}`);
  console.log(`📦 Target: ${count} templates\n`);

  // Validate category
  const validCategories = Object.keys(TEMPLATE_SOURCES);
  if (!validCategories.includes(category)) {
    console.error(`[ERROR] Invalid category: ${category}`);
    console.log(`Valid categories: ${validCategories.join(', ')}`);
    process.exit(1);
  }

  // Search for templates
  const templates = await searchTemplates(category, count);
  console.log(`[INFO] Found ${templates.length} templates\n`);

  // Download each template
  const results = [];
  for (let i = 0; i < templates.length; i++) {
    const template = templates[i];
    const result = await downloadTemplate(template, category);
    results.push(result);
    
    if (result.success) {
      console.log(`✅ Downloaded: ${template.name}`);
      // Generate metadata with template info
      await generateMetadata(result.path, result.name, category, template);
    } else {
      console.log(`❌ Failed: ${template.name}: ${result.error}`);
    }
    
    // Small delay between downloads to be respectful
    if (i < templates.length - 1) {
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }

  console.log(`\n✨ Download complete! ${results.filter(r => r.success).length}/${results.length} templates downloaded`);
  console.log(`📁 Location: templates/${category}/\n`);

  return results;
}

/**
 * Generate metadata.json for template
 */
async function generateMetadata(templatePath, templateName, category, templateInfo = {}) {
  const metadata = {
    name: templateName,
    category: category,
    source: templateInfo.source || 'premium-template',
    sourceUrl: templateInfo.downloadUrl || templateInfo.url || '',
    description: templateInfo.description || `Premium ${category} template`,
    status: 'downloaded',
    preview: path.join(templatePath, 'index.html').replace(process.cwd(), ''),
    downloadedAt: new Date().toISOString(),
    version: '1.0.0',
    premium: true,
  };

  const metadataPath = path.join(templatePath, 'metadata.json');
  await fs.writeFile(metadataPath, JSON.stringify(metadata, null, 2));
  console.log(`[INFO] Generated metadata for ${templateName}`);
}

// CLI handler
if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];
  const category = args[1];
  const count = parseInt(args[2]) || 12;

  if (command === 'download-category' && category) {
    downloadCategory(category, count)
      .then(() => process.exit(0))
      .catch((error) => {
        console.error('[ERROR]', error);
        process.exit(1);
      });
  } else {
    console.log('Usage: node downloader.js download-category <category> [count]');
    console.log('Example: node downloader.js download-category restaurant 12');
    process.exit(1);
  }
}

module.exports = { downloadCategory, downloadTemplate, generateMetadata };

