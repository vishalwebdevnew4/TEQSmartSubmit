#!/usr/bin/env python3
"""
Seed templates to the database via the Next.js API.
"""

import json
import sys
from pathlib import Path

import requests

API_BASE_URL = "https://teqsmartsubmit.xcelanceweb.com/api/templates"

# Universal template that works with auto-detection for all domains
UNIVERSAL_TEMPLATE = {
    "name": "Universal Auto-Detect Template",
    "description": "Automatically detects and fills form fields on any website. Works with all domains.",
    "fieldMappings": {
        "fields": [],
        "submit_selector": "button[type='submit'], input[type='submit'], button:has-text('Submit'), button:has-text('Send'), button:has-text('Send message')",
        "post_submit_wait_ms": 30000,
        "captcha_timeout_ms": 600000,
        "captcha": True,
        "use_auto_detect": True,
        "use_local_captcha_solver": True,
        "use_hybrid_captcha_solver": False,
        "captcha_service": "local",
        "headless": True,
        "wait_until": "load",
        "test_data": {
            "name": "TEQ QA User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "message": "This is an automated test submission from TEQSmartSubmit.",
            "subject": "Test Inquiry",
            "company": "Test Company"
        }
    },
    "domainId": None  # Universal template (no specific domain)
}

# Template for Interior Design site (if you want domain-specific)
INTERIOR_DESIGN_TEMPLATE = {
    "name": "Interior Design Contact Form",
    "description": "Template for interior design contact forms",
    "fieldMappings": {
        "fields": [
            {"selector": "input[name='name'], input#name, input[name='fullname']", "name": "name"},
            {"selector": "input[name='email'], input#email, input[type='email']", "name": "email"},
            {"selector": "input[name='phone'], input#phone, input[type='tel']", "name": "phone"},
            {"selector": "textarea[name='message'], textarea#message, textarea[name='comment']", "name": "message"}
        ],
        "submit_selector": "button[type='submit'], input[type='submit'], button:has-text('Send'), button:has-text('Submit')",
        "post_submit_wait_ms": 30000,
        "captcha_timeout_ms": 600000,
        "captcha": True,
        "use_auto_detect": True,  # Still enable auto-detect as fallback
        "use_local_captcha_solver": True,
        "use_hybrid_captcha_solver": False,
        "captcha_service": "local",
        "headless": True,
        "wait_until": "load",
        "test_data": {
            "name": "TEQ QA User",
            "email": "test@example.com",
            "phone": "+1234567890",
            "message": "This is an automated test submission from TEQSmartSubmit.",
            "subject": "Test Inquiry",
            "company": "Test Company"
        }
    },
    "domainId": None  # Can be set to specific domain ID if needed
}


def get_domains():
    """Fetch all domains to optionally link templates."""
    try:
        response = requests.get("http://localhost:3000/api/domains", timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []


def find_domain_by_url(domains, url):
    """Find domain ID by URL."""
    for domain in domains:
        if domain.get("url") == url:
            return domain.get("id")
    return None


def create_template(template_data):
    """Create a template via the API."""
    print(f"  Creating template: {template_data['name']}...")
    
    try:
        response = requests.post(
            API_BASE_URL,
            json=template_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"    ✅ Created successfully (ID: {result.get('id')})")
            return True, result
        elif response.status_code == 409:
            print(f"    ⚠️  Template already exists (skipping)")
            return False, None
        else:
            error_detail = response.json().get('detail', 'Unknown error')
            print(f"    ❌ Failed: {error_detail}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print(f"    ❌ Connection error: Could not connect to http://localhost:3000")
        return False, None
    except Exception as e:
        print(f"    ❌ Error: {str(e)}")
        return False, None


def seed_templates(templates=None):
    """Seed templates to the database."""
    if templates is None:
        templates = [UNIVERSAL_TEMPLATE]
    
    print("="*80)
    print("Seeding Templates to Database")
    print("="*80)
    print(f"API Endpoint: {API_BASE_URL}")
    print(f"Total Templates: {len(templates)}")
    print("="*80)
    
    # Optionally fetch domains to link templates
    print("\n📋 Fetching domains...")
    domains = get_domains()
    if domains:
        print(f"   ✅ Found {len(domains)} domain(s)")
    else:
        print("   ⚠️  No domains found (templates will be universal)")
    
    print("\n🚀 Creating templates...\n")
    
    results = {
        "created": 0,
        "skipped": 0,
        "failed": 0
    }
    
    for template in templates:
        # If template has a domain URL, try to find and link it
        if "domainUrl" in template and template["domainUrl"]:
            domain_id = find_domain_by_url(domains, template["domainUrl"])
            if domain_id:
                template["domainId"] = domain_id
                print(f"  Linking to domain: {template['domainUrl']} (ID: {domain_id})")
            else:
                print(f"  ⚠️  Domain not found: {template['domainUrl']} (will be universal)")
                template["domainId"] = None
        
        success, result = create_template(template)
        if success:
            results["created"] += 1
        elif result is None:
            results["skipped"] += 1
        else:
            results["failed"] += 1
        
        print()  # Blank line between templates
    
    # Summary
    print("="*80)
    print("Summary:")
    print(f"  ✅ Created: {results['created']}")
    print(f"  ⚠️  Skipped (already exists): {results['skipped']}")
    print(f"  ❌ Failed: {results['failed']}")
    print("="*80)
    
    if results["created"] > 0 or results["skipped"] > 0:
        print("\n✅ Seeding completed!")
        print("   View templates at: http://localhost:3000/templates")
    else:
        print("\n❌ No templates were created.")
    
    print("="*80)
    
    return results["failed"] == 0


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed templates to the database")
    parser.add_argument(
        "--universal-only",
        action="store_true",
        help="Only create the universal template (default)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Create all templates (universal + domain-specific)"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Load templates from a JSON file"
    )
    
    args = parser.parse_args()
    
    templates_to_create = []
    
    if args.file:
        # Load from file
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return 1
        
        with open(file_path, 'r') as f:
            templates_data = json.load(f)
            if isinstance(templates_data, list):
                templates_to_create = templates_data
            elif isinstance(templates_data, dict):
                templates_to_create = [templates_data]
            else:
                print(f"❌ Invalid JSON format in file: {file_path}")
                return 1
    elif args.all:
        # Create all templates
        templates_to_create = [UNIVERSAL_TEMPLATE, INTERIOR_DESIGN_TEMPLATE]
    else:
        # Default: only universal template
        templates_to_create = [UNIVERSAL_TEMPLATE]
    
    success = seed_templates(templates_to_create)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

