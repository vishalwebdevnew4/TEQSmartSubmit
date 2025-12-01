#!/usr/bin/env node
/**
 * Template Processor
 * Normalizes, fixes, and prepares templates for integration
 */

const fs = require('fs').promises;
const path = require('path');
const { JSDOM } = require('jsdom');

/**
 * Process a template directory
 */
async function processTemplate(templatePath) {
  console.log(`[INFO] Processing template: ${templatePath}`);

  const indexHtmlPath = path.join(templatePath, 'index.html');
  
  try {
    // Read HTML
    const html = await fs.readFile(indexHtmlPath, 'utf-8');
    const dom = new JSDOM(html);
    const document = dom.window.document;

    // 1. Extract inline CSS to external stylesheet
    await extractInlineCSS(document, templatePath);

    // 2. Fix broken asset paths
    await fixAssetPaths(document, templatePath);

    // 3. Remove external tracking scripts
    removeTrackingScripts(document);

    // 4. Validate folder structure
    await validateStructure(templatePath);

    // 5. Save processed HTML
    await fs.writeFile(indexHtmlPath, dom.serialize());

    console.log(`✅ Template processed successfully`);
    return true;
  } catch (error) {
    console.error(`[ERROR] Failed to process template:`, error.message);
    return false;
  }
}

/**
 * Extract inline CSS to external stylesheet
 */
async function extractInlineCSS(document, templatePath) {
  const styleElements = document.querySelectorAll('style');
  const cssDir = path.join(templatePath, 'assets', 'css');
  await fs.mkdir(cssDir, { recursive: true });

  let extractedCSS = '';

  styleElements.forEach((style, index) => {
    const css = style.textContent;
    extractedCSS += `\n/* Extracted from inline style ${index + 1} */\n${css}\n`;
    style.remove();
  });

  if (extractedCSS) {
    const cssFile = path.join(cssDir, 'extracted.css');
    await fs.appendFile(cssFile, extractedCSS);
    
    // Add link to extracted CSS
    const head = document.querySelector('head');
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'assets/css/extracted.css';
    head.appendChild(link);
  }
}

/**
 * Fix broken asset paths
 */
async function fixAssetPaths(document, templatePath) {
  // Fix image paths
  const images = document.querySelectorAll('img');
  images.forEach((img) => {
    const src = img.getAttribute('src');
    if (src && !src.startsWith('http') && !src.startsWith('/')) {
      // Make relative paths work
      if (!src.startsWith('./') && !src.startsWith('../')) {
        img.setAttribute('src', `./${src}`);
      }
    }
  });

  // Fix CSS paths
  const stylesheets = document.querySelectorAll('link[rel="stylesheet"]');
  stylesheets.forEach((link) => {
    const href = link.getAttribute('href');
    if (href && !href.startsWith('http') && !href.startsWith('/')) {
      if (!href.startsWith('./') && !href.startsWith('../')) {
        link.setAttribute('href', `./${href}`);
      }
    }
  });

  // Fix JS paths
  const scripts = document.querySelectorAll('script[src]');
  scripts.forEach((script) => {
    const src = script.getAttribute('src');
    if (src && !src.startsWith('http') && !src.startsWith('/')) {
      if (!src.startsWith('./') && !src.startsWith('../')) {
        script.setAttribute('src', `./${src}`);
      }
    }
  });
}

/**
 * Remove external tracking scripts
 */
function removeTrackingScripts(document) {
  const scripts = document.querySelectorAll('script');
  scripts.forEach((script) => {
    const src = script.getAttribute('src');
    if (src) {
      // Remove common tracking scripts
      const trackingDomains = [
        'google-analytics.com',
        'googletagmanager.com',
        'facebook.net',
        'doubleclick.net',
        'adsbygoogle',
        'hotjar.com',
        'mixpanel.com',
      ];

      if (trackingDomains.some(domain => src.includes(domain))) {
        script.remove();
      }
    }

    // Remove inline tracking code
    const content = script.textContent || '';
    if (content.includes('gtag') || content.includes('ga(') || content.includes('fbq')) {
      script.remove();
    }
  });
}

/**
 * Validate folder structure
 */
async function validateStructure(templatePath) {
  const requiredDirs = [
    'assets',
    'assets/css',
    'assets/js',
    'assets/images',
  ];

  for (const dir of requiredDirs) {
    const dirPath = path.join(templatePath, dir);
    try {
      await fs.mkdir(dirPath, { recursive: true });
    } catch (error) {
      console.warn(`[WARN] Could not create ${dir}:`, error.message);
    }
  }

  // Check for index.html
  const indexPath = path.join(templatePath, 'index.html');
  try {
    await fs.access(indexPath);
  } catch {
    throw new Error('index.html not found');
  }
}

module.exports = { processTemplate, extractInlineCSS, fixAssetPaths, removeTrackingScripts };

