# database.py - Sets up the database connection and session management.
# Supports local SQLite (carbon.db) and also remote Supabase PostgreSQL when DATABASE_URL is set.

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Default to SQLite file 'carbon.db' located in the backend folder.
# If a remote database URL (such as Supabase PostgreSQL) is provided via environment variable, use that instead.
current_dir = os.path.dirname(os.path.abspath(__file__))
default_db_path = os.path.join(current_dir, "carbon.db").replace("\\", "/")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{default_db_path}")

# Supabase gives connection URLs starting with "postgres://", but SQLAlchemy 2.0 requires "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite requires 'check_same_thread: False' so multiple requests can safely read/write.
# PostgreSQL does not need this setting.
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

# SessionLocal is a factory that gives us a new database session for each request.
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class which our SQLAlchemy models (tables) will inherit from.
Base = declarative_base()


def get_db():
    """
    Dependency function for FastAPI routes to obtain a database session.
    Opens a new session, yields it to the route, and closes it when the request is done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        # Always close the session to prevent database locks and memory leaks
        db.close()
