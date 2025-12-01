#!/usr/bin/env node
/**
 * Template Converter
 * Converts HTML templates to Next.js, Laravel, or Vue.js
 */

const fs = require('fs').promises;
const path = require('path');
const { JSDOM } = require('jsdom');

/**
 * Convert template to Next.js
 */
async function convertToNextJS(templatePath, outputPath) {
  console.log(`[INFO] Converting to Next.js...`);

  const html = await fs.readFile(path.join(templatePath, 'index.html'), 'utf-8');
  const dom = new JSDOM(html);
  const document = dom.window.document;

  // Create Next.js structure
  await fs.mkdir(path.join(outputPath, 'app'), { recursive: true });
  await fs.mkdir(path.join(outputPath, 'public'), { recursive: true });
  await fs.mkdir(path.join(outputPath, 'components'), { recursive: true });

  // Convert HTML to React/Next.js
  const headContent = document.querySelector('head')?.innerHTML || '';
  const bodyContent = document.querySelector('body')?.innerHTML || '';

  const pageContent = `'use client';

export default function HomePage() {
  return (
    <>
      <head dangerouslySetInnerHTML={{ __html: \`${headContent.replace(/`/g, '\\`')}\` }} />
      <div dangerouslySetInnerHTML={{ __html: \`${bodyContent.replace(/`/g, '\\`')}\` }} />
    </>
  );
}
`;

  await fs.writeFile(path.join(outputPath, 'app', 'page.tsx'), pageContent);

  // Create package.json
  const packageJson = {
    name: path.basename(outputPath),
    version: '1.0.0',
    scripts: {
      dev: 'next dev',
      build: 'next build',
      start: 'next start',
    },
    dependencies: {
      next: '^14.0.0',
      react: '^18.0.0',
      'react-dom': '^18.0.0',
    },
  };

  await fs.writeFile(
    path.join(outputPath, 'package.json'),
    JSON.stringify(packageJson, null, 2)
  );

  // Copy assets to public
  const assetsPath = path.join(templatePath, 'assets');
  if (await fileExists(assetsPath)) {
    await copyDirectory(assetsPath, path.join(outputPath, 'public', 'assets'));
  }

  console.log(`✅ Next.js conversion complete: ${outputPath}`);
}

/**
 * Convert template to Laravel
 */
async function convertToLaravel(templatePath, outputPath) {
  console.log(`[INFO] Converting to Laravel...`);

  const html = await fs.readFile(path.join(templatePath, 'index.html'), 'utf-8');
  const dom = new JSDOM(html);
  const document = dom.window.document;

  // Create Laravel structure
  await fs.mkdir(path.join(outputPath, 'resources', 'views'), { recursive: true });
  await fs.mkdir(path.join(outputPath, 'public'), { recursive: true });
  await fs.mkdir(path.join(outputPath, 'app', 'Http', 'Controllers'), { recursive: true });

  // Create Blade template
  const bodyContent = document.querySelector('body')?.innerHTML || '';
  const bladeContent = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ $title ?? 'Laravel App' }}</title>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>
<body>
    ${bodyContent}
</body>
</html>
`;

  await fs.writeFile(path.join(outputPath, 'resources', 'views', 'welcome.blade.php'), bladeContent);

  // Copy assets
  const assetsPath = path.join(templatePath, 'assets');
  if (await fileExists(assetsPath)) {
    await copyDirectory(assetsPath, path.join(outputPath, 'public', 'assets'));
  }

  console.log(`✅ Laravel conversion complete: ${outputPath}`);
}

/**
 * Convert template to Vue.js
 */
async function convertToVue(templatePath, outputPath) {
  console.log(`[INFO] Converting to Vue.js...`);

  const html = await fs.readFile(path.join(templatePath, 'index.html'), 'utf-8');
  const dom = new JSDOM(html);
  const document = dom.window.document;

  // Create Vue structure
  await fs.mkdir(path.join(outputPath, 'src', 'components'), { recursive: true });
  await fs.mkdir(path.join(outputPath, 'public'), { recursive: true });

  const bodyContent = document.querySelector('body')?.innerHTML || '';

  const vueContent = `<template>
  <div>
    ${bodyContent}
  </div>
</template>

<script>
export default {
  name: 'HomePage',
};
</script>

<style scoped>
/* Component styles */
</style>
`;

  await fs.writeFile(path.join(outputPath, 'src', 'App.vue'), vueContent);

  // Create package.json
  const packageJson = {
    name: path.basename(outputPath),
    version: '1.0.0',
    scripts: {
      dev: 'vite',
      build: 'vite build',
      preview: 'vite preview',
    },
    dependencies: {
      vue: '^3.0.0',
    },
    devDependencies: {
      '@vitejs/plugin-vue': '^4.0.0',
      vite: '^4.0.0',
    },
  };

  await fs.writeFile(
    path.join(outputPath, 'package.json'),
    JSON.stringify(packageJson, null, 2)
  );

  // Copy assets
  const assetsPath = path.join(templatePath, 'assets');
  if (await fileExists(assetsPath)) {
    await copyDirectory(assetsPath, path.join(outputPath, 'public', 'assets'));
  }

  console.log(`✅ Vue.js conversion complete: ${outputPath}`);
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
  const category = args.find(arg => arg.startsWith('--category='))?.split('=')[1];
  const name = args.find(arg => arg.startsWith('--name='))?.split('=')[1];
  const to = args.find(arg => arg.startsWith('--to='))?.split('=')[1];

  if (!category || !name || !to) {
    console.log('Usage: node converter.js --category=<category> --name=<template-name> --to=<nextjs|laravel|vue>');
    process.exit(1);
  }

  const templatePath = path.join(process.cwd(), 'templates', category, name);
  const outputPath = path.join(process.cwd(), 'converted', category, `${name}-${to}`);

  (async () => {
    try {
      switch (to.toLowerCase()) {
        case 'nextjs':
          await convertToNextJS(templatePath, outputPath);
          break;
        case 'laravel':
          await convertToLaravel(templatePath, outputPath);
          break;
        case 'vue':
          await convertToVue(templatePath, outputPath);
          break;
        default:
          console.error(`[ERROR] Unknown framework: ${to}`);
          process.exit(1);
      }
    } catch (error) {
      console.error('[ERROR]', error);
      process.exit(1);
    }
  })();
}

module.exports = { convertToNextJS, convertToLaravel, convertToVue };

