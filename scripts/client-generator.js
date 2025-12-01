#!/usr/bin/env node
/**
 * Client Site Generator
 * Creates dynamic websites from templates with business data
 */

const fs = require('fs').promises;
const path = require('path');
const { JSDOM } = require('jsdom');
const { execSync } = require('child_process');

/**
 * Generate client site from template
 */
async function generateClientSite(clientName, category, templateName, businessData = {}) {
  console.log(`\n🚀 Generating client site for: ${clientName}`);
  console.log(`📦 Template: ${templateName} (${category})\n`);

  const templatePath = path.join(process.cwd(), 'templates', category, templateName);
  const clientPath = path.join(process.cwd(), 'client-sites', clientName.toLowerCase().replace(/\s+/g, '-'));

  try {
    // Check if template exists
    const templateExists = await fileExists(path.join(templatePath, 'index.html'));
    if (!templateExists) {
      throw new Error(`Template not found: ${templatePath}`);
    }

    // Create client directory
    await fs.mkdir(clientPath, { recursive: true });

    // Read template HTML
    const html = await fs.readFile(path.join(templatePath, 'index.html'), 'utf-8');
    const dom = new JSDOM(html);
    const document = dom.window.document;

    // Inject business data
    await injectBusinessData(document, businessData, clientName);

    // Save processed HTML
    await fs.writeFile(path.join(clientPath, 'index.html'), dom.serialize());

    // Copy assets
    const assetsPath = path.join(templatePath, 'assets');
    if (await fileExists(assetsPath)) {
      await copyDirectory(assetsPath, path.join(clientPath, 'assets'));
    }

    // Create client metadata
    const metadata = {
      clientName,
      category,
      template: templateName,
      businessData,
      generatedAt: new Date().toISOString(),
      previewUrl: `http://localhost:3000/preview/${clientName.toLowerCase().replace(/\s+/g, '-')}`,
    };

    await fs.writeFile(
      path.join(clientPath, 'metadata.json'),
      JSON.stringify(metadata, null, 2)
    );

    console.log(`✅ Client site generated: ${clientPath}`);
    console.log(`🌐 Preview: ${metadata.previewUrl}\n`);

    return {
      success: true,
      path: clientPath,
      previewUrl: metadata.previewUrl,
    };
  } catch (error) {
    console.error(`[ERROR] Failed to generate client site:`, error.message);
    return {
      success: false,
      error: error.message,
    };
  }
}

/**
 * Inject business data into HTML
 */
async function injectBusinessData(document, businessData, clientName) {
  // Replace title
  const title = document.querySelector('title');
  if (title) {
    title.textContent = businessData.name || clientName;
  }

  // Replace h1 tags
  const h1s = document.querySelectorAll('h1');
  h1s.forEach((h1, index) => {
    if (index === 0) {
      h1.textContent = businessData.name || clientName;
    }
  });

  // Replace business info placeholders
  const placeholders = {
    '{{business.name}}': businessData.name || clientName,
    '{{business.phone}}': businessData.phone || '',
    '{{business.email}}': businessData.email || '',
    '{{business.address}}': businessData.address || '',
    '{{business.website}}': businessData.website || '',
    '{{business.description}}': businessData.description || '',
  };

  const body = document.querySelector('body');
  if (body) {
    let html = body.innerHTML;
    Object.entries(placeholders).forEach(([placeholder, value]) => {
      html = html.replace(new RegExp(placeholder, 'g'), value);
    });
    body.innerHTML = html;
  }

  // Add meta tags
  const head = document.querySelector('head');
  if (head && businessData.description) {
    let metaDesc = document.querySelector('meta[name="description"]');
    if (!metaDesc) {
      metaDesc = document.createElement('meta');
      metaDesc.setAttribute('name', 'description');
      head.appendChild(metaDesc);
    }
    metaDesc.setAttribute('content', businessData.description);
  }
}

/**
 * Start local server for preview
 */
async function startPreviewServer(clientPath, port = 3000) {
  console.log(`[INFO] Starting preview server on port ${port}...`);

  // Create simple HTTP server
  const http = require('http');
  const fs = require('fs');
  const path = require('path');

  const server = http.createServer((req, res) => {
    let filePath = path.join(clientPath, req.url === '/' ? 'index.html' : req.url);
    
    fs.readFile(filePath, (err, data) => {
      if (err) {
        res.writeHead(404);
        res.end('Not Found');
        return;
      }

      const ext = path.extname(filePath);
      const contentType = {
        '.html': 'text/html',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
      }[ext] || 'text/plain';

      res.writeHead(200, { 'Content-Type': contentType });
      res.end(data);
    });
  });

  server.listen(port, () => {
    console.log(`✅ Preview server running: http://localhost:${port}`);
  });

  return server;
}

/**
 * Helper functions
 */
async function fileExists(filePath) {
  try {
    await fs.access(filePath);
    return true;
  } catch {
    return false;
  }
}

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

// CLI handler
if (require.main === module) {
  const args = process.argv.slice(2);
  const client = args.find(arg => arg.startsWith('--client='))?.split('=')[1];
  const category = args.find(arg => arg.startsWith('--category='))?.split('=')[1];
  const template = args.find(arg => arg.startsWith('--template='))?.split('=')[1];

  if (!client || !category || !template) {
    console.log('Usage: node client-generator.js --client="Client Name" --category=<category> --template=<template-name>');
    console.log('Example: node client-generator.js --client="Gobind Sweets" --category=restaurant --template=restaurant-template-1');
    process.exit(1);
  }

  // Default business data (can be enhanced with API calls)
  const businessData = {
    name: client,
    phone: '+1-234-567-8900',
    email: `contact@${client.toLowerCase().replace(/\s+/g, '')}.com`,
    address: '123 Main Street, City, State 12345',
    website: `https://${client.toLowerCase().replace(/\s+/g, '')}.com`,
    description: `Welcome to ${client}!`,
  };

  (async () => {
    const result = await generateClientSite(client, category, template, businessData);
    if (result.success) {
      // Optionally start preview server
      console.log(`\n💡 To preview, run: cd ${result.path} && python3 -m http.server 8000`);
    }
    process.exit(result.success ? 0 : 1);
  })();
}

module.exports = { generateClientSite, injectBusinessData, startPreviewServer };

