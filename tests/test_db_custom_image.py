import sys
import uuid

sys.path.insert(0, "src")

import pytest
import docker
from conftest import require_integration
from omcp_py.config import get_config


def test_db_with_custom_image():
    require_integration()
    try:
        client = docker.DockerClient(base_url="unix:///var/run/docker.sock")
        client.ping()
    except Exception:
        pytest.skip("Docker is not available")

    try:
        client.images.get("omcp-sandbox:latest")
    except Exception:
        pytest.skip("Custom image omcp-sandbox:latest not found")

    config = get_config()
    sandbox_id = str(uuid.uuid4())
    container = client.containers.run(
        "omcp-sandbox:latest",
        command=["sleep", "infinity"],
        detach=True,
        name=f"omcp-sandbox-{sandbox_id}",
        network="omcp_py_default",
        mem_limit="512m",
        cpu_period=100000,
        cpu_quota=50000,
        remove=True,
        user=1000,
        read_only=True,
        cap_drop=["ALL"],
        security_opt=["no-new-privileges"],
        tmpfs={
            "/tmp": "rw,noexec,nosuid,size=100M",
            "/sandbox": "rw,noexec,nosuid,size=500M",
        },
    )

    try:
        db_code = f"""
import psycopg2
try:
    conn = psycopg2.connect(
        dbname={config.db_name!r},
        user={config.db_user!r},
        password={config.db_password!r},
        host={'db'!r},
        port={config.db_port!r}
    )
    cur = conn.cursor()
    cur.execute("SELECT version()")
    print("Database connection: SUCCESS")
    print("PostgreSQL version:", cur.fetchone())
    cur.close()
    conn.close()
except Exception as e:
    print("Database connection failed:", e)
"""
        result = container.exec_run(["python3", "-c", db_code])
        assert b"SUCCESS" in result.output
    finally:
        container.stop(timeout=1)
        container.remove()
