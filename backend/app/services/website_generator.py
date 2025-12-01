#!/usr/bin/env python3
"""
AI Website Generator - Generates Next.js + Tailwind templates with AI-generated content.
Uses OpenAI or Anthropic for intelligent content generation.
"""

import json
import sys
import os
import argparse
from typing import Dict, Any, Optional
from pathlib import Path

# Load environment variables from .env files
try:
    from dotenv import load_dotenv
    # Load from root .env
    load_dotenv()
    # Load from backend/.env
    backend_env = Path(__file__).parent.parent.parent / ".env"
    if backend_env.exists():
        load_dotenv(backend_env)
    # Also try backend/.env
    backend_env2 = Path(__file__).parent.parent / ".env"
    if backend_env2.exists():
        load_dotenv(backend_env2)
except ImportError:
    pass  # dotenv not available, use system env vars

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# AI imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


def generate_color_palette(business_name: str, categories: list = None) -> Dict[str, str]:
    """Generate a color palette based on business type."""
    # Simple color palette generator (can be enhanced with AI)
    palettes = {
        "restaurant": {"primary": "#ef4444", "secondary": "#f97316", "accent": "#fbbf24"},
        "medical": {"primary": "#3b82f6", "secondary": "#06b6d4", "accent": "#8b5cf6"},
        "retail": {"primary": "#8b5cf6", "secondary": "#ec4899", "accent": "#f43f5e"},
        "default": {"primary": "#6366f1", "secondary": "#8b5cf6", "accent": "#ec4899"},
    }
    
    if categories:
        for cat in categories:
            cat_lower = cat.lower()
            if "restaurant" in cat_lower or "food" in cat_lower:
                return palettes["restaurant"]
            elif "medical" in cat_lower or "health" in cat_lower:
                return palettes["medical"]
            elif "retail" in cat_lower or "shop" in cat_lower:
                return palettes["retail"]
    
    return palettes["default"]


def call_ai_api(prompt: str, style: str = "friendly", max_tokens: int = 500) -> str:
    """
    Call AI API (OpenAI, Anthropic, Google Gemini, or Hugging Face) to generate content.
    Falls back to template-based generation if AI is not available.
    """
    # Get API keys from environment
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    google_api_key = os.getenv("GOOGLE_AI_API_KEY")  # Free tier available
    huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")  # Free tier available
    
    # Try OpenAI first
    if OPENAI_AVAILABLE and openai_api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Use cost-effective model
                messages=[
                    {"role": "system", "content": f"You are a professional web developer and copywriter. Write in a {style} tone."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API error: {e}", file=sys.stderr)
    
    # Try Google Gemini (FREE tier: 60 requests/minute)
    if google_api_key:
        try:
            import google.generativeai as genai
            print(f"[AI] Attempting Google Gemini API...", file=sys.stderr)
            print(f"[AI] API Key present: {google_api_key[:10]}...", file=sys.stderr)
            genai.configure(api_key=google_api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            # Build the full prompt
            full_prompt = f"You are a professional web developer and copywriter. Write in a {style} tone.\n\n{prompt}"
            print(f"[AI] Prompt length: {len(full_prompt)} chars", file=sys.stderr)
            
            response = model.generate_content(
                full_prompt,
                generation_config={
                    "max_output_tokens": min(max_tokens, 8192),  # Gemini limit
                    "temperature": 0.7,
                }
            )
            result = response.text.strip()
            print(f"[AI] ✅ Google Gemini success! ({len(result)} chars)", file=sys.stderr)
            return result
        except ImportError:
            print("[AI] ❌ google-generativeai not installed. Install with: pip install google-generativeai", file=sys.stderr)
        except Exception as e:
            print(f"[AI] ❌ Google Gemini API error: {e}", file=sys.stderr)
            import traceback
            print(f"[AI] Traceback: {traceback.format_exc()}", file=sys.stderr)
    
    # Try Hugging Face Inference API (FREE tier available)
    if huggingface_api_key:
        try:
            import requests
            print(f"[AI] Attempting Hugging Face API...", file=sys.stderr)
            # Use a free model - try smaller/faster models first
            model_name = "mistralai/Mistral-7B-Instruct-v0.2"  # Free model
            api_url = f"https://api-inference.huggingface.co/models/{model_name}"
            headers = {"Authorization": f"Bearer {huggingface_api_key}"}
            
            # Format prompt for Mistral
            formatted_prompt = f"<s>[INST] You are a professional web developer and copywriter. Write in a {style} tone.\n\n{prompt} [/INST]"
            
            payload = {
                "inputs": formatted_prompt,
                "parameters": {
                    "max_new_tokens": min(max_tokens, 2048),  # Increased limit
                    "temperature": 0.7,
                    "return_full_text": False
                }
            }
            
            response = requests.post(api_url, headers=headers, json=payload, timeout=60)
            print(f"[AI] Hugging Face response status: {response.status_code}", file=sys.stderr)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    text = result[0].get("generated_text", "").strip()
                    print(f"[AI] ✅ Hugging Face success! ({len(text)} chars)", file=sys.stderr)
                    return text
                elif isinstance(result, dict) and "generated_text" in result:
                    text = result["generated_text"].strip()
                    print(f"[AI] ✅ Hugging Face success! ({len(text)} chars)", file=sys.stderr)
                    return text
            else:
                print(f"[AI] ❌ Hugging Face error: {response.status_code} - {response.text[:200]}", file=sys.stderr)
        except Exception as e:
            print(f"[AI] ❌ Hugging Face API error: {e}", file=sys.stderr)
            import traceback
            print(f"[AI] Traceback: {traceback.format_exc()}", file=sys.stderr)
    
    # Try Anthropic (paid but has free tier for new users)
    if ANTHROPIC_AVAILABLE and anthropic_api_key:
        try:
            client = anthropic.Anthropic(api_key=anthropic_api_key)
            message = client.messages.create(
                model="claude-3-haiku-20240307",  # Fast and cost-effective
                max_tokens=max_tokens,
                temperature=0.7,
                system=f"You are a professional web developer and copywriter. Write in a {style} tone.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return message.content[0].text.strip()
        except Exception as e:
            print(f"Anthropic API error: {e}", file=sys.stderr)
    
    # Fallback to template-based generation
    return None


def generate_ai_copy(business_data: Dict[str, Any], style: str = "friendly") -> Dict[str, str]:
    """
    Generate AI-powered copy for website sections using OpenAI/Anthropic.
    Falls back to template-based generation if AI is not available.
    """
    name = business_data.get("name", "Business")
    description = business_data.get("description", "")
    categories = business_data.get("categories", [])
    address = business_data.get("address", "")
    phone = business_data.get("phone", "")
    
    # Build context for AI
    context = f"Business: {name}"
    if description:
        context += f"\nDescription: {description}"
    if categories:
        context += f"\nCategories: {', '.join(categories)}"
    if address:
        context += f"\nLocation: {address}"
    
    # Generate hero section with AI
    hero_prompt = f"""Create a compelling hero section for a business website.

{context}

Style: {style}
Tone: {"Professional and business-like" if style == "formal" else "Warm and approachable" if style == "friendly" else "Engaging and persuasive" if style == "marketing" else "Clean and simple"}

Generate:
1. A catchy hero title (max 8 words)
2. A compelling subtitle (max 15 words)

Format as JSON: {{"title": "...", "subtitle": "..."}}"""
    
    hero_result = call_ai_api(hero_prompt, style)
    if hero_result:
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[^}]+\}', hero_result, re.DOTALL)
            if json_match:
                hero_data = json.loads(json_match.group())
                hero_title = hero_data.get("title", f"Welcome to {name}")
                hero_subtitle = hero_data.get("subtitle", description or f"Your trusted partner")
            else:
                # If no JSON, use first two lines
                lines = hero_result.split('\n')[:2]
                hero_title = lines[0].strip() if lines else f"Welcome to {name}"
                hero_subtitle = lines[1].strip() if len(lines) > 1 else description or f"Your trusted partner"
        except:
            hero_title = f"Welcome to {name}"
            hero_subtitle = description or f"Your trusted {categories[0] if categories else 'business'} partner"
    else:
        # Fallback
        hero_title = f"Welcome to {name}"
        hero_subtitle = description or f"Your trusted {categories[0] if categories else 'business'} partner"
    
    # Generate about section with AI
    about_prompt = f"""Write a compelling "About Us" section for a business website.

{context}

Style: {style}
Length: 2-3 sentences
Focus on: What makes this business unique, their values, and commitment to customers"""
    
    about_result = call_ai_api(about_prompt, style)
    about_text = about_result if about_result else f"{name} is committed to providing exceptional service and quality. " + (description or f"We specialize in {', '.join(categories[:3]) if categories else 'excellence'}.")
    
    # Generate services section with AI
    services_prompt = f"""Write an engaging services section introduction for a business website.

{context}

Style: {style}
Length: 1-2 sentences
Focus on: The value and benefits they provide to customers"""
    
    services_result = call_ai_api(services_prompt, style)
    services_text = services_result if services_result else f"At {name}, we offer a comprehensive range of services designed to meet your needs."
    
    # Generate contact section with AI
    contact_prompt = f"""Write a friendly contact section call-to-action for a business website.

{context}

Style: {style}
Length: 1 sentence
Focus on: Encouraging customers to reach out"""
    
    contact_result = call_ai_api(contact_prompt, style)
    contact_text = contact_result if contact_result else f"Get in touch with {name} today. We're here to help!"
    
    # Adjust tone based on style (override AI if needed)
    if style == "formal":
        hero_title = f"{name} - Professional Excellence"
        hero_subtitle = "Delivering exceptional quality and service"
    elif style == "marketing":
        hero_title = f"Transform Your Experience with {name}"
        hero_subtitle = "Discover the difference that sets us apart"
    elif style == "minimalist":
        hero_title = name
        hero_subtitle = description or "Quality. Simplicity. Excellence."
    
    return {
        "heroTitle": hero_title,
        "heroSubtitle": hero_subtitle,
        "aboutText": about_text,
        "servicesText": services_text,
        "contactText": contact_text,
    }


def generate_services_list(business_data: Dict[str, Any], categories: list, style: str = "friendly") -> list:
    """
    Generate a list of services/features using AI based on business categories.
    """
    if not categories or len(categories) == 0:
        return []
    
    name = business_data.get("name", "Business")
    description = business_data.get("description", "")
    
    services_prompt = f"""Generate 3-5 specific services or features for a business website.

Business: {name}
Categories: {', '.join(categories)}
Description: {description or 'N/A'}

Style: {style}

For each service, provide:
- Service name (short, 2-4 words)
- Brief description (1 sentence)

Format as JSON array: [{{"name": "...", "description": "..."}}, ...]"""
    
    services_result = call_ai_api(services_prompt, style)
    if services_result:
        try:
            import re
            json_match = re.search(r'\[[^\]]+\]', services_result, re.DOTALL)
            if json_match:
                services_data = json.loads(json_match.group())
                return services_data[:5]  # Limit to 5 services
        except:
            pass
    
    # Fallback: use categories as services
    return [
        {"name": cat, "description": f"Comprehensive {cat.lower()} solutions tailored to your needs."}
        for cat in categories[:5]
    ]


def generate_full_template_with_gpt(business_data: Dict[str, Any], copy_style: str = "friendly", color_palette: Dict[str, str] = None) -> Dict[str, str]:
    """
    Use GPT to generate complete Next.js website with all standard pages.
    Returns a dictionary of file paths to file contents.
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
    
    if not color_palette:
        color_palette = generate_color_palette(name, categories)
    
    # Build comprehensive prompt for GPT to generate premium design
    prompt = f"""You are an expert web designer. Generate a STUNNING, PREMIUM Next.js home page (app/page.tsx) for a business website.

BUSINESS INFORMATION:
- Name: {name}
- Description: {description or 'N/A'}
- Address: {address or 'N/A'}
- Phone: {phone or 'N/A'}
- Website: {website or 'N/A'}
- Categories: {', '.join(categories) if categories else 'N/A'}

DESIGN REQUIREMENTS:
- Copy Style: {copy_style} ({'Warm and approachable' if copy_style == 'friendly' else 'Professional and business-like' if copy_style == 'formal' else 'Engaging and persuasive' if copy_style == 'marketing' else 'Clean and simple'})
- Primary Color: {color_palette['primary']}
- Secondary Color: {color_palette['secondary']}
- Accent Color: {color_palette['accent']}

CRITICAL DESIGN REQUIREMENTS - MAKE IT PREMIUM:
1. Use Next.js 15 with App Router (app/page.tsx format)
2. Use TypeScript
3. Include Metadata export for SEO
4. Use Tailwind CSS for ALL styling
5. Make it VISUALLY STUNNING with:
   - Beautiful gradients (bg-gradient-to-r, bg-gradient-to-br)
   - Smooth shadows (shadow-xl, shadow-2xl)
   - Glass morphism effects (backdrop-blur-md, bg-white/10)
   - Smooth animations (transition-all, hover:scale-105)
   - Modern card designs with rounded corners
   - Professional typography with proper spacing
6. Include these sections with PREMIUM design:
   - Fixed navigation bar (responsive, glass effect, smooth scroll)
   - Hero section: Large, bold headline with gradient text, compelling CTA buttons with hover effects
   - About section: Beautiful cards with icons, engaging copy
   - Services section: Modern service cards with hover animations, icons, gradients
   - Testimonials section: Elegant testimonial cards with quotes
   - Contact section: Side-by-side layout with beautiful form and contact info cards
   - Professional footer: Multi-column with social icons, links, copyright
7. Use the provided colors creatively - gradients, accents, hover states
8. Make it fully responsive (mobile-first, breakpoints: sm, md, lg, xl)
9. Add smooth scroll behavior and scroll animations
10. Include proper semantic HTML
11. Add hover effects: scale, shadow, color transitions
12. Make it production-ready and professional

IMPORTANT:
- Generate ONLY the complete page.tsx file code
- Do NOT include explanations or markdown code blocks
- Start with: import {{ Metadata }} from "next";
- Use the exact business name, address, phone, website provided
- Generate AI-powered compelling copy for all sections
- Make services specific to the business categories
- Include a working contact form (HTML form, no backend needed)
- Footer should include copyright with current year
- Make it look AMAZING - use modern design trends

Generate the complete PREMIUM code now:"""
    
    # Call GPT to generate the full template (use more tokens for premium design)
    print(f"[GPT] Calling API with {copy_style} style, max_tokens=8000...", file=sys.stderr)
    gpt_response = call_ai_api(prompt, copy_style, max_tokens=8000)
    
    if gpt_response:
        print(f"[GPT] Received response ({len(gpt_response)} chars)", file=sys.stderr)
        # Clean up the response - remove markdown code blocks if present
        code = gpt_response.strip()
        if code.startswith("```"):
            # Remove markdown code blocks
            lines = code.split('\n')
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines[-1].strip() == "```":
                lines = lines[:-1]
            code = '\n'.join(lines)
        
        # Ensure it has the basic structure
        if "export default function" in code and ("Home" in code or "Page" in code):
            print(f"[GPT] ✅ Valid GPT response detected", file=sys.stderr)
            # Return as dictionary with single page
            return {"app/page.tsx": code.strip()}
        else:
            print(f"[GPT] ⚠️ Response missing required structure", file=sys.stderr)
            return None
    
    print(f"[GPT] ❌ No response from API", file=sys.stderr)
    return None


def generate_nextjs_template(business_data: Dict[str, Any], copy_style: str = "friendly") -> Dict[str, Any]:
    """
    Generate a complete Next.js + Tailwind website template.
    Uses GPT to generate the full template code if available.
    
    Returns:
        Dictionary with template files and configuration
    """
    name = business_data.get("name", "Business")
    address = business_data.get("address", "")
    phone = business_data.get("phone", "")
    website = business_data.get("website", "")
    categories = business_data.get("categories", [])
    
    color_palette = generate_color_palette(name, categories)
    
    # Try template library first (15+ templates, low to high quality)
    print(f"[TEMPLATE] Using template library system for {name}...", file=sys.stderr)
    page_content = ""
    gpt_used = False
    gpt_templates = None
    prebuilt_used = False
    
    try:
        # Import template library
        template_library_path = Path(__file__).parent / "template_library.py"
        if template_library_path.exists():
            import importlib.util
            spec = importlib.util.spec_from_file_location("template_library", template_library_path)
            template_library = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(template_library)
            
            # Select template based on business category or use premium-modern as default
            template_id = "premium-modern"  # Default to premium
            categories = business_data.get("categories", [])
            if isinstance(categories, str):
                try:
                    categories = json.loads(categories)
                except:
                    categories = []
            
            # Auto-select template based on category
            if categories:
                cat_lower = str(categories[0]).lower() if categories else ""
                if "restaurant" in cat_lower or "food" in cat_lower:
                    template_id = "restaurant"
                elif "medical" in cat_lower or "health" in cat_lower:
                    template_id = "medical"
                elif "real" in cat_lower and "estate" in cat_lower:
                    template_id = "real-estate"
            
            print(f"[TEMPLATE] Selected template: {template_id}", file=sys.stderr)
            
            # Get template from library
            template_files = template_library.get_template(template_id, business_data)
            
            if template_files and "app/page.tsx" in template_files:
                print(f"[TEMPLATE] ✅ Using template library template: {template_id}", file=sys.stderr)
                page_content = template_files["app/page.tsx"]
                prebuilt_used = True
                gpt_templates = template_files  # Store all template files
            else:
                raise Exception("Template library template missing page.tsx")
        else:
            raise Exception("Template library not found")
    except Exception as e:
        print(f"[TEMPLATE] Template library failed: {e}, trying GPT...", file=sys.stderr)
        # Fallback to GPT generation
        gpt_templates = generate_full_template_with_gpt(business_data, copy_style, color_palette)
    
    # Initialize variables (may be set by pre-built template above)
    if 'page_content' not in locals():
        page_content = ""
    if 'gpt_used' not in locals():
        gpt_used = False
    if 'gpt_templates' not in locals():
        gpt_templates = None
    
    if gpt_templates and len(gpt_templates) > 0:
        print(f"[TEMPLATE] ✅ GPT generated {len(gpt_templates)} files!", file=sys.stderr)
        # Use GPT-generated templates (multiple pages)
        # Store all pages in the template files
        template_files = {}
        for file_path, content in gpt_templates.items():
            template_files[file_path] = content
        
        # Ensure we have a home page
        if "app/page.tsx" not in template_files:
            # Fallback: use first file as home page
            first_file = list(template_files.keys())[0] if template_files else None
            if first_file:
                template_files["app/page.tsx"] = template_files[first_file]
        
        page_content = template_files.get("app/page.tsx", "")
        
        if page_content and len(page_content) >= 100:
            gpt_used = True
            print(f"[TEMPLATE] ✅ Using GPT-generated content ({len(page_content)} chars)", file=sys.stderr)
        else:
            print(f"[TEMPLATE] ⚠️ GPT content too short, using fallback", file=sys.stderr)
            page_content = ""  # Force fallback
    else:
        print(f"[TEMPLATE] ⚠️ GPT generation failed or returned empty, using fallback template", file=sys.stderr)
    
    if not page_content:
        # Fallback to template-based generation
        ai_copy = generate_ai_copy(business_data, copy_style)
        
        # Ensure categories is a list
        if isinstance(categories, str):
            try:
                categories = json.loads(categories)
            except:
                categories = []
        elif not isinstance(categories, list):
            categories = []
        
        # Generate main page component
        # Escape quotes and special characters for f-string
        def escape_js(text):
            if not text:
                return ""
            return str(text).replace('\\', '\\\\').replace('"', '\\"').replace("'", "\\'").replace('\n', '\\n').replace('\r', '')
        
        hero_title_escaped = escape_js(ai_copy['heroTitle'])
        hero_subtitle_escaped = escape_js(ai_copy['heroSubtitle'])
        about_text_escaped = escape_js(ai_copy['aboutText'])
        services_text_escaped = escape_js(ai_copy['servicesText'])
        contact_text_escaped = escape_js(ai_copy['contactText'])
        name_escaped = escape_js(name)
        address_escaped = escape_js(address) if address else ""
        phone_escaped = escape_js(phone) if phone else ""
        website_escaped = escape_js(website) if website else ""
        
        # Use hex colors directly in inline styles for Tailwind compatibility
        primary_color = color_palette['primary']
        secondary_color = color_palette['secondary']
        
        # Generate services list using AI
        services_list = generate_services_list(business_data, categories, copy_style)
        
        # Generate categories JSX with AI-generated services
        categories_jsx = ""
        if services_list and len(services_list) > 0:
            categories_jsx = '\n'.join([
                f'''            <div key={{{idx}}} className="p-6 bg-slate-800/50 rounded-lg border border-slate-700">
              <h3 className="text-xl font-semibold text-white mb-2">{escape_js(service.get("name", "Service"))}</h3>
              <p className="text-slate-400">{escape_js(service.get("description", "Professional service tailored to your needs."))}</p>
            </div>'''
                for idx, service in enumerate(services_list[:3])
            ])
        elif categories and len(categories) > 0:
            # Fallback to categories
            categories_jsx = '\n'.join([
                f'''            <div key={{{idx}}} className="p-6 bg-slate-800/50 rounded-lg border border-slate-700">
              <h3 className="text-xl font-semibold text-white mb-2">{escape_js(cat)}</h3>
              <p className="text-slate-400">Comprehensive {escape_js(cat.lower())} solutions tailored to your needs.</p>
            </div>'''
                for idx, cat in enumerate(categories[:3])
            ])
        else:
            categories_jsx = '<div className="col-span-3 text-center text-slate-400">No services listed</div>'
    
        # Fallback template (if GPT not available)
        page_content = f'''import {{ Metadata }} from "next";
import Link from "next/link";

export const metadata: Metadata = {{
  title: "{name_escaped}",
  description: "{hero_subtitle_escaped}",
}};

export default function Home() {{
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {{/* Navigation */}}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-900/80 backdrop-blur-md border-b border-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-bold text-white">{name_escaped}</h1>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#about" className="text-slate-300 hover:text-white transition-colors">About</a>
              <a href="#services" className="text-slate-300 hover:text-white transition-colors">Services</a>
              <a href="#contact" className="text-slate-300 hover:text-white transition-colors">Contact</a>
              <a href="#contact" className="px-4 py-2 rounded-lg text-white font-medium transition-opacity" style={{{{ backgroundColor: "{primary_color}" }}}}>
                Get Started
              </a>
            </div>
            <button className="md:hidden text-slate-300 hover:text-white">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>
      </nav>
      {{/* Hero Section */}}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 opacity-20" style={{{{ background: `linear-gradient(to right, ${{primary_color}}, ${{secondary_color}})` }}}}></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32">
          <div className="text-center">
            <h1 className="text-5xl sm:text-6xl font-bold text-white mb-6">
              {hero_title_escaped}
            </h1>
            <p className="text-xl text-slate-300 max-w-2xl mx-auto mb-8">
              {hero_subtitle_escaped}
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="#contact"
                className="px-8 py-3 text-white rounded-lg font-semibold hover:opacity-90 transition-opacity"
                style={{{{ backgroundColor: "{primary_color}" }}}}
              >
                Get Started
              </a>
              <a
                href="#about"
                className="px-8 py-3 border-2 border-white/20 text-white rounded-lg font-semibold hover:border-white/40 transition-colors"
              >
                Learn More
              </a>
            </div>
          </div>
        </div>
      </section>

      {{/* About Section */}}
      <section id="about" className="py-24 bg-slate-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">About Us</h2>
            <p className="text-lg text-slate-300 max-w-3xl mx-auto">
              {about_text_escaped}
            </p>
          </div>
        </div>
      </section>

      {{/* Services Section */}}
      <section id="services" className="py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">Our Services</h2>
            <p className="text-lg text-slate-300 max-w-3xl mx-auto">
              {services_text_escaped}
            </p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {categories_jsx}
          </div>
        </div>
      </section>

      {{/* Contact Section */}}
      <section id="contact" className="py-24 bg-slate-800/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-white mb-4">Contact Us</h2>
            <p className="text-lg text-slate-300 max-w-3xl mx-auto mb-8">
              {contact_text_escaped}
            </p>
          </div>
          <div className="max-w-md mx-auto bg-slate-900/60 p-8 rounded-lg border border-slate-700">
            <div className="space-y-4">
              {f'<div><p className="text-sm text-slate-400 mb-1">Address</p><p className="text-white">{address_escaped}</p></div>' if address_escaped else ''}
              {f'<div><p className="text-sm text-slate-400 mb-1">Phone</p><a href="tel:{phone_escaped}" className="hover:underline" style={{{{ color: "{primary_color}" }}}}>{phone_escaped}</a></div>' if phone_escaped else ''}
              {f'<div><p className="text-sm text-slate-400 mb-1">Website</p><a href="{website_escaped}" target="_blank" rel="noopener noreferrer" className="hover:underline" style={{{{ color: "{primary_color}" }}}}>Visit Website</a></div>' if website_escaped else ''}
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}}
'''
    
    # Generate package.json
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
            "react": "^19.0.0",
            "react-dom": "^19.0.0",
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
    
    # Generate tailwind.config.js
    tailwind_config = f'''module.exports = {{
  content: [
    "./src/**/*.{{js,ts,jsx,tsx,mdx}}",
    "./app/**/*.{{js,ts,jsx,tsx,mdx}}",
  ],
  theme: {{
    extend: {{
      colors: {{
        primary: "{color_palette['primary']}",
        secondary: "{color_palette['secondary']}",
        accent: "{color_palette['accent']}",
      }},
    }},
  }},
  plugins: [],
}}
'''
    
    # Build the complete template files dictionary
    template_content = {
        "app/page.tsx": page_content,
        "package.json": json.dumps(package_json, indent=2),
        "tailwind.config.js": tailwind_config,
    }
    
    # Add all GPT-generated pages if available
    if gpt_templates:
        for file_path, content in gpt_templates.items():
            if file_path != "app/page.tsx":  # Already added above
                template_content[file_path] = content
    
    # Determine if GPT was used (check if we actually used GPT content)
    is_gpt_generated = gpt_used
    
    return {
        "content": template_content,
        "colorPalette": color_palette,
        "typography": {
            "fontFamily": "Inter, sans-serif",
            "headingFont": "Inter, sans-serif",
        },
        "aiCopyStyle": copy_style,
        "isGptGenerated": is_gpt_generated,
    }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Generate Next.js website template")
    parser.add_argument("--business-data", required=True, help="JSON string with business data")
    parser.add_argument("--style", choices=["formal", "friendly", "marketing", "minimalist"], default="friendly")
    parser.add_argument("--output", help="Output directory (default: stdout JSON)")
    
    args = parser.parse_args()
    
    try:
        business_data = json.loads(args.business_data)
        template = generate_nextjs_template(business_data, args.style)
        
        if args.output:
            # Write files to directory
            output_path = Path(args.output)
            output_path.mkdir(parents=True, exist_ok=True)
            
            for file_path, content in template["content"].items():
                file_full_path = output_path / file_path
                file_full_path.parent.mkdir(parents=True, exist_ok=True)
                file_full_path.write_text(content, encoding="utf-8")
            
            # Return both success and the template data (including content)
            result = {
                "success": True,
                "output": str(output_path),
                "content": template["content"],
                "colorPalette": template["colorPalette"],
                "typography": template["typography"],
                "aiCopyStyle": template["aiCopyStyle"],
            }
            print(json.dumps(result))
        else:
            print(json.dumps(template, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

