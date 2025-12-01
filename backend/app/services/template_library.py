#!/usr/bin/env python3
"""
Template Library - Downloads and manages 15+ premium templates from various sources.
"""

import json
import sys
import os
import shutil
import subprocess
import requests
import zipfile
import tempfile
from typing import Dict, Any, Optional, List
from pathlib import Path
import re
from datetime import datetime

# Template sources organized by quality and category
TEMPLATE_SOURCES = {
    # HIGH QUALITY - Premium templates
    "premium-modern": {
        "name": "Premium Modern Business",
        "quality": "high",
        "category": "business",
        "source": "github",
        "repo": "vercel/next.js",
        "path": "examples/with-tailwindcss",
        "description": "Modern business template with Tailwind CSS",
    },
    "premium-startup": {
        "name": "Premium Startup Landing",
        "quality": "high",
        "category": "startup",
        "source": "github",
        "repo": "vercel/next.js",
        "path": "examples/hello-world",
        "description": "Clean startup landing page",
    },
    "premium-saas": {
        "name": "Premium SaaS Template",
        "quality": "high",
        "category": "saas",
        "source": "github",
        "repo": "shadcn/next-template",
        "path": "",
        "description": "Modern SaaS template with shadcn/ui",
    },
    
    # MEDIUM-HIGH QUALITY
    "modern-dark": {
        "name": "Modern Dark Theme",
        "quality": "medium-high",
        "category": "business",
        "source": "github",
        "repo": "tailwindlabs/tailwindui",
        "path": "examples/nextjs",
        "description": "Dark theme business template",
    },
    "ecommerce": {
        "name": "E-commerce Template",
        "quality": "medium-high",
        "category": "ecommerce",
        "source": "github",
        "repo": "vercel/next.js",
        "path": "examples/with-stripe-typescript",
        "description": "E-commerce template with Stripe",
    },
    "portfolio": {
        "name": "Portfolio Template",
        "quality": "medium-high",
        "category": "portfolio",
        "source": "github",
        "repo": "vercel/next.js",
        "path": "examples/blog",
        "description": "Portfolio/blog template",
    },
    
    # MEDIUM QUALITY
    "minimal": {
        "name": "Minimal Template",
        "quality": "medium",
        "category": "business",
        "source": "github",
        "repo": "vercel/next.js",
        "path": "examples/with-typescript",
        "description": "Minimal TypeScript template",
    },
    "restaurant": {
        "name": "Restaurant Template",
        "quality": "medium",
        "category": "restaurant",
        "source": "built-in",
        "description": "Restaurant-specific template",
    },
    "medical": {
        "name": "Medical Template",
        "quality": "medium",
        "category": "medical",
        "source": "built-in",
        "description": "Medical/healthcare template",
    },
    "real-estate": {
        "name": "Real Estate Template",
        "quality": "medium",
        "category": "real-estate",
        "source": "built-in",
        "description": "Real estate listing template",
    },
    
    # MEDIUM-LOW QUALITY
    "simple-business": {
        "name": "Simple Business",
        "quality": "medium-low",
        "category": "business",
        "source": "built-in",
        "description": "Simple business template",
    },
    "landing-page": {
        "name": "Landing Page",
        "quality": "medium-low",
        "category": "marketing",
        "source": "built-in",
        "description": "Simple landing page",
    },
    "corporate": {
        "name": "Corporate Template",
        "quality": "medium-low",
        "category": "corporate",
        "source": "built-in",
        "description": "Corporate website template",
    },
    
    # LOW QUALITY (but functional)
    "basic": {
        "name": "Basic Template",
        "quality": "low",
        "category": "general",
        "source": "built-in",
        "description": "Basic functional template",
    },
    "simple": {
        "name": "Simple Template",
        "quality": "low",
        "category": "general",
        "source": "built-in",
        "description": "Very simple template",
    },
}

# Template storage directory
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"
TEMPLATES_DIR.mkdir(exist_ok=True)


def download_template_from_github(repo: str, path: str = "", template_id: str = "") -> Optional[Path]:
    """
    Download a template from GitHub.
    """
    try:
        template_path = TEMPLATES_DIR / template_id
        if template_path.exists():
            print(f"[TEMPLATE] Template {template_id} already exists, skipping download", file=sys.stderr)
            return template_path
        
        # Use GitHub API to download as zip
        if path:
            api_url = f"https://api.github.com/repos/{repo}/contents/{path}"
        else:
            api_url = f"https://api.github.com/repos/{repo}/contents"
        
        # Alternative: Use git clone (simpler)
        repo_url = f"https://github.com/{repo}.git"
        with tempfile.TemporaryDirectory() as tmpdir:
            clone_path = Path(tmpdir) / "template"
            
            # Clone the repo
            result = subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, str(clone_path)],
                capture_output=True,
                text=True,
                timeout=120,
            )
            
            if result.returncode != 0:
                print(f"[TEMPLATE] Failed to clone {repo_url}: {result.stderr}", file=sys.stderr)
                return None
            
            # If there's a specific path, use that
            if path and (clone_path / path).exists():
                source_path = clone_path / path
            else:
                source_path = clone_path
            
            # Copy to templates directory
            if template_path.exists():
                shutil.rmtree(template_path)
            shutil.copytree(source_path, template_path, ignore=shutil.ignore_patterns('.git', 'node_modules', '.next'))
            
            print(f"[TEMPLATE] ✅ Downloaded {template_id} from GitHub", file=sys.stderr)
            return template_path
            
    except Exception as e:
        print(f"[TEMPLATE] Error downloading from GitHub: {e}", file=sys.stderr)
        return None


def create_builtin_template(template_id: str, business_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Create a built-in template (not downloaded, generated on-the-fly).
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
    
    services_list = categories[:5] if categories else ["Service 1", "Service 2", "Service 3"]
    
    # Get template-specific content based on template_id
    if template_id == "premium-modern":
        return generate_premium_modern_template(name, address, phone, website, description, services_list)
    elif template_id == "restaurant":
        return generate_restaurant_template(name, address, phone, website, description, services_list)
    elif template_id == "medical":
        return generate_medical_template(name, address, phone, website, description, services_list)
    elif template_id == "real-estate":
        return generate_real_estate_template(name, address, phone, website, description, services_list)
    elif template_id == "simple-business":
        return generate_simple_business_template(name, address, phone, website, description, services_list)
    elif template_id == "landing-page":
        return generate_landing_page_template(name, address, phone, website, description, services_list)
    elif template_id == "corporate":
        return generate_corporate_template(name, address, phone, website, description, services_list)
    elif template_id == "basic":
        return generate_basic_template(name, address, phone, website, description, services_list)
    elif template_id == "simple":
        return generate_simple_template(name, address, phone, website, description, services_list)
    else:
        # Default to premium modern
        return generate_premium_modern_template(name, address, phone, website, description, services_list)


def generate_premium_modern_template(name: str, address: str, phone: str, website: str, description: str, services: list) -> Dict[str, str]:
    """Premium modern template with gradients and animations."""
    page_content = f'''import {{ Metadata }} from "next";

export const metadata: Metadata = {{
  title: "{name}",
  description: "{description or f'Welcome to {name}'}",
}};

export default function Home() {{
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-900/80 backdrop-blur-md border-b border-purple-500/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              {name}
            </h1>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#about" className="text-slate-300 hover:text-white transition-colors">About</a>
              <a href="#services" className="text-slate-300 hover:text-white transition-colors">Services</a>
              <a href="#contact" className="text-slate-300 hover:text-white transition-colors">Contact</a>
            </div>
          </div>
        </div>
      </nav>

      <section className="relative overflow-hidden pt-24 pb-32">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-600/20 to-pink-600/20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-6xl sm:text-7xl font-bold text-white mb-6 bg-gradient-to-r from-purple-400 via-pink-400 to-purple-400 bg-clip-text text-transparent">
            Welcome to {name}
          </h1>
          <p className="text-xl text-slate-300 max-w-3xl mx-auto mb-8">
            {description or f'Experience excellence with {name}. We deliver exceptional quality and service.'}
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="#contact" className="px-8 py-4 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold hover:shadow-2xl hover:shadow-purple-500/50 transition-all transform hover:scale-105">
              Get Started
            </a>
            <a href="#about" className="px-8 py-4 rounded-lg border-2 border-purple-500/50 text-white font-semibold hover:border-purple-500 hover:bg-purple-500/10 transition-all">
              Learn More
            </a>
          </div>
        </div>
      </section>

      <section id="services" className="py-24 bg-slate-800/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">Our Services</h2>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {services.map((service, idx) => (
              <div key={idx} className="p-6 bg-slate-800/50 rounded-xl border border-purple-500/20 hover:border-purple-500/50 transition-all hover:shadow-xl hover:shadow-purple-500/20">
                <h3 className="text-xl font-semibold text-white mb-2">{{service}}</h3>
                <p className="text-slate-400">Professional solutions tailored to your needs.</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="contact" className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">Contact Us</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="bg-slate-800/50 p-8 rounded-xl border border-purple-500/20">
              <h3 className="text-xl font-semibold text-white mb-6">Get in Touch</h3>
              <div className="space-y-4">
                {address && <p className="text-white"><strong>Address:</strong> {address}</p>}
                {phone && <p className="text-white"><strong>Phone:</strong> <a href="tel:{phone}" className="text-purple-400">{phone}</a></p>}
                {website && <p className="text-white"><strong>Website:</strong> <a href="{website}" className="text-purple-400">{website}</a></p>}
              </div>
            </div>
            <div className="bg-slate-800/50 p-8 rounded-xl border border-purple-500/20">
              <h3 className="text-xl font-semibold text-white mb-6">Send a Message</h3>
              <form className="space-y-4">
                <input type="text" placeholder="Your Name" className="w-full px-4 py-3 rounded-lg bg-slate-900 border border-slate-700 text-white" />
                <input type="email" placeholder="Your Email" className="w-full px-4 py-3 rounded-lg bg-slate-900 border border-slate-700 text-white" />
                <textarea placeholder="Your Message" rows={4} className="w-full px-4 py-3 rounded-lg bg-slate-900 border border-slate-700 text-white"></textarea>
                <button type="submit" className="w-full px-6 py-3 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 text-white font-semibold">
                  Send Message
                </button>
              </form>
            </div>
          </div>
        </div>
      </section>

      <footer className="bg-slate-900 border-t border-slate-800 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-slate-400">&copy; {datetime.now().year} {name}. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
}}
'''
    
    return {
        "app/page.tsx": page_content,
        "package.json": json.dumps({
            "name": name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "private": True,
            "scripts": {"dev": "next dev", "build": "next build", "start": "next start"},
            "dependencies": {"next": "^15.0.0", "react": "^18.3.0", "react-dom": "^18.3.0"},
            "devDependencies": {"@types/node": "^20", "@types/react": "^18", "@types/react-dom": "^18", "typescript": "^5", "tailwindcss": "^3.4.0", "postcss": "^8", "autoprefixer": "^10"},
        }, indent=2),
        "tailwind.config.js": 'module.exports = { content: ["./app/**/*.{js,ts,jsx,tsx,mdx}"], theme: { extend: {} }, plugins: [] }',
    }


def generate_restaurant_template(name: str, address: str, phone: str, website: str, description: str, services: list) -> Dict[str, str]:
    """Restaurant-specific template with warm colors."""
    page_content = f'''import {{ Metadata }} from "next";

export const metadata: Metadata = {{
  title: "{name} - Restaurant",
  description: "{description or f'Welcome to {name} restaurant'}",
}};

export default function Home() {{
  return (
    <div className="min-h-screen bg-gradient-to-b from-orange-50 to-red-50">
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <h1 className="text-3xl font-bold text-orange-600">{name}</h1>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#menu" className="text-gray-700 hover:text-orange-600">Menu</a>
              <a href="#about" className="text-gray-700 hover:text-orange-600">About</a>
              <a href="#contact" className="text-gray-700 hover:text-orange-600">Contact</a>
            </div>
          </div>
        </div>
      </nav>

      <section className="py-20 text-center bg-gradient-to-r from-orange-400 to-red-500 text-white">
        <h1 className="text-5xl font-bold mb-4">Welcome to {name}</h1>
        <p className="text-xl mb-8">{description or 'Delicious food, great atmosphere'}</p>
        <a href="#contact" className="px-8 py-3 bg-white text-orange-600 rounded-lg font-semibold hover:bg-gray-100">
          Reserve a Table
        </a>
      </section>

      <section id="menu" className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center mb-12">Our Menu</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {services.map((item, idx) => (
              <div key={idx} className="bg-gray-50 p-6 rounded-lg shadow-md">
                <h3 className="text-2xl font-semibold text-orange-600 mb-2">{{item}}</h3>
                <p className="text-gray-600">Delicious {item.lower()} prepared with care.</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="contact" className="py-16 bg-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center mb-12">Contact Us</h2>
          <div className="max-w-2xl mx-auto text-center">
            {address && <p className="text-lg mb-2"><strong>Address:</strong> {address}</p>}
            {phone && <p className="text-lg mb-2"><strong>Phone:</strong> <a href="tel:{phone}" className="text-orange-600">{phone}</a></p>}
            {website && <p className="text-lg"><strong>Website:</strong> <a href="{website}" className="text-orange-600">{website}</a></p>}
          </div>
        </div>
      </section>

      <footer className="bg-gray-800 text-white py-8 text-center">
        <p>&copy; {datetime.now().year} {name}. All rights reserved.</p>
      </footer>
    </div>
  );
}}
'''
    
    return {
        "app/page.tsx": page_content,
        "package.json": json.dumps({
            "name": name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "private": True,
            "scripts": {"dev": "next dev", "build": "next build", "start": "next start"},
            "dependencies": {"next": "^15.0.0", "react": "^18.3.0", "react-dom": "^18.3.0"},
            "devDependencies": {"@types/node": "^20", "@types/react": "^18", "@types/react-dom": "^18", "typescript": "^5", "tailwindcss": "^3.4.0"},
        }, indent=2),
        "tailwind.config.js": 'module.exports = { content: ["./app/**/*.{js,ts,jsx,tsx,mdx}"], theme: { extend: {} }, plugins: [] }',
    }


def generate_medical_template(name: str, address: str, phone: str, website: str, description: str, services: list) -> Dict[str, str]:
    """Medical/healthcare template with clean, professional design."""
    page_content = f'''import {{ Metadata }} from "next";

export const metadata: Metadata = {{
  title: "{name} - Healthcare",
  description: "{description or f'Welcome to {name} healthcare services'}",
}};

export default function Home() {{
  return (
    <div className="min-h-screen bg-white">
      <nav className="bg-blue-600 text-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <h1 className="text-2xl font-bold">{name}</h1>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#services" className="hover:text-blue-200">Services</a>
              <a href="#about" className="hover:text-blue-200">About</a>
              <a href="#contact" className="hover:text-blue-200">Contact</a>
            </div>
          </div>
        </div>
      </nav>

      <section className="py-20 bg-gradient-to-r from-blue-600 to-blue-800 text-white text-center">
        <h1 className="text-5xl font-bold mb-4">Your Health is Our Priority</h1>
        <p className="text-xl mb-8">{description or 'Professional healthcare services'}</p>
        <a href="#contact" className="px-8 py-3 bg-white text-blue-600 rounded-lg font-semibold hover:bg-gray-100">
          Book Appointment
        </a>
      </section>

      <section id="services" className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-center mb-12">Our Services</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {services.map((service, idx) => (
              <div key={idx} className="bg-white p-6 rounded-lg shadow-md">
                <h3 className="text-xl font-semibold text-blue-600 mb-2">{{service}}</h3>
                <p className="text-gray-600">Professional {service.lower()} care.</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="contact" className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl font-bold mb-8">Contact Us</h2>
          <div className="max-w-2xl mx-auto">
            {address && <p className="text-lg mb-2"><strong>Address:</strong> {address}</p>}
            {phone && <p className="text-lg mb-2"><strong>Phone:</strong> <a href="tel:{phone}" className="text-blue-600">{phone}</a></p>}
            {website && <p className="text-lg"><strong>Website:</strong> <a href="{website}" className="text-blue-600">{website}</a></p>}
          </div>
        </div>
      </section>

      <footer className="bg-gray-800 text-white py-8 text-center">
        <p>&copy; {datetime.now().year} {name}. All rights reserved.</p>
      </footer>
    </div>
  );
}}
'''
    
    return {
        "app/page.tsx": page_content,
        "package.json": json.dumps({
            "name": name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "private": True,
            "scripts": {"dev": "next dev", "build": "next build", "start": "next start"},
            "dependencies": {"next": "^15.0.0", "react": "^18.3.0", "react-dom": "^18.3.0"},
            "devDependencies": {"@types/node": "^20", "@types/react": "^18", "@types/react-dom": "^18", "typescript": "^5", "tailwindcss": "^3.4.0"},
        }, indent=2),
        "tailwind.config.js": 'module.exports = { content: ["./app/**/*.{js,ts,jsx,tsx,mdx}"], theme: { extend: {} }, plugins: [] }',
    }


def generate_real_estate_template(name: str, address: str, phone: str, website: str, description: str, services: list) -> Dict[str, str]:
    """Real estate template."""
    return generate_simple_business_template(name, address, phone, website, description, services)


def generate_simple_business_template(name: str, address: str, phone: str, website: str, description: str, services: list) -> Dict[str, str]:
    """Simple business template."""
    page_content = f'''import {{ Metadata }} from "next";

export const metadata: Metadata = {{
  title: "{name}",
  description: "{description or f'Welcome to {name}'}",
}};

export default function Home() {{
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold">{name}</h1>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold mb-4">Welcome to {name}</h1>
        <p className="text-lg mb-8">{description or 'Your trusted business partner'}</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {services.map((service, idx) => (
            <div key={idx} className="bg-white p-6 rounded shadow">
              <h3 className="text-xl font-semibold mb-2">{{service}}</h3>
              <p className="text-gray-600">Professional service</p>
            </div>
          ))}
        </div>
        <div className="mt-12">
          <h2 className="text-2xl font-bold mb-4">Contact</h2>
          {address && <p><strong>Address:</strong> {address}</p>}
          {phone && <p><strong>Phone:</strong> <a href="tel:{phone}">{phone}</a></p>}
          {website && <p><strong>Website:</strong> <a href="{website}">{website}</a></p>}
        </div>
      </main>
      <footer className="bg-gray-800 text-white py-6 text-center">
        <p>&copy; {datetime.now().year} {name}</p>
      </footer>
    </div>
  );
}}
'''
    
    return {
        "app/page.tsx": page_content,
        "package.json": json.dumps({
            "name": name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "private": True,
            "scripts": {"dev": "next dev", "build": "next build", "start": "next start"},
            "dependencies": {"next": "^15.0.0", "react": "^18.3.0", "react-dom": "^18.3.0"},
            "devDependencies": {"@types/node": "^20", "@types/react": "^18", "@types/react-dom": "^18", "typescript": "^5", "tailwindcss": "^3.4.0"},
        }, indent=2),
        "tailwind.config.js": 'module.exports = { content: ["./app/**/*.{js,ts,jsx,tsx,mdx}"], theme: { extend: {} }, plugins: [] }',
    }


def generate_landing_page_template(name: str, address: str, phone: str, website: str, description: str, services: list) -> Dict[str, str]:
    """Simple landing page template."""
    return generate_simple_business_template(name, address, phone, website, description, services)


def generate_corporate_template(name: str, address: str, phone: str, website: str, description: str, services: list) -> Dict[str, str]:
    """Corporate template."""
    return generate_simple_business_template(name, address, phone, website, description, services)


def generate_basic_template(name: str, address: str, phone: str, website: str, description: str, services: list) -> Dict[str, str]:
    """Basic template - minimal design."""
    page_content = f'''export default function Home() {{
  return (
    <div>
      <h1>{name}</h1>
      <p>{description or 'Welcome'}</p>
      {address && <p>Address: {address}</p>}
      {phone && <p>Phone: {phone}</p>}
      {website && <p>Website: {website}</p>}
    </div>
  );
}}
'''
    
    return {
        "app/page.tsx": page_content,
        "package.json": json.dumps({
            "name": name.lower().replace(" ", "-"),
            "version": "1.0.0",
            "private": True,
            "scripts": {"dev": "next dev", "build": "next build", "start": "next start"},
            "dependencies": {"next": "^15.0.0", "react": "^18.3.0", "react-dom": "^18.3.0"},
        }, indent=2),
    }


def generate_simple_template(name: str, address: str, phone: str, website: str, description: str, services: list) -> Dict[str, str]:
    """Very simple template."""
    return generate_basic_template(name, address, phone, website, description, services)


def get_template(template_id: str, business_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Get a template by ID, with business data injected.
    """
    if template_id not in TEMPLATE_SOURCES:
        template_id = "premium-modern"  # Default
    
    template_info = TEMPLATE_SOURCES[template_id]
    
    # If it's a built-in template, generate it
    if template_info["source"] == "built-in":
        return create_builtin_template(template_id, business_data)
    
    # If it's from GitHub, try to download/use it
    if template_info["source"] == "github":
        template_path = download_template_from_github(
            template_info["repo"],
            template_info.get("path", ""),
            template_id
        )
        
        if template_path and template_path.exists():
            # Read and inject data
            return inject_data_into_template(template_path, business_data)
        else:
            # Fallback to built-in
            print(f"[TEMPLATE] GitHub download failed, using built-in for {template_id}", file=sys.stderr)
            return create_builtin_template("premium-modern", business_data)
    
    # Default fallback
    return create_builtin_template("premium-modern", business_data)


def inject_data_into_template(template_path: Path, business_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Inject business data into a downloaded template.
    """
    template_files = {}
    
    name = business_data.get("name", "Business")
    address = business_data.get("address", "")
    phone = business_data.get("phone", "")
    website = business_data.get("website", "")
    description = business_data.get("description", "")
    
    # Find and process all relevant files
    for file_path in template_path.rglob("*.tsx"):
        if "node_modules" in str(file_path) or ".next" in str(file_path):
            continue
        
        try:
            content = file_path.read_text(encoding="utf-8")
            
            # Replace common placeholders
            replacements = {
                r'\{\{BUSINESS_NAME\}\}': name,
                r'\{\{businessName\}\}': name,
                r'Your Company': name,
                r'Company Name': name,
                r'\{\{BUSINESS_ADDRESS\}\}': address or "123 Main Street",
                r'\{\{BUSINESS_PHONE\}\}': phone or "+1 (555) 123-4567",
                r'\{\{BUSINESS_WEBSITE\}\}': website or f"https://{name.lower().replace(' ', '')}.com",
                r'\{\{BUSINESS_DESCRIPTION\}\}': description or f"Welcome to {name}",
            }
            
            for pattern, replacement in replacements.items():
                content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
            
            rel_path = file_path.relative_to(template_path)
            template_files[str(rel_path)] = content
        except Exception as e:
            print(f"[TEMPLATE] Error processing {file_path}: {e}", file=sys.stderr)
    
    return template_files


def list_available_templates() -> List[Dict[str, Any]]:
    """
    List all available templates with their metadata.
    """
    return [
        {
            "id": template_id,
            **template_info
        }
        for template_id, template_info in TEMPLATE_SOURCES.items()
    ]


