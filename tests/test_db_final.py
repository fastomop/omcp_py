import sys
import uuid
sys.path.insert(0, "src")

from omcp_py.config import get_config
try:
    import importlib
    sqlalchemy = importlib.import_module('sqlalchemy')
    create_engine = getattr(sqlalchemy, 'create_engine')
    text = getattr(sqlalchemy, 'text')
except Exception:
    print("⚠️ SQLAlchemy not installed; skipping DB connection test in test_db_final.py")
else:
    config = get_config()
    url = f"postgresql://{config.db_user}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_name}"
    engine = create_engine(url)

    with engine.connect() as conn:
        print(conn.execute(text("SELECT 1")).fetchall())

    print("Test completed")
