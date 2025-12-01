#!/usr/bin/env python3
"""
Vercel Deployment Service - Automates deployment to Vercel via API.
"""

import json
import sys
import os
import argparse
import subprocess
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import requests
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def initialize_git_repo(project_path: str) -> bool:
    """Initialize git repo and make initial commit."""
    try:
        os.chdir(project_path)
        
        # Initialize git if not already
        if not Path(".git").exists():
            subprocess.run(["git", "init"], check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "TEQSmartSubmit"], check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "deploy@teqsmartsubmit.com"], check=True, capture_output=True)
        
        # Add all files
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit from TEQSmartSubmit"], check=True, capture_output=True)
        
        return True
    except Exception as e:
        print(f"Git init error: {e}", file=sys.stderr)
        return False


def push_to_github(repo_url: str, project_path: str, github_token: Optional[str] = None) -> Dict[str, Any]:
    """
    Push project to GitHub.
    
    Returns:
        Dict with repo_url and success status
    """
    github_token = github_token or os.getenv("GITHUB_TOKEN")
    if not github_token:
        return {"success": False, "error": "GITHUB_TOKEN not set"}
    
    try:
        os.chdir(project_path)
        
        # Extract repo name from URL
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        
        # Add remote if not exists
        result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True)
        if result.returncode != 0:
            # Create repo via GitHub API if needed
            # For now, assume repo exists
            subprocess.run(
                ["git", "remote", "add", "origin", repo_url],
                check=True,
                capture_output=True
            )
        
        # Push to GitHub
        repo_url_with_token = repo_url.replace("https://", f"https://{github_token}@")
        subprocess.run(
            ["git", "push", "-u", "origin", "main"],
            check=True,
            capture_output=True,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"}
        )
        
        return {"success": True, "repo_url": repo_url}
    except Exception as e:
        return {"success": False, "error": str(e)}


def deploy_to_vercel(project_path: str, vercel_token: Optional[str] = None) -> Dict[str, Any]:
    """
    Deploy to Vercel using Vercel CLI or API.
    
    Returns:
        Dict with deployment URL and status
    """
    vercel_token = vercel_token or os.getenv("VERCEL_TOKEN")
    if not vercel_token:
        return {"success": False, "error": "VERCEL_TOKEN not set"}
    
    try:
        # Use Vercel CLI if available
        result = subprocess.run(
            ["vercel", "--token", vercel_token, "--yes", "--prod"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            # Extract URL from output
            output = result.stdout
            # Vercel CLI outputs URL in format: https://project-name.vercel.app
            lines = output.split("\n")
            url = None
            for line in lines:
                if "https://" in line and "vercel.app" in line:
                    url = line.strip().split()[-1]
                    break
            
            return {
                "success": True,
                "url": url or "https://deployment.vercel.app",
                "deployment_id": "cli-deployment",
            }
        else:
            return {"success": False, "error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Deployment timeout"}
    except FileNotFoundError:
        # Fallback to API deployment
        return deploy_to_vercel_api(project_path, vercel_token)
    except Exception as e:
        return {"success": False, "error": str(e)}


def deploy_to_vercel_api(project_path: str, vercel_token: str) -> Dict[str, Any]:
    """Deploy using Vercel API directly."""
    try:
        # Create deployment archive
        import tarfile
        import tempfile
        
        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
            with tarfile.open(tmp.name, "w:gz") as tar:
                tar.add(project_path, arcname=".")
            
            # Upload to Vercel
            headers = {
                "Authorization": f"Bearer {vercel_token}",
            }
            
            # This is simplified - actual Vercel API requires more steps
            return {
                "success": False,
                "error": "Vercel API deployment requires additional setup. Please use Vercel CLI.",
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def deploy_website(
    template_path: str,
    github_repo_url: Optional[str] = None,
    vercel_token: Optional[str] = None,
    github_token: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Complete deployment workflow: Git init -> GitHub push -> Vercel deploy.
    
    Returns:
        Dict with deployment status and URLs
    """
    results = {
        "git_initialized": False,
        "github_pushed": False,
        "vercel_deployed": False,
        "vercel_url": None,
        "github_repo_url": None,
        "errors": [],
    }
    
    # Step 1: Initialize Git
    if initialize_git_repo(template_path):
        results["git_initialized"] = True
    else:
        results["errors"].append("Failed to initialize git repo")
        return results
    
    # Step 2: Push to GitHub (if repo URL provided)
    if github_repo_url:
        github_result = push_to_github(github_repo_url, template_path, github_token)
        if github_result.get("success"):
            results["github_pushed"] = True
            results["github_repo_url"] = github_repo_url
        else:
            results["errors"].append(f"GitHub push failed: {github_result.get('error')}")
    
    # Step 3: Deploy to Vercel
    vercel_result = deploy_to_vercel(template_path, vercel_token)
    if vercel_result.get("success"):
        results["vercel_deployed"] = True
        results["vercel_url"] = vercel_result.get("url")
        results["deployment_id"] = vercel_result.get("deployment_id")
    else:
        results["errors"].append(f"Vercel deployment failed: {vercel_result.get('error')}")
    
    return results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Deploy website to Vercel")
    parser.add_argument("--template-path", required=True, help="Path to generated template")
    parser.add_argument("--github-repo", help="GitHub repository URL")
    parser.add_argument("--vercel-token", help="Vercel token (or use VERCEL_TOKEN env var)")
    parser.add_argument("--github-token", help="GitHub token (or use GITHUB_TOKEN env var)")
    
    args = parser.parse_args()
    
    try:
        result = deploy_website(
            args.template_path,
            args.github_repo,
            args.vercel_token,
            args.github_token,
        )
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

