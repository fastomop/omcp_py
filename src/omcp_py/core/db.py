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

# Database engine and session setup
def get_engine():
    config = get_config()
    url = f"postgresql+psycopg2://{config.db_user}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_name}"
    return create_engine(url, echo=config.debug)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())

def get_session():
    return SessionLocal()

def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine) 