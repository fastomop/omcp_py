import sys
sys.path.insert(0, "src")

from omcp_py.config import get_config
from omcp_py.sandbox_manager import SandboxManager

config = get_config()
manager = SandboxManager(config)

# Create sandbox
sandbox_id = manager.create_sandbox()
print(f"Sandbox created: {sandbox_id}")

# Test simple database connection without package installation
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
print("Network test result:", result.output.decode())

# Clean up
manager.remove_sandbox(sandbox_id)
print("Test completed")
