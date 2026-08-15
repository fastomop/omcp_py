import sys
import pytest

sys.path.insert(0, "src")

from conftest import require_integration
from omcp_py.config import get_config
from omcp_py.sandbox_manager import SandboxManager


def test_package_install():
    require_integration()
    config = get_config()
    if not (config.sandbox_network or config.allow_host_gateway):
        pytest.skip("Network access disabled; package installation requires network")
    manager = SandboxManager(config)

    sandbox_id = manager.create_sandbox()
    try:
        install_code = """
import os
import subprocess
import sys
os.makedirs("/sandbox/packages", exist_ok=True)
subprocess.check_call([sys.executable, "-m", "pip", "install", "--target", "/sandbox/packages", "psycopg2-binary"])
print("Package installation: SUCCESS")
"""
        result = manager.execute_code(sandbox_id, install_code)
        assert result["exit_code"] == 0
        assert "SUCCESS" in result["output"]
    finally:
        manager.remove_sandbox(sandbox_id)
