"""Comprehensive test script with timeouts to prevent hanging."""

import sys
import os
import asyncio
import signal
from contextlib import contextmanager
from typing import Optional

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

def timeout_handler(signum, frame):
    """Handle timeout signal."""
    raise TimeoutError("Operation timed out")

@contextmanager
def timeout_context(seconds: int):
    """Context manager for timeout."""
    if sys.platform != 'win32':
        # Unix-like systems
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(seconds)
        try:
            yield
        finally:
            signal.alarm(0)
    else:
        # Windows doesn't support SIGALRM, use asyncio timeout instead
        yield

async def test_database_connection(timeout: int = 5):
    """Test database connection with timeout."""
    print("\n" + "=" * 60)
    print("TEST 1: Database Connection")
    print("=" * 60)
    
    try:
        from app.db.session import get_session
        from sqlalchemy import text
        
        async with asyncio.timeout(timeout):
            async for session in get_session():
                try:
                    result = await session.execute(text("SELECT 1"))
                    row = result.scalar()
                    if row == 1:
                        print("✅ Database connection: SUCCESS")
                        return True
                    else:
                        print("❌ Database connection: FAILED (unexpected result)")
                        return False
                except asyncio.TimeoutError:
                    print(f"❌ Database connection: TIMEOUT ({timeout}s)")
                    return False
                except Exception as e:
                    print(f"❌ Database connection: ERROR - {str(e)}")
                    return False
    except asyncio.TimeoutError:
        print(f"❌ Database connection: TIMEOUT ({timeout}s)")
        return False
    except Exception as e:
        print(f"❌ Database connection: ERROR - {str(e)}")
        return False

async def test_database_tables(timeout: int = 5):
    """Test if database tables exist."""
    print("\n" + "=" * 60)
    print("TEST 2: Database Tables")
    print("=" * 60)
    
    try:
        from app.db.session import get_session
        from sqlalchemy import text
        
        required_tables = ['domains', 'submission_logs', 'templates', 'admins']
        missing_tables = []
        
        async with asyncio.timeout(timeout):
            async for session in get_session():
                try:
                    for table in required_tables:
                        result = await session.execute(
                            text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
                        )
                        exists = result.scalar()
                        if exists:
                            print(f"✅ Table '{table}': EXISTS")
                        else:
                            print(f"❌ Table '{table}': NOT FOUND")
                            missing_tables.append(table)
                    
                    if missing_tables:
                        print(f"\n⚠️  Missing tables: {', '.join(missing_tables)}")
                        print("   Run: cd backend && python -m alembic upgrade head")
                        return False
                    else:
                        print("\n✅ All required tables exist")
                        return True
                except asyncio.TimeoutError:
                    print(f"❌ Table check: TIMEOUT ({timeout}s)")
                    return False
                except Exception as e:
                    print(f"❌ Table check: ERROR - {str(e)}")
                    return False
    except asyncio.TimeoutError:
        print(f"❌ Table check: TIMEOUT ({timeout}s)")
        return False
    except Exception as e:
        print(f"❌ Table check: ERROR - {str(e)}")
        return False

async def test_domain_model(timeout: int = 5):
    """Test Domain model queries."""
    print("\n" + "=" * 60)
    print("TEST 3: Domain Model Queries")
    print("=" * 60)
    
    try:
        from app.db.session import get_session
        from app.db.models.domain import Domain
        from sqlalchemy import select
        
        async with asyncio.timeout(timeout):
            async for session in get_session():
                try:
                    result = await session.execute(
                        select(Domain).limit(5)
                    )
                    domains = result.scalars().all()
                    domain_count = len(domains)
                    print(f"✅ Domain query: SUCCESS ({domain_count} domains found)")
                    
                    if domain_count > 0:
                        print("   Sample domains:")
                        for domain in domains[:3]:
                            print(f"      - {domain.url} (Active: {domain.is_active})")
                    else:
                        print("   ⚠️  No domains in database")
                    
                    return True
                except Exception as e:
                    error_msg = str(e)
                    if "does not exist" in error_msg.lower() or "relation" in error_msg.lower():
                        print(f"❌ Domain query: FAILED - Table may not exist")
                        print(f"   Error: {error_msg}")
                    else:
                        print(f"❌ Domain query: ERROR - {error_msg}")
                    return False
    except asyncio.TimeoutError:
        print(f"❌ Domain query: TIMEOUT ({timeout}s)")
        return False
    except Exception as e:
        print(f"❌ Domain query: ERROR - {str(e)}")
        return False

async def test_submission_log_model(timeout: int = 5):
    """Test SubmissionLog model queries."""
    print("\n" + "=" * 60)
    print("TEST 4: Submission Log Model Queries")
    print("=" * 60)
    
    try:
        from app.db.session import get_session
        from app.db.models.submission import SubmissionLog
        from sqlalchemy import select
        
        async with asyncio.timeout(timeout):
            async for session in get_session():
                try:
                    result = await session.execute(
                        select(SubmissionLog).limit(5)
                    )
                    logs = result.scalars().all()
                    log_count = len(logs)
                    print(f"✅ Submission log query: SUCCESS ({log_count} logs found)")
                    
                    if log_count > 0:
                        print("   Sample logs:")
                        for log in logs[:3]:
                            print(f"      - {log.url} (Status: {log.status})")
                    else:
                        print("   ⚠️  No submission logs in database")
                    
                    return True
                except Exception as e:
                    error_msg = str(e)
                    if "does not exist" in error_msg.lower() or "relation" in error_msg.lower():
                        print(f"❌ Submission log query: FAILED - Table may not exist")
                        print(f"   Error: {error_msg}")
                    else:
                        print(f"❌ Submission log query: ERROR - {error_msg}")
                    return False
    except asyncio.TimeoutError:
        print(f"❌ Submission log query: TIMEOUT ({timeout}s)")
        return False
    except Exception as e:
        print(f"❌ Submission log query: ERROR - {str(e)}")
        return False

async def test_admin_model(timeout: int = 5):
    """Test Admin model queries."""
    print("\n" + "=" * 60)
    print("TEST 5: Admin Model Queries")
    print("=" * 60)
    
    try:
        from app.db.session import get_session
        from app.db.models.admin import Admin
        from sqlalchemy import select
        
        async with asyncio.timeout(timeout):
            async for session in get_session():
                try:
                    result = await session.execute(
                        select(Admin).limit(5)
                    )
                    admins = result.scalars().all()
                    admin_count = len(admins)
                    print(f"✅ Admin query: SUCCESS ({admin_count} admins found)")
                    
                    if admin_count > 0:
                        print("   Admin users:")
                        for admin in admins:
                            print(f"      - {admin.username} (Active: {admin.is_active})")
                    else:
                        print("   ⚠️  No admin users in database")
                        print("   Run: python create_admin.py <username> <password>")
                    
                    return True
                except Exception as e:
                    error_msg = str(e)
                    if "does not exist" in error_msg.lower() or "relation" in error_msg.lower():
                        print(f"❌ Admin query: FAILED - Table may not exist")
                        print(f"   Error: {error_msg}")
                    else:
                        print(f"❌ Admin query: ERROR - {error_msg}")
                    return False
    except asyncio.TimeoutError:
        print(f"❌ Admin query: TIMEOUT ({timeout}s)")
        return False
    except Exception as e:
        print(f"❌ Admin query: ERROR - {str(e)}")
        return False

def test_config_loading():
    """Test configuration loading."""
    print("\n" + "=" * 60)
    print("TEST 6: Configuration Loading")
    print("=" * 60)
    
    try:
        from app.core.config import get_settings
        
        settings = get_settings()
        print(f"✅ Config loading: SUCCESS")
        print(f"   Database URL: {settings.database_url[:50]}...")
        print(f"   App name: {settings.app_name}")
        print(f"   Environment: {settings.environment}")
        print(f"   Debug mode: {settings.debug}")
        return True
    except Exception as e:
        print(f"❌ Config loading: ERROR - {str(e)}")
        return False

def test_imports():
    """Test all critical imports."""
    print("\n" + "=" * 60)
    print("TEST 7: Module Imports")
    print("=" * 60)
    
    modules = [
        ("app.db.session", "get_session"),
        ("app.db.models.domain", "Domain"),
        ("app.db.models.submission", "SubmissionLog"),
        ("app.db.models.admin", "Admin"),
        ("app.core.config", "get_settings"),
    ]
    
    all_ok = True
    for module_name, item_name in modules:
        try:
            module = __import__(module_name, fromlist=[item_name])
            getattr(module, item_name)
            print(f"✅ {module_name}.{item_name}: OK")
        except Exception as e:
            print(f"❌ {module_name}.{item_name}: FAILED - {str(e)}")
            all_ok = False
    
    return all_ok

async def run_all_tests():
    """Run all tests with timeouts."""
    print("=" * 60)
    print("COMPREHENSIVE APPLICATION TEST SUITE")
    print("=" * 60)
    print(f"\nAll tests will timeout after 5 seconds to prevent hanging.")
    print(f"Running tests...\n")
    
    results = {}
    
    # Test imports first (no timeout needed)
    results['imports'] = test_imports()
    
    # Test config (no timeout needed)
    results['config'] = test_config_loading()
    
    # Test database connection
    results['db_connection'] = await test_database_connection(timeout=5)
    
    # Test tables
    results['db_tables'] = await test_database_tables(timeout=5)
    
    # Test models (only if tables exist)
    if results['db_tables']:
        results['domain_model'] = await test_domain_model(timeout=5)
        results['log_model'] = await test_submission_log_model(timeout=5)
        results['admin_model'] = await test_admin_model(timeout=5)
    else:
        print("\n⚠️  Skipping model tests - tables don't exist")
        results['domain_model'] = False
        results['log_model'] = False
        results['admin_model'] = False
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n✅ ALL TESTS PASSED!")
        return True
    else:
        print("\n⚠️  SOME TESTS FAILED")
        return False

if __name__ == "__main__":
    try:
        # Set default timeout for asyncio operations
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(run_all_tests())
        loop.close()
        
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

