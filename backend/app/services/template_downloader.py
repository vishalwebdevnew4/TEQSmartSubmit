#!/usr/bin/env python3
"""
Template Downloader - Downloads pre-built Next.js templates and makes them dynamic.
"""

import json
import sys
import os
import shutil
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path
import re

# Template sources (GitHub repos with Next.js templates)
TEMPLATE_SOURCES = {
    "modern": {
        "name": "Modern Business Template",
        "repo": "vercel/next.js/examples/with-tailwindcss",
        "description": "Modern, clean design with Tailwind CSS",
    },
    "premium": {
        "name": "Premium Business Template",
        "repo": "tailwindlabs/headlessui/tree/main/examples/nextjs",
        "description": "Premium design with animations",
    },
    "minimal": {
        "name": "Minimal Template",
        "repo": "shadcn/next-template",
        "description": "Clean, minimal design",
    },
    "startup": {
        "name": "Startup Template",
        "repo": "vercel/next.js/examples/hello-world",
        "description": "Simple startup landing page",
    },
}

# Alternative: Use curated template URLs or local templates
CURATED_TEMPLATES = {
    "modern-dark": {
        "name": "Modern Dark Theme",
        "url": "https://github.com/tailwindlabs/tailwindui-nextjs-starter",
        "local_path": "templates/modern-dark",
    },
    "business": {
        "name": "Business Landing Page",
        "url": "https://github.com/vercel/next.js/tree/canary/examples/with-tailwindcss",
        "local_path": "templates/business",
    },
}


def download_template_from_github(repo_path: str, destination: Path) -> bool:
    """
    Download a template from GitHub.
    """
    try:
        # Use git to clone the template
        repo_url = f"https://github.com/{repo_path}.git"
        result = subprocess.run(
            ["git", "clone", "--depth", "1", repo_url, str(destination)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        return result.returncode == 0
    except Exception as e:
        print(f"[TEMPLATE] Failed to download from GitHub: {e}", file=sys.stderr)
        return False


def create_dynamic_template(template_path: Path, business_data: Dict[str, Any], template_style: str = "modern") -> Dict[str, str]:
    """
    Take a pre-built template and make it dynamic by injecting business data.
    """
    template_files = {}
    
    # Find all relevant files
    for file_path in template_path.rglob("*.tsx"):
        if "node_modules" in str(file_path) or ".next" in str(file_path):
            continue
        
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # Replace placeholders with business data
            content = inject_business_data(content, business_data, template_style)
            
            # Get relative path from template root
            rel_path = file_path.relative_to(template_path)
            template_files[str(rel_path)] = content
        except Exception as e:
            print(f"[TEMPLATE] Error processing {file_path}: {e}", file=sys.stderr)
    
    # Also process .ts, .js, .json files
    for ext in ["*.ts", "*.js", "*.json"]:
        for file_path in template_path.rglob(ext):
            if "node_modules" in str(file_path) or ".next" in str(file_path):
                continue
            
            try:
                content = file_path.read_text(encoding="utf-8")
                content = inject_business_data(content, business_data, template_style)
                rel_path = file_path.relative_to(template_path)
                template_files[str(rel_path)] = content
            except:
                pass
    
    return template_files


def inject_business_data(content: str, business_data: Dict[str, Any], style: str) -> str:
    """
    Inject business data into template content by replacing placeholders.
    """
    name = business_data.get("name", "Business")
    address = business_data.get("address", "")
    phone = business_data.get("phone", "")
    website = business_data.get("website", "")
    description = business_data.get("description", "")
    categories = business_data.get("categories", [])
    
    if isinstance(categories, str):
        try:
            categories = json.loads(categories)
        except:
            categories = []
    elif not isinstance(categories, list):
        categories = []
    
    # Common placeholder patterns to replace
    replacements = {
        # Business info
        r'\{\{BUSINESS_NAME\}\}': name,
        r'\{\{businessName\}\}': name,
        r'Business Name': name,
        r'Your Company': name,
        r'Company Name': name,
        
        # Contact info
        r'\{\{BUSINESS_ADDRESS\}\}': address or "123 Main Street",
        r'\{\{businessAddress\}\}': address or "123 Main Street",
        r'\{\{BUSINESS_PHONE\}\}': phone or "+1 (555) 123-4567",
        r'\{\{businessPhone\}\}': phone or "+1 (555) 123-4567",
        r'\{\{BUSINESS_EMAIL\}\}': f"contact@{name.lower().replace(' ', '')}.com",
        r'\{\{businessEmail\}\}': f"contact@{name.lower().replace(' ', '')}.com",
        r'\{\{BUSINESS_WEBSITE\}\}': website or f"https://{name.lower().replace(' ', '')}.com",
        r'\{\{businessWebsite\}\}': website or f"https://{name.lower().replace(' ', '')}.com",
        
        # Description
        r'\{\{BUSINESS_DESCRIPTION\}\}': description or f"Welcome to {name}. We provide exceptional services.",
        r'\{\{businessDescription\}\}': description or f"Welcome to {name}. We provide exceptional services.",
        
        # Services/Categories
        r'\{\{SERVICES\}\}': ', '.join(categories[:5]) if categories else "Our Services",
        r'\{\{services\}\}': ', '.join(categories[:5]) if categories else "Our Services",
    }
    
    # Apply replacements
    for pattern, replacement in replacements.items():
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
    
    return content


def get_prebuilt_template(template_id: str = "modern", business_data: Dict[str, Any] = None) -> Dict[str, str]:
    """
    Get a pre-built template and make it dynamic.
    """
    if business_data is None:
        business_data = {}
    
    # For now, we'll create a template from scratch using a base structure
    # In production, you'd download from GitHub or use local templates
    
    name = business_data.get("name", "Business")
    address = business_data.get("address", "")
    phone = business_data.get("phone", "")
    website = business_data.get("website", "")
    description = business_data.get("description", "")
    categories = business_data.get("categories", [])
    
    if isinstance(categories, str):
        try:
            categories = json.loads(categories)
        except:
            categories = []
    elif not isinstance(categories, list):
        categories = []
    
    # Generate a premium pre-built template structure
    template_files = generate_prebuilt_template_structure(name, address, phone, website, description, categories, template_id)
    
    return template_files


def generate_prebuilt_template_structure(name: str, address: str, phone: str, website: str, description: str, categories: list, style: str) -> Dict[str, str]:
    """
    Generate a pre-built template structure (simulated download + customization).
    """
    # This simulates having downloaded a premium template
    # In production, you'd download actual templates from GitHub
    
    services_list = categories[:5] if categories else ["Service 1", "Service 2", "Service 3"]
    
    page_content = f'''import {{ Metadata }} from "next";
import Link from "next/link";

export const metadata: Metadata = {{
  title: "{name}",
  description: "{description or f'Welcome to {name}'}",
}};

export default function Home() {{
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-900/80 backdrop-blur-md border-b border-purple-500/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                {name}
              </h1>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#about" className="text-slate-300 hover:text-white transition-colors">About</a>
              <a href="#services" className="text-slate-300 hover:text-white transition-colors">Services</a>
              <a href="#contact" className="text-slate-300 hover:text-white transition-colors">Contact</a>
              <a href="#contact" className="px-4 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white font-medium hover:opacity-90 transition-opacity">
                Get Started
              </a>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-24 pb-32">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-pink-600/20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-6xl sm:text-7xl font-bold text-white mb-6 bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent animate-pulse">
            Welcome to {name}
          </h1>
          <p className="text-xl text-slate-300 max-w-3xl mx-auto mb-8">
            {description or f'Experience excellence with {name}. We deliver exceptional quality and service.'}
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="#contact"
              className="px-8 py-4 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold hover:shadow-2xl hover:shadow-purple-500/50 transition-all transform hover:scale-105"
            >
              Get Started
            </a>
            <a
              href="#about"
              className="px-8 py-4 rounded-lg border-2 border-purple-500/50 text-white font-semibold hover:border-purple-500 hover:bg-purple-500/10 transition-all"
            >
              Learn More
            </a>
          </div>
        </div>
      </section>

      {/* Services Section */}
      <section id="services" className="py-24 bg-slate-800/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">Our Services</h2>
            <p className="text-lg text-slate-300">Discover what we offer</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {services_list.map((service, idx) => (
              <div key={idx} className="p-6 bg-slate-800/50 rounded-xl border border-purple-500/20 hover:border-purple-500/50 transition-all hover:shadow-xl hover:shadow-purple-500/20">
                <div className="w-12 h-12 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 mb-4 flex items-center justify-center">
                  <span className="text-2xl">✨</span>
                </div>
                <h3 className="text-xl font-semibold text-white mb-2">{service}</h3>
                <p className="text-slate-400">Professional {service.lower()} solutions tailored to your needs.</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section id="contact" className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">Contact Us</h2>
            <p className="text-lg text-slate-300">Get in touch with us</p>
          </div>
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="bg-slate-800/50 p-8 rounded-xl border border-purple-500/20">
              <h3 className="text-xl font-semibold text-white mb-6">Get in Touch</h3>
              <div className="space-y-4">
                {address && (
                  <div className="flex items-start gap-4">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-sm text-slate-400 mb-1">Address</p>
                      <p className="text-white">{address}</p>
                    </div>
                  </div>
                )}
                {phone && (
                  <div className="flex items-start gap-4">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-sm text-slate-400 mb-1">Phone</p>
                      <a href="tel:{phone}" className="text-purple-400 hover:text-purple-300">{phone}</a>
                    </div>
                  </div>
                )}
                {website && (
                  <div className="flex items-start gap-4">
                    <div className="w-10 h-10 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 flex items-center justify-center">
                      <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-sm text-slate-400 mb-1">Website</p>
                      <a href="{website}" target="_blank" rel="noopener noreferrer" className="text-purple-400 hover:text-purple-300">{website}</a>
                    </div>
                  </div>
                )}
              </div>
            </div>
            <div className="bg-slate-800/50 p-8 rounded-xl border border-purple-500/20">
              <h3 className="text-xl font-semibold text-white mb-6">Send a Message</h3>
              <form className="space-y-4">
                <input type="text" placeholder="Your Name" className="w-full px-4 py-3 rounded-lg bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-purple-500" />
                <input type="email" placeholder="Your Email" className="w-full px-4 py-3 rounded-lg bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-purple-500" />
                <textarea placeholder="Your Message" rows={4} className="w-full px-4 py-3 rounded-lg bg-slate-900 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-purple-500"></textarea>
                <button type="submit" className="w-full px-6 py-3 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold hover:opacity-90 transition-opacity">
                  Send Message
                </button>
              </form>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 border-t border-slate-800 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <h3 className="text-lg font-bold text-white mb-4">{name}</h3>
            <p className="text-slate-400 text-sm mb-4">{description or f'Welcome to {name}'}</p>
            <div className="flex justify-center gap-4">
              <a href="#" className="w-10 h-10 rounded-lg bg-slate-800 hover:bg-purple-600 transition-colors flex items-center justify-center">
                <span className="text-slate-400 hover:text-white">f</span>
              </a>
              <a href="#" className="w-10 h-10 rounded-lg bg-slate-800 hover:bg-purple-600 transition-colors flex items-center justify-center">
                <span className="text-slate-400 hover:text-white">t</span>
              </a>
              <a href="#" className="w-10 h-10 rounded-lg bg-slate-800 hover:bg-purple-600 transition-colors flex items-center justify-center">
                <span className="text-slate-400 hover:text-white">in</span>
              </a>
            </div>
            <p className="text-slate-500 text-sm mt-8">&copy; {new Date().getFullYear()} {name}. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}}
'''
    
    package_json = {
        "name": name.lower().replace(" ", "-"),
        "version": "1.0.0",
        "private": True,
        "scripts": {
            "dev": "next dev",
            "build": "next build",
            "start": "next start",
        },
        "dependencies": {
            "next": "^15.0.0",
            "react": "^18.3.0",
            "react-dom": "^18.3.0",
        },
        "devDependencies": {
            "@types/node": "^20",
            "@types/react": "^18",
            "@types/react-dom": "^18",
            "typescript": "^5",
            "tailwindcss": "^3.4.0",
            "postcss": "^8",
            "autoprefixer": "^10",
        },
    }
    
    tailwind_config = '''module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#9333ea",
        secondary: "#ec4899",
      },
    },
  },
  plugins: [],
}
'''
    
    return {
        "app/page.tsx": page_content,
        "package.json": json.dumps(package_json, indent=2),
        "tailwind.config.js": tailwind_config,
    }


