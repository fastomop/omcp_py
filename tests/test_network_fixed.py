import sys
import uuid

sys.path.insert(0, "src")

import pytest
from conftest import require_integration
import docker


def test_network_access_with_explicit_network():
    require_integration()
    try:
        client = docker.DockerClient(base_url="unix:///var/run/docker.sock")
        client.ping()
    except Exception:
        pytest.skip("Docker is not available")

    sandbox_id = str(uuid.uuid4())
    container = client.containers.run(
        "python:3.11-slim",
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
        db_code = """
import socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)
    result = sock.connect_ex(("db", 5432))
    if result == 0:
        print("Network connectivity to database: SUCCESS")
    else:
        print(f"Network connectivity failed: {result}")
    sock.close()
except Exception as e:
    print(f"Network test failed: {e}")
"""
        result = container.exec_run(["python3", "-c", db_code])
        assert b"SUCCESS" in result.output
    finally:
        container.stop(timeout=1)
        container.remove()
