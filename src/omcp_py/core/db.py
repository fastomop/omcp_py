from sqlalchemy import create_engine, Column, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from omcp_py.config import get_config

Base = declarative_base()

class Sandbox(Base):
    __tablename__ = 'sandboxes'
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, default=datetime.utcnow)

# Database engine and session setup with lazy initialization
_engine = None
_SessionLocal = None

def get_engine():
    """Get or create the database engine."""
    global _engine
    if _engine is None:
        config = get_config()
        url = f"postgresql+psycopg2://{config.db_user}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_name}"
        _engine = create_engine(url, echo=config.debug)
    return _engine

def get_session():
    """Get a new database session using lazy-initialized session maker."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal()

def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine) 