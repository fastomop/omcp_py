import sys
sys.path.insert(0, "src")

from omcp_py.config import get_config
from omcp_py.sandbox_manager import SandboxManager

config = get_config()
manager = SandboxManager(config)

# Create sandbox
sandbox_id = manager.create_sandbox()
print(f"Sandbox created: {sandbox_id}")

# Install psycopg2
install_code = """
import subprocess
import sys
import os
os.makedirs("/sandbox/packages", exist_ok=True)
subprocess.check_call([sys.executable, "-m", "pip", "install", "--target", "/sandbox/packages", "psycopg2-binary"])
print("Package installation: SUCCESS")
"""

result = manager.execute_code(sandbox_id, install_code)
print("Install result:", result.output.decode())

# Test database connection
db_code = """
import sys
sys.path.insert(0, "/sandbox/packages")
import psycopg2

try:
    conn = psycopg2.connect(
        dbname="omop",
        user="omop_user",
        password="omop_pass",
        host="db",
        port=5432
    )
    cur = conn.cursor()
    cur.execute("SELECT version()")
    print("Database connection: SUCCESS")
    print("PostgreSQL version:", cur.fetchone())
    cur.close()
    conn.close()
except Exception as e:
    print(f"Database connection failed: {e}")
"""

result = manager.execute_code(sandbox_id, db_code)
print("DB test result:", result.output.decode())

# Clean up
manager.remove_sandbox(sandbox_id)
print("Test completed")
