"""Check if 


 users exist in the database."""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.db.session import get_session
from app.db.models.admin import Admin
from sqlalchemy import select


async def check_admins():
    """Check existing admin users."""
    try:
        async for session in get_session():
            result = await session.execute(select(Admin).where(Admin.is_active == True))
            admins = result.scalars().all()
            
            if admins:
                print(f"\nFound {len(admins)} active admin user(s):")
                for admin in admins:
                    print(f"  - Username: {admin.username}")
                    print(f"    Created: {admin.created_at}")
                    print()
            else:
                print("\n⚠️  No admin users found in the database!")
                print("\nTo create an admin user, run:")
                print("  python create_admin.py <username> <password>")
                print("\nExample:")
                print("  python create_admin.py admin mypassword123")
                return False
            return True
    except Exception as e:
        print(f"\n❌ Error checking admins: {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL is running")
        print("  2. Database migrations have been run")
        print("  3. DATABASE_URL environment variable is set")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Checking Admin Users")
    print("=" * 60)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    success = loop.run_until_complete(check_admins())
    loop.close()
    
    sys.exit(0 if success else 1)

