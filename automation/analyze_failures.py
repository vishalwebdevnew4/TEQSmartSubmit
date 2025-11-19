#!/usr/bin/env python3
"""
Analyze failure logs and suggest improvements.
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

def analyze_log_file(log_file_path):
    """Analyze a failure log file."""
    failures = []
    
    with open(log_file_path, 'r') as f:
        for line in f:
            if line.strip():
                try:
                    failures.append(json.loads(line))
                except:
                    continue
    
    if not failures:
        print("No failures found in log file.")
        return
    
    # Group by error type
    by_type = defaultdict(list)
    for failure in failures:
        by_type[failure.get("error_type", "unknown")].append(failure)
    
    print(f"\n{'='*80}")
    print(f"FAILURE ANALYSIS: {log_file_path.name}")
    print(f"{'='*80}")
    print(f"Total failures: {len(failures)}")
    print(f"\nBreakdown by error type:")
    
    for error_type, error_list in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"\n  {error_type.upper()}: {len(error_list)} failures")
        
        # Show common patterns
        messages = [f.get("error_message", "") for f in error_list]
        common_words = defaultdict(int)
        for msg in messages:
            words = msg.lower().split()
            for word in words:
                if len(word) > 4:  # Only meaningful words
                    common_words[word] += 1
        
        if common_words:
            top_words = sorted(common_words.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"    Common keywords: {', '.join([w[0] for w in top_words])}")
        
        # Show sample URLs
        print(f"    Sample URLs:")
        for failure in error_list[:3]:
            print(f"      - {failure.get('url', 'unknown')}")
            print(f"        {failure.get('error_message', '')[:80]}")
    
    # Suggest improvements
    print(f"\n{'='*80}")
    print("SUGGESTED IMPROVEMENTS:")
    print(f"{'='*80}")
    
    if "captcha_error" in by_type:
        print("\n1. CAPTCHA ERRORS:")
        print("   - Increase CAPTCHA timeout")
        print("   - Improve local CAPTCHA solver")
        print("   - Add retry logic for CAPTCHA solving")
    
    if "form_error" in by_type or "field" in str(by_type).lower():
        print("\n2. FORM/FIELD ERRORS:")
        print("   - Improve form detection logic")
        print("   - Add more field selectors")
        print("   - Increase wait time for dynamic forms")
    
    if "timeout_error" in by_type:
        print("\n3. TIMEOUT ERRORS:")
        print("   - Increase page load timeout")
        print("   - Increase form detection timeout")
        print("   - Add retry logic for slow-loading pages")
    
    if "parse_error" in by_type or "syntax_error" in by_type:
        print("\n4. PARSE/SYNTAX ERRORS:")
        print("   - Fix syntax errors in code")
        print("   - Improve error handling")
        print("   - Add better output parsing")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        log_file = Path(sys.argv[1])
    else:
        # Find most recent log file
        log_files = sorted(Path(__file__).parent.glob("failure_log_*.jsonl"), reverse=True)
        if not log_files:
            print("No failure log files found.")
            sys.exit(1)
        log_file = log_files[0]
    
    if not log_file.exists():
        print(f"Log file not found: {log_file}")
        sys.exit(1)
    
    analyze_log_file(log_file)

