#!/usr/bin/env python3
"""Create admin user for TEQSmartSubmit - Simple version with inline database setup."""

import sys
import os
import argparse
from getpass import getpass

# Add backend directory to path
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

try:
    from passlib.context import CryptContext
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.db.models.admin import Admin
    from app.db.base import Base
except ImportError as e:
    print(f"[ERROR] Import error: {e}")
    print("\nPlease install dependencies:")
    print("  pip install passlib[bcrypt] sqlalchemy psycopg2-binary")
    sys.exit(1)


def get_database_url():
    """Get database URL from environment or prompt user."""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("\n[INFO] DATABASE_URL not set. Please provide database connection details:")
        print("Format: postgresql://username:password@localhost:5432/database_name")
        print("\nExample: postgresql://postgres:mypassword@localhost:5432/teqsmartsubmit")
        
        db_input = input("\nEnter DATABASE_URL (or press Enter to use default): ").strip()
        if db_input:
            database_url = db_input
        else:
            # Try common defaults
            username = input("PostgreSQL username [postgres]: ").strip() or "postgres"
            password = getpass("PostgreSQL password: ")
            host = input("Host [localhost]: ").strip() or "localhost"
            port = input("Port [5432]: ").strip() or "5432"
            database = input("Database name [teqsmartsubmit]: ").strip() or "teqsmartsubmit"
            
            database_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
    
    return database_url


def create_admin(username: str, password: str, email: str = None, role: str = "admin"):
    """Create an admin user."""
    database_url = get_database_url()
    
    # Create engine and session
    engine = create_engine(database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
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

