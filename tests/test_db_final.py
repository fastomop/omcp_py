import sys
import uuid
sys.path.insert(0, "src")

from omcp_py.config import get_config
from omcp_py.sandbox_manager import SandboxManager
import docker

config = get_config()
manager = SandboxManager(config)

# Create sandbox with network access using custom image
sandbox_id = str(uuid.uuid4())
client = docker.DockerClient(base_url="unix:///var/run/docker.sock")

try:
    # Create container with network access and pre-installed psycopg2
    container = client.containers.run(
        "11c24f68e03b",  # Use image ID
        command=["sleep", "infinity"],
        detach=True,
        name=f"omcp-sandbox-{sandbox_id}",
        network="omcp_py_default",  # Connect to the same network as the database
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
            "/sandbox": "rw,noexec,nosuid,size=500M"
        }
    )
    
    print(f"Sandbox created: {sandbox_id}")
    
    # Test database connection
    db_code = """
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
    
    result = container.exec_run(["python3", "-c", db_code])
    print("DB test result:", result.output.decode())
    
    # Clean up
    container.stop(timeout=1)
    container.remove()
    print("Test completed")
    
except Exception as e:
    print(f"Error: {e}")
