#!/usr/bin/env node
/**
 * Main CLI Handler
 * Routes commands to appropriate scripts
 */

const { execSync } = require('child_process');
const path = require('path');

const commands = {
  'download-category': (category, count = 12) => {
    const downloader = require('./downloader.js');
    return downloader.downloadCategory(category, count);
  },

  'preview-template': (category, templateName) => {
    const templatePath = path.join(process.cwd(), 'templates', category, templateName);
    const indexPath = path.join(templatePath, 'index.html');
    
    console.log(`\n📄 Template Preview: ${templateName}`);
    console.log(`📁 Path: ${templatePath}`);
    console.log(`🌐 Open: file://${indexPath}\n`);
    
    // Try to open in browser
    try {
      const open = require('open');
      open(indexPath);
    } catch {
      console.log('💡 Open the file manually in your browser');
    }
  },

  'convert-template': async (category, templateName, framework) => {
    const converter = require('./converter.js');
    const templatePath = path.join(process.cwd(), 'templates', category, templateName);
    const outputPath = path.join(process.cwd(), 'converted', category, `${templateName}-${framework}`);

    switch (framework.toLowerCase()) {
      case 'nextjs':
        return converter.convertToNextJS(templatePath, outputPath);
      case 'laravel':
        return converter.convertToLaravel(templatePath, outputPath);
      case 'vue':
        return converter.convertToVue(templatePath, outputPath);
      default:
        throw new Error(`Unknown framework: ${framework}`);
    }
  },

  'create-client-site': async (clientName, category, templateName) => {
    const generator = require('./client-generator.js');
    return generator.generateClientSite(clientName, category, templateName);
  },

  'process-template': async (category, templateName) => {
    const processor = require('./template-processor.js');
    const templatePath = path.join(process.cwd(), 'templates', category, templateName);
    return processor.processTemplate(templatePath);
  },
};

// Parse command line arguments
const args = process.argv.slice(2);
const command = args[0];

if (!command || !commands[command]) {
  console.log(`
📦 Category-Based Template Downloader

Usage:
  node cli.js <command> [options]

Commands:
  download-category <category> [count]
    Download templates for a category
    Example: download-category restaurant 12

  preview-template <category> <template-name>
    Preview a downloaded template
    Example: preview-template restaurant restaurant-template-1

  convert-template --category=<cat> --name=<name> --to=<framework>
    Convert template to Next.js, Laravel, or Vue
    Example: convert-template --category=restaurant --name=restaurant-template-1 --to=nextjs

  create-client-site --client="Name" --category=<cat> --template=<name>
    Generate a client site from a template
    Example: create-client-site --client="Gobind Sweets" --category=restaurant --template=restaurant-template-1

  process-template <category> <template-name>
    Process and normalize a template
    Example: process-template restaurant restaurant-template-1

Categories:
  restaurant, cafe, hotel, bakery, sweets-shop, grocery, salon, barber, gym,
  portfolio, real-estate, e-commerce, medical, doctor, construction, travel
`);
  process.exit(1);
}

// Execute command
(async () => {
  try {
    switch (command) {
      case 'download-category':
        await commands[command](args[1], parseInt(args[2]) || 12);
        break;

      case 'preview-template':
        await commands[command](args[1], args[2]);
        break;

      case 'convert-template':
        const category = args.find(arg => arg.startsWith('--category='))?.split('=')[1];
        const name = args.find(arg => arg.startsWith('--name='))?.split('=')[1];
        const to = args.find(arg => arg.startsWith('--to='))?.split('=')[1];
        await commands[command](category, name, to);
        break;

      case 'create-client-site':
        const client = args.find(arg => arg.startsWith('--client='))?.split('=')[1]?.replace(/"/g, '');
        const cat = args.find(arg => arg.startsWith('--category='))?.split('=')[1];
        const template = args.find(arg => arg.startsWith('--template='))?.split('=')[1];
        await commands[command](client, cat, template);
        break;

      case 'process-template':
        await commands[command](args[1], args[2]);
        break;

      default:
        console.error(`Unknown command: ${command}`);
        process.exit(1);
    }
  } catch (error) {
    console.error('[ERROR]', error.message);
    process.exit(1);
  }
})();

