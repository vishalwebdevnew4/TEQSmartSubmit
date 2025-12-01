"""Check database connection and tables for GUI application."""

import sys
import os
import asyncio

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.db.session import get_session
from app.db.models.domain import Domain
from app.db.models.submission import SubmissionLog
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import AsyncSession

async def check_database():
    """Check database connection and tables."""
    print("Checking database connection...")
    
    try:
        async for session in get_session():
            # Test basic connection
            print("\n1. Testing database connection...")
            result = await session.execute(text("SELECT 1"))
            row = result.scalar()
            if row == 1:
                print("   ✅ Database connection successful!")
            else:
                print("   ❌ Database connection test failed!")
                return False
            
            # Check if tables exist
            print("\n2. Checking if tables exist...")
            inspector = inspect(session.bind)
            tables = await inspector.get_table_names()
            
            required_tables = ['domains', 'submission_logs', 'templates', 'admins']
            missing_tables = []
            
            for table in required_tables:
                if table in tables:
                    print(f"   ✅ Table '{table}' exists")
                else:
                    print(f"   ❌ Table '{table}' NOT FOUND!")
                    missing_tables.append(table)
            
            if missing_tables:
                print(f"\n⚠️  Missing tables: {', '.join(missing_tables)}")
                print("   Run database migrations to create them:")
                print("   cd backend && python -m alembic upgrade head")
                return False
            
            # Check domain count
            print("\n3. Checking domain count...")
            result = await session.execute(text("SELECT COUNT(*) FROM domains"))
            domain_count = result.scalar()
            print(f"   Found {domain_count} domains in database")
            
            # Check submission logs count
            print("\n4. Checking submission logs count...")
            result = await session.execute(text("SELECT COUNT(*) FROM submission_logs"))
            log_count = result.scalar()
            print(f"   Found {log_count} submission logs in database")
            
            # Try to query using SQLAlchemy models
            print("\n5. Testing SQLAlchemy model queries...")
            try:
                result = await session.execute(text("SELECT id, url FROM domains LIMIT 5"))
                domains = result.fetchall()
                if domains:
                    print(f"   ✅ Successfully queried {len(domains)} domains:")
                    for domain in domains:
                        print(f"      - {domain[1]}")
                else:
                    print("   ⚠️  No domains found in database")
            except Exception as e:
                print(f"   ❌ Error querying domains: {e}")
                return False
            
            print("\n✅ All database checks passed!")
            return True
            
    except Exception as e:
        print(f"\n❌ Database connection error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Database Connection Check for GUI Application")
    print("=" * 60)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    success = loop.run_until_complete(check_database())
    loop.close()
    
    if not success:
        print("\n" + "=" * 60)
        print("❌ Database check failed!")
        print("\nTroubleshooting steps:")
        print("1. Make sure PostgreSQL is running")
        print("2. Check DATABASE_URL environment variable")
        print("3. Verify database exists: teqsmartsubmit")
        print("4. Run migrations: cd backend && python -m alembic upgrade head")
        print("=" * 60)
        sys.exit(1)
    else:
        print("\n" + "=" * 60)
        print("✅ Database is ready!")
        print("=" * 60)
        sys.exit(0)


