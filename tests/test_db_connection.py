import sys

sys.path.insert(0, "src")

import pytest
from conftest import require_integration
from omcp_py.config import get_config


def test_db_connection():
    require_integration()
    try:
        from sqlalchemy import create_engine, text
    except Exception:
        pytest.skip("SQLAlchemy not installed")

    config = get_config()
    url = f"postgresql://{config.db_user}:{config.db_password}@{config.db_host}:{config.db_port}/{config.db_name}"
    engine = create_engine(url)

    with engine.connect() as conn:
        res = conn.execute(text("SELECT version()"))
        assert res.fetchone() is not None
