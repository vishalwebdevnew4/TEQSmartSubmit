"""Reset admin user password."""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.db.session import get_session
from app.db.models.admin import Admin
from app.core.security import hash_password
from sqlalchemy import select


async def reset_password(username: str, new_password: str):
    """Reset password for an admin user."""
    if len(new_password.encode('utf-8')) > 72:
        print("Error: Password is too long (maximum 72 bytes)")
        return False
    
    async for session in get_session():
        # Find admin user
        result = await session.execute(select(Admin).where(Admin.username == username))
        admin = result.scalar_one_or_none()
        
        if not admin:
            print(f"Error: Admin user '{username}' not found!")
            return False
        
        try:
            # Update password
            admin.password_hash = hash_password(new_password)
            session.add(admin)
            await session.commit()
            print(f"✅ Password reset successfully for user '{username}'!")
            return True
        except Exception as e:
            print(f"Error resetting password: {e}")
            await session.rollback()
            return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python reset_admin_password.py <username> <new_password>")
        print("\nExample:")
        print("  python reset_admin_password.py admin mynewpassword123")
        print("\nAvailable admin users:")
        print("  - admin")
        print("  - newadmin")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    
    print("=" * 60)
    print("Reset Admin Password")
    print("=" * 60)
    print(f"Username: {username}")
    print(f"New password: {'*' * len(password)}")
    print("=" * 60)
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(reset_password(username, password))
        loop.close()
        
        if success:
            print("\n✅ Password reset complete!")
            print(f"You can now login with:")
            print(f"  Username: {username}")
            print(f"  Password: {password}")
        else:
            print("\n❌ Failed to reset password!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


