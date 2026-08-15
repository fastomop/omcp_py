import sys

sys.path.insert(0, "src")

from conftest import require_integration
from omcp_py.config import get_config
from omcp_py.sandbox_manager import SandboxManager


def test_network_access_matches_config():
    require_integration()
    config = get_config()
    manager = SandboxManager(config)

    sandbox_id = manager.create_sandbox()
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
        result = manager.execute_code(sandbox_id, db_code)
        output = result["output"]
        network_expected = bool(config.sandbox_network or config.allow_host_gateway)
        if network_expected:
            assert "SUCCESS" in output
        else:
            assert "SUCCESS" not in output
    finally:
        manager.remove_sandbox(sandbox_id)
