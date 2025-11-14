#!/usr/bin/env python3
"""
Check submission logs to diagnose why submissions aren't received
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta

async def check_submission_logs():
    """Check the submission log in the database"""
    
    print("\n" + "="*80)
    print("CHECKING SUBMISSION LOGS IN DATABASE")
    print("="*80)
    
    try:
        from prisma import Prisma
        
        prisma = Prisma()
        await prisma.connect()
        
        print(f"\n📊 Fetching recent submission logs...")
        
        # Get last 10 submissions
        submissions = await prisma.submissionlog.find_many(
            order_by={'createdAt': 'desc'},
            take=10
        )
        
        if not submissions:
            print(f"\n❌ NO SUBMISSIONS FOUND IN DATABASE")
            print(f"   Check: No form submissions have been received yet")
            return False
        
        print(f"\n✅ Found {len(submissions)} submissions\n")
        
        # Display submission details
        for i, sub in enumerate(submissions, 1):
            print(f"Submission #{i}")
            print(f"  ID: {sub.id}")
            print(f"  URL: {sub.url}")
            print(f"  Status: {sub.status}")
            print(f"  Message: {sub.message[:100] if sub.message else 'None'}")
            print(f"  Created: {sub.createdAt}")
            print(f"  Finished: {sub.finishedAt}")
            print(f"  Domain ID: {sub.domainId}")
            print(f"  Template ID: {sub.templateId}")
            print(f"  Admin ID: {sub.adminId}")
            print()
        
        # Count by status
        print(f"📈 Submission Status Summary:")
        status_counts = {}
        for sub in submissions:
            status_counts[sub.status] = status_counts.get(sub.status, 0) + 1
        
        for status, count in status_counts.items():
            emoji = "✅" if status == "success" else "❌" if status == "failed" else "⏳"
            print(f"  {emoji} {status}: {count}")
        
        # Check for recent failures
        recent = [s for s in submissions if (datetime.now(s.createdAt.tzinfo) - s.createdAt).total_seconds() < 3600]
        if recent:
            print(f"\n⚠️  Recent submissions (last 1 hour):")
            for sub in recent:
                print(f"  {sub.status.upper()} - {sub.message[:60] if sub.message else 'No message'}")
        
        await prisma.disconnect()
        return len(submissions) > 0
    
    except Exception as e:
        print(f"\n❌ Could not connect to database: {e}")
        print(f"\n💡 Check:")
        print(f"   1. Is the database running?")
        print(f"   2. Is DATABASE_URL set correctly?")
        print(f"   3. Have you run migrations?")
        return False

async def check_api_endpoint():
    """Test if the API endpoint is working"""
    
    print("\n" + "="*80)
    print("TESTING API ENDPOINT")
    print("="*80)
    
    import json
    import urllib.request
    import urllib.error
    
    test_payload = {
        "url": "https://interiordesign.xcelanceweb.com/",
        "template": {
            "fields": [
                {"selector": 'input[name="name"]', "value": "Test User"},
                {"selector": 'input[name="email"]', "value": "test@test.com"},
                {"selector": 'input[name="phone"]', "value": "123456789"},
                {"selector": 'textarea[name="comment"]', "value": "Test message"}
            ],
            "use_local_captcha_solver": True
        }
    }
    
    endpoints = [
        "http://localhost:3000/api/run",
        "http://127.0.0.1:3000/api/run"
    ]
    
    print(f"\n🔍 Attempting to reach API endpoints...\n")
    
    for endpoint in endpoints:
        try:
            print(f"Testing: {endpoint}")
            
            req = urllib.request.Request(
                endpoint,
                data=json.dumps(test_payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            response = urllib.request.urlopen(req, timeout=5)
            data = response.read().decode('utf-8')
            result = json.loads(data)
            
            print(f"✅ API is responding!")
            print(f"   Status: {response.status}")
            print(f"   Response: {json.dumps(result, indent=2)[:200]}")
            return True
            
        except urllib.error.URLError as e:
            print(f"❌ Cannot connect: {e}")
        except Exception as e:
            print(f"⚠️  Error: {str(e)[:100]}")
    
    print(f"\n💡 Suggestion: Make sure frontend server is running")
    print(f"   Command: npm run dev")
    return False

async def check_python_automation():
    """Check if Python automation script works"""
    
    print("\n" + "="*80)
    print("TESTING PYTHON AUTOMATION SCRIPT")
    print("="*80)
    
    import subprocess
    import json
    
    # Create a test template
    test_template = {
        "url": "https://httpbin.org/html",  # Use a reliable test page
        "fields": [
            {"selector": "input[name='test']", "value": "Test Value"}
        ],
        "use_local_captcha_solver": False
    }
    
    print(f"\n🧪 Running test with httpbin.org...")
    
    try:
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_template, f)
            template_path = f.name
        
        script_path = "/var/www/html/TEQSmartSubmit/automation/run_submission.py"
        
        # Run the script
        result = subprocess.run(
            ["python3", script_path, "--url", test_template["url"], "--template", template_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        print(f"Exit code: {result.returncode}")
        
        if result.returncode == 0:
            print(f"✅ Python script executed successfully")
            if result.stdout:
                print(f"Output:\n{result.stdout[:200]}")
        else:
            print(f"❌ Python script failed")
            if result.stderr:
                print(f"Error:\n{result.stderr[:200]}")
        
        # Cleanup
        import os
        os.unlink(template_path)
        
        return result.returncode == 0
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def main():
    """Run all diagnostics"""
    
    print("\n" + "█"*80)
    print("█" + " "*78 + "█")
    print("█" + "SUBMISSION DIAGNOSIS - WHY ARE SUBMISSIONS NOT RECEIVED?".center(78) + "█")
    print("█" + " "*78 + "█")
    print("█"*80)
    
    results = {}
    
    print("\n[1/3] Checking submission logs...")
    results['logs'] = await check_submission_logs()
    
    print("\n[2/3] Testing API endpoint...")
    results['api'] = await check_api_endpoint()
    
    print("\n[3/3] Testing Python automation...")
    results['automation'] = await check_python_automation()
    
    # Final diagnosis
    print("\n" + "="*80)
    print("DIAGNOSIS RESULTS")
    print("="*80)
    
    print(f"\nDatabase Logs:      {'✅ Submissions recorded' if results['logs'] else '❌ No submissions'}")
    print(f"API Endpoint:       {'✅ Responding' if results['api'] else '❌ Not responding'}")
    print(f"Python Automation:  {'✅ Working' if results['automation'] else '❌ Failed'}")
    
    print("\n" + "="*80)
    print("RECOMMENDED ACTIONS")
    print("="*80)
    
    if not results['api']:
        print("\n🔴 CRITICAL: API endpoint is not responding")
        print("   1. Check if Next.js frontend is running: npm run dev")
        print("   2. Check port 3000 is accessible")
        print("   3. Check firewall settings")
    
    if not results['logs']:
        print("\n🟡 WARNING: No submissions in database")
        print("   1. Check if database is running")
        print("   2. Run database migrations: npm run db:migrate")
        print("   3. Verify DATABASE_URL is set correctly")
    
    if not results['automation']:
        print("\n🟡 WARNING: Python automation has issues")
        print("   1. Check if Python 3 is installed")
        print("   2. Check if Playwright dependencies are installed")
        print("   3. Check Python script logs")
    
    if all(results.values()):
        print("\n✅ All systems operational! Problem may be with frontend submission code.")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏸️  Interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
