import sys
import uuid
sys.path.insert(0, "src")

from omcp_py.config import get_config
from typing import TYPE_CHECKING

if not TYPE_CHECKING:
    try:
        from sqlalchemy import create_engine, text
    except Exception:
        print("⚠️ SQLAlchemy not installed; skipping DB connection test in test_db_simple.py")
    else:
        config = get_config()
        url = f"postgresql://{config.db_user}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_name}"
        engine = create_engine(url)

        with engine.connect() as conn:
            print(conn.execute(text("SELECT 1")).fetchall())

        print("Test completed")
