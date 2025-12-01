"""Synchronous database session for background tasks."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Get database URL (convert asyncpg to psycopg2)
database_url = os.getenv("DATABASE_URL", "").replace("+asyncpg", "").replace("postgresql+asyncpg://", "postgresql://")

# If DATABASE_URL is empty, try to get from TEQ_DATABASE_URL
if not database_url:
    teq_db_url = os.getenv("TEQ_DATABASE_URL", "")
    if teq_db_url:
        database_url = teq_db_url.replace("+asyncpg", "").replace("postgresql+asyncpg://", "postgresql://")

# Only create engine if we have a valid database URL
if database_url:
    engine = create_engine(database_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
else:
    # Create a dummy sessionmaker that will fail with a helpful error
    engine = None
    SessionLocal = None
