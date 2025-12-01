#!/usr/bin/env python3
"""Create admin user for TEQSmartSubmit."""

import sys
import os
import argparse
from getpass import getpass

# Load environment variables from .env file if it exists
def load_env_file():
    """Load environment variables from .env file."""
    env_files = ['.env', 'backend/.env', '.env.local']
    for env_file in env_files:
        if os.path.exists(env_file):
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            # Set environment variable if not already set
                            if key not in os.environ:
                                os.environ[key] = value
                            # Also check for DATABASE_URL variants
                            if key == 'TEQ_DATABASE_URL' and 'DATABASE_URL' not in os.environ:
                                # Convert asyncpg to regular postgresql
                                db_url = value.replace('+asyncpg', '').replace('postgresql+asyncpg://', 'postgresql://')
                                os.environ['DATABASE_URL'] = db_url
            except Exception as e:
                print(f"[WARNING] Could not load {env_file}: {e}")

# Load .env files FIRST, before any imports
load_env_file()

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from passlib.context import CryptContext
    from app.db.sync_session import SessionLocal
    from app.db.models.admin import Admin
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    print(f"[INFO] Current Python path: {sys.path}")
    print(f"[INFO] Backend path: {backend_path}")
    print(f"[INFO] Checking if backend/app exists: {os.path.exists(os.path.join(backend_path, 'app'))}")
    print("\nPlease ensure:")
    print("  1. Dependencies are installed: pip install -r requirements.txt")
    print("  2. Backend directory structure is correct")
    print("  3. You're running from the project root directory")
    sys.exit(1)


def create_admin(username: str, password: str, email: str = None, role: str = "admin"):
    """Create an admin user."""
    # Check if DATABASE_URL is set
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # Try TEQ_DATABASE_URL
        teq_db_url = os.getenv("TEQ_DATABASE_URL", "")
        if teq_db_url:
            database_url = teq_db_url.replace("+asyncpg", "").replace("postgresql+asyncpg://", "postgresql://")
    
    if not database_url:
        print("[ERROR] DATABASE_URL not set!")
        print("\nPlease set DATABASE_URL environment variable:")
        print("  PowerShell: $env:DATABASE_URL='postgresql://user:pass@localhost:5432/dbname'")
        print("  Or create a .env file with: DATABASE_URL=postgresql://user:pass@localhost:5432/dbname")
        return False
    
    if SessionLocal is None:
        print("[ERROR] Database session not initialized!")
        print(f"[INFO] DATABASE_URL: {database_url[:50]}...")
        return False
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    db = SessionLocal()
    try:
        # Check if user exists
        existing = db.query(Admin).filter(Admin.username == username).first()
        if existing:
            print(f"[ERROR] User '{username}' already exists")
            return False
        
        # Hash password
        password_hash = pwd_context.hash(password)
        
        # Create admin
        admin = Admin(
            username=username,
            password_hash=password_hash,
            email=email,
            role=role,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        
        print(f"\n[OK] Admin user '{username}' created successfully!")
        print(f"   Role: {role}")
        if email:
            print(f"   Email: {email}")
        print(f"\nYou can now login with:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        return True
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Error creating admin: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Create admin user")
    parser.add_argument("username", help="Admin username")
    parser.add_argument("password", nargs="?", help="Admin password (will prompt if not provided)")
    parser.add_argument("--email", help="Admin email")
    parser.add_argument("--role", choices=["admin", "operator", "viewer"], default="admin", help="User role")
    
    args = parser.parse_args()
    
    password = args.password
    if not password:
        password = getpass("Enter password: ")
        password_confirm = getpass("Confirm password: ")
        if password != password_confirm:
            print("[ERROR] Passwords do not match")
            sys.exit(1)
    
    success = create_admin(args.username, password, args.email, args.role)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
