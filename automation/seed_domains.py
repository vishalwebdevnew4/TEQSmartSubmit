#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Seed all test sites to the domains database via the Next.js API.
"""

import json
import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import requests

# All test URLs
TEST_SITES = [
    "https://thefabcode.com/contact-us/",
    "https://www.seodiscovery.com/contact-us.php",
    "https://blacklisted.agency/contact/",
    "https://www.imarkinfotech.com/contact/",
    "https://www.softtrix.com/contact",
    "https://www.offsure.com/#/contact",
    "https://www.younedia.com/contact-us",
    "https://netpeak.in/contact-us/",
    "https://adroitors.com/contact-us/",
    "https://www.smart-minds.co.in/contact.php",
    "https://360digiexpertz.com/contact-us/",
    "https://www.onlinechandigarh.com/contact-us.html",
    "https://marketing-digital.in/contact/",
    "https://www.sagetitans.com/contact-us.html",
    "https://www.seoily.com/contact-us",
    "https://thehebrewscholar.com/index.php/contact",
    "https://petpointmedia.com/contact-us/",
    "https://teqtopaustralia.xcelanceweb.com/contact",
    "https://interiordesign.xcelanceweb.com/"
]

API_BASE_URL = "http://localhost:3000/api/domains/upload"


def seed_domains(urls=None, category=None, is_active=True):
    """Seed domains to the database via the Next.js API."""
    if urls is None:
        urls = TEST_SITES
    
    print("="*80)
    print("Seeding Domains to Database")
    print("="*80)
    print(f"API Endpoint: {API_BASE_URL}")
    print(f"Total URLs: {len(urls)}")
    print(f"Category: {category or '(none)'}")
    print(f"Active: {is_active}")
    print("="*80)
    print("\nURLs to seed:")
    for i, url in enumerate(urls, 1):
        print(f"  {i:2d}. {url}")
    print("="*80)
    print("\n🚀 Sending request...\n")
    
    try:
        payload = {
            "urls": urls,
            "isActive": is_active
        }
        
        if category:
            payload["category"] = category
        
        response = requests.post(
            API_BASE_URL,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS!")
            print(f"\nResult:")
            print(f"  Message: {result.get('message', 'N/A')}")
            print(f"  Created: {result.get('created', 0)}")
            print(f"  Skipped: {result.get('skipped', 0)}")
            
            if result.get('errors'):
                print(f"\n⚠️  Errors/Warnings ({len(result['errors'])}):")
                for error in result['errors'][:10]:  # Show first 10 errors
                    print(f"    - {error}")
                if len(result['errors']) > 10:
                    print(f"    ... and {len(result['errors']) - 10} more")
            
            print("\n" + "="*80)
            print("✅ Seeding completed successfully!")
            print("="*80)
            return True
        else:
            error_detail = response.json().get('detail', 'Unknown error')
            print(f"❌ FAILED!")
            print(f"  Status Code: {response.status_code}")
            print(f"  Error: {error_detail}")
            print("\n" + "="*80)
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR!")
        print("  Could not connect to https://teqsmartsubmit.xcelanceweb.com/")
        print("  Make sure the Next.js server is running:")
        print("    cd /var/www/html/TEQSmartSubmit")
        print("    npm run dev")
        print("\n" + "="*80)
        return False
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT!")
        print("  Request took too long (>30 seconds)")
        print("\n" + "="*80)
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n" + "="*80)
        return False


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed domains to the database")
    parser.add_argument(
        "--urls",
        nargs="+",
        help="Specific URLs to seed (default: all test sites)"
    )
    parser.add_argument(
        "--category",
        type=str,
        help="Category to assign to all domains"
    )
    parser.add_argument(
        "--inactive",
        action="store_true",
        help="Add domains as inactive (default: active)"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Read URLs from a file (one per line)"
    )
    
    args = parser.parse_args()
    
    urls = args.urls or TEST_SITES
    
    # If file is provided, read URLs from it
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return 1
        
        urls = []
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    urls.append(line)
        
        if not urls:
            print(f"❌ No valid URLs found in file: {file_path}")
            return 1
    
    success = seed_domains(
        urls=urls,
        category=args.category,
        is_active=not args.inactive
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

