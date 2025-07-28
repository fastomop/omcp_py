import sys
sys.path.insert(0, "src")

from omcp_py.config import get_config
from omcp_py.sandbox_manager import SandboxManager

config = get_config()
manager = SandboxManager(config)

# Create sandbox
sandbox_id = manager.create_sandbox()
print(f"Sandbox created: {sandbox_id}")

# Test package installation
install_code = """
import subprocess
import sys
import os

# Try to install in user directory
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "psycopg2-binary"])
    print("Package installation: SUCCESS")
except Exception as e:
    print(f"Package installation failed: {e}")
    # Try alternative approach
    try:
        os.makedirs("/sandbox/packages", exist_ok=True)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--target", "/sandbox/packages", "psycopg2-binary"])
        print("Package installation in /sandbox: SUCCESS")
    except Exception as e2:
        print(f"Alternative installation failed: {e2}")
"""

result = manager.execute_code(sandbox_id, install_code)
print("Install result:", result.output.decode())

# Clean up
manager.remove_sandbox(sandbox_id)
print("Test completed")
