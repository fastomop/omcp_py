import sys
sys.path.insert(0, "src")

from conftest import require_integration
from omcp_py.config import get_config
from omcp_py.sandbox_manager import SandboxManager


def test_sandbox_basic_execution():
    require_integration()
    config = get_config()
    manager = SandboxManager(config)

    sandbox_id = manager.create_sandbox()
    try:
        test_code = "print('Hello from sandbox!')"
        result = manager.execute_code(sandbox_id, test_code)
        assert result["exit_code"] == 0
        assert "Hello from sandbox!" in result["output"]
    finally:
        manager.remove_sandbox(sandbox_id)
