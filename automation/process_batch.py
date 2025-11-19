#!/usr/bin/env python3
"""
Batch processing script for multiple domains.

This script processes multiple domains in parallel using asyncio.
It's designed to be called from the Next.js API or run standalone.

Usage:
    python3 process_batch.py --domains domain1.com domain2.com --template template.json
    python3 process_batch.py --domains-file domains.txt --template template.json --workers 10
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add automation directory to Python path
_script_dir = Path(__file__).parent.absolute()
if str(_script_dir) not in sys.path:
    sys.path.insert(0, str(_script_dir))

from run_submission import run_submission


async def process_single_domain(
    url: str,
    template_path: Path,
    domain_id: Optional[int] = None,
    template_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Process a single domain and return the result."""
    try:
        result = await run_submission(url, template_path)
        return {
            "url": url,
            "domain_id": domain_id,
            "template_id": template_id,
            "status": result.get("status", "unknown"),
            "message": result.get("message", ""),
            "success": result.get("status") == "success",
        }
    except Exception as e:
        return {
            "url": url,
            "domain_id": domain_id,
            "template_id": template_id,
            "status": "error",
            "message": f"Exception: {str(e)}",
            "success": False,
        }


async def process_batch_parallel(
    domains: List[Dict[str, Any]],
    template_path: Path,
    max_workers: int = 20,
) -> List[Dict[str, Any]]:
    """Process multiple domains in parallel using asyncio semaphore.
    
    Optimized for maximum speed with aggressive parallelism.
    """
    
    # Cap workers at reasonable limit to avoid resource exhaustion
    max_workers = min(max_workers, 50)
    
    # Create semaphore to limit concurrent workers
    semaphore = asyncio.Semaphore(max_workers)
    
    async def process_with_semaphore(domain_info: Dict[str, Any]) -> Dict[str, Any]:
        """Process a domain with semaphore control."""
        async with semaphore:
            return await process_single_domain(
                url=domain_info["url"],
                template_path=template_path,
                domain_id=domain_info.get("domain_id"),
                template_id=domain_info.get("template_id"),
            )
    
    # Create tasks for all domains
    tasks = [process_with_semaphore(domain_info) for domain_info in domains]
    
    # Run all tasks concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Handle exceptions
    processed_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            processed_results.append({
                "url": domains[i]["url"],
                "domain_id": domains[i].get("domain_id"),
                "template_id": domains[i].get("template_id"),
                "status": "error",
                "message": f"Exception: {str(result)}",
                "success": False,
            })
        else:
            processed_results.append(result)
    
    return processed_results


async def process_batch_sequential(
    domains: List[Dict[str, Any]],
    template_path: Path,
) -> List[Dict[str, Any]]:
    """Process multiple domains sequentially (for comparison/testing)."""
    results = []
    for domain_info in domains:
        result = await process_single_domain(
            url=domain_info["url"],
            template_path=template_path,
            domain_id=domain_info.get("domain_id"),
            template_id=domain_info.get("template_id"),
        )
        results.append(result)
    return results


def load_domains_from_file(file_path: Path) -> List[Dict[str, Any]]:
    """Load domains from a text file (one URL per line)."""
    domains = []
    with open(file_path, "r") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if line and not line.startswith("#"):
                domains.append({"url": line})
    return domains


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Process multiple domains in parallel or sequentially"
    )
    parser.add_argument(
        "--domains",
        nargs="+",
        help="List of domain URLs to process",
    )
    parser.add_argument(
        "--domains-file",
        type=Path,
        help="File containing domain URLs (one per line)",
    )
    parser.add_argument(
        "--template",
        type=Path,
        required=True,
        help="Path to template JSON file",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=20,
        help="Number of parallel workers (default: 20, max recommended: 50)",
    )
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Process domains sequentially instead of in parallel",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file for results (JSON)",
    )
    
    args = parser.parse_args()
    
    # Load domains
    domains = []
    if args.domains:
        domains = [{"url": url} for url in args.domains]
    elif args.domains_file:
        if not args.domains_file.exists():
            print(f"Error: Domains file not found: {args.domains_file}", file=sys.stderr)
            return 1
        domains = load_domains_from_file(args.domains_file)
    else:
        print("Error: Must provide either --domains or --domains-file", file=sys.stderr)
        return 1
    
    if not domains:
        print("Error: No domains to process", file=sys.stderr)
        return 1
    
    # Check template file
    if not args.template.exists():
        print(f"Error: Template file not found: {args.template}", file=sys.stderr)
        return 1
    
    print(f"Processing {len(domains)} domain(s)...", file=sys.stderr)
    print(f"Template: {args.template}", file=sys.stderr)
    print(f"Mode: {'Sequential' if args.sequential else f'Parallel ({args.workers} workers)'}", file=sys.stderr)
    print("", file=sys.stderr)
    
    # Process domains
    if args.sequential:
        results = asyncio.run(process_batch_sequential(domains, args.template))
    else:
        results = asyncio.run(process_batch_parallel(domains, args.template, args.workers))
    
    # Print summary
    success_count = sum(1 for r in results if r.get("success"))
    error_count = len(results) - success_count
    
    print("", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print("SUMMARY", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print(f"Total domains: {len(results)}", file=sys.stderr)
    print(f"Successful: {success_count}", file=sys.stderr)
    print(f"Failed: {error_count}", file=sys.stderr)
    print("", file=sys.stderr)
    
    # Output results
    output_data = {
        "total": len(results),
        "successful": success_count,
        "failed": error_count,
        "results": results,
    }
    
    if args.output:
        with open(args.output, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"Results saved to: {args.output}", file=sys.stderr)
    else:
        # Print JSON to stdout
        print(json.dumps(output_data, indent=2))
    
    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

