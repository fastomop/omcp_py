from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone
from omcp_py.config import get_config
import logging
import os
from contextlib import contextmanager
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)

Base = declarative_base()

class Sandbox(Base):
    __tablename__ = 'sandboxes'
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_used = Column(DateTime, default=lambda: datetime.now(timezone.utc))

# Database engine and session setup with lazy initialization
_engine = None
_SessionLocal = None

def get_engine():
    """Get or create the database engine with proper pooling configuration."""
    global _engine
    if _engine is None:
        config = get_config()
        
        # Build connection URL without logging credentials
        safe_url = f"postgresql+psycopg2://{config.db_user}:***@{config.db_host}:{config.db_port}/{config.db_name}"
        full_url = f"postgresql+psycopg2://{config.db_user}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_name}"
        
        logger.info(f"Connecting to database: {safe_url}")
        
        # Never echo SQL in production (logs full queries with parameters/credentials)
        # Only enable if explicitly requested via LOG_SQL env var
        echo_enabled = config.debug and os.getenv("LOG_SQL", "").lower() == "true"
        
        # Proper pooling configuration for production reliability
        _engine = create_engine(
            full_url,
            echo=echo_enabled,
            poolclass=QueuePool,
            pool_size=10,              # Keep 10 connections open
            max_overflow=20,           # Allow 20 extra connections under load
            pool_timeout=30,           # Wait max 30 seconds for connection
            pool_recycle=3600,         # Recycle connections after 1 hour (db timeout safety)
            pool_pre_ping=True,        # Test connections before using (catch stale connections)
            connect_args={
                "connect_timeout": 10,  # TCP connect timeout
                "application_name": "omcp_sandbox",  # Identify in pg_stat_activity
            }
        )
    return _engine

def get_session():
    """Get a new database session. Use get_session_context() for automatic cleanup."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine(),
            expire_on_commit=False,
        )
    return _SessionLocal()

@contextmanager
def get_session_context():
    """Get a database session with automatic cleanup.
    
    Recommended usage:
        with get_session_context() as session:
            result = session.query(Sandbox).all()
    """
    session = get_session()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def create_tables():
    """Create all database tables if they don't exist."""
    engine = get_engine()
    Base.metadata.create_all(engine) 