import sys
sys.path.insert(0, "src")

from omcp_py.config import get_config
from omcp_py.sandbox_manager import SandboxManager

config = get_config()
manager = SandboxManager(config)

# Create sandbox
sandbox_id = manager.create_sandbox()
print(f"Sandbox created: {sandbox_id}")

# Test basic code execution
test_code = "print(\"Hello from sandbox!\"); import sys; print(f\"Python version: {sys.version}\")"
result = manager.execute_code(sandbox_id, test_code)
print("Test result:", result.output.decode())

# Clean up
manager.remove_sandbox(sandbox_id)
print("Test completed")
