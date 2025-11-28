#!/usr/bin/env python3
"""
Script to extract domains from visitors CSV and format them according to domains-sample format.
Output: domains-extracted.csv
"""

import csv
import re
from urllib.parse import urlparse

def normalize_url(url):
    """Normalize URL to include protocol if missing."""
    if not url or not isinstance(url, str):
        return None
    
    url = url.strip()
    
    # Skip invalid entries
    if not url or url.lower() in ['api limit exaust', 'api limit exhausted', 'request exception with api']:
        return None
    
    # Remove trailing slashes for consistency
    url = url.rstrip('/')
    
    # If URL doesn't have a protocol, add https://
    if not url.startswith(('http://', 'https://')):
        # Check if it starts with www. or is a domain
        if url.startswith('www.'):
            url = 'https://' + url
        else:
            # Assume it's a domain and add https://
            url = 'https://' + url
    # Convert http:// to https:// for consistency
    elif url.startswith('http://'):
        url = url.replace('http://', 'https://', 1)
    
    # Validate URL format
    try:
        parsed = urlparse(url)
        if not parsed.netloc:
            return None
        return url
    except:
        return None

def extract_domain_from_url(url):
    """Extract base domain from URL for categorization."""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except:
        return None

def main():
    input_file = 'visitors (1)-1764222509856.csv'
    output_file = 'domains-extracted.csv'
    
    domains = []
    seen_urls = set()
    
    print(f"Reading from {input_file}...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # Skip header row
            next(reader, None)
            
            for row_num, row in enumerate(reader, start=2):
                if not row:
                    continue
                
                # Get the searched_domain (first column)
                searched_domain = row[0].strip() if len(row) > 0 else ''
                
                # Normalize the URL
                normalized_url = normalize_url(searched_domain)
                
                if normalized_url and normalized_url not in seen_urls:
                    seen_urls.add(normalized_url)
                    domains.append({
                        'url': normalized_url,
                        'category': 'domains'  # Empty category as per sample format
                    })
    
    except FileNotFoundError:
        print(f"Error: {input_file} not found!")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Sort domains alphabetically
    domains.sort(key=lambda x: x['url'])
    
    print(f"Found {len(domains)} unique domains")
    print(f"Writing to {output_file}...")
    
    # Write to output file
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['url', 'category'])
            
            # Write domains
            for domain in domains:
                writer.writerow([domain['url'], domain['category']])
        
        print(f"✓ Successfully created {output_file} with {len(domains)} domains")
        print(f"\nFirst 5 domains:")
        for i, domain in enumerate(domains[:5], 1):
            print(f"  {i}. {domain['url']}")
        
    except Exception as e:
        print(f"Error writing file: {e}")
        return

if __name__ == '__main__':
    main()

